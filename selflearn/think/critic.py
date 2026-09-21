"""The adversarial critic.

The critic's job is stated in the design document as "destroy bad ideas". It is
implemented as a set of named, deterministic rules rather than as free text
generation, for one reason: a rule can be checked. Each attack records the rule
that fired, the claims it looked at, and a severity. A reviewer can therefore
disagree with a rule and see exactly which candidates it affected.

Attack statements talk about *the analysis* ("all cited claims come from one
source"), never about the world. They are therefore verified against the library,
which is where the facts live, rather than against a source document. Statements
are kept free of figures so that the numeric guard applied to published text
cannot be circumvented through the critique section.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models import Attack, Claim, Contradiction, EvidenceRecord, Strategy
from ..util import content_tokens, jaccard, stable_id
from .personas import declares_mechanism

SEVERITY_ORDER = {"minor": 0, "moderate": 1, "major": 2, "fatal": 3}


@dataclass
class CriticRule:
    rule_id: str
    attack_type: str
    description: str


RULES: tuple[CriticRule, ...] = (
    CriticRule("C1", "citation", "A cited claim did not pass full verification."),
    CriticRule("C2", "citation", "A cited claim is only partially supported by its document."),
    CriticRule("C3", "assumption", "The brief states an assumption it has not evidenced."),
    CriticRule("C4", "counterexample", "Another claim in the library pulls in the opposite direction."),
    CriticRule("C5", "repro", "A cited claim rests on a stored snapshot rather than a live retrieval."),
    CriticRule("C6", "repro", "A cited claim rests on synthetic fixture evidence."),
    CriticRule("C7", "data", "All cited claims come from a single source."),
    CriticRule("C8", "data", "The cited evidence is older than the staleness horizon."),
    CriticRule("C9", "assumption", "The brief infers a mechanism from observational statements."),
    CriticRule("C10", "simplicity", "The brief carries more assumptions than cited claims."),
    CriticRule("C11", "simplicity", "The argument is long relative to the amount of evidence it cites."),
)
RULE_INDEX = {rule.rule_id: rule for rule in RULES}

STALENESS_DAYS = 1095.0  # three years


def _attack(
    strategy: Strategy,
    rule: CriticRule,
    statement: str,
    severity: str,
    claim_refs: Iterable[str] = (),
    outcome: str = "open",
) -> Attack:
    return Attack(
        attack_id=stable_id("atk", strategy.strategy_id, rule.rule_id, statement[:80]),
        strategy_id=strategy.strategy_id,
        topic_id=strategy.topic_id,
        critic=f"{rule.rule_id}: {rule.description}",
        attack_type=rule.attack_type,
        statement=statement,
        severity=severity,
        claim_refs=list(claim_refs),
        outcome=outcome,
    )


def critique_strategy(
    strategy: Strategy,
    claims_by_id: dict[str, Claim],
    *,
    library_claims: Iterable[Claim] = (),
    evidence_index: dict[str, EvidenceRecord] | None = None,
    contradictions: Iterable[Contradiction] = (),
    now_iso: str | None = None,
) -> list[Attack]:
    """Apply every critic rule to one candidate and return the attacks that fire."""
    evidence_index = evidence_index or {}
    library_claims = list(library_claims)
    contradictions = list(contradictions)
    attacks: list[Attack] = []

    cited = [claims_by_id[cid] for cid in strategy.supporting_claim_ids if cid in claims_by_id]

    if not cited:
        attacks.append(
            _attack(
                strategy,
                RULE_INDEX["C1"],
                "This brief cites no verified claim, so nothing in it can be checked against a source.",
                "fatal" if strategy.status != "blocked" else "major",
                outcome="open" if strategy.status != "blocked" else "survived",
            )
        )
        return attacks

    # -- C1 / C2: citation quality --------------------------------------
    for claim in cited:
        if claim.verification.verdict == "unsupported":
            attacks.append(
                _attack(
                    strategy,
                    RULE_INDEX["C1"],
                    f"The brief relies on {claim.claim_id}, which did not pass verification against its document.",
                    "fatal",
                    [claim.claim_id],
                )
            )
        elif claim.verification.verdict == "partially_supported":
            attacks.append(
                _attack(
                    strategy,
                    RULE_INDEX["C2"],
                    f"The brief relies on {claim.claim_id}, which is only partially supported "
                    f"(token coverage {claim.verification.coverage:.0%}). The wording of the brief may overstate it.",
                    "moderate",
                    [claim.claim_id],
                )
            )

    # -- C3: declared assumptions ---------------------------------------
    for assumption in strategy.assumptions:
        attacks.append(
            _attack(
                strategy,
                RULE_INDEX["C3"],
                "Declared assumption, unevidenced by the retrieved sources: " + assumption,
                "minor",
                outcome="survived",
            )
        )

    # -- C4: counterevidence in the library -----------------------------
    cited_ids = {claim.claim_id for claim in cited}
    for claim in cited:
        for other in library_claims:
            if other.claim_id in cited_ids or other.claim_id == claim.claim_id:
                continue
            if other.verification.verdict != "supported":
                continue
            similarity = jaccard(content_tokens(claim.text), content_tokens(other.text))
            if similarity < 0.55:
                continue
            contradicts = any(
                contradiction.claim_a in {claim.claim_id, other.claim_id}
                and contradiction.claim_b in {claim.claim_id, other.claim_id}
                for contradiction in contradictions
            )
            if contradicts:
                attacks.append(
                    _attack(
                        strategy,
                        RULE_INDEX["C4"],
                        f"The library holds {other.claim_id} from {other.source_name}, which points the other way "
                        f"from {claim.claim_id} on the same subject. The brief does not address it.",
                        "major",
                        [claim.claim_id, other.claim_id],
                    )
                )

    # -- C5 / C6: reproducibility of the underlying evidence -------------
    for claim in cited:
        record = evidence_index.get(claim.evidence_id)
        if record is None:
            continue
        if record.is_fixture:
            attacks.append(
                _attack(
                    strategy,
                    RULE_INDEX["C6"],
                    f"{claim.claim_id} rests on synthetic fixture evidence, which is a test artefact and not a "
                    "real-world observation.",
                    "fatal",
                    [claim.claim_id],
                )
            )
        elif not record.is_live:
            attacks.append(
                _attack(
                    strategy,
                    RULE_INDEX["C5"],
                    f"{claim.claim_id} was verified against a stored snapshot rather than a live retrieval in this "
                    "cycle, so a reader must confirm the source still says this.",
                    "moderate",
                    [claim.claim_id],
                )
            )

    # -- C7: single source ----------------------------------------------
    sources = {claim.source_name for claim in cited}
    if len(sources) == 1:
        attacks.append(
            _attack(
                strategy,
                RULE_INDEX["C7"],
                f"Every claim this brief cites comes from one source ({sorted(sources)[0]}). "
                "Independence has not been demonstrated.",
                "major",
                [claim.claim_id for claim in cited],
            )
        )

    # -- C8: staleness ---------------------------------------------------
    if now_iso:
        from ..util import days_between

        dated = [evidence_index[c.evidence_id] for c in cited if c.evidence_id in evidence_index]
        ages = [days_between(record.published_at, now_iso) for record in dated if record.published_at]
        ages = [age for age in ages if age is not None and age >= 0]
        if ages and min(ages) > STALENESS_DAYS:
            attacks.append(
                _attack(
                    strategy,
                    RULE_INDEX["C8"],
                    "The freshest document cited by this brief is more than three years old at the time of the run, "
                    "which is a risk for a question about current conditions.",
                    "moderate",
                    [claim.claim_id for claim in cited],
                )
            )

    # -- C9: mechanism inferred from observational evidence --------------
    causal = [claim.claim_id for claim in cited if declares_mechanism(claim.text)]
    if causal:
        classes = {claim.evidence_class for claim in cited}
        experimental = bool(classes & {"direct_experiment", "reproduced_experiment"})
        if not experimental:
            attacks.append(
                _attack(
                    strategy,
                    RULE_INDEX["C9"],
                    "The quoted statements use causal language while every cited document is observational. "
                    "Association in the sources does not establish the mechanism the brief implies.",
                    "major",
                    causal,
                )
            )

    # -- C10 / C11: simplicity -------------------------------------------
    if len(strategy.assumptions) > len(cited):
        attacks.append(
            _attack(
                strategy,
                RULE_INDEX["C10"],
                "This brief carries more declared assumptions than cited claims; its support is thinner than its length "
                "suggests.",
                "moderate",
                [claim.claim_id for claim in cited],
            )
        )
    if len(strategy.argument) > 1200 and len(cited) <= 2:
        attacks.append(
            _attack(
                strategy,
                RULE_INDEX["C11"],
                "The argument is long relative to the two or fewer claims it cites. Prefer the shorter statement.",
                "minor",
                [claim.claim_id for claim in cited],
            )
        )

    return attacks


def summarise_attacks(attacks: Iterable[Attack]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for attack in attacks:
        row = summary.setdefault(attack.strategy_id, {})
        row[attack.severity] = row.get(attack.severity, 0) + 1
    return summary


def worst_severity(attacks: Iterable[Attack]) -> str:
    """The most severe attack that has not been resolved in the candidate's favour."""
    worst = "none"
    for attack in attacks:
        if attack.outcome == "survived":
            continue
        if SEVERITY_ORDER.get(attack.severity, -1) > SEVERITY_ORDER.get(worst, -1):
            worst = attack.severity
    return worst


def survival_rate(attacks: Iterable[Attack]) -> float:
    """Share of attacks a candidate survives, weighted by severity."""
    attacks = list(attacks)
    if not attacks:
        return 1.0
    weights = {"minor": 0.35, "moderate": 0.65, "major": 1.0, "fatal": 1.5}
    total = sum(weights.get(a.severity, 1.0) for a in attacks)
    survived = sum(weights.get(a.severity, 1.0) for a in attacks if a.outcome in {"survived", "conceded"})
    return round(max(0.0, 1.0 - (total - survived) / max(total, 1e-9)), 4)


def has_fatal(attacks: Iterable[Attack]) -> bool:
    return any(a.severity == "fatal" and a.outcome != "survived" for a in attacks)
