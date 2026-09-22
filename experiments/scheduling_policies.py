#!/usr/bin/env python3
"""Experiment: how do three scheduling policies compare on a stationary bandit?

The manager in ``selflearn/think/manager.py`` has to decide which question to work
on next with a fixed budget of cycles. That is a multi-armed bandit problem in
miniature: each question is an arm, each cycle is a pull, and the reward is what
the cycle produced. This experiment does not use the engine's real questions - it
uses a synthetic bandit whose arm means are known, so the regret of each policy
can be computed exactly from which arm was pulled.

Hypothesis
    On a K-armed Bernoulli bandit with fixed means, both an adaptive policy that
    explores in proportion to uncertainty (UCB1) and one that explores at a fixed
    rate (epsilon-greedy) accumulate less pseudo-regret than round-robin over a
    horizon of T pulls; UCB1's regret grows sublinearly (its second half of the
    horizon costs less than its first), while a fixed exploration rate keeps paying
    a cost proportional to T.

Falsifier
    Round-robin is not the worst of the three, or UCB1's second-half regret is not
    lower than its first-half regret, or epsilon-greedy's second-half regret falls
    below the analytic floor implied by its exploration rate.

Metric
    Mean cumulative pseudo-regret over the horizon: the sum over pulls of
    (best arm mean - pulled arm mean), averaged over independent trials. Because
    pseudo-regret uses the true means, round-robin's value is exact and serves as
    the analytic baseline.

Note on what this can and cannot show
    Arms are stationary Bernoulli variables with means chosen here. Real research
    questions are not stationary and their payoff is not a coin flip. The result
    says which policy wastes fewer pulls on a known toy problem; it says nothing
    about which question the engine should investigate next.

Run
    python experiments/scheduling_policies.py --seed 5 --out result.json
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import statistics
import sys

ARM_MEANS = (0.15, 0.25, 0.35, 0.45, 0.60)
HORIZON = 4000
TRIALS = 100
EPSILON = 0.10


def pull(generator: random.Random, mean: float) -> int:
    return 1 if generator.random() < mean else 0


def run_round_robin(generator: random.Random, horizon: int) -> list[int]:
    """Return the sequence of arm indices pulled."""
    return [t % len(ARM_MEANS) for t in range(horizon)]


def run_epsilon_greedy(generator: random.Random, horizon: int, epsilon: float) -> list[int]:
    counts = [0] * len(ARM_MEANS)
    sums = [0] * len(ARM_MEANS)
    pulled: list[int] = []
    for t in range(horizon):
        if t < len(ARM_MEANS):
            arm = t  # pull each arm once first
        elif generator.random() < epsilon:
            arm = generator.randrange(len(ARM_MEANS))
        else:
            estimates = [sums[i] / counts[i] for i in range(len(ARM_MEANS))]
            best = max(estimates)
            arm = min(i for i, value in enumerate(estimates) if value == best)  # deterministic tie-break
        reward = pull(generator, ARM_MEANS[arm])
        counts[arm] += 1
        sums[arm] += reward
        pulled.append(arm)
    return pulled


def run_ucb1(generator: random.Random, horizon: int) -> list[int]:
    counts = [0] * len(ARM_MEANS)
    sums = [0] * len(ARM_MEANS)
    pulled: list[int] = []
    for t in range(horizon):
        if t < len(ARM_MEANS):
            arm = t
        else:
            scores = [
                sums[i] / counts[i] + math.sqrt(2.0 * math.log(t) / counts[i]) for i in range(len(ARM_MEANS))
            ]
            best = max(scores)
            arm = min(i for i, value in enumerate(scores) if value == best)
        reward = pull(generator, ARM_MEANS[arm])
        counts[arm] += 1
        sums[arm] += reward
        pulled.append(arm)
    return pulled


def pseudo_regret(pulled: list[int]) -> tuple[float, float, float]:
    """(total, first half, second half) pseudo-regret of a pull sequence."""
    best = max(ARM_MEANS)
    gaps = [best - ARM_MEANS[arm] for arm in pulled]
    half = len(gaps) // 2
    return sum(gaps), sum(gaps[:half]), sum(gaps[half:])


def run(seed: int, horizon: int = HORIZON, trials: int = TRIALS, epsilon: float = EPSILON) -> dict:
    generator = random.Random(seed)
    policies = {
        "round_robin": lambda g: run_round_robin(g, horizon),
        "epsilon_greedy": lambda g: run_epsilon_greedy(g, horizon, epsilon),
        "ucb1": lambda g: run_ucb1(g, horizon),
    }
    totals: dict[str, list[float]] = {name: [] for name in policies}
    first_half: dict[str, list[float]] = {name: [] for name in policies}
    second_half: dict[str, list[float]] = {name: [] for name in policies}
    for _ in range(trials):
        for name, policy in policies.items():
            total, first, second = pseudo_regret(policy(generator))
            totals[name].append(total)
            first_half[name].append(first)
            second_half[name].append(second)

    means = {name: statistics.mean(values) for name, values in totals.items()}
    first_means = {name: statistics.mean(values) for name, values in first_half.items()}
    second_means = {name: statistics.mean(values) for name, values in second_half.items()}

    best = max(ARM_MEANS)
    mean_gap = sum(best - mean for mean in ARM_MEANS) / len(ARM_MEANS)
    # Round-robin pulls each arm horizon/K times, so its pseudo-regret is exact.
    analytic_round_robin = horizon * mean_gap
    # With probability epsilon a pull is uniform over all arms, costing mean_gap in
    # expectation; the exploitation pulls add a non-negative amount on top. Half
    # of that floor is used so that sampling noise over `trials` cannot fail a
    # check that holds in expectation.
    exploration_floor_second_half = 0.5 * epsilon * (horizon - horizon // 2) * mean_gap

    checks = [
        {
            "check": "round-robin pseudo-regret equals the analytic value T x mean gap",
            "outcome": abs(means["round_robin"] - analytic_round_robin) < 1e-6,
            "observed": f"observed={means['round_robin']:.4f} analytic={analytic_round_robin:.4f}",
        },
        {
            "check": "UCB1 accumulates less pseudo-regret than round-robin",
            "outcome": means["ucb1"] < means["round_robin"],
            "observed": f"ucb1={means['ucb1']:.3f} round_robin={means['round_robin']:.3f}",
        },
        {
            "check": "epsilon-greedy accumulates less pseudo-regret than round-robin",
            "outcome": means["epsilon_greedy"] < means["round_robin"],
            "observed": f"epsilon_greedy={means['epsilon_greedy']:.3f} round_robin={means['round_robin']:.3f}",
        },
        {
            "check": "UCB1 regret is sublinear: the second half of the horizon costs less than the first",
            "outcome": second_means["ucb1"] < first_means["ucb1"],
            "observed": f"first_half={first_means['ucb1']:.3f} second_half={second_means['ucb1']:.3f}",
        },
        {
            "check": "a fixed exploration rate keeps paying: epsilon-greedy second-half regret stays above half its analytic floor",
            "outcome": second_means["epsilon_greedy"] >= exploration_floor_second_half,
            "observed": (
                f"second_half={second_means['epsilon_greedy']:.3f} floor={exploration_floor_second_half:.3f}"
            ),
        },
    ]
    supported = all(check["outcome"] for check in checks)
    best_name = min(means, key=lambda name: (means[name], name))

    return {
        "experiment_id": "scheduling-policies-v1",
        "hypothesis": (
            f"On a {len(ARM_MEANS)}-armed Bernoulli bandit with fixed means over {horizon} pulls, UCB1 and "
            f"epsilon-greedy (epsilon={epsilon}) both accumulate less pseudo-regret than round-robin, UCB1's regret "
            "grows sublinearly, and a fixed exploration rate keeps paying a cost proportional to the horizon."
        ),
        "falsifier": (
            "Round-robin is not the worst of the three, or UCB1's second-half regret is not below its first-half "
            "regret, or epsilon-greedy's second-half regret falls below the analytic exploration floor."
        ),
        "method": (
            f"{trials} independent trials of {horizon} pulls per policy on arms with means {list(ARM_MEANS)}; "
            "pseudo-regret computed from the true mean of each pulled arm, so the metric has no reward noise."
        ),
        "metric": "mean cumulative pseudo-regret",
        "baseline": round(analytic_round_robin, 4),
        "baseline_name": "round-robin (analytic: T x mean gap)",
        "variants": [
            {"name": name, "value": round(means[name], 4)} for name in ("round_robin", "epsilon_greedy", "ucb1")
        ],
        "best_variant": best_name,
        "best_value": round(means[best_name], 4),
        "regret_by_half": {
            name: {"first_half": round(first_means[name], 4), "second_half": round(second_means[name], 4)}
            for name in policies
        },
        "checks": checks,
        "conclusion": "hypothesis supported by all stated checks" if supported else "hypothesis falsified by at least one check",
        "limitation": (
            "Stationary Bernoulli arms with means chosen in this script. The result compares policies on a known "
            "toy problem; it is not a measurement of any real research schedule and does not say which question "
            "the engine should investigate next."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "seed": seed,
        "arm_means": list(ARM_MEANS),
        "horizon": horizon,
        "trials": trials,
        "epsilon": epsilon,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=5)
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
