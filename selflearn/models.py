"""Typed records for every object the engine stores.

Every record carries provenance or an explicit statement of its own limits.
`to_dict()` output is what lands in the append-only JSONL library and in the
published site data, so field names are part of the public contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .util import utcnow_iso

# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@dataclass
class EvidenceRecord:
    """An immutable snapshot of one retrieved document."""

    evidence_id: str
    source_id: str
    source_name: str
    url: str
    title: str
    text: str
    content_hash: str
    evidence_class: str
    evidence_rank: int
    retrieved_at: str = field(default_factory=utcnow_iso)
    published_at: str | None = None
    license: str | None = None
    publisher: str | None = None
    is_fixture: bool = False
    is_live: bool = False
    http_status: int | None = None
    bytes_read: int = 0
    response_sha256: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        # The full text is stored in the snapshot file, not duplicated in the
        # index; the index keeps a bounded excerpt for review.
        payload["excerpt"] = self.text[:400]
        payload.pop("text", None)
        return payload


@dataclass
class Verification:
    """Result of the deterministic support check for a single claim."""

    # Defaults are the most conservative possible verdict, so a claim that somehow
    # loses its verification record can never be read as supported.
    verdict: str = "unsupported"  # supported | partially_supported | unsupported | contradicted
    quote_match: bool = False
    coverage: float = 0.0
    missing_numbers: list[str] = field(default_factory=list)
    missing_dates: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Claim:
    """One atomic, checkable statement sourced from exactly one document."""

    claim_id: str
    topic_id: str
    text: str
    evidence_id: str
    source_name: str
    url: str
    quote: str
    evidence_class: str
    evidence_rank: int
    confidence: str = "unknown"   # high | medium | low | unknown
    verification: Verification = field(default_factory=Verification)
    # "direct" claims are quotations from a retrieved document. "derived" claims
    # are statements the engine computes about its own library; they are verified
    # against the engine's own numbers (context_numbers) rather than a document,
    # and they are exempt from the source-link check for that reason.
    # "synthesis" claims combine figures that appear in two or more *documents*:
    # they cite the direct claims they were built from (cited_claim_ids), and every
    # figure they contain must appear in one of those claims or in the counts the
    # engine computed alongside them (context_numbers).
    claim_kind: str = "direct"
    context_numbers: list[str] = field(default_factory=list)
    cited_claim_ids: list[str] = field(default_factory=list)
    # Output of the published substance rule (selflearn.learn.substance). It is a
    # reading aid, never a verdict: the verification record above decides support.
    substance: dict[str, Any] = field(default_factory=dict)
    # Non-empty when a later cycle would no longer produce this statement, because
    # the rule that composed it changed or a claim it cited is gone. The record is
    # never deleted - the streams are append-only - but a superseded statement is
    # not published as a current one, and the reason is stored here.
    superseded: str = ""
    recorded_at: str = field(default_factory=utcnow_iso)
    limitations: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["verification"] = self.verification.to_dict()
        return payload


@dataclass
class Contradiction:
    """Two claims that conflict on the same number or on the same subject."""

    contradiction_id: str
    topic_id: str
    claim_a: str
    claim_b: str
    kind: str                     # numeric | polar
    detail: str
    severity: str                 # high | medium
    resolution: str = "unresolved"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Topic intelligence
# ---------------------------------------------------------------------------


@dataclass
class Topic:
    """An evolving record for one subject of study."""

    topic_id: str
    title: str
    slug: str
    question: str
    status: str = "new"
    origin: str = "seed"          # seed | discovery
    keywords: list[str] = field(default_factory=list)
    signal: dict[str, Any] = field(default_factory=dict)
    first_seen: str = field(default_factory=utcnow_iso)
    last_updated: str = field(default_factory=utcnow_iso)
    source_ids: list[str] = field(default_factory=list)
    parent_topic_id: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Question:
    id: str
    topic_id: str
    text: str
    origin: str                   # seed | sub_question | gap | discovery
    status: str = "open"          # open | answered | abandoned
    priority: float = 0.5
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Competition
# ---------------------------------------------------------------------------


@dataclass
class Strategy:
    """A competing candidate answer produced by one persona."""

    strategy_id: str
    topic_id: str
    persona_code: str
    persona_name: str
    persona_brief: str
    title: str
    argument: str
    supporting_claim_ids: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    predicted_outcomes: list[str] = field(default_factory=list)
    falsifier: str = ""
    status: str = "hypothesis"
    scorecard: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utcnow_iso)
    limitations: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Attack:
    """An adversarial critique of one strategy."""

    attack_id: str
    strategy_id: str
    topic_id: str
    critic: str
    attack_type: str              # assumption | counterexample | citation | repro | simplicity | data
    statement: str
    severity: str                 # minor | moderate | major | fatal
    claim_refs: list[str] = field(default_factory=list)
    outcome: str = "open"         # open | survived | partial | conceded
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TournamentResult:
    topic_id: str
    round_name: str
    ranking: list[str] = field(default_factory=list)      # strategy ids best-first
    scores: dict[str, float] = field(default_factory=dict)
    winner: str | None = None
    criterion_table: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: str = ""
    decided_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


@dataclass
class ExperimentResult:
    experiment_id: str
    topic_id: str
    hypothesis: str
    method: str
    command: str
    script_path: str
    script_sha256: str
    metric: str
    baseline: float | None
    best_variant: str | None
    best_value: float | None
    seed: int
    result_json: dict[str, Any] = field(default_factory=dict)
    status: str = "completed"     # completed | failed | inconclusive
    error: str = ""
    ran_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Meta
# ---------------------------------------------------------------------------


@dataclass
class Discovery:
    discovery_id: str
    topic_id: str
    text: str
    kind: str                     # finding | new_question | gap | contradiction
    derived_from: list[str] = field(default_factory=list)
    confidence: str = "low"
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Failure:
    failure_id: str
    topic_id: str | None
    stage: str
    summary: str
    detail: str = ""
    remedy: str = ""
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Irregularity:
    """Something a human must look at: missing data, mismatch, conflict, leak."""

    irregularity_id: str
    severity: str                 # info | warning | error
    stage: str
    topic_id: str | None
    summary: str
    detail: str = ""
    url: str | None = None
    suggested_action: str = ""
    created_at: str = field(default_factory=utcnow_iso)
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceStatus:
    """Per-source health record, published so a reader can audit coverage."""

    source_id: str
    name: str
    url: str
    evidence_class: str
    evidence_rank: int
    requires_key: bool
    live_status: str              # reachable | unreachable | not_attempted
    http_status: int | None = None
    detail: str = ""
    checked_at: str = field(default_factory=utcnow_iso)
    items: int = 0
    # Topic ids this poll was made for. The collector fills it so a per-topic
    # report can show only the sources that were actually consulted for that
    # topic; old rows from before this field existed carry an empty list and are
    # then treated as run-wide.
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    """A unit of work the research manager hands to a worker."""

    task_id: str
    kind: str                     # scan | research | compete | criticise | experiment | publish
    topic_id: str | None
    payload: dict[str, Any] = field(default_factory=dict)
    priority: float = 0.5
    status: str = "queued"
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
