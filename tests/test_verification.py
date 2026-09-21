"""Tests for the anti-hallucination core: grounding, verification, audit.

These are the tests that matter most. If one of them fails, a claim the engine
cannot support could reach the published site.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.config import FIXTURE_DIR, THRESHOLDS, VerificationThresholds  # noqa: E402
from selflearn.learn.calibration import evaluate, load_cases  # noqa: E402
from selflearn.models import Claim, EvidenceRecord, Verification  # noqa: E402
from selflearn.util import (  # noqa: E402
    coverage,
    extract_dates,
    extract_numbers,
    missing_numbers,
    normalize_for_match,
    sha256_text,
    split_sentences,
)
from selflearn.verify.audit import check_links, recheck_claims  # noqa: E402
from selflearn.verify.grounding import ground_evidence, proposal_from_sentence  # noqa: E402
from selflearn.verify.verifier import verify_claim, verify_derived  # noqa: E402

DOC = (
    "Source: National statistics release\n"
    "Title: Annual capacity report\n"
    "Installed grid-scale battery capacity reached 1200 megawatts in the reporting year. "
    "Capacity degradation is about 2% per year for cells held at moderate temperature. "
    "Battery cell prices fell sharply over the decade, and deployment of grid-scale storage grew steadily."
)


class NumberExtractionTests(unittest.TestCase):
    def test_canonicalises_thousands_separators_and_percent(self) -> None:
        self.assertEqual(extract_numbers("1,200 megawatts"), {"1200"})
        self.assertEqual(extract_numbers("12%"), {"12%"})
        self.assertEqual(extract_numbers("12 percent"), {"12%"})
        self.assertEqual(extract_numbers("12 pct"), {"12%"})
        self.assertEqual(extract_numbers("-3.50"), {"-3.5"})
        self.assertEqual(extract_numbers("007"), {"7"})

    def test_missing_numbers_detects_fabrication(self) -> None:
        self.assertEqual(missing_numbers("degradation is 42% per year", DOC), {"42%"})
        self.assertEqual(missing_numbers("degradation is 2% per year", DOC), set())

    def test_dates(self) -> None:
        self.assertEqual(extract_dates("published 2026-09-21"), {"2026-09-21"})

    def test_unicode_normalisation(self) -> None:
        self.assertEqual(normalize_for_match("\u201cA  B\u201d"), '"a b"')

    def test_split_sentences_keeps_abbreviation_free_text_intact(self) -> None:
        sentences = split_sentences("One thing. Two things! Three things?")
        self.assertEqual(len(sentences), 3)


class VerificationTests(unittest.TestCase):
    def test_verbatim_quote_is_supported(self) -> None:
        claim = "Installed grid-scale battery capacity reached 1200 megawatts in the reporting year."
        result = verify_claim(claim, claim, DOC)
        self.assertEqual(result.verdict, "supported")
        self.assertTrue(result.quote_match)

    def test_fabricated_number_is_unsupported_even_with_good_wording(self) -> None:
        claim = "Installed grid-scale battery capacity reached 4200 megawatts in the reporting year."
        result = verify_claim(claim, "", DOC)
        self.assertEqual(result.verdict, "unsupported")
        self.assertIn("4200", result.missing_numbers)

    def test_quote_does_not_override_a_fabricated_number(self) -> None:
        claim = "Capacity degradation is 42% per year for cells."
        quote = "Capacity degradation is"
        result = verify_claim(claim, quote, DOC)
        self.assertEqual(result.verdict, "unsupported")

    def test_wrong_year_is_unsupported(self) -> None:
        result = verify_claim("The dataset was published in 1998.", "", DOC)
        self.assertEqual(result.verdict, "unsupported")

    def test_negation_in_document_blocks_support(self) -> None:
        result = verify_claim(
            "The intervention reduced infection rates in the treated group.",
            "",
            "The intervention did not reduce infection rates in the treated group; the difference was within noise.",
        )
        self.assertEqual(result.verdict, "unsupported")

    def test_empty_claim_and_document(self) -> None:
        self.assertEqual(verify_claim("", "", DOC).verdict, "unsupported")
        self.assertEqual(verify_claim("A real sentence about capacity.", "", "").verdict, "unsupported")

    def test_coverage_ignores_percent_spelling(self) -> None:
        self.assertEqual(
            verify_claim("The reported share is 12 percent.", "", "The reported share is 12%.").verdict,
            "supported",
        )

    def test_partial_support_band(self) -> None:
        thresholds = VerificationThresholds(supported=0.9, partially_supported=0.2, quote_min_chars=24)
        result = verify_claim("Battery deployment grew steadily over the decade.", "", DOC, thresholds=thresholds)
        self.assertIn(result.verdict, {"partially_supported", "supported"})

    def test_derived_statement_rejects_uncomputed_figures(self) -> None:
        ok = verify_derived("This question is supported by 5 claim(s) from 2 source(s).", ["5", "2"])
        bad = verify_derived("This question is supported by 9 claim(s) from 2 source(s).", ["5", "2"])
        self.assertEqual(ok.verdict, "supported")
        self.assertEqual(bad.verdict, "unsupported")
        self.assertIn("9", bad.missing_numbers)


class GroundingTests(unittest.TestCase):
    def test_admits_informative_sentences_only(self) -> None:
        record = EvidenceRecord(
            evidence_id="ev-test",
            source_id="test",
            source_name="Test source",
            url="https://example.invalid/x",
            title="Test",
            text=DOC,
            content_hash=sha256_text(DOC),
            evidence_class="official_data",
            evidence_rank=5,
        )
        proposals = ground_evidence(record)
        self.assertGreater(len(proposals), 0)
        for proposal in proposals:
            self.assertNotIn("source:", proposal.text.casefold())
            self.assertGreaterEqual(len(proposal.text), 40)

    def test_rejects_content_free_sentence(self) -> None:
        self.assertIsNone(proposal_from_sentence("This is the same as that and so on and so forth."))
        self.assertIsNone(proposal_from_sentence("Short."))

    def test_boilerplate_is_dropped(self) -> None:
        self.assertIsNone(proposal_from_sentence("Source: Some API response header line that is long enough to pass length checks."))


class CalibrationTests(unittest.TestCase):
    def test_labelled_cases_are_answered_correctly_at_the_selected_thresholds(self) -> None:
        cases = load_cases(FIXTURE_DIR / "verification_cases.jsonl")
        self.assertGreaterEqual(len(cases), 20)
        selected = VerificationThresholds(supported=0.80, partially_supported=0.45, quote_min_chars=24)
        result = evaluate([c for c in cases if not c.excluded_from_selection], selected)
        self.assertEqual(result["false_supports"], 0, "a labelled non-case must never be accepted")
        self.assertEqual(result["accuracy"], 1.0, f"disagreements: {result['disagreements']}")

    def test_excluded_case_is_documented(self) -> None:
        cases = load_cases(FIXTURE_DIR / "verification_cases.jsonl")
        excluded = [c for c in cases if c.excluded_from_selection]
        self.assertTrue(excluded, "the unit-substitution limitation must stay documented")
        self.assertTrue(all(c.exclusion_reason for c in excluded))

    def test_default_thresholds_still_pass_the_critical_property(self) -> None:
        cases = load_cases(FIXTURE_DIR / "verification_cases.jsonl")
        result = evaluate([c for c in cases if not c.excluded_from_selection], THRESHOLDS)
        self.assertEqual(result["false_supports"], 0)


class StrengthRuleTests(unittest.TestCase):
    """Rules that cap a claim when its wording outruns the passage it matches."""

    DOC = (
        "Registry note. Emissions from the sector fell by 4% over the period. "
        "The method worked in about a third of the conditions tested."
    )

    def test_reversed_direction_is_capped(self) -> None:
        from selflearn.verify.verifier import verify_claim

        result = verify_claim(
            "Emissions from the sector rose by 4% over the period.",
            "",
            self.DOC,
            thresholds=THRESHOLDS,
        )
        self.assertEqual(result.verdict, "partially_supported")
        self.assertTrue(any("capped" in reason.casefold() for reason in result.reasons))

    def test_universal_claim_against_a_hedge_is_capped(self) -> None:
        from selflearn.verify.verifier import verify_claim

        result = verify_claim(
            "The method worked in all of the conditions tested.",
            "",
            self.DOC,
            thresholds=THRESHOLDS,
        )
        self.assertEqual(result.verdict, "partially_supported")

    def test_direction_helpers_do_not_fire_on_agreement(self) -> None:
        from selflearn.verify.verifier import directional_conflict, universality_gap

        self.assertEqual(directional_conflict("Emissions fell by 4%.", "Emissions fell by 4%."), "")
        self.assertEqual(universality_gap("The method worked in about a third of conditions.", "about a third"), "")

    def test_fabricated_number_still_outranks_a_cap(self) -> None:
        from selflearn.verify.verifier import verify_claim

        result = verify_claim(
            "Emissions from the sector rose by 4% in 1999.",
            "",
            self.DOC,
            thresholds=THRESHOLDS,
        )
        self.assertEqual(result.verdict, "unsupported")


class AuditTests(unittest.TestCase):
    def test_recheck_reports_a_missing_snapshot(self) -> None:
        claim = Claim(
            claim_id="cl-1",
            topic_id="topic-1",
            text="A statement about capacity.",
            evidence_id="ev-missing",
            source_name="Test",
            url="https://example.invalid/1",
            quote="",
            evidence_class="official_data",
            evidence_rank=5,
            confidence="medium",
            verification=Verification(verdict="supported", quote_match=False, coverage=1.0),
        )
        findings = recheck_claims([claim], Path("/nonexistent-snapshot-dir"))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "error")

    def test_recheck_accepts_a_consistent_snapshot(self) -> None:
        import tempfile

        text = DOC
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ev-good.json"
            path.write_text(json.dumps({"text": text, "content_hash": sha256_text(text)}), encoding="utf-8")
            claim = Claim(
                claim_id="cl-2",
                topic_id="topic-1",
                text="Capacity degradation is about 2% per year for cells held at moderate temperature.",
                evidence_id="ev-good",
                source_name="Test",
                url="https://example.invalid/2",
                quote="Capacity degradation is about 2% per year for cells held at moderate temperature.",
                evidence_class="official_data",
                evidence_rank=5,
                confidence="medium",
                verification=verify_claim(
                    "Capacity degradation is about 2% per year for cells held at moderate temperature.",
                    "Capacity degradation is about 2% per year for cells held at moderate temperature.",
                    text,
                ),
            )
            findings = recheck_claims([claim], Path(tmp))
            self.assertEqual([f for f in findings if f.severity == "error"], [])

    def test_link_check_flags_relative_urls(self) -> None:
        claim = Claim(
            claim_id="cl-3",
            topic_id="topic-1",
            text="A statement.",
            evidence_id="ev-3",
            source_name="Test",
            url="not-a-url",
            quote="",
            evidence_class="official_data",
            evidence_rank=5,
            confidence="low",
            verification=Verification(verdict="supported", quote_match=False, coverage=1.0),
        )
        findings = check_links([claim])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "warning")

    def test_coverage_of_claim_by_document(self) -> None:
        self.assertEqual(coverage("Battery cell prices fell sharply over the decade", DOC), 1.0)
        self.assertLess(coverage("The protein fold was determined by cryogenic electron microscopy", DOC), 0.2)


if __name__ == "__main__":
    unittest.main()
