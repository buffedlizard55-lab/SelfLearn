"""Tests for the GEMS Prize research knowledge base.

No network. They lock in: the section's files exist and link to each other;
every research entry and hypothesis carries the required fields; the builder is
idempotent (re-rendering reproduces byte-identical pages); the data-placement
evidence pins match the placement script's pins; and the site integration
(publisher template nav) points at the section.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import gems_research_content as C  # noqa: E402
import build_gems_research as B  # noqa: E402

RESEARCH = ROOT / "docs" / "research"


class TestSectionFiles(unittest.TestCase):
    def test_required_pages_exist(self):
        required = [
            "index.html",
            "hypotheses.html",
            "ai-usage-log.html",
            "ai-usage-log.md",
            "changelog.html",
            "data-placement.html",
        ] + [f"domains/{d['slug']}.html" for d in C.DOMAINS]
        for rel in required:
            self.assertTrue((RESEARCH / rel).is_file(), f"missing {rel}")

    def test_internal_links_resolve(self):
        link_re = re.compile(r'href="([^"#]+)"')
        broken = []
        for page in RESEARCH.rglob("*.html"):
            for href in link_re.findall(page.read_text(encoding="utf-8")):
                if href.startswith(("http://", "https://", "mailto:", "data:")):
                    continue
                if not (page.parent / href).resolve().exists():
                    broken.append(f"{page.name} -> {href}")
        self.assertEqual(broken, [])

    def test_json_exports_parse(self):
        for rel in ["anchors.json", "domains.json", "hypotheses.json", "ai_usage_log.json",
                    "changelog.json", "irregularities.json"]:
            data = json.loads((RESEARCH / "data" / rel).read_text(encoding="utf-8"))
            self.assertIsNotNone(data)


class TestContentDiscipline(unittest.TestCase):
    def test_entries_have_required_fields(self):
        for d in C.DOMAINS:
            for e in d["entries"]:
                for field in ("sources", "claims", "relevance", "confidence", "kind"):
                    self.assertTrue(e.get(field), f"{e['id']} missing {field}")
                self.assertTrue(e["sources"], f"{e['id']} has no source link")

    def test_hypotheses_have_required_fields_and_valid_status(self):
        valid = {"untested", "validated-on-spatial-holdout", "rejected"}
        for h in C.HYPOTHESES:
            for field in ("layers", "signature", "gap_reasoning", "dti_impact", "cost",
                          "status", "status_detail", "sources"):
                self.assertTrue(h.get(field), f"{h['id']} missing {field}")
            self.assertIn(h["status"], valid, f"{h['id']} bad status {h['status']}")

    def test_anchors_are_https_and_unique(self):
        urls = [a["url"] for a in C.ANCHORS]
        self.assertEqual(len(urls), len(set(urls)))
        for u in urls:
            self.assertTrue(u.startswith("https://"), u)

    def test_anchor_count_claim_matches(self):
        changelog = json.dumps(C.CHANGELOG)
        n = len(C.ANCHORS)
        words = {11: "eleven", 12: "twelve", 13: "thirteen"}
        self.assertIn(words[n], changelog)


class TestBuilderIdempotent(unittest.TestCase):
    def setUp(self):
        self._orig = (B.OUT, B.DATA_OUT)

    def tearDown(self):
        B.OUT, B.DATA_OUT = self._orig

    def test_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            outs = []
            for run in range(2):
                out = Path(td) / f"run{run}"
                (out / "domains").mkdir(parents=True)
                B.OUT, B.DATA_OUT = out, out / "data"
                B.main()
                outs.append((out / "index.html").read_bytes())
            self.assertEqual(outs[0], outs[1])

    def test_committed_pages_match_a_fresh_render(self):
        """The committed HTML must be exactly what the current content renders."""
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "render"
            (out / "domains").mkdir(parents=True)
            B.OUT, B.DATA_OUT = out, out / "data"
            B.main()
            for rel in ["index.html", "hypotheses.html", "changelog.html",
                        "data-placement.html", "ai-usage-log.html", "ai-usage-log.md",
                        "domains/catalogue-gaps.html", "domains/governance.html"]:
                self.assertEqual(
                    (out / rel).read_bytes(),
                    (RESEARCH / rel).read_bytes(),
                    f"{rel} is stale; re-run tools/build_gems_research.py",
                )


class TestPlacementPins(unittest.TestCase):
    PINS = {
        "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
        "existing_faults.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
        "example_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
    }

    def test_evidence_record_matches_script_pins(self):
        script = (ROOT / "scripts" / "download_competition_data.sh").read_text(encoding="utf-8")
        evidence = json.loads(
            (ROOT / "evidence" / "gems" / "2026-09-26_data_placement.json").read_text(encoding="utf-8")
        )
        for name, pin in self.PINS.items():
            self.assertIn(pin, script, f"script is missing the official pin for {name}")
            self.assertEqual(evidence["sha256_pins"][name], pin)

    def test_session6_evidence_used_the_same_feature_bytes(self):
        s6 = json.loads(
            (ROOT / "gemsdoe_review" / "evidence" / "grav_hg_identity_session6.json").read_text(encoding="utf-8")
        )
        self.assertEqual(s6["training_features_sha256"], self.PINS["training_features.tif"])

    def test_inventory_spec_checks_conforming(self):
        inv = json.loads(
            (ROOT / "evidence" / "gems" / "2026-09-26_data_placement.json").read_text(encoding="utf-8")
        )
        self.assertTrue(inv["inspection"]["checks"]["all_conforming"])
        feats = [f for f in inv["inspection"]["files"] if f["path"].endswith("training_features.tif")][0]
        self.assertEqual(feats["bands"], 19)
        self.assertEqual(feats["epsg"], 32611)
        self.assertEqual(feats["res_x"], 100.0)


class TestSiteIntegration(unittest.TestCase):
    def test_publisher_nav_points_at_section(self):
        site_py = (ROOT / "selflearn" / "publish" / "site.py").read_text(encoding="utf-8")
        self.assertIn('("research/index.html", "GEMS research")', site_py)

    def test_generated_docs_pages_link_the_section(self):
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("research/index.html", index)
        root = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("docs/research/index.html", root)

    def test_no_submission_generation_in_section(self):
        """The research section and its tools must never write a prediction file."""
        for script in ["scripts/download_competition_data.sh", "scripts/prepare_data.py",
                       "tools/build_gems_research.py", "tools/gems_research_content.py"]:
            text = (ROOT / script).read_text(encoding="utf-8")
            self.assertNotIn("build_submission", text)
            self.assertNotIn("predicted_faults", text)


if __name__ == "__main__":
    unittest.main()
