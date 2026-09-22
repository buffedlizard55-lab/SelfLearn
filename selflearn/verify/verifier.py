"""The support checker.

A claim is only promoted to ``supported`` when **all** of the following hold:

1. Every numeric literal in the claim appears in the cited document.
2. Every date literal in the claim appears in the cited document.
3. Either the claim carries a verbatim quote present in the document, or the
   document contains at least ``THRESHOLDS.supported`` of the claim's content
   tokens.

Condition 1 is the important one. It is what stops the engine writing
"efficiency improves by 12%" about a source that never mentioned 12%. There is no
language model in this path: the check is a string and set operation, so it is
reproducible and its failure modes are inspectable.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable

from ..config import THRESHOLDS, VerificationThresholds
from ..models import Claim, Verification
from ..util import (
    content_tokens,
    coverage,
    jaccard,
    split_sentences,
    extract_dates,
    extract_numbers,
    missing_numbers,
    normalized_contains,
    similarity,
)

LOG = logging.getLogger("selflearn.verify")

VERDICT_ORDER = {
    "supported": 0,
    "partially_supported": 1,
    "unsupported": 2,
    "contradicted": 3,
}


NEGATION_MARKERS = (
    " no ",
    " not ",
    "n't ",
    "never ",
    "none ",
    "without ",
    "fails to",
    "failed to",
    "does not",
    "did not",
    "is not",
    "are not",
    "cannot",
    "no significant",
    "no evidence",
    "no effect",
)


def has_negation(text: str) -> bool:
    """True when the text contains an explicit negation marker."""
    padded = f" {text.casefold()} "
    return any(marker in padded for marker in NEGATION_MARKERS)


def best_supporting_span(document_text: str, claim_text: str) -> str:
    """The sentence of the document that overlaps the claim most.

    Used for polarity comparison: checking negation against a whole document is
    meaningless (long documents contain negations somewhere), so the comparison
    is narrowed to the passage that actually overlaps the claim.
    """
    sentences = split_sentences(document_text)
    if not sentences:
        return ""
    claim_tokens = content_tokens(claim_text)
    if not claim_tokens:
        return sentences[0]
    return max(sentences, key=lambda sentence: jaccard(claim_tokens, content_tokens(sentence)))


# Directional pairs. A claim that says the quantity rose while the passage it
# overlaps most says it fell is a classic evaluation failure; the pair list makes
# it visible. Matching is on stems so "degrade", "degradation" and "degraded" all
# count, and a pair only fires when the claim's own direction is absent from the
# passage.
DIRECTION_PAIRS: tuple[tuple[str, str], ...] = (
    ("increas", "decreas"),
    ("ris", "fell"),
    ("rose", "fell"),
    ("improv", "degrad"),
    ("improv", "worsen"),
    ("better", "worse"),
    ("higher", "lower"),
    ("bigger", "smaller"),
    ("faster", "slower"),
    ("more", "less"),
    ("gain", "loss"),
    ("expand", "contract"),
    ("accelerat", "decelerat"),
    ("enable", "prevent"),
    ("support", "undermin"),
    ("maximis", "minimis"),
    ("maximiz", "minimiz"),
)

# A claim stated as universal where the passage it overlaps is hedged is stronger
# than its evidence. It is not rejected - the passage may still be the right one -
# but it is capped and shown as needing review.
UNIVERSAL_MARKERS = (" all ", " every ", " always ", " never ", " none ", " no ", " any ")
HEDGE_MARKERS = (
    "about ",
    "approximately",
    "roughly",
    "around ",
    "may ",
    "might ",
    "could ",
    "some ",
    "often ",
    "usually ",
    "likely",
    "estimat",
    "suggest",
    "in temperate",
    "in some",
    "up to ",
)


def directional_conflict(claim_text: str, span: str) -> str:
    """Return a description when claim and passage point in opposite directions."""
    claim = claim_text.casefold()
    passage = span.casefold()
    for positive, negative in DIRECTION_PAIRS:
        for first, second in ((positive, negative), (negative, positive)):
            if first in claim and second in passage and first not in passage:
                return f"claim says '{first}' while the overlapping passage says '{second}'"
    return ""


def universality_gap(claim_text: str, span: str) -> str:
    """Return a description when a universal claim meets a hedged passage."""
    padded_claim = f" {claim_text.casefold()} "
    if not any(marker in padded_claim for marker in UNIVERSAL_MARKERS):
        return ""
    passage = span.casefold()
    for marker in HEDGE_MARKERS:
        if marker in passage:
            return f"claim is stated as universal while the overlapping passage hedges with '{marker.strip()}'"
    return ""


def verify_claim(
    claim_text: str,
    quote: str,
    document_text: str,
    *,
    thresholds: VerificationThresholds = THRESHOLDS,
) -> Verification:
    """Return the deterministic verdict for one claim against one document.

    Order of precedence matters and is deliberate:

    1. **Hard failures** - a number, date or year in the claim that the document
       does not contain, or a polarity mismatch against the closest matching
       passage. These can never be overridden by a good token score, because a
       well-worded claim with a fabricated figure is exactly the failure this
       project is built to prevent.
    2. **Quote match** - a verbatim span of a minimum length. Stronger than a
       token score, so it promotes straight to supported.
    3. **Token coverage** - the fallback, compared against the two thresholds.
    """
    reasons: list[str] = []

    if not claim_text.strip():
        return Verification(verdict="unsupported", quote_match=False, coverage=0.0, reasons=["Claim text is empty."])
    if not document_text.strip():
        return Verification(
            verdict="unsupported",
            quote_match=False,
            coverage=0.0,
            reasons=["Cited document has no text; nothing could be checked."],
        )

    quote_match = normalized_contains(document_text, quote, min_needle_chars=thresholds.quote_min_chars)
    if quote and not quote_match:
        reasons.append(
            f"Quoted span ({len(quote.strip())} characters) does not appear verbatim in the document. "
            "It is retained for review but cannot count as support."
        )

    # -- hard failure 1: invented quantities ------------------------------
    miss_numbers = sorted(missing_numbers(claim_text, document_text))
    document_numbers = extract_numbers(document_text)
    claim_dates = extract_dates(claim_text)
    document_dates = extract_dates(document_text)
    miss_dates = sorted(d for d in claim_dates if d not in document_dates)
    if miss_numbers:
        reasons.insert(
            0,
            "Hard failure: numeric literals absent from the document: " + ", ".join(miss_numbers) + ".",
        )
    if miss_dates:
        reasons.insert(0, "Hard failure: dates absent from the document: " + ", ".join(miss_dates) + ".")
    del document_numbers

    cover = coverage(claim_text, document_text)

    # -- hard failure 2: polarity, and the two strength caps --------------
    polarity_note = ""
    caps: list[str] = []
    if not quote_match:
        span = best_supporting_span(document_text, claim_text)
        if span:
            span_negated, claim_negated = has_negation(span), has_negation(claim_text)
            if span_negated != claim_negated and not miss_numbers and not miss_dates:
                polarity_note = (
                    "Polarity mismatch: the passage of the document that overlaps this claim most contains a negation "
                    "the claim does not reflect (or the reverse). Accepting the claim would invert the source."
                )
                reasons.insert(0, "Hard failure: " + polarity_note)
            # These two are caps rather than rejections: the wording differs in a way
            # the overlap test cannot resolve, so the claim is shown for review
            # instead of being published as supported.
            for note in (directional_conflict(claim_text, span), universality_gap(claim_text, span)):
                if note:
                    caps.append(note)

    if reasons and (miss_numbers or miss_dates or polarity_note):
        verdict = "unsupported"
    elif quote_match:
        verdict = "supported"
        reasons.insert(0, "Verbatim quoted span found in the document.")
    elif cover >= thresholds.supported:
        verdict = "supported"
        reasons.insert(
            0,
            f"Token coverage {cover:.0%} meets the support threshold of {thresholds.supported:.0%} and every numeric "
            "and temporal literal in the claim appears in the document.",
        )
    elif cover >= thresholds.partially_supported:
        verdict = "partially_supported"
        reasons.insert(
            0,
            f"Token coverage {cover:.0%} is below the support threshold of {thresholds.supported:.0%} but above the "
            "partial threshold; the claim is shown, marked as needing review.",
        )
    else:
        verdict = "unsupported"
        reasons.insert(0, f"Token coverage {cover:.0%} is too low to treat the document as support.")

    if caps:
        strength = {"supported": 2, "partially_supported": 1, "unsupported": 0, "contradicted": -1}
        if strength.get(verdict, 0) > 1:
            verdict = "partially_supported"
        for note in caps:
            reasons.insert(0, "Capped to partially supported: " + note + ".")

    return Verification(
        verdict=verdict,
        quote_match=quote_match,
        coverage=round(cover, 4),
        missing_numbers=miss_numbers,
        missing_dates=miss_dates,
        reasons=reasons,
    )


def confidence_label(
    verdict: str,
    evidence_rank: int,
    independent_sources: int,
) -> str:
    """Map verdict + evidence strength onto a published confidence label.

    Deliberately conservative: a single weak source can never yield ``high``, and
    an unsupported claim is labelled ``unknown`` rather than given a low score
    that might read as a weak finding.
    """
    if verdict == "unsupported" or verdict == "contradicted":
        return "unknown"
    if verdict == "partially_supported":
        if evidence_rank <= 4 and independent_sources >= 2:
            return "medium"
        return "low"
    # supported
    if evidence_rank <= 4 and independent_sources >= 2:
        return "high"
    if evidence_rank <= 5:
        return "medium"
    return "low"


def independent_source_count(claim: Claim, all_claims: Iterable[Claim]) -> int:
    """Number of distinct sources making substantially the same statement."""
    same = 0
    for other in all_claims:
        if other.claim_id == claim.claim_id:
            continue
        if other.topic_id != claim.topic_id:
            continue
        if other.source_name == claim.source_name:
            continue
        if similarity(claim.text, other.text) >= 0.6:
            same += 1
    return same


def verify_library(claims: Iterable[Claim]) -> dict[str, Any]:
    """Summary statistics for a set of verified claims."""
    claims = list(claims)
    counts: dict[str, int] = {}
    for claim in claims:
        counts[claim.verification.verdict] = counts.get(claim.verification.verdict, 0) + 1
    total = len(claims)
    supported = counts.get("supported", 0)
    return {
        "total": total,
        "by_verdict": dict(sorted(counts.items())),
        "supported_share": round(supported / total, 4) if total else 0.0,
        "independent_sources": len({c.source_name for c in claims}),
        "evidence_classes": sorted({c.evidence_class for c in claims}),
    }


def verify_derived(claim_text: str, context_numbers: list[str] | None = None) -> Verification:
    """Verify an engine-composed statement against engine-computed values.

    Used for the ``derived`` claim tier: statements about the library itself
    (counts, shares, spreads). Every numeric literal in the statement must appear
    in ``context_numbers``, where ``context_numbers`` is produced by the same
    deterministic computation that produced the statement. A derived statement
    therefore cannot introduce a figure that the engine did not compute, and the
    computation is re-run on every cycle so a stale figure is caught.
    """
    if not claim_text.strip():
        return Verification(verdict="unsupported", quote_match=False, coverage=0.0, reasons=["Derived statement is empty."])
    context = {str(n) for n in (context_numbers or [])}
    numbers = extract_numbers(claim_text)
    missing = sorted(n for n in numbers if n not in context)
    if missing:
        return Verification(
            verdict="unsupported",
            quote_match=False,
            coverage=0.0,
            missing_numbers=missing,
            reasons=[
                "Derived statement contains figures the engine did not compute: "
                + ", ".join(missing)
                + ". Recomputation disagrees with the recorded context."
            ],
        )
    return Verification(
        verdict="supported",
        quote_match=False,
        coverage=1.0,
        reasons=[f"All {len(numbers)} numeric literal(s) match the engine-computed context set."],
    )


def verify_synthesis(
    claim_text: str,
    cited_claims: list[Claim],
    context_numbers: list[str] | None = None,
) -> Verification:
    """Verify a cross-document statement against the claims it cites.

    Used for the ``synthesis`` claim tier. Three conditions, all of them
    recomputable from the library alone:

    1. at least two *documents* are cited, otherwise the statement is not
       cross-document and the claim is rejected;
    2. every numeric literal in the statement must appear either in one of the
       cited claims (text or quote) or in ``context_numbers``, which holds the
       document and source counts the engine computed while composing it;
    3. every date literal must likewise appear in a cited claim.

    Nothing here accepts an average, a sum or a difference: the arithmetic that
    would produce one is never performed, so a figure of that kind can only reach
    the statement by being quoted, and condition 2 then fails.
    """
    if not claim_text.strip():
        return Verification(
            verdict="unsupported", quote_match=False, coverage=0.0, reasons=["Synthesis statement is empty."]
        )
    if len(cited_claims) < 2:
        return Verification(
            verdict="unsupported",
            quote_match=False,
            coverage=0.0,
            reasons=["A synthesis statement must cite at least two claims; it cites " + str(len(cited_claims)) + "."],
        )
    documents = {claim.evidence_id for claim in cited_claims if claim.evidence_id}
    if len(documents) < 2:
        return Verification(
            verdict="unsupported",
            quote_match=False,
            coverage=0.0,
            reasons=[
                f"The {len(cited_claims)} cited claims come from {len(documents)} document(s). "
                "A cross-document statement requires at least two distinct documents."
            ],
        )

    allowed = {str(n) for n in (context_numbers or [])}
    cited_text = " \n ".join((claim.text or "") + " " + (claim.quote or "") for claim in cited_claims)
    allowed |= extract_numbers(cited_text)
    allowed_dates = extract_dates(cited_text)

    numbers = extract_numbers(claim_text)
    missing = sorted(n for n in numbers if n not in allowed)
    dates = extract_dates(claim_text)
    missing_dates = sorted(d for d in dates if d not in allowed_dates)
    if missing or missing_dates:
        return Verification(
            verdict="unsupported",
            quote_match=False,
            coverage=0.0,
            missing_numbers=missing,
            missing_dates=missing_dates,
            reasons=[
                "Synthesis statement contains figures that do not appear in the claims it cites: "
                + ", ".join(missing + missing_dates)
                + ". Cross-document statements may only combine figures already verified in a source."
            ],
        )
    return Verification(
        verdict="supported",
        quote_match=False,
        coverage=1.0,
        reasons=[
            f"All {len(numbers)} figure(s) and {len(dates)} date(s) appear in the "
            f"{len(cited_claims)} cited claim(s) drawn from {len(documents)} documents, or in the "
            "recorded document/source counts."
        ],
    )


def audit_narrative(text: str, allowed_numbers: Iterable[str]) -> list[str]:
    """Return numbers in a narrative that are not present in the allowed set.

    This is the guard applied to every published summary: a summary may only
    quote figures that already exist in the verified claim set.
    """
    allowed = {str(n) for n in allowed_numbers}
    return sorted(n for n in extract_numbers(text) if n not in allowed)
