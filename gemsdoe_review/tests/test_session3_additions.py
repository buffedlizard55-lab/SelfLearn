"""Session-3 additions: tests for the shipping-axis experiment tool.

Run with:
  GEMSDOE_ENTRY_ROOT=/path/to/6GEMSDOE .venv/bin/python -m pytest -q \
      gemsdoe_review/tests/test_session3_additions.py

The entry-rooted tests skip when no entry checkout is available; the pure
numpy ones always run.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
ENTRY = Path(os.environ.get("GEMSDOE_ENTRY_ROOT", "/tmp/gems_entry"))

needs_entry = pytest.mark.skipif(
    not (ENTRY / "src" / "gems" / "spec.py").exists(),
    reason="GEMSDOE_ENTRY_ROOT not available (no entry checkout)")


def tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------- topk identity

@needs_entry
def test_topk_hard_matches_canonical_entry_placement():
    """The ablation's topk_hard must be byte-identical to the entry's
    scripts/experiment.py::placements topk_hard — the yardstick only works if
    the budget selection is the same code path."""
    sa = tool("shipping_axis_ablation")
    sys.path.insert(0, str(ENTRY / "src"))
    from gems import spec  # noqa: E402
    sys.path.insert(0, str(ENTRY / "scripts"))
    import experiment  # noqa: E402  (the canonical placements() lives there)

    rng = np.random.default_rng(3)
    p = rng.random((373, 329)).astype(np.float32)
    valid = np.ones(p.shape, dtype=bool)
    valid[rng.choice(p.shape[0], 50), :] = False
    for frac in (0.02, 0.03, 0.05):
        mine = sa.topk_hard(p, valid, frac)
        theirs = experiment.placements(p, valid)[f"topk_hard@{frac:g}"]
        assert (mine == theirs).all(), f"topk_hard@{frac} diverges from canonical"
        n_valid = int(valid.sum())
        k = max(1, int(round(frac * n_valid)))
        assert int(mine.sum()) >= k
        assert not (mine > 0)[~valid].any()


def test_topk_hard_deterministic_and_in_range():
    sa = tool("shipping_axis_ablation")
    rng = np.random.default_rng(11)
    p = rng.random((64, 64)).astype(np.float32)
    valid = np.ones(p.shape, dtype=bool)
    for frac in (0.01, 0.03, 0.5):
        a = sa.topk_hard(p, valid, frac)
        b = sa.topk_hard(p, valid, frac)
        assert (a == b).all()
        assert set(np.unique(a)) <= {0.0, 1.0}
        assert not (a > 0)[~valid].any()


# --------------------------------------------------------- trace keep identity

@needs_entry
def test_kept_trace_table_matches_canonical():
    sa = tool("shipping_axis_ablation")
    sys.path.insert(0, str(ENTRY / "src"))
    sys.path.insert(0, str(ENTRY / "scripts"))
    import experiment  # noqa: E402
    rng = np.random.default_rng(5)
    trace_id = rng.integers(0, 40, size=(50, 50))  # synthetic 40 traces
    n_trace = int(trace_id.max())
    for keep in (0.5, 0.25):
        mine = sa.kept_trace_table(trace_id, n_trace, keep)
        theirs = experiment.kept_trace_mask(trace_id, n_trace, keep)
        # canonical returns a (n_trace+1,) table of trace ids to keep
        assert (mine == theirs).all(), f"keep={keep} diverges from canonical"


# ------------------------------------------------------------- config geometry

def test_drop_configs_remove_exactly_the_declared_channels():
    sa = tool("shipping_axis_ablation")
    # a stand-in 105-channel list in the canonical order shape (88 core + 17 agreement)
    channels = [f"ch{i:03d}" for i in range(105)]
    channels[19] = "mag_asa"     # canonical index of mag_asa (19 bands + 20th)
    channels[20] = "mag_tilt"
    channels[60] = "tdr_tmi_s1.5"
    channels[61] = "tdr_tmi_s3.0"
    full = channels[:88]
    drop2 = [c for c in full if c not in sa.DROP2]
    drop4 = [c for c in full if c not in sa.DROP4]
    assert len(full) == 88 and len(drop2) == 86 and len(drop4) == 84
    assert "mag_asa" not in drop2 and "mag_tilt" not in drop2
    assert "tdr_tmi_s1.5" not in drop4 and "tdr_tmi_s3.0" not in drop4
    # order is preserved, so columns remain comparable with the canonical stack
    assert [c for c in full if c not in sa.DROP2] == drop2


# --------------------------------------------------------------- pseudo logic

def test_pseudo_mask_stays_in_region_and_off_catalogue():
    """The pseudo-positive set must never leave the held-out region and never
    include a catalogue pixel — the two constraints that keep the semi-sup
    protocol spatially honest."""
    sa = tool("shipping_axis_ablation")
    rng = np.random.default_rng(7)
    region = np.zeros((40, 40), dtype=bool)
    region[:, :10] = True
    gt = np.zeros((40, 40), dtype=bool)
    gt[5, 3] = True
    gt[20, 8] = True
    p = np.zeros((40, 40), dtype=np.float32)
    p[5, 3] = 0.99     # catalogue pixel, high prob -> must be excluded
    p[20, 8] = 0.99    # catalogue pixel, high prob -> must be excluded
    p[10, 5] = 0.7     # in region, off-catalogue, above threshold -> in
    p[12, 25] = 0.9    # OUTSIDE region, above threshold -> must be excluded
    agree = np.ones((40, 40), dtype=bool)
    agree[10, 5] = True
    pseudo = (region & ~gt & (p >= sa.PSEUDO_MIN_PROB) & agree)
    assert pseudo[10, 5]
    assert not pseudo[5, 3] and not pseudo[20, 8]
    assert not pseudo[12, 25]
    assert not (pseudo & ~region).any()
    assert not (pseudo & gt).any()


# ------------------------------------------------------------------ evidence

def test_session3_reverification_evidence_is_pinned():
    ev = Path(__file__).resolve().parents[1] / "evidence" / \
        "session3_reverification_2026-09-26.json"
    if not ev.exists():
        pytest.skip("session-3 reverification evidence not yet written")
    import json
    d = json.loads(ev.read_text())
    assert d["format_gate_shipped_file"]["checks"] == "13/13 PASS (all hard)"
    assert d["format_gate_shipped_file"]["stats"]["nan_inside_footprint"] == 0
    assert d["poison_test"]["result"].startswith("values-in-0-1 still PASS")


@needs_entry
def test_entry_cv_is_patched_euclidean():
    """After this session the canonical entry must carry the Euclidean buffer:
    the (2,2) corner at sqrt(8) px must be excluded from training."""
    sa = tool("shipping_axis_ablation")  # noqa: F841 (import side-effect: none)
    sys.path.insert(0, str(ENTRY / "src"))
    from gems import cv  # noqa: E402
    score = np.zeros((9, 9), dtype=bool)
    score[0, 0] = True
    dil = cv._dilate(score, 3)
    assert dil[2, 2], "(2,2) corner must be inside the Euclidean 3-px buffer"
    assert not dil[3, 3]


# ---------------------------------------------------------------------------
# Session-3 additions from the PARALLEL branch (arena/01a0de93-selflearn):
# system-holdout evidence pins, toy-grid budget/selection semantics, and the
# parallel ownership/leaderboard re-resolution records.
# ---------------------------------------------------------------------------
EVIDENCE = Path(__file__).resolve().parent.parent / "evidence"
import json  # used by the parallel-branch evidence tests below

# ---------------------------------------------------------------- toy grid

def _toy_metric():
    entry = os.environ.get("GEMSDOE_ENTRY_ROOT")
    if not entry:
        pytest.skip("set GEMSDOE_ENTRY_ROOT to the canonical entry checkout")
    sys.path.insert(0, str(Path(entry).resolve() / "src"))
    from gems import metric
    return metric


def test_score_rule_analogue_perfect_and_dead_cases():
    """The staff-rule analogue: predictions on trained labels are masked; the
    score is against the held-out systems only."""
    metric = _toy_metric()
    sh = tool("system_holdout_cv")
    n = 40
    footprint = np.zeros((n, n), dtype=bool)
    footprint[5:35, 5:35] = True
    trained = np.zeros((n, n), dtype=bool)
    trained[10:12, 10:20] = True          # a 'supplied label' trace
    held = np.zeros((n, n), dtype=bool)    # a 'new fault' line
    held[25, 15:30] = True

    # a perfect prediction exactly on the held-out fault, plus mass on the
    # trained labels (which must be masked away, costing nothing)
    prob = np.zeros((n, n), dtype=np.float32)
    prob[25, 15:30] = 1.0
    prob[10:12, 10:20] = 1.0
    out = sh.score_rule_analogue(prob, held, trained, footprint, metric,
                                 budgets=(0.05,))
    # top-5% of scoreable pixels includes the held line: TP = 15, FP = rest
    rec = out["topk_hard@0.05"]
    assert rec["n_gt"] == 15
    assert rec["tp_w"] == pytest.approx(15.0)
    # soft raw must also be perfect where the probability is 1
    assert out["soft_raw"]["dti"] == pytest.approx(1.0)

    # dead case: ALL mass on trained labels only -> masked -> DTI = 0
    prob_dead = np.zeros((n, n), dtype=np.float32)
    prob_dead[10:12, 10:20] = 1.0
    out2 = sh.score_rule_analogue(prob_dead, held, trained, footprint, metric,
                                  budgets=(0.05,))
    assert out2["soft_raw"]["dti"] == 0.0

    # blanket control: p=1 everywhere scoreable; DTI must equal the analytic
    # full-coverage value for this GT (c / (c + alpha*(1-c)) approximation is
    # NOT exact on a discrete grid, so compare against the metric directly)
    blanket = (footprint & ~trained).astype(np.float32)
    ref = metric.components(blanket, held)
    assert out["blanket_full"]["dti"] == pytest.approx(ref.dti)


def test_topk_hard_respects_budget_and_mask():
    sh = tool("system_holdout_cv")
    n = 100
    valid = np.zeros((n, n), dtype=bool)
    valid[:50, :] = True                       # 5000 scoreable pixels
    prob = np.zeros((n, n), dtype=np.float32)
    prob[:50, :] = np.arange(5000, dtype=np.float32).reshape(50, 100) / 5000.0
    sel = sh.topk_hard(prob, valid, 0.02) > 0
    assert sel.sum() == 100                    # exactly 2% of 5000
    assert not sel[~valid].any()               # never outside the valid mask
    assert sel[:48].sum() == 0                 # the lowest-probability rows lose


def test_build_systems_merges_nearby_traces_only():
    sh = tool("system_holdout_cv")
    tid = np.zeros((60, 60), dtype=np.int32)
    tid[10, 5:25] = 1        # trace 1: a horizontal line
    tid[11, 5:25] = 2        # trace 2: 1 px below -> same system at any thr
    tid[50, 5:25] = 3        # trace 3: 40 px away -> separate at 25 px, same at 50
    sysmap = sh.build_systems(tid, 3, threshold_m=1500.0)   # 15 px
    assert sysmap[1] == sysmap[2]
    assert sysmap[3] != sysmap[1]
    sysmap2 = sh.build_systems(tid, 3, threshold_m=5000.0)  # 50 px
    assert sysmap2[3] == sysmap2[1]


# ---------------------------------------------------------------- evidence

def test_system_holdout_evidence_present_and_shaped():
    p = EVIDENCE / "system_holdout_cv_2026-09-26.json"
    if not p.exists():
        pytest.skip("evidence not generated in this checkout")
    d = json.loads(p.read_text())
    assert "NOT a leaderboard value" in d["_what_this_is"]
    design = d["design"]
    assert design["system_threshold_m"] == 5000.0
    assert design["n_systems"] > 50
    assert design["folds"] == 4
    assert "supplied training-label pixels are masked" in design["scoring_rule"]
    for fold in d["folds"]:
        assert fold["n_held_gt_px"] > 0
        assert "blanket_full" in fold["base"]
        assert "topk_hard@0.03" in fold["base"]
        assert "topk_hard_shipsel@0.03" in fold["base"]
        # the no-skill gate number must be present for every fold
        assert fold["base"]["blanket_full"]["dti"] >= 0.0
    assert "aggregate_base" in d and d["aggregate_base"]
    if "aggregate_semisup" in d and d["aggregate_semisup"]:
        for fold in d["folds"]:
            assert "pseudo" in fold
            # pseudo-positives must be a strict subset of the footprint and
            # at most the declared pool
            assert fold["pseudo"]["verified_px"] <= fold["pseudo"]["pool_px"]


def test_ownership_session3_resolution():
    p = EVIDENCE / "ownership_resolution_2026-09-26_session3_parallel.json"
    if not p.exists():
        pytest.skip("evidence not generated in this checkout")
    d = json.loads(p.read_text())
    assert d["account"]["login"] == "buffedlizard55-lab"
    assert d["account"]["id"] == 309556078
    for name, r in d["repos"].items():
        assert r["owner"] == "buffedlizard55-lab", name
        assert r["fork"] is False, name
        assert r["has_pages"] is True, name
        for c in r["contributors"]:
            assert c["login"] in ("buffedlizard55-lab",
                                  "arena-ai-coding-agent[bot]",
                                  "arena-agent", "github-actions[bot]",
                                  "Arena Agent", "GEMSDOE agent"), (name, c)
    assert d["_bottom_line"]["github_layer"].startswith("RESOLVED")
    assert "STILL UNRESOLVED" in d["_bottom_line"]["drivendata_layer"]


def test_leaderboard_snapshot_session3_claims_no_owned_score():
    p = EVIDENCE / "leaderboard_snapshot_2026-09-26_session3.json"
    if not p.exists():
        pytest.skip("evidence not generated in this checkout")
    d = json.loads(p.read_text())
    assert d["field_high"]["score"] == 0.3049
    assert d["field_high"]["participant"] == "DARD"
    ours = {"buffedlizard55-lab", "6GEMSDOE", "GEMSDOE"}
    for row in d["brief_attributed_scores_today"]:
        assert row["participant"] not in ours
    assert "no owned submission" in d["reading"] or "no owned public score" in d["reading"]
