"""The Chief Research Scientist: what to work on next.

The manager does three things and nothing else:

1. **Prioritise.** Score every question with :func:`~selflearn.think.discovery.score_topic`
   and work the top of the list, with an explicit neglect term so a question that
   has been ignored longest rises even if it is not obviously exciting.
2. **Choose reading material.** Decide which registered sources to poll for each
   question, and say so, so that the choice is reviewable rather than implicit.
3. **Budget.** Keep the cycle inside hard limits: documents, requests, experiments.

It never chooses what is *true*. It only chooses what to look at.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ..config import BUDGET, Budget, EVIDENCE_RANK
from ..fetch.registry import REGISTRY
from ..models import Claim, Task, Topic
from ..util import content_tokens, stable_id, utcnow_iso
from .discovery import TopicScore, score_candidate_topics

# A general-purpose reading list used when a question does not name its own
# sources. Chosen to span independent evidence classes rather than to be large.
DEFAULT_SOURCE_IDS: tuple[str, ...] = (
    "crossref",
    "openalex",
    "arxiv",
    "github",
    "hackernews",
)

# Sources whose declared topics overlap a question's vocabulary are preferred, but
# never at the cost of polling a source that cannot contribute an evidence class
# the question needs.
MAX_SOURCES_PER_TOPIC = 6


@dataclass
class Plan:
    run_id: str
    selected: list[Topic] = field(default_factory=list)
    scores: list[TopicScore] = field(default_factory=list)
    sources_by_topic: dict[str, list[str]] = field(default_factory=dict)
    tasks: list[Task] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    budget: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "selected_topics": [t.topic_id for t in self.selected],
            "scores": [s.to_dict() for s in self.scores],
            "sources_by_topic": self.sources_by_topic,
            "tasks": [t.to_dict() for t in self.tasks],
            "notes": self.notes,
            "budget": self.budget,
        }


def source_affinity(topic: Topic, source_id: str) -> int:
    """How many of a source's declared topics overlap the question's vocabulary."""
    spec = REGISTRY.get(source_id)
    if spec is None:
        return 0
    question_terms = content_tokens(" ".join([topic.title, topic.question, " ".join(topic.keywords)]))
    source_terms = content_tokens(" ".join([spec.name, " ".join(spec.topics), spec.notes]))
    return len(question_terms & source_terms)


def choose_sources(topic: Topic, *, limit: int = MAX_SOURCES_PER_TOPIC) -> list[str]:
    """Pick the reading list for one question.

    An explicit list on the topic wins. Otherwise sources are ranked by vocabulary
    overlap with the question, with the general reading list always included so
    that a narrow question does not end up reading only one kind of source.
    """
    if topic.source_ids:
        return [sid for sid in topic.source_ids if sid in REGISTRY][:limit]
    scored = sorted(
        ((source_affinity(topic, sid), sid) for sid in REGISTRY),
        key=lambda item: (-item[0], item[1]),
    )
    chosen: list[str] = []
    for affinity, source_id in scored:
        if affinity > 0 and len(chosen) < limit - 1:
            chosen.append(source_id)
    for source_id in DEFAULT_SOURCE_IDS:
        if source_id not in chosen:
            chosen.append(source_id)
    return chosen[:limit]


def build_plan(
    topics: Iterable[Topic],
    claims_by_topic: dict[str, list[Claim]],
    evidence_index: dict[str, Any],
    *,
    run_id: str,
    budget: Budget = BUDGET,
    max_topics: int | None = None,
    now_iso: str | None = None,
    attention_by_topic: dict[str, float] | None = None,
) -> Plan:
    """Score the questions and produce the cycle plan."""
    now_iso = now_iso or utcnow_iso()
    topics = list(topics)
    max_topics = max_topics or budget.max_topics_per_cycle
    scores = score_candidate_topics(
        topics,
        claims_by_topic,
        evidence_index,
        now_iso=now_iso,
        attention_by_topic=attention_by_topic,
    )
    by_id = {topic.topic_id: topic for topic in topics}
    selected = [by_id[score.topic_id] for score in scores[:max_topics]]

    plan = Plan(
        run_id=run_id,
        selected=selected,
        scores=scores,
        budget=budget.as_dict(),
    )
    for topic in selected:
        sources = choose_sources(topic)
        plan.sources_by_topic[topic.topic_id] = sources
        plan.tasks.append(
            Task(
                task_id=stable_id("task", run_id, topic.topic_id, "research"),
                kind="research",
                topic_id=topic.topic_id,
                payload={"sources": sources},
                priority=1.0,
            )
        )
    for score in scores:
        if score.unmeasurable:
            plan.notes.append(
                f"{score.topic_id}: cannot measure {', '.join(score.unmeasurable)} for this question. "
                "Those components are excluded from the score rather than defaulted."
            )
    return plan


def topic_transition(topic: Topic, *, claims: list[Claim], strategies: int, experiments: int) -> str:
    """Compute the lifecycle stage implied by the evidence actually held.

    The stage is derived, never asserted: a question is only 'validated' when it
    has supported claims and a surviving candidate, and it never skips 'testing'
    because a test is missing.
    """
    supported = [c for c in claims if c.verification.verdict == "supported"]
    if not claims:
        return "researching"
    if experiments and supported and strategies:
        return "testing"
    if strategies and supported:
        return "competing"
    if supported:
        return "hypothesis"
    return "researching"


def evidence_rank_mix(claims: Iterable[Claim]) -> dict[str, int]:
    """Counts of claims per evidence class, for the run summary."""
    mix: dict[str, int] = {}
    for claim in claims:
        mix[claim.evidence_class] = mix.get(claim.evidence_class, 0) + 1
    return dict(sorted(mix.items(), key=lambda item: EVIDENCE_RANK.get(item[0], 9)))
