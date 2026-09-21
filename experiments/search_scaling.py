#!/usr/bin/env python3
"""Experiment: how does binary search comparison count scale with array size?

Hypothesis
    The number of element comparisons needed by binary search on a sorted array of
    n elements grows logarithmically: each doubling of n adds approximately one
    comparison. The observed count stays at or below ceil(log2(n)) + 1.

    The tested sizes are exact powers of two, so a doubling is a single step in the
    size ladder and the increment between consecutive sizes is directly comparable
    with the predicted one comparison.

Falsifier
    The observed mean comparison count at any tested size exceeds ceil(log2(n)) + 1,
    or the increment between consecutive doublings is not approximately one.

Metric
    Mean element comparisons per successful and unsuccessful search.

Limitation
    This measures a textbook algorithm implemented in the standard library style;
    it is a check of the implementation and of the stated bound, not new knowledge
    about search. The value of the experiment to this project is that it produces a
    quantified, reproducible statement that later claims can be grounded in.

Run
    python experiments/search_scaling.py --seed 3 --out result.json
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import statistics
import sys

SIZES = (1_024, 2_048, 4_096, 8_192, 16_384, 32_768, 65_536, 131_072, 262_144, 524_288, 1_048_576)
TRIALS_PER_SIZE = 400


def binary_search(values: list[int], target: int) -> tuple[bool, int]:
    """Return (found, comparisons)."""
    low, high, comparisons = 0, len(values) - 1, 0
    while low <= high:
        comparisons += 1
        middle = (low + high) // 2
        if values[middle] == target:
            return True, comparisons
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return False, comparisons


def linear_search(values: list[int], target: int) -> tuple[bool, int]:
    comparisons = 0
    for value in values:
        comparisons += 1
        if value == target:
            return True, comparisons
    return False, comparisons


def run(seed: int) -> dict:
    generator = random.Random(seed)
    per_size: dict[str, dict[str, float]] = {}
    checks: list[dict] = []
    for size in SIZES:
        pool = sorted(generator.sample(range(0, size * 10), size))
        hits: list[int] = []
        misses: list[int] = []
        for _ in range(TRIALS_PER_SIZE):
            target = pool[generator.randrange(size)]
            found, comparisons = binary_search(pool, target)
            if found:
                hits.append(comparisons)
            absent = pool[-1] + 1
            _, miss_comparisons = binary_search(pool, absent)
            misses.append(miss_comparisons)

        bound = math.ceil(math.log2(size)) + 1
        per_size[str(size)] = {
            "mean_comparisons_hit": round(statistics.mean(hits), 3),
            "max_comparisons_hit": max(hits),
            "mean_comparisons_miss": round(statistics.mean(misses), 3),
            "theoretical_bound": bound,
            "log2_size": round(math.log2(size), 3),
        }
        checks.append(
            {
                "check": f"observed mean comparisons within the stated bound at n={size}",
                "outcome": statistics.mean(hits) <= bound and statistics.mean(misses) <= bound,
                "observed": (
                    f"mean_hit={statistics.mean(hits):.3f} mean_miss={statistics.mean(misses):.3f} bound={bound}"
                ),
            }
        )

    linear_comparisons: list[int] = []
    reference = sorted(generator.sample(range(0, 20_000), 10_000))
    for _ in range(TRIALS_PER_SIZE):
        target = reference[generator.randrange(len(reference))]
        _, comparisons = linear_search(reference, target)
        linear_comparisons.append(comparisons)
    baseline = statistics.mean(linear_comparisons)

    increments = []
    ordered = [str(size) for size in SIZES]
    for previous, current in zip(ordered, ordered[1:]):
        increments.append(
            round(per_size[current]["mean_comparisons_hit"] - per_size[previous]["mean_comparisons_hit"], 3)
        )
    increments_ok = all(0.5 <= value <= 1.6 for value in increments)
    checks.append(
        {
            "check": "each doubling of n adds approximately one comparison",
            "outcome": increments_ok,
            "observed": f"increments={increments}",
        }
    )

    supported = all(check["outcome"] for check in checks)
    return {
        "experiment_id": "search-scaling-v1",
        "hypothesis": (
            "Binary search comparison count grows logarithmically with array size: each doubling of n adds "
            "approximately one comparison, and the count stays at or below ceil(log2(n)) + 1."
        ),
        "falsifier": (
            "The observed mean comparison count at any tested size exceeds the stated bound, or the increment between "
            "consecutive doublings departs from one comparison."
        ),
        "method": (
            f"Deterministic binary search over sorted arrays of {len(SIZES)} sizes, {TRIALS_PER_SIZE} successful and "
            "unsuccessful searches per size, with a comparison counter."
        ),
        "metric": "mean element comparisons per search",
        "baseline": round(baseline, 3),
        "baseline_name": "linear search on a sorted array of 10000 elements (the largest decade-scale scan used as a reference point)",
        "variants": [
            {"name": f"binary_search_n_{size}", "value": per_size[size]["mean_comparisons_hit"]} for size in ordered
        ],
        "best_variant": f"binary_search_n_{ordered[-1]}",
        "best_value": per_size[ordered[-1]]["mean_comparisons_hit"],
        "sizes": per_size,
        "doubling_increments": increments,
        "checks": checks,
        "conclusion": "hypothesis supported by all stated checks" if supported else "hypothesis falsified by at least one check",
        "limitation": (
            "Comparison counts are counted by this implementation. The measurement characterises the algorithm and the "
            "stated bound; it is not evidence about any other search implementation."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "seed": seed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args(argv)
    payload = run(args.seed)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
