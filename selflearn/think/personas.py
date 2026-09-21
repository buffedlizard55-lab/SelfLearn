"""The competing thinkers.

Six briefs come straight from the project design document. Each persona answers
the same question from a different angle and, crucially, has a different rule for
*which verified claims it may use*. That is what makes the competition real
rather than cosmetic: the personas look at different parts of the evidence.

Selection is deterministic given the topic id, so a re-run reproduces the same
line-up, and the published site can state exactly which personas competed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ..config import PERSONAS


@dataclass(frozen=True)
class Persona:
    code: str
    name: str
    brief: str

    @property
    def persona_id(self) -> str:
        return f"persona-{self.code.lower()}"


ALL_PERSONAS: tuple[Persona, ...] = tuple(Persona(code, name, brief) for code, name, brief in PERSONAS)

# How each persona filters the claim set. The rules are deliberately simple and
# inspectable; each one is a predicate over a Claim.
NEGATIVE_MARKERS = (
    "no ",
    "not ",
    "never ",
    "failed",
    "failure",
    "decline",
    "declined",
    "decrease",
    "decreased",
    "limited",
    "unclear",
    "however",
    "challenge",
    "risk",
    "uncertain",
    "barrier",
    "costly",
)

COST_MARKERS = ("cost", "price", "eur", "usd", "dollar", "efficiency", "scal", "capacity", "throughput", "rate", "per ")
MECHANISM_MARKERS = ("because", "drives", "causes", "cause", "leads to", "due to", "results in", "mechanism")


def personas_for(topic_id: str, count: int = 6) -> list[Persona]:
    """Deterministically choose ``count`` personas for a topic.

    The ordering of personas around the circle is stable for a given topic id, so
    two different topics get genuinely different line-ups while every re-run of
    the same topic reproduces its own line-up exactly.
    """
    count = max(1, min(count, len(ALL_PERSONAS)))
    ordered = list(ALL_PERSONAS)
    if count >= len(ordered):
        return ordered
    digest = hashlib.sha256(topic_id.encode("utf-8")).digest()
    offset = digest[0] % len(ordered)
    rotated = ordered[offset:] + ordered[:offset]
    # Always include the conventional and the contrarian brief: without both, the
    # competition has no baseline to disagree with.
    must_have = [p for p in (ALL_PERSONAS[0], ALL_PERSONAS[1]) if p not in rotated[:count]]
    selected = rotated[: count - len(must_have)] + must_have
    # Preserve the canonical order for stable presentation.
    return sorted({p.code: p for p in selected}.values(), key=lambda p: p.code)


def rank_claims_for_persona(persona: Persona, claims: list) -> list:
    """Order a topic's claims according to what the persona is looking for."""

    def key(claim):
        text = claim.text.casefold()
        verdict_bonus = {"supported": 2.0, "partially_supported": 0.5}.get(claim.verification.verdict, -5.0)
        strength = (10 - claim.evidence_rank) / 10.0
        numbers = 1.0 if claim.verification.missing_numbers == [] else 0.0
        if persona.code == "A":
            return verdict_bonus + strength * 2 + numbers * 0.5
        if persona.code == "B":
            negative = 1.5 if any(marker in text for marker in NEGATIVE_MARKERS) else 0.0
            return verdict_bonus + negative + strength * 0.5
        if persona.code == "C":
            from ..util import extract_numbers

            return verdict_bonus + (2.0 if extract_numbers(claim.text) else 0.0) + strength
        if persona.code == "D":
            return verdict_bonus + strength
        if persona.code == "E":
            cost = 1.5 if any(marker in text for marker in COST_MARKERS) else 0.0
            return verdict_bonus + cost + strength
        # F - experimental: prefers quantified claims with a time reference.
        from ..util import extract_dates, extract_numbers

        return verdict_bonus + (2.0 if extract_numbers(claim.text) else 0.0) + (1.0 if extract_dates(claim.text) else 0.0)

    return sorted(claims, key=key, reverse=True)


def declares_mechanism(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in lowered for marker in MECHANISM_MARKERS)
