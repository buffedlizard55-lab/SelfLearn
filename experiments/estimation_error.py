#!/usr/bin/env python3
"""Experiment: how fast does estimation error fall with sample size?

Why this experiment exists
    Every quantitative claim the engine publishes is an estimate of something.
    This experiment measures the one property every estimate shares: how the
    error of a sample mean falls with the number of samples. It is the smallest
    honest study of sampling and estimation error that can run with no network
    and no data: the populations are synthetic and their means and standard
    deviations are known in closed form, so the estimator's error can be
    computed exactly per replication.

Hypothesis
    For the sample mean of independent draws from a population with known mean
    and finite variance, the root-mean-square error of the estimate falls
    proportionally to 1/sqrt(n): quadrupling the sample size halves the RMSE.
    Two populations are measured - a standard normal and a unit uniform - and
    the observed RMSE agrees with the analytic standard error sigma/sqrt(n).

Falsifier
    The fitted log-log slope of RMSE against n falls outside [-0.6, -0.4] on
    either population (the analytic value is -0.5), or any observed RMSE falls
    outside [0.8, 1.25] times the analytic standard error at that sample size.

Metric
    Root-mean-square error of the sample mean as an estimate of the known
    population mean, over independent replications at each sample size. Bias
    (mean signed error) is recorded beside it.

Note on what this can and cannot show
    The populations are a Gaussian and a uniform distribution chosen in this
    script. The 1/sqrt(n) rate holds for any distribution with finite variance;
    it says nothing about the error of any real measurement, and it does not
    cover estimators other than the sample mean.

Run
    python experiments/estimation_error.py --seed 3 --out result.json
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import statistics
import sys

SIZES = (16, 64, 256, 1024, 4096)
TRIALS = 400
SLOPE_BAND = (-0.6, -0.4)
RATIO_BAND = (0.8, 1.25)

#: name -> (draw function, known mean, known sigma)
POPULATIONS = {
    "gaussian": (lambda rng: rng.gauss(0.0, 1.0), 0.0, 1.0),
    "uniform": (lambda rng: rng.uniform(0.0, 1.0), 0.5, math.sqrt(1.0 / 12.0)),
}


def sample_mean(draw, rng: random.Random, n: int) -> float:
    return sum(draw(rng) for _ in range(n)) / n


def loglog_slope(sizes: tuple[int, ...], rmses: list[float]) -> float:
    """Least-squares slope of log(RMSE) against log(n)."""
    xs = [math.log(n) for n in sizes]
    ys = [math.log(value) for value in rmses]
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = sum((x - x_mean) ** 2 for x in xs)
    return numerator / denominator


def run(seed: int, sizes: tuple[int, ...] = SIZES, trials: int = TRIALS) -> dict:
    rng = random.Random(seed)
    rows = {}
    for name, (draw, true_mean, sigma) in POPULATIONS.items():
        cells = []
        for n in sizes:
            errors = [sample_mean(draw, rng, n) - true_mean for _ in range(trials)]
            rmse = math.sqrt(sum(error * error for error in errors) / trials)
            bias = statistics.mean(errors)
            analytic = sigma / math.sqrt(n)
            cells.append(
                {
                    "n": n,
                    "rmse": round(rmse, 6),
                    "bias": round(bias, 6),
                    "analytic_standard_error": round(analytic, 6),
                    "ratio_observed_to_analytic": round(rmse / analytic, 4),
                    "analytic_bias_standard_error": round(analytic / math.sqrt(trials), 6),
                }
            )
        rows[name] = {
            "true_mean": true_mean,
            "sigma": sigma,
            "cells": cells,
            "loglog_slope": round(loglog_slope(sizes, [cell["rmse"] for cell in cells]), 4),
        }

    checks = []
    for name, row in rows.items():
        slope = row["loglog_slope"]
        checks.append(
            {
                "check": f"{name}: RMSE falls as 1/sqrt(n) (log-log slope in [{SLOPE_BAND[0]}, {SLOPE_BAND[1]}])",
                "outcome": SLOPE_BAND[0] <= slope <= SLOPE_BAND[1],
                "observed": f"slope={slope}",
            }
        )
        worst = max(row["cells"], key=lambda cell: abs(cell["ratio_observed_to_analytic"] - 1.0))
        checks.append(
            {
                "check": (
                    f"{name}: every RMSE within [{RATIO_BAND[0]}, {RATIO_BAND[1]}]x the analytic "
                    "standard error"
                ),
                "outcome": all(
                    RATIO_BAND[0] <= cell["ratio_observed_to_analytic"] <= RATIO_BAND[1]
                    for cell in row["cells"]
                ),
                "observed": (
                    f"worst cell n={worst['n']} ratio={worst['ratio_observed_to_analytic']} "
                    f"(rmse={worst['rmse']}, analytic={worst['analytic_standard_error']})"
                ),
            }
        )
        biased = [
            cell
            for cell in row["cells"]
            if abs(cell["bias"]) > 4.0 * cell["analytic_bias_standard_error"] + 1e-12
        ]
        checks.append(
            {
                "check": f"{name}: no measured bias beyond four analytic bias standard errors",
                "outcome": not biased,
                "observed": (
                    "no cell beyond the band"
                    if not biased
                    else f"biased cells: {[(cell['n'], cell['bias']) for cell in biased]}"
                ),
            }
        )

    supported = all(check["outcome"] for check in checks)
    largest = sizes[-1]
    variants = [
        {
            "name": f"{name} (RMSE x sqrt(n) / sigma at n={largest})",
            "value": round(
                rows[name]["cells"][-1]["ratio_observed_to_analytic"], 4
            ),
        }
        for name in sorted(rows)
    ]
    # The value every population is chasing is 1.0 (observed error exactly the
    # analytic standard error), so "best" is the closest to 1, not the smallest.
    best = min(variants, key=lambda row: (abs(row["value"] - 1.0), row["name"]))

    return {
        "experiment_id": "estimation-error-v1",
        "hypothesis": (
            "For the sample mean of independent draws from a population with known mean and finite variance, "
            f"RMSE falls proportionally to 1/sqrt(n) (log-log slope in [{SLOPE_BAND[0]}, {SLOPE_BAND[1]}]) and "
            f"observed RMSE stays within [{RATIO_BAND[0]}, {RATIO_BAND[1]}]x the analytic standard error "
            "on a standard normal and a unit uniform population."
        ),
        "falsifier": (
            "The fitted log-log slope of RMSE against n falls outside the stated band on either population, "
            "or any observed RMSE falls outside the stated multiple of the analytic standard error."
        ),
        "method": (
            f"{trials} independent replications of the sample mean at each of n={list(sizes)} draws, "
            "per population; the true mean and sigma are known in closed form, so the error of every "
            "replication is exact rather than estimated."
        ),
        "metric": "root-mean-square error of the sample mean",
        "baseline": round(POPULATIONS["gaussian"][2] / math.sqrt(largest), 6),
        "baseline_name": f"analytic standard error sigma/sqrt(n) of the gaussian at n={largest}",
        "variants": variants,
        "best_variant": best["name"],
        "best_value": best["value"],
        "rmse_by_size": {
            name: {str(cell["n"]): cell["rmse"] for cell in row["cells"]} for name, row in rows.items()
        },
        "slopes": {name: rows[name]["loglog_slope"] for name in sorted(rows)},
        "checks": checks,
        "conclusion": (
            "hypothesis supported by all stated checks" if supported else "hypothesis falsified by at least one check"
        ),
        "limitation": (
            "Synthetic Gaussian and uniform populations, sample mean only. The 1/sqrt(n) rate is a statement "
            "about independent draws from a fixed distribution with finite variance; it is not a measurement "
            "of any real quantity and says nothing about biased or dependent data."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "seed": seed,
        "sizes": list(sizes),
        "trials": trials,
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
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
