"""Session-2 additions: tests for the new measurement/narrative tools.

Run with:
  GEMSDOE_ENTRY_ROOT=/path/to/6GEMSDOE .venv/bin/python -m pytest -q \
      gemsdoe_review/tests/test_session2_additions.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"


def tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------- AUC sanity

def test_auc_perfect_separation_and_ties():
    fa = tool("feature_priorities_audit")
    assert fa.auc(np.array([3.0, 4.0]), np.array([1.0, 2.0])) == 1.0
    assert fa.auc(np.array([1.0, 2.0]), np.array([3.0, 4.0])) == 0.0
    # complete tie -> 0.5
    assert fa.auc(np.array([1.0, 1.0]), np.array([1.0, 1.0])) == 0.5
    # 3 of 4 pairings favour pos (2>1, 3>1, 3>2), 2==2 ties -> 0.875
    assert abs(fa.auc(np.array([2.0, 3.0]), np.array([1.0, 2.0])) - 0.875) < 1e-12
    # mirror symmetry
    rng = np.random.default_rng(0)
    p, n = rng.normal(0.3, 1.0, 500), rng.normal(0.0, 1.0, 700)
    assert abs(fa.auc(p, n) + fa.auc(n, p) - 1.0) < 1e-12


def test_sep_polarity_and_trend_bands():
    fa = tool("feature_priorities_audit")
    pn = tool("phase2_narrative")
    assert fa.sep(0.44) == (0.56, "-")
    assert fa.sep(0.56) == (0.56, "+")
    assert pn.trend_reading(300.0)[0].startswith("NW")
    assert pn.trend_reading(345.0)[0].startswith("NW")
    assert pn.trend_reading(350.0)[0].startswith("N")   # wrap 345 -> 25
    assert pn.trend_reading(25.0)[0].startswith("N")
    assert pn.trend_reading(24.9)[0].startswith("N")
    assert pn.trend_reading(46.3)[0].startswith("NE")
    assert pn.trend_reading(98.2)[0] == "outside the three regional trend families"
    assert pn.trend_reading(180.0)[0] == "outside the three regional trend families"


# ------------------------------------------------- phase2 narrative renderer

def _mk_rec(**over):
    rec = {
        "candidate_id": 1, "rank_by_size": 1, "class": "near_trace",
        "emitted_pixels": 2000, "area_km2": 2.0,
        "major_axis_km": 5.0, "minor_axis_km": 1.0, "elongation": 5.0,
        "azimuth_deg_from_north": 320.0,
        "centroid_lonlat": [-118.0, 38.5],
        "distance_to_catalogue_px": {"median": 2.0, "mean": 2.5,
                                     "fraction_within_300m": 0.6},
        "agreement": {"n_families_of_6": 2, "families": ["seismicity", "strain"]},
        "diagnostics": {"geod_2ndinv": {"family": "strain", "direction": "high",
                                        "regional_percentile_median": 0.99,
                                        "favourable": True},
                        "tdr_mag": {"family": "untrusted_tilt",
                                    "direction": "untrusted",
                                    "regional_percentile_median": 0.5,
                                    "favourable": False}},
        "tilt_depth": {"status": "not estimable from the supplied bands"},
    }
    rec.update(over)
    return rec


HALO = _mk_rec(**{"class": "halo"})
NEAR = _mk_rec(**{"class": "near_trace"})
ISO = _mk_rec(**{"class": "isolated",
                 "distance_to_catalogue_px": {"median": 9.0, "mean": 9.5,
                                              "fraction_within_300m": 0.0}})


def test_confidence_ceiling_is_provisional_and_tiers_are_measured():
    fa = tool("phase2_narrative")
    assert fa.confidence_of(_mk_rec()) == "low-to-provisional"
    three = {"n_families_of_6": 3, "families": ["a", "b", "c"]}
    assert fa.confidence_of(_mk_rec(agreement=three)) == "provisional"
    assert fa.confidence_of(_mk_rec(agreement=three, elongation=1.5)) == \
        "low-to-provisional"
    assert fa.confidence_of(_mk_rec(agreement=three, emitted_pixels=900)) == \
        "low-to-provisional"
    assert fa.confidence_of(_mk_rec(agreement={"n_families_of_6": 0,
                                               "families": []})) == "low"
    assert fa.confidence_of(ISO) == "low"


def test_untrusted_tilt_never_counts_as_support():
    fa = tool("phase2_narrative")
    s = fa.family_sentence(_mk_rec())
    assert "geod_2ndinv" in s and "tdr_mag" not in s
    zero = fa.family_sentence(_mk_rec(agreement={"n_families_of_6": 0,
                                                 "families": []}))
    assert "0/6" in zero


def test_masking_consequences_are_class_specific():
    fa = tool("phase2_narrative")
    assert "excluded training-label band" in fa.halo_sentence(HALO)
    assert "cannot be counted as an independent discovery" in \
        fa.halo_sentence(NEAR)
    assert "no confirmatory weight" in fa.halo_sentence(ISO)


def test_depth_sentence_never_invents_a_depth():
    fa = tool("phase2_narrative")
    s = fa.depth_sentence(_mk_rec())
    assert "not estimable" in s and "No depth is claimed" in s


def test_renderer_refuses_dossier_without_submission_sha(tmp_path):
    fa = tool("phase2_narrative")
    bad = tmp_path / "d.json"
    bad.write_text(json.dumps({"candidates": []}))
    sys_argv = sys.argv
    sys.argv = ["phase2_narrative.py", "--dossier", str(bad),
                "--outdir", str(tmp_path)]
    try:
        with pytest.raises(SystemExit, match="input_sha256.submission"):
            fa.main()
    finally:
        sys.argv = sys_argv


# --------------------------------------------------- stored evidence hygiene

def test_session2_evidence_files_parse_and_carry_pins():
    fa = json.loads(
        (EVIDENCE / "feature_priorities_audit_2026-09-26.json").read_text())
    assert fa["features_raster_sha256_matches_pin"] is True
    assert fa["n_catalogue_positive_pixels"] == 60988
    assert set(fa["A_potential_field_gradient_tilt"]["auc_pos_vs_far_bg"]) == \
        {"mag_tilt_abs", "tdr_tmi_s1.5_abs", "tdr_tmi_s3.0_abs",
         "grav_tilt_abs", "mag_asa", "grav_asa"}

    ph = json.loads(
        (EVIDENCE / "phase2_candidate_narratives_2026-09-26.json").read_text())
    assert ph["submission_sha256"].startswith("33cec71f")
    assert ph["n_candidates"] == 180
    assert all(r["confidence"] in ("low", "low-to-provisional", "provisional")
               for r in ph["candidates"])
    assert ph["confidence_counts"].get("provisional", 0) == 0

    ow = json.loads(
        (EVIDENCE / "ownership_resolution_2026-09-26_session2.json").read_text())
    assert ow["_bottom_line"]["github_layer"].startswith("RESOLVED")
    assert ow["github_evidence_2026_09_26"]["repos"]["6GEMSDOE"]["owner"] == \
        "buffedlizard55-lab"


def test_cv_patch_still_applies_to_entry_copy():
    """The patch dry-runs against the audited entry checkout (if provided)."""
    entry = os.environ.get("GEMSDOE_ENTRY_ROOT")
    if not entry:
        pytest.skip("set GEMSDOE_ENTRY_ROOT to the canonical entry checkout")
    patch = Path(__file__).resolve().parents[1] / "patches" / \
        "cv_euclidean_buffer.patch"
    r = subprocess.run(["patch", "-p1", "--dry-run", "-i", str(patch)],
                       cwd=entry, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
