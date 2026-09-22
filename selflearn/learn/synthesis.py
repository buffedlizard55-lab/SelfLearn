"""Cross-document synthesis, under the same rules as everything else.

A single-source claim can be true and still narrow. The most useful sentence a
research loop can produce is one that holds across several sources - and that is
also the most dangerous kind of sentence, because it is exactly where a system
that paraphrases would quietly invent an average, a trend or a consensus.

So synthesis here is arithmetic over quotations, and nothing else:

1. Only claims that already passed verification against their own document take
   part, and only ``direct`` claims (quotations), never the engine's own derived
   statistics.
2. A synthesis statement must cite at least two *documents*. If the two claims
   come from the same document it is not cross-document and no statement is made.
3. Every figure in a synthesis statement must already appear in one of the cited
   claims, or be a count of documents or sources that the engine computed and
   recorded alongside the statement (``context_numbers``). The engine never
   averages, interpolates, extrapolates or re-expresses a figure. A statement
   that would need arithmetic it did not record is not written.
4. Disagreement is published as disagreement. When two documents carry different
   values sharing a unit, the statement says so and names both, and the pair is
   flagged for review rather than reconciled.

:func:`selflearn.verify.verifier.verify_synthesis` re-checks (2) and (3) on every
audit, recomputing from the cited claims, so a synthesis statement cannot survive
the deletion or the change of a claim it depends on.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..models import Claim
from ..util import extract_numbers, stable_id

MIN_DOCUMENTS_FOR_SYNTHESIS = 2
MIN_SOURCES_FOR_SYNTHESIS = 2
# Minimum shared subject words between two claims before their figures may be
# compared. Without it, two unrelated records ("repo A has 37459 stars", "repo B
# has 27614 stars") are described as disagreeing about one value, which is true
# of nothing in particular and reads as a finding.
MIN_SHARED_SUBJECT_WORDS = 1

# Words that follow a number but are not units ("of the", "in 2024", "and").
_UNIT_STOPWORDS = {
    "of", "the", "a", "an", "in", "on", "at", "to", "and", "or", "for", "with", "by",
    "from", "as", "is", "was", "were", "be", "than", "that", "this", "it", "its",
    "has", "have", "had", "are", "not", "no", "per", "each", "over", "about",
}

_NUMBER_IN_TEXT = re.compile(r"(?<![\w.])(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)\s?(%|percent|pct)?", re.I)

# Dates and clock times are not quantities. A claim reading "pushed_at
# 2026-08-02T01:55:40Z, stargazers_count 37459" contains one measurement and
# five date fragments; read as numbers, the fragments pair with the next word in
# the sentence and produce a statement like "one reports 02 and the other reports
# 04" - which is false, because neither document reported 02 of anything. Dates
# are extracted separately, by the verifier, as dates.
_DATE_TIME_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?"
    r"|\d{4}-\d{2}(?!-\d)"
    r"|\b\d{1,2}:\d{2}(?::\d{2})?\b"
    r"|\b(?:1[6-9]|20|21)\d{2}\b"
)


@dataclass
class SynthesisProposal:
    """One candidate cross-document statement, with its full provenance."""

    text: str
    kind: str                      # agreement | range | divergence
    cited_claim_ids: list[str] = field(default_factory=list)
    context_numbers: list[str] = field(default_factory=list)
    source_figures: dict[str, str] = field(default_factory=dict)
    limitations: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "kind": self.kind,
            "cited_claim_ids": list(self.cited_claim_ids),
            "context_numbers": list(self.context_numbers),
            "source_figures": dict(self.source_figures),
            "limitations": self.limitations,
        }


# ---------------------------------------------------------------------------
# Figure and unit extraction (lexical, and deliberately narrow)
# ---------------------------------------------------------------------------


def _canonical(raw: str) -> str:
    """Normalise a numeric literal the same way the verifier does."""
    text = raw.replace(",", "")
    if text.endswith(".0"):
        text = text[:-2]
    return text


def figures_with_units(text: str) -> list[tuple[str, str]]:
    """Return ``(number, unit)`` pairs found in a sentence, in order.

    Dates and clock times are removed first, for the reason given at
    :data:`_DATE_TIME_RE`: a date fragment read as a quantity produces a
    statement that is false, not merely thin.

    The unit is the first content word after the number, singularised. When there
    is none ("42 of the samples"), the unit is the empty string and the figure can
    still be quoted - it just cannot be compared against another document's
    figures, because the engine has no basis for saying the two measure the same
    thing.
    """
    pairs: list[tuple[str, str]] = []
    text = _DATE_TIME_RE.sub(" ", text or "")
    for match in _NUMBER_IN_TEXT.finditer(text):
        raw = match.group(1)
        suffix = (match.group(2) or "").casefold()
        number = _canonical(raw) + ("%" if suffix in {"%", "percent", "pct"} else "")
        head = (text or "")[: match.start()]
        preceding = [w for w in re.split(r"[^A-Za-z_]+", head) if w]
        tail = text[match.end():]
        words = [w for w in re.split(r"[^A-Za-z]+", tail) if w]
        unit = ""
        # Adapters render fields as "label value", so the label precedes the
        # number. Taking the following word there would attach the *next* field's
        # label to this figure, which is how 37459 came to be described as a fork
        # count. A field name is recognised by the underscore the API gave it.
        if preceding and "_" in preceding[-1]:
            label = preceding[-1].casefold()
            unit = label[:-1] if label.endswith("s") and len(label) > 4 else label
            pairs.append((number, unit))
            continue
        for word in words[:3]:
            lowered = word.casefold()
            if lowered in _UNIT_STOPWORDS or len(lowered) < 3:
                continue
            unit = lowered[:-1] if lowered.endswith("s") and len(lowered) > 4 else lowered
            break
        pairs.append((number, unit))
    return pairs


def _eligible(claims: Iterable[Claim]) -> list[Claim]:
    """Claims allowed to take part: verified quotations from a real document."""
    return [
        claim
        for claim in claims
        if claim.claim_kind == "direct" and claim.verification.verdict == "supported"
    ]


def _subject(claim: Claim) -> set[str]:
    """Content words that identify what a claim is about.

    The adapters' own field rendering is excluded, because words like "record",
    "reports" and "stargazers" appear in every GitHub record and would make any
    two of them look like the same subject. A claim that is nothing but a
    rendered field list therefore has no subject at all, and its figures are not
    compared against anything - which is the honest outcome for registry
    metadata.
    """
    from ..util import content_tokens
    from ..verify.grounding import strip_rendered_labels

    words = content_tokens(strip_rendered_labels(claim.text or ""))
    return {w for w in words if len(w) >= 5 and w not in _UNIT_STOPWORDS}


def _shares_subject(a: Claim, b: Claim) -> bool:
    """Whether two claims are about the same thing, lexically.

    A conservative test: at least one shared content word of five or more
    characters. It is deliberately lexical and deliberately narrow - a missed
    comparison costs nothing, while a comparison between two unrelated records
    publishes a statement that means nothing.
    """
    return len(_subject(a) & _subject(b)) >= MIN_SHARED_SUBJECT_WORDS


# ---------------------------------------------------------------------------
# The three statement forms
# ---------------------------------------------------------------------------


def _agreement_statements(by_number: dict[str, list[Claim]]) -> list[SynthesisProposal]:
    """Figures that more than one document reports, quoted side by side."""
    proposals: list[SynthesisProposal] = []
    for number, claims in sorted(by_number.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        documents = {claim.evidence_id for claim in claims}
        if len(documents) < MIN_DOCUMENTS_FOR_SYNTHESIS:
            continue
        sources = sorted({claim.source_name for claim in claims})
        if len(sources) < MIN_SOURCES_FOR_SYNTHESIS:
            # One operator repeating a figure across its own records is not
            # cross-source agreement, and publishing it as such overstates the
            # independence of the evidence.
            continue
        text = (
            f"The figure {number} appears in verified statements from {len(documents)} separate documents "
            f"published by {len(sources)} source(s), each quoting its own source. "
            "This is agreement on a figure, not confirmation of a shared cause."
        )
        context = [number, str(len(documents)), str(len(sources))]
        proposals.append(
            SynthesisProposal(
                text=text,
                kind="agreement",
                cited_claim_ids=[claim.claim_id for claim in claims],
                context_numbers=context,
                source_figures={claim.claim_id: number for claim in claims},
                limitations=(
                    "Composed only of a figure that appears verbatim in each cited document and a count of "
                    "documents. The engine does not know whether the documents are independent of one another; "
                    "two outlets reporting the same press release count as two documents here."
                ),
            )
        )
        if len(proposals) >= 3:
            break
    return proposals


def _range_statements(claims: list[Claim]) -> list[SynthesisProposal]:
    """The spread of reported values that share a unit, across documents."""
    by_unit: dict[str, dict[str, list[Claim]]] = {}
    for claim in claims:
        for number, unit in figures_with_units(claim.text):
            if not unit:
                continue
            by_unit.setdefault(unit, {}).setdefault(number, []).append(claim)

    proposals: list[SynthesisProposal] = []
    for unit, numbers in sorted(by_unit.items()):
        if len(numbers) < 2:
            continue
        involved = [claim for group in numbers.values() for claim in group]
        documents = {claim.evidence_id for claim in involved}
        sources = {claim.source_name for claim in involved}
        if len(documents) < MIN_DOCUMENTS_FOR_SYNTHESIS or len(sources) < MIN_SOURCES_FOR_SYNTHESIS:
            continue

        def _value(number: str) -> float:
            return float(number.rstrip("%"))

        ordered = sorted(numbers, key=_value)
        low, high = ordered[0], ordered[-1]
        sources = sorted({claim.source_name for claim in involved})
        text = (
            f"Across {len(documents)} documents from {len(sources)} source(s), reported values expressed in "
            f"{unit} range from {low} to {high}. The documents are not measuring an agreed quantity: the unit is "
            "a word the engine matched, not a standardised measure."
        )
        context = [str(len(documents)), str(len(sources)), low, high]
        proposals.append(
            SynthesisProposal(
                text=text,
                kind="range",
                cited_claim_ids=sorted({claim.claim_id for claim in involved}),
                context_numbers=context,
                source_figures={claim.claim_id: ", ".join(sorted(numbers)) for claim in involved},
                limitations=(
                    "The unit is the word that followed the number in the source sentence. Two documents using "
                    "the same word for different measures would be combined here, which is why the values are "
                    "listed rather than averaged and why the claim is published as needing review."
                ),
            )
        )
        if len(proposals) >= 2:
            break
    return proposals


def _divergence_statements(claims: list[Claim]) -> list[SynthesisProposal]:
    """Two documents, one unit, different figures: published as a disagreement."""
    by_unit: dict[str, dict[str, list[Claim]]] = {}
    for claim in claims:
        for number, unit in figures_with_units(claim.text):
            if not unit:
                continue
            by_unit.setdefault(unit, {}).setdefault(number, []).append(claim)

    proposals: list[SynthesisProposal] = []
    for unit, numbers in sorted(by_unit.items()):
        cross: list[tuple[str, str, Claim, Claim]] = []
        ordered = sorted(numbers)
        for i, first in enumerate(ordered):
            for second in ordered[i + 1:]:
                pairs = [
                    (a, b)
                    for a in numbers[first]
                    for b in numbers[second]
                    if a.evidence_id != b.evidence_id      # a difference within one document is not a disagreement
                    and a.source_name != b.source_name     # nor is one operator contradicting itself
                    and _shares_subject(a, b)              # and nor is a comparison of two unrelated records
                ]
                if not pairs:
                    continue
                claim_a, claim_b = pairs[0]
                cross.append((first, second, claim_a, claim_b))
        if not cross:
            continue
        first, second, claim_a, claim_b = cross[0]
        text = (
            f"Two documents disagree about a value expressed in {unit}: one reports {first} and the other "
            f"reports {second}. Both statements are verified against their own source; the engine cannot decide "
            "which is correct and has published the pair for review, with both sources linked below."
        )
        context = [first, second]
        proposals.append(
            SynthesisProposal(
                text=text,
                kind="divergence",
                cited_claim_ids=[claim_a.claim_id, claim_b.claim_id],
                context_numbers=context,
                source_figures={claim_a.claim_id: first, claim_b.claim_id: second},
                limitations=(
                    "A published disagreement, not a finding. The two figures may describe different periods, "
                    "populations or definitions; the engine matched only the word that followed each number."
                ),
            )
        )
        if len(proposals) >= 2:
            break
    return proposals


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def synthesise(topic_id: str, claims: Iterable[Claim], *, limit: int = 6) -> list[SynthesisProposal]:
    """Build the cross-document statements a topic's verified claims support.

    Returns proposals only; the caller verifies each one with
    :func:`~selflearn.verify.verifier.verify_synthesis` before it is stored, and
    drops any proposal that does not survive.
    """
    eligible = _eligible(claims)
    if len(eligible) < MIN_DOCUMENTS_FOR_SYNTHESIS:
        return []
    if len({claim.evidence_id for claim in eligible}) < MIN_DOCUMENTS_FOR_SYNTHESIS:
        return []

    by_number: dict[str, list[Claim]] = {}
    for claim in eligible:
        for number, _unit in figures_with_units(claim.text):
            by_number.setdefault(number, [])
            if claim not in by_number[number]:
                by_number[number].append(claim)

    proposals = _agreement_statements(by_number)
    proposals += _range_statements(eligible)
    proposals += _divergence_statements(eligible)

    # Deterministic, de-duplicated by text, capped.
    unique: dict[str, SynthesisProposal] = {}
    for proposal in proposals:
        unique.setdefault(proposal.text, proposal)
    ordered = sorted(unique.values(), key=lambda p: ({"agreement": 0, "divergence": 1, "range": 2}[p.kind], p.text))
    return ordered[:limit]


def synthesis_evidence_id(topic_id: str) -> str:
    """Identifier of the computation record backing a topic's synthesis claims."""
    return f"synthesis-{topic_id}"


def synthesis_claim_id(topic_id: str, proposal: SynthesisProposal) -> str:
    return stable_id("cl", topic_id, "synthesis", proposal.text)
