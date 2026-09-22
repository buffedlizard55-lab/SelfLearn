"""The research loop.

One call to :func:`run_cycle` performs one bounded pass of:

discover -> retrieve -> verify -> compete -> criticise -> experiment -> rank ->
curiosity -> audit -> publish

and returns a summary. The loop is built to be driven by an external scheduler
(GitHub Actions on a cron, or any queue), which is what the design document means
by "event-driven rather than literally nonstop": the graph determines what work
exists, and workers run continuously against it.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import __version__
from .config import (
    BUDGET,
    EVIDENCE_HIERARCHY,
    FIXTURE_DIR,
    REQUIREMENTS_VERSION,
    SEED_DIR,
    SITE_DATA_DIR,
    SITE_DIR,
    THRESHOLDS,
)
from .experiment.catalogue import catalogue as experiment_catalogue
from .experiment.catalogue import experiments_for_topic
from .experiment.runner import run_experiment, to_evidence, to_result
from .fetch.collector import Collector, summarise_status
from .fetch.net import HttpClient, NetworkUnavailable
from .fetch.registry import registry_summary, source_matrix
from .learn.calibration import active_thresholds, run_calibration, thresholds_in_force
from .learn.store import Library
from .learn.substance import score_claim, substance_summary
from .learn.synthesis import synthesis_claim_id, synthesis_evidence_id, synthesise
from .models import Claim, Discovery, Irregularity, SourceStatus, Topic
from .publish.report import build_site_data, topic_slug
from .publish.site import build_site
from .think.competition import cross_domain_claims, generate_strategies, strategy_numbers_ok
from .think.critic import critique_strategy
from .think.discovery import attention_from_records, discover_questions
from .think.elo import EloTable
from .think.manager import build_plan, choose_sources, evidence_rank_mix, topic_transition
from .think.personas import personas_for
from .think.tournament import run_tournament
from .util import load_json, save_json, sha256_text, slugify, stable_id, to_jsonable, utcnow_iso, write_text
from .verify.audit import (
    audit_run_summary,
    check_coverage,
    check_fixtures,
    check_links,
    recheck_claims,
    render_markdown,
    summarise,
)
from .verify.contradiction import detect_contradictions
from .verify.grounding import ground_evidence
from .verify.verifier import (
    confidence_label,
    independent_source_count,
    verify_claim,
    verify_derived,
    verify_synthesis,
)

LOG = logging.getLogger("selflearn.loop")


@dataclass
class CycleResult:
    run_id: str
    mode: str
    counts: dict[str, int] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)
    source_summary: dict[str, Any] = field(default_factory=dict)
    irregularities: list[Irregularity] = field(default_factory=list)
    published: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "counts": self.counts,
            "plan": self.plan,
            "sources": self.source_summary,
            "irregularities": summarise(self.irregularities),
            "published": self.published,
            "notes": self.notes,
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def state_path(root: Path, name: str) -> Path:
    """Resolve a state file relative to ``root`` (keeps non-default roots working)."""
    return Path(root) / "state" / name


def load_seed_topics(path: Path | None = None) -> list[Topic]:
    """Read the seed question set from ``data/seeds/topics.json``."""
    target = Path(path or (SEED_DIR / "topics.json"))
    payload = load_json(target, default=[]) or []
    topics: list[Topic] = []
    for row in payload:
        title = row.get("title", "untitled")
        topics.append(
            Topic(
                topic_id=row.get("topic_id") or stable_id("topic", title),
                title=title,
                slug=row.get("slug") or slugify(title),
                question=row.get("question", ""),
                status=row.get("status", "new"),
                origin=row.get("origin", "seed"),
                keywords=list(row.get("keywords", [])),
                signal=dict(row.get("signal", {})),
                source_ids=list(row.get("source_ids", [])),
                parent_topic_id=row.get("parent_topic_id"),
                notes=row.get("notes", ""),
            )
        )
    return topics


def build_claims(
    topic: Topic,
    records: Iterable[Any],
    existing: list[Claim],
    *,
    thresholds,
    max_claims: int = BUDGET.max_claims_per_topic,
) -> list[Claim]:
    """Ground, verify and label every claim extracted in this cycle."""
    produced: list[Claim] = []
    seen_texts = {claim.text for claim in existing}
    budget_left = max(0, max_claims - len(existing))
    for record in records:
        if budget_left <= 0:
            break
        for proposal in ground_evidence(record, max_claims=8):
            if budget_left <= 0:
                break
            if proposal.text in seen_texts:
                continue
            seen_texts.add(proposal.text)
            verification = verify_claim(proposal.text, proposal.quote, record.text, thresholds=thresholds)
            limitations = proposal.limitations
            if record.source_id == "arxiv":
                limitations = (limitations + " arXiv preprint: not peer reviewed.").strip()
            provisional = Claim(
                claim_id=stable_id("cl", topic.topic_id, record.evidence_id, proposal.text),
                topic_id=topic.topic_id,
                text=proposal.text,
                evidence_id=record.evidence_id,
                source_name=record.source_name,
                url=record.url,
                quote=proposal.quote,
                evidence_class=record.evidence_class,
                evidence_rank=record.evidence_rank,
                confidence="unknown",
                verification=verification,
                limitations=limitations,
            )
            independent = independent_source_count(provisional, existing + produced)
            provisional.confidence = confidence_label(verification.verdict, record.evidence_rank, independent)
            # The substance score is a reading aid computed from the finished
            # verification record; it never feeds back into the verdict.
            provisional.substance = score_claim(provisional).to_dict()
            produced.append(provisional)
            budget_left -= 1
    return produced


def derived_evidence_id(topic_id: str) -> str:
    """Identifier of the computation record backing a topic's derived claims."""
    return f"derived-{topic_id}"


