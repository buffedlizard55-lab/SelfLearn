"""An access-policy gate: RFC 9309 (Robots Exclusion Protocol), honoured literally.

Why this module exists
----------------------
The register's own admission rule says the engine does not scrape sites that forbid
it. Until now that rule was a sentence in a document, not a check: nothing in the
pipeline read the operator's ``robots.txt`` before requesting a path. Reading it
line by line for this session found a source that is documented by its operator as
an API *and* disallowed to every crawler by the same operator's robots.txt:

    https://pypi.org/robots.txt (fetched 2026-09-22)
        Disallow: /pypi/*/json
        Disallow: /search*

while https://docs.pypi.org/api/json/ documents ``GET /pypi/<project>/json`` and
https://docs.pypi.org/api/ says "For periodically checking for new packages or
updates to existing packages, use our RSS feeds" - a path robots.txt does not
disallow. The engine therefore uses the feeds and refuses the JSON route, and
publishes both facts instead of picking one silently.

What is implemented, and from where
-----------------------------------
Every rule below cites the clause of RFC 9309 that requires it
(https://www.rfc-editor.org/rfc/rfc9309.txt, published September 2022, Standards
Track):

* ``2.2.1`` group selection: a group's product token matches when it "is a
  substring of the User-Agent HTTP header", case-insensitively; several matching
  groups are merged; otherwise the ``*`` group applies; if neither exists, "no
  rules apply".
* ``2.2.2`` path matching: "The matching MUST start with the first octet of the
  path. The most specific match found MUST be used. The most specific match is the
  match that has the most octets." and "If an 'allow' rule and a 'disallow' rule
  are equivalent, then the 'allow' rule SHOULD be used." No match, or a group with
  no rules, means the URI is allowed. Rules outside any group are ignored.
* ``2.2.3`` special characters: ``#`` (comment), ``$`` (end of pattern), ``*``
  (zero or more of any character).
* ``2.3.1.3`` a 4xx response for robots.txt means "unavailable" and the crawler
  "MAY access any resources on the server".
* ``2.3.1.4`` a robots.txt that is unreachable through server or network errors
  "means the robots.txt file is undefined and the crawler MUST assume complete
  disallow", with permission to keep using a cached copy.
* ``2.4`` caching: a cached copy "SHOULD NOT" be used for more than 24 hours
  unless the file is unreachable.
* ``2.5`` the parsing limit "MUST be at least 500 kibibytes".

Deliberate, published departures from a strict reading
------------------------------------------------------
1. **Matching is against the path only**, not the query string. RFC 9309 2.2.2
   speaks of "the path"; its Figure 4 lists ``/foo/bar?baz=quz`` in a column headed
   "Path to Match", which is ambiguous, and the engine records which reading it
   used rather than choosing silently.
2. **An unreachable robots.txt disallows, and the refusal is published as its own
   status** (``robots_unreachable``) rather than being folded into "the source is
   down". A host this machine cannot reach at all produces that status for every
   source, which is the honest description of a sandbox with no egress.
3. **A response that is not ``text/plain`` is recorded as an irregularity** and
   then parsed anyway (2.3.1.1 requires following the parseable rules; a body with
   no ``user-agent:`` lines has no groups, and 2.2.1 then says no rules apply).
   ``https://registry.npmjs.org/robots.txt`` is exactly this case: it answers HTTP
   200 with the *package document* of an npm package named ``robots.txt``
   (``content-type: application/json``, observed 2026-09-22).

Nothing here decides what is true. It decides what the engine is allowed to ask
for, and it publishes every decision with the verbatim rule behind it.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from ..util import sha256_text, utcnow_iso

#: The standard this module implements. Published on the site next to every decision.
SPEC_URL = "https://www.rfc-editor.org/rfc/rfc9309.html"
SPEC_TEXT_URL = "https://www.rfc-editor.org/rfc/rfc9309.txt"

#: RFC 9309 2.4: a cached copy SHOULD NOT be used for more than 24 hours unless
#: the file is unreachable.
CACHE_MAX_AGE_HOURS = 24

#: RFC 9309 2.5: the parsing limit MUST be at least 500 KiB.
PARSE_LIMIT_BYTES = 512 * 1024

#: How much of a fetched robots.txt is kept in the cache for a reviewer to read.
STORED_TEXT_LIMIT = 64 * 1024

DEFAULT_TIMEOUT = 10


class RobotsDisallowed(RuntimeError):
    """Raised instead of performing a request the operator's robots.txt refuses."""

    def __init__(self, decision: "RobotsDecision") -> None:
        super().__init__(decision.detail or f"{decision.status} for {decision.url}")
        self.decision = decision


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RobotsRule:
    """One ``allow``/``disallow`` line, kept with the text it came from."""

    kind: str                    # "allow" | "disallow"
    pattern: str                 # the value after the colon, comment removed
    line: str                    # the verbatim line, for publication
    specificity: int             # octets in the pattern (RFC 9309 2.2.2)
    matcher: "re.Pattern[str]" = field(compare=False, repr=False, default=None)  # type: ignore[assignment]

    def matches(self, path: str) -> bool:
        return bool(self.matcher and self.matcher.match(path))


