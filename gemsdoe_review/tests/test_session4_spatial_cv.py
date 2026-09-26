"""Independent geometry/placement oracles for the replacement validation harness."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from scipy.spatial.distance import cdist

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
spec = importlib.util.spec_from_file_location('spatial_system_cv', TOOLS / 'spatial_system_cv.py')
cv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv)


def test_short_trace_bridge_was_not_allowed_to_disappear():
    # Global every-fourth sampling omits both intermediate traces, severing a
    # real transitive system. ALL pixels, including singleton traces, matter.
    traces = np.zeros((3, 15), np.int32)
    traces[1, [1, 4, 7, 10, 13]] = np.arange(1, 6)
    systems = cv.exact_systems(traces, 5, threshold_m=300)
    assert systems[0] == 0
    assert np.unique(systems[1:]).size == 1


def test_clustering_matches_all_pairs_oracle():
    rng = np.random.default_rng(83)
    for _ in range(10):
        traces = np.zeros((20, 23), np.int32)
        coords = rng.choice(traces.size, size=40, replace=False)
        traces.ravel()[coords] = np.repeat(np.arange(1, 11), 4)
        points = np.argwhere(traces > 0)
        ids = traces[traces > 0]
        graph = np.eye(11, dtype=bool)
        rr, cc = np.nonzero(cdist(points, points) <= 3)
        graph[ids[rr], ids[cc]] = True
        for k in range(1, 11):  # independent Floyd-Warshall reachability
            graph |= graph[:, k, None] & graph[None, k, :]
        actual = cv.exact_systems(traces, 10, threshold_m=300)
        assert np.array_equal(actual[:, None] == actual[None, :], graph)


def test_exact_threshold_and_empty_input():
    traces = np.zeros((7, 7), np.int32)
    traces[0, 0] = 1
    traces[3, 4] = 2
    assert cv.exact_systems(traces, 2, 500)[1] == cv.exact_systems(traces, 2, 500)[2]
    assert cv.exact_systems(traces, 2, 499)[1] != cv.exact_systems(traces, 2, 499)[2]
    assert cv.exact_systems(np.zeros((4, 4), np.int32), 0).tolist() == [0]


@pytest.mark.parametrize('blocks,folds', [(2, 4), (4, 4), (5, 3), (6, 4)])
def test_spatial_masks_against_pairwise_distance_oracle(blocks, folds):
    shape = (61, 63)
    footprint = np.ones(shape, bool)
    ids = cv.spatial_folds(shape, blocks, folds)
    systems = np.zeros(shape, int)
    systems[10, 10] = systems[45, 45] = 1  # same system across geography
    seen = np.zeros(shape, int)
    for k in range(folds):
        train, score, held = cv.purged_masks(footprint, systems, ids, k)
        seen += score
        assert not (train & score).any()
        if train.any():
            distances = cdist(np.argwhere(train), np.argwhere(score))
            assert distances.min() > 3  # includes diagonal corners
            if held.any():
                assert cdist(np.argwhere(train), np.argwhere(held)).min() > 3
        assert not (train & held).any()
    assert (seen == 1).all()


def test_system_touching_score_is_purged_globally_with_its_negatives():
    footprint = np.ones((40, 40), bool)
    systems = np.zeros((40, 40), int)
    systems[8, 8] = systems[30, 30] = 1
    ids = cv.spatial_folds(footprint.shape)
    train, score, held = cv.purged_masks(footprint, systems, ids, 0)
    assert held[30, 30]
    assert not train[30, 30]  # positive removed far beyond test block
    assert not train[31, 31]  # adjacent negative removed too
    assert not train[21, 21]  # sqrt(2**2 + 2**2) from block's last pixel
    assert train[25, 35]


@pytest.mark.parametrize('spacing', [1, 4, 5])
def test_budget_and_minimum_spacing_not_flattened_subsampling(spacing):
    rng = np.random.default_rng(9)
    p = rng.random((70, 80)).astype(np.float32)
    valid = np.ones(p.shape, bool)
    valid[:3] = False
    a = cv.budget_nodes(p, valid, spacing=spacing)
    assert np.array_equal(a, cv.budget_nodes(p, valid, spacing=spacing))
    assert not a[~valid].any()
    assert int(a.sum()) <= round(0.03 * valid.sum())
    coords = np.argwhere(a > 0)
    d = cdist(coords, coords, metric='chebyshev')
    np.fill_diagonal(d, np.inf)
    assert d.min() >= spacing
    if spacing == 1:
        assert a.sum() == round(0.03 * valid.sum())


def test_ties_empty_and_bad_probability_fail_closed():
    p = np.ones((10, 10), np.float32)
    valid = np.ones(p.shape, bool)
    a = cv.budget_nodes(p, valid, fraction=0.03)
    assert np.flatnonzero(a).tolist() == [0, 1, 2]  # no tie-driven blanket
    assert not cv.budget_nodes(p, ~valid).any()
    p[0, 0] = np.nan
    with pytest.raises(ValueError, match='finite probabilities'):
        cv.budget_nodes(p, valid)
    p[0, 0] = 1.1
    with pytest.raises(ValueError):
        cv.budget_nodes(p, valid)


@pytest.mark.parametrize('kwargs', [{'buffer_px': 2}, {'buffer_px': float('nan')}])
def test_insufficient_or_nonfinite_buffer_rejected(kwargs):
    with pytest.raises(ValueError):
        cv.purged_masks(np.ones((8, 8), bool), np.zeros((8, 8), int),
                        cv.spatial_folds((8, 8)), 0, **kwargs)


def test_degenerate_folds_are_not_silently_averaged_away():
    footprint = np.ones((20, 20), bool)
    systems = np.zeros((20, 20), int)
    train, score, held = cv.purged_masks(footprint, systems, cv.spatial_folds((20, 20)), 0)
    with pytest.raises(ValueError, match='lacks training classes'):
        cv.audit_masks(train, score, systems, held, 3)


def test_metric_cannot_see_mass_or_truth_outside_test_area():
    entry = os.environ.get('GEMSDOE_ENTRY_ROOT')
    if not entry:
        pytest.skip('entry metric not available')
    sys.path.insert(0, str(Path(entry) / 'src'))
    from gems import metric
    p = np.zeros((30, 30), np.float32)
    truth = np.zeros((30, 30), bool)
    truth[5, 5] = truth[20, 20] = True
    score = np.zeros((30, 30), bool)
    score[:15, :15] = True
    p[5, 5] = 1
    first = cv.evaluate(p, truth, score, metric)
    p[~score] = 1
    second = cv.evaluate(p, truth, score, metric)
    assert first == second
    assert first['soft']['n_gt'] == 1
    assert first['soft']['dti'] == pytest.approx(1)


def test_retired_harness_cannot_accidentally_produce_new_cv_scores():
    result = subprocess.run([sys.executable, str(TOOLS / 'system_holdout_cv.py')], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'spatial_system_cv.py' in result.stderr


def test_geometry_evidence_is_complete_and_isolated():
    path = TOOLS.parent / 'evidence/spatial_system_geometry_session4.json'
    d = json.loads(path.read_text())
    assert d['complete'] and len(d['folds']) == 4
    assert d['n_exact_systems'] == 40  # all-pixel computation, not 317 sampled clusters
    for fold in d['folds']:
        g = fold['geometry']
        assert g['train_test_overlap'] == g['train_pixels_within_buffer_of_score'] == g['train_held_system_overlap'] == 0
        assert g['shared_positive_systems'] == []


def test_archive_provenance_never_inherits_parent_repo_head():
    import tempfile
    audit_spec = importlib.util.spec_from_file_location('feature_priorities_audit', TOOLS / 'feature_priorities_audit.py')
    audit = importlib.util.module_from_spec(audit_spec)
    audit_spec.loader.exec_module(audit)
    with tempfile.TemporaryDirectory(dir=TOOLS.parent) as nested_archive:
        assert audit.entry_git_head(Path(nested_archive)) is None


def test_comparison_rejects_mismatched_or_incomplete_controls():
    import copy
    summary_spec = importlib.util.spec_from_file_location('summarize_spatial_cv', TOOLS / 'summarize_spatial_cv.py')
    summary = importlib.util.module_from_spec(summary_spec)
    summary_spec.loader.exec_module(summary)
    evidence = TOOLS.parent / 'evidence'
    models = json.loads((evidence / 'spatial_system_ablation_session4.json').read_text())
    controls = json.loads((evidence / 'spatial_controls_session4.json').read_text())
    result = summary.summarize(models, controls)
    full = {r['policy']: r for r in result['rows'] if r['model'] == 'full88'}
    assert full['budget03_spacing4']['beats_all_null_seeds_every_fold']
    assert full['budget03_spacing4']['identical_actual_budget']
    assert not full['budget03_spacing1']['beats_all_null_seeds_every_fold']
    assert not full['budget03_spacing5']['identical_actual_budget']
    for mutation in ['incomplete', 'mask', 'seed', 'fold']:
        bad = copy.deepcopy(controls)
        if mutation == 'incomplete':
            bad['complete'] = False
        elif mutation == 'mask':
            bad['folds'][0]['score_mask_sha256'] = 'wrong'
        elif mutation == 'seed':
            bad['folds'][0]['controls'].pop()
        else:
            bad['folds'][1]['fold'] = bad['folds'][0]['fold']
        with pytest.raises(ValueError):
            summary.summarize(models, bad)
