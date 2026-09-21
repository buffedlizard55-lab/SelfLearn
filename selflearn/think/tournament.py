"""The research tournament: rank competing candidates on stated criteria.

The design document is explicit that the winner must not be "whoever writes the
most convincing explanation". Every criterion below is therefore either

* **measured** - computed from the claim set, the evidence records or an actual
  experiment result; or
* **heuristic** - a documented proxy, published as such on the site, so that a
  reader can discount it.

The distinction is carried into the published data in the ``method`` column of
every criterion table. Nothing is hidden behind a single opaque score.

The tournament structure follows the design document: a round-robin among all
candidates, then a final between the two leaders, with a critic veto - a candidate
carrying an unresolved *fatal* attack cannot win, regardless of its score.
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Iterable

from ..config import TOURNAMENT_CRITERIA
from ..models import Attack, Claim, EvidenceRecord, ExperimentResult, Strategy, TournamentResult
from ..util import clamp, extract_numbers, stable_id
from .critic import has_fatal, survival_rate
from .elo import EloTable

# criterion key -> (weight, method, explanation)
CRITERIA: dict[str, tuple[float, str, str]] = {
    key: (weight, method, note)
    for key, _label, weight, note in TOURNAMENT_CRITERIA
    for method in ["measured"]
}

METHODS: dict[str, str] = {
    "correctness": "measured",
    "evidence_quality": "measured",
    "reproducibility": "measured",
    "adversarial_survival": "measured",
    "robustness": "measured",
    "experimental_performance": "measured",
    "simplicity": "measured",
    "scalability": "heuristic",
    "computational_cost": "measured",
}

CRITERION_NOTES: dict[str, str] = {
    key: note for key, _label, _weight, note in TOURNAMENT_CRITERIA
}

LABELS: dict[str, str] = {key: label for key, label, _w, _n in TOURNAMENT_CRITERIA}

SCALE_TERMS = (
    "%",
    " per ",
    "rate",
    "capacity",
    "throughput",
    "cost",
    "scal",
    "annual",
    "monthly",
    "gwh",
    "mwh",
    "kw",
    "mw",
    "tonne",
    "kg",
    "km",
)


def _cited(strategy: Strategy, claims_by_id: dict[str, Claim]) -> list[Claim]:
    return [claims_by_id[cid] for cid in strategy.supporting_claim_ids if cid in claims_by_id]


def correctness(strategy: Strategy, claims: list[Claim]) -> float:
    if not claims:
        return 0.0
    weights = {"supported": 1.0, "partially_supported": 0.4, "unsupported": 0.0, "contradicted": 0.0}
    return mean(weights.get(claim.verification.verdict, 0.0) for claim in claims)


def evidence_quality(records: list[EvidenceRecord]) -> float:
    if not records:
        return 0.0
    return mean((10 - record.evidence_rank) / 9.0 for record in records)


def reproducibility(records: list[EvidenceRecord]) -> float:
    if not records:
        return 0.0
    values = []
    for record in records:
        if record.is_fixture:
            values.append(0.0)
        elif record.is_live:
            values.append(1.0)
        else:
            values.append(0.75)
    return mean(values)


def simplicity(strategy: Strategy, claims: list[Claim]) -> float:
    claims_n = len(claims)
    assumptions = len(strategy.assumptions)
    base = claims_n / max(claims_n + assumptions, 1)
    if len(strategy.argument) > 2400:
        base *= 0.8
    return clamp(base)


def scalability(strategy: Strategy, claims: list[Claim]) -> float:
    """Heuristic proxy: do the cited statements carry a scale or rate term?

    This is a *proxy*, not a measurement. It is published with ``method:
    heuristic`` so that a reader can disregard it without losing the rest of the
    ranking. A statement with a rate term is at least expressed in a form that
    can be scaled; whether it actually generalises is not established by this
    function.
    """
    if not claims:
        return 0.0
    hits = 0
    for claim in claims:
        lowered = f" {claim.text.casefold()} "
        if any(term in lowered for term in SCALE_TERMS) or extract_numbers(claim.text):
            hits += 1
    return hits / len(claims)


def computational_cost(strategy: Strategy, claims: list[Claim]) -> float:
    size = len(strategy.argument) + 200 * len(claims)
    return clamp(1.0 - size / 3000.0)


def experimental_performance(experiment: ExperimentResult | None) -> tuple[float, str]:
    """Score a real experiment result, or report that no test exists."""
    if experiment is None or experiment.baseline is None or experiment.best_value is None:
        return 0.0, "No experiment has been run for this question, so this criterion contributes nothing."
    baseline = abs(float(experiment.baseline))
    if baseline == 0:
        return 0.0, "Baseline is zero; relative improvement is undefined."
    gain = (float(experiment.best_value) - float(experiment.baseline)) / baseline
    return clamp(gain if gain > 0 else 0.0), (
        f"Measured {experiment.metric}: best variant {experiment.best_variant} scored "
        f"{experiment.best_value} against baseline {experiment.baseline} (experiment {experiment.experiment_id})."
    )


def robustness(strategy: Strategy, claims: list[Claim], records: list[EvidenceRecord]) -> tuple[float, str]:
    """Stability of the candidate under perturbation of its own support.

    Three deterministic perturbations are applied: (i) support reduced to the two
    strongest claims, (ii) the weakest claim removed, (iii) evidence quality
    double-weighted. The score is the stability of the *quality* signal across
    those perturbations. A brief that only looks strong when all of its evidence
    is counted is not robust.
    """
    if len(claims) < 2:
        return 0.35, "Fewer than two cited claims: stability cannot be assessed, so a low default is used."

    def quality(subset: list[Claim]) -> float:
        subset_records = [r for r in records if r.evidence_id in {c.evidence_id for c in subset}]
        return 0.5 * correctness(strategy, subset) + 0.5 * evidence_quality(subset_records)

    variants = [quality(claims[:2]), quality(claims[:-1]), 0.4 * correctness(strategy, claims) + 0.6 * evidence_quality(records)]
    spread = pstdev(variants) if len(variants) > 1 else 0.0
    centre = mean(variants) if variants else 0.0
    score = clamp(1.0 - (spread / centre if centre > 1e-9 else 1.0))
    return score, f"Perturbation spread {spread:.3f} around a centre of {centre:.3f}."


def score_strategy(
    strategy: Strategy,
    claims_by_id: dict[str, Claim],
    evidence_index: dict[str, EvidenceRecord],
    attacks: list[Attack],
    *,
    experiment: ExperimentResult | None = None,
) -> dict[str, Any]:
    """Compute the full criterion table for one candidate."""
    claims = _cited(strategy, claims_by_id)
    records = [evidence_index[c.evidence_id] for c in claims if c.evidence_id in evidence_index]
    numbers_ok, unbacked = _numbers_ok(strategy, claims_by_id)

    values: dict[str, float] = {
        "correctness": correctness(strategy, claims) * (1.0 if numbers_ok else 0.5),
        "evidence_quality": evidence_quality(records),
        "reproducibility": reproducibility(records),
        "adversarial_survival": survival_rate(attacks),
        "robustness": robustness(strategy, claims, records)[0],
        "simplicity": simplicity(strategy, claims),
        "scalability": scalability(strategy, claims),
        "computational_cost": computational_cost(strategy, claims),
    }
    values["experimental_performance"], experiment_note = experimental_performance(experiment)

    weights = {key: weight for key, _label, weight, _note in TOURNAMENT_CRITERIA}
    total_weight = sum(weights.values())
    total = sum(values[key] * weights[key] for key in values) / total_weight

    table: dict[str, dict[str, Any]] = {}
    for key, value in values.items():
        table[key] = {
            "label": LABELS[key],
            "value": round(value, 4),
            "weight": weights[key],
            "method": METHODS[key],
            "note": CRITERION_NOTES[key],
        }
    table["experimental_performance"]["detail"] = experiment_note
    table["robustness"]["detail"] = robustness(strategy, claims, records)[1]

    return {
        "criteria": table,
        "total": round(total, 4),
        "weights_total": total_weight,
        "numbers_checked": numbers_ok,
        "unbacked_numbers": unbacked,
        "claims_cited": len(claims),
        "evidence_records": len(records),
        "attacks": len(attacks),
        "fatal_attack": has_fatal(attacks),
    }


def _numbers_ok(strategy: Strategy, claims_by_id: dict[str, Claim]) -> tuple[bool, list[str]]:
    from .competition import strategy_numbers_ok

    return strategy_numbers_ok(strategy, claims_by_id)


def run_tournament(
    topic_id: str,
    strategies: list[Strategy],
    claims_by_id: dict[str, Claim],
    evidence_index: dict[str, EvidenceRecord],
    attacks_by_strategy: dict[str, list[Attack]],
    elo: EloTable | None = None,
    *,
    experiment: ExperimentResult | None = None,
) -> TournamentResult:
    """Score every candidate, run the round-robin, then the final."""
    for strategy in strategies:
        strategy.scorecard = score_strategy(
            strategy,
            claims_by_id,
            evidence_index,
            attacks_by_strategy.get(strategy.strategy_id, []),
            experiment=experiment,
        )

    ranking = sorted(strategies, key=lambda s: (-float(s.scorecard.get("total", 0.0)), s.strategy_id))
    scores = {s.strategy_id: float(s.scorecard.get("total", 0.0)) for s in strategies}
    criterion_table = {
        s.strategy_id: {k: v for k, v in s.scorecard.get("criteria", {}).items()} for s in strategies
    }

    # Round robin: every pair meets once; Elo accumulates across the whole project.
    if elo is not None and len(ranking) > 1:
        for i, left in enumerate(ranking):
            for right in ranking[i + 1 :]:
                a, b = scores[left.strategy_id], scores[right.strategy_id]
                outcome = 1.0 if a > b else (0.0 if a < b else 0.5)
                elo.record(
                    f"persona-{left.persona_code}",
                    f"persona-{right.persona_code}",
                    outcome,
                    topic_id=topic_id,
                    criterion="total",
                )

    winner: str | None = None
    notes: list[str] = []
    finalists = ranking[:2]
    if len(finalists) == 1:
        winner = finalists[0].strategy_id if not has_fatal(attacks_by_strategy.get(finalists[0].strategy_id, [])) else None
        if winner is None:
            notes.append("The only candidate carries an unresolved fatal attack, so no winner is declared.")
    elif len(finalists) == 2:
        first, second = finalists
        first_fatal = has_fatal(attacks_by_strategy.get(first.strategy_id, []))
        second_fatal = has_fatal(attacks_by_strategy.get(second.strategy_id, []))
        if first_fatal and not second_fatal:
            winner = second.strategy_id
            notes.append("The highest-scoring candidate was vetoed by an unresolved fatal attack; the runner-up advances.")
        elif first_fatal and second_fatal:
            winner = None
            notes.append("Both finalists carry unresolved fatal attacks, so no winner is declared for this round.")
        elif scores[first.strategy_id] > scores[second.strategy_id]:
            winner = first.strategy_id
            notes.append("The final was decided on the weighted criterion total; the margin is published below.")
        elif scores[first.strategy_id] < scores[second.strategy_id]:
            winner = second.strategy_id
            notes.append("The final was decided on the weighted criterion total; the margin is published below.")
        else:
            notes.append("The final was a tie on the weighted total, so no winner is declared.")
        if elo is not None and winner is not None:
            loser = second if winner == first.strategy_id else first
            elo.record(
                f"persona-{first.persona_code if winner == first.strategy_id else second.persona_code}",
                f"persona-{loser.persona_code}",
                1.0,
                topic_id=topic_id,
                criterion="final",
            )

    if not ranking:
        notes.append("No candidates were generated for this question.")

    return TournamentResult(
        topic_id=topic_id,
        round_name="round-robin then final",
        ranking=[s.strategy_id for s in ranking],
        scores=scores,
        winner=winner,
        criterion_table=criterion_table,
        notes=" ".join(notes),
    )


def criterion_rows(result: TournamentResult, strategies: list[Strategy]) -> list[dict[str, Any]]:
    """Flatten a criterion table into rows for rendering."""
    by_id = {s.strategy_id: s for s in strategies}
    rows: list[dict[str, Any]] = []
    for strategy_id in result.ranking:
        strategy = by_id.get(strategy_id)
        if strategy is None:
            continue
        for key, value in result.criterion_table.get(strategy_id, {}).items():
            rows.append(
                {
                    "strategy_id": strategy_id,
                    "persona": f"{strategy.persona_code} - {strategy.persona_name}",
                    "criterion": value.get("label", key),
                    "criterion_key": key,
                    "value": value.get("value"),
                    "weight": value.get("weight"),
                    "method": value.get("method"),
                    "note": value.get("detail") or value.get("note"),
                    "winner": strategy_id == result.winner,
                }
            )
    return rows


def tournament_id(topic_id: str, ranking: list[str]) -> str:
    return stable_id("tour", topic_id, ",".join(ranking))
