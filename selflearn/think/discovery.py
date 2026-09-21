"""Curiosity and topic discovery.

Two jobs, kept deliberately separate:

**Question discovery** - after a topic has been researched, derive the next
questions from what was actually retrieved: unresolved findings, missing
reference periods, transfers from other topics, and vocabulary the topic did not
previously contain. Each question records which claims it came from, so a reader
can see the thread from evidence to question.

**Topic scoring** - decide what deserves research next. Every component of the
score is computed from retrieved metadata and is reported separately. When a
component has no data (for example, no source returned a publication date), it is
reported as unmeasurable and is excluded from the total, rather than defaulted to
a number that would look like a measurement. This is the design document's
"recognise its own knowledge gaps" requirement applied to prioritisation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..models import Claim, EvidenceRecord, Question, Topic
from ..util import content_tokens, days_between, stable_id, truncate, utcnow_iso

UNCERTAINTY_MARKERS = (
    "however",
    "unclear",
    "uncertain",
    "may ",
    "might ",
    "could ",
    "appears",
    "suggests",
    "preliminary",
    "not yet",
    "remains",
    "unknown",
    "limited",
    "conflicting",
)

RECENCY_WINDOW_DAYS = 180.0
MOMENTUM_WINDOW_DAYS = 30.0


@dataclass
class TopicScore:
    topic_id: str
    total: float
    components: dict[str, float]
    unmeasurable: list[str]
    basis: list[str]
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "total": round(self.total, 4),
            "components": {k: round(v, 4) for k, v in self.components.items()},
            "unmeasurable": list(self.unmeasurable),
            "basis": list(self.basis),
            "details": self.details,
        }


# ---------------------------------------------------------------------------
# Question discovery
# ---------------------------------------------------------------------------


def discover_questions(
    topic: Topic,
    claims: list[Claim],
    evidence_index: dict[str, EvidenceRecord],
    *,
    max_questions: int = 8,
    cross_topic_claims: list[Claim] | None = None,
) -> list[Question]:
    """Derive follow-up questions from the verified claim set."""
    questions: list[Question] = []
    supported = [c for c in claims if c.verification.verdict == "supported"]

    # 1. Unresolved or hedged findings.
    for claim in supported:
        lowered = claim.text.casefold()
        if any(marker in lowered for marker in UNCERTAINTY_MARKERS):
            questions.append(
                Question(
                    id=stable_id("q", topic.topic_id, "uncertain", claim.claim_id),
                    topic_id=topic.topic_id,
                    text=(
                        f"The source {claim.source_name} reports an unresolved or hedged finding: "
                        f"\"{truncate(claim.quote or claim.text, 200)}\". "
                        "Which additional evidence would settle whether this holds for this question?"
                    ),
                    origin="sub_question",
                    priority=0.7,
                )
            )
            break

    # 2. Quantities with no reference period.
    for claim in supported:
        from ..util import extract_dates, extract_numbers

        if extract_numbers(claim.text) and not extract_dates(claim.text) and not re.search(r"\b(19|20)\d{2}\b", claim.text):
            questions.append(
                Question(
                    id=stable_id("q", topic.topic_id, "period", claim.claim_id),
                    topic_id=topic.topic_id,
                    text=(
                        f"The quantity reported in {claim.claim_id} has no reference period in the quoted text. "
                        "Over what period, and in what population, was it measured?"
                    ),
                    origin="gap",
                    priority=0.65,
                )
            )
            break

    # 3. Cross-topic transfers.
    for claim in (cross_topic_claims or [])[:2]:
        questions.append(
            Question(
                id=stable_id("q", topic.topic_id, "transfer", claim.claim_id),
                topic_id=topic.topic_id,
                text=(
                    f"A statement verified for a different topic - \"{truncate(claim.quote or claim.text, 180)}\" "
                    f"({claim.source_name}) - shares subject matter with this question. "
                    "Does it transfer, and what domain-specific constraint could block it?"
                ),
                origin="discovery",
                priority=0.6,
            )
        )

    # 4. Vocabulary the topic did not previously carry: candidate new topics.
    known = content_tokens(" ".join(topic.keywords) + " " + topic.title + " " + topic.question)
    emerging: dict[str, int] = {}
    for claim in supported:
        for token in content_tokens(claim.text):
            if token not in known and len(token) >= 5:
                emerging[token] = emerging.get(token, 0) + 1
    for token, count in sorted(emerging.items(), key=lambda kv: (-kv[1], kv[0]))[:2]:
        if count >= 2:
            questions.append(
                Question(
                    id=stable_id("q", topic.topic_id, "term", token),
                    topic_id=topic.topic_id,
                    text=(
                        f"The retrieved statements repeatedly introduce the term '{token}', which the topic brief does not "
                        "mention. Does it warrant a topic of its own, and what primary evidence would define it?"
                    ),
                    origin="discovery",
                    priority=0.55,
                )
            )

    # 5. No evidence at all: an explicit gap question beats a fabricated one.
    if not supported:
        questions.append(
            Question(
                id=stable_id("q", topic.topic_id, "no-evidence"),
                topic_id=topic.topic_id,
                text=(
                    "No retrieved statement for this question passed verification. Which registered source carries the "
                    "authoritative record for this subject, and what query would retrieve it?"
                ),
                origin="gap",
                priority=0.9,
            )
        )

    # Deduplicate by text, keep the highest priority, and cap.
    unique: dict[str, Question] = {}
    for question in questions:
        current = unique.get(question.text)
        if current is None or question.priority > current.priority:
            unique[question.text] = question
    ordered = sorted(unique.values(), key=lambda q: (-q.priority, q.id))
    return ordered[:max_questions]


# ---------------------------------------------------------------------------
# Topic scoring
# ---------------------------------------------------------------------------


def score_topic(
    topic: Topic,
    claims: list[Claim],
    evidence_index: dict[str, EvidenceRecord],
    *,
    now_iso: str | None = None,
    attention_signal: float | None = None,
) -> TopicScore:
    """Score a topic for research priority, publishing what could not be measured."""
    now_iso = now_iso or utcnow_iso()
    components: dict[str, float] = {}
    unmeasurable: list[str] = []
    basis: list[str] = []
    details: dict[str, Any] = {}

    records = [evidence_index[c.evidence_id] for c in claims if c.evidence_id in evidence_index]

    # -- evidence strength (measurable whenever there is evidence) --------
    if records:
        strength = sum((10 - r.evidence_rank) / 9.0 for r in records) / len(records)
        components["evidence_strength"] = round(strength, 4)
        basis.append(f"mean evidence rank over {len(records)} document(s)")
    else:
        components["evidence_strength"] = 0.0
        unmeasurable.append("evidence_strength")
        basis.append("no documents retrieved")

    # -- freshness (needs publication dates from the sources) -------------
    ages = [days_between(r.published_at, now_iso) for r in records if r.published_at]
    ages = [age for age in ages if age is not None and age >= 0]
    if ages:
        fresh = sum(1 for age in ages if age <= RECENCY_WINDOW_DAYS) / len(ages)
        components["freshness"] = round(fresh, 4)
        basis.append(f"{len(ages)} document(s) carried a publication date")
        details["newest_document_age_days"] = round(min(ages), 1)
    else:
        components["freshness"] = 0.0
        unmeasurable.append("freshness")
        basis.append("no publication dates were returned by any source")

    # -- unrest (open questions and unresolved findings) ------------------
    open_questions = sum(1 for c in claims if c.verification.verdict == "partially_supported")
    components["evidence_gaps"] = round(min(open_questions / max(len(claims), 1), 1.0), 4)
    basis.append(f"{open_questions} partially supported claim(s) out of {len(claims)}")

    # -- testability (does any claim carry a number we could test?) -------
    from ..util import extract_numbers

    quantified = sum(1 for c in claims if extract_numbers(c.text))
    components["testability"] = round(min(quantified / max(len(claims), 1), 1.0), 4)
    basis.append(f"{quantified} quantified claim(s)")

    # -- attention (only if a real attention signal was retrieved) --------
    if attention_signal is None:
        components["attention"] = 0.0
        unmeasurable.append("attention")
        basis.append("no attention signal (forum or repository activity) was retrieved for this topic")
    else:
        components["attention"] = round(max(0.0, min(attention_signal, 1.0)), 4)
        basis.append("attention measured from retrieved public activity counts")

    # -- staleness of the topic record ------------------------------------
    age_days = days_between(topic.last_updated, now_iso)
    if age_days is None:
        components["neglect"] = 1.0
        basis.append("topic has no usable last-updated timestamp")
    else:
        components["neglect"] = round(min(age_days / 30.0, 1.0), 4)
        basis.append(f"topic last updated {age_days:.1f} day(s) ago")

    weights = {
        "evidence_strength": 0.2,
        "freshness": 0.15,
        "evidence_gaps": 0.2,
        "testability": 0.15,
        "attention": 0.1,
        "neglect": 0.2,
    }
    measurable = {k: v for k, v in components.items() if k not in unmeasurable}
    measurable_weight = sum(weights[k] for k in measurable)
    total = sum(components[k] * weights[k] for k in measurable) / max(measurable_weight, 1e-9)

    return TopicScore(
        topic_id=topic.topic_id,
        total=total,
        components=components,
        unmeasurable=unmeasurable,
        basis=basis,
        details=details,
    )


def score_candidate_topics(
    topics: Iterable[Topic],
    claims_by_topic: dict[str, list[Claim]],
    evidence_index: dict[str, EvidenceRecord],
    *,
    now_iso: str | None = None,
    attention_by_topic: dict[str, float] | None = None,
) -> list[TopicScore]:
    attention_by_topic = attention_by_topic or {}
    scores = [
        score_topic(
            topic,
            claims_by_topic.get(topic.topic_id, []),
            evidence_index,
            now_iso=now_iso,
            attention_signal=attention_by_topic.get(topic.topic_id),
        )
        for topic in topics
    ]
    scores.sort(key=lambda s: (-s.total, s.topic_id))
    return scores


def attention_from_records(records: list[EvidenceRecord]) -> float | None:
    """Turn raw public activity counts into a bounded attention signal.

    Only sources whose declared purpose is attention measurement are consulted
    (forum and repository sources). Counting is done on retrieved numbers, and the
    mapping to ``[0, 1]`` is logarithmic because activity is heavy-tailed. If no
    such record exists, this returns ``None`` - never a default that would look
    like a measurement.
    """
    from ..fetch.registry import get_source

    values: list[float] = []
    for record in records:
        try:
            spec = get_source(record.source_id)
        except KeyError:
            continue
        if spec.evidence_class != "commentary" and record.source_id != "github":
            continue
        numbers = re.findall(r"(?:Points|Stars|Comments|Citation count): (\d+)", record.text)
        values.extend(float(n) for n in numbers)
    if not values:
        return None
    import math

    peak = max(values)
    return min(1.0, math.log10(peak + 1) / 4.0)
