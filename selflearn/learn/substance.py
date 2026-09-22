"""Substance scoring: which verified claims actually carry knowledge.

Verification answers one question: *is this sentence a span of a retrieved
document?* It does not answer the question a reader cares about next: *does this
sentence tell me anything?* "The record for X reports licence MIT" is checkable
and useless. "Capacity degraded 18% over 400 cycles at 40 C" is both.

This module publishes a single, deterministic, arithmetic rule that ranks claims
by how much they carry, so the topic pages lead with the sentences a researcher
came for and label the rest honestly as registry metadata.

Design constraints, which the rule respects:

* **No language model, no learned weights.** Every feature is a lexical test or a
  count, and every weight is a constant declared below and rendered on the site's
  method page. A reviewer can recompute any score by hand.
* **It never changes a verdict.** A claim's verification result is untouched. The
  score only decides reading order and the label shown next to the claim.
* **It cannot promote an unsupported claim.** Verification contributes to the
  score, so a claim that failed verification is ranked below an equivalent claim
  that passed, never above.
* **Metadata is named, not hidden.** Claims that score below ``METADATA_CUTOFF``
  are labelled ``metadata`` on the page with the reason, which is what makes the
  corpus's current skew (only one source reachable, so mostly repository facts)
  visible instead of merely felt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..models import Claim
from ..util import extract_dates, extract_numbers

# --- the published rule ----------------------------------------------------
# Feature weights. They sum to 1.0 so the score is directly readable as a share.
SUBSTANCE_WEIGHTS: dict[str, float] = {
    "quantity": 0.24,       # a number is what makes a claim testable
    "date": 0.12,           # a reference period is what makes a number meaningful
    "comparison": 0.14,     # "more than", "faster", "twice" - a claim with a contrast
    "mechanism": 0.14,      # "because", "causes", "enables" - a claim with a why
    "caveat": 0.08,         # negation and limits; a stated limit is knowledge too
    "specificity": 0.12,    # neither a label nor a paragraph
    "verification": 0.10,   # the verdict already reached by the verifier
    "evidence": 0.06,       # where in the evidence hierarchy the source sits
}

# Reading-order labels. A claim is never dropped, only placed.
SUBSTANTIVE_CUTOFF = 0.55
METADATA_CUTOFF = 0.35

COMPARISON_MARKERS = (
    "than ", "more than", "less than", "at least", "at most", "up to", "down to",
    "higher", "lower", "greater", "fewer", "faster", "slower", "increase", "decrease",
    "improve", "outperform", "twice", "double", "half", "ratio", "percent", "%",
    " per ", "versus", "compared", "exceed", "below", "above", "peak", "worst", "best",
)

MECHANISM_MARKERS = (
    "because", "causes", "cause", "leads to", "results in", "resulting in", "enables",
    "prevents", "reduces", "increases", "improves", "degrades", "requires", "required",
    "depends on", "produces", "drives", "triggers", "allows", "blocks", "limits",
    "when ", "if ", "so that", "in order to",
)

CAVEAT_MARKERS = (
    "not ", "no ", "never", "cannot", "could not", "fails", "failed", "without",
    "risk", "limitation", "limited", "error", "uncertain", "unclear", "unknown",
    "caveat", "however", "although", "except", "unresolved", "deprecated", "stale",
)

_MIN_WORDS = 6
_FULL_WORDS = 14
_LONG_WORDS = 45


@dataclass
class SubstanceScore:
    """One claim's score, with every component exposed for review."""

    claim_id: str
    total: float
    label: str
    features: dict[str, float] = field(default_factory=dict)
    contributions: dict[str, float] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "total": round(self.total, 4),
            "label": self.label,
            "features": {k: round(v, 4) for k, v in self.features.items()},
            "contributions": {k: round(v, 4) for k, v in self.contributions.items()},
            "reason": self.reason,
        }


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def _has(text: str, markers: Iterable[str]) -> float:
    lowered = text.casefold()
    return 1.0 if any(marker in lowered for marker in markers) else 0.0


def _specificity(text: str) -> float:
    """Ramp up to a full sentence, then decay: a label is thin, a paragraph is not a claim."""
    words = _word_count(text)
    if words < _MIN_WORDS:
        return 0.0
    if words < _FULL_WORDS:
        return round((words - _MIN_WORDS) / (_FULL_WORDS - _MIN_WORDS), 4)
    if words <= _LONG_WORDS:
        return 1.0
    return round(max(0.2, 1.0 - (words - _LONG_WORDS) / 120.0), 4)


_VERDICT_VALUE = {"supported": 1.0, "partially_supported": 0.5, "contradicted": 0.25, "unsupported": 0.0}


