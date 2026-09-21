"""Persistent Elo ratings for personas and strategies.

The design document asks for an idea competition with a ranking that is not
simply "whoever writes the most convincing explanation". Elo is used here as a
*bookkeeping* device: every head-to-head comparison produced by the tournament
updates the ratings, so a persona's standing accumulates across cycles and across
topics, and a reader can see which briefs keep winning and which keep losing.

Ratings are stored in ``state/elo.json`` and are fully reproducible: given the
same tournament order and the same scores, the same ratings result.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..util import load_json, save_json, utcnow_iso

DEFAULT_RATING = 1500.0
K_FACTOR = 16.0


@dataclass
class EloTable:
    path: Path
    ratings: dict[str, float] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = ""

    # -- persistence -------------------------------------------------------
    @classmethod
    def load(cls, path: Path) -> "EloTable":
        payload = load_json(path, default={}) or {}
        return cls(
            path=Path(path),
            ratings={str(k): float(v) for k, v in (payload.get("ratings") or {}).items()},
            history=list(payload.get("history") or []),
            updated_at=payload.get("updated_at", ""),
        )

    def save(self) -> None:
        self.updated_at = utcnow_iso()
        save_json(
            self.path,
            {"ratings": self.ratings, "history": self.history[-500:], "updated_at": self.updated_at},
        )

    # -- rating maths ------------------------------------------------------
    def rating(self, key: str) -> float:
        return self.ratings.get(key, DEFAULT_RATING)

    @staticmethod
    def expected(score_a: float, score_b: float) -> float:
        return 1.0 / (1.0 + 10 ** ((score_b - score_a) / 400.0))

    def record(self, key_a: str, key_b: str, outcome_a: float, *, topic_id: str, criterion: str) -> dict[str, float]:
        """Update both ratings. ``outcome_a`` is 1.0 win, 0.5 draw, 0.0 loss."""
        ra, rb = self.rating(key_a), self.rating(key_b)
        expected_a = self.expected(ra, rb)
        delta = K_FACTOR * (outcome_a - expected_a)
        self.ratings[key_a] = round(ra + delta, 2)
        self.ratings[key_b] = round(rb - delta, 2)
        self.history.append(
            {
                "topic_id": topic_id,
                "criterion": criterion,
                "a": key_a,
                "b": key_b,
                "outcome_a": outcome_a,
                "rating_a": self.ratings[key_a],
                "rating_b": self.ratings[key_b],
                "recorded_at": utcnow_iso(),
            }
        )
        return {key_a: self.ratings[key_a], key_b: self.ratings[key_b]}

    # -- reporting ---------------------------------------------------------
    def leaderboard(self, prefix: str | None = None) -> list[dict[str, Any]]:
        rows = [
            {"key": key, "rating": round(value, 1)}
            for key, value in self.ratings.items()
            if prefix is None or key.startswith(prefix)
        ]
        rows.sort(key=lambda row: (-row["rating"], row["key"]))
        for index, row in enumerate(rows, start=1):
            row["rank"] = index
            row["matches"] = sum(1 for h in self.history if h["a"] == row["key"] or h["b"] == row["key"])
            row["wins"] = sum(
                1
                for h in self.history
                if (h["a"] == row["key"] and h["outcome_a"] == 1.0) or (h["b"] == row["key"] and h["outcome_a"] == 0.0)
            )
        return rows

    def to_dict(self) -> dict[str, Any]:
        return {
            "ratings": dict(sorted(self.ratings.items())),
            "leaderboard": self.leaderboard(),
            "matches": len(self.history),
            "updated_at": self.updated_at,
            "k_factor": K_FACTOR,
            "default_rating": DEFAULT_RATING,
        }

    def save_json_copy(self, path: Path) -> None:
        save_json(path, self.to_dict())


def load_elo(path: Path) -> EloTable:
    return EloTable.load(path)


def reset_elo(path: Path) -> None:
    Path(path).write_text(json.dumps({"ratings": {}, "history": [], "updated_at": utcnow_iso()}, indent=2) + "\n", encoding="utf-8")