def build_derived_claims(
    topic: Topic,
    claims: list[Claim],
    records: list[Any],
    *,
    snapshot_dir: Path | None = None,
) -> list[Claim]:
    """Verify and materialise the library-statistics claims for one topic.

    These are the only sentences the engine composes itself. Their provenance is
    the computation, not a document, so they are marked ``claim_kind="derived"``,
    carry the figures they were computed from, and get a human-readable
    computation record on disk for review.
    """
    from .learn.aggregate import derive_library_claims

    evidence_id = derived_evidence_id(topic.topic_id)
    derived: list[Claim] = []
    contexts: dict[str, list[str]] = {}
    rendered: list[str] = []
    for proposal, context in derive_library_claims(topic, claims, records):
        context_strings = [str(n) for n in context]
        verification = verify_derived(proposal.text, context_strings)
        claim_id = stable_id("cl", topic.topic_id, "derived", proposal.text)
        contexts[claim_id] = context_strings
        rendered.append(proposal.text)
        derived.append(
            Claim(
                claim_id=claim_id,
                topic_id=topic.topic_id,
                text=proposal.text,
                evidence_id=evidence_id,
                source_name="SelfLearn library computation",
                url="",
                quote="",
                evidence_class="reproduced_experiment",
                evidence_rank=2,
                confidence="medium" if verification.verdict == "supported" else "unknown",
                verification=verification,
                claim_kind="derived",
                context_numbers=context_strings,
                limitations=proposal.limitations,
            )
        )
    if derived and snapshot_dir is not None:
        _write_derived_record(topic, derived, contexts, rendered, Path(snapshot_dir))
    return derived