def compile_pattern(pattern: str) -> "re.Pattern[str]":
    """Turn a robots.txt path pattern into a prefix matcher (RFC 9309 2.2.3).

    ``*`` means "0 or more instances of any character" and ``$`` anchors the end
    of the pattern. Everything else is literal, including ``?``: the protocol
    defines only the three special characters in 2.2.3, so a ``?`` in a rule is
    matched as itself and never as "any single character".
    """
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    out: list[str] = []
    for char in body:
        if char == "*":
            out.append(".*")
        else:
            out.append(re.escape(char))
    # 2.2.2: "The match evaluates positively if and only if the end of the path
    # from the rule is reached before a difference in octets is encountered" -
    # a prefix match, unless the rule was anchored with "$".
    return re.compile("^" + "".join(out) + ("$" if anchored else ""))


@dataclass
class RobotsGroup:
    agents: list[str] = field(default_factory=list)
    rules: list[RobotsRule] = field(default_factory=list)

    def matches_agent(self, user_agent: str) -> bool:
        """RFC 9309 2.2.1: the product token is a substring of the User-Agent."""
        haystack = (user_agent or "").casefold()
        return any(token.casefold() in haystack for token in self.agents if token and token != "*")

    def is_wildcard(self) -> bool:
        return any(token.strip() == "*" for token in self.agents)


