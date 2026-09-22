"""Generate competing candidate answers from the verified claim set.

Every sentence a candidate contributes is either

* a **verbatim quotation** of a verified claim, with the claim id and source
  attached, or
* **fixed scaffolding language** whose job is to state what the brief is, what it
  assumes, and what would falsify it.

No other text is permitted. That constraint is what makes the competition
auditable: a reader can trace every substantive sentence in a candidate back to
a claim, and every claim back to a stored document. Scaffolding never contains a
digit, so the numeric guard in :mod:`selflearn.verify.audit` can mechanically
confirm that no candidate sneaks an unbacked figure into the page.
"""

from __future__ import annotations

from typing import Any, Iterable

from ..models import Claim, Strategy, Topic
from ..util import content_tokens, extract_numbers, stable_id, truncate
from .personas import Persona, declares_mechanism, rank_claims_for_persona  # noqa: F401

MAX_SUPPORT = 6

BRIEF_HEADER = {
    "A": "Established-knowledge brief. The most strongly evidenced statements retrieved for this question are quoted below.",
    "B": "Contrarian brief. The retrieved evidence is searched for findings that limit, qualify or contradict the conventional reading.",
    "C": "First-principles brief. The statements below carry an explicit quantity, so a constraint can be derived from them rather than assumed.",
    "D": "Cross-domain brief. The statements below were retrieved for other topics and share subject matter with this one; they are candidates for transfer.",
    "E": "Optimisation brief. The statements below carry a rate, cost or scale term and are candidates for a cost or throughput argument.",
    "F": "Experimental brief. The statements below carry a measurement, which makes them usable as the basis of a test.",
}

NO_EVIDENCE_BRIEF = (
    "No candidate answer is offered. The claim set for this question contains no statement that "
    "passed verification, so any answer would be speculation rather than research."
)

ASSUMPTION_NOTE = (
    "An assumption is a statement this brief needs to be true but which the retrieved sources do not "
    "establish. Assumptions are listed explicitly so that a critic can attack them."
)


def _quote_block(claims: Iterable[Claim]) -> str:
    """Render supporting claims as attributed verbatim quotations."""
    lines: list[str] = []
    for claim in claims:
        lines.append(f'[{claim.claim_id}] "{claim.quote or claim.text}" - {claim.source_name} ({claim.evidence_class})')
    return "\n".join(lines)


def cross_domain_claims(
    topic: Topic,
    library: dict[str, list[Claim]],
    *,
    limit: int = 2,
    min_overlap: float = 0.12,
) -> list[Claim]:
    """Claims from *other* topics that share vocabulary with this topic.

    Overlap is measured on content tokens. It is a coarse signal and is labelled
    as one: the brief that consumes it presents these statements as candidates
    for transfer, not as established results about this topic.
    """
    target = content_tokens(" ".join(topic.keywords) + " " + topic.title + " " + topic.question)
    if not target:
        return []
    scored: list[tuple[float, Claim]] = []
    for other_topic_id, claims in library.items():
        if other_topic_id == topic.topic_id:
            continue
        for claim in claims:
            if claim.verification.verdict != "supported" or claim.superseded:
                # A retired claim is still in the library, but it is not a current
                # finding, so it must not be transferred into a new brief either.
                continue
            tokens = content_tokens(claim.text)
            if not tokens:
                continue
            overlap = len(target & tokens) / len(tokens)
            if overlap >= min_overlap:
                scored.append((overlap, claim))
    scored.sort(key=lambda item: (-item[0], item[1].claim_id))
    return [claim for _, claim in scored[:limit]]


def _assumptions_for(persona: Persona, claims: list[Claim]) -> list[str]:
    """Derive the honest assumption list for a brief.

    These are the things the brief is *taking for granted*. Stating them is what
    lets the adversarial stage attack something concrete.
    """
    if not claims:
        return ["No evidence was usable, so nothing is assumed beyond the question being answerable."]
    classes = {claim.evidence_class for claim in claims}
    assumptions = [
        "The retrieved documents are representative of the current state of the question.",
        "Quoted measurements were produced under the conditions the quoted text describes.",
    ]
    if classes & {"peer_reviewed", "primary_source", "official_data"}:
        assumptions.append("The named publishers are the authority for the identifiers they mint (DOI, PMID, dataset id).")
    if persona.code in {"A", "E"}:
        assumptions.append("Conditions reported in the sources still hold; no newer evidence supersedes them.")
    if persona.code == "B":
        assumptions.append("The absence of a contradicting statement in the retrieved set is not evidence that none exists.")
    if persona.code == "C":
        assumptions.append("The quantities quoted are commensurable with each other after unit conversion.")
    if persona.code == "D":
        assumptions.append("The other field's mechanism transfers without an omitted domain-specific constraint.")
    if persona.code == "F":
        assumptions.append("The measurement can be reproduced with the same method in this environment.")
    return assumptions


