#!/usr/bin/env python3
"""Label-blind, equal-budget controls for spatial_system_cv (not new models).

Full blanket is insufficient when evaluating sparse placement: coverage alone
can beat it. Freeze three independent random-priority seeds, use the identical
score masks and 3% budget/spacing as the models, and never choose seeds by score.
This script verifies the official bytes and per-fold score-mask hashes first.
It produces scores only; no candidate faults or submission files.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import rasterio

from spatial_system_cv import budget_nodes, sha256, spatial_folds


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--entry', type=Path, required=True)
    ap.add_argument('--geometry', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    reference = json.loads(args.geometry.read_text())
    if not reference.get('complete'):
        raise ValueError('refuse incomplete geometry evidence')
    for name, expected in reference['official_sha256'].items():
        if sha256(args.entry / 'data' / name) != expected:
            raise ValueError(f'{name} pin mismatch')
    sys.path.insert(0, str(args.entry.resolve() / 'src'))
    from gems import metric
    with rasterio.open(args.entry / 'data/labels.tif') as src:
        gt = src.read(1) == 1
    with rasterio.open(args.entry / 'data/sample_submission.tif') as src:
        footprint = np.isfinite(src.read(1))
    design = reference['design']
    ids = spatial_folds(gt.shape, design['blocks'], design['folds'])
    out = {'kind': 'Label-blind null controls; NOT a leaderboard value',
           'geometry_sha256': sha256(args.geometry), 'tool_sha256': sha256(__file__),
           'placement_tool_sha256': sha256(Path(__file__).with_name('spatial_system_cv.py')),
           'seeds': [17, 29, 43], 'fraction': 0.03, 'folds': []}
    for record in reference['folds']:
        k = record['fold']
        score = (ids == k) & footprint
        import hashlib
        if hashlib.sha256(np.packbits(score).tobytes()).hexdigest() != record['geometry']['score_mask_sha256']:
            raise ValueError('score mask differs from model experiment')
        fold = {'fold': k, 'score_mask_sha256': record['geometry']['score_mask_sha256'], 'controls': []}
        for seed in out['seeds']:
            random_priority = np.random.default_rng(seed).random(gt.shape, dtype=np.float32)
            result = {'seed': seed, 'scores': {}}
            for spacing in (1, 4, 5):
                p = budget_nodes(random_priority, score, spacing=spacing)
                comp = metric.components(p, gt & score).as_dict()
                result['scores'][f'budget03_spacing{spacing}'] = comp | {'emitted_pixels': int(p.sum())}
            fold['controls'].append(result)
            print(f'fold {k}, seed {seed}: ' + str({p: round(v['dti'], 5) for p, v in result['scores'].items()}), flush=True)
        out['folds'].append(fold)
        out['complete'] = len(out['folds']) == design['folds']
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
