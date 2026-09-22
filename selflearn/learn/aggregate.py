"""Derived claims: statements the engine makes about its own library.

A derived claim is the only kind of sentence the engine composes itself. It is
always about the *library*, never about the world, and it always carries the
numeric context it was computed from. :func:`selflearn.verify.verifier.verify_derived`
then re-checks that every figure in the sentence appears in that context, and the
audit stage recomputes the context on the next cycle, so a stale figure is caught
rather than republished.

Examples of what belongs here: how many independent sources support a topic, what
share of claims passed verification, which evidence classes are represented.
Examples of what does not: anything about batteries, proteins or markets.
"""

from __future__ import annotations

from typing import Iterable

from ..models import Claim, EvidenceRecord, Topic
from ..util import utcnow_iso
from ..verify.grounding import derived_proposal

MIN_CLAIMS_FOR_AGGREGATE = 3


def derive_library_claims(
    topic: Topic,
    claims: list[Claim],
    records: list[EvidenceRecord],
) -> list[tuple]:
    """Return ``(proposal, context_numbers)`` pairs of derived library statistics.

    The statistics describe the *evidence*: only non-superseded ``direct`` claims
    are counted. Counting the library's own composed statements (``derived``,
    ``synthesis``) here would make the figures self-referential - each cycle's
    "supported by N claims" would grow by the statements that quote it - and
    counting retired claims would publish a figure that a later cycle has
    already withdrawn. Both call sites (the cycle writer and the page renderer)
    pass the topic's claims; filtering inside keeps their numbers identical.
    """
    proposals: list[tuple] = []
    claims = [c for c in claims if c.claim_kind == "direct" and not c.superseded]
    if len(claims) < MIN_CLAIMS_FOR_AGGREGATE:
        return proposals

    supported = [c for c in claims if c.verification.verdict == "supported"]
    partial = [c for c in claims if c.verification.verdict == "partially_supported"]
    sources = sorted({c.source_name for c in claims})
    classes = sorted({c.evidence_class for c in claims})
    with_numbers = [c for c in claims if c.verification.missing_numbers == [] and c.verification.quote_match]

    # 1. Volume and independence.
    text = (
        f"This question is currently supported by {len(claims)} verified claim(s) drawn from "
        f"{len(sources)} independent source(s)."
    )
    context = [len(claims), len(sources)]
    proposals.append(
        (
            derived_proposal(
                text,
                label="library_volume",
                context_numbers=[str(n) for n in context],
                limitations="A derived statement about this library, not about the subject matter.",
            ),
            context,
        )
    )

    # 2. Verification pass rate - the headline integrity number.
    if claims:
        rate = round(100.0 * len(supported) / len(claims), 1)
        text = (
            f"Of the claims recorded for this question, {rate}% passed full verification against their cited document; "
            f"{len(partial)} were only partially supported and are marked as such on this page."
        )
        # The context must contain the figure exactly as it is written in the
        # sentence, including the percent sign, or the derived check would reject
        # the engine's own arithmetic.
        context = [f"{rate}%", rate, len(partial), len(supported)]
        proposals.append(
            (
                derived_proposal(
                    text,
                    label="verification_rate",
                    context_numbers=[str(n) for n in context],
                    limitations="A derived statement about this library, not about the subject matter.",
                ),
                context,
            )
        )

    # 3. Evidence classes represented.
    text = f"The supporting documents span {len(classes)} evidence class(es) in the project hierarchy."
    context = [len(classes)]
    proposals.append(
        (
            derived_proposal(
                text,
                label="evidence_spread",
                context_numbers=[str(n) for n in context],
                limitations="A derived statement about this library, not about the subject matter.",
            ),
            context,
        )
    )

    # 4. Coverage of the current run: live versus replayed evidence.
    if records:
        live = sum(1 for r in records if r.is_live)
        fixtures = sum(1 for r in records if r.is_fixture)
        text = (
            f"Of the documents cited here, {live} were retrieved live from their source and "
            f"{fixtures} are synthetic test fixtures, which are labelled wherever they appear."
        )
        context = [live, fixtures]
        proposals.append(
            (
                derived_proposal(
                    text,
                    label="retrieval_mode",
                    context_numbers=[str(n) for n in context],
                    limitations="A derived statement about this library, not about the subject matter.",
                ),
                context,
            )
        )

    # 5. Quantified support: how much of the claim set carries a checkable figure.
    text = (
        f"{len(with_numbers)} claim(s) for this question carry a quantified statement that was found verbatim in the "
        "cited document, which is what makes an experiment possible."
    )
    context = [len(with_numbers)]
    proposals.append(
        (
            derived_proposal(
                text,
                label="quantified_support",
                context_numbers=[str(n) for n in context],
                limitations="A derived statement about this library, not about the subject matter.",
            ),
            context,
        )
    )

    return proposals


def aggregate_context_numbers(proposals: Iterable[tuple]) -> set[str]:
    """Every engine-computed figure referenced by the derived claims."""
    numbers: set[str] = set()
    for _proposal, context in proposals:
        numbers |= {str(n) for n in context}
    return numbers


def library_statistics(claims: list[Claim], records: list[EvidenceRecord]) -> dict:
    """Raw counters used by the site and by the derived claims above."""
    return {
        "claims": len(claims),
        "supported": sum(1 for c in claims if c.verification.verdict == "supported"),
        "partially_supported": sum(1 for c in claims if c.verification.verdict == "partially_supported"),
        "unsupported": sum(1 for c in claims if c.verification.verdict == "unsupported"),
        "sources": len({c.source_name for c in claims}),
        "evidence_classes": sorted({c.evidence_class for c in claims}),
        "documents": len(records),
        "live_documents": sum(1 for r in records if r.is_live),
        "fixture_documents": sum(1 for r in records if r.is_fixture),
        "computed_at": utcnow_iso(),
    }
