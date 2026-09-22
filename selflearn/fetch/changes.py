"""Change-driven scanning: what is new since the last run.

The design document asks the system to *watch* the world, not only to answer
questions about it. A question-driven poll answers "what is true about X"; a
change scan answers "what changed in X since we last looked". They need different
request shapes, and only some sources offer them.

Every mechanism below is a filter documented by the operator of the source, with
the documentation URL recorded next to it and published on the site. Nothing here
guesses at an undocumented parameter, because an unsupported filter usually does
not fail loudly: it returns the unfiltered result set and the engine would report
old items as new.

The five mechanisms implemented, and where each is documented:

``crossref``        ``filter=from-index-date:<date>``
                    https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/
``arxiv``           ``sortBy=submittedDate`` / ``sortBy=lastUpdatedDate`` with ``sortOrder``
                    https://info.arxiv.org/help/api/user-manual.html
``github``          ``pushed:>=<date>`` search qualifier
                    https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories
``nvd``             ``lastModStartDate`` with ``lastModEndDate`` (both required, <= 120 days)
                    https://nvd.nist.gov/developers/vulnerabilities
``usgs_earthquake`` ``starttime`` / ``endtime`` (and ``updatedafter``)
                    https://earthquake.usgs.gov/fdsnws/event/1/

A source that offers no change filter is *not* scanned and is reported as
``no_change_filter`` with the reason, rather than being polled and its whole
result set being described as new.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from ..models import Failure, Irregularity
from ..util import load_json, save_json, stable_id, utcnow_iso
from .net import HttpClient, HttpError, NetworkUnavailable
from .registry import get_source
from .sources import ParsedItem, Request, build_source

MAX_ITEMS_PER_SCAN = 10
DEFAULT_WINDOW_DAYS = 7
MAX_WINDOW_DAYS = 119          # NVD rejects a last-modified range longer than 120 days
MAX_SEEN_IDENTIFIERS = 4000


@dataclass
class ChangeMechanism:
    """One source's documented way of asking 'what changed?'."""

    source_id: str
    label: str
    docs_url: str
    path: str
    #: ``date`` (a single day boundary) or ``range`` (an explicit start and end).
    kind: str = "date"
    note: str = ""


MECHANISMS: dict[str, ChangeMechanism] = {
    "crossref": ChangeMechanism(
        source_id="crossref",
        label="Works reindexed at or after the given date",
        docs_url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/",
        path="/works",
        kind="date",
        note="from-index-date covers changes from members, Crossref and external sources.",
    ),
    "arxiv": ChangeMechanism(
        source_id="arxiv",
        label="Results sorted by submission date, newest first",
        docs_url="https://info.arxiv.org/help/api/user-manual.html",
        path="/query",
        kind="date",
        note=(
            "arXiv documents sortBy=relevance|lastUpdatedDate|submittedDate with sortOrder=ascending|descending; "
            "the newest-first ordering is the change signal, and the client drops entries older than the window."
        ),
    ),
    "github": ChangeMechanism(
        source_id="github",
        label="Repositories pushed to on or after the given date",
        docs_url="https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories",
        path="/search/repositories",
        kind="date",
        note="pushed: is the documented qualifier for the date of the most recent commit on any branch.",
    ),
    "nvd": ChangeMechanism(
        source_id="nvd",
        label="CVE records last modified inside an explicit window",
        docs_url="https://nvd.nist.gov/developers/vulnerabilities",
        path="/cves/2.0",
        kind="range",
        note="lastModStartDate and lastModEndDate are both required and the range may not exceed 120 days.",
    ),
    "usgs_earthquake": ChangeMechanism(
        source_id="usgs_earthquake",
        label="Earthquake events inside an explicit time window",
        docs_url="https://earthquake.usgs.gov/fdsnws/event/1/",
        path="/query",
        kind="range",
        note="starttime and endtime are ISO-8601; updatedafter is available for revision tracking.",
    ),
}


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------


