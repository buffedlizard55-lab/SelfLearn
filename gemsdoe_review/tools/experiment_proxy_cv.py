#!/usr/bin/env python3
"""Blocked-CV comparison of feature-stack variants scored on the NEW-FAULT
population instead of the catalogue.

WHY THIS EXISTS
---------------
`scripts/experiment.py` in the entry repository trains the model on the provided
catalogue and scores it on held-out blocks of that same catalogue. Both prize rounds
score faults the catalogue does not contain, so that harness can rank models that
memorise mapped traces above models that generalise — it cannot see the difference.
This script keeps the harness identical (same blocked, buffered folds, same model,
same placements) and changes only the *scored truth*: the USGS SGMC faults that the
labels do not contain (`proxy_catalogue.tif` code 2), restricted to the held-out
blocks. Training positives stay the catalogue, exactly as the shipped model.

`GEMSDOE/scripts/eval_proxy_catalogue.py` measures a *finished submission* on that
population. This measures a *feature stack* on it, out of block, which is the only way
to answer "did the 40 channels added after the 0.1119/0.1628 result help on the
population that is actually scored?".

Because FP_w is a global sum and the scored region here is a block subset, the
absolute DTI is not comparable with the numbers in `data/evidence/experiments*.json`;
the comparison between the variants run in the same invocation is exact, and that is
what this script is for.

    PYTHONPATH=src python <this file> --configs baseline,extended --folds 0

Caveats that belong with any number it prints:
  * SGMC faults are surface-mapped by state geologists; the scored faults were chosen
    from GeoDAWN geophysics. The populations overlap in character, not in identity.
  * Only faults present inside a held-out block are scored, so per-fold truth is
    ~1/4 of the 61,664-px population.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "src"))

from gems import cv as gcv                                                   # noqa: E402
from gems import metric, spec                                                # noqa: E402

CODES = {"baseline": 48, "extended": 88}


def load_grid(labels_path, proxy_path):
    with rasterio.open(labels_path) as s:
        lab = s.read(1)
    with rasterio.open(proxy_path) as s:
        proxy = s.read(1)
    return lab, proxy


def placements(grid_pred, valid, fracs=(0.02, 0.03, 0.05)):
    """The placement policies that matter here, without the lineament variants
    (already measured as a dead end in the entry's own `experiments_round2.json`)."""
    from gems import placement as P

    out = {}
    for f in fracs:
        out[f"topk_hard@{f:g}"] = P.get_strategy(f"topk_hard@{f:g}", grid_pred, valid,
                                                 threshold=0.3)
    return out


def run_fold(mm, meta, n_ch, train_gt, score_gt, folds, k, max_train_px, iters, seed,
             place_min_frac, dump=None):
    from sklearn.ensemble import HistGradientBoostingClassifier

    shape = (spec.HEIGHT, spec.WIDTH)
    train_mask, test_mask = folds.train_test_masks(shape, k)
    train_mask &= (meta["valid"])

    pos_idx = np.flatnonzero((train_gt & train_mask).ravel())
    neg_idx = np.flatnonzero((~train_gt & train_mask).ravel())
    rng = np.random.default_rng(1000 + k)
    n_neg = min(neg_idx.size, max_train_px)
    neg_idx = rng.choice(neg_idx, size=n_neg, replace=False)
    sel = np.concatenate([pos_idx, neg_idx])
    rows, cols = np.unravel_index(sel, shape)
    X = np.asarray(mm[rows, cols, :n_ch], dtype=np.float32)
    y = train_gt[rows, cols].astype(np.uint8)
    del rows, cols, sel, pos_idx, neg_idx

    model = HistGradientBoostingClassifier(
        max_iter=iters, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=40,
        l2_regularization=1.0, random_state=seed + k, early_stopping=False)
    t0 = time.time()
    model.fit(X, y)
    fit_s = round(time.time() - t0, 1)
    del X, y

    score_mask = test_mask & meta["valid"]
    srows, scols = np.nonzero(score_mask)
    order = np.argsort(srows, kind="stable")
    srows, scols = srows[order], scols[order]
    grid_pred = np.zeros(shape, dtype=np.float32)
    step = 200_000
    for i in range(0, srows.size, step):
        sl = slice(i, min(i + step, srows.size))
        grid_pred[srows[sl], scols[sl]] = model.predict_proba(
            np.asarray(mm[srows[sl], scols[sl], :n_ch], dtype=np.float32))[:, 1]
    del srows, scols

    # Score on the bounding box of the held-out blocks, exactly as the entry's own
    # harness does: both the prediction and the scored truth are zero outside it.
    ys, xs = np.nonzero(score_mask)
    margin = int(np.ceil(metric.RADIUS_PX)) + 1
    r0, r1 = max(0, int(ys.min()) - margin), min(spec.HEIGHT, int(ys.max()) + margin + 1)
    c0, c1 = max(0, int(xs.min()) - margin), min(spec.WIDTH, int(xs.max()) + margin + 1)
    del ys, xs
    sl = (slice(r0, r1), slice(c0, c1))

    sub_gt = (score_gt & score_mask)[sl]
    crop_pred = grid_pred[sl]
    crop_valid = score_mask[sl]
    del grid_pred

    rec = {"fold": k, "n_train_pos": int((train_gt & train_mask).sum()),
           "n_train_neg_used": int(n_neg), "n_score_px": int(score_mask.sum()),
           "n_truth_in_block": int(sub_gt.sum()), "fit_seconds": fit_s,
           "crop": [int(r0), int(r1), int(c0), int(c1)], "policies": {}}

    cands = placements(crop_pred, crop_valid)
    for name, arr in cands.items():
        comp = metric.components(arr, sub_gt)
        rec["policies"][name] = {"dti": comp.dti, "tp_w": comp.tp_w, "fp_w": comp.fp_w,
                                 "fn_w": comp.fn_w, "n_pos_pred": comp.n_pos_pred}
        # the emitted width lever: dilate the binary emission by r px
        for r in (1, 3):
            dil = ndimage.binary_dilation(arr, structure=ndimage.generate_binary_structure(2, 2),
                                          iterations=r)
            cd = metric.components(dil, sub_gt)
            rec["policies"][f"{name}|dilate{r}"] = {
                "dti": cd.dti, "tp_w": cd.tp_w, "fp_w": cd.fp_w, "fn_w": cd.fn_w,
                "n_pos_pred": cd.n_pos_pred}
    if dump:
        np.save(dump, crop_pred.astype(np.float32))
    del crop_pred, cands, sub_gt
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="data/evidence/features.f32.npy")
    ap.add_argument("--configs", default="baseline,extended")
    ap.add_argument("--folds", default="0")
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--buffer", type=int, default=3)
    ap.add_argument("--max-train-px", type=int, default=200_000)
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--labels", default="data/labels.tif")
    ap.add_argument("--proxy", default="/home/user/scratch/r1/data/evidence/proxy/proxy_catalogue.tif")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lab, proxy = load_grid(args.labels, args.proxy)
    train_gt = lab == 1                       # what the model is trained on
    score_gt = proxy == 2                     # what it is scored on here
    meta = {"valid": lab != -1}
    print(f"train positives {int(train_gt.sum())}; scored truth {int(score_gt.sum())} "
          f"({int((score_gt & meta['valid']).sum())} inside the footprint)")

    mm = np.load(REPO / args.features, mmap_mode="r")
    print(f"features {mm.shape} {mm.dtype}")
    folds = gcv.make_folds(n_blocks=args.blocks, n_folds=args.blocks, buffer_px=args.buffer)
    report = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "purpose": "blocked-CV comparison of feature-stack variants, scored on "
                         "faults the training labels do not contain (SGMC proxy code 2)",
              "design": {"train_truth": "data/labels.tif (the provided catalogue)",
                         "score_truth": "proxy_catalogue.tif code 2, restricted to held-out blocks",
                         "n_blocks": args.blocks, "buffer_px": args.buffer,
                         "max_train_px": args.max_train_px, "iters": args.iters,
                         "model": "HistGradientBoostingClassifier(lr=0.08, leaves=31, "
                                  "min_leaf=40, l2=1.0)"},
              "caveats": ["SGMC surface-mapped faults; the scored faults were chosen from "
                          "GeoDAWN geophysics",
                          "FP_w is global, so this block-restricted DTI is not comparable "
                          "with data/evidence/experiments*.json; comparisons within this file are"],
              "configs": {}}

    for cfg in args.configs.split(","):
        n_ch = CODES[cfg]
        for k in [int(x) for x in args.folds.split(",")]:
            t0 = time.time()
            rec = run_fold(mm, meta, n_ch, train_gt, score_gt, folds, k,
                           args.max_train_px, args.iters, args.seed, None)
            report["configs"].setdefault(cfg, {"n_channels": n_ch, "folds": []})
            report["configs"][cfg]["folds"].append(rec)
            shown = ["topk_hard@0.03", "topk_hard@0.03|dilate2", "topk_hard@0.05"]
            print(f"  {cfg:9s} fold {k}: truth_in_block {rec['n_truth_in_block']:,} "
                  f"fit {rec['fit_seconds']}s total {time.time()-t0:.0f}s | "
                  + " | ".join(f"{s} {rec['policies'][s]['dti']:.4f}"
                               for s in shown if s in rec["policies"]), flush=True)

    # compare
    if len(report["configs"]) == 2:
        a, b = list(report["configs"])
        keys = sorted(set(report["configs"][a]["folds"][0]["policies"])
                      & set(report["configs"][b]["folds"][0]["policies"]))
        print(f"\n{'policy':<28} {a:>10} {b:>10} {'delta':>9}")
        for kk in keys:
            va = np.mean([f["policies"][kk]["dti"] for f in report["configs"][a]["folds"]])
            vb = np.mean([f["policies"][kk]["dti"] for f in report["configs"][b]["folds"]])
            print(f"{kk:<28} {va:>10.4f} {vb:>10.4f} {vb-va:>+9.4f}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=1) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
