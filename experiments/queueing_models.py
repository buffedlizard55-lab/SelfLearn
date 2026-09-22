#!/usr/bin/env python3
"""Experiment: do simulated queues match the textbook waiting-time formulas?

Why this experiment exists
    Waiting-time formulas (M/M/1 and M/D/1) are among the few quantitative
    claims about service systems that have an exact closed form. That makes them
    an unusually honest test case: a simulation either reproduces the published
    formula at a stated tolerance or it does not. This experiment measures both
    and compares them - the classic result that removing variance from service
    time, at equal load, lowers the mean wait.

Hypothesis
    At utilisation rho = 0.8 with a single server and Poisson arrivals, a
    first-come-first-served queue with exponential service of mean 1/mu
    (M/M/1) has mean wait in queue Wq = rho / (mu (1 - rho)), and with constant
    service of the same mean (M/D/1) has half that, Wq = rho / (2 mu (1 - rho)).
    A seeded simulation of both stays within three standard errors (with a
    five-percent relative floor for Monte Carlo noise) of the analytic means,
    and M/D/1's mean wait is lower than M/M/1's at equal load.

Falsifier
    Either simulated mean wait falls outside its stated tolerance band around
    the analytic value, or the M/D/1 mean wait is not lower than the M/M/1 mean
    wait at the same utilisation.

Metric
    Mean wait in queue per customer, over independent trials, with the first
    portion of each run discarded as warm-up. The standard error is computed
    across the independent trial means, not across the autocorrelated
    per-customer waits.

Note on what this can and cannot show
    These are textbook queues: Poisson arrivals, one server, exponential or
    constant service, unbounded capacity. Real systems burst, retry and block.
    The result says the formulas and the simulation agree on the model; it is
    not a statement about any deployed system's latency.

Run
    python experiments/queueing_models.py --seed 13 --out result.json
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import statistics
import sys

MU = 1.0
RHO = 0.8
LAMBDA = RHO * MU
CUSTOMERS = 40_000
WARMUP = 4_000
TRIALS = 20
RELATIVE_FLOOR = 0.05


def analytic_wq(service_kind: str) -> float:
    """Pollaczek-Khinchine at zero initial wait: rho/(mu(1-rho)) for M, half for D."""
    base = RHO / (MU * (1.0 - RHO))
    return base if service_kind == "exponential" else base / 2.0


def simulate_trial(rng: random.Random, service_kind: str, customers: int, warmup: int) -> list[float]:
    """Waits in queue for one FCFS run (Lindley's recursion), warm-up excluded."""
    now_free = 0.0
    arrival = 0.0
    waits: list[float] = []
    for index in range(customers):
        arrival += rng.expovariate(LAMBDA)
        wait = max(0.0, now_free - arrival)
        service = rng.expovariate(MU) if service_kind == "exponential" else 1.0 / MU
        now_free = arrival + wait + service
        if index >= warmup:
            waits.append(wait)
    return waits


def run(
    seed: int,
    trials: int = TRIALS,
    customers: int = CUSTOMERS,
    warmup: int = WARMUP,
) -> dict:
    rng = random.Random(seed)
    results = {}
    for service_kind in ("exponential", "constant"):
        trial_means = [
            statistics.mean(simulate_trial(rng, service_kind, customers, warmup))
            for _ in range(trials)
        ]
        mean_wq = statistics.mean(trial_means)
        standard_error = statistics.stdev(trial_means) / math.sqrt(trials) if trials > 1 else 0.0
        analytic = analytic_wq(service_kind)
        results[service_kind] = {
            "model": "M/M/1" if service_kind == "exponential" else "M/D/1",
            "mean_wait_in_queue": round(mean_wq, 6),
            "standard_error_across_trials": round(standard_error, 6),
            "analytic_mean_wait_in_queue": round(analytic, 6),
            "tolerance": round(max(3.0 * standard_error, RELATIVE_FLOOR * analytic), 6),
            "trial_means": [round(value, 6) for value in trial_means],
        }

    checks = []
    for service_kind, row in results.items():
        difference = abs(row["mean_wait_in_queue"] - row["analytic_mean_wait_in_queue"])
        checks.append(
            {
                "check": (
                    f"{row['model']}: simulated mean wait within tolerance of the analytic "
                    "Pollaczek-Khinchine value"
                ),
                "outcome": difference <= row["tolerance"],
                "observed": (
                    f"simulated={row['mean_wait_in_queue']} analytic={row['analytic_mean_wait_in_queue']} "
                    f"difference={round(difference, 6)} tolerance={row['tolerance']}"
                ),
            }
        )
    md1 = results["constant"]["mean_wait_in_queue"]
    mm1 = results["exponential"]["mean_wait_in_queue"]
    checks.append(
        {
            "check": "M/D/1 mean wait is lower than M/M/1 at equal load (service variance removed)",
            "outcome": md1 < mm1,
            "observed": f"M/D/1={md1} M/M/1={mm1}",
        }
    )
    supported = all(check["outcome"] for check in checks)
    best = "M/D/1" if md1 < mm1 else "M/M/1"

    return {
        "experiment_id": "queueing-models-v1",
        "hypothesis": (
            f"At utilisation {RHO} with Poisson arrivals of rate {LAMBDA} and one server with mean service "
            f"1/{MU}, the simulated mean wait in queue reproduces rho/(mu(1-rho)) = "
            f"{round(analytic_wq('exponential'), 4)} for M/M/1 and rho/(2 mu(1-rho)) = "
            f"{round(analytic_wq('constant'), 4)} for M/D/1 within tolerance, and M/D/1's mean wait is lower."
        ),
        "falsifier": (
            "Either simulated mean wait falls outside three standard errors (with a five-percent relative "
            "floor) of its analytic value, or M/D/1 does not have the lower mean wait at equal load."
        ),
        "method": (
            f"{trials} independent FCFS runs per model of {customers} customers each (Lindley recursion), "
            f"first {warmup} customers discarded as warm-up; standard error computed across trial means."
        ),
        "metric": "mean wait in queue per customer",
        "baseline": round(analytic_wq("exponential"), 6),
        "baseline_name": "M/M/1 analytic Wq = rho/(mu(1-rho))",
        "variants": [
            {"name": row["model"], "value": row["mean_wait_in_queue"]}
            for row in (results["exponential"], results["constant"])
        ],
        "best_variant": best,
        "best_value": results["constant" if best == "M/D/1" else "exponential"]["mean_wait_in_queue"],
        "analytic": {row["model"]: row["analytic_mean_wait_in_queue"] for row in results.values()},
        "standard_errors": {
            row["model"]: row["standard_error_across_trials"] for row in results.values()
        },
        "checks": checks,
        "conclusion": (
            "hypothesis supported by all stated checks" if supported else "hypothesis falsified by at least one check"
        ),
        "limitation": (
            "Textbook queues only: Poisson arrivals, one server, exponential or constant service, unbounded "
            "capacity, FCFS discipline. This measures agreement between a simulation and the published "
            "formulas on that model; it is not a latency measurement of any real system."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "seed": seed,
        "mu": MU,
        "rho": RHO,
        "lambda": LAMBDA,
        "customers": customers,
        "warmup": warmup,
        "trials": trials,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args(argv)
    payload = run(args.seed)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
