"""The reasoning layer: competing personas, adversarial critics, tournaments."""

from __future__ import annotations

from .competition import generate_strategies, strategy_numbers_ok
from .critic import critique_strategy
from .discovery import discover_questions, score_candidate_topics
from .elo import EloTable
from .personas import Persona, personas_for
from .tournament import run_tournament, score_strategy

__all__ = [
    "Persona",
    "personas_for",
    "generate_strategies",
    "strategy_numbers_ok",
    "critique_strategy",
    "run_tournament",
    "score_strategy",
    "discover_questions",
    "score_candidate_topics",
    "EloTable",
]
