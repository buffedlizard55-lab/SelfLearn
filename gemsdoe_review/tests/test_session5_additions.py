#!/usr/bin/env python3
"""Session-5 regressions.

Split into three groups, in the same style as the earlier session files:

  * pure-numpy oracles that always run (no entry checkout, no network);
  * evidence pins that re-derive the session-5 JSON from its own sources;
  * entry-rooted tests that skip when GEMSDOE_ENTRY_ROOT is not available.

Nothing here uploads, publishes or registers anything.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
ENTRY = Path(os.environ.get("GEMSDOE_ENTRY_ROOT", "/home/user/entry-src"))

needs_entry = pytest.mark.skipif(
    not (ENTRY / "src" / "gems" / "spec.py").exists(),
    reason="GEMSDOE_ENTRY_ROOT not available (no entry checkout)")


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_evidence(name: str) -> dict:
    path = EVIDENCE / name
    assert path.is_file(), f"missing session-5 evidence: {name}"
    return json.loads(path.read_text())


# --------------------------------------------------------------- DTI oracle
# A deliberately independent implementation of the published formula (page 967)
# so the metric claims are checked against a second code path, not against the
# entry's own module alone.

def dti(pred: np.ndarray, gt: np.ndarray, radius_px: float = 3.0,
        alpha: float = 0.2, beta: float = 0.8) -> tuple[float, float, float]:
    from scipy import ndimage
    p = np.clip(np.asarray(pred, float), 0.0, 1.0)
    g = np.asarray(gt, bool)
    n_gt = int(g.sum())
    if n_gt == 0:
        return 0.0, float((p > 0).sum()), 0.0
    d_to_gt = ndimage.distance_transform_edt(~g, sampling=1.0)
    k_near = np.maximum(1.0 - d_to_gt / radius_px, 0.0)
    fp = float((p * (1.0 - k_near))[p > 0].sum())
    best = np.zeros_like(p)
    r = int(np.ceil(radius_px))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = float(np.hypot(dy, dx))
            if d > radius_px:
                continue
            k = max(1.0 - d / radius_px, 0.0)
            shifted = np.zeros_like(p)
            ys_src = slice(max(0, -dy), p.shape[0] - max(0, dy))
            ys_dst = slice(max(0, dy), p.shape[0] - max(0, -dy))
            xs_src = slice(max(0, -dx), p.shape[1] - max(0, dx))
            xs_dst = slice(max(0, dx), p.shape[1] - max(0, -dx))
            shifted[ys_dst, xs_dst] = p[ys_src, xs_src]
            np.maximum(best, shifted * k, out=best)
    tp = float(best[g].sum())
    fn = float((1.0 - best[g]).sum())
    denom = tp + alpha * fp + beta * fn
    return (tp / denom if denom > 0 else 0.0), fp, fn


def test_uniform_rescaling_is_monotone_but_hardening_is_not():
    """Claim 1 (uniform rescaling) holds; claim 2 (hardening always helps) does not.

    This is the exact sentence the live 6GEMSDOE page still publishes.
    """
    g = np.zeros((13, 13), bool)
    p = np.zeros((13, 13), float)
    g[6, 6] = True
    p[6, 6] = 0.4
    p[9, 9] = 0.3
    lam = np.linspace(0.2, 2.5, 24)
    lam = lam[lam <= 1.0 / p.max()]
    scores = [dti(np.clip(p * l, 0, 1), g)[0] for l in lam]
    assert all(b > a for a, b in zip(scores, scores[1:])), scores

    g2 = np.zeros((13, 13), bool)
    p2 = np.zeros((13, 13), float)
    g2[2, 2] = True
    p2[2, 2] = 1.0
    p2[9, 9] = 0.01
    soft, _, _ = dti(p2, g2)
    hard, _, _ = dti((p2 > 0).astype(float), g2)
    assert soft > hard, (soft, hard)
    assert soft == pytest.approx(0.998004, abs=1e-6)
    assert hard == pytest.approx(0.833333, abs=1e-6)


@needs_entry
def test_metric_claim_evidence_matches_the_canonical_metric():
    """The recorded counterexample must reproduce under the entry's own metric."""
    sys.path.insert(0, str(ENTRY / "src"))
    from gems import metric  # noqa: PLC0415
    data = read_evidence("metric_claim_check_session5.json")
    case = data["claim_2_hardening_always_helps"]["counterexample"]
    g = np.zeros((13, 13), bool)
    p = np.zeros((13, 13), float)
    g[2, 2] = True
    p[2, 2] = 1.0
    p[9, 9] = 0.01
    assert metric.components(p, g).dti == pytest.approx(case["soft"]["dti"], abs=1e-12)
    assert metric.components((p > 0).astype(float), g).dti == pytest.approx(case["hard"]["dti"], abs=1e-12)
    assert data["claim_1_uniform_rescaling_is_monotone"]["measured"] is True
    assert data["claim_2_hardening_always_helps"]["counterexample"]["hardening_lost"] is True


