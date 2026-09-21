"""Assemble the published view of the library.

Nothing here may invent a fact. Every field of a topic report is either

* a verbatim quotation from a verified claim, with its source and link;
* a derived statement about the library, carrying the figures it was computed
  from so that :func:`selflearn.verify.verifier.verify_derived` can check it;
* an explicit ``UNKNOWN`` marker explaining what is missing and what would
  resolve it; or
* fixed scaffolding text with no factual content.

The audit stage re-checks the published payload against these rules before the
site is written (see :mod:`selflearn.verify.audit`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .. import ENGINE_REPO_URL, ENGINE_SITE_URL, __version__
from ..config import EVIDENCE_LABEL, LIFECYCLE_STATES
from ..learn.aggregate import derive_library_claims, library_statistics
from ..learn.memory import build_meta_knowledge
from ..models import (
    Attack,
    Claim,
    Contradiction,
    EvidenceRecord,
    ExperimentResult,
    Failure,
    Irregularity,
    Question,
    SourceStatus,
    Strategy,
    Topic,
)
from ..util import extract_dates, extract_numbers, stable_id, truncate, utcnow_iso

# The design document's own prompt for each topic record, kept verbatim so the
# site can show exactly which questions each page is answering.
EPISTEMIC_QUESTIONS = (
    "What do we know?",
    "What do we think we know?",
    "What are we assuming?",
    "What do we not know?",
    "What would change our conclusion?",
    "What experiment would resolve it?",
)


@dataclass
class TopicReport:
    topic: Topic
    claims: list[Claim]
    records: list[EvidenceRecord]
    strategies: list[Strategy]
    attacks: list[Attack]
    questions: list[Question]
    experiments: list[ExperimentResult]
    contradictions: list[Contradiction]
    tournament: dict[str, Any] | None
    source_status: list[SourceStatus]
    status_history: list[dict[str, Any]]

    # -- headline numbers -------------------------------------------------
    def statistics(self) -> dict[str, Any]:
        return library_statistics(self.claims, self.records)

    def derived(self) -> list[dict[str, Any]]:
        out = []
        for proposal, context in derive_library_claims(self.topic, self.claims, self.records):
            out.append(
                {
                    "text": proposal.text,
                    "label": proposal.label,
                    "context_numbers": [str(n) for n in context],
                    "limitations": proposal.limitations,
                }
            )
        return out

    def unknowns(self) -> list[dict[str, str]]:
        """Explicit statements of what is missing. Never omitted, never guessed."""
        unknowns: list[dict[str, str]] = []
        supported = [c for c in self.claims if c.verification.verdict == "supported"]
        if not supported:
            unknowns.append(
                {
                    "question": "What do we know?",
                    "answer": "UNKNOWN. No claim for this question passed full verification.",
                    "resolve_with": "Retrieve the authoritative source for this subject and re-run the cycle.",
                }
            )
        if not self.experiments:
            unknowns.append(
                {
                    "question": "What experiment would resolve it?",
                    "answer": (
                        "No experiment has been run for this question yet. The tournament's experimental criterion "
                        "therefore contributes zero for every candidate, by construction."
                    ),
                    "resolve_with": (
                        "Add a runnable experiment to the catalogue whose keywords match this topic, or retrieve "
                        "measured data from a registered source."
                    ),
                }
            )
        unreachable = [s for s in self.source_status if s.live_status in {"unreachable", "error"}]
        if unreachable:
            unknowns.append(
                {
                    "question": "What do we not know?",
                    "answer": (
                        "These registered sources could not be reached, so their evidence is absent from this page: "
                        + ", ".join(sorted(s.source_id for s in unreachable))
                        + "."
                    ),
                    "resolve_with": "Confirm network egress from the run environment, then re-run.",
                }
            )
        partial = [c for c in self.claims if c.verification.verdict == "partially_supported"]
        if partial:
            unknowns.append(
                {
                    "question": "What do we think we know?",
                    "answer": (
                        f"{len(partial)} claim(s) are only partially supported by their cited document. "
                        "They are listed with their coverage score and are not presented as established."
                    ),
                    "resolve_with": "Retrieve the fuller source document for those claims.",
                }
            )
        return unknowns

    def to_dict(self) -> dict[str, Any]:
        stats = self.statistics()
        winner = None
        if self.tournament and self.tournament.get("winner"):
            winner = self.tournament["winner"]
            for strategy in self.strategies:
                if strategy.strategy_id == winner:
                    winner = {
                        "strategy_id": strategy.strategy_id,
                        "persona": f"{strategy.persona_code} - {strategy.persona_name}",
                        "title": strategy.title,
                        "score": self.tournament.get("scores", {}).get(strategy.strategy_id),
                    }
                    break
        return {
            "topic": self.topic.to_dict(),
            "statistics": stats,
            "derived": self.derived(),
            "unknowns": self.unknowns(),
            "epistemic_questions": list(EPISTEMIC_QUESTIONS),
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "text": c.text,
                    "quote": c.quote,
                    "source_name": c.source_name,
                    "url": c.url,
                    "evidence_class": c.evidence_class,
                    "evidence_class_label": EVIDENCE_LABEL.get(c.evidence_class, c.evidence_class),
                    "evidence_rank": c.evidence_rank,
                    "confidence": c.confidence,
                    "verdict": c.verification.verdict,
                    "coverage": c.verification.coverage,
                    "quote_match": c.verification.quote_match,
                    "missing_numbers": c.verification.missing_numbers,
                    "reasons": c.verification.reasons,
                    "limitations": c.limitations,
                    "recorded_at": c.recorded_at,
                    "evidence_id": c.evidence_id,
                }
                for c in sorted(self.claims, key=lambda c: (c.evidence_rank, -c.verification.coverage, c.claim_id))
            ],
            "documents": [
                {
                    "evidence_id": r.evidence_id,
                    "title": r.title,
                    "url": r.url,
                    "source_name": r.source_name,
                    "evidence_class": r.evidence_class,
                    "evidence_class_label": EVIDENCE_LABEL.get(r.evidence_class, r.evidence_class),
                    "published_at": r.published_at,
                    "retrieved_at": r.retrieved_at,
                    "is_live": r.is_live,
                    "is_fixture": r.is_fixture,
                    "content_hash": r.content_hash,
                    "bytes_read": r.bytes_read,
                    "notes": r.notes,
                }
                for r in sorted(self.records, key=lambda r: (r.evidence_rank, r.evidence_id))
            ],
            "strategies": [
                {
                    "strategy_id": s.strategy_id,
                    "persona": f"{s.persona_code} - {s.persona_name}",
                    "persona_code": s.persona_code,
                    "persona_brief": s.persona_brief,
                    "title": s.title,
                    "argument": s.argument,
                    "supporting_claim_ids": s.supporting_claim_ids,
                    "assumptions": s.assumptions,
                    "predicted_outcomes": s.predicted_outcomes,
                    "falsifier": s.falsifier,
                    "status": s.status,
                    "scorecard": s.scorecard,
                    "limitations": s.limitations,
                }
                for s in sorted(self.strategies, key=lambda s: -float(s.scorecard.get("total", 0.0)))
            ],
            "attacks": [
                {
                    "attack_id": a.attack_id,
                    "strategy_id": a.strategy_id,
                    "critic": a.critic,
                    "attack_type": a.attack_type,
                    "statement": a.statement,
                    "severity": a.severity,
                    "outcome": a.outcome,
                    "claim_refs": a.claim_refs,
                }
                for a in sorted(self.attacks, key=lambda a: (a.strategy_id, a.severity, a.attack_id))
            ],
            "questions": [
                {"id": q.id, "text": q.text, "origin": q.origin, "priority": q.priority, "status": q.status}
                for q in sorted(self.questions, key=lambda q: (-q.priority, q.id))
            ],
            "experiments": [e.to_dict() for e in self.experiments],
            "contradictions": [c.to_dict() for c in self.contradictions],
            "tournament": self.tournament,
            "winner": winner,
            "source_status": [s.to_dict() for s in self.source_status],
            "status_history": self.status_history,
            "generated_at": utcnow_iso(),
        }


def _topic_status_history(library) -> list[dict[str, Any]]:
    from ..util import read_jsonl

    history: list[dict[str, Any]] = []
    for row in read_jsonl(library.path("topics")):
        history.append(
            {
                "topic_id": row.get("topic_id"),
                "status": row.get("status"),
                "last_updated": row.get("last_updated"),
                "line": row.get("_line"),
            }
        )
    return history


def order_claims_for_reading(claims: list[Claim]) -> list[Claim]:
    """Order a topic's claims so the reader meets the most substantive ones first.

    The rule is deliberately simple and published: claims that passed verification
    come before those needing review, quantified claims before purely descriptive
    ones, and stronger evidence classes before weaker. Nothing is dropped - the
    ordering only decides what is read first. Every claim keeps its own verdict
    badge, so this cannot promote anything.
    """
    def key(claim: Claim):
        verdict_rank = {"supported": 0, "partially_supported": 1, "unsupported": 2, "contradicted": 3}
        quantified = 0 if extract_numbers(claim.text) or extract_dates(claim.text) else 1
        derived = 0 if claim.claim_kind == "derived" else 1
        return (
            derived,
            verdict_rank.get(claim.verification.verdict, 4),
            quantified,
            claim.evidence_rank,
            claim.claim_id,
        )

    return sorted(claims, key=key)


def build_topic_report(
    library,
    topic: Topic,
    *,
    source_status: list[SourceStatus] | None = None,
) -> TopicReport:
    """Assemble the report object for one topic from the library."""
    claims = order_claims_for_reading(library.claims_for_topic(topic.topic_id))
    evidence_ids = {c.evidence_id for c in claims}
    records = [library.evidence[eid] for eid in evidence_ids if eid in library.evidence]
    strategies = library.strategies_for_topic(topic.topic_id)
    attacks = [a for s in strategies for a in library.attacks_for_strategy(s.strategy_id)]
    questions = library.questions_for_topic(topic.topic_id)
    experiments = library.experiments_for_topic(topic.topic_id)
    contradictions = [c for c in library.contradictions.values() if c.topic_id == topic.topic_id]
    tournament = None
    for row in library.tournaments.values():
        if row.get("topic_id") == topic.topic_id:
            tournament = row
            break
    # Only the sources polled for this topic; a status row written before the
    # topic stamp existed carries no topics and is shown run-wide rather than
    # silently dropped.
    status = [
        s
        for s in (source_status or [])
        if not getattr(s, "topics", None) or topic.topic_id in s.topics
    ]
    history = [row for row in _topic_status_history(library) if row.get("topic_id") == topic.topic_id]
    return TopicReport(
        topic=topic,
        claims=claims,
        records=records,
        strategies=strategies,
        attacks=attacks,
        questions=questions,
        experiments=experiments,
        contradictions=contradictions,
        tournament=tournament,
        source_status=status,
        status_history=history,
    )


def build_site_data(
    library,
    *,
    source_matrix: list[dict[str, Any]],
    source_status: list[SourceStatus],
    irregularities: list[Irregularity],
    failures: list[Failure],
    elo_payload: dict[str, Any],
    calibration: dict[str, Any],
    requirements: list[dict[str, Any]],
    methodology: dict[str, Any],
    mode: str,
    run_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build every JSON payload the site and external consumers read."""
    topics = sorted(library.active_topics(), key=lambda t: t.topic_id)
    reports = [build_topic_report(library, topic, source_status=source_status) for topic in topics]

    meta = build_meta_knowledge(
        library.claims.values(),
        library.evidence.values(),
        library.attacks.values(),
        library.strategies.values(),
        library.experiments.values(),
        elo_leaderboard=elo_payload.get("leaderboard", []),
    )

    payload = {
        "generated_at": utcnow_iso(),
        "run_id": library.run_id,
        "engine": {
            "name": "SelfLearn",
            "version": __version__,
            "repository": ENGINE_REPO_URL,
            "site": ENGINE_SITE_URL,
        },
        "mode": mode,
        "run_summary": run_summary,
        "counts": {
            "topics": len(topics),
            "claims": len(library.claims),
            "documents": len(library.evidence),
            "strategies": len(library.strategies),
            "attacks": len(library.attacks),
            "questions": len(library.questions),
            "experiments": len(library.experiments),
            "discoveries": len(library.discoveries),
            "contradictions": len(library.contradictions),
            "irregularities": len(library.irregularities),
            "failures": len(library.failures),
        },
        "lifecycle_states": list(LIFECYCLE_STATES),
        "topics": [r.to_dict() for r in reports],
        "sources": {
            "matrix": source_matrix,
            "status": [s.to_dict() for s in source_status],
            "reliability": meta.sources,
        },
        "meta_knowledge": meta.to_dict(),
        "elo": elo_payload,
        "calibration": calibration,
        "irregularities": [i.to_dict() for i in irregularities],
        "failures": [f.to_dict() for f in failures],
        "contradictions": [c.to_dict() for c in library.contradictions.values()],
        "requirements": requirements,
        "methodology": methodology,
        "experiments": [e.to_dict() for e in library.experiments.values()],
    }
    payload["checks"] = {
        "fixture_documents": sum(1 for r in library.evidence.values() if r.is_fixture),
        "unsupported_claims": sum(1 for c in library.claims.values() if c.verification.verdict == "unsupported"),
        "claims_without_link": sum(1 for c in library.claims.values() if not str(c.url).startswith("http")),
        "unresolved_contradictions": sum(1 for c in library.contradictions.values() if c.resolution == "unresolved"),
        "irregularity_counts": {
            severity: sum(1 for i in irregularities if i.severity == severity)
            for severity in ("error", "warning", "info")
        },
    }
    return payload


def topic_slug(topic: Topic) -> str:
    from ..util import slugify

    return topic.slug or slugify(topic.title)


def short_topic_id(topic: Topic) -> str:
    return topic.topic_id


def next_question_summary(questions: Iterable[Question]) -> list[str]:
    return [truncate(q.text, 240) for q in sorted(questions, key=lambda q: -q.priority)][:5]


def claim_anchor(claim: Claim) -> str:
    return f"claim-{claim.claim_id}"


def stable_page_id(prefix: str, *parts: Any) -> str:
    return stable_id(prefix, *parts)
