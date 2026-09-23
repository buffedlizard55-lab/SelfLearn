"""Optional database mirror of the JSONL library (roadmap item 8).

Why this exists
---------------
The JSONL streams stay the source of truth: they are append-only, diffable and
readable with ``cat``. This module adds the migration path the roadmap and
``docs/ARCHITECTURE.md`` describe - write each stream's rows to a table with
the id as part of the key, and read them back through the same loader - so that
"the same site builds from the database" can be tested rather than asserted.

Shape
-----
One table, ``library_rows``, holds every row of every stream as JSON:

===================  =========================================================
column               meaning
===================  =========================================================
``seq``              insertion order (assigned by the writer; append-only)
``stream``           stream name from ``config.STREAM_FILES``
``row_key``          the stream's primary-key field (``''`` for the audit log)
``stamp``            the stream's "newest wins" timestamp field
``payload``          the row itself, JSON
===================  =========================================================

Reading applies exactly the deduplication rule ``Library.load`` uses
(one row per primary key, last write winning, audit log in order), so a
database view and a JSONL view of the same rows produce the same records.

Drivers
-------
* ``sqlite:///path/to/file.db`` - the standard library's ``sqlite3``. This is
  the default and what the tests exercise: a full round trip of the real
  library, compared row for row against the JSONL streams.
* ``postgres://...`` / ``postgresql://...`` - requires an optional DB-API
  driver (``psycopg`` v3 or ``psycopg2``) to be installed. The engine itself
  still has no required third-party dependency; this path is the only place one
  can be needed, and it fails with that fact stated rather than an ImportError
  traceback.

``python3 -m selflearn storage verify`` reports whether the two views agree -
row for row, and record for record after both sides go through
``Library.from_rows`` - the roadmap's "audit reports identical verdicts" check
reduced to something a machine can re-run.
"""

from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
from typing import Any

from ..config import STREAM_FILES
from ..learn.store import Library, STREAM_KEYS, _dedupe, _stream_paths
from ..util import read_jsonl, utcnow_iso

DEFAULT_SQLITE_DSN = "sqlite:///state/library.sqlite3"
ENV_DSN = "SELFLEARN_DATABASE_URL"

#: Streams with no primary-key field in ``STREAM_KEYS``. The audit log is an
#: ordered append-only list; its "key" is the row's position in the file, which
#: is stable because the file is never rewritten.
_EXTRA_KEYS: dict[str, tuple[str, str] | None] = {
    "contradictions": ("contradiction_id", "created_at"),
    "tournaments": ("tournament_id", "decided_at"),
    "tasks": ("task_id", "created_at"),
    "audit": None,
}


def row_key_for(stream: str, row: dict[str, Any], index: int) -> str:
    """The primary-key value stored for one row of one stream."""
    if stream == "audit":
        return f"{index:06d}"
    key_field = _key_and_stamp(stream)[0]
    return str(row.get(key_field, ""))


def stamp_for(stream: str, row: dict[str, Any]) -> str:
    """The "newest wins" timestamp stored for one row of one stream."""
    if stream == "audit":
        return str(row.get("recorded_at") or row.get("created_at") or "")
    return str(row.get(_key_and_stamp(stream)[1], ""))


def _key_and_stamp(stream: str) -> tuple[str, str]:
    if stream in STREAM_KEYS:
        return STREAM_KEYS[stream]
    extra = _EXTRA_KEYS.get(stream)
    if extra is None:
        raise KeyError(f"stream {stream!r} has no primary key and is not the audit log")
    return extra


def dsn_from_environment(explicit: str | None = None) -> str:
    """The database to use: an explicit argument, the environment, or SQLite."""
    if explicit:
        return explicit
    return os.environ.get(ENV_DSN) or DEFAULT_SQLITE_DSN


def connect(dsn: str) -> Any:
    """Open a DB-API connection for ``dsn``.

    SQLite paths work with the standard library alone. PostgreSQL URLs need an
    optional driver; when one is missing the error says exactly that, because
    "the engine has no third-party dependencies" must stay true for everything
    except this explicitly requested path. A relative sqlite path is resolved
    against the active library root (``SELFLEARN_ROOT`` or the repository), never
    the working directory.
    """
    if dsn.startswith("sqlite:///"):
        import sqlite3

        path = dsn[len("sqlite:///"):]
        if path != ":memory:" and not os.path.isabs(path):
            # Relative sqlite paths resolve against the library root, not the
            # working directory. Found 2026-09-22: a smoke run with its own
            # SELFLEARN_ROOT synced 152 rows into whatever ./state/ it was
            # started from, and `site --from-database` - correctly - refused to
            # publish from the contaminated mirror. Each root now gets its own
            # mirror at <root>/state/library.sqlite3, which is where the README
            # has always said it lands.
            from ..config import ROOT as LIBRARY_ROOT

            path = str(Path(LIBRARY_ROOT) / path)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(path)
    if dsn.startswith("sqlite://"):
        raise ValueError("sqlite DSN must be sqlite:///absolute/or/relative.db")
    if dsn.startswith(("postgres://", "postgresql://")):
        try:
            import psycopg  # type: ignore
        except ImportError:
            try:
                import psycopg2  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    f"database {dsn!r} needs an optional PostgreSQL driver: install "
                    "'psycopg[binary]' (v3) or 'psycopg2'. Nothing else in this engine "
                    "requires a third-party package; sqlite:/// DSNs use the standard library."
                ) from exc
            return psycopg2.connect(dsn)
        return psycopg.connect(dsn)
    raise ValueError(f"unsupported database DSN: {dsn!r} (expected sqlite:/// or postgres://)")


