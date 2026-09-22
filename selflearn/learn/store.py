"""The knowledge library: an append-only, deduplicated structured memory.

Layout (design document section 6 - the five memory layers):

======================  =========================================================
layer                   stream
======================  =========================================================
raw evidence            ``library/evidence_index.jsonl`` + ``evidence/snapshots``
knowledge (facts)       ``library/claims.jsonl``
reasoning               ``library/strategies.jsonl``, ``library/attacks.jsonl``,
                        ``library/questions.jsonl``
experiments             ``library/experiments.jsonl``
meta-knowledge          ``library/discoveries.jsonl``, ``library/failures.jsonl``,
                        ``library/irregularities.jsonl``, ``library/audit_log.jsonl``
======================  =========================================================

Streams are append-only JSONL so that history is never destroyed, and every write
is also recorded in the audit log with the run id that produced it. On load,
records are deduplicated by primary key with **last write winning**, so the
in-memory view is the current state while the file keeps the full history.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, TypeVar

from ..config import STREAM_FILES, STREAMS  # noqa: F401  (STREAMS kept for external callers)
from ..models import (
    Attack,
    Claim,
    Contradiction,
    Discovery,
    EvidenceRecord,
    ExperimentResult,
    Failure,
    Irregularity,
    Question,
    Strategy,
    Task,
    Topic,
)
from ..util import append_jsonl, read_jsonl, save_json, utcnow_iso

T = TypeVar("T")

# Primary key for each stream, and the field used to decide "newest wins".
STREAM_KEYS: dict[str, tuple[str, str]] = {
    "evidence": ("evidence_id", "retrieved_at"),
    "claims": ("claim_id", "recorded_at"),
    "topics": ("topic_id", "last_updated"),
    "questions": ("id", "created_at"),
    "strategies": ("strategy_id", "created_at"),
    "attacks": ("attack_id", "created_at"),
    "experiments": ("experiment_id", "ran_at"),
    "discoveries": ("discovery_id", "created_at"),
    "failures": ("failure_id", "created_at"),
    "irregularities": ("irregularity_id", "created_at"),
}


def _dedupe(rows: Iterable[dict[str, Any]], key: str, stamp: str) -> list[dict[str, Any]]:
    """Keep the newest record for each primary key; stable ordering by key."""
    best: dict[str, dict[str, Any]] = {}
    for row in rows:
        identifier = str(row.get(key, ""))
        if not identifier:
            continue
        previous = best.get(identifier)
        if previous is None or str(row.get(stamp, "")) >= str(previous.get(stamp, "")):
            best[identifier] = row
    return [best[k] for k in sorted(best)]


@dataclass
class Library:
    """In-memory view of the knowledge library, backed by JSONL streams."""

    root: Path
    run_id: str = ""
    evidence: dict[str, EvidenceRecord] = field(default_factory=dict)
    claims: dict[str, Claim] = field(default_factory=dict)
    topics: dict[str, Topic] = field(default_factory=dict)
    questions: dict[str, Question] = field(default_factory=dict)
    strategies: dict[str, Strategy] = field(default_factory=dict)
    attacks: dict[str, Attack] = field(default_factory=dict)
    experiments: dict[str, ExperimentResult] = field(default_factory=dict)
    discoveries: dict[str, Discovery] = field(default_factory=dict)
    failures: dict[str, Failure] = field(default_factory=dict)
    irregularities: dict[str, Irregularity] = field(default_factory=dict)
    contradictions: dict[str, Contradiction] = field(default_factory=dict)
    tasks: dict[str, Task] = field(default_factory=dict)
    tournaments: dict[str, dict[str, Any]] = field(default_factory=dict)
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    # -- paths -------------------------------------------------------------
    def path(self, stream: str) -> Path:
        """Absolute path of a stream for this library's root."""
        return _stream_paths(self.root)[stream]

    # -- loading -----------------------------------------------------------
    @classmethod
    def load(cls, root: Path, *, run_id: str = "") -> "Library":
        streams = _stream_paths(Path(root))
        rows = {name: list(read_jsonl(path)) for name, path in streams.items()}
        return cls.from_rows(root, rows, run_id=run_id)

    @classmethod
    def from_rows(cls, root: Path, rows: dict[str, list[dict]], *, run_id: str = "") -> "Library":
        """Build a library from raw stream rows.

        `load` reads the JSONL files and calls this; the storage mirror reads the
        same shapes out of the database and calls this, so both views of the same
        rows go through one decoder."""
        library = cls(root=Path(root), run_id=run_id)
        for row in _dedupe(rows.get("evidence", []), *STREAM_KEYS["evidence"]):
            record = _evidence_from_row(row)
            library.evidence[record.evidence_id] = record
        for row in _dedupe(rows.get("claims", []), *STREAM_KEYS["claims"]):
            library.claims[row["claim_id"]] = _claim_from_row(row)
        for row in _dedupe(rows.get("topics", []), *STREAM_KEYS["topics"]):
            library.topics[row["topic_id"]] = _dataclass(Topic, row)
        for row in _dedupe(rows.get("questions", []), *STREAM_KEYS["questions"]):
            library.questions[row["id"]] = _dataclass(Question, row)
        for row in _dedupe(rows.get("strategies", []), *STREAM_KEYS["strategies"]):
            library.strategies[row["strategy_id"]] = _dataclass(Strategy, row)
        for row in _dedupe(rows.get("attacks", []), *STREAM_KEYS["attacks"]):
            library.attacks[row["attack_id"]] = _dataclass(Attack, row)
        for row in _dedupe(rows.get("experiments", []), *STREAM_KEYS["experiments"]):
            library.experiments[row["experiment_id"]] = _dataclass(ExperimentResult, row)
        for row in _dedupe(rows.get("discoveries", []), *STREAM_KEYS["discoveries"]):
            library.discoveries[row["discovery_id"]] = _dataclass(Discovery, row)
        for row in _dedupe(rows.get("failures", []), *STREAM_KEYS["failures"]):
            library.failures[row["failure_id"]] = _dataclass(Failure, row)
        for row in _dedupe(rows.get("irregularities", []), *STREAM_KEYS["irregularities"]):
            library.irregularities[row["irregularity_id"]] = _dataclass(Irregularity, row)
        for row in rows.get("audit", []):
            library.audit_log.append(row)
        for row in _dedupe(rows.get("contradictions", []), "contradiction_id", "created_at"):
            library.contradictions[row["contradiction_id"]] = _dataclass(Contradiction, row)
        for row in _dedupe(rows.get("tournaments", []), "tournament_id", "decided_at"):
            library.tournaments[row["tournament_id"]] = row
        for row in _dedupe(rows.get("tasks", []), "task_id", "created_at"):
            library.tasks[row["task_id"]] = _dataclass(Task, row)
        return library

    # -- writers -----------------------------------------------------------
    def _write(self, stream: str, rows: list[dict[str, Any]], *, stage: str) -> None:
        if not rows:
            return
        path = _stream_paths(self.root)[stream]
        append_jsonl(path, rows)
        append_jsonl(
            _stream_paths(self.root)["audit"],
            [
                {
                    "run_id": self.run_id,
                    "stage": stage,
                    "stream": stream,
                    "records": len(rows),
                    "written_at": utcnow_iso(),
                }
            ],
        )

    def add_evidence(self, records: Iterable[EvidenceRecord], *, stage: str = "collect") -> int:
        rows = [r.to_dict() for r in records]
        for record in records:
            self.evidence[record.evidence_id] = record
        self._write("evidence", rows, stage=stage)
        return len(rows)

    def add_claims(self, claims: Iterable[Claim]) -> int:
        claims = list(claims)
        for claim in claims:
            self.claims[claim.claim_id] = claim
        self._write("claims", [c.to_dict() for c in claims], stage="verify")
        return len(claims)

    def add_topics(self, topics: Iterable[Topic]) -> int:
        topics = list(topics)
        for topic in topics:
            self.topics[topic.topic_id] = topic
        self._write("topics", [t.to_dict() for t in topics], stage="research")
        return len(topics)

    def add_questions(self, questions: Iterable[Question]) -> int:
        """Append the given questions, including updates to ones already stored.

        This used to write only ids it had not seen before, on the assumption that a
        question is written once. That assumption broke the withdrawal path: a
        question whose claim had been retired was updated in memory and then
        silently dropped from the stream, so the published page kept showing it as
        an open gap. Every other ``add_*`` here appends the row it is given and lets
        the last write win; this one does the same now.
        """
        questions = list(questions)
        for question in questions:
            self.questions[question.id] = question
        self._write("questions", [q.to_dict() for q in questions], stage="curiosity")
        return len(questions)

    def add_strategies(self, strategies: Iterable[Strategy]) -> int:
        strategies = list(strategies)
        for strategy in strategies:
            self.strategies[strategy.strategy_id] = strategy
        self._write("strategies", [s.to_dict() for s in strategies], stage="compete")
        return len(strategies)

    def add_attacks(self, attacks: Iterable[Attack]) -> int:
        attacks = list(attacks)
        for attack in attacks:
            self.attacks[attack.attack_id] = attack
        self._write("attacks", [a.to_dict() for a in attacks], stage="criticise")
        return len(attacks)

    def add_experiments(self, experiments: Iterable[ExperimentResult]) -> int:
        experiments = list(experiments)
        for experiment in experiments:
            self.experiments[experiment.experiment_id] = experiment
        self._write("experiments", [e.to_dict() for e in experiments], stage="experiment")
        return len(experiments)

    def add_discoveries(self, discoveries: Iterable[Discovery]) -> int:
        discoveries = list(discoveries)
        for discovery in discoveries:
            self.discoveries[discovery.discovery_id] = discovery
        self._write("discoveries", [d.to_dict() for d in discoveries], stage="curiosity")
        return len(discoveries)

    def add_failures(self, failures: Iterable[Failure]) -> int:
        failures = [f for f in failures]
        new = [f for f in failures if f.failure_id not in self.failures]
        for failure in failures:
            self.failures[failure.failure_id] = failure
        self._write("failures", [f.to_dict() for f in new], stage="meta")
        return len(new)

    def add_irregularities(self, findings: Iterable[Irregularity]) -> int:
        findings = list(findings)
        # Re-raise the visibility of a recurring irregularity rather than
        # duplicating it: unresolved findings accumulate a repeat count instead.
        for finding in findings:
            existing = self.irregularities.get(finding.irregularity_id)
            if existing is not None:
                existing.detail = finding.detail or existing.detail
                existing.created_at = finding.created_at
                # A reviewer's decision outlives the run that re-detects the
                # finding: the engine may raise the same id again, but it must
                # not silently reopen what a human closed. The reviewer fields
                # are copied onto the incoming record so the appended row and
                # the in-memory view agree.
                if existing.resolved and not finding.resolved:
                    finding.resolved = True
                    finding.resolution = finding.resolution or existing.resolution
                    finding.resolved_at = finding.resolved_at or existing.resolved_at
                    finding.resolution_link = finding.resolution_link or existing.resolution_link
                existing.resolved = finding.resolved
                existing.resolution = finding.resolution
                existing.resolved_at = finding.resolved_at
                existing.resolution_link = finding.resolution_link
            else:
                self.irregularities[finding.irregularity_id] = finding
        self._write("irregularities", [f.to_dict() for f in findings], stage="audit")
        return len(findings)

    def add_contradictions(self, contradictions: Iterable[Contradiction]) -> int:
        contradictions = list(contradictions)
        for contradiction in contradictions:
            existing = self.contradictions.get(contradiction.contradiction_id)
            # Same rule as for irregularities: the detector re-emits a pair as
            # "unresolved" on every cycle, and a reviewer's resolution must
            # survive that. The detector never writes the reviewer fields.
            if existing is not None and existing.resolution != "unresolved" and contradiction.resolution == "unresolved":
                contradiction.resolution = existing.resolution
                contradiction.resolution_note = existing.resolution_note
                contradiction.resolved_at = existing.resolved_at
                contradiction.resolution_link = existing.resolution_link
            self.contradictions[contradiction.contradiction_id] = contradiction
        rows = [c.to_dict() for c in contradictions]
        self._write("contradictions", rows, stage="verify")
        return len(rows)

    def add_tournaments(self, tournaments: Iterable[dict[str, Any]]) -> int:
        rows = list(tournaments)
        for row in rows:
            self.tournaments[str(row.get("tournament_id", ""))] = row
        self._write("tournaments", rows, stage="compete")
        return len(rows)

    def add_tasks(self, tasks: Iterable[Task]) -> int:
        tasks = list(tasks)
        for task in tasks:
            self.tasks[task.task_id] = task
        self._write("tasks", [t.to_dict() for t in tasks], stage="manage")
        return len(tasks)

    # -- queries -----------------------------------------------------------
    def claims_for_topic(self, topic_id: str) -> list[Claim]:
        return [c for c in self.claims.values() if c.topic_id == topic_id]

    def strategies_for_topic(self, topic_id: str) -> list[Strategy]:
        return [s for s in self.strategies.values() if s.topic_id == topic_id]

    def attacks_for_strategy(self, strategy_id: str) -> list[Attack]:
        return [a for a in self.attacks.values() if a.strategy_id == strategy_id]

    def experiments_for_topic(self, topic_id: str) -> list[ExperimentResult]:
        return [e for e in self.experiments.values() if e.topic_id == topic_id]

    def questions_for_topic(self, topic_id: str) -> list[Question]:
        return [q for q in self.questions.values() if q.topic_id == topic_id]

    def library_by_topic(self) -> dict[str, list[Claim]]:
        grouped: dict[str, list[Claim]] = {}
        for claim in self.claims.values():
            grouped.setdefault(claim.topic_id, []).append(claim)
        return grouped

    def active_topics(self) -> list[Topic]:
        return [t for t in self.topics.values() if t.status not in {"rejected"}]

    # -- export ------------------------------------------------------------
    def export_state(self, path: Path) -> Path:
        """Write a compact JSON view of the library for the site and for audits."""
        payload = {
            "run_id": self.run_id,
            "exported_at": utcnow_iso(),
            "counts": {
                "topics": len(self.topics),
                "claims": len(self.claims),
                "evidence": len(self.evidence),
                "strategies": len(self.strategies),
                "attacks": len(self.attacks),
                "questions": len(self.questions),
                "experiments": len(self.experiments),
                "irregularities": len(self.irregularities),
                "contradictions": len(self.contradictions),
                "failures": len(self.failures),
            },
            "claims": [c.to_dict() for c in self.claims.values()],
            "topics": [t.to_dict() for t in self.topics.values()],
        }
        return save_json(path, payload, indent=2)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _stream_paths(root: Path) -> dict[str, Path]:
    """Resolve every stream path against ``root`` (normally the repository root)."""
    return {name: Path(root) / relative for name, relative in STREAM_FILES.items()}