def _write_derived_record(
    topic: Topic,
    derived: list[Claim],
    contexts: dict[str, list[str]],
    rendered: list[str],
    snapshot_dir: Path,
) -> Path:
    """Store the computation behind the derived claims so a reviewer can check it."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            f"Source: SelfLearn library computation for {topic.topic_id}",
            f"Question: {topic.question}",
            "These statements are computed by the engine from its own records. They assert nothing about the world.",
            "Statements and the figures each was computed from:",
            *[f"{statement} [figures: {', '.join(contexts[claim.claim_id])}]" for statement, claim in zip(rendered, derived)],
        ]
    )
    payload = {
        "evidence_id": derived_evidence_id(topic.topic_id),
        "source_id": "selflearn_library",
        "source_name": "SelfLearn library computation",
        "url": "",
        "title": f"Library computation for {topic.title}",
        "text": text,
        "content_hash": sha256_text(text),
        "evidence_class": "reproduced_experiment",
        "evidence_rank": 2,
        "is_fixture": False,
        "is_live": True,
        "derived_contexts": contexts,
        "claim_ids": [claim.claim_id for claim in derived],
        "written_at": utcnow_iso(),
    }
    path = snapshot_dir / f"{payload['evidence_id']}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def retire_stale_synthesis(topic: Topic, existing: list[Claim], kept: list[Claim]) -> list[Claim]:
    """Mark the synthesis statements this cycle would no longer produce.

    A synthesis statement is composed by a rule, and the rule can be corrected -
    the first version of it read date fragments as quantities and published
    "one reports 02 and the other reports 04". The streams are append-only, so the
    correction cannot delete the old record; what it can do is stop publishing it
    as current and say why. The record stays in ``library/claims.jsonl`` and the
    reason is stored on it.
    """
    kept_ids = {claim.claim_id for claim in kept}
    retired: list[Claim] = []
    for claim in existing:
        if claim.claim_kind != "synthesis" or claim.topic_id != topic.topic_id:
            continue
        if claim.claim_id in kept_ids or claim.superseded:
            continue
        claim.superseded = (
            f"Superseded {utcnow_iso()}: a re-run of the synthesis rules no longer produces this statement. "
            "It is kept in the library and is not published as a current finding."
        )
        retired.append(claim)
    return retired


def build_synthesis_claims(
    topic: Topic,
    claims: list[Claim],
    *,
    snapshot_dir: Path | None = None,
    limit: int = 6,
    existing: list[Claim] | None = None,
) -> list[Claim]:
    """Compose, verify and materialise this topic's cross-document statements.

    A proposal that does not survive :func:`~selflearn.verify.verifier.verify_synthesis`
    is dropped rather than published with a warning: an unsupported
    cross-document statement is the most misleading thing this engine could say.
    Every statement that is kept records the claims it cites and the figures it
    was allowed to use, and the audit recomputes both on the next cycle.
    """
    evidence_id = synthesis_evidence_id(topic.topic_id)
    kept: list[Claim] = []
    record_lines: list[str] = []
    for proposal in synthesise(topic.topic_id, claims, limit=limit):
        cited = [c for c in claims if c.claim_id in set(proposal.cited_claim_ids)]
        verification = verify_synthesis(proposal.text, cited, proposal.context_numbers)
        if verification.verdict != "supported":
            continue
        claim = Claim(
            claim_id=synthesis_claim_id(topic.topic_id, proposal),
            topic_id=topic.topic_id,
            text=proposal.text,
            evidence_id=evidence_id,
            source_name="Cross-document synthesis of cited claims",
            url="",
            quote="",
            evidence_class="reproduced_experiment",
            evidence_rank=2,
            confidence="medium",
            verification=verification,
            claim_kind="synthesis",
            context_numbers=list(proposal.context_numbers),
            cited_claim_ids=list(proposal.cited_claim_ids),
            limitations=proposal.limitations,
        )
        claim.substance = score_claim(claim).to_dict()
        kept.append(claim)
        record_lines.append(
            f"{claim.claim_id} [{proposal.kind}] cites {', '.join(proposal.cited_claim_ids)}; "
            f"allowed figures: {', '.join(proposal.context_numbers)}"
        )
    if kept and snapshot_dir is not None:
        _write_synthesis_record(topic, kept, record_lines, Path(snapshot_dir))
    return kept


def retire_dependents(library: "Library", retired_claims: list[Claim]) -> dict[str, list[Any]]:
    """Withdraw the records that were built on top of a retired claim.

    A brief is an inference over the claims it quotes, a criticism is a criticism
    of that brief, and a gap question is a question about a claim. None of them can
    outlive the claim they rest on. This is the second half of the same fix that
    retired the synthesis statements: the first version of that layer published a
    false sentence, and the sentence had already been copied into 57 competing
    briefs, 15 criticisms and 2 open questions. Retiring the claim alone left all
    of those published.

    Nothing is deleted. Each record keeps its text and gains a reason.
    """
    retired_ids = {claim.claim_id for claim in retired_claims}
    if not retired_ids:
        return {"strategies": [], "attacks": [], "questions": []}
    reason = (
        f"Withdrawn {utcnow_iso()}: a claim this record quotes has been superseded, so this record is not "
        "published as current. It remains in the library."
    )
    strategies: list[Strategy] = []
    attacks: list[Attack] = []
    questions: list[Question] = []
    for strategy in library.strategies.values():
        if strategy.superseded:
            continue
        quoted = [cid for cid in strategy.supporting_claim_ids if cid in retired_ids]
        if quoted:
            strategy.superseded = reason + f" Retired claim(s): {', '.join(sorted(quoted))}."
            strategies.append(strategy)
    retired_strategy_ids = {s.strategy_id for s in strategies}
    for attack in library.attacks.values():
        if attack.superseded:
            continue
        if attack.strategy_id in retired_strategy_ids:
            attack.superseded = reason + f" Its brief {attack.strategy_id} quotes a retired claim."
            attacks.append(attack)
    for question in library.questions.values():
        if question.superseded:
            continue
        quoted = sorted(cid for cid in retired_ids if cid in (question.text or ""))
        if quoted:
            question.superseded = reason + f" Retired claim(s): {', '.join(quoted)}."
            question.status = "superseded"
            questions.append(question)
    return {"strategies": strategies, "attacks": attacks, "questions": questions}


def rebuild_synthesis(
    topic: Topic,
    claims: list[Claim],
    *,
    snapshot_dir: Path | None = None,
    limit: int = 6,
    existing: list[Claim] | None = None,
) -> tuple[list[Claim], list[Claim]]:
    """Compose this topic's synthesis claims and retire the ones that no longer hold.

    Returns ``(kept, retired)``. Both are written back to the library: the kept
    statements as current claims, the retired ones with a supersession reason.
    """
    kept = build_synthesis_claims(topic, claims, snapshot_dir=snapshot_dir, limit=limit)
    retired = retire_stale_synthesis(topic, existing or [], kept)
    return kept, retired


def _write_synthesis_record(
    topic: Topic,
    claims: list[Claim],
    record_lines: list[str],
    snapshot_dir: Path,
) -> Path:
    """Store the composition record behind the synthesis claims."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            f"Source: cross-document synthesis for {topic.topic_id}",
            f"Question: {topic.question}",
            "These statements combine figures that were already verified in the documents cited below.",
            "No figure was averaged, summed or otherwise computed; a statement needing arithmetic is not written.",
            "Statements, their citations and the figures each was allowed to use:",
            *record_lines,
        ]
    )
    payload = {
        "evidence_id": synthesis_evidence_id(topic.topic_id),
        "source_id": "selflearn_synthesis",
        "source_name": "Cross-document synthesis of cited claims",
        "url": "",
        "title": f"Cross-document synthesis for {topic.title}",
        "text": text,
        "content_hash": sha256_text(text),
        "evidence_class": "reproduced_experiment",
        "evidence_rank": 2,
        "is_fixture": False,
        "is_live": True,
        "claim_ids": [claim.claim_id for claim in claims],
        "citations": {claim.claim_id: claim.cited_claim_ids for claim in claims},
        "context_numbers": {claim.claim_id: claim.context_numbers for claim in claims},
        "written_at": utcnow_iso(),
    }
    path = snapshot_dir / f"{payload['evidence_id']}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def attention_by_topic(library: Library) -> dict[str, float]:
    """Measured attention signals, for the topics where a signal exists at all."""
    signals: dict[str, float] = {}
    for topic in library.active_topics():
        records = [
            library.evidence[claim.evidence_id]
            for claim in library.claims_for_topic(topic.topic_id)
            if claim.evidence_id in library.evidence
        ]
        value = attention_from_records(records)
        if value is not None:
            signals[topic.topic_id] = value
    return signals