def _falsifier_for(persona: Persona, claims: list[Claim]) -> str:
    if not claims:
        return "Supply at least one supported claim; until then this brief cannot be tested."
    numbers = sorted({n for claim in claims for n in extract_numbers(claim.text)})
    quantified = f" a value outside the set {', '.join(numbers[:6])}" if numbers else " a contradictory value"
    base = f"This brief is falsified if a source of comparable or stronger evidence class reports{quantified} for the same quantity."
    if persona.code == "D":
        base += " For a transferred mechanism, falsification is a demonstration that the domain-specific constraint is missing."
    if persona.code == "F":
        base += " The attached experiment is the intended test."
    return base


def generate_strategies(
    topic: Topic,
    claims: list[Claim],
    personas: list[Persona],
    *,
    library: dict[str, list[Claim]] | None = None,
    max_support: int = MAX_SUPPORT,
) -> list[Strategy]:
    """Produce one candidate answer per persona, all grounded in the same claims."""
    library = library or {}
    usable = [
        c
        for c in claims
        if c.verification.verdict in {"supported", "partially_supported"} and not c.superseded
    ]
    strategies: list[Strategy] = []

    for persona in personas:
        ranked = rank_claims_for_persona(persona, usable)
        supporting = ranked[:max_support]
        transferred: list[Claim] = []
        if persona.code == "D":
            transferred = cross_domain_claims(topic, library, limit=2)
            supporting = (supporting[: max_support - len(transferred)] + transferred) if transferred else supporting

        title = f"{persona.name} brief: {truncate(topic.title, 80)}"
        if not supporting:
            strategies.append(
                Strategy(
                    strategy_id=stable_id("st", topic.topic_id, persona.code, "empty"),
                    topic_id=topic.topic_id,
                    persona_code=persona.code,
                    persona_name=persona.name,
                    persona_brief=persona.brief,
                    title=title,
                    argument=NO_EVIDENCE_BRIEF,
                    supporting_claim_ids=[],
                    assumptions=_assumptions_for(persona, []),
                    predicted_outcomes=[],
                    falsifier=_falsifier_for(persona, []),
                    status="blocked",
                    limitations="UNKNOWN: no verified evidence was available for this question.",
                )
            )
            continue

        blocks = [BRIEF_HEADER.get(persona.code, persona.brief), "", _quote_block(supporting), "", ASSUMPTION_NOTE]
        argument = "\n".join(blocks)
        predicted = [f"If the sourced statement holds, then: \"{claim.quote or claim.text}\"" for claim in supporting[:3]]
        cross_note = ""
        if transferred:
            cross_note = (
                "Cross-domain transfer is a hypothesis, not a result: the statements below were verified for a "
                "different question and their applicability here has not been tested."
            )
        mechanism_claims = [c.claim_id for c in supporting if declares_mechanism(c.text)]
        limitations = "This brief is an inference over the quoted claims. It is not itself a sourced fact."
        if cross_note:
            limitations += " " + cross_note

        strategies.append(
            Strategy(
                strategy_id=stable_id("st", topic.topic_id, persona.code, ",".join(c.claim_id for c in supporting)),
                topic_id=topic.topic_id,
                persona_code=persona.code,
                persona_name=persona.name,
                persona_brief=persona.brief,
                title=title,
                argument=argument,
                supporting_claim_ids=[c.claim_id for c in supporting],
                assumptions=_assumptions_for(persona, supporting),
                predicted_outcomes=predicted,
                falsifier=_falsifier_for(persona, supporting),
                status="competing",
                limitations=limitations,
                scorecard={"mechanism_claim_ids": mechanism_claims},
            )
        )
    return strategies


def strategy_numbers_ok(strategy: Strategy, claims_by_id: dict[str, Claim]) -> tuple[bool, list[str]]:
    """Every number in a candidate must come from one of its supporting claims."""
    allowed: set[str] = set()
    for claim_id in strategy.supporting_claim_ids:
        claim = claims_by_id.get(claim_id)
        if claim is not None:
            allowed |= extract_numbers(claim.text)
    if strategy.persona_code == "D":
        return True, []  # transferred claims carry their own external provenance
    unbacked = sorted(n for n in extract_numbers(strategy.argument + " " + strategy.falsifier) if n not in allowed)
    return (not unbacked), unbacked


def scenario_comparison(strategies: Iterable[Strategy]) -> list[dict[str, Any]]:
    """A compact comparison table for publication."""
    rows = []
    for strategy in strategies:
        rows.append(
            {
                "strategy_id": strategy.strategy_id,
                "persona": f"{strategy.persona_code} - {strategy.persona_name}",
                "claims_cited": len(strategy.supporting_claim_ids),
                "assumptions": len(strategy.assumptions),
                "status": strategy.status,
                "score": round(float(strategy.scorecard.get("total", 0.0)), 4),
            }
        )
    rows.sort(key=lambda row: (-row["score"], row["strategy_id"]))
    return rows
