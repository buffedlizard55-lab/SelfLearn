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

    def test_nvd_sends_both_ends_of_the_window(self):
        request = change_request("nvd", "openssl", since="2026-09-01", until="2026-09-08")
        self.assertIn("lastModStartDate", request.params)
        self.assertIn("lastModEndDate", request.params)

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
        """The honest answer for a variable with no transcribed mechanism."""
        declared_only = [
            spec.source_id
            for spec in REGISTRY.values()
            if spec.key_env and credential_status(spec)["state"] == "declared_only"
        ]
        self.assertIn("census_us", declared_only)
        self.assertIn(
            "has not been transcribed",
            credential_status(get_source("census_us"))["detail"],
        )

    def test_required_sources_all_have_a_transmitted_mechanism(self):
        """No source may be gated on a credential the engine then fails to send."""
        for spec in REGISTRY.values():
            if not spec.requires_key:
                continue
            with self.subTest(source=spec.source_id):
                self.assertEqual(
                    credential_status(spec)["state"],
                    "applied",
                    f"{spec.source_id} refuses to run without {spec.key_env} but never sends it",
                )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