# ---------------------------------------------------------------------------
# The cycle
# ---------------------------------------------------------------------------


def run_cycle(
    *,
    root: Path,
    mode: str = "live",
    max_topics: int | None = None,
    max_requests: int | None = None,
    allow_network: bool = True,
    publish: bool = True,
    run_experiments: bool = True,
    seeds_path: Path | None = None,
) -> CycleResult:
    """Run one full cycle of the research loop and (optionally) publish the site."""
    root = Path(root)
    run_id = stable_id("run", utcnow_iso(), mode)
    result = CycleResult(run_id=run_id, mode=mode)
    library = Library.load(root, run_id=run_id)

    # -- 1. seed questions ---------------------------------------------------
    seeds = load_seed_topics(seeds_path)
    if seeds:
        library.add_topics(seeds)
        result.notes.append(f"{len(seeds)} question(s) loaded from the seed file.")

    # -- 2. calibrate the verifier ------------------------------------------
    cases_path = FIXTURE_DIR / "verification_cases.jsonl"
    calibration_payload: dict[str, Any] = {}
    if cases_path.exists():
        calibration_payload = run_calibration(cases_path, apply=True, state_path=state_path(root, "calibration.json"))
        thresholds = active_thresholds()
        result.notes.append(
            f"Verification thresholds calibrated from {calibration_payload.get('case_count')} labelled cases; "
            f"accuracy at the selected point {(calibration_payload.get('selected') or {}).get('accuracy')}."
        )
    else:
        thresholds = THRESHOLDS
        result.notes.append("No labelled case file found; the configured default thresholds are in force.")

    # -- 3. plan -------------------------------------------------------------
    signals = attention_by_topic(library)
    plan = build_plan(
        library.active_topics(),
        library.library_by_topic(),
        library.evidence,
        run_id=run_id,
        max_topics=max_topics or BUDGET.max_topics_per_cycle,
        attention_by_topic=signals,
    )
    library.add_tasks(plan.tasks)
    result.plan = plan.to_dict()
    result.notes.extend(plan.notes)

    client = HttpClient(
        max_requests=max_requests or BUDGET.max_http_requests,
        allow_network=allow_network,
    )
    collector = Collector(client, root / "evidence" / "snapshots", strict=False)
    elo = EloTable.load(state_path(root, "elo.json"))

    all_statuses: list[SourceStatus] = []
    irregularities: list[Irregularity] = list(library.irregularities.values())
    synthesis_retired: list[Claim] = []

    # -- 4. per-topic research ----------------------------------------------
    for topic in plan.selected:
        source_ids = plan.sources_by_topic.get(topic.topic_id) or choose_sources(topic)
        outcome = collector.collect(topic, source_ids)
        all_statuses.extend(outcome.statuses)
        irregularities.extend(outcome.irregularities)
        library.add_failures(outcome.failures)
        if outcome.records:
            library.add_evidence(outcome.records)

        existing = library.claims_for_topic(topic.topic_id)
        new_claims = build_claims(topic, outcome.records, existing, thresholds=thresholds)
        library.add_claims(new_claims)
        topic_claims = existing + new_claims

        contradictions = detect_contradictions(topic_claims, topic_id=topic.topic_id)
        library.add_contradictions(contradictions)

        topic_records = [
            library.evidence[claim.evidence_id] for claim in topic_claims if claim.evidence_id in library.evidence
        ]
        derived = build_derived_claims(
            topic,
            topic_claims,
            topic_records,
            snapshot_dir=root / "evidence" / "snapshots",
        )
        library.add_claims(derived)

        # Cross-document synthesis, built only from claims that are already
        # verified against their own document, and re-verified here before storage.
        synthesis, retired = rebuild_synthesis(
            topic,
            topic_claims,
            snapshot_dir=root / "evidence" / "snapshots",
            existing=existing,
        )
        library.add_claims(synthesis)
        if retired:
            library.add_claims(retired)
            synthesis_retired.extend(retired)
            irregularities.append(
                Irregularity(
                    irregularity_id=stable_id("irr", "synthesis-retired", topic.topic_id),
                    severity="info",
                    stage="synthesis",
                    topic_id=topic.topic_id,
                    summary=f"{len(retired)} cross-document statement(s) retired for {topic.topic_id}",
                    detail=(
                        "The synthesis rules no longer produce these statements, so they are marked superseded and "
                        "are not published as current findings. The records remain in library/claims.jsonl with the "
                        "reason stored on each."
                    ),
                    suggested_action="No action needed unless a reviewer believes a retired statement was correct.",
                )
            )
        topic_claims = topic_claims + [c for c in synthesis if not c.superseded]

        personas = personas_for(topic.topic_id, count=6)
        strategies = generate_strategies(topic, topic_claims, personas, library=library.library_by_topic())
        library.add_strategies(strategies)

        experiments_here = []
        if run_experiments:
            for spec in experiments_for_topic(topic, limit=1):
                exp_run = run_experiment(spec, root=root)
                if exp_run.error:
                    irregularities.append(
                        Irregularity(
                            irregularity_id=stable_id("irr", "experiment", spec.experiment_id, exp_run.error[:60]),
                            severity="warning",
                            stage="experiment",
                            topic_id=topic.topic_id,
                            summary=f"Experiment {spec.experiment_id} did not complete",
                            detail=f"{exp_run.error}. stderr: {exp_run.stderr[:400]}",
                            suggested_action="Inspect the script and re-run the command shown on the experiments page.",
                        )
                    )
                    continue
                experiment_result = to_result(exp_run, topic.topic_id)
                library.add_experiments([experiment_result])
                library.add_evidence([to_evidence(exp_run, topic.topic_id)])
                experiments_here.append(experiment_result)

        attacks = []
        for strategy in strategies:
            attacks.extend(
                critique_strategy(
                    strategy,
                    library.claims,
                    library_claims=list(library.claims.values()),
                    evidence_index=library.evidence,
                    contradictions=contradictions,
                    now_iso=utcnow_iso(),
                )
            )
        library.add_attacks(attacks)

        attacks_by_strategy: dict[str, list] = {}
        for attack in attacks:
            attacks_by_strategy.setdefault(attack.strategy_id, []).append(attack)
        tournament = run_tournament(
            topic.topic_id,
            strategies,
            library.claims,
            library.evidence,
            attacks_by_strategy,
            elo=elo,
            experiment=experiments_here[0] if experiments_here else None,
        )
        library.add_strategies(strategies)
        row = tournament.to_dict()
        row["tournament_id"] = stable_id("tour", topic.topic_id, ",".join(tournament.ranking))
        library.add_tournaments([row])

        transferred = cross_domain_claims(topic, library.library_by_topic(), limit=2)
        questions = discover_questions(topic, topic_claims, library.evidence, cross_topic_claims=transferred)
        library.add_questions(questions)
        library.add_discoveries(
            [
                Discovery(
                    discovery_id=stable_id("disc", topic.topic_id, question.id),
                    topic_id=topic.topic_id,
                    text=question.text,
                    kind="new_question" if question.origin in {"discovery", "gap"} else "finding",
                    derived_from=[claim.claim_id for claim in topic_claims[:5]],
                    confidence="low",
                )
                for question in questions[:3]
            ]
        )

        topic.status = topic_transition(
            topic, claims=topic_claims, strategies=len(strategies), experiments=len(experiments_here)
        )
        topic.last_updated = utcnow_iso()
        topic.source_ids = source_ids
        library.add_topics([topic])

        result.notes.append(
            f"{topic.topic_id}: {len(new_claims)} new claim(s) from {len(outcome.records)} document(s); "
            f"{len(strategies)} candidate(s); {len(attacks)} attack(s)."
        )

    elo.save()

    # -- 4b. open scan: invent topics and look for what changed ------------
    proposals_payload: list[dict[str, Any]] = []
    promoted_topics: list[Topic] = []
    if plan.selected:
        from .think.invention import MAX_PROPOSALS_PER_CYCLE, propose_topics, to_topic

        cycle_records = list(library.evidence.values())
        proposals = propose_topics(
            records=cycle_records,
            claims=list(library.claims.values()),
            topics=list(library.topics.values()),
            existing_titles=[topic.title for topic in library.topics.values()],
            limit=MAX_PROPOSALS_PER_CYCLE,
        )
        proposals_payload = [proposal.to_dict() for proposal in proposals]
        for proposal in proposals:
            if not proposal.accepted:
                continue
            new_topic = to_topic(proposal)
            if new_topic.topic_id in library.topics:
                continue
            promoted_topics.append(new_topic)
            library.add_topics([new_topic])
            library.add_discoveries(
                [
                    Discovery(
                        discovery_id=stable_id("disc", "invention", new_topic.topic_id),
                        topic_id=new_topic.topic_id,
                        text=(
                            f"Proposed a new question, '{new_topic.title}', from {proposal.support_documents} "
                            f"retrieved documents at novelty {proposal.novelty:.2f}."
                        ),
                        kind="new_question",
                        derived_from=proposal.support_claim_ids[:5],
                        confidence="low",
                    )
                ]
            )
        result.notes.append(
            f"{len(proposals)} candidate topic(s) scored from the retrieved documents; "
            f"{len(promoted_topics)} promoted to the topic list."
        )

    scan_payload: dict[str, Any] = {}
    if allow_network:
        from .fetch.changes import DEFAULT_WINDOW_DAYS, ChangeScanner, summarise_scan

        scanner = ChangeScanner(client, state_path(root, "change_scan.json"), allow_network=allow_network)
        scan_query = next((topic.keywords[0] for topic in plan.selected if topic.keywords), "research")
        scan_outcome = scanner.scan(
            scan_query,
            run_id=run_id,
            window_days=DEFAULT_WINDOW_DAYS,
            limit=5,
        )
        irregularities.extend(scan_outcome.irregularities)
        library.add_failures(scan_outcome.failures)
        scan_payload = scan_outcome.to_dict()
        save_json(root / "reports" / "change_scan.json", scan_payload)
        if scan_outcome.items_new:
            from .models import Question as _Question

            new_questions = [
                _Question(
                    id=stable_id("q", "scan", row["identifier"]),
                    topic_id="",
                    text=(
                        f"{scan.source_name} published or updated \"{row['title']}\" inside the window "
                        f"{scan.window.get('since')}..{scan.window.get('until')} ({row['url'] or scan.request_url}). "
                        "What does it change about what this library holds?"
                    ),
                    origin="discovery",
                    priority=0.6,
                )
                for scan in scan_outcome.scans
                for row in scan.new_items[:3]
            ]
            library.add_questions(new_questions)
            result.notes.append(
                f"Change scan: {scan_outcome.items_new} item(s) seen for the first time across "
                f"{sum(1 for s in scan_outcome.scans if s.status == 'scanned')} source(s); "
                f"{len(new_questions)} question(s) derived."
            )
        else:
            result.notes.append(
                "Change scan: no previously unseen items in the windows polled "
                f"({summarise_scan(scan_outcome)})."
            )
    else:
        result.notes.append(
            "Change scan not attempted: this run was offline. The scan needs egress to the source it polls."
        )

    # -- 5. audit ------------------------------------------------------------
    published_claims = list(library.claims.values())
    findings: list[Irregularity] = list(irregularities)
    findings.extend(recheck_claims(published_claims, root / "evidence" / "snapshots"))
    findings.extend(check_links(published_claims))
    findings.extend(check_fixtures(library.evidence.values(), published_claims))
    findings.extend(check_coverage(library.active_topics(), published_claims, all_statuses))
    for strategy in library.strategies.values():
        ok, unbacked = strategy_numbers_ok(strategy, library.claims)
        if not ok:
            findings.append(
                Irregularity(
                    irregularity_id=stable_id("irr", "strategy-numbers", strategy.strategy_id),
                    severity="error",
                    stage="audit",
                    topic_id=strategy.topic_id,
                    summary=f"Candidate {strategy.strategy_id} contains figures not present in its cited claims",
                    detail="Unbacked figures: " + ", ".join(unbacked),
                    suggested_action="A bug in the competition stage: the candidate is published with a warning badge.",
                )
            )

    # -- 5b. withdraw records built on retired claims -----------------------
    # Every superseded claim counts, not only the ones retired this cycle: the
    # first fix retired 24 statements, and 57 briefs quoting them stayed published
    # until the next run. The pass below is idempotent - a record already carrying
    # a reason is skipped - so it can be re-run on any library.
    withdrawn = retire_dependents(
        library, [claim for claim in library.claims.values() if claim.superseded]
    )
    if any(withdrawn.values()):
        library.add_strategies(withdrawn["strategies"])
        library.add_attacks(withdrawn["attacks"])
        library.add_questions(withdrawn["questions"])
        irregularities.append(
            Irregularity(
                irregularity_id=stable_id("irr", "retired-dependents", run_id),
                severity="info",
                stage="synthesis",
                topic_id="",
                summary=(
                    f"{len(withdrawn['strategies'])} brief(s), {len(withdrawn['attacks'])} criticism(s) and "
                    f"{len(withdrawn['questions'])} open question(s) withdrawn with their retired claims"
                ),
                detail=(
                    "These records quote a claim that a later cycle no longer produces. They stay in the library with "
                    "the reason recorded on each, and are excluded from the competing answers, criticisms and open "
                    "questions on the published pages."
                ),
                suggested_action="Review the retired statements section on the affected topic pages.",
            )
        )

    # -- 6. run summary (checked by the same numeric guard as the claims) ----
    claims_by_kind = {"direct": 0, "derived": 0, "synthesis": 0}
    for claim in library.claims.values():
        if claim.superseded:
            # A retired statement is still in the library, but it is not a current
            # finding, so it is not counted as one. Reporting it as composed would
            # make the summary disagree with the published page.
            continue
        claims_by_kind[claim.claim_kind] = claims_by_kind.get(claim.claim_kind, 0) + 1
    substance = substance_summary(library.claims.values())
    counts = {
        "topics": len(library.topics),
        "claims": len(library.claims),
        "documents": len(library.evidence),
        "strategies": len(library.strategies),
        "attacks": len(library.attacks),
        "questions": len(library.questions),
        "experiments": len(library.experiments),
        "http_requests": client.request_count,
        "synthesis_claims": claims_by_kind["synthesis"],
        "substantive_claims": substance["labels"]["substantive"],
        "metadata_claims": substance["labels"]["metadata"],
    }
    severity_counts = summarise(findings)["by_severity"]
    # Every figure that appears in the generated summary is collected here first,
    # and this dictionary is what the narrative guard is allowed to accept. The
    # summary cannot introduce a number that is not in the measured set.
    figures = {
        "claims": counts["claims"],
        "topics": counts["topics"],
        "documents_retrieved": sum(status.items for status in all_statuses),
        "documents_total": counts["documents"],
        "sources_polled": len({status.source_id for status in all_statuses}),
        "sources_reached": len({status.source_id for status in all_statuses if status.live_status == "reachable"}),
        "open_questions": counts["questions"],
        "errors": severity_counts.get("error", 0),
        "warnings": severity_counts.get("warning", 0),
        "synthesis_claims": counts["synthesis_claims"],
        "synthesis_retired": len(synthesis_retired),
        "records_withdrawn": (
            len(withdrawn["strategies"]) + len(withdrawn["attacks"]) + len(withdrawn["questions"])
        ),
        "substantive_claims": counts["substantive_claims"],
        "metadata_claims": counts["metadata_claims"],
        "topics_proposed": len(proposals_payload),
        "topics_promoted": len(promoted_topics),
        "change_scan_sources": len(scan_payload.get("scans", [])),
        "change_scan_new_items": int(scan_payload.get("items_new", 0)),
    }
    run_summary = {
        "run_id": run_id,
        "mode": mode,
        "generated_at": utcnow_iso(),
        "figures": figures,
        "what_changed": [
            f"Library now holds {figures['claims']} claim(s) across {figures['topics']} question(s).",
            f"This cycle retrieved {figures['documents_retrieved']} document(s) from "
            f"{figures['sources_reached']} of {figures['sources_polled']} polled source(s).",
            f"{figures['open_questions']} open question(s) have been derived from the retrieved evidence.",
            f"{figures['synthesis_claims']} cross-document statement(s) are current, "
            f"{figures['synthesis_retired']} were retired this cycle because the composition rules no longer "
            f"produce them ({figures['records_withdrawn']} briefs, criticisms and questions withdrew with them), and "
            f"{figures['substantive_claims']} claim(s) scored as substantive while {figures['metadata_claims']} "
            "are labelled as registry metadata.",
            f"{figures['topics_proposed']} candidate topic(s) were scored from the retrieved documents and "
            f"{figures['topics_promoted']} promoted; the change scan polled {figures['change_scan_sources']} "
            f"source(s) and found {figures['change_scan_new_items']} item(s) not seen before.",
            f"{figures['errors']} error(s) and {figures['warnings']} warning(s) are waiting for review.",
        ],
        "claim_kinds": claims_by_kind,
        "substance": substance,
        "topic_proposals": proposals_payload,
        "change_scan": scan_payload,
        "evidence_rank_mix": evidence_rank_mix(library.claims.values()),
        "registry": registry_summary(),
        "thresholds": thresholds_in_force(state_path(root, "calibration.json")),
    }
    findings.extend(
        audit_run_summary(
            " ".join(run_summary["what_changed"]),
            published_claims,
            extra_allowed=list(figures.values()),
        )
    )
    run_summary["irregularities"] = summarise(findings)
    library.add_irregularities(findings)
    result.irregularities = findings

    save_json(root / "reports" / "run_summary.json", run_summary)
    write_text(root / "reports" / "irregularities.md", render_markdown(findings, generated_at=run_summary["generated_at"]))

    # -- 7. publish ----------------------------------------------------------
    data = build_site_data(
        library,
        source_matrix=source_matrix(),
        source_status=all_statuses,
        irregularities=findings,
        failures=list(library.failures.values()),
        elo_payload=elo.to_dict(),
        calibration=calibration_payload or thresholds_in_force(state_path(root, "calibration.json")),
        requirements=load_json(root / "data" / "requirements.json", default=[]) or [],
        methodology={
            "engine_version": __version__,
            "evidence_hierarchy": [
                {"rank": rank, "name": name, "description": description}
                for rank, name, description in EVIDENCE_HIERARCHY
            ],
            "thresholds": thresholds_in_force(state_path(root, "calibration.json")),
            "requirements_version": REQUIREMENTS_VERSION,
        },
        mode=mode,
        run_summary=run_summary,
    )
    data["experiment_catalogue"] = experiment_catalogue()

    published: list[Path] = []
    if publish:
        published = build_site(
            data,
            SITE_DIR if root == Path(__file__).resolve().parent.parent else root / "docs",
            write_root_entry=True,
        )
        result.published = [str(path) for path in published]
    save_json(root / "reports" / "site_data.json", data)

    result.counts = counts
    result.source_summary = summarise_status(all_statuses)
    save_json(state_path(root, "last_cycle.json"), result.to_dict())
    return result


def run_forever(*, root: Path, interval_seconds: int = 900, **kwargs: Any) -> None:
    """Run cycles back to back with a fixed pause.

    Left unbounded on purpose: continuous operation is a deployment decision. The
    bundled GitHub Actions workflow is the supported way to run this, because it
    gives the loop a scheduler, a timeout and an audit trail.
    """
    import time

    while True:
        try:
            result = run_cycle(root=root, **kwargs)
            LOG.info("cycle complete: %s", json.dumps(to_jsonable(result.counts)))
        except NetworkUnavailable as exc:
            LOG.warning("cycle skipped, network unavailable: %s", exc)
        except Exception as exc:  # pragma: no cover - keep the loop alive
            LOG.exception("cycle failed: %s", exc)
        time.sleep(interval_seconds)