@dataclass
class RobotsFile:
    """A parsed robots.txt, with the provenance a reviewer needs."""

    text: str
    groups: list[RobotsGroup] = field(default_factory=list)
    sitemaps: list[str] = field(default_factory=list)
    unattached_rules: list[str] = field(default_factory=list)
    content_type: str = ""
    source_url: str = ""
    fetched_at: str = ""
    http_status: int | None = None
    truncated: bool = False

    @property
    def sha256(self) -> str:
        return sha256_text(self.text)

    @property
    def rule_count(self) -> int:
        return sum(len(group.rules) for group in self.groups)

    @classmethod
    def parse(cls, text: str, *, content_type: str = "", source_url: str = "", fetched_at: str = "", http_status: int | None = None) -> "RobotsFile":
        truncated = len(text.encode("utf-8", errors="replace")) > PARSE_LIMIT_BYTES
        if truncated:
            text = text[:PARSE_LIMIT_BYTES]
        parsed = cls(
            text=text,
            content_type=content_type,
            source_url=source_url,
            fetched_at=fetched_at,
            http_status=http_status,
            truncated=truncated,
        )
        current: RobotsGroup | None = None
        for raw in text.splitlines():
            # 2.2: a "#" designates a line comment, anywhere in the line.
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().casefold()
            value = value.strip()
            if key == "user-agent":
                if current is not None and current.rules:
                    # 2.2 ABNF: a user-agent line after rules starts a new group.
                    parsed.groups.append(current)
                    current = RobotsGroup()
                if current is None:
                    current = RobotsGroup()
                if value:
                    current.agents.append(value)
                continue
            if key == "sitemap":
                # 2.2.4: other records MUST NOT terminate a group.
                if value:
                    parsed.sitemaps.append(value)
                continue
            if key not in {"allow", "disallow"}:
                continue
            rule = RobotsRule(
                kind=key,
                pattern=value,
                line=raw.strip(),
                specificity=len(value.encode("utf-8", errors="replace")),
                matcher=compile_pattern(value),
            )
            if current is None:
                # 2.2.2: "The crawler SHOULD ignore 'disallow' and 'allow' rules
                # that are not in any group." Ignored, but published.
                parsed.unattached_rules.append(raw.strip())
                continue
            current.rules.append(rule)
        if current is not None:
            parsed.groups.append(current)
        return parsed

    def rules_for(self, user_agent: str) -> list[RobotsRule]:
        """The merged rule set that applies to this crawler (RFC 9309 2.2.1)."""
        matching = [group for group in self.groups if group.matches_agent(user_agent)]
        if not matching:
            matching = [group for group in self.groups if group.is_wildcard()]
        rules: list[RobotsRule] = []
        for group in matching:
            rules.extend(group.rules)
        return rules

    def decision(self, path: str, user_agent: str) -> tuple[bool, RobotsRule | None, str]:
        """``(allowed, winning_rule, explanation)`` for one path."""
        rules = self.rules_for(user_agent)
        if not rules:
            # 2.2.1: "If no group matches the product token and there is no group
            # with a user-agent line with the '*' value, or no groups are present
            # at all, no rules apply."
            return True, None, "no group in the operator's robots.txt applies to this user agent, so no rules apply (RFC 9309 2.2.1)"
        hits = [rule for rule in rules if rule.pattern and rule.matches(path)]
        if not hits:
            return True, None, "no rule in the applicable group matches this path, so the URI is allowed (RFC 9309 2.2.2)"
        # 2.2.2: the most specific match (most octets) is used; an allow and an
        # equivalent disallow resolve in favour of allow.
        best = max(hits, key=lambda rule: (rule.specificity, 1 if rule.kind == "allow" else 0))
        tied = [rule for rule in hits if rule.specificity == best.specificity]
        if len(tied) > 1 and {rule.kind for rule in tied} == {"allow", "disallow"}:
            best = next(rule for rule in tied if rule.kind == "allow")
        allowed = best.kind == "allow"
        why = (
            f"{'allow' if allowed else 'disallow'} rule {best.line!r} is the most specific match for {path} "
            f"({best.specificity} octets, RFC 9309 2.2.2)"
        )
        return allowed, best, why


def robots_url_for(url: str) -> str:
    """RFC 9309 2.3: ``scheme:[//authority]/robots.txt``."""
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/robots.txt"


def path_for(url: str) -> str:
    """The path the rules are matched against (see the module docstring, note 1)."""
    parts = urllib.parse.urlsplit(url)
    return parts.path or "/"


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------


@dataclass
class RobotsDecision:
    """One published decision about one URL."""

    url: str
    allowed: bool
    status: str                  # allowed | disallowed | no_rules | unavailable_allowed
                                 # | unreachable_disallowed | not_a_robots_file | offline | cached_*
    robots_url: str
    host: str
    path: str
    rule: str = ""               # verbatim winning line, when one matched
    detail: str = ""
    fetched_at: str = ""
    http_status: int | None = None
    content_type: str = ""
    sha256: str = ""
    from_cache: bool = False
    cache_age_hours: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "allowed": self.allowed,
            "status": self.status,
            "robots_url": self.robots_url,
            "host": self.host,
            "path": self.path,
            "rule": self.rule,
            "detail": self.detail,
            "fetched_at": self.fetched_at,
            "http_status": self.http_status,
            "content_type": self.content_type,
            "sha256": self.sha256,
            "from_cache": self.from_cache,
            "cache_age_hours": self.cache_age_hours,
            "spec": SPEC_URL,
        }