# ------------------------------------------------------- budget_nodes oracle

def test_budget_nodes_exact_budget_and_minimum_spacing():
    cv = load_tool("spatial_system_cv")
    rng = np.random.default_rng(11)
    prob = rng.random((40, 37)).astype(np.float32)
    valid = np.ones_like(prob, bool)
    budget = max(1, int(round(0.03 * valid.sum())))
    dense = cv.budget_nodes(prob, valid, fraction=0.03, spacing=1)
    spaced = cv.budget_nodes(prob, valid, fraction=0.03, spacing=4)
    assert int(dense.sum()) == budget == int(spaced.sum())
    ys, xs = np.nonzero(spaced > 0)
    gaps = np.abs(ys[:, None] - ys[None, :]) + np.abs(xs[:, None] - xs[None, :])
    cheb = np.maximum(np.abs(ys[:, None] - ys[None, :]), np.abs(xs[:, None] - xs[None, :]))
    assert cheb[~np.eye(len(ys), dtype=bool)].min() >= 4, "spacing 4 must be a minimum separation"
    assert int(spaced.sum()) <= int(dense.sum())
    # deterministic: identical inputs, identical bytes
    assert np.array_equal(spaced, cv.budget_nodes(prob, valid, fraction=0.03, spacing=4))
    # the dense policy is exactly the top-k prefix in probability order
    order = np.argsort(-prob.ravel(), kind="stable")[:budget]
    assert set(np.flatnonzero(dense.ravel())) == set(order.tolist())


def test_budget_nodes_spacing5_can_underfill_and_is_reported():
    cv = load_tool("spatial_system_cv")
    prob = np.zeros((9, 9), np.float32)
    prob[:] = np.linspace(0.9, 0.1, 81).reshape(9, 9)
    valid = np.ones_like(prob, bool)
    out = cv.budget_nodes(prob, valid, fraction=0.5, spacing=5)
    assert 0 < int(out.sum()) < int(round(0.5 * valid.sum())), "packing can underfill; report it"


def test_budget_nodes_rejects_bad_input():
    cv = load_tool("spatial_system_cv")
    valid = np.ones((5, 5), bool)
    with pytest.raises(ValueError):
        cv.budget_nodes(np.zeros((5, 5)), valid, fraction=0.0)
    with pytest.raises(ValueError):
        cv.budget_nodes(np.zeros((5, 5)), valid, fraction=0.5, spacing=0)
    with pytest.raises(ValueError):
        cv.budget_nodes(np.full((5, 5), 2.0), valid, fraction=0.5)
    with pytest.raises(ValueError):
        cv.budget_nodes(np.zeros((4, 4)), np.ones((5, 5), bool), fraction=0.5)


# ------------------------------------------------------------- evidence pins

def test_ownership_audit_resolves_the_brief_sites_and_flags_the_new_repo():
    data = read_evidence("ownership_resolution_2026-09-26_session5.json")
    findings = data["findings"]
    assert findings["single_github_owner"] is True
    assert findings["owner_ids"] == [309556078]
    assert findings["fork_repos"] == [] and findings["archived_repos"] == []
    assert findings["designated_entry"] == "6GEMSDOE"
    repos = data["repositories"]
    for site in ("5GEMSDOE", "GEMSDOE4", "6GEMSDOE"):
        assert repos[site]["owner_login"] == "buffedlizard55-lab"
        assert repos[site]["fork"] is False
        assert repos[site]["pages_status"] == "built"
    # the brief's three "unconfirmed" sites are our own GitHub history ...
    assert set(data["brief_unconfirmed_sites"]) == {"5GEMSDOE", "GEMSDOE4", "6GEMSDOE"}
    # ... but the DrivenData layer stays unresolved and says so
    assert "UNRESOLVED" in data["drivendata_layer"]["status"]
    assert data["drivendata_layer"]["no_action_taken"]
    # irregularity: a 12th GEMS-named repo appeared inside the audit window
    recent = findings["created_since_finding"]
    assert "LEARNGEMSDOE" in recent
    assert recent["LEARNGEMSDOE"] >= "2026-09-26T00:00:00Z"
    assert "NOT created by this session" in findings["new_repo_irregularity"]


