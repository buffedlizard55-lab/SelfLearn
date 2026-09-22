"""Turn retrieved documents into candidate claims - without inventing anything.

Two tiers exist, and the distinction is published on the site:

``direct``
    A span copied verbatim out of the retrieved document. The claim's text *is*
    the quotation, so its provenance cannot be argued about. Verification checks
    that the span really is present in the stored bytes and that any numbers in
    it are consistent with the document.

``derived``
    A statement the engine composes about its own library, for example a count of
    how many independent sources support a topic. These are verified against the
    engine's own computed values (:func:`selflearn.verify.verifier.verify_derived`),
    never against a source document, and are always labelled as derived.

No language model is involved in producing either tier. A sentence either exists
in the retrieved text or it does not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..models import EvidenceRecord
from ..util import content_tokens, extract_numbers, normalize_ws, similarity, split_sentences

MIN_CLAIM_CHARS = 40
MAX_CLAIM_CHARS = 420

# Lines the adapters emit as provenance scaffolding rather than content. They are
# recorded in the evidence record's own metadata, so repeating them as claims
# would add noise without adding evidence.
BOILERPLATE_PREFIXES = (
    "source:",
    "peer review status:",
    "record url:",
    "abstract:",
    "title:",
)


# Whole lines the attributed renderer emits purely so a reader can see where the
# text came from. They describe the engine, not the world, so they must never
# become claims. The header line is dropped even though it names the subject,
# because every content sentence repeats "The record for <subject> ...".
SCAFFOLD_LINE_PREFIXES = (
    "record:",
    "source:",
    "source note:",
    "every sentence below names the record it describes.",
    "values are copied from the response without change",
)


def strip_scaffolding(text: str) -> str:
    """Remove provenance scaffolding lines, keeping all content lines.

    Only whole lines whose *beginning* matches a known scaffolding phrase are
    removed, so a sentence that merely mentions a source keeps its place.
    """
    kept: list[str] = []
    for line in text.splitlines():
        lowered = line.strip().casefold()
        if any(lowered.startswith(prefix) for prefix in SCAFFOLD_LINE_PREFIXES):
            continue
        kept.append(line)
    return "\n".join(kept)


_LABEL_LINE_RE = re.compile(r"^the record for .+ reports:", re.I)


def strip_rendered_labels(text: str) -> str:
    """Remove the adapters' own rendering, keeping only the source's prose.

    A retrieved document mixes three things: provenance scaffolding, the
    adapters' rendering of response *fields* ("The record for X reports:
    language Python, stars 400", or a raw ``path = value`` dump), and prose the
    source itself wrote. The first two are the engine's vocabulary and are
    identical across every document from that source, so anything computed from
    them - a candidate topic, a shared subject between two claims - describes the
    adapter rather than the world.
    """
    kept: list[str] = []
    for line in strip_scaffolding(text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _LABEL_LINE_RE.match(stripped):
            continue
        if " = " in stripped:                     # the raw-response renderer's format
            continue
        if stripped.casefold().startswith(("the record for", "source note", "record:", "source:")):
            continue
        kept.append(stripped)
    return "\n".join(kept)


@dataclass
class ClaimProposal:
    text: str
    quote: str
    kind: str = "direct"          # direct | derived
    label: str = ""
    context_numbers: list[str] = field(default_factory=list)
    limitations: str = ""

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "quote": self.quote,
            "kind": self.kind,
            "label": self.label,
            "context_numbers": list(self.context_numbers),
            "limitations": self.limitations,
        }


def is_boilerplate(sentence: str) -> bool:
    lowered = sentence.casefold().strip()
    if not lowered:
        return True
    # A rendered "Label: value" line is scaffolding only when the label is one of
    # the provenance labels; "Magnitude: 6.4" is real content and is kept.
    for prefix in BOILERPLATE_PREFIXES:
        if lowered.startswith(prefix):
            # Keep genuine content lines such as "Abstract: <substantial text>".
            head, _, tail = sentence.partition(":")
            if len(tail.strip()) >= 120 and prefix in {"abstract:", "title:"}:
                return False
            return True
    return False


def informative_score(sentence: str) -> float:
    """Rank sentences for inclusion in the library.

    Rewards specificity (numbers, dates, units) and discourages very short or
    very long spans. The weights are heuristics; they only affect *ordering*, and
    every selected sentence is still verified against the document, so a bad
    weight can change what is shown first but cannot create a false claim.
    """
    tokens = content_tokens(sentence)
    numbers = extract_numbers(sentence)
    score = min(len(tokens), 40) / 40.0
    score += 0.35 if numbers else 0.0
    if re.search(r"\b(19|20)\d{2}\b", sentence):
        score += 0.15
    if len(sentence) > MAX_CLAIM_CHARS:
        score -= 0.2
    return score


def proposal_from_sentence(sentence: str, *, label: str = "") -> ClaimProposal | None:
    """Build a direct claim proposal from one sentence, or ``None`` if unusable."""
    text = normalize_ws(sentence)
    if len(text) < MIN_CLAIM_CHARS or len(text) > MAX_CLAIM_CHARS + 200:
        return None
    if is_boilerplate(text):
        return None
    if len(content_tokens(text)) < 4:
        return None
    # Quotes must be verbatim spans of the document, so the quote is the
    # sentence itself, trimmed to the published maximum length at a word break.
    quote = text[:MAX_CLAIM_CHARS].rstrip()
    return ClaimProposal(text=text, quote=quote, kind="direct", label=label)


def ground_evidence(record: EvidenceRecord, *, max_claims: int = 20) -> list[ClaimProposal]:
    """Select up to ``max_claims`` verifiable claims from one evidence record."""
    proposals: list[ClaimProposal] = []
    seen: list[str] = []

    for sentence in split_sentences(strip_scaffolding(record.text)):
        proposal = proposal_from_sentence(sentence)
        if proposal is None:
            continue
        # Drop near-duplicates inside the same document (APIs often repeat the
        # title in the abstract, for example).
        if any(similarity(proposal.text, previous) >= 0.85 for previous in seen):
            continue
        seen.append(proposal.text)
        proposals.append(proposal)

    proposals.sort(key=lambda p: informative_score(p.text), reverse=True)
    chosen = proposals[:max_claims]
    for proposal in chosen:
        if record.is_fixture:
            proposal.limitations = "Sourced from a synthetic test fixture; not real-world evidence."
        elif not record.is_live:
            proposal.limitations = (
                "Verified against a stored snapshot rather than a live retrieval; "
                f"content hash {record.content_hash[:23]}."
            )
    return chosen


def derived_proposal(
    text: str,
    *,
    label: str,
    context_numbers: list[str],
    limitations: str = "",
) -> ClaimProposal:
    """Build a derived claim whose numbers must match engine-computed values."""
    return ClaimProposal(
        text=normalize_ws(text),
        quote="",
        kind="derived",
        label=label,
        context_numbers=sorted(set(str(n) for n in context_numbers)),
        limitations=limitations,
    )
