#!/usr/bin/env python3
"""Experiment: comparison counts of three sorting algorithms.

Hypothesis
    On a shuffled array of 256 distinct integers, merge sort and heapsort use
    fewer element comparisons than insertion sort; on an already sorted array of
    the same size, insertion sort uses fewer comparisons than either.

Falsifier
    Insertion sort uses fewer comparisons than merge sort on the shuffled input,
    or does not use fewer than merge sort on the sorted input.

Metric
    Mean number of element comparisons per run, over a fixed number of seeds.

Why this experiment exists
    It is the smallest experiment with a verifiable outcome that can be run on any
    machine with no network and no data. Its purpose in the project is to
    demonstrate the *shape* of an honest experiment: a stated hypothesis, a stated
    falsifier, a measured baseline, a recorded environment, and a reproducible
    seed. It produces evidence of the strongest class in the hierarchy
    (``direct_experiment``).

Run
    python experiments/sorting_comparisons.py --seed 7 --out result.json
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import sys
import time

N = 256
REPEATS = 15

COMPARISONS = {"insertion_sort": 0, "merge_sort": 0, "heapsort": 0}


def reset() -> None:
    for key in COMPARISONS:
        COMPARISONS[key] = 0


def insertion_sort(values: list[int]) -> list[int]:
    data = list(values)
    for index in range(1, len(data)):
        key = data[index]
        position = index - 1
        while position >= 0:
            COMPARISONS["insertion_sort"] += 1
            if data[position] <= key:
                break
            data[position + 1] = data[position]
            position -= 1
        data[position + 1] = key
    return data


def merge_sort(values: list[int]) -> list[int]:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        COMPARISONS["merge_sort"] += 1
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def heapsort(values: list[int]) -> list[int]:
    data = list(values)
    n = len(data)

    def sift_down(start: int, end: int) -> None:
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break
            if child + 1 <= end:
                COMPARISONS["heapsort"] += 1
                if data[child] < data[child + 1]:
                    child += 1
            COMPARISONS["heapsort"] += 1
            if data[root] < data[child]:
                data[root], data[child] = data[child], data[root]
                root = child
            else:
                break

    for start in range((n - 2) // 2, -1, -1):
        sift_down(start, n - 1)
    for end in range(n - 1, 0, -1):
        data[end], data[0] = data[0], data[end]
        sift_down(0, end - 1)
    return data


ALGORITHMS = {
    "insertion_sort": insertion_sort,
    "merge_sort": merge_sort,
    "heapsort": heapsort,
}


def build_input(profile: str, seed: int) -> list[int]:
    generator = random.Random(seed)
    values = list(range(N))
    if profile == "shuffled":
        generator.shuffle(values)
    elif profile == "reversed":
        values.reverse()
    elif profile != "sorted":
        raise ValueError(f"unknown profile: {profile}")
    return values


def run(seed: int) -> dict:
    results: dict[str, dict[str, float]] = {}
    checks_passed = []
    for profile in ("shuffled", "sorted", "reversed"):
        per_algorithm: dict[str, list[int]] = {name: [] for name in ALGORITHMS}
        time_taken: dict[str, list[float]] = {name: [] for name in ALGORITHMS}
        for repeat in range(REPEATS):
            values = build_input(profile, seed + repeat)
            expected = sorted(values)
            for name, function in ALGORITHMS.items():
                reset()
                started = time.perf_counter()
                output = function(values)
                time_taken[name].append(time.perf_counter() - started)
                if output != expected:
                    raise AssertionError(f"{name} produced an incorrect sort on profile {profile}")
                per_algorithm[name].append(COMPARISONS[name])
        results[profile] = {
            "mean_comparisons": {name: round(statistics.mean(vals), 2) for name, vals in per_algorithm.items()},
            "min_comparisons": {name: min(vals) for name, vals in per_algorithm.items()},
            "max_comparisons": {name: max(vals) for name, vals in per_algorithm.items()},
            "mean_seconds": {name: round(statistics.mean(vals), 8) for name, vals in time_taken.items()},
        }

    shuffled = results["shuffled"]["mean_comparisons"]
    sorted_profile = results["sorted"]["mean_comparisons"]
    checks_passed.append(
        {
            "check": "merge sort uses fewer comparisons than insertion sort on shuffled input",
            "outcome": shuffled["merge_sort"] < shuffled["insertion_sort"],
            "observed": f"merge_sort={shuffled['merge_sort']} insertion_sort={shuffled['insertion_sort']}",
        }
    )
    checks_passed.append(
        {
            "check": "heapsort uses fewer comparisons than insertion sort on shuffled input",
            "outcome": shuffled["heapsort"] < shuffled["insertion_sort"],
            "observed": f"heapsort={shuffled['heapsort']} insertion_sort={shuffled['insertion_sort']}",
        }
    )
    checks_passed.append(
        {
            "check": "insertion sort uses fewer comparisons than merge sort on sorted input",
            "outcome": sorted_profile["insertion_sort"] < sorted_profile["merge_sort"],
            "observed": (
                f"insertion_sort={sorted_profile['insertion_sort']} merge_sort={sorted_profile['merge_sort']}"
            ),
        }
    )
    supported = all(check["outcome"] for check in checks_passed)
    return {
        "experiment_id": "sorting-comparisons-v1",
        "hypothesis": (
            "On a shuffled array of 256 distinct integers, merge sort and heapsort use fewer element comparisons than "
            "insertion sort; on an already sorted array of the same size, insertion sort uses fewer comparisons than "
            "either."
        ),
        "falsifier": (
            "Insertion sort uses fewer comparisons than merge sort on the shuffled input, or does not use fewer than "
            "merge sort on the sorted input."
        ),
        "method": f"Deterministic in-process benchmark, {REPEATS} seeds per input profile, comparison counter per algorithm.",
        "metric": "mean element comparisons per run",
        "baseline": shuffled["insertion_sort"],
        "baseline_name": "insertion_sort on shuffled input",
        "variants": [{"name": name, "value": value} for name, value in sorted(shuffled.items())],
        "best_variant": min(shuffled, key=lambda name: shuffled[name]),
        "best_value": min(shuffled.values()),
        "profiles": results,
        "checks": checks_passed,
        "conclusion": "hypothesis supported by all stated checks" if supported else "hypothesis falsified by at least one check",
        "environment": environment(),
        "seed": seed,
        "sample_size": N,
    }


def environment() -> dict:
    import os

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=7)
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