Fetcher = Callable[[str, int], "tuple[int, dict[str, str], str]"]


def _default_fetcher(url: str, timeout: int) -> tuple[int, dict[str, str], str]:
    """Fetch robots.txt with no retries and no budget accounting.

    One request per host per 24 hours (RFC 9309 2.4). Retries are deliberately
    absent: an unreachable robots.txt is already a defined outcome (2.3.1.4), and
    retrying it three times would only slow a cycle whose egress is blocked.
    """
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "SelfLearn-robots-check/0.1 (RFC 9309 policy gate)")
    request.add_header("Accept", "text/plain, */*;q=0.5")
    request.add_header("Accept-Encoding", "identity")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(PARSE_LIMIT_BYTES + 1)
        headers = {k.lower(): v for k, v in response.headers.items()}
        return int(response.status), headers, body.decode("utf-8", errors="replace")


@dataclass
class RobotsGate:
    """Checks request URLs against their host's robots.txt before they are sent.

    The gate is attached to :class:`~selflearn.fetch.net.HttpClient` so that no
    caller - the collector, the reachability probe, the change scan - can bypass
    it by forgetting to ask. It is inert when the network is disabled, because an
    offline run performs no requests anyway and must keep replaying the snapshots
    it already stored.
    """

    cache_path: Path | None = None
    user_agent: str = ""
    allow_network: bool = True
    timeout: int = DEFAULT_TIMEOUT
    max_age_hours: float = CACHE_MAX_AGE_HOURS
    fetcher: Fetcher | None = None
    hosts: dict[str, dict[str, Any]] = field(default_factory=dict)
    checked: dict[str, RobotsDecision] = field(default_factory=dict)
    #: Hosts this gate instance actually consulted. The cache holds hosts from
    #: earlier runs, so "hosts in the table" and "hosts read by this run" are
    #: different numbers and the published figures must not conflate them.
    touched: set[str] = field(default_factory=set, init=False, repr=False)
    #: Decisions read back from the cache, kept so a run that makes no request
    #: does not erase the last recorded one.
    stored_decisions: list[dict[str, Any]] = field(default_factory=list, init=False, repr=False)
    stored_decisions_at: str = field(default="", init=False, repr=False)
    _files: dict[str, RobotsFile | None] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.user_agent:
            from ..config import DEFAULT_USER_AGENT

            self.user_agent = DEFAULT_USER_AGENT
        if self.cache_path is not None:
            self.cache_path = Path(self.cache_path)
            self._load_cache()

    # -- cache -----------------------------------------------------------
    def _load_cache(self) -> None:
        path = self.cache_path
        if path is None or not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        hosts = payload.get("hosts") if isinstance(payload, dict) else None
        if isinstance(hosts, dict):
            self.hosts = hosts
        # The stored decisions are deliberately *not* loaded into `checked`: a
        # run that consults the gate must make its own decisions, and reusing an
        # old one would let a changed robots.txt go unnoticed for a whole cycle.
        if isinstance(payload, dict):
            self.stored_decisions = [
                row for row in (payload.get("decisions") or []) if isinstance(row, dict)
            ]
            self.stored_decisions_at = str(payload.get("decisions_recorded_at") or payload.get("generated_at") or "")

    def save(self) -> None:
        """Persist the fetch records so a later cycle can reuse them (2.4).

        The per-URL decisions are stored alongside them: `python3 -m selflearn
        site` rebuilds the published pages without running a cycle, and the
        access-policy table on the sources page shows the decision each request
        URL received, with the verbatim rule behind it. A rebuild that could not
        read them back would publish the hosts but none of the decisions.
        """
        if self.cache_path is None:
            return
        fresh = sorted(self.checked.values(), key=lambda d: (d.host, d.url))
        if fresh:
            decisions = [decision.to_dict() for decision in fresh]
            recorded_at = utcnow_iso()
        else:
            # A run that consulted nothing - an offline cycle, a rebuild - must
            # not blank the decisions the last networked check recorded. They are
            # kept, with the timestamp of the run that actually made them.
            decisions = self.stored_decisions
            recorded_at = self.stored_decisions_at
        payload = {
            "generated_at": utcnow_iso(),
            "spec": SPEC_URL,
            "user_agent": self.user_agent,
            "cache_max_age_hours": self.max_age_hours,
            "hosts": self.hosts,
            "decisions": decisions,
            "decisions_recorded_at": recorded_at,
        }
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    def _cached_file(self, host: str) -> tuple[RobotsFile | None, float | None, str]:
        """Return ``(file, age_hours, note)`` from the cache, if it is usable."""
        row = self.hosts.get(host) or {}
        text = row.get("text")
        fetched = row.get("fetched_at") or ""
        if not isinstance(text, str) or not fetched:
            return None, None, ""
        age = _age_hours(fetched)
        if age is None:
            return None, None, ""
        parsed = RobotsFile.parse(
            text,
            content_type=row.get("content_type", ""),
            source_url=row.get("robots_url", ""),
            fetched_at=fetched,
            http_status=row.get("http_status"),
        )
        return parsed, age, row.get("status", "")

    # -- fetching --------------------------------------------------------
    def _host_record(self, host: str, robots_url: str) -> tuple[RobotsFile | None, str, dict[str, Any]]:
        """Fetch (or reuse) the robots.txt for one host.

        Returns the parsed file (or ``None`` when it is undefined), a status
        string, and the record that is published and cached.
        """
        if host in self._files:
            record = self.hosts.get(host) or {}
            return self._files[host], record.get("status", "cached"), record

        cached, age, cached_status = self._cached_file(host)
        if cached is not None and age is not None and age <= self.max_age_hours:
            # 2.4: a cached copy is fine inside 24 hours.
            self._files[host] = cached
            record = dict(self.hosts.get(host) or {})
            record["status"] = f"cached_{cached_status}" if not cached_status.startswith("cached") else cached_status
            record["cache_age_hours"] = round(age, 2)
            self.hosts[host] = record
            return cached, record["status"], record

        record: dict[str, Any] = {
            "host": host,
            "robots_url": robots_url,
            "checked_at": utcnow_iso(),
            "status": "",
            "http_status": None,
            "content_type": "",
            "sha256": "",
            "rules": 0,
            "groups": 0,
            "media_type_note": "",
            "detail": "",
            "text": "",
            "truncated": False,
            "cache_age_hours": None,
            "spec": SPEC_URL,
        }
        if not self.allow_network:
            record["status"] = "offline"
            record["detail"] = "Network use was disabled for this run; robots.txt was not fetched."
            self.hosts[host] = record
            self._files[host] = None
            return None, "offline", record

        fetch = self.fetcher or _default_fetcher
        try:
            status, headers, text = fetch(robots_url, self.timeout)
        except urllib.error.HTTPError as exc:
            status_code = int(exc.code)
            record["http_status"] = status_code
            if 400 <= status_code < 500:
                # 2.3.1.3: "If a server status code indicates that the robots.txt
                # file is unavailable to the crawler, then the crawler MAY access
                # any resources on the server."
                record["status"] = "unavailable"
                record["detail"] = (
                    f"HTTP {status_code} for {robots_url}: the file is unavailable, so any resource on this host "
                    "may be accessed (RFC 9309 2.3.1.3)."
                )
                self.hosts[host] = record
                self._files[host] = None
                return None, "unavailable", record
            record["status"] = "unreachable"
            record["detail"] = f"HTTP {status_code} for {robots_url}"
            return self._unreachable(host, robots_url, record, cached, age)
        except Exception as exc:  # URLError, timeout, TLS refusal, DNS failure
            record["status"] = "unreachable"
            record["detail"] = f"{type(exc).__name__}: {str(exc)[:200]}"
            return self._unreachable(host, robots_url, record, cached, age)

        content_type = headers.get("content-type", "")
        record["http_status"] = status
        record["content_type"] = content_type
        record["sha256"] = sha256_text(text)
        parsed = RobotsFile.parse(
            text,
            content_type=content_type,
            source_url=robots_url,
            fetched_at=utcnow_iso(),
            http_status=status,
        )
        record["fetched_at"] = parsed.fetched_at
        record["rules"] = parsed.rule_count
        record["groups"] = len(parsed.groups)
        record["sitemaps"] = parsed.sitemaps[:5]
        record["unattached_rules"] = parsed.unattached_rules[:5]
        record["truncated"] = parsed.truncated
        record["text"] = text[:STORED_TEXT_LIMIT]
        if content_type and "text/plain" not in content_type.casefold():
            # 2.3: the file "MUST be UTF-8 encoded ... and Internet Media Type
            # 'text/plain'". It is not, so the observation is published; 2.3.1.1
            # still requires following the parseable rules, and a body with no
            # user-agent lines has no groups at all (2.2.1).
            record["media_type_note"] = (
                f"{robots_url} answered HTTP {status} with content-type {content_type}, not the text/plain that "
                "RFC 9309 2.3 requires. The body was parsed anyway: whatever rules it contains are followed, and "
                "if it contains none, no rules apply."
            )
        record["status"] = "fetched"
        record["detail"] = (
            f"{parsed.rule_count} rule(s) in {len(parsed.groups)} group(s); sha256 {record['sha256'][:16]}..."
        )
        self.hosts[host] = record
        self._files[host] = parsed
        return parsed, "fetched", record

    def _unreachable(
        self,
        host: str,
        robots_url: str,
        record: dict[str, Any],
        cached: RobotsFile | None,
        age: float | None,
    ) -> tuple[RobotsFile | None, str, dict[str, Any]]:
        """RFC 9309 2.3.1.4: unreachable means undefined, and undefined means disallow."""
        if cached is not None:
            # 2.3.1.4 permits continuing to use a cached copy when the file is
            # unreachable, however old it is.
            record["status"] = "unreachable_cached"
            record["cache_age_hours"] = age
            record["detail"] = (
                f"{robots_url} could not be fetched ({record['detail']}); the cached copy from "
                f"{cached.fetched_at} is used instead, as RFC 9309 2.3.1.4 permits."
            )
            self.hosts[host] = record
            self._files[host] = cached
            return cached, "unreachable_cached", record
        record["detail"] = (
            f"{robots_url} could not be fetched ({record['detail']}). RFC 9309 2.3.1.4: an unreachable robots.txt "
            "means the file is undefined and a crawler MUST assume complete disallow, so no request was made to "
            "this host."
        )
        self.hosts[host] = record
        self._files[host] = None
        return None, "unreachable", record

    # -- public API ------------------------------------------------------
    def check(self, url: str) -> RobotsDecision:
        """Decide whether ``url`` may be requested, and record the decision."""
        if url in self.checked:
            return self.checked[url]
        parts = urllib.parse.urlsplit(url)
        host = parts.netloc
        robots_url = robots_url_for(url)
        path = path_for(url)
        if not self.allow_network:
            decision = RobotsDecision(
                url=url,
                allowed=True,
                status="offline",
                robots_url=robots_url,
                host=host,
                path=path,
                detail="Network use is disabled for this run; the gate made no request and the client refuses every fetch itself.",
            )
            self.checked[url] = decision
            return decision

        self.touched.add(host)
        parsed, status, record = self._host_record(host, robots_url)
        base = dict(
            robots_url=robots_url,
            host=host,
            path=path,
            fetched_at=record.get("fetched_at") or record.get("checked_at") or "",
            http_status=record.get("http_status"),
            content_type=record.get("content_type", ""),
            sha256=record.get("sha256", ""),
            from_cache=bool(str(status).startswith("cached")) or status == "unreachable_cached",
            cache_age_hours=record.get("cache_age_hours"),
        )
        if status == "unavailable":
            decision = RobotsDecision(
                url=url, allowed=True, status="unavailable_allowed", detail=record.get("detail", ""), **base
            )
        elif parsed is None:
            decision = RobotsDecision(
                url=url,
                allowed=False,
                status="unreachable_disallowed",
                detail=record.get("detail", ""),
                **base,
            )
        else:
            allowed, rule, why = parsed.decision(path, self.user_agent)
            detail = why
            if record.get("media_type_note"):
                detail = f"{record['media_type_note']} {why}"
            if rule is None and allowed:
                # Two different reasons for "allowed with no rule", and the site
                # says which: a file with no applicable group at all (RFC 9309
                # 2.2.1) versus an applicable group none of whose rules match
                # this path (2.2.2).
                suffix = "_no_applicable_group" if not parsed.rules_for(self.user_agent) else ""
                status_name = "allowed" + suffix
            else:
                status_name = "allowed" if allowed else "disallowed"
            decision = RobotsDecision(
                url=url,
                allowed=allowed,
                status=status_name,
                rule=rule.line if rule else "",
                detail=detail,
                **base,
            )
        self.checked[url] = decision
        return decision

    def assert_allowed(self, url: str) -> RobotsDecision:
        """Raise :class:`RobotsDisallowed` for a refused URL, else return the decision."""
        decision = self.check(url)
        if not decision.allowed:
            raise RobotsDisallowed(decision)
        return decision

    # -- publication -----------------------------------------------------
    def payload(self) -> dict[str, Any]:
        """Everything the site publishes about the policy gate."""
        decisions = sorted(self.checked.values(), key=lambda d: (d.host, d.url))
        counts: dict[str, int] = {}
        for decision in decisions:
            counts[decision.status] = counts.get(decision.status, 0) + 1
        hosts: list[dict[str, Any]] = []
        for host in sorted(self.hosts):
            row = dict(self.hosts[host])
            # The verbatim file stays in state/robots.json (the cache a reviewer
            # can read); the published payload carries its hash and a short
            # excerpt, so site_data.json does not grow by every robots.txt.
            text = row.pop("text", "") or ""
            row["excerpt"] = "\n".join(text.splitlines()[:18])
            hosts.append(row)
        return {
            "spec": SPEC_URL,
            "spec_text": SPEC_TEXT_URL,
            "user_agent": self.user_agent,
            "cache_max_age_hours": self.max_age_hours,
            "generated_at": utcnow_iso(),
            # Two different counts, because they mean two different things:
            # hosts_published is every host record on the page (this run's plus
            # the cached ones), hosts_checked is what *this* run read.
            "hosts_published": len(self.hosts),
            "hosts_checked": len(self.touched),
            "network_allowed": self.allow_network,
            "urls_checked": len(decisions),
            "urls_refused": sum(1 for d in decisions if not d.allowed),
            "by_status": dict(sorted(counts.items())),
            "hosts": hosts,
            "decisions": [decision.to_dict() for decision in decisions],
        }


def _age_hours(stamp: str) -> float | None:
    from datetime import datetime, timezone

    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - parsed).total_seconds() / 3600.0


def load_gate(
    root: Path | str,
    *,
    allow_network: bool = True,
    user_agent: str = "",
    fetcher: Fetcher | None = None,
) -> RobotsGate:
    """The gate a cycle uses, reading and writing ``state/robots.json``."""
    return RobotsGate(
        cache_path=Path(root) / "state" / "robots.json",
        user_agent=user_agent,
        allow_network=allow_network,
        fetcher=fetcher,
    )


def summarise(payload: dict[str, Any]) -> dict[str, Any]:
    """The figures a run summary may quote about the gate."""
    return {
        "hosts_checked": payload.get("hosts_checked", 0),
        "hosts_published": payload.get("hosts_published", payload.get("hosts_checked", 0)),
        "urls_checked": payload.get("urls_checked", 0),
        "urls_refused": payload.get("urls_refused", 0),
        "network_allowed": payload.get("network_allowed", True),
        "by_status": payload.get("by_status", {}),
    }


def host_decisions(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Per-host rows for the sources page."""
    return payload.get("hosts", []) or []
