#!/usr/bin/env python3
"""Spatial block CV with exact whole-system purging, never a random pixel split.

Replaces the session-3 system-holdout diagnostic: that diagnostic trained on
negatives in its scoring area, allowed pseudo-label training there, and clustered
only every fourth fault pixel. Its scores are not clean spatial CV estimates.

Default: four geographic quadrants, 300 m Euclidean train exclusion, and removal
of EVERY system touching a test quadrant from training (including its buffer).
Systems are exact transitive clusters of raster traces within 5 km. Systems may
touch multiple test quadrants, so folds are not independent system replicates.
Only test-area labels/predictions are scored. This is a mapped-fault transfer
proxy, not hidden truth. No pseudo-labels or submission artifacts are produced.

Example:
  python spatial_system_cv.py --entry /path/to/6GEMSDOE --audit-only --out split.json
  python spatial_system_cv.py --entry /path/to/6GEMSDOE --out scores.json

Freeze policies before running; do not pick a submission on these diagnostic
folds. A GPU model must use the same masks, with additional patch/receptive-field
exclusion if its input support exceeds the buffer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.spatial import cKDTree


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def exact_systems(trace_id, n_trace, threshold_m=5000.0, pixel_m=100.0):
    """Exact all-pixel single-linkage, bounded query batches; no subsampling.

    Dense ids 1..n_trace must all exist. Background maps to zero. Does not
    materialize the potentially quadratic complete pixel-pair graph.
    """
    if not np.isfinite(threshold_m) or threshold_m < 0 or not np.isfinite(pixel_m) or pixel_m <= 0:
        raise ValueError('finite nonnegative threshold and positive pixel size required')
    if trace_id.ndim != 2 or not np.issubdtype(trace_id.dtype, np.integer):
        raise ValueError('trace_id must be a two-dimensional integer array')
    present = np.unique(trace_id)
    if n_trace < 0 or np.any(present < 0) or not np.array_equal(present[present > 0], np.arange(1, n_trace + 1)):
        raise ValueError('trace ids must be dense 1..n_trace')
    coords = np.argwhere(trace_id > 0)
    ids = trace_id[trace_id > 0]
    parent = np.arange(n_trace + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    if len(coords):
        tree = cKDTree(coords)
        for start in range(0, len(coords), 256):
            neighbors = tree.query_ball_point(coords[start:start + 256], threshold_m / pixel_m)
            for offset, near in enumerate(neighbors):
                root = find(int(ids[start + offset]))
                for other in np.unique(ids[near]):
                    other_root = find(int(other))
                    if root != other_root:
                        parent[other_root] = root
    roots = np.array([find(i) for i in range(1, n_trace + 1)])
    out = np.zeros(n_trace + 1, dtype=np.int32)
    if n_trace:
        out[1:] = np.unique(roots, return_inverse=True)[1] + 1
    return out


def spatial_folds(shape, n_blocks=2, n_folds=4):
    if len(shape) != 2 or n_blocks < 1 or n_blocks > min(shape) or not 2 <= n_folds <= n_blocks ** 2:
        raise ValueError('nonempty blocks and at least two folds required')
    row = np.arange(shape[0]) * n_blocks // shape[0]
    col = np.arange(shape[1]) * n_blocks // shape[1]
    return (row[:, None] * n_blocks + col[None, :]) % n_folds


def purged_masks(footprint, system_of_pixel, fold_ids, fold, buffer_px=3):
    """Return train, score, held-system mask; purge both classes, globally.

    The geographic test block (even its out-of-footprint portion) is excluded
    from training with a true Euclidean buffer. Entire held systems outside the
    test block also receive the same buffer. No held labels become negatives.
    """
    if buffer_px < 3 or not np.isfinite(buffer_px):
        raise ValueError('buffer must cover at least the 3 px metric kernel')
    if footprint.dtype != bool or footprint.shape != system_of_pixel.shape or footprint.shape != fold_ids.shape:
        raise ValueError('aligned masks and boolean footprint required')
    test = fold_ids == fold
    if not test.any():
        raise ValueError('fold has no test blocks')
    score = test & footprint
    held_ids = np.unique(system_of_pixel[score])
    held_ids = held_ids[held_ids > 0]
    held_system = np.isin(system_of_pixel, held_ids) & (system_of_pixel > 0)
    exclusion = test | held_system
    distance = ndimage.distance_transform_edt(~exclusion)
    train = footprint & (distance > buffer_px)
    return train, score, held_system


def audit_masks(train, score, systems, held_system, buffer_px):
    distance = ndimage.distance_transform_edt(~score)
    train_ids = np.unique(systems[train & (systems > 0)])
    test_ids = np.unique(systems[score & (systems > 0)])
    rec = {
        'train_pixels': int(train.sum()), 'score_pixels': int(score.sum()),
        'train_positive_pixels': int((train & (systems > 0)).sum()),
        'score_positive_pixels': int((score & (systems > 0)).sum()),
        'train_test_overlap': int((train & score).sum()),
        'train_pixels_within_buffer_of_score': int((train & (distance <= buffer_px)).sum()),
        'train_held_system_overlap': int((train & held_system).sum()),
        'shared_positive_systems': np.intersect1d(train_ids, test_ids).tolist(),
        'held_systems': test_ids.tolist(),
        'train_mask_sha256': hashlib.sha256(np.packbits(train).tobytes()).hexdigest(),
        'score_mask_sha256': hashlib.sha256(np.packbits(score).tobytes()).hexdigest(),
    }
    if (rec['train_test_overlap'] or rec['train_pixels_within_buffer_of_score'] or
            rec['train_held_system_overlap'] or rec['shared_positive_systems']):
        raise ValueError(f'CV isolation failed: {rec}')
    if not rec['train_positive_pixels'] or not rec['score_positive_pixels'] or not (train & (systems == 0)).any():
        raise ValueError('fold lacks training classes or held-out truth; do not silently drop it')
    return rec


def budget_nodes(prob, valid, fraction=0.03, spacing=1):
    """Fixed maximum budget; deterministic probability order, square suppression.

    spacing=1 is dense top-k; spacing=4/5 enforces MINIMUM Chebyshev separation,
    not maximum along-trace gaps or guaranteed kernel coverage. Report actual
    emitted count: packing constraints can underfill the requested budget.
    """
    if not 0 < fraction <= 1 or not isinstance(spacing, int) or spacing < 1:
        raise ValueError('fraction in (0,1] and integer spacing >=1 required')
    if prob.shape != valid.shape or valid.dtype != bool:
        raise ValueError('aligned probability and boolean valid mask required')
    if not np.isfinite(prob[valid]).all() or ((prob[valid] < 0) | (prob[valid] > 1)).any():
        raise ValueError('finite probabilities in [0,1] required inside score area')
    flat = np.flatnonzero(valid)
    out = np.zeros(prob.shape, dtype=np.float32)
    if not flat.size:
        return out
    budget = max(1, int(round(fraction * flat.size)))
    order = flat[np.argsort(-prob.ravel()[flat], kind='stable')]
    if spacing == 1:
        out.ravel()[order[:budget]] = 1
        return out
    blocked = np.zeros(valid.shape, dtype=bool)
    h, w = valid.shape
    radius = spacing - 1
    emitted = 0
    for idx in order:
        r, c = divmod(int(idx), w)
        if blocked[r, c]:
            continue
        out[r, c] = 1
        blocked[max(0, r-radius):min(h, r+radius+1), max(0, c-radius):min(w, c+radius+1)] = True
        emitted += 1
        if emitted == budget:
            break
    return out


def evaluate(prob, truth, score, metric):
    """All mass/GT outside the held geographic area is zero, before kernels."""
    gt = truth & score
    result = {}
    surfaces = {'blanket': score.astype(np.float32),
                'soft': np.where(score, prob, 0).astype(np.float32)}
    for spacing in (1, 4, 5):
        surfaces[f'budget03_spacing{spacing}'] = budget_nodes(prob, score, spacing=spacing)
    for name, pred in surfaces.items():
        if (pred[~score] != 0).any():
            raise ValueError('prediction leaked beyond scoring area')
        result[name] = {**metric.components(pred, gt).as_dict(),
                        'emitted_pixels': int((pred > 0).sum())}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--entry', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--audit-only', action='store_true')
    ap.add_argument('--blocks', type=int, default=2)
    ap.add_argument('--folds', type=int, default=4)
    ap.add_argument('--buffer-px', type=float, default=3)
    ap.add_argument('--system-threshold-m', type=float, default=5000)
    ap.add_argument('--max-neg', type=int, default=50000)
    ap.add_argument('--iters', type=int, default=100)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--configs', nargs='+', choices=['raw19', 'full88', 'drop2'], default=['raw19', 'full88', 'drop2'])
    args = ap.parse_args()
    if args.max_neg <= 0 or args.iters <= 0:
        ap.error('training budgets must be positive')
    entry = args.entry.resolve()
    sys.path.insert(0, str(entry / 'src'))
    from gems import metric, spec
    pins = {}
    for name in ('labels.tif', 'sample_submission.tif', 'training_features.tif'):
        expected = spec.PINS[name]['sha256']
        actual = sha256(entry / 'data' / name)
        if actual != expected:
            raise ValueError(f'{name}: official pin mismatch')
        pins[name] = actual
    with rasterio.open(entry / 'data/labels.tif') as src:
        gt = src.read(1) == 1
    with rasterio.open(entry / 'data/sample_submission.tif') as src:
        footprint = np.isfinite(src.read(1))
    traces, n = ndimage.label(gt, structure=np.ones((3, 3), int))
    lookup = exact_systems(traces, n, args.system_threshold_m)
    systems = lookup[traces]
    fold_ids = spatial_folds(gt.shape, args.blocks, args.folds)
    print(f'{n} traces -> {lookup.max()} exact systems', flush=True)
    meta = None
    mm = None
    if not args.audit_only:
        meta = json.loads((entry / 'data/evidence/features_meta.json').read_text())
        if meta['features_sha256'] != pins['training_features.tif']:
            raise ValueError('feature stack source mismatch')
        mm = np.load(entry / 'data/evidence/features.f32.npy', mmap_mode='r')
        if mm.shape != (*gt.shape, len(meta['channels'])) or len(meta['channels']) < 88:
            raise ValueError('feature stack geometry mismatch')
        from sklearn.ensemble import HistGradientBoostingClassifier
    output = {'kind': 'spatial-system-purged mapped-fault proxy; NOT a leaderboard score',
              'design': vars(args) | {'entry': str(entry), 'out': str(args.out)},
              'official_sha256': pins, 'tool_sha256': sha256(__file__),
              'n_traces': n, 'n_exact_systems': int(lookup.max()), 'folds': [],
              'limitations': ['Quadrant boundary clipping excludes cross-boundary metric credit.',
                             'Test-touching systems can recur across folds; folds are not independent system replicates.',
                             'No pseudo-labels. Random sampling is within spatially isolated TRAIN negatives only.',
                             'Known catalogue faults are the proxy truth, not new expert faults.',
                             'Feature transforms use unlabeled whole-region context; CNN input windows need additional exclusion.',
                             'Reduced-budget diagnostic, not shipping-scale selection or evidence of hidden-score improvement.']}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    for k in range(args.folds):
        train, score, held = purged_masks(footprint, systems, fold_ids, k, args.buffer_px)
        record = {'fold': k, 'geometry': audit_masks(train, score, systems, held, args.buffer_px), 'models': {}}
        print(f'fold {k}: {record["geometry"]["train_positive_pixels"]} train positives, {record["geometry"]["score_positive_pixels"]} test positives', flush=True)
        if not args.audit_only:
            pos = np.flatnonzero((train & gt).ravel())
            pool = np.flatnonzero((train & ~gt).ravel())
            neg = np.random.default_rng(args.seed + k).choice(pool, min(args.max_neg, len(pool)), replace=False)
            sel = np.concatenate([pos, neg])
            rows, cols = np.unravel_index(sel, gt.shape)
            y = gt[rows, cols].astype(np.uint8)
            for config in args.configs:
                channels = list(range(19 if config == 'raw19' else 88))
                if config == 'drop2':
                    channels = [i for i in channels if meta['channels'][i] not in ('mag_tilt', 'mag_asa')]
                X = np.asarray(mm[rows, cols, :88][:, channels], dtype=np.float32)
                model = HistGradientBoostingClassifier(max_iter=args.iters, learning_rate=0.08, max_leaf_nodes=31,
                          min_samples_leaf=40, l2_regularization=1, random_state=args.seed + k, early_stopping=False)
                model.fit(X, y)
                del X
                prob = np.zeros(gt.shape, dtype=np.float32)
                rr, cc = np.nonzero(score)
                for start in range(0, len(rr), 50000):
                    r, c = rr[start:start+50000], cc[start:start+50000]
                    prob[r, c] = model.predict_proba(np.asarray(mm[r, c, :88][:, channels]))[:, 1]
                record['models'][config] = {'channels': [meta['channels'][i] for i in channels],
                                            'scores': evaluate(prob, gt, score, metric)}
                print(f'fold {k} {config}: { {p: round(v["dti"], 5) for p,v in record["models"][config]["scores"].items()} }', flush=True)
                del prob, model
        output['folds'].append(record)
        output['complete'] = len(output['folds']) == args.folds
        output['elapsed_seconds'] = round(time.time() - started, 2)
        args.out.write_text(json.dumps(output, indent=2, default=str) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
