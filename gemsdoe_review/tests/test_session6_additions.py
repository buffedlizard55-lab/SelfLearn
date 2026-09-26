#!/usr/bin/env python3
"""Session-6 regressions: the nested placement check and its evidence.

Pure-numpy oracles (always run), evidence pins that re-derive the session-6
selection and verdict from the committed inner/outer scores, and ownership pins.
No entry checkout, no network, no upload.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
NESTED = EVIDENCE / "nested_policy_cv_session6.json"


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def brute_dti(pred_bool: np.ndarray, gt: np.ndarray, r: float = 3.0, a: float = 0.2, b: float = 0.8) -> float:
    """O(N_pred * N_gt) oracle of the published formula; independent of every tool."""
    P = np.argwhere(pred_bool).astype(float)
    G = np.argwhere(gt).astype(float)
    if len(G) == 0 or len(P) == 0:
        return 0.0
    d = np.sqrt(((P[:, None, :] - G[None, :, :]) ** 2).sum(-1))
    k = np.maximum(1.0 - d / r, 0.0)
    tp = k.max(axis=0).sum()
    fn = len(G) - tp
    fp = (1.0 - k.max(axis=1)).sum()
    return float(tp / (tp + a * fp + b * fn))


def test_fast_components_matches_bruteforce_oracle():
    n = load_tool("nested_policy_cv")
    from scipy import ndimage
    rng = np.random.default_rng(6)
    for _ in range(25):
        gt = rng.random((40, 37)) < 0.03
        pred = rng.random((40, 37)) < rng.uniform(0.01, 0.2)
        k = np.maximum(1 - ndimage.distance_transform_edt(~gt) / 3, 0)
        assert abs(n.fast_components(pred, gt, k)[3] - brute_dti(pred, gt)) < 1e-10


@pytest.mark.parametrize("spacing", [1, 2, 3, 4, 5, 6])
def test_greedy_prefix_equals_budget_nodes(spacing):
    n = load_tool("nested_policy_cv")
    cv = load_tool("spatial_system_cv")
    rng = np.random.default_rng(spacing)
    prob = rng.random((60, 50)).astype(np.float32)
    prob[rng.random(prob.shape) < 0.2] = 0.5  # ties exercise the stable order
    valid = rng.random(prob.shape) < 0.8
    seq = n.greedy_sequence(np.where(valid, prob, 0), valid, spacing, 10_000)
    for frac in (0.01, 0.03, 0.08):
        ref = cv.budget_nodes(prob, valid, fraction=frac, spacing=spacing)
        b = max(1, int(round(frac * valid.sum())))
        mine = np.zeros(prob.shape, dtype=np.float32)
        mine.ravel()[seq[:b]] = 1
        assert np.array_equal(ref, mine)


def test_surfaces_are_label_free_bounded_and_confined():
    n = load_tool("nested_policy_cv")
    rng = np.random.default_rng(1)
    prob = rng.random((50, 50)).astype(np.float32)
    score = np.zeros((50, 50), bool)
    score[5:40, 8:45] = True
    for kind in n.SURFACES:
        s = n.make_surface(prob, score, kind)
        assert (s[~score] == 0).all() and np.isclose(s.max(), 1.0) and s.min() >= 0
    # kconv of a single spike reproduces the metric kernel weights around it
    spike = np.zeros((15, 15), np.float32)
    spike[7, 7] = 1
    full = np.ones_like(spike, bool)
    s = n.make_surface(spike, full, "kconv")
    assert np.isclose(s[7, 8], 2 / 3) and np.isclose(s[7, 10], 0.0) and np.isclose(s[8, 8], 1 - np.sqrt(2) / 3)


def test_decision_rule_in_evidence_is_the_tool_rule():
    n = load_tool("nested_policy_cv")
    printed = json.loads((EVIDENCE / "nested_policy_rule_printed_session6.json").read_text())
    assert printed["decision_rule"] == n.DECISION_RULE
    if NESTED.exists():
        assert json.loads(NESTED.read_text())["decision_rule"] == n.DECISION_RULE


@pytest.mark.skipif(not NESTED.exists(), reason="nested evidence not committed")
def test_nested_selection_and_verdict_rederive_from_scores():
    d = json.loads(NESTED.read_text())
    grid = d["grid"]
    keys = [f"{s}|{f}|{sp}" for s in grid["surfaces"] for f in grid["fractions"] for sp in grid["spacings"]]
    frozen = "|".join(map(str, grid["frozen"]))
    outs, froz, surfaces = [], [], []
    for q in range(4):
        inner = {k: np.mean([d["inner"][f"{q}-{j}"]["scores"][k]["dti"] for j in range(4) if j != q]) for k in keys}
        best = max(keys, key=lambda k: inner[k])
        rec = d["selection"][str(q)]
        assert rec["selected"] == best
        assert np.isclose(rec["outer_selected"], d["outer"][str(q)]["scores"][best]["dti"])
        # the outer quadrant's own scores must not be able to change the selection
        for k in keys:
            assert k in d["inner"][f"{q}-{(q + 1) % 4}"]["scores"]
        outs.append(rec["outer_selected"])
        froz.append(d["outer"][str(q)]["scores"][frozen]["dti"])
        surfaces.append(best.split("|")[0])
    v = d["verdict"]
    assert np.isclose(v["nested_estimate"], np.mean(outs)) and np.isclose(v["frozen_outer_mean"], np.mean(froz))
    assert v["N1"] == (np.mean(outs) > np.mean(froz))
    assert v["N2"] == (sum(o > f for o, f in zip(outs, froz)) >= 3)
    assert v["N4_stability"] == (max(surfaces.count(s) for s in set(surfaces)) >= 3)
    assert v["adopt"] == (v["N1"] and v["N2"] and v["N3"] and v["N4_stability"])


@pytest.mark.skipif(not NESTED.exists(), reason="nested evidence not committed")
def test_nested_outer_models_reproduce_session5_and_inner_isolation():
    d = json.loads(NESTED.read_text())
    s5 = json.loads((EVIDENCE / "spatial_system_models_shipping_session5.json").read_text())
    for fold in s5["folds"]:
        q = str(fold["fold"])
        ref = fold["models"]["full88"]["scores"]["budget03_spacing4"]["dti"]
        assert abs(d["outer"][q]["scores"]["raw|0.03|4"]["dti"] - ref) < 1e-9
    for key, rec in d["inner"].items():
        q, j = key.split("-")
        g = rec["geometry"]
        assert sorted(g["excluded_folds"]) == sorted([int(q), int(j)])
        for f in (q, j):
            iso = g[f"fold{f}"]
            assert iso["train_score_overlap"] == 0 and iso["train_within_buffer"] == 0
            assert iso["train_on_held_systems"] == 0 and iso["shared_positive_systems"] == []


def test_ownership_session6_single_owner_and_inventory():
    d = json.loads((EVIDENCE / "ownership_resolution_2026-09-26_session6.json").read_text())
    f = d["findings"]
    assert f["single_github_owner"] and f["owner_ids"] == [309556078] and f["fork_repos"] == []
    assert d["account"]["gems_named_count"] == 12
    for name in ("5GEMSDOE", "GEMSDOE4", "6GEMSDOE"):
        assert d["repositories"][name]["owner_login"] == "buffedlizard55-lab"
        assert d["repositories"][name]["fork"] is False
    assert f["created_since_finding"] == {}  # no new GEMS repo since session 5 began


# --------------------------------------------------------------------------
# Session 6, pass 2: gravity band identity, label-blind corroboration, F1/G1
# --------------------------------------------------------------------------

def _plane_bands(h=40, w=50, seed=1):
    """Synthetic bands where hg is (by construction) dG/dx and slope is |grad G|."""
    rng = np.random.default_rng(seed)
    G = ndi_smooth(rng.normal(size=(h, w)), 3) * 50.0
    gy, gx = np.gradient(G, 100.0)
    T = ndi_smooth(rng.normal(size=(h, w)), 2) * 100.0
    ty, tx = np.gradient(T, 100.0)
    b = {"iso_grav_anom": G, "iso_grav_anom_hg": gx * 1000.0, "iso_grav_anom_vg": rng.normal(size=(h, w)),
         "iso_grav_anom_slope": np.hypot(gx, gy), "tmi": T, "tmi_hg": np.hypot(tx, ty)}
    return b, np.zeros((h, w), dtype=bool)


def ndi_smooth(a, s):
    from scipy import ndimage
    return ndimage.gaussian_filter(a, s)


def test_grav_identity_detects_signed_derivative():
    gbi = load_tool("grav_band_identity")
    b, invalid = _plane_bands()
    st = gbi.identity_stats(b, invalid, n_sample=1000)
    assert st["spearman_hg_vs_dGdx"] > 0.99
    assert abs(st["spearman_hg_vs_HGM"]) < 0.3
    assert st["spearman_slope_vs_HGM"] > 0.99
    assert st["tmi_check_spearman_tmi_hg_vs_HGM"] > 0.99
    assert 0.3 < st["hg_frac_negative"] < 0.7


def test_grav_identity_evidence_pins():
    d = json.loads((EVIDENCE / "grav_hg_identity_session6.json").read_text())
    st = d["stats"]
    assert st["n_sample"] >= 100_000
    assert st["spearman_hg_vs_dGdx"] > 0.9 and abs(st["spearman_hg_vs_HGM"]) < 0.05
    assert st["spearman_slope_vs_HGM"] > 0.9 and st["tmi_check_spearman_tmi_hg_vs_HGM"] > 0.99
    assert d["training_features_sha256"].startswith("4371c82e")


def test_dossier_reads_slope_not_hg_for_gravity_edge():
    src = (TOOLS / "geology_dossier.py").read_text()
    assert 'out["grav_hgm"] = bands["iso_grav_anom_slope"]' in src
    assert 'out["grav_hgm"] = bands["iso_grav_anom_hg"]' not in src


def test_quadrant_percentiles_and_classes():
    lbc = load_tool("label_blind_corroboration")
    oof = np.arange(16, dtype=np.float32).reshape(4, 4)
    m0 = np.zeros((4, 4), bool); m0[:2] = True
    m1 = ~m0
    pct = lbc.quadrant_percentiles(oof, [m0, m1])
    assert pct[0, 0] == 0 and pct[1, 3] == 1 and pct[2, 0] == 0 and pct[3, 3] == 1
    assert lbc.classify(0.95) == "label-blind corroborated"
    assert lbc.classify(0.49) == "label-dependent"
    assert lbc.classify(0.7) == "intermediate"


def test_label_blind_evidence_consistent():
    d = json.loads((EVIDENCE / "label_blind_corroboration_session6.json").read_text())
    rows = d["components"]
    assert len(rows) == d["summary"]["all"]["n"] == 943
    med = np.array([r["oof_percentile_median"] for r in rows])
    assert int((med >= 0.90).sum()) == d["summary"]["all"]["corroborated"]
    assert int((med < 0.50).sum()) == d["summary"]["all"]["dependent"]
    by = {r["candidate_id"]: r for r in rows}
    # session-5's named multi-family candidates: none is label-blind corroborated
    for cid in (20871, 21434, 21229, 24935, 24621, 24431, 24951, 21101):
        assert by[cid]["label_blind_class"] != "label-blind corroborated"


def test_feature_arm_105_rule_rederives():
    a = json.loads((EVIDENCE / "feature_arm_105_session6.json").read_text())
    b = json.loads((EVIDENCE / "nested_policy_cv_session6.json").read_text())
    pol = "raw|0.03|4"
    f105 = [a["outer"][str(q)]["scores"][pol]["dti"] for q in range(4)]
    f88 = [b["outer"][str(q)]["scores"][pol]["dti"] for q in range(4)]
    assert a["complete"] and a["design"]["n_channels"] == "105"
    assert np.mean(f105) > 0.2345 and sum(x > y for x, y in zip(f105, f88)) >= 3


def test_mirror_trainer_swaps_only_gravity_channels():
    bsc = load_tool("build_spaced_candidate")
    mm = np.random.default_rng(0).normal(size=(6, 7, 30)).astype(np.float32)
    fix = {"asa": np.full((6, 7), 5.0, np.float32), "tilt": np.full((6, 7), -1.0, np.float32)}
    rows, cols = np.array([0, 3, 5]), np.array([1, 2, 6])
    X0 = bsc.make_get_X(mm, 30, None)(rows, cols)
    X1 = bsc.make_get_X(mm, 30, fix)(rows, cols)
    assert np.array_equal(X0, mm[rows, cols])
    assert (X1[:, 25] == 5).all() and (X1[:, 26] == -1).all()
    keep = [i for i in range(30) if i not in (25, 26)]
    assert np.array_equal(X0[:, keep], X1[:, keep])


ENTRY = Path(__file__).resolve().parents[3] / "entry-src"


@pytest.mark.skipif(not (ENTRY / "scripts/build_submission.py").exists(), reason="needs entry checkout")
def test_mirror_trainer_equals_entry_trainer(tmp_path):
    pytest.importorskip("sklearn")
    sys.path.insert(0, str(ENTRY / "scripts"))
    import build_submission as bs
    bsc = load_tool("build_spaced_candidate")
    rng = np.random.default_rng(3)
    stack = rng.normal(size=(30, 40, 8)).astype(np.float32)
    gt = np.zeros((30, 40), bool); gt[10:13, 5:30] = True
    stack[gt, 0] += 2.0
    fp = np.ones_like(gt); fp[:, :2] = False
    p = tmp_path / "s.npy"; np.save(p, stack)
    m1, _ = bs.train_model(p, 8, gt, fp, 500, seed=7, iters=20)
    m2, _ = bsc.train_model_X(bsc.make_get_X(np.load(p, mmap_mode="r"), 8, None), gt, fp, 500, seed=7, iters=20)
    a = bs.predict_full(p, m1, fp, 8)
    b = bsc.predict_full_X(bsc.make_get_X(np.load(p, mmap_mode="r"), 8, None), m2, fp)
    assert np.array_equal(a, b)


def _frozen(name):
    d = json.loads((EVIDENCE / name).read_text())
    assert d["complete"]
    return np.array([d["outer"][str(q)]["scores"]["raw|0.03|4"]["dti"] for q in range(4)])


def test_gravity_fix_verdicts_rederive():
    """G1 (88 ch) passes non-inferiority; G1b (105 ch) fails on one fold by > 0.01."""
    base88, g1 = _frozen("nested_policy_cv_session6.json"), _frozen("grav_fix_arm_session6.json")
    base105, g1b = _frozen("feature_arm_105_session6.json"), _frozen("grav_fix_arm_105_session6.json")

    def non_inferior(new, base):
        return bool(new.mean() >= base.mean() - 0.005 and (new - base).min() >= -0.01)

    assert non_inferior(g1, base88)
    assert not non_inferior(g1b, base105)
    assert g1b.mean() >= base105.mean() - 0.005        # it fails on the fold clause only
    for name in ("grav_fix_arm_session6.json", "grav_fix_arm_105_session6.json"):
        d = json.loads((EVIDENCE / name).read_text())
        assert d["design"]["grav_fix"] == "True"
        assert d["grav_fix"]["spearman_hg_vs_dGdx"] > 0.9
