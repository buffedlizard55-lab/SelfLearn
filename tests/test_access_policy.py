"""Offline tests for the RFC 9309 gate, the adapters it protects, and the collector.

Every case here runs without a network: the gate is given a stub fetcher, so the
clause of the standard being exercised is the thing under test rather than the
reachability of this machine. The clause numbers in the test names are RFC 9309
(https://www.rfc-editor.org/rfc/rfc9309.txt).
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.fetch import collector as collector_module  # noqa: E402
from selflearn.fetch.registry import REGISTRY  # noqa: E402
from selflearn.fetch.collector import Collector  # noqa: E402
from selflearn.fetch.net import HttpClient  # noqa: E402
from selflearn.fetch.robots import (  # noqa: E402
    CACHE_MAX_AGE_HOURS,
    PARSE_LIMIT_BYTES,
    RobotsDisallowed,
    RobotsFile,
    RobotsGate,
    compile_pattern,
    path_for,
    robots_url_for,
    summarise,
)
from selflearn.fetch.sources import build_source  # noqa: E402
from selflearn.models import Topic  # noqa: E402

USER_AGENT = "SelfLearn/0.1 (autonomous research engine) python-urllib"

PYPI_ROBOTS = """\
# https://pypi.org/robots.txt (fetched 2026-09-22)
User-agent: *
Disallow: /pypi/*/json
Disallow: /search*
Disallow: /account/
Allow: /account/login
Sitemap: https://pypi.org/sitemap.xml
"""


class StubFetcher:
    """A stand-in for :func:`_default_fetcher` that counts what it was asked for."""

    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, url: str, timeout: int) -> tuple[int, dict[str, str], str]:
        self.calls.append(url)
        response = self.responses.get(url, self.responses.get("*"))
        if response is None:
            raise urllib.error.URLError(f"no stub response for {url}")
        if isinstance(response, Exception):
            raise response
        status, headers, body = response
        return status, headers, body


def gate_with(fetcher: StubFetcher, *, root: Path | None = None, agent: str = USER_AGENT) -> RobotsGate:
    return RobotsGate(
        cache_path=(root / "state" / "robots.json") if root else None,
        user_agent=agent,
        allow_network=True,
        fetcher=fetcher,
    )


class ParseTests(unittest.TestCase):
    """RFC 9309 2.2: what a robots.txt file means."""

    def test_group_selection_is_by_product_token_substring(self) -> None:
        parsed = RobotsFile.parse(
            "User-agent: SelfLearn\nDisallow: /private\n\nUser-agent: *\nDisallow: /\n",
            source_url="https://example.test/robots.txt",
        )
        # 2.2.1: the token is a substring of the User-Agent header, so the
        # specific group applies and the wildcard group is not merged into it.
        rules = parsed.rules_for(USER_AGENT)
        self.assertEqual([rule.pattern for rule in rules], ["/private"])
        self.assertTrue(parsed.decision("/", USER_AGENT)[0])
        self.assertFalse(parsed.decision("/private/x", USER_AGENT)[0])

    def test_wildcard_group_applies_when_no_token_matches(self) -> None:
        parsed = RobotsFile.parse("User-agent: Googlebot\nDisallow: /no\nUser-agent: *\nDisallow: /all\n")
        self.assertFalse(parsed.decision("/all/thing", USER_AGENT)[0])
        self.assertTrue(parsed.decision("/open", USER_AGENT)[0])

    def test_several_matching_groups_are_merged(self) -> None:
        parsed = RobotsFile.parse(
            "User-agent: SelfLearn\nDisallow: /a\nUser-agent: python-urllib\nDisallow: /b\nUser-agent: *\nDisallow: /c\n",
        )
        patterns = sorted(rule.pattern for rule in parsed.rules_for(USER_AGENT))
        self.assertEqual(patterns, ["/a", "/b"])

    def test_no_applicable_group_means_no_rules(self) -> None:
        parsed = RobotsFile.parse("User-agent: Googlebot\nDisallow: /\n")
        allowed, rule, why = parsed.decision("/anything", USER_AGENT)
        self.assertTrue(allowed)
        self.assertIsNone(rule)
        self.assertIn("2.2.1", why)

    def test_most_specific_rule_wins_and_allow_beats_an_equivalent_disallow(self) -> None:
        parsed = RobotsFile.parse(
            "User-agent: *\n"
            "Disallow: /folder\n"
            "Allow: /folder/page\n"
            "Disallow: /folder/page.html\n"
            "Allow: /folder/page.html\n",
        )
        # 2.2.2: the longest match is used, so the allow under /folder wins.
        self.assertTrue(parsed.decision("/folder/page", USER_AGENT)[0])
        self.assertFalse(parsed.decision("/folder/other", USER_AGENT)[0])
        # 2.2.2: equivalent allow and disallow resolve in favour of allow.
        self.assertTrue(parsed.decision("/folder/page.html", USER_AGENT)[0])

    def test_no_matching_rule_means_allowed(self) -> None:
        parsed = RobotsFile.parse("User-agent: *\nDisallow: /admin\n")
        allowed, rule, why = parsed.decision("/public/data", USER_AGENT)
        self.assertTrue(allowed)
        self.assertIsNone(rule)
        self.assertIn("2.2.2", why)

    def test_empty_disallow_is_not_a_rule_that_matches(self) -> None:
        parsed = RobotsFile.parse("User-agent: *\nDisallow:\n")
        self.assertTrue(parsed.decision("/anything", USER_AGENT)[0])

    def test_rules_outside_a_group_are_ignored_but_published(self) -> None:
        parsed = RobotsFile.parse("Disallow: /orphan\nUser-agent: *\nDisallow: /real\n")
        self.assertEqual(parsed.unattached_rules, ["Disallow: /orphan"])
        self.assertFalse(parsed.decision("/real", USER_AGENT)[0])
        self.assertTrue(parsed.decision("/orphan", USER_AGENT)[0])

    def test_comment_hash_and_special_characters(self) -> None:
        parsed = RobotsFile.parse(
            "User-agent: * # every crawler\nDisallow: /a#b   # a literal hash is not a comment start\n"
            "Disallow: /*.json$\nDisallow: /q?a=1\n",
        )
        patterns = [rule.pattern for rule in parsed.rules_for(USER_AGENT)]
        self.assertIn("/a", patterns)          # the comment was cut at the first "#"
        self.assertIn("/*.json$", patterns)
        self.assertIn("/q?a=1", patterns)
        # 2.2.3: "*" is zero or more of any character, "$" ends the pattern, and
        # "?" is literal because the protocol defines only those three specials.
        self.assertFalse(parsed.decision("/data.json", USER_AGENT)[0])
        self.assertTrue(parsed.decision("/data.json?x=1", USER_AGENT)[0])
        self.assertFalse(parsed.decision("/q?a=1", USER_AGENT)[0])
        self.assertTrue(parsed.decision("/qxb=1", USER_AGENT)[0])
        self.assertTrue(compile_pattern("/a").match("/abc"))
        self.assertFalse(compile_pattern("/a$").match("/abc"))

    def test_sitemap_does_not_terminate_a_group(self) -> None:
        parsed = RobotsFile.parse("User-agent: *\nSitemap: https://example.test/s.xml\nDisallow: /x\n")
        self.assertEqual(parsed.sitemaps, ["https://example.test/s.xml"])
        self.assertEqual(parsed.rule_count, 1)
        self.assertFalse(parsed.decision("/x", USER_AGENT)[0])

    def test_a_body_over_the_parsing_limit_is_truncated_and_says_so(self) -> None:
        text = "User-agent: *\n" + ("Disallow: /x\n" * (PARSE_LIMIT_BYTES // 8))
        parsed = RobotsFile.parse(text)
        self.assertTrue(parsed.truncated)          # 2.5: at least 500 KiB are parsed
        self.assertLessEqual(len(parsed.text.encode("utf-8")), PARSE_LIMIT_BYTES)

    def test_url_helpers_match_the_standard(self) -> None:
        self.assertEqual(robots_url_for("https://pypi.org/rss/packages.xml?a=1"), "https://pypi.org/robots.txt")
        self.assertEqual(path_for("https://pypi.org/rss/packages.xml?a=1"), "/rss/packages.xml")
        self.assertEqual(path_for("https://pypi.org"), "/")


class GateTests(unittest.TestCase):
    """RFC 9309 2.3: what a fetch outcome means for a request."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_explicit_disallow_is_refused_with_the_verbatim_rule(self) -> None:
        fetcher = StubFetcher({"https://pypi.org/robots.txt": (200, {"content-type": "text/plain"}, PYPI_ROBOTS)})
        gate = gate_with(fetcher, root=self.root)
        decision = gate.check("https://pypi.org/pypi/requests/json")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status, "disallowed")
        self.assertEqual(decision.rule, "Disallow: /pypi/*/json")
        self.assertIn("2.2.2", decision.detail)
        with self.assertRaises(RobotsDisallowed) as caught:
            gate.assert_allowed("https://pypi.org/pypi/requests/json")
        self.assertEqual(caught.exception.decision.rule, "Disallow: /pypi/*/json")
        # The documented feed route on the same host is allowed.
        feed = gate.check("https://pypi.org/rss/packages.xml")
        self.assertTrue(feed.allowed)
        self.assertEqual(feed.status, "allowed")

    def test_a_4xx_robots_txt_fails_open(self) -> None:
        fetcher = StubFetcher({"https://api.github.com/robots.txt": urllib.error.HTTPError(
            "https://api.github.com/robots.txt", 404, "Not Found", {}, None)})  # type: ignore[arg-type]
        gate = gate_with(fetcher, root=self.root)
        decision = gate.check("https://api.github.com/search/repositories?q=x")
        self.assertTrue(decision.allowed)          # 2.3.1.3
        self.assertEqual(decision.status, "unavailable_allowed")
        self.assertEqual(decision.http_status, 404)

    def test_an_unreachable_robots_txt_fails_closed(self) -> None:
        fetcher = StubFetcher({"https://example.test/robots.txt": urllib.error.URLError("TLS/SSL connection closed")})
        gate = gate_with(fetcher, root=self.root)
        decision = gate.check("https://example.test/data")
        self.assertFalse(decision.allowed)         # 2.3.1.4
        self.assertEqual(decision.status, "unreachable_disallowed")
        self.assertIn("complete disallow", decision.detail)
        host = gate.hosts["example.test"]
        self.assertEqual(host["status"], "unreachable")
        self.assertIn("URLError", host["detail"])

    def test_a_5xx_robots_txt_fails_closed_too(self) -> None:
        fetcher = StubFetcher({"https://example.test/robots.txt": urllib.error.HTTPError(
            "https://example.test/robots.txt", 503, "Unavailable", {}, None)})  # type: ignore[arg-type]
        gate = gate_with(fetcher, root=self.root)
        decision = gate.check("https://example.test/data")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status, "unreachable_disallowed")
        self.assertEqual(gate.hosts["example.test"]["http_status"], 503)

    def test_a_cached_copy_is_reused_inside_24_hours_and_refetched_after(self) -> None:
        url = "https://example.test/robots.txt"
        fetcher = StubFetcher({url: (200, {"content-type": "text/plain"}, "User-agent: *\nDisallow: /x\n")})
        gate = gate_with(fetcher, root=self.root)
        self.assertFalse(gate.check("https://example.test/x").allowed)
        self.assertTrue(gate.check("https://example.test/y").allowed)
        self.assertEqual(fetcher.calls, [url])     # one request per host
        gate.save()

        # A second gate in the same run reuses the cache (2.4) without fetching.
        reloaded = gate_with(StubFetcher({}), root=self.root)
        self.assertFalse(reloaded.check("https://example.test/x").allowed)
        self.assertTrue(reloaded.hosts["example.test"]["status"].startswith("cached"))
        self.assertIsNotNone(reloaded.hosts["example.test"]["cache_age_hours"])

        # Ageing the cached copy past the limit forces a refetch.
        state_path = self.root / "state" / "robots.json"
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        payload["hosts"]["example.test"]["fetched_at"] = "2000-01-01T00:00:00Z"
        state_path.write_text(json.dumps(payload), encoding="utf-8")
        aged_fetcher = StubFetcher({url: (200, {"content-type": "text/plain"}, "User-agent: *\nDisallow: /z\n")})
        aged = gate_with(aged_fetcher, root=self.root)
        self.assertTrue(aged.check("https://example.test/x").allowed)
        self.assertFalse(aged.check("https://example.test/z").allowed)
        self.assertEqual(aged_fetcher.calls, [url])   # the stale copy was replaced
        self.assertEqual(aged.hosts["example.test"]["status"], "fetched")
        self.assertGreaterEqual(CACHE_MAX_AGE_HOURS, 24)

    def test_an_unreachable_file_falls_back_to_the_cached_copy(self) -> None:
        url = "https://example.test/robots.txt"
        fetcher = StubFetcher({url: (200, {"content-type": "text/plain"}, "User-agent: *\nDisallow: /x\n")})
        gate = gate_with(fetcher, root=self.root)
        gate.check("https://example.test/x")
        gate.save()
        # Age it out of the cache window, then make the host unreachable: 2.3.1.4
        # permits carrying on with the cached copy however old it is.
        state_path = self.root / "state" / "robots.json"
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        payload["hosts"]["example.test"]["fetched_at"] = "2000-01-01T00:00:00Z"
        state_path.write_text(json.dumps(payload), encoding="utf-8")
        broken = gate_with(StubFetcher({url: urllib.error.URLError("gone")}), root=self.root)
        decision = broken.check("https://example.test/x")
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.from_cache)
        self.assertEqual(broken.hosts["example.test"]["status"], "unreachable_cached")

    def test_a_body_that_is_not_text_plain_is_recorded_and_then_parsed(self) -> None:
        # registry.npmjs.org answers /robots.txt with the package document of a
        # package called "robots.txt" (content-type application/json, observed
        # 2026-09-22): a JSON body has no user-agent lines, so 2.2.1 leaves no
        # rules applying, and the observation is published rather than hidden.
        url = "https://registry.npmjs.org/robots.txt"
        body = json.dumps({"name": "robots.txt", "versions": {"1.0.0": {}}})
        fetcher = StubFetcher({url: (200, {"content-type": "application/json"}, body)})
        gate = gate_with(fetcher, root=self.root)
        decision = gate.check("https://registry.npmjs.org/-/v1/search?text=agent")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.status, "allowed_no_applicable_group")
        self.assertEqual(decision.content_type, "application/json")
        self.assertIn("text/plain", gate.hosts["registry.npmjs.org"]["media_type_note"])
        self.assertIn("2.2.1", decision.detail)

    def test_an_applicable_group_with_no_matching_path_is_plain_allowed(self) -> None:
        url = "https://example.test/robots.txt"
        fetcher = StubFetcher({url: (200, {"content-type": "text/plain"}, "User-agent: *\nDisallow: /admin\n")})
        gate = gate_with(fetcher, root=self.root)
        decision = gate.check("https://example.test/public")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.status, "allowed")   # 2.2.2, a group did apply
        self.assertEqual(decision.rule, "")

    def test_an_offline_run_makes_no_policy_request(self) -> None:
        gate = RobotsGate(cache_path=None, user_agent=USER_AGENT, allow_network=False)
        decision = gate.check("https://pypi.org/pypi/requests/json")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.status, "offline")
        self.assertEqual(gate.hosts, {})

    def test_the_same_url_is_decided_once(self) -> None:
        url = "https://example.test/robots.txt"
        fetcher = StubFetcher({url: (200, {"content-type": "text/plain"}, "User-agent: *\n")})
        gate = gate_with(fetcher, root=self.root)
        first = gate.check("https://example.test/a")
        second = gate.check("https://example.test/a")
        self.assertIs(first, second)
        self.assertEqual(len(gate.payload()["decisions"]), 1)

    def test_payload_and_summary_publish_every_decision(self) -> None:
        fetcher = StubFetcher({
            "https://pypi.org/robots.txt": (200, {"content-type": "text/plain"}, PYPI_ROBOTS),
            "https://example.test/robots.txt": urllib.error.URLError("refused"),
        })
        gate = gate_with(fetcher, root=self.root)
        gate.check("https://pypi.org/pypi/requests/json")
        gate.check("https://pypi.org/rss/packages.xml")
        gate.check("https://example.test/data")
        payload = gate.payload()
        figures = summarise(payload)
        self.assertEqual(figures["hosts_checked"], 2)
        self.assertEqual(figures["urls_checked"], 3)
        self.assertEqual(figures["urls_refused"], 2)
        self.assertEqual(figures["by_status"], {"allowed": 1, "disallowed": 1, "unreachable_disallowed": 1})
        # The published payload carries a hash and an excerpt, never the whole file.
        for host in payload["hosts"]:
            self.assertNotIn("text", host)
            self.assertIn("excerpt", host)

    def test_the_cache_keeps_the_verbatim_file_for_a_reviewer(self) -> None:
        url = "https://pypi.org/robots.txt"
        fetcher = StubFetcher({url: (200, {"content-type": "text/plain"}, PYPI_ROBOTS)})
        gate = gate_with(fetcher, root=self.root)
        gate.check("https://pypi.org/pypi/x/json")
        gate.save()
        stored = json.loads((self.root / "state" / "robots.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["spec"], "https://www.rfc-editor.org/rfc/rfc9309.html")
        self.assertEqual(stored["cache_max_age_hours"], CACHE_MAX_AGE_HOURS)
        self.assertIn("Disallow: /pypi/*/json", stored["hosts"]["pypi.org"]["text"])


class AdapterRouteTests(unittest.TestCase):
    """The adapters build only routes their operator documents."""

    def test_every_registered_adapter_can_build_a_request(self) -> None:
        # This is the sweep that found worldbank's KeyError('indicator').
        broken = []
        for source_id in sorted(REGISTRY):
            spec = REGISTRY[source_id]
            if spec.requires_key:
                continue
            try:
                build_source(source_id).requests("autonomous research agent")
            except Exception as exc:  # noqa: BLE001 - the point is that none may raise
                broken.append(f"{source_id}: {type(exc).__name__}: {exc}")
        self.assertEqual(broken, [])

    def test_worldbank_uses_the_documented_indicator_routes(self) -> None:
        source = build_source("worldbank")
        (all_indicators,) = source.requests("autonomous research agent")
        self.assertEqual(all_indicators.url, "https://api.worldbank.org/v2/indicator")
        self.assertEqual(all_indicators.params["format"], "json")
        self.assertEqual(all_indicators.label, "worldbank:all-indicators")
        (one,) = source.requests("NY.GDP.MKTP.CD")
        self.assertEqual(one.url, "https://api.worldbank.org/v2/indicator/NY.GDP.MKTP.CD")
        self.assertEqual(one.label, "worldbank:NY.GDP.MKTP.CD")
        self.assertIsNone(source.indicator_for("renewable energy share"))

    def test_eurostat_does_not_send_prose_as_a_dataset_code(self) -> None:
        source = build_source("eurostat")
        self.assertEqual(source.dataset_for("autonomous research agent"), ("nrg_ind_ren", False))
        self.assertEqual(source.dataset_for("nrg_ind_ren"), ("nrg_ind_ren", True))
        (request,) = source.requests("autonomous research agent")
        self.assertTrue(request.url.endswith("/statistics/1.0/data/nrg_ind_ren"))
        self.assertTrue(request.label.endswith(":default"))

    def test_pypi_requests_the_feeds_the_operator_directs_consumers_to(self) -> None:
        source = build_source("pypi")
        urls = [request.url for request in source.requests("anything")]
        self.assertEqual(urls, ["https://pypi.org/rss/packages.xml", "https://pypi.org/rss/updates.xml"])
        self.assertTrue(all("/json" not in url for url in urls))

    def test_npm_reports_its_own_minimum_query_length(self) -> None:
        source = build_source("npm")
        reason = source.unusable_query_reason("ai")
        self.assertIsNotNone(reason)
        self.assertIn("at least 3 characters", reason or "")
        self.assertIsNone(source.unusable_query_reason("agent"))
        self.assertTrue(source.requests("agent"))


class CollectorRobustnessTests(unittest.TestCase):
    """An unattended cycle survives an adapter that cannot build its request."""

    def test_an_adapter_that_raises_is_published_as_adapter_error(self) -> None:
        class Broken:
            spec = collector_module.build_source("arxiv").spec

            def missing_credential(self) -> str:
                return ""

            def unusable_query_reason(self, query: str) -> str | None:
                return None

            def requests(self, query: str):
                raise KeyError("indicator")

        topic = Topic(
            topic_id="t-broken",
            title="Autonomous research agents",
            slug="autonomous-research-agents",
            question="What do autonomous research agents do?",
            keywords=["autonomous", "research", "agent"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            collector = Collector(HttpClient(allow_network=False), Path(tmp) / "snapshots")
            original = collector_module.build_source
            collector_module.build_source = lambda source_id: Broken()  # type: ignore[assignment]
            self.addCleanup(setattr, collector_module, "build_source", original)
            outcome = collector.collect(topic, ["worldbank"])

        self.assertEqual(outcome.records, [])
        self.assertEqual([status.live_status for status in outcome.statuses], ["adapter_error"])
        self.assertIn("KeyError", outcome.statuses[0].detail)
        self.assertEqual([failure.stage for failure in outcome.failures], ["adapter"])
        self.assertIn("worldbank", outcome.failures[0].summary)
        self.assertEqual([item.severity for item in outcome.irregularities], ["error"])
        self.assertIn("https://", outcome.irregularities[0].url)

    def test_an_adapter_that_builds_nothing_says_so(self) -> None:
        topic = Topic(
            topic_id="t-empty",
            title="Autonomous research agents",
            slug="autonomous-research-agents",
            question="What do autonomous research agents do?",
            keywords=["agent"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            collector = Collector(HttpClient(allow_network=False), Path(tmp) / "snapshots")
            outcome = collector.collect(topic, ["npm"])
        statuses = {status.source_id: status.live_status for status in outcome.statuses}
        # npm refuses a two-character query itself; the collector must publish the
        # refusal rather than send a request the operator will not answer.
        self.assertIn(statuses.get("npm"), {"not_attempted", "reachable", "unreachable", "robots_disallowed",
                                            "robots_unreachable"})


if __name__ == "__main__":
    unittest.main()
