"""The catalogue of runnable experiments.

Every entry is a self-contained script in ``experiments/`` that runs with the
standard library only, is deterministic given a seed, and emits a JSON result
containing: hypothesis, falsifier, method, metric, baseline, variants, checks and
conclusion.

Scope, stated plainly
---------------------
These experiments are *computational* and *self-contained*. They can verify
statements about algorithms, numeric methods and the engine's own verification
procedure. They cannot, offline, verify statements about the physical world: doing
that requires a source of measurements, which is what the source registry is for.
The catalogue therefore mixes:

* **capability experiments** - they prove the pipeline's experiment stage works
  end to end and produce the strongest evidence class (rank 1);
* **method experiments** - they validate the engine's own verification procedure,
  which is a prerequisite for trusting anything else it publishes.

The site labels every experiment with which of those two it is, so a reader is
never led to think a benchmark of sorting algorithms is research about batteries.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Topic
from ..util import content_tokens


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    script: str
    title: str
    purpose: str                      # capability | method
    hypothesis: str
    falsifier: str
    metric: str
    seeds: tuple[int, ...] = (7,)
    timeout_seconds: int = 300
    keywords: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "script": self.script,
            "title": self.title,
            "purpose": self.purpose,
            "hypothesis": self.hypothesis,
            "falsifier": self.falsifier,
            "metric": self.metric,
            "seeds": list(self.seeds),
            "timeout_seconds": self.timeout_seconds,
            "keywords": list(self.keywords),
            "run_command": f"python {self.script} --seed {self.seeds[0]} --out result.json",
        }


EXPERIMENTS: tuple[ExperimentSpec, ...] = (
    ExperimentSpec(
        experiment_id="verification-thresholds-v1",
        script="experiments/verification_thresholds.py",
        title="Calibrate the claim-verification thresholds",
        purpose="method",
        hypothesis=(
            "A threshold pair exists that reproduces every human label in the labelled verification case set with zero "
            "false supports."
        ),
        falsifier="No swept threshold pair achieves zero false supports, or the best pair disagrees with a non-excluded case.",
        metric="verdict accuracy on labelled cases",
        seeds=(0,),
        timeout_seconds=600,
        keywords=("verification", "evidence", "claims", "epistemics", "research methods", "trust", "accuracy"),
    ),
    ExperimentSpec(
        experiment_id="search-scaling-v1",
        script="experiments/search_scaling.py",
        title="Scaling of binary search comparison counts",
        purpose="capability",
        hypothesis="Binary search comparison count grows logarithmically, adding about one comparison per doubling of n.",
        falsifier="The observed count exceeds ceil(log2(n)) + 1, or doublings do not add about one comparison.",
        metric="mean element comparisons per search",
        seeds=(3,),
        keywords=("algorithm", "search", "complexity", "data structures", "scaling", "software"),
    ),
    ExperimentSpec(
        experiment_id="sorting-comparisons-v1",
        script="experiments/sorting_comparisons.py",
        title="Comparison counts of three sorting algorithms",
        purpose="capability",
        hypothesis="Merge sort and heapsort beat insertion sort on shuffled input; insertion sort wins on sorted input.",
        falsifier="Insertion sort wins on shuffled input, or loses on sorted input.",
        metric="mean element comparisons per run",
        seeds=(7,),
        keywords=("algorithm", "sorting", "complexity", "benchmark", "software", "performance"),
    ),
    ExperimentSpec(
        experiment_id="hash-collision-rates-v1",
        script="experiments/hash_collision_rates.py",
        title="Collision counts against the birthday law",
        purpose="capability",
        hypothesis="Mean colliding pairs for a modulo hash follows k(k-1)/(2m) within the simulated uniform interval.",
        falsifier="The observed mean falls outside the three-sigma interval of the simulated uniform model.",
        metric="mean colliding pairs",
        seeds=(11,),
        keywords=("hash", "collision", "probability", "data structures", "sampling", "software"),
    ),
    ExperimentSpec(
        experiment_id="scheduling-policies-v1",
        script="experiments/scheduling_policies.py",
        title="Scheduling policies on a stationary bandit: round-robin, epsilon-greedy, UCB1",
        purpose="capability",
        hypothesis=(
            "On a five-armed Bernoulli bandit with fixed means, UCB1 and epsilon-greedy both accumulate less "
            "pseudo-regret than round-robin; UCB1's regret grows sublinearly and a fixed exploration rate keeps "
            "paying a cost proportional to the horizon."
        ),
        falsifier=(
            "Round-robin is not the worst of the three, or UCB1's second-half regret is not below its first-half "
            "regret, or epsilon-greedy's second-half regret falls below the analytic exploration floor."
        ),
        metric="mean cumulative pseudo-regret",
        seeds=(5,),
        keywords=("scheduling", "prioritisation", "bandit", "exploration", "exploitation", "regret", "prioritise", "schedule"),
    ),
    ExperimentSpec(
        experiment_id="estimation-error-v1",
        script="experiments/estimation_error.py",
        title="Sampling and estimation error: how fast does RMSE fall with sample size?",
        purpose="capability",
        hypothesis=(
            "The RMSE of a sample mean falls proportionally to 1/sqrt(n) (log-log slope in [-0.6, -0.4]) and "
            "stays within [0.8, 1.25]x the analytic standard error on a standard normal and a unit uniform "
            "population."
        ),
        falsifier=(
            "The fitted log-log slope of RMSE against n falls outside the stated band on either population, or "
            "any observed RMSE falls outside the stated multiple of the analytic standard error."
        ),
        metric="root-mean-square error of the sample mean",
        seeds=(3,),
        keywords=(
            "sampling", "estimation", "error", "statistics", "variance", "uncertainty",
            "quantitative", "confidence", "measurement",
        ),
    ),
    ExperimentSpec(
        experiment_id="queueing-models-v1",
        script="experiments/queueing_models.py",
        title="Queueing models: do simulated M/M/1 and M/D/1 waits match the textbook formulas?",
        purpose="capability",
        hypothesis=(
            "At utilisation 0.8 with Poisson arrivals, a simulated FCFS queue reproduces rho/(mu(1-rho)) for "
            "M/M/1 and rho/(2 mu(1-rho)) for M/D/1 within tolerance, and M/D/1's mean wait is lower at equal load."
        ),
        falsifier=(
            "Either simulated mean wait falls outside three standard errors (with a five-percent relative floor) "
            "of its analytic value, or M/D/1 does not have the lower mean wait at equal load."
        ),
        metric="mean wait in queue per customer",
        seeds=(13,),
        keywords=(
            "queueing", "queue", "waiting", "latency", "throughput", "utilisation",
            "capacity", "service", "load",
        ),
    ),
)


def get_experiment(experiment_id: str) -> ExperimentSpec:
    for spec in EXPERIMENTS:
        if spec.experiment_id == experiment_id:
            return spec
    raise KeyError(f"unknown experiment: {experiment_id}")


def experiments_for_topic(topic: Topic, *, limit: int = 1) -> list[ExperimentSpec]:
    """Pick experiments whose declared keywords overlap the topic.

    An honest empty result is preferred to a forced match: if nothing in the
    catalogue relates to the question, the tournament's experimental criterion
    stays at zero and says so, rather than attaching an irrelevant benchmark to an
    unrelated question.
    """
    topic_terms = content_tokens(" ".join(topic.keywords) + " " + topic.title + " " + topic.question)
    scored: list[tuple[int, ExperimentSpec]] = []
    for spec in EXPERIMENTS:
        overlap = len(topic_terms & set(spec.keywords))
        if overlap:
            scored.append((overlap, spec))
    scored.sort(key=lambda item: (-item[0], item[1].experiment_id))
    return [spec for _score, spec in scored[:limit]]


def catalogue() -> list[dict]:
    return [spec.to_dict() for spec in EXPERIMENTS]
