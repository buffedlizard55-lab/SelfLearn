#!/usr/bin/env python3
"""Experiment: calibrate the claim-verification thresholds on labelled cases.

Hypothesis
    A threshold pair (support, partial) exists that reproduces every human label in
    ``data/fixtures/verification_cases.jsonl`` with zero false supports, where a
    false support means the verifier accepts a claim the cited document does not
    back.

Falsifier
    No point in the swept grid achieves zero false supports, or the best point
    disagrees with a labelled case that is not marked as a known engine limitation.

Metric
    Accuracy and macro F1 across the three verdicts, and the count of false
    supports.

Note
    The labelled cases are synthetic and were written by the project, not collected
    from an external study. That is stated in the published output, and it means the
    number below measures agreement with the project's own adjudication standard -
    not agreement with an independent annotator panel.

Run
    python experiments/verification_thresholds.py --out result.json
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from selflearn.learn.calibration import load_cases, sweep  # noqa: E402

CASES = REPO_ROOT / "data" / "fixtures" / "verification_cases.jsonl"


def run() -> dict:
    cases = load_cases(CASES)
    result = sweep(cases)
    selected = result.get("selected") or {}
    baseline = result.get("baseline") or {}
    thresholds = selected.get("thresholds", {})
    baseline_thresholds = baseline.get("thresholds", {})

    checks = [
        {
            "check": "a threshold pair achieves zero false supports on the labelled set",
            "outcome": bool(selected) and selected.get("false_supports", 1) == 0,
            "observed": f"false_supports={selected.get('false_supports')}",
        },
        {
            "check": "the selected point disagrees with no non-excluded labelled case",
            "outcome": not selected.get("disagreements"),
            "observed": f"disagreements={len(selected.get('disagreements', []))}",
        },
        {
            "check": "the selected point is at least as accurate as the configured default",
            "outcome": selected.get("accuracy", 0.0) >= baseline.get("accuracy", 0.0),
            "observed": f"selected={selected.get('accuracy')} default={baseline.get('accuracy')}",
        },
    ]
    supported = all(check["outcome"] for check in checks)

    return {
        "experiment_id": "verification-thresholds-v1",
        "hypothesis": (
            "A threshold pair exists that reproduces every human label in the labelled verification case set with zero "
            "false supports."
        ),
        "falsifier": (
            "No swept threshold pair achieves zero false supports, or the best pair disagrees with a non-excluded "
            "labelled case."
        ),
        "method": (
            f"Exhaustive sweep of {len(result.get('grid', []))} threshold combinations, evaluated against "
            f"{len(cases)} hand-labelled claim/document pairs; selection is lexicographic on false supports, recall, F1, "
            "macro F1, distance from the documented default, then strictness."
        ),
        "metric": "verdict accuracy on labelled cases",
        "baseline": baseline.get("accuracy", 0.0),
        "baseline_name": (
            f"configured default thresholds support={baseline_thresholds.get('supported')} "
            f"partial={baseline_thresholds.get('partially_supported')} "
            f"quote_chars={baseline_thresholds.get('quote_min_chars')}"
        ),
        "variants": [
            {
                "name": (
                    f"support_{row['thresholds']['supported']}"
                    f"_partial_{row['thresholds']['partially_supported']}"
                    f"_quote_{row['thresholds']['quote_min_chars']}"
                ),
                "value": row["accuracy"],
            }
            for row in sorted(result.get("grid", []), key=lambda row: -row["accuracy"])[:5]
        ],
        "best_variant": (
            f"support={thresholds.get('supported')} partial={thresholds.get('partially_supported')} "
            f"quote_chars={thresholds.get('quote_min_chars')}"
        ),
        "best_value": selected.get("accuracy", 0.0),
        "selected_thresholds": thresholds,
        "selected_metrics": selected.get("metrics", {}),
        "false_supports": selected.get("false_supports"),
        "macro_f1": selected.get("macro_f1"),
        "excluded_cases": result.get("excluded_cases", []),
        "checks": checks,
        "conclusion": "hypothesis supported by all stated checks" if supported else "hypothesis falsified by at least one check",
        "limitation": (
            "The labelled cases are synthetic and were written by this project. The measured accuracy therefore reflects "
            "agreement with the project's own adjudication standard, and a different annotator could disagree with "
            "individual labels. The full case list and the sweep grid are published so that a reviewer can re-label and "
            "re-run. The excluded case is published with its reason."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "case_count": len(cases),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # Accepted for interface consistency with the other catalogue scripts: this
    # experiment is exhaustive over the labelled set and takes no random seed.
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args(argv)
    payload = run()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