def test_leaderboard_snapshot_matches_its_raw_transcript():
    tool = load_tool("leaderboard_snapshot")
    raw = EVIDENCE / "leaderboard_raw_2026-09-26_session5.md"
    rows = tool.parse(raw.read_text())
    snap = read_evidence("leaderboard_snapshot_2026-09-26_session5.json")
    assert [r["rank"] for r in rows] == list(range(1, len(rows) + 1))
    assert len(rows) == snap["rows_visible"] == 50
    assert snap["field_high"]["participant"] == "DARD"
    assert snap["field_high"]["score"] == 0.3049
    assert snap["organizer_row"]["participant"] == "doegemsDrivendata"
    assert snap["organizer_row"]["score"] == 0.1847
    assert snap["reading"]["owned_public_score"] is None


def test_brief_scores_belong_to_other_entrants_and_one_has_left_the_board():
    snap = read_evidence("leaderboard_snapshot_2026-09-26_session5.json")
    attributed = {a["score"]: a for a in snap["brief_attributed_scores_today"]}
    assert {h["participant"] for h in attributed[0.1563]["rows_on_board_today"]} == {"extradr19", "SDCF9"}
    assert attributed[0.1560]["rows_on_board_today"][0]["participant"] == "smashi34"
    assert attributed[0.1193]["rows_on_board_today"][0]["participant"] == "smrtdoog5"
    assert attributed[0.0830]["rows_on_board_today"][0]["participant"] == "wbg1"
    assert attributed[0.1152]["rows_on_board_today"] == []
    assert "NOT on the visible board" in attributed[0.1152]["reading"]
    # no row anywhere on the board is attributed to this workspace
    assert all(r["participant"] not in ("buffedlizard55-lab", "6GEMSDOE") for r in snap["rows"])


def test_entry_doc_check_findings_are_recorded_verbatim():
    offline = (EVIDENCE / "entry_docs_offline_session5.txt").read_text()
    online = (EVIDENCE / "entry_docs_online_session5.txt").read_text()
    assert "35/37 checks passed" in offline
    assert "47/51 checks passed" in online
    for needle in ("limitations-cover-masking", "geology-dossier-present"):
        assert f"[FAIL] {needle}" in offline
    # the new repo made the entry's own checker fail two more checks
    assert "[FAIL] account-repo-count" in online
    assert "[FAIL] account-table-LEARNGEMSDOE" in online


def test_rank_tables_pin_is_unreproducible_by_design():
    data = read_evidence("rank_tables_pin_audit_session5.json")
    assert data["content_identical_ignoring_built_utc"] is True
    assert data["raster_pin_reproduced"] is True
    assert data["pinned_rank_tables_sha256"] == \
        "64a62c3b3e9925ba19a43276af1d931863d81906d26f0b06c8fb74f3fe53c0ae"
    assert data["rebuilt_rank_tables_sha256"]["before"] != data["pinned_rank_tables_sha256"]
    assert data["rebuilt_rank_tables_sha256"]["before"] != data["rebuilt_rank_tables_sha256"]["after"]
    assert "unreproducible" in data["finding"]


def test_submission_gate_and_poison_evidence_are_consistent():
    gate = read_evidence("submission_gate_session5.json")["result"]
    poison = read_evidence("nan_poison_session5.json")["result"]
    assert gate["ok"] is True and len(gate["checks"]) == 13
    assert poison["ok"] is False and len(poison["checks"]) == 13
    names = {c["name"]: c for c in gate["checks"]}
    assert names["NAN-INSIDE-FOOTPRINT"]["ok"] is True
    assert names["values-in-0-1"]["ok"] is True
    assert names["footprint-matches-official"]["ok"] is True
    bad = {c["name"]: c for c in poison["checks"]}
    assert bad["NAN-INSIDE-FOOTPRINT"]["ok"] is False
    assert bad["values-in-0-1"]["ok"] is True, "the range check must NOT be what catches it"


def test_shipping_geometry_is_isolated_on_every_layout():
    path = EVIDENCE / "spatial_system_geometry_session5.json"
    if not path.is_file():
        pytest.skip("shipping geometry evidence not copied into the repo yet")
    data = json.loads(path.read_text())
    assert data["layouts"], "no layouts recorded"
    for layout, payload in data["layouts"].items():
        assert payload["n_exact_systems"] == 40, layout
        assert payload["n_traces"] == 3199, layout
        for record in payload["folds"]:
            g = record["geometry"]
            assert g["train_test_overlap"] == 0, layout
            assert g["train_pixels_within_buffer_of_score"] == 0, layout
            assert g["train_held_system_overlap"] == 0, layout
            assert g["shared_positive_systems"] == [], layout
            assert g["train_positive_pixels"] > 0 and g["score_positive_pixels"] > 0


