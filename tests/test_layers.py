"""Tests for the layers added on top of the verification core.

These cover the roadmap work: the substance rule (reading order and metadata
labelling), cross-document synthesis (the guard that stops a multi-source
statement from inventing a figure), the change scanner (documented filters only),
topic invention (promotion gates), and the USPTO Open Data Portal adapter that
replaced the retired PatentsView endpoint.

Every fixture response here is either a document the operator publishes or a
deliberately wrong one, and the wrong ones must be rejected.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.fetch.changes import (  # noqa: E402
    MECHANISMS,
    ChangeScanner,
    change_request,
    mechanism_table,
    scan_window,
)
from selflearn.fetch.net import HttpClient, HttpResult  # noqa: E402
from selflearn.fetch.registry import REGISTRY, get_source  # noqa: E402
from selflearn.fetch.sources import (  # noqa: E402
    CREDENTIAL_MECHANISMS,
    build_source,
    credential_status,
)
from selflearn.learn.substance import (  # noqa: E402
    SUBSTANCE_WEIGHTS,
    order_by_substance,
    score_claim,
    substance_rule,
    substance_summary,
)
from selflearn.learn.synthesis import figures_with_units, synthesise  # noqa: E402
from selflearn.models import Claim, EvidenceRecord, Topic, Verification  # noqa: E402
from selflearn.think.invention import (  # noqa: E402
    MIN_NOVELTY,
    candidate_phrases,
    library_vocabulary,
    propose_topics,
    score_proposal,
    to_topic,
)
from selflearn.util import sha256_text, utcnow_iso  # noqa: E402
from selflearn.verify.verifier import verify_synthesis  # noqa: E402


def http_result(url: str, payload: dict, *, content_type: str = "application/json") -> HttpResult:
    """A response object shaped exactly like one the client would return."""
    body = json.dumps(payload).encode("utf-8")
    return HttpResult(
        url=url,
        status=200,
        headers={"content-type": content_type},
        body=body,
        content_type=content_type,
        retrieved_at=utcnow_iso(),
        attempts=1,
    )


def make_claim(
    text: str,
    *,
    claim_id: str | None = None,
    evidence_id: str = "ev-a",
    verdict: str = "supported",
    source: str = "Source A",
    rank: int = 3,
    kind: str = "direct",
    quote: str = "",
) -> Claim:
    return Claim(
        claim_id=claim_id or f"cl-{sha256_text(text)[:10]}",
        topic_id="topic-test",
        text=text,
        evidence_id=evidence_id,
        source_name=source,
        url="https://example.org/doc",
        quote=quote or text,
        evidence_class="primary_source",
        evidence_rank=rank,
        verification=Verification(verdict=verdict, quote_match=True, coverage=0.95),
        claim_kind=kind,
    )


def make_record(evidence_id: str, title: str, text: str, *, source_id: str = "github", rank: int = 3) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        source_id=source_id,
        source_name=source_id,
        url=f"https://example.org/{evidence_id}",
        title=title,
        text=text,
        content_hash=sha256_text(text),
        evidence_class="primary_source",
        evidence_rank=rank,
        is_live=True,
    )


# ---------------------------------------------------------------------------
# Substance
# ---------------------------------------------------------------------------


class SubstanceRuleTests(unittest.TestCase):
    def test_weights_are_a_complete_published_rule(self):
        self.assertAlmostEqual(sum(SUBSTANCE_WEIGHTS.values()), 1.0, places=9)
        rule = substance_rule()
        self.assertEqual(set(rule["weights"]), set(SUBSTANCE_WEIGHTS))
        self.assertEqual(set(rule["features"]), set(SUBSTANCE_WEIGHTS))

    def test_quantified_claim_outranks_registry_metadata(self):
        quantified = make_claim(
            "Capacity degraded 18% over 400 cycles because the electrolyte decomposes above 40 C."
        )
        metadata = make_claim("The record for selflearn reports licence MIT.")
        self.assertEqual(score_claim(quantified).label, "substantive")
        self.assertEqual(score_claim(metadata).label, "metadata")
        self.assertGreater(score_claim(quantified).total, score_claim(metadata).total)

    def test_an_unsupported_claim_cannot_outscore_an_equivalent_supported_one(self):
        supported = make_claim("Latency fell 32% after the cache was enabled.", verdict="supported")
        unsupported = make_claim("Latency fell 32% after the cache was enabled.", verdict="unsupported")
        self.assertGreater(score_claim(supported).total, score_claim(unsupported).total)

    def test_scoring_is_deterministic_and_bounded(self):
        claim = make_claim("Two of the nine adapters returned 500 errors in 2026.")
        first, second = score_claim(claim), score_claim(claim)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertGreaterEqual(first.total, 0.0)
        self.assertLessEqual(first.total, 1.0)

    def test_ordering_is_stable_and_puts_metadata_last(self):
        claims = [
            make_claim("The record for alpha reports language Python.", claim_id="cl-1"),
            make_claim("Throughput improved 41% when batching was enabled in 2026.", claim_id="cl-2"),
            make_claim("The record for beta reports licence Apache-2.0.", claim_id="cl-3"),
        ]
        ordered = order_by_substance(claims)
        self.assertEqual(ordered[0].claim_id, "cl-2")
        self.assertEqual(order_by_substance(list(reversed(claims)))[0].claim_id, "cl-2")

    def test_summary_counts_match_the_input(self):
        claims = [
            make_claim("Errors rose 12% in 2026 because the pool was exhausted."),
            make_claim("The record for gamma reports stars 400."),
        ]
        summary = substance_summary(claims)
        self.assertEqual(summary["claims"], 2)
        self.assertEqual(sum(summary["labels"].values()), 2)
        self.assertEqual(summary["quantified"], 2)
        self.assertEqual(summary["dated"], 1)


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------


class SynthesisTests(unittest.TestCase):
    def test_figures_carry_the_unit_that_followed_them(self):
        pairs = figures_with_units("Capacity reached 1200 megawatts in the reporting year.")
        self.assertIn(("1200", "megawatt"), pairs)

    def test_agreement_needs_two_documents_and_only_quotes_their_figures(self):
        claims = [
            make_claim("Installed capacity reached 1200 megawatts.", evidence_id="ev-a"),
            make_claim("Installed capacity reached 1200 megawatts nationally.", evidence_id="ev-b", source="Source B"),
        ]
        proposals = synthesise("topic-test", claims)
        agreements = [p for p in proposals if p.kind == "agreement"]
        self.assertTrue(agreements, "a figure in two documents should produce an agreement statement")
        proposal = agreements[0]
        verification = verify_synthesis(
            proposal.text, [c for c in claims if c.claim_id in proposal.cited_claim_ids], proposal.context_numbers
        )
        self.assertEqual(verification.verdict, "supported", verification.reasons)

    def test_one_document_is_never_a_cross_document_statement(self):
        claims = [
            make_claim("Installed capacity reached 1200 megawatts.", evidence_id="ev-a"),
            make_claim("Installed capacity reached 1200 megawatts.", claim_id="cl-dup", evidence_id="ev-a"),
        ]
        self.assertEqual(synthesise("topic-test", claims), [])

    def test_unverified_and_derived_claims_cannot_be_cited(self):
        claims = [
            make_claim("Installed capacity reached 1200 megawatts.", evidence_id="ev-a", verdict="unsupported"),
            make_claim(
                "This question is supported by 2 claims.",
                evidence_id="derived-topic-test",
                source="SelfLearn",
                kind="derived",
            ),
        ]
        self.assertEqual(synthesise("topic-test", claims), [])

    def test_a_figure_absent_from_the_citations_is_rejected(self):
        claims = [
            make_claim("Installed capacity reached 1200 megawatts.", evidence_id="ev-a"),
            make_claim("Installed capacity reached 900 megawatts.", evidence_id="ev-b", source="Source B"),
        ]
        verification = verify_synthesis(
            "The average installed capacity was 1050 megawatts across 2 documents.",
            claims,
            ["2"],
        )
        self.assertEqual(verification.verdict, "unsupported")
        self.assertIn("1050", verification.missing_numbers)

    def test_divergence_is_published_as_a_disagreement(self):
        claims = [
            make_claim("Reported throughput was 480 tokens per second.", evidence_id="ev-a"),
            make_claim("Reported throughput was 512 tokens per second.", evidence_id="ev-b", source="Source B"),
        ]
        proposals = synthesise("topic-test", claims)
        divergent = [p for p in proposals if p.kind == "divergence"]
        self.assertTrue(divergent)
        self.assertIn("disagree", divergent[0].text.casefold())

    def test_date_fragments_are_never_read_as_quantities(self):
        """Regression: '02' from 2026-08-02 was published as a reported value."""
        text = (
            "The record for khoj-ai/khoj reports: pushed_at 2026-08-02T01:55:40Z, "
            "stargazers_count 37459, forks_count 2490."
        )
        pairs = figures_with_units(text)
        numbers = [number for number, _unit in pairs]
        self.assertNotIn("02", numbers)
        self.assertNotIn("08", numbers)
        self.assertNotIn("55", numbers)
        self.assertIn("37459", numbers)

    def test_a_field_label_preceding_a_number_is_its_unit(self):
        text = "The record for x/y reports: stargazers_count 37459, forks_count 2490."
        pairs = dict((number, unit) for number, unit in figures_with_units(text))
        self.assertEqual(pairs["37459"], "stargazers_count")
        self.assertEqual(pairs["2490"], "forks_count")

    def test_one_operator_repeating_a_figure_is_not_agreement(self):
        claims = [
            make_claim("Reported yield was 92 percent in the first batch.", evidence_id="ev-a"),
            make_claim("Reported yield was 92 percent in the second batch.", evidence_id="ev-b"),
        ]
        agreements = [p for p in synthesise("topic-test", claims) if p.kind == "agreement"]
        self.assertEqual(agreements, [], "both claims come from one source, so this is not cross-source agreement")

    def test_two_unrelated_records_are_not_described_as_disagreeing(self):
        claims = [
            make_claim("The record for alpha reports: stargazers_count 37459.", evidence_id="ev-a"),
            make_claim("The record for beta reports: stargazers_count 27614.", evidence_id="ev-b", source="Source B"),
        ]
        divergent = [p for p in synthesise("topic-test", claims) if p.kind == "divergence"]
        self.assertEqual(divergent, [], "different subjects share no measured value, so there is nothing to disagree about")

    def test_the_same_subject_measured_differently_by_two_sources_is_a_divergence(self):
        claims = [
            make_claim("Reported cell efficiency was 21 percent for the tested module.", evidence_id="ev-a"),
            make_claim("Reported cell efficiency was 19 percent for the tested module.", evidence_id="ev-b", source="Source B"),
        ]
        divergent = [p for p in synthesise("topic-test", claims) if p.kind == "divergence"]
        self.assertTrue(divergent)
        self.assertEqual(verify_synthesis(
            divergent[0].text,
            [c for c in claims if c.claim_id in divergent[0].cited_claim_ids],
            divergent[0].context_numbers,
        ).verdict, "supported")

    def test_range_statement_uses_only_figures_from_the_sources(self):
        claims = [
            make_claim("Cost per kilowatt-hour was 120 dollars.", evidence_id="ev-a"),
            make_claim("Cost per kilowatt-hour was 145 dollars.", evidence_id="ev-b", source="Source B"),
        ]
        ranges = [p for p in synthesise("topic-test", claims) if p.kind == "range"]
        self.assertTrue(ranges)
        for proposal in ranges:
            cited = [c for c in claims if c.claim_id in proposal.cited_claim_ids]
            self.assertEqual(verify_synthesis(proposal.text, cited, proposal.context_numbers).verdict, "supported")


# ---------------------------------------------------------------------------
# Derived library statistics and snapshot replay
# ---------------------------------------------------------------------------


class DerivedStatisticsTests(unittest.TestCase):
    """The figures must describe the evidence, never the library talking about itself."""

    def test_volume_counts_only_current_direct_claims(self) -> None:
        from selflearn.learn.aggregate import derive_library_claims

        topic = Topic(topic_id="topic-agg", title="T", slug="t", question="Q?", keywords=["q"])
        direct = [
            make_claim("Capacity faded 18% over 400 cycles."),
            make_claim("The cell swells above 40 C."),
            make_claim("Throughput settled at 95 units per hour."),
        ]
        self_stat = make_claim(
            "This question is currently supported by 3 verified claim(s).", kind="derived"
        )
        retired_direct = make_claim("An older direct statement that a later cycle retired.")
        retired_direct.superseded = "Superseded for the test."
        proposals = derive_library_claims(topic, direct + [self_stat, retired_direct], [])
        volume = next(p for p, _ in proposals if p.label == "library_volume")
        self.assertIn("3 verified claim(s)", volume.text, "the count must exclude derived and retired claims")
        self.assertNotIn("5 verified claim(s)", volume.text)

    def test_retrieval_mode_never_claims_this_cycle(self) -> None:
        from selflearn.learn.aggregate import derive_library_claims

        topic = Topic(topic_id="topic-agg", title="T", slug="t", question="Q?", keywords=["q"])
        direct = [
            make_claim("Capacity faded 18% over 400 cycles."),
            make_claim("The cell swells above 40 C."),
            make_claim("Throughput settled at 95 units per hour."),
        ]
        live = make_record("ev-live", "Live doc", "Fetched from the source.")
        fixture = make_record("ev-fix", "Fixture doc", "Synthetic.")
        fixture.is_fixture = True
        fixture.is_live = False
        proposals = derive_library_claims(topic, direct, [live, fixture])
        mode = next(p for p, _ in proposals if p.label == "retrieval_mode")
        self.assertNotIn("in this cycle", mode.text, "records cited here were fetched across cycles")
        self.assertIn("retrieved live from their source", mode.text)
        self.assertIn("1", mode.context_numbers)
        self.assertIn("1", mode.context_numbers)


class SnapshotReplayTests(unittest.TestCase):
    """Replaying a stored snapshot must not downgrade the original provenance."""

    def test_replay_preserves_original_live_flag(self) -> None:
        import json as jsonlib

        from selflearn.fetch.collector import Collector
        from selflearn.fetch.net import HttpClient
        from selflearn.fetch.sources import Request

        topic = Topic(topic_id="topic-replay", title="T", slug="t", question="Q?", keywords=["q"])
        with tempfile.TemporaryDirectory() as tmp:
            snap = Path(tmp)
            (snap / "ev-replay-live.json").write_text(
                jsonlib.dumps(
                    {
                        "evidence_id": "ev-replay-live",
                        "source_id": "github",
                        "source_name": "GitHub",
                        "url": "https://example.org/a",
                        "title": "Live record",
                        "text": "Fetched live in an earlier cycle.",
                        "content_hash": sha256_text("Fetched live in an earlier cycle."),
                        "evidence_class": "primary_source",
                        "evidence_rank": 3,
                        "retrieved_at": "2026-09-01T00:00:00Z",
                        "is_fixture": False,
                        "is_live": True,
                    }
                ),
                encoding="utf-8",
            )
            (snap / "ev-replay-fixture.json").write_text(
                jsonlib.dumps(
                    {
                        "evidence_id": "ev-replay-fixture",
                        "source_id": "github",
                        "source_name": "GitHub",
                        "url": "https://example.org/b",
                        "title": "Fixture record",
                        "text": "Synthetic fixture text.",
                        "content_hash": sha256_text("Synthetic fixture text."),
                        "evidence_class": "unverified_claim",
                        "evidence_rank": 8,
                        "retrieved_at": "2026-09-01T00:00:00Z",
                        "is_fixture": True,
                        "is_live": False,
                    }
                ),
                encoding="utf-8",
            )
            collector = Collector(HttpClient(allow_network=False), snap)
            request = Request(url="https://api.github.com/search", params={"q": "q"}, label="github:test")
            rows = collector._replay(topic, "github", request, "query: q")
            by_id = {row.evidence_id: row for row in rows}
            self.assertTrue(by_id["ev-replay-live"].is_live, "a live document stays live across replays")
            self.assertFalse(by_id["ev-replay-fixture"].is_live)
            self.assertTrue(by_id["ev-replay-live"].is_fixture is False)
            self.assertIn("replayed from stored snapshot", by_id["ev-replay-live"].notes)


# ---------------------------------------------------------------------------
# Change scanning
# ---------------------------------------------------------------------------


class ChangeScanTests(unittest.TestCase):
    def test_every_mechanism_names_a_documented_filter_and_its_source(self):
        for source_id, mechanism in MECHANISMS.items():
            self.assertIn(source_id, REGISTRY, "a change mechanism must belong to a registered source")
            self.assertTrue(mechanism.docs_url.startswith("https://"), source_id)
            self.assertTrue(mechanism.label, source_id)

    def test_crossref_uses_the_documented_index_date_filter(self):
        request = change_request("crossref", "batteries", since="2026-09-01", until="2026-09-08")
        self.assertTrue(request.url.endswith("/works"))
        self.assertIn("from-index-date:2026-09-01", request.params["filter"])

    def test_arxiv_sorts_newest_first(self):
        request = change_request("arxiv", "batteries", since="2026-09-01", until="2026-09-08")
        self.assertEqual(request.params["sortBy"], "submittedDate")
        self.assertEqual(request.params["sortOrder"], "descending")

    def test_github_uses_the_pushed_qualifier(self):
        request = change_request("github", "batteries", since="2026-09-01", until="2026-09-08")
        self.assertIn("pushed:>=2026-09-01", request.params["q"])

    def test_nvd_sends_both_ends_of_the_window_in_the_documented_iso_format(self):
        request = change_request("nvd", "openssl", since="2026-09-01", until="2026-09-08")
        # API 2.0 requires the extended ISO-8601 datetime format; the API 1.0
        # nonstandard form (yyyy-MM-ddTHH:mm:ss:SSS UTC-00:00) answers HTTP 404
        # with "Invalid ISO 8601 date/time format". Observed live 2026-09-22.
        self.assertEqual(request.params["lastModStartDate"], "2026-09-01T00:00:00.000+00:00")
        self.assertEqual(request.params["lastModEndDate"], "2026-09-08T00:00:00.000+00:00")
        self.assertNotIn("UTC-", request.params["lastModStartDate"])

    def test_usgs_uses_iso_time_boundaries(self):
        request = change_request("usgs_earthquake", "earthquake", since="2026-09-01", until="2026-09-08")
        self.assertEqual(request.params["starttime"], "2026-09-01")
        self.assertEqual(request.params["endtime"], "2026-09-08")
        self.assertEqual(request.params["format"], "geojson")

    def test_window_never_exceeds_the_nvd_limit(self):
        since, until, days = scan_window("2020-01-01T00:00:00Z", max_days=7)
        self.assertLessEqual(days, 119)
        self.assertLessEqual(since, until)

    def test_first_scan_is_labelled_as_a_look_back_not_a_real_interval(self):
        since, _until, days = scan_window(None, max_days=7)
        self.assertEqual(days, 7)
        self.assertTrue(since)

    def test_offline_scan_records_the_window_without_polling(self):
        with __import__("tempfile").TemporaryDirectory() as tmp:
            scanner = ChangeScanner(HttpClient(allow_network=False), Path(tmp) / "change_scan.json", allow_network=False)
            outcome = scanner.scan("batteries")
            self.assertEqual(len(outcome.scans), len(MECHANISMS))
            self.assertTrue(all(scan.status == "not_attempted" for scan in outcome.scans))
            self.assertEqual(outcome.items_new, 0)
            for scan in outcome.scans:
                self.assertIn("since", scan.window)

    def test_a_second_scan_does_not_report_the_same_item_twice(self):
        """The seen-index must stop the same record being announced as new again."""
        class StubClient(HttpClient):
            def __init__(self):
                super().__init__(allow_network=True, max_requests=10)
                self.calls = 0

            def get(self, url, params=None, headers=None):  # type: ignore[override]
                self.calls += 1
                return http_result(url, ODP_BULK_SAMPLE)

        with __import__("tempfile").TemporaryDirectory() as tmp:
            state = Path(tmp) / "change_scan.json"
            # patentsview is not in MECHANISMS, so drive the dedup path through the
            # scanner's own state helpers, which is what the scan loop calls.
            scanner = ChangeScanner(StubClient(), state, allow_network=True)
            identifiers = ["patentsview:PVGPTXT"]
            self.assertEqual(scanner._seen_ids("patentsview"), set())
            scanner._remember("patentsview", identifiers, "2026-09-21T00:00:00Z", "scanned", 1)
            scanner.save()
            reloaded = ChangeScanner(StubClient(), state, allow_network=True)
            self.assertEqual(reloaded._seen_ids("patentsview"), set(identifiers))
            self.assertEqual(reloaded._last_scan("patentsview"), "2026-09-21T00:00:00Z")

    def test_mechanism_table_is_publishable(self):
        rows = mechanism_table()
        self.assertEqual(len(rows), len(MECHANISMS))
        for row in rows:
            self.assertTrue(row["endpoint"].startswith("https://"))
            self.assertTrue(row["docs_url"].startswith("https://"))


# ---------------------------------------------------------------------------
# Topic invention
# ---------------------------------------------------------------------------


class InventionTests(unittest.TestCase):
    def _pool(self):
        records = [
            make_record(
                "ev-1",
                "Solid state electrolyte interfaces",
                "Interfacial resistance in solid state electrolyte cells dominates the impedance at low temperature.",
            ),
            make_record(
                "ev-2",
                "Solid state electrolyte scaling",
                "Manufacturing yield for solid state electrolyte stacks falls as area increases.",
            ),
            make_record("ev-3", "Unrelated note", "A short note about nothing in particular."),
        ]
        claims = [
            make_claim(
                "Interfacial resistance reached 240 ohms at 20 C in the tested cells.",
                evidence_id="ev-1",
            ),
            make_claim("Manufacturing yield fell 18% as stack area doubled.", evidence_id="ev-2", source="Source B"),
        ]
        topics = [Topic(topic_id="topic-batteries", title="Battery degradation", slug="battery-degradation", question="How fast do cells degrade?")]
        return records, claims, topics

    def test_recurring_phrases_become_candidates_and_singletons_do_not(self):
        records, _claims, _topics = self._pool()
        phrases = {candidate.phrase for candidate in candidate_phrases(records)}
        self.assertIn("solid state electrolyte", phrases)
        self.assertNotIn("impedance", phrases)

    def test_the_engine_scaffolding_never_becomes_a_candidate(self):
        """Regression: the adapters write the same provenance lines into every
        document, so those phrases used to be proposed as novel topics."""
        scaffolding = (
            "Source: GitHub REST API (https://api.github.com)\n"
            "Every sentence below names the record it describes. Values are copied from the response without change; "
            "field labels are the adapter's own rendering of the response's field names.\n"
            "Record: alpha\n"
            "The record for alpha reports: language Python, stars 400.\n"
            "Source note: Repository activity is an adoption signal, not proof of correctness."
        )
        records = [
            make_record("ev-s1", "alpha", scaffolding),
            make_record("ev-s2", "beta", scaffolding.replace("alpha", "beta")),
        ]
        phrases = {candidate.phrase for candidate in candidate_phrases(records)}
        self.assertNotIn("sentence below names", phrases)
        self.assertNotIn("every sentence below", phrases)
        self.assertNotIn("adoption signal", phrases)
        self.assertEqual(phrases, set(), "scaffolding-only documents should yield no candidates")

    def test_novelty_is_measured_against_the_library_not_the_world(self):
        records, claims, topics = self._pool()
        known = library_vocabulary(claims, topics)
        self.assertIn("degrade", known | {"degrade"})
        candidate = next(c for c in candidate_phrases(records) if c.phrase == "solid state electrolyte")
        records_index = {r.evidence_id: r for r in records}
        proposal = score_proposal(candidate, known=known, records=records_index, claims=claims)
        self.assertGreater(proposal.novelty, 0.0)
        self.assertLessEqual(proposal.novelty, 1.0)
        self.assertEqual(proposal.support_documents, 2)

    def test_a_phrase_made_only_of_known_words_is_not_novel(self):
        records, claims, topics = self._pool()
        known = library_vocabulary(claims, topics) | {"solid", "state", "electrolyte"}
        candidate = next(c for c in candidate_phrases(records) if c.phrase == "solid state electrolyte")
        proposal = score_proposal(
            candidate, known=known, records={r.evidence_id: r for r in records}, claims=claims
        )
        self.assertEqual(proposal.novelty, 0.0)
        self.assertFalse(proposal.accepted)

    def test_promotion_needs_documents_novelty_and_a_score(self):
        records, claims, topics = self._pool()
        proposals = propose_topics(
            records=records, claims=claims, topics=topics, existing_titles=[t.title for t in topics]
        )
        for proposal in proposals:
            if proposal.accepted:
                self.assertGreaterEqual(proposal.novelty, MIN_NOVELTY)
                self.assertGreaterEqual(proposal.support_documents, 2)
                self.assertTrue(proposal.reason)

    def test_an_accepted_proposal_carries_its_provenance_into_the_topic(self):
        records, claims, topics = self._pool()
        proposals = propose_topics(records=records, claims=claims, topics=topics)
        accepted = [p for p in proposals if p.accepted]
        if not accepted:
            self.skipTest("this pool produced no accepted proposal; the gates are asserted above")
        topic = to_topic(accepted[0])
        self.assertEqual(topic.origin, "discovery")
        self.assertEqual(topic.status, "new")
        self.assertIn("novel to this library", topic.signal["provenance"])
        self.assertIn("novelty", topic.signal["proposal"])


# ---------------------------------------------------------------------------
# USPTO Open Data Portal adapter (the PatentsView replacement)
# ---------------------------------------------------------------------------


ODP_BULK_SAMPLE = {
    "count": 1,
    "bulkDataProductBag": [
        [
            {
                "productIdentifier": "PVGPTXT",
                "productDescriptionText": "PatentsView granted patent long text tables.",
                "productTitleText": "PatentsView Granted Patent Text",
                "productFrequencyText": "WEEKLY",
                "productFromDate": "2001-01-01",
                "productToDate": "2026-12-31",
                "productTotalFileSize": 32511973080,
                "productFileTotalQuantity": 3,
                "lastModifiedDateTime": "2026-09-01T15:52:00.000Z",
                "mimeTypeIdentifierArrayText": [["JSON"]],
                "productFileBag": {
                    "count": 1,
                    "fileDataBag": [
                        {
                            "fileName": "2020-2026-patentsview-text.zip",
                            "fileSize": 1698377311,
                            "fileDownloadURI": "https://api.uspto.gov/api/v1/datasets/products/files/PVGPTXT/2020-2026-patentsview-text.zip",
                            "fileReleaseDate": "2026-09-01 08:01:00",
                        }
                    ],
                },
            }
        ]
    ],
}


class UsptoOdpAdapterTests(unittest.TestCase):
    def setUp(self):
        os.environ["USPTO_ODP_API_KEY"] = "TEST-KEY"
        self.addCleanup(os.environ.pop, "USPTO_ODP_API_KEY", None)
        self.source = build_source("patentsview")

    def test_register_points_at_the_open_data_portal_not_the_retired_host(self):
        spec = get_source("patentsview")
        self.assertEqual(spec.base_url, "https://api.uspto.gov/api/v1")
        self.assertNotIn("search.patentsview.org", spec.base_url)
        self.assertEqual(spec.key_env, "USPTO_ODP_API_KEY")
        self.assertIn("transition-guide/patentsview", spec.notes)

    def test_requests_use_the_documented_endpoints_and_key_header(self):
        requests = self.source.requests("battery separator")
        paths = [request.url for request in requests]
        self.assertIn("https://api.uspto.gov/api/v1/patent/applications/search", paths)
        self.assertIn("https://api.uspto.gov/api/v1/datasets/products/search", paths)
        for request in requests:
            self.assertEqual(request.headers["X-API-KEY"], "TEST-KEY")
        self.assertEqual(requests[0].params["q"], "battery separator")
        self.assertEqual(requests[1].params["productTitle"], "battery separator")

    def test_bulk_product_response_is_parsed_field_by_field(self):
        request = self.source.requests("patent")[1]
        result = http_result(request.url, ODP_BULK_SAMPLE)
        items = self.source.parse(request, result)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.identifier, "PVGPTXT")
        self.assertEqual(item.title, "PatentsView Granted Patent Text")
        self.assertIn("32511973080", item.text)
        self.assertIn("2020-2026-patentsview-text.zip", item.text)
        self.assertTrue(item.url.startswith("https://api.uspto.gov/api/v1/datasets/products/files/"))
        # Every sentence must name its record, or a claim cut from it would read
        # as an assertion the engine never made.
        for line in item.text.splitlines():
            if line.startswith("The record for"):
                self.assertIn("PatentsView Granted Patent Text", line)

    def test_an_unknown_response_shape_is_stored_verbatim_not_guessed(self):
        request = self.source.requests("patent")[0]
        result = http_result(request.url, {"someUnmodelledEnvelope": {"rows": [{"a": 1}]}})
        items = self.source.parse(request, result)
        self.assertEqual(len(items), 1)
        self.assertIn("someUnmodelledEnvelope", items[0].text)
        self.assertTrue(items[0].extra.get("raw"))

    def test_identifiers_are_stable_across_processes(self):
        request = self.source.requests("patent")[0]
        result = http_result(request.url, {"envelope": "value"})
        items = self.source.parse(request, result)
        self.assertEqual(items[0].identifier, self.source.parse(request, result)[0].identifier)
        # A content hash, not a salted hash() of the URL.
        self.assertIn(sha256_text(items[0].text)[:16], items[0].identifier)


class CredentialPathTests(unittest.TestCase):
    """A configured credential has to reach the request, not just the register.

    These tests exist because the register used to name a ``key_env`` for sources
    whose adapter sent no credential at all, so a reviewer who set the secret was
    told it was enabled while every request still went out unauthenticated.
    """

    def set_env(self, name: str, value: str) -> None:
        previous = os.environ.get(name)
        os.environ[name] = value
        self.addCleanup(lambda: os.environ.__setitem__(name, previous) if previous is not None else os.environ.pop(name, None))

    def test_a_query_parameter_credential_is_added_to_the_request(self):
        for source_id, env in (("eia", "EIA_API_KEY"), ("fred", "FRED_API_KEY")):
            with self.subTest(source=source_id):
                self.set_env(env, "TEST-KEY")
                request = build_source(source_id).requests("energy")[0]
                self.assertEqual(request.params.get("api_key"), "TEST-KEY")

    def test_a_header_credential_is_added_as_a_header_not_a_parameter(self):
        self.set_env("NCEI_TOKEN", "TEST-TOKEN")
        request = build_source("ncei").requests("climate")[0]
        self.assertEqual(request.headers.get("token"), "TEST-TOKEN")
        self.assertNotIn("token", request.params)

    def test_a_bearer_credential_carries_the_documented_scheme_prefix(self):
        self.set_env("GITHUB_TOKEN", "TEST-TOKEN")
        request = build_source("github").requests("agents")[0]
        self.assertEqual(request.headers.get("Authorization"), "Bearer TEST-TOKEN")

    def test_an_absent_credential_leaves_the_request_untouched(self):
        os.environ.pop("EIA_API_KEY", None)
        request = build_source("eia").requests("energy")[0]
        self.assertNotIn("api_key", request.params)

    def test_every_documented_mechanism_cites_the_operators_own_page(self):
        for source_id, mechanism in CREDENTIAL_MECHANISMS.items():
            with self.subTest(source=source_id):
                self.assertIn(mechanism.kind, ("query", "header"))
                self.assertTrue(mechanism.name)
                self.assertTrue(mechanism.docs_url.startswith("https://"))
                # A transcription nobody can check is not a citation.
                if mechanism.applied_by == "shared":
                    self.assertTrue(mechanism.quote, f"{source_id} has no quoted operator text")
                    self.assertTrue(mechanism.verified_at, f"{source_id} has no verification date")
                self.assertTrue(
                    REGISTRY[source_id].key_env,
                    f"{source_id} documents a credential mechanism but names no environment variable",
                )

    def test_a_credential_the_adapter_does_not_send_is_reported_as_such(self):
        """The honest branch still exists, for a spec with no transcribed mechanism.

        Every registered keyed source now has one (see the test below); this
        exercises the reporting path itself with a synthetic source id, because
        a future registration without a transcription must not be silently
        described as transmitting.
        """
        import dataclasses

        synthetic = dataclasses.replace(get_source("eia"), source_id="untranscribed_source")
        status = credential_status(synthetic)
        self.assertEqual(status["state"], "declared_only")
        self.assertIn("has not been transcribed", status["detail"])

    def test_every_keyed_source_in_the_register_transmits_its_credential(self):
        """No variable may be named in the register without a transcribed mechanism."""
        untransmitted = [
            spec.source_id
            for spec in REGISTRY.values()
            if spec.key_env and credential_status(spec)["state"] != "applied"
        ]
        self.assertEqual(
            untransmitted, [],
            f"these sources name a credential the engine does not send: {untransmitted}",
        )

    def test_optional_query_credentials_reach_the_request(self):
        for source_id, env, param in (
            ("census_us", "CENSUS_API_KEY", "key"),
            ("pubmed", "NCBI_API_KEY", "api_key"),
            ("doaj", "DOAJ_API_KEY", "api_key"),
        ):
            with self.subTest(source=source_id):
                self.set_env(env, "TEST-KEY")
                request = build_source(source_id).requests("population")[0]
                self.assertEqual(request.params.get(param), "TEST-KEY")

    def test_optional_header_credentials_reach_the_request_as_headers(self):
        for source_id, env, header in (
            ("nvd", "NVD_API_KEY", "apiKey"),
            ("semantic_scholar", "S2_API_KEY", "x-api-key"),
        ):
            with self.subTest(source=source_id):
                self.set_env(env, "TEST-KEY")
                request = build_source(source_id).requests("cve")[0]
                self.assertEqual(request.headers.get(header), "TEST-KEY")
                self.assertNotIn(header, request.params)

    def test_stackexchange_sends_the_bearer_authorization_header(self):
        """The operator documents Authorization: Bearer for API keys (read 2026-09-22)."""
        self.set_env("STACKEXCHANGE_KEY", "TEST-KEY")
        request = build_source("stackexchange").requests("python")[0]
        self.assertEqual(request.headers.get("Authorization"), "Bearer TEST-KEY")
        self.assertNotIn("key", request.params)

    def test_pubmed_stages_both_carry_the_key(self):
        """A two-stage adapter must authenticate every stage, not only the first."""
        self.set_env("NCBI_API_KEY", "TEST-KEY")
        adapter = build_source("pubmed")
        search = adapter.requests("vaccine")[0]
        self.assertEqual(search.params.get("api_key"), "TEST-KEY")
        sample = HttpResult(
            url=search.url, status=200, headers={}, content_type="application/json",
            body=json.dumps({"esearchresult": {"idlist": ["1", "2"]}}).encode(),
            retrieved_at="2026-09-22T00:00:00Z", attempts=1,
        )
        follow = adapter.follow_up(sample)[0]
        self.assertEqual(follow.params.get("api_key"), "TEST-KEY")


class ReviewerResolutionTests(unittest.TestCase):
    """tools/resolve_finding.py: a finding is closed by appending, never by editing."""

    def _library(self, root):
        from selflearn.learn.store import Library
        from selflearn.models import Contradiction, Irregularity

        library = Library.load(root, run_id="test-1")
        library.add_irregularities([
            Irregularity(irregularity_id="irr-test0001", severity="warning", stage="audit", topic_id=None,
                         summary="A finding", detail="Original detail")
        ])
        library.add_contradictions([
            Contradiction(contradiction_id="con-test0001", topic_id="topic-x", claim_a="cl-a", claim_b="cl-b",
                          kind="numeric", detail="Disjoint numbers", severity="medium")
        ])
        return library

    def _tool(self):
        import contextlib
        import importlib.util
        import io

        spec = importlib.util.spec_from_file_location("resolve_finding", ROOT / "tools" / "resolve_finding.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        real_main = module.main

        def quiet_main(argv):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return real_main(argv)

        module.main = quiet_main
        return module

    def test_resolving_an_irregularity_appends_and_keeps_the_original_text(self):
        import tempfile
        from selflearn.learn.store import Library

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._library(root)
            tool = self._tool()
            self.assertEqual(tool.main(["--root", tmp, "--id", "irr-test0001", "--reason", "Checked by hand", "--link", "https://example.org/x"]), 0)
            reloaded = Library.load(root, run_id="test-2")
            finding = reloaded.irregularities["irr-test0001"]
            self.assertTrue(finding.resolved)
            self.assertEqual(finding.resolution, "Checked by hand")
            self.assertEqual(finding.resolution_link, "https://example.org/x")
            self.assertTrue(finding.resolved_at)
            self.assertEqual(finding.summary, "A finding")
            self.assertEqual(finding.detail, "Original detail")
            lines = (root / "library" / "irregularities.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2, "the original row stays; the resolution is a second row")

    def test_resolving_twice_is_refused_and_reopen_is_explicit(self):
        import tempfile
        from selflearn.learn.store import Library

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._library(root)
            tool = self._tool()
            self.assertEqual(tool.main(["--root", tmp, "--id", "irr-test0001", "--reason", "first"]), 0)
            self.assertEqual(tool.main(["--root", tmp, "--id", "irr-test0001", "--reason", "second"]), 1)
            self.assertEqual(tool.main(["--root", tmp, "--id", "irr-test0001", "--reopen", "--reason", "was wrong"]), 0)
            finding = Library.load(root, run_id="t").irregularities["irr-test0001"]
            self.assertFalse(finding.resolved)
            self.assertIn("Reopened", finding.resolution)

    def test_a_reviewers_decision_survives_the_engine_redetecting_the_finding(self):
        import tempfile
        from selflearn.learn.store import Library
        from selflearn.models import Contradiction, Irregularity

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._library(root)
            tool = self._tool()
            tool.main(["--root", tmp, "--id", "irr-test0001", "--reason", "closed"])
            tool.main(["--root", tmp, "--id", "con-test0001", "--reason", "same period, different unit"])
            # A later cycle raises both again, exactly as the detectors emit them.
            library = Library.load(root, run_id="cycle-2")
            library.add_irregularities([
                Irregularity(irregularity_id="irr-test0001", severity="warning", stage="audit", topic_id=None,
                             summary="A finding", detail="Original detail")
            ])
            library.add_contradictions([
                Contradiction(contradiction_id="con-test0001", topic_id="topic-x", claim_a="cl-a", claim_b="cl-b",
                              kind="numeric", detail="Disjoint numbers", severity="medium")
            ])
            reloaded = Library.load(root, run_id="cycle-3")
            self.assertTrue(reloaded.irregularities["irr-test0001"].resolved)
            self.assertEqual(reloaded.irregularities["irr-test0001"].resolution, "closed")
            self.assertEqual(reloaded.contradictions["con-test0001"].resolution, "resolved")
            self.assertEqual(reloaded.contradictions["con-test0001"].resolution_note, "same period, different unit")

    def test_the_review_page_shows_resolved_findings_with_their_reason(self):
        from selflearn.publish.site import page_review

        data = {
            "irregularities": [
                {"irregularity_id": "irr-open", "severity": "warning", "stage": "audit", "summary": "Still open", "detail": "", "resolved": False},
                {"irregularity_id": "irr-done", "severity": "warning", "stage": "audit", "summary": "Was closed", "detail": "d",
                 "resolved": True, "resolution": "Reviewer reason text", "resolved_at": "2026-09-22T00:00:00Z", "resolution_link": ""},
            ],
            "failures": [],
            "contradictions": [
                {"contradiction_id": "con-done", "topic_id": "t", "kind": "numeric", "detail": "x", "claim_a": "a", "claim_b": "b",
                 "resolution": "resolved", "resolution_note": "Contradiction reason", "resolved_at": "2026-09-22T00:00:00Z"},
            ],
            "checks": {"irregularity_counts": {"error": 0, "warning": 1}, "unresolved_contradictions": 0},
            "calibration": {},
            "counts": {}, "run_summary": {}, "topics": [],
        }
        html = page_review(data)
        self.assertIn("Reviewer reason text", html)
        self.assertIn("Contradiction reason", html)
        self.assertIn("Was closed", html)
        self.assertIn("Still open", html)
        open_table = html.split('id="resolved"')[0]
        self.assertNotIn("Was closed", open_table.split('id="irregularities"')[1].split("</section>")[0])

    def test_an_unknown_prefix_and_a_missing_reason_are_rejected(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            self._library(Path(tmp))
            tool = self._tool()
            self.assertEqual(tool.main(["--root", tmp, "--id", "xyz-1", "--reason", "r"]), 2)
            self.assertEqual(tool.main(["--root", tmp, "--id", "irr-test0001"]), 2)
            self.assertEqual(tool.main(["--root", tmp, "--id", "irr-missing", "--reason", "r"]), 1)


class FindingMergeTests(unittest.TestCase):
    """The report, the JSON export and the store must not disagree about findings.

    These tests exist because `selflearn audit` used to overwrite
    reports/irregularities.md with only the fresh audit rows - one info line
    where the review page showed eighteen warnings - and because a plain
    last-wins dedupe drops a reviewer's resolution as soon as the engine
    re-detects the same finding.
    """

    def _stored(self):
        from selflearn.models import Irregularity

        return Irregularity(
            irregularity_id="irr-merge0001", severity="warning", stage="change_scan",
            topic_id=None, summary="A source was unreachable", detail="TLS closed",
            resolved=True, resolved_at="2026-09-22T10:00:00Z",
            resolution="Checked by hand", resolution_link="https://example.org/note",
        )

    def _fresh(self):
        from selflearn.models import Irregularity

        return Irregularity(
            irregularity_id="irr-merge0001", severity="warning", stage="change_scan",
            topic_id=None, summary="A source was unreachable", detail="TLS closed",
        )

    def test_re_detection_does_not_erase_a_reviewers_resolution(self):
        from selflearn.verify.audit import merge_findings

        rows = merge_findings([self._stored(), self._fresh()])
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].resolved)
        self.assertEqual(rows[0].resolution, "Checked by hand")

    def test_render_markdown_counts_the_merged_row_once_and_keeps_the_reason(self):
        from selflearn.verify.audit import render_markdown, summarise, merge_findings

        merged = merge_findings([self._stored(), self._fresh(), self._fresh()])
        self.assertEqual(summarise(merged)["total"], 1)
        text = render_markdown([self._stored(), self._fresh()], generated_at="2026-09-22T00:00:00Z")
        self.assertIn("resolved by a reviewer: 1", text)
        self.assertIn("Checked by hand", text)
        self.assertEqual(text.count("### [WARNING] A source was unreachable"), 1)

    def test_published_check_counts_come_from_the_deduplicated_rows(self):
        from selflearn.learn.store import Library
        from selflearn.publish.report import build_site_data

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = Library.load(root, run_id="merge-test")
            data = build_site_data(
                library,
                source_matrix=[],
                source_status=[],
                irregularities=[self._stored(), self._fresh()],
                failures=[],
                elo_payload={"leaderboard": []},
                calibration={},
                requirements=[],
                methodology={},
                mode="live",
                run_summary={},
            )
            self.assertEqual(len(data["irregularities"]), 1, "one row per id")
            self.assertTrue(data["irregularities"][0]["resolved"])
            # The raw list held two rows for one id; counting it directly would
            # have reported one open warning plus one resolved, i.e. two.
            self.assertEqual(data["checks"]["irregularity_counts"]["warning"], 0)
            self.assertEqual(data["checks"]["resolved_irregularities"], 1)


class VectorIndexTests(unittest.TestCase):
    """The TF-IDF index is deterministic, dependency-free and actually used."""

    def _claims(self):
        from selflearn.models import Claim, Verification

        def make(i, text):
            return Claim(
                claim_id=f"cl-vec{i}", topic_id="topic-a", text=text,
                evidence_id="ev-vec", url="https://example.org/doc", quote="",
                evidence_class="primary_source", evidence_rank=3, source_name="S",
                verification=Verification(verdict="supported", coverage=1.0),
            )

        return [
            make(1, "Sorting networks reduce comparison counts for fixed-size inputs."),
            make(2, "Comparison sorting requires n log n comparisons in the average case."),
            make(3, "Repository star counts indicate popularity of the project."),
        ]

    def test_search_is_deterministic_and_ranks_shared_vocabulary_first(self):
        from selflearn.learn.vector_index import VectorIndex

        claims = self._claims()
        first = VectorIndex.build(claims).search("comparison sorting counts", k=3)
        second = VectorIndex.build(list(reversed(claims))).search("comparison sorting counts", k=3)
        self.assertEqual(first, second, "build order must not affect results")
        self.assertEqual(first[0][0], "cl-vec1")
        for claim_id, score in first:
            self.assertGreater(score, 0.0)
        self.assertTrue(all(a[1] >= b[1] for a, b in zip(first, first[1:])), "scores descending")

    def test_a_query_with_no_indexed_terms_returns_nothing(self):
        from selflearn.learn.vector_index import VectorIndex

        index = VectorIndex.build(self._claims())
        self.assertEqual(index.search("zeppelin xylophone quartzite"), [])

    def test_retired_claims_are_excluded_from_the_cli_index_pool(self):
        from selflearn.learn.vector_index import VectorIndex

        claims = self._claims()
        claims[0].superseded = "rule change"
        index = VectorIndex.build(c for c in claims if not c.superseded)
        self.assertNotIn("cl-vec1", index.doc_vectors)
        self.assertEqual(len(index.doc_vectors), 2)

    def test_cross_domain_claims_rank_with_the_vector_index(self):
        from selflearn.learn.vector_index import VectorIndex
        from selflearn.models import Topic
        from selflearn.think.competition import cross_domain_claims

        topic = Topic(
            topic_id="topic-a", title="Which sorting strategy scales?", slug="sorting",
            question="How do sorting strategies compare?", keywords=["sorting", "comparison"],
        )
        claims = self._claims()
        library = {"topic-b": claims}
        transferred = cross_domain_claims(topic, library, limit=2)
        self.assertLessEqual(len(transferred), 2)
        if transferred:
            index = VectorIndex.build(claims)
            query = index.query_vector(" ".join(topic.keywords) + " " + topic.title + " " + topic.question)
            expected_top = [
                claim_id for claim_id, _ in
                sorted(
                    ((c.claim_id, index.similarity(query, c.claim_id)) for c in claims),
                    key=lambda item: (-item[1], item[0]),
                )
            ][: len(transferred)]
            self.assertEqual([c.claim_id for c in transferred], expected_top)


class StorageMirrorTests(unittest.TestCase):
    """Roadmap item 8: the database mirror must round-trip the real library."""

    def _connection(self, tmp):
        from selflearn.storage import connect, ensure_schema

        connection = connect(f"sqlite:///{tmp}/mirror.db")
        self.addCleanup(connection.close)
        ensure_schema(connection)
        return connection

    def test_sync_then_verify_reports_identical_views(self):
        import shutil

        from selflearn.storage import connect, ensure_schema, sync_library, verify_views

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "library", root / "library")
            connection = self._connection(tmp)
            report = sync_library(root, connection)
            self.assertGreater(report["rows_inserted"], 0)
            self.assertEqual(
                report["rows_inserted"],
                sum(report["file_rows_by_stream"].values()),
                "every stored row must land in the database exactly once",
            )
            verdict = verify_views(root, connection)
            self.assertTrue(
                verdict["rows_identical"],
                f"rows differ: {[name for name, row in verdict['streams'].items() if not row['matches']]}",
            )
            self.assertTrue(
                verdict["library_identical"],
                f"decoded records differ: {verdict['library_mismatched_streams']}",
            )
            for row in verdict["streams"].values():
                self.assertTrue(row["matches"])

    def test_a_second_sync_adds_nothing_and_a_changed_row_wins_in_both_views(self):
        import shutil

        from selflearn.learn.store import Library
        from selflearn.storage import sync_library, verify_views

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "library", root / "library")
            connection = self._connection(tmp)
            sync_library(root, connection)
            again = sync_library(root, connection)
            self.assertEqual(again["rows_inserted"], 0, "sync must be idempotent")

            # A changed record is appended (never edited in place); both views
            # must show the newest write for that primary key.
            library = Library.load(root, run_id="storage-change")
            topic = next(iter(library.topics.values()))
            topic.status = "rejected"
            library.add_topics([topic])
            verdict = verify_views(root, connection)
            # The database only has the old row until the new file row is synced...
            self.assertFalse(verdict["rows_identical"], "a new file row is not yet in the database")
            sync_library(root, connection)
            verdict = verify_views(root, connection)
            self.assertTrue(verdict["rows_identical"], "after sync both row sets must agree again")
            self.assertTrue(
                verdict["library_identical"],
                f"after sync the decoded records must agree: {verdict['library_mismatched_streams']}",
            )

    def test_a_tampered_database_row_fails_both_checks(self):
        """A row edited in place (never in the files) must fail both views."""
        import shutil

        from selflearn.storage import sync_library, verify_views

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "library", root / "library")
            connection = self._connection(tmp)
            sync_library(root, connection)
            cursor = connection.cursor()
            # audit_log is appended in full (no dedupe), so any edit there is
            # guaranteed to break both the row comparison and the record view.
            cursor.execute("SELECT seq, payload FROM library_rows WHERE stream='audit' LIMIT 1")
            seq, payload = cursor.fetchone()
            row = json.loads(payload)
            row["event"] = str(row.get("event", "")) + " (tampered)"
            cursor.execute(
                "UPDATE library_rows SET payload = ? WHERE seq = ?",
                (json.dumps(row, ensure_ascii=False), seq),
            )
            connection.commit()
            verdict = verify_views(root, connection)
            self.assertFalse(verdict["rows_identical"], "an edited row must fail the row check")
            self.assertFalse(verdict["library_identical"], "an edited row must fail the record check")
            self.assertIn("audit", verdict["library_mismatched_streams"])

    def test_decoding_rows_that_predate_a_timestamp_field_is_deterministic(self):
        """Old rows omit created_at; decoding must not stamp the wall clock.

        The default_factory used to fire at decode time, so two Library.from_rows
        calls a second apart disagreed about created_at and storage verify flipped
        between identical and not on the same data.
        """
        from selflearn.learn.store import _dataclass
        from selflearn.models import Contradiction

        row = {
            "contradiction_id": "con-test",
            "topic_id": "topic-x",
            "claim_a": "claim-1",
            "claim_b": "claim-2",
            "kind": "numeric",
            "detail": "1 vs 2",
            "severity": "high",
        }
        first = _dataclass(Contradiction, dict(row))
        second = _dataclass(Contradiction, dict(row))
        self.assertEqual(first.created_at, "", "a missing stamp must decode to empty, not to now()")
        self.assertEqual(first.created_at, second.created_at, "two decodes of the same row must agree")

    def test_postgres_dsn_without_a_driver_fails_with_the_documented_message(self):
        import importlib.util

        from selflearn.storage import connect

        if importlib.util.find_spec("psycopg") or importlib.util.find_spec("psycopg2"):
            self.skipTest("a PostgreSQL driver is installed; the failure path cannot be exercised")
        with self.assertRaises(RuntimeError) as caught:
            connect("postgres://localhost/library")
        self.assertIn("optional PostgreSQL driver", str(caught.exception))
        self.assertIn("sqlite", str(caught.exception))

    def test_an_unsupported_dsn_is_rejected(self):
        from selflearn.storage import connect

        with self.assertRaises(ValueError):
            connect("mysql://localhost/library")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
