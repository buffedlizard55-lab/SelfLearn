"""Detect candidate contradictions between supported claims.

Scope and honesty note
----------------------
Detecting that two sentences genuinely disagree about the same quantity is a
hard natural-language problem. This module therefore does *not* claim to have
found contradictions; it produces **candidates for human review** using two
conservative, inspectable rules:

* **numeric divergence** - the claims are about the same subject (high token
  overlap) but assert disjoint numeric values.
* **polarity divergence** - the claims are near-identical in wording but one
  contains an explicit negation that the other lacks.

Every candidate is published with both claims, both sources and both links, and
is labelled as unresolved until a human or a stronger method resolves it.
"""

from __future__ import annotations

from ..models import Claim, Contradiction
from ..util import extract_numbers, similarity, stable_id

NEGATION_MARKERS = (
    " no ",
    " not ",
    "n't ",
    "never ",
    "none ",
    "without ",
    "fails to",
    "does not",
    "did not",
    "no significant",
    "no evidence",
)


def _has_negation(text: str) -> bool:
    padded = f" {text.casefold()} "
    return any(marker in padded for marker in NEGATION_MARKERS)


def detect_contradictions(
    claims: list[Claim],
    *,
    topic_id: str | None = None,
    similarity_threshold: float = 0.55,
) -> list[Contradiction]:
    """Return candidate contradictions among claims for one topic."""
    candidates = [c for c in claims if topic_id is None or c.topic_id == topic_id]
    candidates = [c for c in candidates if c.verification.verdict in {"supported", "partially_supported"}]
    found: list[Contradiction] = []
    seen: set[tuple[str, str]] = set()

    for index, claim_a in enumerate(candidates):
        for claim_b in candidates[index + 1 :]:
            if claim_a.source_name == claim_b.source_name and claim_a.evidence_id == claim_b.evidence_id:
                continue  # same document cannot contradict itself for our purposes
            key = tuple(sorted((claim_a.claim_id, claim_b.claim_id)))
            if key in seen:
                continue
            sim = similarity(claim_a.text, claim_b.text)
            if sim < similarity_threshold:
                continue

            numbers_a = extract_numbers(claim_a.text)
            numbers_b = extract_numbers(claim_b.text)
            kind = ""
            detail = ""
            if numbers_a and numbers_b and not (numbers_a & numbers_b):
                kind = "numeric"
                detail = (
                    f"Claims share {sim:.0%} of their content tokens but contain disjoint numeric values "
                    f"({', '.join(sorted(numbers_a))} vs {', '.join(sorted(numbers_b))}). "
                    "One of the two readings, the unit, or the time period differs."
                )
            elif _has_negation(claim_a.text) != _has_negation(claim_b.text):
                kind = "polar"
                detail = (
                    f"Claims share {sim:.0%} of their content tokens but only one contains an explicit negation. "
                    "Check whether they refer to the same population and time period."
                )
            if not kind:
                continue

            seen.add(key)
            found.append(
                Contradiction(
                    contradiction_id=stable_id("con", claim_a.claim_id, claim_b.claim_id),
                    topic_id=claim_a.topic_id,
                    claim_a=claim_a.claim_id,
                    claim_b=claim_b.claim_id,
                    kind=kind,
                    detail=detail,
                    severity="high" if sim >= 0.7 else "medium",
                    resolution="unresolved",
                )
            )
    return found