def _parse_iso(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        parsed = datetime.strptime(value.strip()[:10], "%Y-%m-%d")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def scan_window(previous_iso: str | None, *, now: datetime | None = None, max_days: int = DEFAULT_WINDOW_DAYS) -> tuple[str, str, int]:
    """Return ``(since, until, days)`` for this scan.

    The window starts where the last successful scan ended, so an item is not
    reported twice. The first scan has no recorded predecessor and uses
    ``max_days`` back from now, and it *says so* in the report: an unbounded
    first look would describe the whole result set as new.
    """
    now = now or datetime.now(timezone.utc)
    if previous_iso:
        since = _parse_iso(previous_iso)
        if since > now:
            since = now - timedelta(hours=1)
        elapsed = (now - since).total_seconds() / 86400.0
        days = max(1, min(MAX_WINDOW_DAYS, int(elapsed) + 1))
    else:
        days = max(1, min(MAX_WINDOW_DAYS, max_days))
    since = now - timedelta(days=days)
    return since.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"), days


def _iso_stamp(value: str) -> str:
    """NVD's documented form: ``yyyy-MM-ddTHH:mm:ss:SSS UTC-00:00``."""
    parsed = _parse_iso(value)
    return parsed.strftime("%Y-%m-%dT%H:%M:%S:000 UTC-00:00")


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


def change_request(source_id: str, query: str, *, since: str, until: str, limit: int = MAX_ITEMS_PER_SCAN) -> Request:
    """Build the documented change request for one source."""
    mechanism = MECHANISMS[source_id]
    spec = get_source(source_id)
    base = spec.base_url.rstrip("/")
    url = base + mechanism.path
    params: dict[str, Any] = {}
    if source_id == "crossref":
        params = {
            "filter": f"from-index-date:{since}",
            "query": query,
            "rows": limit,
            "select": "DOI,title,abstract,URL,issued,container-title,type,publisher,is-referenced-by-count",
            "mailto": "selflearn@example.invalid",
        }
    elif source_id == "arxiv":
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    elif source_id == "github":
        params = {
            "q": f"{query} pushed:>={since}",
            "per_page": limit,
            "sort": "updated",
            "order": "desc",
        }
    elif source_id == "nvd":
        params = {
            "keywordSearch": query,
            "lastModStartDate": _iso_stamp(since),
            "lastModEndDate": _iso_stamp(until),
            "resultsPerPage": limit,
        }
    elif source_id == "usgs_earthquake":
        params = {
            "format": "geojson",
            "starttime": since,
            "endtime": until,
            "orderby": "time",
            "limit": limit,
        }
    else:  # pragma: no cover - MECHANISMS is the only way in
        raise KeyError(f"no change mechanism registered for {source_id}")
    return Request(
        url=url,
        params=params,
        label=f"{source_id}:changes:{since}",
    )


def mechanism_table() -> list[dict[str, Any]]:
    """The mechanisms as data, for the site and the docs."""
    return [
        {
            "source_id": mechanism.source_id,
            "label": mechanism.label,
            "docs_url": mechanism.docs_url,
            "kind": mechanism.kind,
            "note": mechanism.note,
            "endpoint": get_source(mechanism.source_id).base_url.rstrip("/") + mechanism.path,
        }
        for mechanism in MECHANISMS.values()
    ]


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


@dataclass
class SourceScan:
    source_id: str
    source_name: str
    status: str                  # scanned | unreachable | error | skipped | not_attempted | no_change_filter
    window: dict[str, Any] = field(default_factory=dict)
    request_url: str = ""
    request_params: dict[str, Any] = field(default_factory=dict)
    mechanism: str = ""
    docs_url: str = ""
    items_seen: int = 0
    items_new: int = 0
    new_items: list[dict[str, Any]] = field(default_factory=list)
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "status": self.status,
            "window": self.window,
            "request_url": self.request_url,
            "request_params": self.request_params,
            "mechanism": self.mechanism,
            "docs_url": self.docs_url,
            "items_seen": self.items_seen,
            "items_new": self.items_new,
            "new_items": self.new_items,
            "detail": self.detail,
        }


@dataclass
class ScanOutcome:
    run_id: str
    generated_at: str
    window_days: int
    scans: list[SourceScan] = field(default_factory=list)
    irregularities: list[Irregularity] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)

    @property
    def items_new(self) -> int:
        return sum(scan.items_new for scan in self.scans)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "window_days": self.window_days,
            "sources_scanned": sum(1 for s in self.scans if s.status == "scanned"),
            "sources_attempted": len(self.scans),
            "items_seen": sum(s.items_seen for s in self.scans),
            "items_new": self.items_new,
            "by_status": _by_status(self.scans),
            "scans": [scan.to_dict() for scan in self.scans],
        }


