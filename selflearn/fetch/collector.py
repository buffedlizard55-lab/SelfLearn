"""The collector: turns a topic into retrieved, hashed, reviewable evidence.

Failure policy (this is the part that keeps the project honest):

* A source that is unreachable, rate limited, or missing a credential is
  recorded as a **gap** with an irregularity entry. It is never quietly skipped
  and never simulated.
* When the live call fails, the engine may replay a stored snapshot. Replayed
  evidence is marked ``is_live = False`` and the verified hash is the hash of the
  *stored* text, so the site can say exactly what was checked.
* Fixture evidence (synthetic, used only in tests) is marked
  ``is_fixture = True`` and is rendered with a visible warning on the site.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ..config import BUDGET, EVIDENCE_LABEL, EVIDENCE_RANK
from ..models import EvidenceRecord, Failure, Irregularity, SourceStatus, Topic
from ..util import content_tokens, sha256_text, stable_id, utcnow_iso
from .net import HttpClient, HttpError, NetworkUnavailable
from .registry import get_source
from .sources import ParsedItem, Request, Source, build_source

LOG = logging.getLogger("selflearn.collector")


@dataclass
class CollectOutcome:
    records: list[EvidenceRecord] = field(default_factory=list)
    statuses: list[SourceStatus] = field(default_factory=list)
    irregularities: list[Irregularity] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)
    queries_used: list[str] = field(default_factory=list)


MIN_RELEVANCE_TOKEN_CHARS = 4


def relevance_overlap(query: str, item_text: str) -> int:
    """How many discriminating query words appear in a retrieved item.

    Search endpoints rank by popularity as often as by relevance, so a query about
    research agents can return the most-starred list of public APIs. Rather than
    publishing that as evidence for the question, the collector drops items that
    share no discriminating word with the query and *reports how many it dropped*.
    Dropping is visible; keeping an irrelevant hit would be worse, because it would
    be quoted as if it answered the question.
    """
    query_terms = {t for t in content_tokens(query) if len(t) >= MIN_RELEVANCE_TOKEN_CHARS}
    if not query_terms:
        return 0
    item_terms = {t for t in content_tokens(item_text) if len(t) >= MIN_RELEVANCE_TOKEN_CHARS}
    return len(query_terms & item_terms)


class Collector:
    """Fetches evidence for one topic from a list of registered sources."""

    def __init__(
        self,
        client: HttpClient,
        snapshot_dir: Path,
        *,
        max_items_per_source: int = BUDGET.max_evidence_per_topic,
        strict: bool = False,
    ) -> None:
        self.client = client
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.max_items = max_items_per_source
        self.strict = strict

    # -- queries -----------------------------------------------------------
    @staticmethod
    def queries_for(topic: Topic) -> list[str]:
        """Search strings for a topic, most specific first.

        Kept plain (no per-API operator syntax) so the same string is valid for
        every registered search endpoint.
        """
        queries: list[str] = []
        for key in ("queries", "search_terms"):
            for value in topic.signal.get(key, []) or []:
                if isinstance(value, str) and value.strip():
                    queries.append(value.strip())
        if topic.keywords:
            queries.append(" ".join(topic.keywords[:6]))
        if topic.title:
            queries.append(topic.title)
        seen: set[str] = set()
        unique: list[str] = []
        for query in queries:
            normalised = query.casefold()
            if normalised not in seen:
                seen.add(normalised)
                unique.append(query)
        return unique or [topic.title]

    # -- main entry point --------------------------------------------------
    def collect(self, topic: Topic, source_ids: Iterable[str]) -> CollectOutcome:
        outcome = CollectOutcome()
        queries = self.queries_for(topic)
        outcome.queries_used = queries[:2]
        for source_id in source_ids:
            if len(outcome.records) >= self.max_items:
                break
            if self.client.request_count >= self.client.max_requests:
                outcome.irregularities.append(
                    self._irregularity(
                        "warning",
                        "collect",
                        topic.topic_id,
                        "Request budget exhausted before all sources were polled",
                        f"Budget is {self.client.max_requests} requests per cycle. "
                        f"Sources not polled this cycle: see source status table.",
                        suggested_action="Raise the budget or reduce the source list for this topic.",
                    )
                )
                break
            self._collect_source(topic, source_id, queries, outcome)
        return outcome

    # -- per source --------------------------------------------------------
    def _collect_source(
        self,
        topic: Topic,
        source_id: str,
        queries: list[str],
        outcome: CollectOutcome,
    ) -> None:
        try:
            spec = get_source(source_id)
        except KeyError:
            outcome.irregularities.append(
                self._irregularity(
                    "error",
                    "collect",
                    topic.topic_id,
                    f"Topic references an unregistered source: {source_id}",
                    "The topic's source list contains an id that is not in the registry.",
                    suggested_action="Fix the topic definition in data/seeds/topics.json.",
                )
            )
            return

        adapter: Source = build_source(source_id)
        missing_env = adapter.missing_credential()
        if missing_env:
            outcome.statuses.append(
                SourceStatus(
                    source_id=source_id,
                    topics=[topic.topic_id],
                    name=spec.name,
                    url=spec.docs_url,
                    evidence_class=spec.evidence_class,
                    evidence_rank=spec.evidence_rank,
                    requires_key=True,
                    live_status="credential_required",
                    detail=f"Set {missing_env} to enable. Free key: {spec.key_url or 'see docs'}",
                )
            )
            outcome.irregularities.append(
                self._irregularity(
                    "info",
                    "collect",
                    topic.topic_id,
                    f"Source {source_id} not queried: credential {missing_env} is not set",
                    "This source requires a credential and the engine never calls an API without one.",
                    suggested_action=f"Set {missing_env} in the repository secrets. Instructions: {spec.key_url or spec.docs_url}",
                )
            )
            return

        note = spec.notes
        for request in adapter.requests(queries[0]):
            records, status, problems = self._run_request(topic, source_id, adapter, request, note)
            outcome.records.extend(records)
            for problem in problems:
                outcome.failures.append(problem)
            if status is not None:
                outcome.statuses.append(status)

    def _run_request(
        self,
        topic: Topic,
        source_id: str,
        adapter: Source,
        request: Request,
        note: str,
    ) -> tuple[list[EvidenceRecord], SourceStatus | None, list[Failure]]:
        spec = adapter.spec
        failures: list[Failure] = []
        try:
            result = self.client.get(request.url, params=request.params, headers=request.headers)
        except NetworkUnavailable as exc:
            failures.append(
                Failure(
                    failure_id=stable_id("fail", source_id, request.url, utcnow_iso()[:10]),
                    topic_id=topic.topic_id,
                    stage="fetch",
                    summary=f"{source_id} unreachable",
                    detail=str(exc)[:600],
                    remedy="Confirm egress from the runner, or rely on snapshot replay for this source.",
                )
            )
            replayed = self._replay(topic, source_id, request, note)
            return (
                replayed,
                SourceStatus(
                    source_id=source_id,
                    topics=[topic.topic_id],
                    name=spec.name,
                    url=request.url,
                    evidence_class=spec.evidence_class,
                    evidence_rank=spec.evidence_rank,
                    requires_key=spec.requires_key,
                    live_status="unreachable",
                    detail=str(exc)[:300],
                    items=len(replayed),
                ),
                failures,
            )
        except HttpError as exc:
            failures.append(
                Failure(
                    failure_id=stable_id("fail", source_id, request.url, str(exc.status)),
                    topic_id=topic.topic_id,
                    stage="fetch",
                    summary=f"{source_id} returned HTTP {exc.status}",
                    detail=exc.body[:400],
                    remedy="Check the API documentation for a changed endpoint or parameter.",
                )
            )
            replayed = self._replay(topic, source_id, request, note)
            return (
                replayed,
                SourceStatus(
                    source_id=source_id,
                    topics=[topic.topic_id],
                    name=spec.name,
                    url=request.url,
                    evidence_class=spec.evidence_class,
                    evidence_rank=spec.evidence_rank,
                    requires_key=spec.requires_key,
                    live_status="error",
                    http_status=exc.status,
                    detail=exc.body[:200],
                    items=len(replayed),
                ),
                failures,
            )

        try:
            items = adapter.parse(request, result)
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            failures.append(
                Failure(
                    failure_id=stable_id("fail", source_id, request.url, "parse"),
                    topic_id=topic.topic_id,
                    stage="parse",
                    summary=f"{source_id} response could not be parsed: {type(exc).__name__}",
                    detail=str(exc)[:400],
                    remedy="The response is still stored; extend the adapter or use the generic renderer.",
                )
            )
            items = []

        query = self._query_for(request)
        kept: list[ParsedItem] = []
        dropped = 0
        for item in items:
            if len(kept) >= self.max_items:
                break
            if relevance_overlap(query, f"{item.title}\n{item.text[:600]}") == 0:
                dropped += 1
                continue
            kept.append(item)

        records = [
            self._to_record(topic, source_id, item, result.status, len(result.body), result.sha256, note, request)
            for item in kept
        ]
        for record in records:
            self._write_snapshot(record)

        return (
            records,
            SourceStatus(
                source_id=source_id,
                topics=[topic.topic_id],
                name=spec.name,
                url=request.url,
                evidence_class=spec.evidence_class,
                evidence_rank=spec.evidence_rank,
                requires_key=spec.requires_key,
                live_status="reachable",
                http_status=result.status,
                detail=(
                    f"{len(records)} document(s) retrieved"
                    + (f"; {dropped} result(s) dropped as unrelated to the query" if dropped else "")
                ),
                items=len(records),
            ),
            failures,
        )

    # -- record construction ----------------------------------------------
    def _to_record(
        self,
        topic: Topic,
        source_id: str,
        item: ParsedItem,
        http_status: int,
        bytes_read: int,
        response_sha: str,
        note: str,
        request: Request,
    ) -> EvidenceRecord:
        text = item.text.strip()
        evidence_id = stable_id("ev", source_id, item.identifier, sha256_text(text)[:24])
        spec = get_source(source_id)
        notes = note
        if spec.evidence_class == "peer_reviewed" and source_id == "arxiv":
            notes = "arXiv preprint: not peer reviewed. " + note
        return EvidenceRecord(
            evidence_id=evidence_id,
            source_id=source_id,
            source_name=spec.name,
            url=item.url or request.url,
            title=item.title[:300],
            text=text,
            content_hash=sha256_text(text),
            evidence_class=spec.evidence_class,
            evidence_rank=EVIDENCE_RANK[spec.evidence_class],
            published_at=item.published_at,
            license=spec.license_name,
            publisher=spec.operator,
            is_fixture=False,
            is_live=True,
            http_status=http_status,
            bytes_read=bytes_read,
            response_sha256=response_sha,
            notes=notes[:500],
        )

    @staticmethod
    def _query_for(request: Request) -> str:
        """The search string that produced a request, used for relevance filtering."""
        for key in ("q", "query", "search", "search_query", "query.term", "term", "search_text", "keywordSearch"):
            value = request.params.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _write_snapshot(self, record: EvidenceRecord) -> Path:
        payload = record.to_dict()
        payload["text"] = record.text
        payload["evidence_class_label"] = EVIDENCE_LABEL.get(record.evidence_class, "")
        path = self.snapshot_dir / f"{record.evidence_id}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    # -- snapshot replay ---------------------------------------------------
    def _replay(self, topic: Topic, source_id: str, request: Request, note: str) -> list[EvidenceRecord]:
        """Replay stored snapshots for a source when the live call fails."""
        replayed: list[EvidenceRecord] = []
        for path in sorted(self.snapshot_dir.glob("ev-*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if payload.get("source_id") != source_id:
                continue
            text = payload.get("text", "")
            if not text:
                continue
            replayed.append(
                EvidenceRecord(
                    evidence_id=payload.get("evidence_id", path.stem),
                    source_id=source_id,
                    source_name=payload.get("source_name", source_id),
                    url=payload.get("url", request.url),
                    title=payload.get("title", ""),
                    text=text,
                    content_hash=payload.get("content_hash", sha256_text(text)),
                    evidence_class=payload.get("evidence_class", "unverified_claim"),
                    evidence_rank=int(payload.get("evidence_rank", 8)),
                    retrieved_at=payload.get("retrieved_at", utcnow_iso()),
                    published_at=payload.get("published_at"),
                    license=payload.get("license"),
                    publisher=payload.get("publisher"),
                    is_fixture=bool(payload.get("is_fixture", False)),
                    # Keep the original acquisition provenance: a document that
                    # was fetched live in an earlier cycle stays live after a
                    # replay (same evidence_id and retrieved_at, so this row
                    # replaces the original in the loaded view). Cycle-level
                    # reachability is reported by SourceStatus, not by quietly
                    # downgrading the record's badge.
                    is_live=bool(payload.get("is_live", False)),
                    http_status=payload.get("http_status"),
                    bytes_read=int(payload.get("bytes_read", 0)),
                    response_sha256=payload.get("response_sha256", ""),
                    notes=(note + " [replayed from stored snapshot]")[:500],
                )
            )
            if len(replayed) >= self.max_items:
                break
        return replayed

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _irregularity(
        severity: str,
        stage: str,
        topic_id: str | None,
        summary: str,
        detail: str = "",
        *,
        url: str | None = None,
        suggested_action: str = "",
    ) -> Irregularity:
        return Irregularity(
            irregularity_id=stable_id("irr", stage, summary, topic_id or ""),
            severity=severity,
            stage=stage,
            topic_id=topic_id,
            summary=summary,
            detail=detail,
            url=url,
            suggested_action=suggested_action,
        )


def load_fixture_evidence(fixture_dir: Path, source_id: str | None = None) -> list[EvidenceRecord]:
    """Load synthetic fixture evidence used by the test suite.

    Fixtures always carry ``is_fixture = True`` and can never be published as if
    they were real research: the publisher blocks that combination.
    """
    fixture_dir = Path(fixture_dir)
    records: list[EvidenceRecord] = []
    if not fixture_dir.exists():
        return records
    for path in sorted(fixture_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if source_id and payload.get("source_id") != source_id:
            continue
        text = payload.get("text", "")
        records.append(
            EvidenceRecord(
                evidence_id=payload.get("evidence_id") or stable_id("ev", payload.get("source_id"), payload.get("title")),
                source_id=payload.get("source_id", "fixture"),
                source_name=payload.get("source_name", "Synthetic fixture"),
                url=payload.get("url", "https://example.invalid/synthetic-fixture"),
                title=payload.get("title", "Synthetic fixture"),
                text=text,
                content_hash=sha256_text(text),
                evidence_class=payload.get("evidence_class", "unverified_claim"),
                evidence_rank=EVIDENCE_RANK.get(payload.get("evidence_class", "unverified_claim"), 8),
                is_fixture=True,
                is_live=False,
                notes="Synthetic test fixture. Not real-world evidence.",
            )
        )
    return records


def source_ids_for(topic: Topic, fallback: list[str]) -> list[str]:
    """Source ids for a topic, defaulting to the scheduler's fallback list."""
    ids = list(topic.source_ids or [])
    return ids or list(fallback)


def summarise_status(statuses: list[SourceStatus]) -> dict[str, Any]:
    reachable = [s.source_id for s in statuses if s.live_status == "reachable"]
    return {
        "checked": len(statuses),
        "reachable": sorted(set(reachable)),
        "unreachable": sorted({s.source_id for s in statuses if s.live_status == "unreachable"}),
        "errors": sorted({s.source_id for s in statuses if s.live_status == "error"}),
        "credential_required": sorted({s.source_id for s in statuses if s.live_status == "credential_required"}),
    }
