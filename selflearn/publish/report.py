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

from dataclasses import dataclass, field
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
from ..fetch.changes import mechanism_table as change_mechanism_table
from ..learn.substance import score_claim, substance_rule, substance_summary
from ..think.invention import invention_rule
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
    # Claims a later cycle no longer produces (see Claim.superseded). Kept here so
    # the page can say how many were retired and why, instead of quietly dropping
    # statements that were published in an earlier cycle.
    retired_claims: list[Claim] = field(default_factory=list)
    retired_strategies: list[Strategy] = field(default_factory=list)
    retired_attacks: list[Attack] = field(default_factory=list)
    retired_questions: list[Question] = field(default_factory=list)

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
                    "claim_kind": c.claim_kind,
                    "context_numbers": c.context_numbers,
                    "cited_claim_ids": c.cited_claim_ids,
                    "substance": c.substance or score_claim(c).to_dict(),
                }
                # Reading order is the published substance rule; see
                # order_claims_for_reading. Nothing is dropped by this sort.
                for c in self.claims
            ],
            "synthesis": [
                {
                    "claim_id": c.claim_id,
                    "text": c.text,
                    "cited_claim_ids": c.cited_claim_ids,
                    "context_numbers": c.context_numbers,
                    "limitations": c.limitations,
                    "verdict": c.verification.verdict,
                    "reasons": c.verification.reasons,
                    "citations": [
                        {
                            "claim_id": other.claim_id,
                            "text": other.text,
                            "source_name": other.source_name,
                            "url": other.url,
                            "evidence_id": other.evidence_id,
                            "verdict": other.verification.verdict,
                        }
                        for other in self.claims
                        if other.claim_id in set(c.cited_claim_ids)
                    ],
                }
                for c in self.claims
                if c.claim_kind == "synthesis"
            ],
            "substance": substance_summary(self.claims),
            "retired": [
                {
                    "claim_id": c.claim_id,
                    "text": c.text,
                    "claim_kind": c.claim_kind,
                    "superseded": c.superseded,
                    "recorded_at": c.recorded_at,
                }
                for c in self.retired_claims
            ]
            + [
                {
                    "claim_id": st.strategy_id,
                    "text": st.title,
                    "claim_kind": f"brief ({st.persona_code})",
                    "superseded": st.superseded,
                    "recorded_at": st.created_at,
                }
                for st in self.retired_strategies
            ]
            + [
                {
                    "claim_id": a.attack_id,
                    "text": a.statement,
                    "claim_kind": f"criticism ({a.critic})",
                    "superseded": a.superseded,
                    "recorded_at": a.created_at,
                }
                for a in self.retired_attacks
            ]
            + [
                {
                    "claim_id": q.id,
                    "text": q.text,
                    "claim_kind": f"open question ({q.origin})",
                    "superseded": q.superseded,
                    "recorded_at": q.created_at,
                }
                for q in self.retired_questions
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

    The ordering rule is the published substance score
    (:mod:`selflearn.learn.substance`), with two overrides that matter more than
    any lexical feature:

    * the engine's own computed statements (``derived``) come first, because they
      tell the reader how much of what follows is supported at all;
    * a claim that failed verification is never placed above one that passed.

    Nothing is dropped - the ordering only decides what is read first, and every
    claim keeps its own verdict and substance label, so this cannot promote
    anything.
    """
    ensure_substance(claims)

    def key(claim: Claim):
        verdict_rank = {"supported": 0, "partially_supported": 1, "unsupported": 2, "contradicted": 3}
        substance = claim.substance or {}
        return (
            0 if claim.claim_kind == "derived" else 1,
            verdict_rank.get(claim.verification.verdict, 4),
            -float(substance.get("total", 0.0)),
            int(claim.evidence_rank or 9),
            claim.claim_id,
        )

    return sorted(claims, key=key)


def ensure_substance(claims: list[Claim]) -> dict[str, Any]:
    """Score every claim that has no stored substance record, in place.

    Claims written before the substance rule existed have no score, and the rule
    itself may be revised; either way the published page must show a score
    computed by the current rule rather than an empty cell. Returns the summary
    for the set, which is what the index and the method page quote.
    """
    for claim in claims:
        if not claim.substance:
            claim.substance = score_claim(claim).to_dict()
    return substance_summary(claims)


def build_topic_report(
    library,
    topic: Topic,
    *,
    source_status: list[SourceStatus] | None = None,
) -> TopicReport:
    """Assemble the report object for one topic from the library."""
    all_topic_claims = library.claims_for_topic(topic.topic_id)
    # A superseded statement is one a later cycle would no longer produce, because
    # the rule that composed it changed or a claim it cited is gone. It stays in
    # the library - the streams are append-only - but it is not published as a
    # current finding; the count and the reason are shown instead.
    retired = [c for c in all_topic_claims if c.superseded]
    claims = order_claims_for_reading([c for c in all_topic_claims if not c.superseded])
    evidence_ids = {c.evidence_id for c in claims}
    records = [library.evidence[eid] for eid in evidence_ids if eid in library.evidence]
    # The same rule applies to the records built on top of a retired claim: a brief
    # is an inference over the claims it quotes, a criticism is a criticism of that
    # brief, and a gap question is a question about a claim. They are withdrawn with
    # it, listed under "Retired", and not published as competing answers.
    all_strategies = library.strategies_for_topic(topic.topic_id)
    strategies = [st for st in all_strategies if not st.superseded]
    retired_strategies = [st for st in all_strategies if st.superseded]
    all_attacks = [a for st in all_strategies for a in library.attacks_for_strategy(st.strategy_id)]
    attacks = [a for a in all_attacks if not a.superseded]
    retired_attacks = [a for a in all_attacks if a.superseded]
    all_questions = library.questions_for_topic(topic.topic_id)
    questions = [q for q in all_questions if not q.superseded]
    retired_questions = [q for q in all_questions if q.superseded]
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
        retired_claims=retired,
        records=records,
        strategies=strategies,
        attacks=attacks,
        questions=questions,
        retired_strategies=retired_strategies,
        retired_attacks=retired_attacks,
        retired_questions=retired_questions,
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
        "substance": ensure_substance(list(library.claims.values())),
        "substance_rule": substance_rule(),
        "invention_rule": invention_rule(),
        "topic_proposals": list(run_summary.get("topic_proposals") or []),
        "change_scan": dict(run_summary.get("change_scan") or {}),
        "change_mechanisms": change_mechanism_table(),
        "link_check": load_link_check(),
        "credentials": credential_table(),
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


def load_link_check(root: Any = None) -> dict[str, Any]:
    """The committed URL register, as evidence rather than as a fresh assertion.

    ``reports/link_check.json`` is written by ``tools/verify_links.py`` and
    committed by the Tests workflow, which runs on a host with unrestricted
    egress. The site publishes what that file records - including the label of
    the machine that produced it - and says so. A sandbox whose egress is
    restricted reports most hosts as ``unreachable``, which is a property of the
    machine; publishing the label is what keeps that from reading as a list of
    broken links.
    """
    import json
    from pathlib import Path

    from ..config import ROOT

    base = Path(root) if root else ROOT
    path = base / "reports" / "link_check.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {
            "available": False,
            "detail": "No committed link check found. Run `python3 tools/verify_links.py` to produce one.",
        }
    results = payload.get("results") or []
    by_source: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        by_source.setdefault(str(row.get("source_id") or "other"), []).append(
            {
                "url": row.get("url"),
                "field": row.get("field"),
                "group": row.get("group"),
                "status": row.get("status"),
                "ok": bool(row.get("ok")),
                "final_url": row.get("final_url"),
                "error": (row.get("error") or "")[:240],
                "elapsed_seconds": row.get("elapsed_seconds"),
            }
        )
    return {
        "available": True,
        "generated_at": payload.get("generated_at"),
        "label": payload.get("label") or "unlabelled run",
        "note": payload.get("note", ""),
        "checked": payload.get("checked", len(results)),
        "ok": payload.get("ok", 0),
        "failed": payload.get("failed", 0),
        "by_status": payload.get("by_status", {}),
        "by_source": by_source,
    }


def credential_table() -> list[dict[str, Any]]:
    """Every source that names a credential, and whether it is transmitted.

    Two different facts, kept apart on purpose: whether the variable is required,
    and whether an adapter actually puts it on the request. Conflating them is
    how a source ends up reported as enabled while every call goes out
    unauthenticated.
    """
    import os

    from ..fetch.registry import REGISTRY
    from ..fetch.sources import CREDENTIAL_MECHANISMS, credential_status

    rows: list[dict[str, Any]] = []
    for spec in sorted(REGISTRY.values(), key=lambda s: s.source_id):
        if not spec.key_env:
            continue
        status = credential_status(spec)
        mechanism = CREDENTIAL_MECHANISMS.get(spec.source_id)
        rows.append(
            {
                "source_id": spec.source_id,
                "name": spec.name,
                "env": spec.key_env,
                "present": bool(os.environ.get(spec.key_env)),
                "required": bool(spec.requires_key),
                "state": status["state"],
                "detail": status["detail"],
                "mechanism": (
                    {
                        "kind": mechanism.kind,
                        "name": mechanism.name,
                        "prefix": mechanism.prefix,
                        "docs_url": mechanism.docs_url,
                        "quote": mechanism.quote,
                        "verified_at": mechanism.verified_at,
                        "applied_by": mechanism.applied_by,
                    }
                    if mechanism
                    else None
                ),
                "key_url": spec.key_url,
                "docs_url": spec.docs_url,
                "rate_limit_note": spec.rate_limit_note,
            }
        )
    return rows


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