def _by_status(scans: Iterable[SourceScan]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for scan in scans:
        counts[scan.status] = counts.get(scan.status, 0) + 1
    return dict(sorted(counts.items()))


def _irregularity(severity: str, summary: str, detail: str, *, action: str = "", url: str | None = None) -> Irregularity:
    return Irregularity(
        irregularity_id=stable_id("irr", "scan", summary, detail[:60]),
        severity=severity,
        stage="change_scan",
        topic_id=None,
        summary=summary,
        detail=detail,
        url=url,
        suggested_action=action,
    )


def _item_row(item: ParsedItem, source_id: str) -> dict[str, Any]:
    return {
        "identifier": item.identifier,
        "title": (item.title or "")[:200],
        "url": item.url,
        "published_at": item.published_at,
        "source_id": source_id,
        "excerpt": (item.text or "")[:280],
    }


class ChangeScanner:
    """Polls the sources that offer a documented change filter."""

    def __init__(self, client: HttpClient, state_path: Path, *, allow_network: bool = True) -> None:
        self.client = client
        self.state_path = Path(state_path)
        self.allow_network = allow_network
        payload = load_json(self.state_path, {}) or {}
        self.state: dict[str, Any] = payload if isinstance(payload, dict) else {}
        self.state.setdefault("sources", {})
        self.state.setdefault("seen", {})

    # -- state -----------------------------------------------------------
    def _last_scan(self, source_id: str) -> str | None:
        row = self.state["sources"].get(source_id) or {}
        value = row.get("last_scan")
        return value if isinstance(value, str) and value else None

    def _seen_ids(self, source_id: str) -> set[str]:
        return set(self.state["seen"].get(source_id) or [])

    def _remember(self, source_id: str, identifiers: list[str], when: str, status: str, items: int) -> None:
        known = self._seen_ids(source_id) | {i for i in identifiers if i}
        # Bounded so an unattended engine cannot grow this file without limit.
        if len(known) > MAX_SEEN_IDENTIFIERS:
            known = set(sorted(known)[-MAX_SEEN_IDENTIFIERS:])
        self.state["seen"][source_id] = sorted(known)
        previous = self.state["sources"].get(source_id) or {}
        self.state["sources"][source_id] = {
            "last_scan": when,
            "last_status": status,
            "last_items": items,
            "scans": int(previous.get("scans", 0)) + 1,
        }

    def save(self) -> None:
        save_json(self.state_path, self.state)

    # -- scan ------------------------------------------------------------
    def scan(
        self,
        query: str,
        *,
        source_ids: Iterable[str] | None = None,
        run_id: str = "scan",
        window_days: int = DEFAULT_WINDOW_DAYS,
        limit: int = MAX_ITEMS_PER_SCAN,
    ) -> ScanOutcome:
        outcome = ScanOutcome(run_id=run_id, generated_at=utcnow_iso(), window_days=window_days)
        now = utcnow_iso()
        targets = [s for s in (source_ids or sorted(MECHANISMS)) if s in MECHANISMS]

        for source_id in targets:
            spec = get_source(source_id)
            mechanism = MECHANISMS[source_id]
            since, until, days = scan_window(self._last_scan(source_id), max_days=window_days)
            scan = SourceScan(
                source_id=source_id,
                source_name=spec.name,
                status="not_attempted",
                window={"since": since, "until": until, "days": days, "first_scan": self._last_scan(source_id) is None},
                mechanism=mechanism.label,
                docs_url=mechanism.docs_url,
            )
            if not self.allow_network:
                scan.status = "not_attempted"
                scan.detail = "Network use was disabled for this run; the window above was not polled."
                outcome.scans.append(scan)
                continue

            adapter = build_source(source_id)
            missing = adapter.missing_credential()
            if missing:
                scan.status = "skipped"
                scan.detail = f"Credential {missing} is not set; the engine never calls a keyed API without one."
                outcome.scans.append(scan)
                outcome.irregularities.append(
                    _irregularity(
                        "info",
                        f"Change scan skipped for {source_id}: credential {missing} is not set",
                        "The source offers a documented change filter but requires a key.",
                        action=f"Set {missing} in the repository secrets to enable it.",
                        url=spec.key_url or spec.docs_url,
                    )
                )
                continue

            request = change_request(source_id, query, since=since, until=until, limit=limit)
            scan.request_url = request.url
            scan.request_params = dict(request.params)
            try:
                result = self.client.get(request.url, params=request.params, headers=request.headers)
            except NetworkUnavailable as exc:
                scan.status = "unreachable"
                scan.detail = str(exc)[:300]
                outcome.failures.append(
                    Failure(
                        failure_id=stable_id("fail", source_id, "scan", since),
                        topic_id=None,
                        stage="change_scan",
                        summary=f"{source_id} unreachable during the change scan",
                        detail=str(exc)[:500],
                        remedy="Confirm egress from the runner; the window will be re-polled on the next run.",
                    )
                )
                outcome.scans.append(scan)
                outcome.irregularities.append(
                    _irregularity(
                        "warning",
                        f"Change scan could not reach {source_id}",
                        f"{str(exc)[:280]}. The window {since}..{until} was not polled, so items published in it "
                        "will appear as new on a later run rather than being missed.",
                        action="Re-run the scan from a host with egress to this source.",
                    )
                )
                continue
            except HttpError as exc:
                scan.status = "error"
                scan.detail = f"HTTP {exc.status}: {exc.body[:200]}"
                outcome.failures.append(
                    Failure(
                        failure_id=stable_id("fail", source_id, "scan", str(exc.status)),
                        topic_id=None,
                        stage="change_scan",
                        summary=f"{source_id} returned HTTP {exc.status} during the change scan",
                        detail=exc.body[:500],
                        remedy="Check the documented filter name and value format; the operator may have changed it.",
                    )
                )
                outcome.scans.append(scan)
                outcome.irregularities.append(
                    _irregularity(
                        "warning",
                        f"Change scan for {source_id} returned HTTP {exc.status}",
                        f"Request: {request.url} with {json.dumps(request.params, sort_keys=True)[:240]}. "
                        f"Response: {exc.body[:200]}",
                        action="Verify the filter against the source's documentation and update changes.py.",
                        url=mechanism.docs_url,
                    )
                )
                continue

            try:
                items = adapter.parse(request, result)
            except (json.JSONDecodeError, ValueError, KeyError) as exc:
                scan.status = "error"
                scan.detail = f"Response could not be parsed: {type(exc).__name__}: {exc}"[:300]
                outcome.scans.append(scan)
                outcome.irregularities.append(
                    _irregularity(
                        "warning",
                        f"Change scan for {source_id} returned an unparseable response",
                        str(exc)[:280],
                        action="Extend the adapter's parser for this response shape.",
                    )
                )
                continue

            seen_before = self._seen_ids(source_id)
            fresh: list[dict[str, Any]] = []
            for item in items:
                identifier = f"{source_id}:{item.identifier}"
                if identifier in seen_before:
                    continue
                fresh.append(_item_row(item, source_id))
            scan.items_seen = len(items)
            scan.items_new = len(fresh)
            scan.new_items = fresh[:limit]
            scan.status = "scanned"
            scan.detail = (
                f"{len(items)} item(s) returned for the window {since}..{until}; "
                f"{len(fresh)} not seen by this engine before."
            )
            if scan.window.get("first_scan"):
                scan.detail += (
                    " First scan for this source: the window is the engine's default look-back, not a real "
                    "interval since a previous run, so 'new' here means 'not previously recorded'."
                )
            self._remember(
                source_id,
                [f"{source_id}:{item.identifier}" for item in items],
                now,
                "scanned",
                len(items),
            )
            outcome.scans.append(scan)

        self.save()
        return outcome


def summarise_scan(outcome: ScanOutcome) -> dict[str, Any]:
    """The figures a report or the run summary may quote about a scan."""
    return {
        "sources_attempted": len(outcome.scans),
        "sources_scanned": sum(1 for s in outcome.scans if s.status == "scanned"),
        "items_seen": sum(s.items_seen for s in outcome.scans),
        "items_new": outcome.items_new,
        "window_days": outcome.window_days,
        "by_status": _by_status(outcome.scans),
    }