def test_shipped_dossier_reproduces_byte_identically_from_pinned_bytes():
    """The shipped artifact's geological reasoning is a committed fact, not a stale one."""
    data = read_evidence("shipped_geology_rerun_session5.json")
    repro = data["reproduced"]
    assert repro["rendered_markdown_byte_identical"] is True
    assert repro["fragment_csv_sha256_identical"] is True
    assert repro["dossier_json_identical_except_generated_utc_and_fragment_filename"] is True
    assert repro["fragment_inventory_only_differs_by_filename"] is True
    assert data["counts"]["candidates"] == 180
    assert data["counts"]["components"] == 2589
    assert data["counts"]["class_counts"]["halo"] == 92
    assert data["artifact"] == "gems6_hgb88-topk03_33cec71ff0.tif"


def test_candidate_dossier_counts_match_the_candidate_report():
    """The committed candidate dossier and the gate evidence describe the same file."""
    report = read_evidence("candidate_spacing4_report_session5.json")
    gate = read_evidence("submission_gate_candidate_session5.json")
    dossier = json.loads((EVIDENCE / "spacing4_candidate_geology_2026-09-26.json").read_text())
    assert gate["sha256"] == report["sha256"] == dossier["input_sha256"]["submission"]
    assert gate["gate_ok"] is True and len(gate["gate"]["checks"]) == 13
    assert dossier["counts"]["candidates"] == 943
    assert dossier["counts"]["components"] - dossier["counts"]["candidates"] == 31410 - 943
    assert sum(c["emitted_pixels"] for c in dossier["candidates"]) < gate["positive_pixels"]
    classes = {c["class"] for c in dossier["candidates"]}
    assert classes == {"isolated", "near_trace", "halo"}, classes
    assert sum(1 for c in dossier["candidates"] if c["class"] == "isolated") == 491


def test_candidate_geology_note_quotes_only_measured_numbers():
    """Every number in the hand-written reading must exist in the committed dossier."""
    note = (EVIDENCE / "spacing4_candidate_geology_session5.md").read_text()
    dossier = json.loads((EVIDENCE / "spacing4_candidate_geology_2026-09-26.json").read_text())
    by_id = {c["candidate_id"]: c for c in dossier["candidates"]}
    for cid in (20871, 21434, 24935, 24431, 14713, 16651):
        assert f"### {cid} " in note, cid
        assert cid in by_id
    # the note's headline class counts
    assert note.count("491") >= 1 and "4,106" in note and "23,605" in note
    # and its honest limits are stated, not implied
    flat = " ".join(note.split())
    assert "No depth" in flat and "not statistically independent" in flat


@needs_entry
def test_session3_patch_applies_to_the_entry_revision_and_fixes_the_dilation():
    import subprocess
    patches = Path(__file__).resolve().parents[1] / "patches"
    evidence = read_evidence("entry_patch_verification_session5.json")
    assert evidence["entry_revision"] == "e2fe3f4"
    full = patches / "session3_entry_full_2026-09-26.patch"
    assert full.is_file()
    check = subprocess.run(["git", "apply", "--check", str(full)], cwd=ENTRY,
                           capture_output=True, text=True)
    assert check.returncode == 0, check.stderr
    # and the recorded defect in the small standalone patch is real, not assumed
    small = patches / "cv_euclidean_buffer.patch"
    small_check = subprocess.run(["git", "apply", "--check", str(small)], cwd=ENTRY,
                                 capture_output=True, text=True)
    # session 5 recorded the small patch as stale (historical record, kept) ...
    assert evidence["patches"]["cv_euclidean_buffer.patch"]["applies_cleanly"] is False
    # ... session 6 regenerated it against the same revision; it must now apply
    s6 = read_evidence("entry_patch_verification_session6.json")
    assert s6["entry_revision"] == "e2fe3f4"
    assert s6["patches"]["cv_euclidean_buffer.patch"]["applies_cleanly"] is True
    assert small_check.returncode == 0, small_check.stderr


def test_shipping_decision_rule_is_predeclared_in_the_tool():
    source = (TOOLS / "shipping_budget_confirmation.py").read_text()
    assert "H1_primary" in source and "H2_sensitivity" in source
    assert "not upload permission" in source
    assert "Pre-specified decision rule" in source
