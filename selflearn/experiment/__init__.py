"""The experiment engine: run code, record the result, cite it as evidence."""

from __future__ import annotations

from .catalogue import EXPERIMENTS, ExperimentSpec, experiments_for_topic, get_experiment
from .runner import ExperimentRun, run_experiment, to_evidence, to_result

__all__ = [
    "EXPERIMENTS",
    "ExperimentSpec",
    "ExperimentRun",
    "experiments_for_topic",
    "get_experiment",
    "run_experiment",
    "to_evidence",
    "to_result",
]
