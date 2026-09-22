"""Optional database mirror of the JSONL library (roadmap item 8).

The JSONL files remain the source of truth; :mod:`selflearn.storage.database`
mirrors them into a SQLite or PostgreSQL table and can prove the two views are
identical. Nothing in the fetch, verify, think or publish paths imports this
package unless the ``storage`` command is run explicitly.
"""

from __future__ import annotations

from .database import (
    DEFAULT_SQLITE_DSN,
    connect,
    count_rows,
    dsn_from_environment,
    ensure_schema,
    read_rows,
    sync_library,
    verify_views,
)

__all__ = [
    "DEFAULT_SQLITE_DSN",
    "connect",
    "count_rows",
    "dsn_from_environment",
    "ensure_schema",
    "read_rows",
    "sync_library",
    "verify_views",
]
