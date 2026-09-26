"""Independent geometry/metric and review safeguards.

For canonical-code checks, set GEMSDOE_ENTRY_ROOT to a read-only checkout of
buffedlizard55-lab/6GEMSDOE (with its src/ directory). Without it the canonical
checks are SKIPPED, not silently run against an unrelated `gems` package:

  GEMSDOE_ENTRY_ROOT=/tmp/gems_entry \\
  GEMSDOE_PRIOR_METRICS=/tmp/gems_prior/src/metrics.py \\
      .venv/bin/python -m pytest -q gemsdoe_review/tests/test_review_regressions.py

The prior-metric parity case is optional and skips without that second variable.

The canonical CV distance test FAILS until the companion patch under patches/
is applied to the entry's src/gems/cv.py. The failure is real: Manhattan-corner
neighbours can fall inside the metric's 300 m Euclidean radius. Testing both
pre- and post-patch copies is required before proposing an upstream merge.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy import ndimage

TOOLS = Path(__file__).resolve().parents[1] / "tools"
REVIEW = TOOLS.parent


def tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_doc_checker_rejects_foreign_score_and_not_nearby_number():
    checker = tool("check_entry_docs")
    docs = {"EXECUTIVE_SUMMARY.md": "Our public score is 0.1563.\n",
            "SUBMISSION_GUIDE.md": "0.15630 is an unrelated longer number.\n"}
    assert checker.board_score_locations(docs, "0.1563") == ["EXECUTIVE_SUMMARY.md:1"]
    assert not checker.board_score_locations({"guide": docs["SUBMISSION_GUIDE.md"]},
                                             "0.1563")
    assert not checker.board_score_locations(docs, "0.1152")


def test_geology_report_rejects_historical_ranks_and_distinguishes_distance_band():
    report = tool("current_geology_report")
    with pytest.raises(ValueError, match="submission SHA-256"):
        report.render({"counts": {"candidates": 1}, "candidates": []})
    record = {"agreement": {"families": ["seismicity"]},
              "diagnostics": {
                  "ieq_n100a15": {"family": "seismicity", "favourable": False},
                  "deq_n100a15": {"family": "seismicity", "favourable": True,
                                   "regional_percentile_median": 0.07,
                                   "description": "distance to earthquakes",
                                   "direction": "low"}}}
    s = report.diagnostic_text(record)
    assert len(s) == 1 and "short distance" in s[0] and "low 0.07" in s[0]


def test_shipped_dossier_is_bound_to_the_current_raster():
    evidence = REVIEW / "evidence" / "current_shipped_geology_2026-09-26.json"
    if not evidence.exists():
        pytest.skip("large measurement JSON not checked out")
    def reject_nonfinite(token):
        raise ValueError(f"invalid non-finite JSON token: {token}")
    d = json.loads(evidence.read_text(), parse_constant=reject_nonfinite)
    report = tool("current_geology_report")
    assert d["input_sha256"]["submission"] == (
        "33cec71ff00b3f32d0d59c81c156f3f1488ffef46baa4b6499094e24ea1875ab")
    assert d["counts"]["candidates"] == 180
    assert all(0 < r["emitted_pixels"] <= r["pixels"] for r in d["candidates"])
    assert any(r["emitted_pixels"] < r["pixels"] for r in d["candidates"])
    assert all("metric_local" not in r for r in d["candidates"])
    inv = d["fragment_inventory"]
    csv_path = evidence.parent / inv["file"]
    assert hashlib.sha256(csv_path.read_bytes()).hexdigest() == inv["sha256"]
    with csv_path.open(newline="") as fh:
        fragments = list(csv.DictReader(fh))
    assert len(fragments) == inv["components"] == 2409
    assert sum(int(r["emitted_px"]) for r in fragments) == inv["emitted_px"]
    assert (sum(r["emitted_pixels"] for r in d["candidates"])
            + inv["emitted_px"] + inv["emitted_lost_to_closing_px"]
            == d["counts"]["predicted_off_catalogue"])
    text = report.render(d)
    assert text.count("\n### S-") == 180
    assert d["input_sha256"]["submission"] in text
    assert "ens12-adopted" not in text


@pytest.fixture(scope="module")
def canonical():
    entry = os.environ.get("GEMSDOE_ENTRY_ROOT")
    if entry is None:
        pytest.skip("set GEMSDOE_ENTRY_ROOT to the canonical entry checkout")
    root = Path(entry).resolve()
    if not (root / "src" / "gems" / "cv.py").is_file():
        raise FileNotFoundError(root / "src" / "gems" / "cv.py")
    sys.path.insert(0, str(root / "src"))
    from gems import cv, metric, features  # noqa: E402
    yield cv, metric, features
    sys.path.remove(str(root / "src"))


@pytest.mark.parametrize("delta", [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2),
                                   (3, 0), (3, 1), (4, 0)])
def test_metric_exact_kernel_and_penalties(canonical, delta):
    """Published equations, hand-derived on one soft pixel, not shared metric code."""
    _, metric, _ = canonical
    g = np.zeros((13, 13), dtype=bool)
    p = np.zeros_like(g, dtype=float)
    g[6, 6] = True
    p[6 + delta[0], 6 + delta[1]] = 0.7
    d = math.hypot(*delta)
    k = max(0.0, 1.0 - d / 3.0)
    expected = (0.7 * k, 0.7 * (1 - k), 1 - 0.7 * k)
    c = metric.components(p, g)
    assert (c.tp_w, c.fp_w, c.fn_w) == pytest.approx(expected, abs=1e-12)
    assert c.dti == pytest.approx(expected[0] / (expected[0] + 0.2 * expected[1] +
                                                     0.8 * expected[2]), abs=1e-12)


def test_prior_fast_proxy_metric_matches_canonical_metric(canonical):
    """The fast SGMC evaluator must match the official-formula implementation."""
    path = os.environ.get("GEMSDOE_PRIOR_METRICS")
    if path is None:
        pytest.skip("set GEMSDOE_PRIOR_METRICS to the prior read-only src/metrics.py")
    prior_spec = importlib.util.spec_from_file_location("gems_prior_metrics_audit", path)
    assert prior_spec and prior_spec.loader
    prior = importlib.util.module_from_spec(prior_spec)
    sys.modules[prior_spec.name] = prior
    prior_spec.loader.exec_module(prior)
    _, metric, _ = canonical
    g = np.zeros((19, 23), dtype=bool)
    g[5, 5] = g[12, 19] = True
    p = np.zeros_like(g, dtype=float)
    p[5, 6] = 0.63       # soft neighbour
    p[10, 18] = 0.87     # sqrt(5) offset
    p[18, 18] = 0.23     # remote FP
    p[12, 19] = 0.8      # on a ground-truth pixel
    # The official page leaves epsilon unspecified. The fast path uses 1e-7;
    # match that documented convention rather than call the roundoff a bug.
    canonical_counts = metric.components(p, g, eps=prior.EPS)
    dti, counts = prior.GtContext(g, R_pixels=3).score(p, return_components=True)
    assert counts == pytest.approx((canonical_counts.tp_w, canonical_counts.fp_w,
                                    canonical_counts.fn_w), abs=1e-11)
    assert dti == pytest.approx(canonical_counts.dti, abs=1e-9)


def test_metric_takes_max_not_sum_for_overlapping_predictions(canonical):
    _, metric, _ = canonical
    g = np.zeros((9, 9), dtype=bool)
    p = np.zeros_like(g, dtype=float)
    g[4, 4] = True
    p[4, 3] = 0.6       # weighted TP 0.4
    p[3, 3] = 0.9       # weighted TP 0.9 * (1 - sqrt(2)/3) ~ 0.4757
    expected_tp = max(0.6 * (2/3), 0.9 * (1 - math.sqrt(2)/3))
    expected_fp = 0.6 * (1/3) + 0.9 * (math.sqrt(2)/3)
    c = metric.components(p, g)
    assert c.tp_w == pytest.approx(expected_tp)
    assert c.fp_w == pytest.approx(expected_fp)
    assert c.fn_w == pytest.approx(1 - expected_tp)
    assert c.tp_w != pytest.approx(sum((0.4, 0.9 * (1 - math.sqrt(2)/3))))


def test_metric_has_no_wrapping_at_borders(canonical):
    _, metric, _ = canonical
    g = np.zeros((9, 9), dtype=bool)
    p = np.zeros_like(g, dtype=float)
    g[0, 0] = True
    p[-1, -1] = 1.0
    c = metric.components(p, g)
    assert (c.tp_w, c.fp_w, c.fn_w, c.dti) == (0.0, 1.0, 1.0, 0.0)


def test_hardening_each_probability_is_not_always_better(canonical):
    _, metric, _ = canonical
    g = np.zeros((13, 13), dtype=bool)
    g[2, 2] = True
    p = np.zeros_like(g, dtype=float)
    p[2, 2] = 1.0
    p[9, 9] = 0.01  # weak remote false positive
    soft = metric.components(p, g)
    hard = metric.components((p > 0).astype(float), g)
    assert soft.tp_w == hard.tp_w == 1.0
    assert soft.fp_w == pytest.approx(0.01)
    assert hard.fp_w == pytest.approx(1.0)
    assert soft.dti > hard.dti


def test_4_or_5_pixel_spacing_is_not_free_on_an_exact_true_line(canonical):
    _, metric, _ = canonical
    g = np.zeros((9, 25), dtype=bool)
    g[4, 2:23] = True
    dense = metric.components(g.astype(float), g)
    assert dense.dti == 1.0
    for spacing in (4, 5):
        thin = np.zeros_like(g, dtype=float)
        thin[4, 2:23:spacing] = 1.0
        c = metric.components(thin, g)
        assert c.dti < dense.dti
        assert c.tp_w < g.sum() and c.fn_w > 0


@pytest.mark.parametrize("n_blocks,n_folds,shape", [
    (4, 4, (80, 80)), (5, 3, (80, 77)), (6, 4, (91, 87)),
])
def test_cv_excludes_full_euclidean_metric_kernel(canonical, n_blocks, n_folds, shape):
    """Independent EDT oracle, unlike canonical test that reuses cv._dilate."""
    cv, _, _ = canonical
    folds = cv.make_folds(n_blocks=n_blocks, n_folds=n_folds, buffer_px=3)
    all_scores = np.zeros(shape, dtype=bool)
    for k in range(n_folds):
        train, score = folds.train_test_masks(shape, k)
        assert score.any() and train.any()
        assert not (score & all_scores).any(), "score folds overlap"
        assert not (train & score).any(), "train contains held-out block"
        all_scores |= score
        distance = ndimage.distance_transform_edt(~score)
        leaking = train & (distance <= 3.0)
        assert not leaking.any(), (n_blocks, k, int(leaking.sum()),
                                   np.argwhere(leaking)[:10].tolist())
    assert all_scores.all(), "scored blocks do not partition the grid"


def test_component_azimuth_accounts_for_southward_increasing_raster_rows(canonical):
    d = tool("geology_dossier")
    # With north up: row decreases as both northing and eastward col increase.
    # The major line runs NE-SW, not NW-SE.
    rows = np.arange(10, 30)
    cols = 50 - rows
    assert d.candidate_geometry(rows, cols)["azimuth_deg_from_north"] == pytest.approx(45)


def test_plan_curvature_is_not_profile_curvature(canonical):
    _, _, features = canonical
    d = tool("geology_dossier")
    # Independent source guard, plus a synthetic surface with different curvature
    # in the x and y directions. The shipped and audit paths must agree.
    import inspect
    source = inspect.getsource(d.build_diagnostics)
    assert 'out["curv_plan"] = curv.plan' in source
    assert 'out["curv_plan"] = curv.profile' not in source
    y, x = np.mgrid[:21, :21]
    curv = features.curvature((x ** 2 + 4 * y ** 2).astype(float), spacing=100.0)
    assert np.max(np.abs(curv.plan - curv.profile)) > 1e-12
