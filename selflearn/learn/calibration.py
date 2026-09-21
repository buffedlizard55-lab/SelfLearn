"""Calibrate the verification thresholds against a labelled case set.

The verification thresholds in :mod:`selflearn.config` are assumptions. This
module turns them into a measured choice: it runs the verifier over a labelled
set of hand-adjudicated cases (``data/fixtures/verification_cases.jsonl``), sweeps
the threshold grid, and reports precision, recall and F1 for the decision that
matters - *accepting a claim as supported*.

The objective is deliberately asymmetric. A false support (publishing a claim the
document does not back) is the failure mode this whole project exists to prevent,
so the selection rule is:

1. maximise recall for ``supported`` subject to **zero** false supports on the
   labelled set, then
2. maximise F1 for the three-way verdict, then
3. prefer the higher (stricter) threshold on a tie.

The result is written to ``state/calibration.json`` and published with the full
grid, so a reviewer can see the trade-off and disagree with the objective.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..config import CALIBRATION_STATE, THRESHOLDS, VerificationThresholds
from ..util import save_json, utcnow_iso
from ..verify.verifier import verify_claim

LOG = logging.getLogger("selflearn.calibration")

GRID_SUPPORTED = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
GRID_PARTIAL = (0.25, 0.35, 0.45, 0.55, 0.65)
GRID_QUOTE_CHARS = (12, 24, 40)
VERDICTS = ("supported", "partially_supported", "unsupported")


@dataclass
class CalibrationCase:
    case_id: str
    name: str
    claim: str
    quote: str
    document: str
    expected: str
    rationale: str = ""
    excluded_from_selection: bool = False
    exclusion_reason: str = ""


def load_cases(path: Path) -> list[CalibrationCase]:
    cases: list[CalibrationCase] = []
    if not Path(path).exists():
        return cases
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            expected = row.get("expected", "")
            if expected not in VERDICTS:
                continue
            cases.append(
                CalibrationCase(
                    case_id=row.get("case_id", f"case-{len(cases)}"),
                    name=row.get("name", ""),
                    claim=row.get("claim", ""),
                    quote=row.get("quote", ""),
                    document=row.get("document", ""),
                    expected=expected,
                    rationale=row.get("rationale", ""),
                    excluded_from_selection=bool(row.get("excluded_from_selection", False)),
                    exclusion_reason=row.get("exclusion_reason", ""),
                )
            )
    return cases


def evaluate(cases: Iterable[CalibrationCase], thresholds: VerificationThresholds) -> dict[str, Any]:
    """Confusion matrices and derived metrics for one threshold setting."""
    matrix: dict[str, dict[str, int]] = {expected: dict.fromkeys(VERDICTS, 0) for expected in VERDICTS}
    disagreements: list[dict[str, str]] = []
    for case in cases:
        predicted = verify_claim(case.claim, case.quote, case.document, thresholds=thresholds).verdict
        matrix.setdefault(case.expected, dict.fromkeys(VERDICTS, 0))[predicted] += 1
        if predicted != case.expected:
            disagreements.append(
                {
                    "case_id": case.case_id,
                    "name": case.name,
                    "expected": case.expected,
                    "predicted": predicted,
                }
            )

    def prf(label: str) -> tuple[float, float, float]:
        true_positive = matrix.get(label, {}).get(label, 0)
        false_positive = sum(matrix.get(other, {}).get(label, 0) for other in VERDICTS if other != label)
        false_negative = sum(
            count for predicted, count in matrix.get(label, {}).items() if predicted != label
        )
        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 0.0
        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        return round(precision, 4), round(recall, 4), round(f1, 4)

    metrics = {label: dict(zip(("precision", "recall", "f1"), prf(label))) for label in VERDICTS}
    total = sum(sum(row.values()) for row in matrix.values())
    correct = sum(matrix[label][label] for label in VERDICTS)
    false_supports = sum(
        matrix.get(other, {}).get("supported", 0) for other in VERDICTS if other != "supported"
    )
    return {
        "thresholds": thresholds.as_dict(),
        "matrix": matrix,
        "metrics": metrics,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "cases": total,
        "false_supports": false_supports,
        "macro_f1": round(sum(m["f1"] for m in metrics.values()) / len(VERDICTS), 4),
        "disagreements": disagreements[:20],
    }


def sweep(cases: list[CalibrationCase]) -> dict[str, Any]:
    """Evaluate the threshold grid and select the recommended point.

    Cases carrying ``excluded_from_selection`` are cases where the engine has a
    *documented* limitation. They are still evaluated and still reported, but they
    are removed from the selection objective so that a known limitation cannot be
    hidden by tuning the thresholds around it. The excluded cases and the reason
    for each exclusion are published alongside the result.
    """
    selected_cases = [case for case in cases if not case.excluded_from_selection]
    excluded_cases = [case for case in cases if case.excluded_from_selection]
    grid: list[dict[str, Any]] = []
    for supported in GRID_SUPPORTED:
        for partial in GRID_PARTIAL:
            if partial >= supported:
                continue
            for quote_chars in GRID_QUOTE_CHARS:
                thresholds = VerificationThresholds(
                    supported=supported,
                    partially_supported=partial,
                    quote_min_chars=quote_chars,
                )
                result = evaluate(selected_cases, thresholds)
                result["all_cases"] = evaluate(cases, thresholds)
                grid.append(result)

    if not grid:
        return {"grid": [], "selected": None, "reason": "no labelled cases available"}

    def objective(result: dict[str, Any]) -> tuple:
        """Lexicographic selection rule, most important criterion first.

        1. fewest false supports (a published claim the document does not back),
        2. highest recall for ``supported``,
        3. highest F1 for ``supported``,
        4. highest macro F1 across the three verdicts,
        5. closest to the documented default, so that the engine does not drift
           its own thresholds when several settings are equivalent on the
           labelled set,
        6. the stricter support threshold on a remaining tie.
        """
        supported_recall = result["metrics"]["supported"]["recall"]
        f1 = result["metrics"]["supported"]["f1"]
        thresholds = result["thresholds"]
        distance = (
            abs(float(thresholds["supported"]) - THRESHOLDS.supported)
            + abs(float(thresholds["partially_supported"]) - THRESHOLDS.partially_supported)
            + abs(float(thresholds["quote_min_chars"]) - float(THRESHOLDS.quote_min_chars)) / 100.0
        )
        return (
            -result["false_supports"],
            supported_recall,
            f1,
            result["macro_f1"],
            -round(distance, 6),
            float(thresholds["supported"]),
        )

    best = max(grid, key=objective)
    baseline = evaluate(selected_cases, THRESHOLDS)
    baseline["all_cases"] = evaluate(cases, THRESHOLDS)
    return {
        "grid": grid,
        "selected": best,
        "baseline": baseline,
        "excluded_cases": [
            {"case_id": case.case_id, "name": case.name, "reason": case.exclusion_reason} for case in excluded_cases
        ],
        "objective": (
            "lexicographic: fewest false supports, then highest recall for 'supported', then highest F1 for "
            "'supported', then highest macro F1, then the setting closest to the documented default, then the "
            "stricter support threshold"
        ),
        "cases": [case.__dict__ for case in cases],
    }


def run_calibration(
    cases_path: Path,
    *,
    apply: bool = True,
    state_path: Path | None = None,
) -> dict[str, Any]:
    """Run the sweep, optionally adopt the recommended thresholds, and record both."""
    cases = load_cases(cases_path)
    result = sweep(cases)
    selected = result.get("selected")
    state_path = Path(state_path or CALIBRATION_STATE)
    previous = _read_state(state_path)

    payload: dict[str, Any] = {
        "ran_at": utcnow_iso(),
        "cases_path": str(cases_path),
        "case_count": len(cases),
        "selected": selected,
        "baseline": result.get("baseline"),
        "objective": result.get("objective"),
        "applied": False,
        "applied_thresholds": THRESHOLDS.as_dict(),
        "changed": None,
        "notes": [],
    }

    if not apply and previous.get("applied"):
        # Inspecting the sweep (the `calibrate` command) must not erase the record of
        # what is actually in force; only an applying run may change it.
        payload["applied"] = True
        payload["applied_thresholds"] = previous.get("applied_thresholds", THRESHOLDS.as_dict())
        payload["changed"] = previous.get("changed")
        payload["notes"].append(
            "This sweep did not change the thresholds in force; the previously applied set is carried over and "
            "shown above."
        )

    if selected is not None:
        chosen = VerificationThresholds(
            supported=float(selected["thresholds"]["supported"]),
            partially_supported=float(selected["thresholds"]["partially_supported"]),
            quote_min_chars=int(selected["thresholds"]["quote_min_chars"]),
        )
        payload["notes"].append(
            f"Selection used {len(cases)} labelled case(s); false supports at the selected point: "
            f"{selected['false_supports']}."
        )
        if apply:
            payload["applied"] = True
            payload["applied_thresholds"] = chosen.as_dict()
            delta = abs(chosen.supported - THRESHOLDS.supported)
            payload["changed"] = delta > 1e-9
            if payload["changed"]:
                payload["notes"].append(
                    "Selected thresholds differ from the values in selflearn/config.py by "
                    f"{delta:.2f} on the support threshold. The engine publishes the threshold in force on every "
                    "claim page and records this change here rather than applying it silently."
                )
            _APPLIED["thresholds"] = chosen

    # Keep the grid small in the state file: it is a publication artefact.
    payload["grid"] = [
        {
            "supported": row["thresholds"]["supported"],
            "partially_supported": row["thresholds"]["partially_supported"],
            "quote_min_chars": row["thresholds"]["quote_min_chars"],
            "accuracy": row["accuracy"],
            "macro_f1": row["macro_f1"],
            "false_supports": row["false_supports"],
            "supported_recall": row["metrics"]["supported"]["recall"],
            "supported_precision": row["metrics"]["supported"]["precision"],
        }
        for row in result.get("grid", [])
    ]
    payload["disagreements"] = (selected or {}).get("disagreements", [])
    save_json(state_path, payload)
    return payload


def active_thresholds(state_path: Path | None = None) -> VerificationThresholds:
    """The thresholds the engine should use right now.

    Within a process the applied set is held in memory. A fresh process reads the
    published calibration state, so a cycle started later uses the same thresholds
    the last calibration adopted rather than silently reverting to the defaults.
    """
    if "thresholds" in _APPLIED:
        return _APPLIED["thresholds"]
    record = _read_state(Path(state_path or CALIBRATION_STATE))
    if record and record.get("applied"):
        values = record.get("applied_thresholds") or {}
        try:
            return VerificationThresholds(
                supported=float(values.get("supported", THRESHOLDS.supported)),
                partially_supported=float(values.get("partially_supported", THRESHOLDS.partially_supported)),
                quote_min_chars=int(values.get("quote_min_chars", THRESHOLDS.quote_min_chars)),
            )
        except (TypeError, ValueError):  # pragma: no cover - corrupt state file
            LOG.warning("calibration state could not be parsed; using config defaults")
    return THRESHOLDS


def _read_state(path: Path) -> dict[str, Any]:
    """Read a calibration state file, returning an empty dict when it is unusable."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


_APPLIED: dict[str, VerificationThresholds] = {}


def thresholds_in_force(state_path: Path | None = None) -> dict[str, Any]:
    """Read the published calibration state, if a calibration has been run."""
    path = Path(state_path or CALIBRATION_STATE)
    if not path.exists():
        return {
            "in_force": THRESHOLDS.as_dict(),
            "source": "config default (no calibration has been recorded yet)",
            "ran_at": None,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"in_force": THRESHOLDS.as_dict(), "source": "config default (state file unreadable)", "ran_at": None}
    return {
        "in_force": payload.get("applied_thresholds", THRESHOLDS.as_dict()),
        "source": "state/calibration.json",
        "ran_at": payload.get("ran_at"),
        "cases": payload.get("case_count"),
        "objective": payload.get("objective"),
        "changed": payload.get("changed"),
        "false_supports": (payload.get("selected") or {}).get("false_supports"),
    }
