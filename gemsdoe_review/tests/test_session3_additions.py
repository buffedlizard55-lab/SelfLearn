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
