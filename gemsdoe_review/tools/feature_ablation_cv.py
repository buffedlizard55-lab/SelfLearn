#!/usr/bin/env python3
"""Paired, buffered spatial CV of magnetic-channel ablations on SGMC proxy.

A follow-up to 6GEMSDOE/NEXT_STEPS.md #6 and the earlier tilt-channel audit.
Train on the public catalogue only, score the independent SGMC code-2 proxy in
held-out strips, with the SAME sampled training rows and model settings for
all predeclared variants. Exclude a Euclidean 3-px train halo and score only
held-out block interiors. Prediction mass on known-label pixels is pixel-exact
masked. No random pixel split, no folds selected after seeing the target.

The original 88 columns and two *drop* variants are compared. Scaling `tmi_vg`
inside arctan2 is deliberately NOT called a new model feature: for a fixed
positive scale it is monotone in the existing tilt and a tree already has its
ordering. Physical vertical-gradient calibration needs source metadata.

The SGMC proxy is NOT the private expert label set; this can only decide
whether removing suspect channels warrants more work, never a final upload.
The 105-channel memmap is a local derived file; never commit it to SelfLearn.

    python gemsdoe_review/tools/feature_ablation_cv.py \\
       --entry /tmp/gems_entry --metrics-src /tmp/gems_prior \\
       --proxy /tmp/gems_entry/data/proxy_catalogue.tif \\
       --features /tmp/gems_entry/data/evidence/features.f32.npy \\
       --out gemsdoe_review/evidence/feature_ablation_cv.json
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from sklearn.ensemble import HistGradientBoostingClassifier

if __package__:  # imported as a package for tests
    from .evaluate_emission_holdout import (
        PROXY_SHA256, RADIUS_PX, components, disk, pooled, sha256,
    )
else:  # launched directly from this directory; no SelfLearn install required
    from evaluate_emission_holdout import (
        PROXY_SHA256, RADIUS_PX, components, disk, pooled, sha256,
    )

# Predeclared before fitting any variant; slice order is pinned in build_features.py.
DROPS = {
    "full88": (),
    "drop_2": ("mag_asa", "mag_tilt"),
    "drop_4": ("mag_asa", "mag_tilt", "tdr_tmi_s1.5", "tdr_tmi_s3"),
}
POLICIES = ((0.03, 0), (0.03, 3), (0.03, 6), (0.05, 0), (0.05, 3))


def score_policy(ctx, prediction: np.ndarray, core: np.ndarray,
                 weights: np.ndarray, on_truth: np.ndarray) -> dict:
    if prediction.shape != core.shape or prediction.shape != ctx.shape:
        raise ValueError("score shape mismatch")
    tp = float(ctx.credit_vector(prediction.astype(np.float32, copy=False))[on_truth].sum())
    # Explicit boolean mask: uint8 & bool stays uint8 in NumPy and becomes
    # *integer fancy indexing* (potentially hundreds of GiB), not a mask.
    positives = core & (prediction > 0)
    fp = float(weights[positives].sum())
    return components(tp, fp, int(on_truth.sum()), int(positives.sum()),
                      scored_pixels=int(core.sum()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", required=True, type=Path)
    ap.add_argument("--metrics-src", required=True, type=Path)
    ap.add_argument("--proxy", required=True, type=Path)
    ap.add_argument("--features", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--max-neg", type=int, default=400_000)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    if args.blocks < 2 or args.folds < 2 or args.folds > args.blocks ** 2:
        ap.error("need >=2 blocks and folds, with folds <= blocks**2")
    root = args.entry.resolve()
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(args.metrics_src.resolve()))
    from gems import cv, placement, spec, raster  # noqa: E402
    from src.metrics import GtContext  # noqa: E402

    for name in ("training_features.tif", "labels.tif", "sample_submission.tif"):
        pin = spec.PINS[name]
        p = root / "data" / name
        if not p.is_file() or p.stat().st_size != pin["bytes"] or sha256(p) != pin["sha256"]:
            raise SystemExit(f"STOP: official file pin mismatch: {p}")
    if sha256(args.proxy) != PROXY_SHA256:
        raise SystemExit("STOP: proxy changed; audit source before using it")
    meta_path = root / "data/evidence/features_meta.json"
    meta = json.loads(meta_path.read_text())
    if meta["features_sha256"] != spec.PINS["training_features.tif"]["sha256"]:
        raise SystemExit("STOP: feature stack built from different official raster")
    mm = np.load(args.features, mmap_mode="r")
    channels = meta["channels"]
    if tuple(mm.shape) != (spec.HEIGHT, spec.WIDTH, len(channels)) or len(channels) < 88:
        raise SystemExit("STOP: feature memmap is not the 88+ stack for this grid")
    # The metadata is generated with the memmap, but a hash of 5 GB is costly;
    # exact bytes of the derived stack are NOT cryptographically checked here.
    # Record this limitation; future portable builds should pin a whole-file hash.
    first88 = channels[:88]
    keeps = {name: np.array([i for i, c in enumerate(first88) if c not in drop], dtype=int)
             for name, drop in DROPS.items()}
    if any(any(col not in first88 for col in drop) for drop in DROPS.values()):
        raise SystemExit("STOP: ablated columns absent from the 88-column stack")

    with rasterio.open(root / "data/sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
        shape, transform, crs = s.shape, s.transform, s.crs
    with rasterio.open(root / "data/labels.tif") as s:
        lab = s.read(1)
    with rasterio.open(args.proxy) as s:
        if s.shape != shape or s.transform != transform or s.crs != crs:
            raise SystemExit("STOP: proxy grid mismatch")
        proxy = s.read(1)
    truth = (proxy == 2) & footprint
    known = lab == 1
    if not truth.any() or np.any(truth & ndimage.binary_dilation(known, structure=disk(3))):
        raise SystemExit("STOP: code-2 proxy is not the known-fault-excluded target")
    spec_folds = cv.make_folds(n_blocks=args.blocks, n_folds=args.folds, buffer_px=RADIUS_PX)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "paired spatially blocked model CV on SGMC proxy; NOT leaderboard",
        "inputs": {"feature_raster_sha256": spec.PINS["training_features.tif"]["sha256"],
                   "features_meta_sha256": sha256(meta_path),
                   "feature_stack_sha256": None,
                   "catalogue_sha256": spec.PINS["labels.tif"]["sha256"],
                   "template_sha256": spec.PINS["sample_submission.tif"]["sha256"],
                   "proxy_sha256": PROXY_SHA256,
                   "catalogue_px": int(known.sum()),
                   "proxy_truth_px": int(truth.sum())},
        "design": {"blocks_per_axis": args.blocks, "n_folds": args.folds,
                   "fold_of_block": spec_folds.fold_of_block.tolist(),
                   "train_buffer": "Euclidean disk radius 3 px (not Manhattan)",
                   "scored": "test-block interior, 3 px from the fold boundary",
                   "known_mask": "catalogue pixels excluded, NOT a 300m halo",
                   "max_negative_px": args.max_neg, "iters": args.iters, "seed": args.seed,
                   "policies": [f"topk_hard@{frac:g}|dilate{radius}"
                                for frac, radius in POLICIES],
                   "ablations": {k: list(v) for k, v in DROPS.items()}},
        "caveats": ["SGMC surface geology is not the expert-picked GeoDAWN target, and "
                    "by construction excludes corrections within 300 m of known faults.",
                    "The four strips share spatial geology and are not independent "
                    "geological systems; ablations reuse the previously inspected SGMC proxy.",
                    "Feature stack matches metadata and source hash but the entire 5GB "
                    "derived memmap is not sha256-pinned."],
        "folds": [],
    }
    for k in range(args.folds):
        t0 = time.monotonic()
        train, test = spec_folds.train_test_masks(shape, k)
        # cv._dilate currently uses a Manhattan radius; its 6x6 folds leave
        # (2,2) corner neighbours within the Euclidean scoring kernel. Hard-
        # exclude the Euclidean disk ourselves, without changing the entry's
        # historical CV scores; fix upstream with the proposed regression test.
        train &= ~ndimage.binary_dilation(test, structure=disk(RADIUS_PX))
        train &= footprint
        scored = test & footprint
        core = ndimage.binary_erosion(test, structure=disk(RADIUS_PX),
                                      border_value=0) & footprint & ~known
        if not core.any() or not (truth & core).any():
            raise SystemExit(f"STOP: fold {k} has no core proxy truth")
        # This assertion is the actual geometry, not a tautology with cv._dilate.
        if np.any(train & (ndimage.distance_transform_edt(~test) <= RADIUS_PX)):
            raise SystemExit(f"STOP: fold {k} trains inside the metric kernel")
        pos_idx = np.flatnonzero((known & train).ravel())
        neg_idx = np.flatnonzero((~known & train).ravel())
        rng = np.random.default_rng(1000 + k)
        neg_idx = rng.choice(neg_idx, size=min(len(neg_idx), args.max_neg), replace=False)
        selected = np.concatenate((pos_idx, neg_idx))
        ry, rx = np.unravel_index(selected, shape)
        y = known[ry, rx].astype(np.uint8)
        X = np.asarray(mm[ry, rx, :88], dtype=np.float32)
        del ry, rx, selected, pos_idx, neg_idx

        target = truth & scored
        ctx = GtContext(target, R_pixels=RADIUS_PX)
        weights = ctx.fp_weight()
        on_truth = core[ctx.gy, ctx.gx]
        blanket = score_policy(ctx, core.astype(np.uint8), core, weights, on_truth)
        srows, scols = np.nonzero(scored)
        record = {"fold": k, "n_train": len(y), "n_train_pos": int(y.sum()),
                  "n_predicted": int(scored.sum()), "n_scored": int(core.sum()),
                  "n_truth_scored": int(on_truth.sum()), "blanket": blanket,
                  "variants": {}}
        for name, keep in keeps.items():
            tfit = time.monotonic()
            model = HistGradientBoostingClassifier(
                max_iter=args.iters, learning_rate=0.08, max_leaf_nodes=31,
                min_samples_leaf=40, l2_regularization=1.0,
                random_state=args.seed + k, early_stopping=False,
            )
            model.fit(X[:, keep], y)
            fit_seconds = round(time.monotonic() - tfit, 2)
            pred = np.zeros(shape, dtype=np.float32)
            for start in range(0, len(srows), 100_000):
                sy, sx = srows[start:start + 100_000], scols[start:start + 100_000]
                pred[sy, sx] = model.predict_proba(
                    np.asarray(mm[sy, sx, :88], dtype=np.float32)[:, keep])[:, 1]
            rec = {"n_features": len(keep), "fit_seconds": fit_seconds, "policies": {}}
            for frac, radius in POLICIES:
                base = placement.get_strategy(f"topk_hard@{frac:g}", pred,
                                              scored, threshold=0.3) > 0
                emitted = (base if radius == 0 else
                           ndimage.binary_dilation(base, structure=disk(radius)))
                emitted &= core
                key = f"topk_hard@{frac:g}|dilate{radius}"
                rec["policies"][key] = score_policy(ctx, emitted, core, weights, on_truth)
                del base, emitted
            record["variants"][name] = rec
            print(f"fold {k}, {name:7s}, fit {fit_seconds:.1f}s, "
                  f"proxy {rec['policies']['topk_hard@0.03|dilate0']['dti']:.5f} / "
                  f"w3 {rec['policies']['topk_hard@0.03|dilate3']['dti']:.5f}",
                  flush=True)
            del pred, model
            gc.collect()
        report["folds"].append(record)
        print(f"fold {k} done {time.monotonic()-t0:.0f}s; "
              f"scored truth {int(on_truth.sum())}", flush=True)
        del X, y, ctx, weights, srows, scols, train, test, scored, core
        gc.collect()

    summary = {}
    for name in DROPS:
        summary[name] = {}
        for frac, radius in POLICIES:
            key = f"topk_hard@{frac:g}|dilate{radius}"
            f = [r["variants"][name]["policies"][key] for r in report["folds"]]
            summary[name][key] = {"all": pooled(f), "west": pooled(f[:2]),
                                  "east": pooled(f[2:]) if len(f) >= 4 else None}
    report["summary"] = summary
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {args.out}. No leaderboard claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