def _placeholder(connection: Any) -> str:
    """``?`` for sqlite, ``%s`` for psycopg DB-API drivers."""
    module = type(connection).__module__.split(".")[0]
    return "%s" if module in {"psycopg", "psycopg2"} else "?"


def ensure_schema(connection: Any) -> None:
    ph = _placeholder(connection)
    cursor = connection.cursor()
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS library_rows (
            seq {('BIGINT' if ph == '%s' else 'INTEGER')} PRIMARY KEY,
            stream VARCHAR(64) NOT NULL,
            row_key VARCHAR(128) NOT NULL DEFAULT '',
            stamp VARCHAR(64) NOT NULL DEFAULT '',
            payload TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_library_rows_stream_seq ON library_rows (stream, seq)"
    )
    connection.commit()


def sync_library(root: Path, connection: Any) -> dict[str, Any]:
    """Append every JSONL row the database does not already hold.

    Idempotent: a row already present (same stream, key, stamp and payload) is
    not inserted twice, so re-running ``sync`` on an unchanged library adds
    nothing. Rows are never updated or deleted - the mirror is append-only like
    the files.
    """
    ph = _placeholder(connection)
    cursor = connection.cursor()
    # Rows are appended under fresh sequence numbers; existing rows are never
    # renumbered. COALESCE handles the empty table; +1 keeps the next insert off
    # the current maximum (MAX itself would collide with the last row as soon as
    # only one new row appeared in the files).
    cursor.execute("SELECT COALESCE(MAX(seq), 0) FROM library_rows")
    next_seq = int(cursor.fetchone()[0]) + 1
    streams = _stream_paths(Path(root))
    inserted: dict[str, int] = {}
    total_inserted = 0
    for stream in sorted(STREAM_FILES):
        rows = list(read_jsonl(streams[stream]))
        stream_inserted = 0
        for index, row in enumerate(rows):
            key = row_key_for(stream, row, index)
            stamp = stamp_for(stream, row)
            payload = json.dumps(row, ensure_ascii=False)
            cursor.execute(
                f"""
                INSERT INTO library_rows (seq, stream, row_key, stamp, payload)
                SELECT {ph}, {ph}, {ph}, {ph}, {ph}
                WHERE NOT EXISTS (
                    SELECT 1 FROM library_rows
                    WHERE stream = {ph} AND row_key = {ph} AND stamp = {ph} AND payload = {ph}
                )
                """,
                (next_seq, stream, key, stamp, payload, stream, key, stamp, payload),
            )
            if cursor.rowcount:
                next_seq += 1
                stream_inserted += 1
        inserted[stream] = stream_inserted
        total_inserted += stream_inserted
    connection.commit()
    return {
        "synced_at": utcnow_iso(),
        "rows_inserted": total_inserted,
        "inserted_by_stream": inserted,
        "file_rows_by_stream": {stream: len(list(read_jsonl(streams[stream]))) for stream in sorted(STREAM_FILES)},
    }


class MirrorNotInitialised(RuntimeError):
    """Raised when a database has no ``library_rows`` table to read.

    ``storage verify`` and ``site --from-database`` both read the mirror. Against
    a database that has never been synced - a fresh checkout, a path typed by hand,
    an empty SQLite file created by the driver on connect - the read raised the
    driver's own error (``sqlite3.OperationalError: no such table: library_rows``)
    as a traceback, which reads like a bug in the engine rather than what it is:
    nothing has been mirrored yet. This exception carries the command that fixes it.
    """


def read_rows(connection: Any) -> dict[str, list[dict[str, Any]]]:
    """Every row in the database, grouped by stream in insertion order."""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT stream, payload FROM library_rows ORDER BY seq")
    except Exception as exc:  # driver-specific: no such table, relation does not exist
        raise MirrorNotInitialised(
            f"{type(exc).__name__}: {exc}. The mirror has no library_rows table, so there is nothing to compare. "
            "Run `python3 -m selflearn storage sync` to write the JSONL rows into it first."
        ) from exc
    grouped: dict[str, list[dict[str, Any]]] = {stream: [] for stream in STREAM_FILES}
    for stream, payload in cursor.fetchall():
        grouped.setdefault(stream, []).append(json.loads(payload))
    return grouped


