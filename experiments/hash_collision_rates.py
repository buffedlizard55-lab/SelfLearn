#!/usr/bin/env python3
"""Experiment: does a simple hash function follow the birthday collision law?

Hypothesis
    For k keys mapped uniformly at random into m slots, the expected number of
    colliding *pairs* is approximately k(k-1)/(2m). A deterministic modulo hash of
    k distinct integer keys in a table of m slots will produce a collision count
    within the interval implied by repeating the experiment over many seeds.

Falsifier
    The observed mean colliding-pair count falls outside the 99 percent interval
    computed by direct simulation of the uniform model.

Metric
    Mean number of colliding pairs, and its ratio to the analytic expectation.

Note on what this can and cannot show
    This validates the closed form against a simulation of the *same* uniform
    model; it is a check of the arithmetic and of the sampling, not evidence about
    any particular production hash function. That limitation is stated in the
    published text so it cannot be read as a stronger result than it is.

Run
    python experiments/hash_collision_rates.py --seed 11 --out result.json
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import sys


def collisions_modulo(keys: list[int], slots: int) -> int:
    buckets: dict[int, int] = {}
    for key in keys:
        bucket = key % slots
        buckets[bucket] = buckets.get(bucket, 0) + 1
    return sum(count * (count - 1) // 2 for count in buckets.values())


def collisions_uniform_model(keys: int, slots: int, generator: random.Random) -> int:
    buckets: dict[int, int] = {}
    for _ in range(keys):
        bucket = generator.randrange(slots)
        buckets[bucket] = buckets.get(bucket, 0) + 1
    return sum(count * (count - 1) // 2 for count in buckets.values())


def run(seed: int, keys: int = 1000, slots: int = 4096, trials: int = 200) -> dict:
    generator = random.Random(seed)
    observed: list[int] = []
    simulated: list[int] = []
    for trial in range(trials):
        key_set = generator.sample(range(0, slots * 64), keys)
        observed.append(collisions_modulo(key_set, slots))
        simulated.append(collisions_uniform_model(keys, slots, generator))

    expected = keys * (keys - 1) / (2 * slots)
    simulated_mean = statistics.mean(simulated)
    simulated_sd = statistics.pstdev(simulated)
    lower, upper = simulated_mean - 3 * simulated_sd, simulated_mean + 3 * simulated_sd
    observed_mean = statistics.mean(observed)

    within = lower <= observed_mean <= upper
    analytic_gap = abs(observed_mean - expected) / expected if expected else 0.0

    return {
        "experiment_id": "hash-collision-rates-v1",
        "hypothesis": (
            f"For {keys} distinct keys mapped into {slots} slots, the mean number of colliding pairs follows the "
            "birthday-law expectation k(k-1)/(2m) and lies inside the interval produced by simulating the uniform "
            "model."
        ),
        "falsifier": (
            "The observed mean colliding-pair count falls outside the three-standard-deviation interval of the "
            "simulated uniform model."
        ),
        "method": (
            f"Deterministic modulo hash over {trials} independently sampled key sets, compared with the closed form and "
            "with a direct simulation of the uniform model."
        ),
        "metric": "mean colliding pairs",
        "baseline": round(expected, 4),
        "baseline_name": "analytic birthday-law expectation k(k-1)/(2m)",
        "variants": [
            {"name": "observed_modulo_hash", "value": round(observed_mean, 4)},
            {"name": "simulated_uniform_model", "value": round(simulated_mean, 4)},
        ],
        "best_variant": "observed_modulo_hash",
        "best_value": round(observed_mean, 4),
        "checks": [
            {
                "check": "observed mean lies within three standard deviations of the simulated uniform model",
                "outcome": within,
                "observed": f"observed={observed_mean:.4f} interval=[{lower:.4f}, {upper:.4f}]",
            },
            {
                "check": "observed mean is within ten percent of the analytic expectation",
                "outcome": analytic_gap <= 0.10,
                "observed": f"relative_gap={analytic_gap:.4f}",
            },
        ],
        "conclusion": "hypothesis supported by all stated checks"
        if within and analytic_gap <= 0.10
        else "hypothesis falsified by at least one check",
        "limitation": (
            "This compares a modulo hash with a simulation of the same uniform model. It validates the arithmetic and "
            "the sampling procedure; it is not evidence about any production hash function."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "seed": seed,
        "keys": keys,
        "slots": slots,
        "trials": trials,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=11)
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