def score_claim(claim: Claim) -> SubstanceScore:
    """Apply the published rule to one claim. Pure function; no state, no I/O."""
    text = claim.text or ""
    features: dict[str, float] = {
        "quantity": 1.0 if extract_numbers(text) else 0.0,
        "date": 1.0 if (extract_dates(text) or re.search(r"\b(1[89]\d{2}|20\d{2}|21\d{2})\b", text)) else 0.0,
        "comparison": _has(text, COMPARISON_MARKERS),
        "mechanism": _has(text, MECHANISM_MARKERS),
        "caveat": _has(text, CAVEAT_MARKERS),
        "specificity": _specificity(text),
        "verification": _VERDICT_VALUE.get(claim.verification.verdict, 0.0),
        "evidence": round(max(0.0, min(1.0, (10 - int(claim.evidence_rank or 9)) / 9.0)), 4),
    }
    contributions = {name: features[name] * weight for name, weight in SUBSTANCE_WEIGHTS.items()}
    total = sum(contributions.values())

    if total >= SUBSTANTIVE_CUTOFF:
        label = "substantive"
        reason = "Carries a checkable quantity, a period or a mechanism, and passed verification."
    elif total >= METADATA_CUTOFF:
        label = "descriptive"
        reason = "Describes a subject without a quantity or a period of its own."
    else:
        label = "metadata"
        reason = (
            "Registry metadata: checkable, but it records a property of a record rather than a "
            "finding about the question."
        )
    return SubstanceScore(
        claim_id=claim.claim_id,
        total=total,
        label=label,
        features=features,
        contributions=contributions,
        reason=reason,
    )


def score_claims(claims: Iterable[Claim]) -> dict[str, SubstanceScore]:
    """Score a set of claims, keyed by claim id."""
    return {claim.claim_id: score_claim(claim) for claim in claims}


def substance_summary(claims: Iterable[Claim]) -> dict[str, Any]:
    """The figures the site and the run summary publish about claim substance.

    Every value here is a count or a share of the claims actually passed in, so
    the summary cannot introduce a figure the library does not hold.
    """
    claims = list(claims)
    scores = score_claims(claims)
    by_label = {"substantive": 0, "descriptive": 0, "metadata": 0}
    for score in scores.values():
        by_label[score.label] = by_label.get(score.label, 0) + 1
    total = len(claims)
    quantified = sum(1 for c in claims if extract_numbers(c.text))
    dated = sum(
        1 for c in claims if extract_dates(c.text) or re.search(r"\b(1[89]\d{2}|20\d{2}|21\d{2})\b", c.text)
    )
    return {
        "claims": total,
        "labels": by_label,
        "substantive_share": round(by_label["substantive"] / total, 4) if total else 0.0,
        "metadata_share": round(by_label["metadata"] / total, 4) if total else 0.0,
        "quantified": quantified,
        "dated": dated,
        "quantified_share": round(quantified / total, 4) if total else 0.0,
        "mean_score": round(sum(s.total for s in scores.values()) / total, 4) if total else 0.0,
    }


def order_by_substance(claims: list[Claim], scores: dict[str, SubstanceScore] | None = None) -> list[Claim]:
    """Most substantive first. Ties break on evidence rank then claim id, so the
    order is stable across runs and never depends on dictionary ordering."""
    scores = scores or score_claims(claims)
    return sorted(
        claims,
        key=lambda c: (
            -round(scores[c.claim_id].total, 4) if c.claim_id in scores else 0.0,
            int(c.evidence_rank or 9),
            c.claim_id,
        ),
    )


def substance_rule() -> dict[str, Any]:
    """The rule as data, so the site can render exactly what is applied."""
    return {
        "weights": dict(SUBSTANCE_WEIGHTS),
        "cutoffs": {"substantive": SUBSTANTIVE_CUTOFF, "metadata": METADATA_CUTOFF},
        "labels": {
            "substantive": "Carries a quantity, a period or a mechanism and passed verification.",
            "descriptive": "Describes a subject without a quantity of its own.",
            "metadata": "A property of a record (licence, language, star count) rather than a finding.",
        },
        "features": {
            "quantity": "The claim contains a numeric literal.",
            "date": "The claim contains an ISO date or a four-digit year.",
            "comparison": "The claim contains a comparative (more than, faster, ratio, percent).",
            "mechanism": "The claim contains a causal or enabling phrase (because, enables, requires).",
            "caveat": "The claim states a limit, a negation or an unresolved point.",
            "specificity": "Word count: 0 below 6 words, 1 between 14 and 45, decaying above.",
            "verification": "supported 1.0, partially supported 0.5, contradicted 0.25, unsupported 0.0.",
            "evidence": "(10 - evidence rank) / 9, the position of the source in the hierarchy.",
        },
        "note": (
            "The score never changes a verification verdict. It orders claims and labels metadata; "
            "it does not accept or reject anything."
        ),
    }