def _dataclass(cls: type[T], row: dict[str, Any]) -> T:
    """Instantiate a dataclass from a dict.

    Keys the dataclass does not declare are ignored (the JSONL rows carry
    bookkeeping fields such as ``_line``). A required string field that is absent
    from the row is filled with an empty string: an index row legitimately omits
    ``text`` because the full document lives in the snapshot file, and inventing a
    missing *value* for any other type would be worse than failing loudly.
    """
    import dataclasses

    fields = {f.name: f for f in dataclasses.fields(cls)}
    kwargs: dict[str, Any] = {}
    for name, field_obj in fields.items():
        if name in row:
            kwargs[name] = row[name]
        elif field_obj.default_factory is utcnow_iso:
            # Rows written before the field existed must not be given a
            # fabricated creation time: decoding them with the wall clock makes
            # every load disagree with the previous one (and the storage mirror
            # disagree with itself across a second boundary). An empty stamp is
            # what _dedupe already assumes for such rows (row.get(stamp, "")).
            kwargs[name] = ""
        elif field_obj.default is dataclasses.MISSING and field_obj.default_factory is dataclasses.MISSING:
            if field_obj.type in {"str", str}:
                kwargs[name] = ""
            else:  # pragma: no cover - a genuinely malformed row
                raise KeyError(f"{cls.__name__} row is missing required field {name!r}")
    return cls(**kwargs)  # type: ignore[arg-type]