def load_library_from_database(root: Path, connection: Any, *, run_id: str = "") -> Library:
    """Build the same ``Library`` a JSONL load would produce, from database rows.

    This is the read half of \"the same site builds from the database\": the
    rows go through ``Library.from_rows`` - the exact decoder ``Library.load``
    uses - so only the origin of the rows differs. Callers that publish from
    this view run ``verify_views`` first and refuse to publish when the two
    views disagree.
    """
    return Library.from_rows(Path(root), read_rows(connection), run_id=run_id)


def count_rows(connection: Any) -> dict[str, int]:
    cursor = connection.cursor()
    cursor.execute("SELECT stream, COUNT(*) FROM library_rows GROUP BY stream ORDER BY stream")
    return {stream: int(count) for stream, count in cursor.fetchall()}


def _view(rows: dict[str, list[dict[str, Any]]], stream: str) -> list[dict[str, Any]]:
    """The records a reader of this stream would see, exactly as load() sees them."""
    if stream == "audit":
        return rows.get(stream, [])
    key, stamp = _key_and_stamp(stream)
    return _dedupe(rows.get(stream, []), key, stamp)


#: Which ``Library`` attribute holds each stream's decoded records.
_LIBRARY_ATTRS: dict[str, str] = {
    "attacks": "attacks",
    "audit": "audit_log",
    "claims": "claims",
    "contradictions": "contradictions",
    "discoveries": "discoveries",
    "evidence": "evidence",
    "experiments": "experiments",
    "failures": "failures",
    "irregularities": "irregularities",
    "questions": "questions",
    "strategies": "strategies",
    "tasks": "tasks",
    "topics": "topics",
    "tournaments": "tournaments",
}


def _canonical(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)


def _record_json(value: Any) -> str:
    """Canonical JSON for one decoded record, whatever shape it has."""
    if hasattr(value, "to_dict"):
        data: Any = value.to_dict()
    elif dataclasses.is_dataclass(value):
        data = dataclasses.asdict(value)
    elif isinstance(value, dict):
        data = value
    else:
        data = {"repr": repr(value)}
    return _canonical(data)


def _library_view(library: Library) -> dict[str, Any]:
    """Per stream: the records ``Library.from_rows`` decoded, canonically."""
    view: dict[str, Any] = {}
    for stream, attr in _LIBRARY_ATTRS.items():
        records = getattr(library, attr)
        if isinstance(records, dict):
            view[stream] = {str(key): _record_json(value) for key, value in records.items()}
        else:  # the audit log is an ordered list of raw rows
            view[stream] = [_record_json(value) for value in records]
    return view


def verify_views(root: Path, connection: Any, *, dsn: str = "") -> dict[str, Any]:
    """Compare the JSONL mirror against the database, row for row and record for record.

    Two independent checks back the verdict:

    * ``rows_identical`` - every stream's raw rows (canonical JSON, file
      order) appear identically in the database: same rows, same order,
      nothing dropped.
    * ``library_identical`` - decoding both row sets through
      ``Library.from_rows`` (the loader ``Library.load`` uses) yields the same
      records. Belt and braces: when the rows agree this can only disagree if
      the decoder itself is inconsistent, which is exactly what a second view
      exists to catch.

    ``streams`` keeps per-stream counts and a ``matches`` flag (plus a few
    example rows when something differs), ``library_mismatched_streams`` names
    the streams whose decoded records disagree, and ``signature`` records the
    visible record counts of the JSONL view at check time.
    """
    root = Path(root)
    streams = _stream_paths(root)
    file_rows = {stream: list(read_jsonl(streams[stream])) for stream in sorted(STREAM_FILES)}
    db_rows = read_rows(connection)

    report: dict[str, Any] = {
        "checked_at": utcnow_iso(),
        "dsn": dsn,
        "driver": type(connection).__module__.split(".")[0],
        "streams": {},
        "rows_identical": True,
        "library_identical": True,
        "library_mismatched_streams": [],
        "signature": library_signature(root),
    }

    file_records = _library_view(Library.from_rows(root, file_rows))
    db_records = _library_view(Library.from_rows(root, db_rows))

    for stream in sorted(STREAM_FILES):
        left = [_canonical(row) for row in file_rows[stream]]
        right = [_canonical(row) for row in db_rows.get(stream, [])]
        matches = left == right
        report["streams"][stream] = {
            "jsonl_rows": len(left),
            "database_rows": len(right),
            "matches": matches,
        }
        if not matches:
            report["rows_identical"] = False
            only_jsonl = [row for row in left if row not in right][:3]
            only_database = [row for row in right if row not in left][:3]
            report["streams"][stream]["only_in_jsonl_sample"] = only_jsonl
            report["streams"][stream]["only_in_database_sample"] = only_database
        if file_records.get(stream) != db_records.get(stream):
            report["library_identical"] = False
            report["library_mismatched_streams"].append(stream)
    return report


def library_signature(root: Path) -> dict[str, int]:
    """Visible record counts per stream for the JSONL view (used by tests)."""
    streams = _stream_paths(Path(root))
    return {
        stream: len(_view({stream: list(read_jsonl(streams[stream]))}, stream))
        for stream in sorted(STREAM_FILES)
    }
