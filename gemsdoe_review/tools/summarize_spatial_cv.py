#!/usr/bin/env python3
"""Compare models ONLY with controls measured on the identical geographic folds.

The output is a diagnostic, never automatic permission to publish or submit.
All means are unweighted means of fold DTI, not pooled competition scores.
"""
import argparse
import json
from pathlib import Path
import statistics


def summarize(experiment, controls):
    if not experiment.get('complete') or not controls.get('complete'):
        raise ValueError('both experiments must be complete')
    folds = experiment['folds']
    null = {r['fold']: r for r in controls['folds']}
    if len(null) != len(controls['folds']) or len({r['fold'] for r in folds}) != len(folds):
        raise ValueError('duplicate folds')
    if set(null) != {r['fold'] for r in folds} or len(folds) != experiment['design']['folds']:
        raise ValueError('fold identities differ')
    if controls['fraction'] != 0.03:
        raise ValueError('control budget differs')
    for fold in folds:
        control = null[fold['fold']]
        if fold['geometry']['score_mask_sha256'] != control['score_mask_sha256']:
            raise ValueError('score masks differ')
        if sorted(r['seed'] for r in control['controls']) != sorted(controls['seeds']):
            raise ValueError('control seeds differ')
    rows = []
    for model in folds[0]['models']:
        for policy in ('budget03_spacing1', 'budget03_spacing4', 'budget03_spacing5'):
            values, deltas, emitted, null_counts = [], [], [], []
            for fold in folds:
                measured = fold['models'][model]['scores'][policy]
                baseline = [r['scores'][policy] for r in null[fold['fold']]['controls']]
                values.append(measured['dti'])
                # Conservative descriptive gate: exceeds ALL frozen null seeds,
                # not merely their mean. This is NOT a significance test.
                deltas.append(measured['dti'] - max(r['dti'] for r in baseline))
                emitted.append(measured['emitted_pixels'])
                null_counts.append([r['emitted_pixels'] for r in baseline])
            null_mean = statistics.mean(r['scores'][policy]['dti'] for f in null.values() for r in f['controls'])
            rows.append({'model': model, 'policy': policy,
                         'mean_dti': statistics.mean(values), 'per_fold_dti': values,
                         'null_mean_dti': null_mean, 'per_fold_delta_vs_best_null_seed': deltas,
                         'beats_all_null_seeds_every_fold': all(d > 0 for d in deltas),
                         'model_emitted_pixels_per_fold': emitted,
                         'null_emitted_pixels_per_fold_seed': null_counts,
                         'identical_actual_budget': all(all(n == m for n in ns) for m, ns in zip(emitted, null_counts))})
    return {'kind': 'local mapped-fault spatial transfer diagnostic; NOT a leaderboard score',
            'promotion': 'NOT APPROVED: reduced training budget, no independent confirmation, account gate unresolved',
            'mean_convention': 'unweighted fold mean (controls average seeds within each fold)',
            'rows': rows,
            'cautions': ['Only spacing4 and dense spacing1 fill the same 3% budget; spacing5 underfills and is not an equal-actual-budget comparison.',
                         'Maximum over three null seeds is a descriptive hurdle, not a statistical confidence interval.',
                         'One geographic design and seed; catalogue truth differs from hidden new faults.',
                         'Do not choose drop2 for a tiny mean gain; its fold changes are mixed.']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--experiment', type=Path, required=True)
    ap.add_argument('--controls', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    result = summarize(json.loads(args.experiment.read_text()), json.loads(args.controls.read_text()))
    from spatial_system_cv import sha256
    result['sources'] = {str(p): sha256(p) for p in (args.experiment, args.controls)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    for row in result['rows']:
        print(f"{row['model']:6} {row['policy']:20} {row['mean_dti']:.4f} / null {row['null_mean_dti']:.4f}; all-fold gate {row['beats_all_null_seeds_every_fold']}; equal budget {row['identical_actual_budget']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
