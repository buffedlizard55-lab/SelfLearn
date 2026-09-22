"""Topic invention: proposing the next question from what was retrieved.

Section 12 of the design document asks for trending-topic discovery scored as
novelty x importance x research potential. The scoring machinery already existed
in :mod:`selflearn.think.discovery`; what was missing was a candidate pool and a
promotion rule.

**What the candidate pool actually is.** This module proposes topics from the
documents this engine has already retrieved - not from an open crawl of the web.
That is a deliberate narrowing and it is published wherever a proposed topic
appears: "novel" here means *novel to this library*, and a topic that is new to
the world but absent from the retrieved documents will not be proposed. The
alternative - inventing topics from the engine's own vocabulary - would produce
plausible-sounding subjects with no evidence behind them, which is the one
failure mode this project is built to avoid.

The rule, all of it arithmetic over stored records:

* **Novelty** - the share of the candidate phrase's content words that do not
  already appear in the library's vocabulary (existing topics plus every stored
  claim). A phrase made only of words the library already uses scores 0.
* **Importance** - the mean evidence strength of the documents carrying the
  phrase, scaled by how many distinct documents carry it and by how recent they
  are. Attention counts are *not* used here: they are commentary-class signals.
* **Potential** - the share of the phrase's supporting claims that carry a
  number (a quantity can be tested) plus the share that the verifier could only
  partially support (a gap can be researched).

A candidate is promoted only when it clears all three gates: enough documents,
enough novelty, and a total above the published threshold. Everything below the
line is still reported, with its components, so a reviewer can see what the
engine looked at and rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..models import Claim, EvidenceRecord, Topic
from ..util import content_tokens, days_between, slugify, stable_id, utcnow_iso
from ..verify.grounding import strip_rendered_labels

MIN_DOCUMENTS_FOR_CANDIDATE = 2
MIN_PHRASE_LENGTH = 2
MAX_PHRASE_LENGTH = 3
MIN_TOKEN_CHARS = 5

# Promotion gates. All three must hold; each is published on the site.
MIN_NOVELTY = 0.5
MIN_TOTAL = 0.45
MAX_PROPOSALS_PER_CYCLE = 3

# Words that recur in every retrieval and would otherwise dominate the candidate
# pool. Kept explicit so the list itself can be reviewed.
STOP_PHRASE_TOKENS = {
    "source", "record", "report", "reports", "values", "value", "field", "fields",
    "response", "request", "document", "documents", "abstract", "description",
    "published", "publisher", "retrieved", "license", "copyright", "reserved",
    "rights", "title", "results", "result", "search", "query", "data", "dataset",
    "page", "pages", "content", "metadata", "identifier", "updated", "created",
    "selflearn", "library", "engine", "claim", "claims", "evidence", "snapshot",
    # Field labels the adapters render. These are the engine's vocabulary, not a
    # subject; a phrase made only of them describes a column, not a topic.
    "language", "stars", "forks", "watchers", "issues", "license", "owner",
    "homepage", "archived", "visibility", "default", "branch", "topics",
    "releases", "download", "downloads", "version", "repository", "repositories",
    "project", "projects", "package", "packages", "author", "authors",
}


@dataclass
class CandidatePhrase:
    phrase: str
    documents: list[str] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)


@dataclass
class TopicProposal:
    phrase: str
    title: str
    novelty: float
    importance: float
    potential: float
    total: float
    components: dict[str, float] = field(default_factory=dict)
    support_documents: int = 0
    support_claim_ids: list[str] = field(default_factory=list)
    novel_tokens: list[str] = field(default_factory=list)
    accepted: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "phrase": self.phrase,
            "title": self.title,
            "novelty": round(self.novelty, 4),
            "importance": round(self.importance, 4),
            "potential": round(self.potential, 4),
            "total": round(self.total, 4),
            "components": {k: round(v, 4) for k, v in self.components.items()},
            "support_documents": self.support_documents,
            "support_claim_ids": list(self.support_claim_ids),
            "novel_tokens": list(self.novel_tokens),
            "accepted": self.accepted,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# Vocabulary and candidates
# ---------------------------------------------------------------------------


def library_vocabulary(claims: Iterable[Claim], topics: Iterable[Topic] = ()) -> set[str]:
    """Every content word the library already uses.

    A proposed topic has to be new *relative to this set*, which is what stops
    the engine proposing a renaming of something it already studies.
    """
    known: set[str] = set()
    for claim in claims:
        known |= content_tokens(claim.text or "")
        known |= content_tokens(claim.quote or "")
    for topic in topics:
        known |= content_tokens(topic.title or "")
        known |= content_tokens(topic.question or "")
        for keyword in topic.keywords or []:
            known |= content_tokens(keyword)
    return known


def _usable(token: str) -> bool:
    return len(token) >= MIN_TOKEN_CHARS and token not in STOP_PHRASE_TOKENS and not token.isdigit()


def prose_lines(text: str) -> list[str]:
    """The lines that are the source's own prose, not the engine's rendering.

    Delegates to :func:`selflearn.verify.grounding.strip_rendered_labels`, which is
    the same filter the rest of the engine uses to tell a source's words from the
    adapters' field rendering. Short lines are dropped as well: a phrase needs
    context to be a candidate for anything.
    """
    return [line for line in strip_rendered_labels(text or "").splitlines() if len(line.strip()) >= 24]


def candidate_phrases(records: Iterable[EvidenceRecord]) -> list[CandidatePhrase]:
    """Phrases that recur across at least two retrieved documents.

    Taken from the source's own prose (:func:`prose_lines`) plus the document
    title, so that a candidate is something a source actually said rather than a
    column name the adapter invented. Multi-word phrases are kept when they recur,
    because a two- or three-word phrase carries a subject; single words are not
    used, since a single word recurs for reasons that have nothing to do with a
    topic.
    """
    per_phrase: dict[str, CandidatePhrase] = {}
    for record in records:
        # The engine's own records (experiment results, library computations) are
        # not the world. Proposing a topic from them would make the engine study
        # its own vocabulary, so they are excluded from the candidate pool.
        if record.is_fixture or str(record.source_id).startswith("selflearn"):
            continue
        prose = " ".join(prose_lines(record.text or ""))[:4000]
        haystack = " ".join([record.title or "", prose]).casefold()
        words = re.findall(r"[a-z][a-z0-9'\-]{2,}", haystack)
        seen_here: set[str] = set()
        for span in (2, 3):
            for index in range(len(words) - span + 1):
                window = [w for w in words[index : index + span]]
                if not all(_usable(w) for w in window):
                    continue
                phrase = " ".join(window)
                if phrase in seen_here:
                    continue
                seen_here.add(phrase)
                entry = per_phrase.setdefault(phrase, CandidatePhrase(phrase=phrase, tokens=window))
                if record.evidence_id not in entry.documents:
                    entry.documents.append(record.evidence_id)
    return [
        candidate
        for candidate in per_phrase.values()
        if len(candidate.documents) >= MIN_DOCUMENTS_FOR_CANDIDATE
        and MIN_PHRASE_LENGTH <= len(candidate.tokens) <= MAX_PHRASE_LENGTH
    ]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

RECENCY_WINDOW_DAYS = 365.0


def score_proposal(
    candidate: CandidatePhrase,
    *,
    known: set[str],
    records: dict[str, EvidenceRecord],
    claims: list[Claim],
    now_iso: str | None = None,
) -> TopicProposal:
    """Apply the novelty x importance x potential rule to one candidate."""
    now_iso = now_iso or utcnow_iso()
    tokens = [token for token in candidate.tokens if _usable(token)]
    novel = [token for token in tokens if token not in known]
    novelty = (len(novel) / len(tokens)) if tokens else 0.0

    supporting_records = [records[eid] for eid in candidate.documents if eid in records]
    if supporting_records:
        strength = sum((10 - record.evidence_rank) / 9.0 for record in supporting_records) / len(
            supporting_records
        )
    else:
        strength = 0.0
    spread = min(1.0, len(supporting_records) / 5.0)
    ages = [days_between(record.published_at, now_iso) for record in supporting_records if record.published_at]
    ages = [age for age in ages if age is not None and age >= 0]
    recency = (sum(1 for age in ages if age <= RECENCY_WINDOW_DAYS) / len(ages)) if ages else 0.5
    importance = round(min(1.0, strength * (0.5 + 0.5 * spread) * (0.6 + 0.4 * recency)), 4)

    supporting_claims = [claim for claim in claims if claim.evidence_id in set(candidate.documents)]
    if supporting_claims:
        from ..util import extract_numbers

        quantified = sum(1 for claim in supporting_claims if extract_numbers(claim.text)) / len(supporting_claims)
        open_share = sum(
            1 for claim in supporting_claims if claim.verification.verdict == "partially_supported"
        ) / len(supporting_claims)
        potential = round(min(1.0, 0.6 * quantified + 0.4 * open_share + (0.2 if supporting_claims else 0.0)), 4)
    else:
        potential = 0.2   # a phrase with documents but no claims yet is researchable but untested

    total = round(novelty * importance * potential * 2.0, 4)   # scaled to [0, 1]; the cap is the gate below
    total = min(1.0, total)

    proposal = TopicProposal(
        phrase=candidate.phrase,
        title=candidate.phrase.replace("-", " ").strip().capitalize(),
        novelty=novelty,
        importance=importance,
        potential=potential,
        total=total,
        components={
            "novelty": novelty,
            "evidence_strength": round(strength, 4),
            "document_spread": round(spread, 4),
            "recency": round(recency, 4),
            "quantified_share": 0.0,
            "open_share": 0.0,
        },
        support_documents=len(candidate.documents),
        support_claim_ids=[claim.claim_id for claim in supporting_claims[:10]],
        novel_tokens=novel,
    )
    if supporting_claims:
        from ..util import extract_numbers

        proposal.components["quantified_share"] = round(
            sum(1 for c in supporting_claims if extract_numbers(c.text)) / len(supporting_claims), 4
        )
        proposal.components["open_share"] = round(
            sum(1 for c in supporting_claims if c.verification.verdict == "partially_supported")
            / len(supporting_claims),
            4,
        )

    if len(candidate.documents) < MIN_DOCUMENTS_FOR_CANDIDATE:
        proposal.reason = f"Fewer than {MIN_DOCUMENTS_FOR_CANDIDATE} documents carry this phrase."
    elif not novel:
        proposal.reason = "Every content word in this phrase is already in the library's vocabulary."
    elif novelty < MIN_NOVELTY:
        proposal.reason = f"Novelty {novelty:.2f} is below the {MIN_NOVELTY} gate: mostly known vocabulary."
    elif total < MIN_TOTAL:
        proposal.reason = f"Total {total:.2f} is below the {MIN_TOTAL} promotion threshold."
    else:
        proposal.accepted = True
        proposal.reason = (
            f"Novelty {novelty:.2f}, importance {importance:.2f}, potential {potential:.2f}; carried by "
            f"{len(candidate.documents)} documents."
        )
    return proposal


def propose_topics(
    *,
    records: Iterable[EvidenceRecord],
    claims: Iterable[Claim],
    topics: Iterable[Topic],
    existing_titles: Iterable[str] = (),
    limit: int = MAX_PROPOSALS_PER_CYCLE,
    now_iso: str | None = None,
) -> list[TopicProposal]:
    """Score every candidate and return them best first, accepted ones first.

    Nothing is created here. The caller decides whether to add an accepted
    proposal to the library, so the promotion rule is testable on its own.
    """
    records_list = list(records)
    claims_list = list(claims)
    record_index = {record.evidence_id: record for record in records_list}
    known = library_vocabulary(claims_list, list(topics))
    taken = {title.casefold() for title in existing_titles}

    proposals: list[TopicProposal] = []
    for candidate in candidate_phrases(records_list):
        if candidate.phrase in taken:
            continue
        proposal = score_proposal(
            candidate,
            known=known,
            records=record_index,
            claims=claims_list,
            now_iso=now_iso,
        )
        proposals.append(proposal)
        taken.add(candidate.phrase)

    proposals.sort(key=lambda p: (not p.accepted, -p.total, p.phrase))
    return proposals[: max(limit, sum(1 for p in proposals if p.accepted))]


def to_topic(proposal: TopicProposal, *, parent_topic_id: str | None = None) -> Topic:
    """Materialise an accepted proposal as a topic record with full provenance."""
    question = (
        f"What is known about {proposal.phrase}? Which primary sources report it, what quantities do they give, "
        "and what would falsify the strongest statement among them?"
    )
    return Topic(
        topic_id=stable_id("topic", "discovery", proposal.phrase),
        title=proposal.title,
        slug=slugify(proposal.title),
        question=question,
        status="new",
        origin="discovery",
        keywords=list(dict.fromkeys(proposal.phrase.split())) + list(proposal.novel_tokens),
        signal={
            "proposal": proposal.to_dict(),
            "provenance": (
                "Proposed by selflearn.think.invention from retrieved documents. 'Novel' means novel to this "
                "library, not new to the world: the candidate pool is what this engine has retrieved, not an "
                "open crawl of the web."
            ),
        },
        parent_topic_id=parent_topic_id,
        notes=(
            f"Accepted at novelty {proposal.novelty:.2f}, importance {proposal.importance:.2f}, potential "
            f"{proposal.potential:.2f}, from {proposal.support_documents} documents."
        ),
        last_updated=utcnow_iso(),
    )


def invention_rule() -> dict[str, Any]:
    """The rule as data, for the site's method page."""
    return {
        "formula": "total = novelty x importance x potential, scaled by 2 and capped at 1",
        "gates": {
            "min_documents": MIN_DOCUMENTS_FOR_CANDIDATE,
            "min_novelty": MIN_NOVELTY,
            "min_total": MIN_TOTAL,
            "max_promotions_per_cycle": MAX_PROPOSALS_PER_CYCLE,
        },
        "novelty": "Share of the phrase's content words absent from the library vocabulary (topics + claims).",
        "importance": "Mean evidence strength of the carrying documents, scaled by document spread and recency.",
        "potential": "0.6 x share of supporting claims carrying a number + 0.4 x share only partially supported.",
        "candidate_pool": (
            "Phrases of two to four content words that recur in at least two retrieved documents. The pool is "
            "the engine's own retrieval, not an open crawl; 'novel' therefore means novel to this library."
        ),
    }