def _evidence_from_row(row: dict[str, Any]) -> EvidenceRecord:
    record = _dataclass(EvidenceRecord, row)
    if not record.text:
        # The index stores an excerpt; the full text lives in the snapshot file.
        record.text = row.get("excerpt", "")
    return record


def _claim_from_row(row: dict[str, Any]) -> Claim:
    from ..models import Verification

    payload = dict(row)
    verification = payload.pop("verification", {}) or {}
    claim = _dataclass(Claim, payload)
    claim.verification = Verification(
        verdict=verification.get("verdict", "unsupported"),
        quote_match=bool(verification.get("quote_match", False)),
        coverage=float(verification.get("coverage", 0.0)),
        missing_numbers=list(verification.get("missing_numbers", []) or []),
        missing_dates=list(verification.get("missing_dates", []) or []),
        reasons=list(verification.get("reasons", []) or []),
    )
    return claim


def load_snapshot_text(snapshot_dir: Path, evidence_id: str) -> str:
    path = Path(snapshot_dir) / f"{evidence_id}.json"
    if not path.exists():
        return ""
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("text", "")
    except (json.JSONDecodeError, OSError):
        return ""


def snapshot_index(snapshot_dir: Path) -> dict[str, dict[str, Any]]:
    """Map evidence id -> snapshot metadata for every stored snapshot."""
    index: dict[str, dict[str, Any]] = {}
    for path in sorted(Path(snapshot_dir).glob("ev-*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        index[payload.get("evidence_id", path.stem)] = payload
    return index
