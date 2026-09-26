#!/usr/bin/env python3
"""Rule-correct local evaluation: the MASKED-catalogue proxy DTI.

WHY THIS EXISTS
---------------
On 2026-09-26 this review verified, from DrivenData staff posts in the official
forum topic 11516 (quoted verbatim in
`evidence/scoring_rule_clarification.json`), three facts about how submissions
are actually scored:

  1. "Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded
     from evaluation, so they do not count towards penalty terms." The mask is
     "pixel-exact - it is identical to the provided set of training fault
     labels."
  2. "Only new-fault ground truth is considered for scoring purposes. A predicted
     pixel that is near a known fault trace but far from a new-fault ground
     truth pixel will be fully penalized, i.e., the buffer does not apply to
     known faults."
  3. "A new-fault ground truth pixel can indeed lie within 300m of a known fault
     trace. Such pixels would constitute corrections or modifications to existing
     fault traces."

The entry's own new-fault-like evaluation (`scripts/eval_proxy_catalogue.py` in
the GEMSDOE repository, generated 2026-09-17) scores a prediction against USGS
SGMC faults that the training labels do NOT contain. That is the right
population — but it was written four days before the clarification and it
implements the *unmasked* metric: predicted mass sitting exactly on a training
label is charged as false-positive mass, which the platform does not do.

The difference is not cosmetic. Under the unmasked proxy, copying the catalogue
scores 0.0 and any emission that hugs the catalogue looks expensive. Under the
rule the platform actually applies, catalogue pixels are FREE — they are simply
deleted from the prediction before scoring — so a submission is never punished
for covering them, and the only mass that costs anything is mass on pixels that
are neither a training label nor within 300 m of a new-fault truth pixel.

This script computes both, side by side, on the same truth, so the two
evaluations can be compared directly:

    unmasked : DTI(pred,              proxy_only_truth)
    MASKED   : DTI(pred * ~labels,    proxy_only_truth)      <- the platform's rule

Usage (paths are explicit; nothing is defaulted to a repo layout):

    python masked_proxy_eval.py \
        --pred  /path/to/submission.tif \
        --labels /path/to/labels.tif \
        --proxy /path/to/proxy_catalogue.tif \
        --out   /path/to/result.json

    # compare several predictions at once
    python masked_proxy_eval.py --batch preds.json --out results.json

`proxy` is a uint8 raster where 2 = a fault with no training label within 300 m
(build it with the GEMSDOE repository's scripts/fetch_proxy_faults.py +
scripts/build_proxy_catalogue.py; provenance and sha256 in its proxy_stats.json).

WHAT IT DOES NOT DO
-------------------
The SGMC proxy is a *population* stand-in, not the scored set, and the tool says
so in its own docstring. Nothing here can predict a leaderboard position. What it
can do — and what the decision it feeds needs — is rank two candidate
submissions whose only difference is how they spend mass relative to the
catalogue, which is exactly the axis the mask rule changes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ALPHA = 0.2
BETA = 0.8
RADIUS_PX = 3.0


def shift_zero(arr: np.ndarray, dy: int, dx: int) -> np.ndarray:
    out = np.zeros_like(arr)
    h, w = arr.shape
    ys_src = slice(max(0, -dy), h - max(0, dy))
    ys_dst = slice(max(0, dy), h - max(0, -dy))
    xs_src = slice(max(0, -dx), w - max(0, dx))
    xs_dst = slice(max(0, dx), w - max(0, -dx))
    out[ys_dst, xs_dst] = arr[ys_src, xs_src]
    return out


def kernel_offsets(radius_px: float = RADIUS_PX):
    r = int(np.ceil(radius_px))
    offs = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = float(np.hypot(dy, dx))
            if d <= radius_px + 1e-12:
                offs.append((dy, dx, d, max(1.0 - d / radius_px, 0.0)))
    offs.sort(key=lambda t: (t[2], t[0], t[1]))
    a = np.array(offs, dtype=np.float64)
    return a[:, 0].astype(np.int64), a[:, 1].astype(np.int64), a[:, 3]


def best_weighted_prediction(pred: np.ndarray, radius_px: float = RADIUS_PX):
    dy, dx, k = kernel_offsets(radius_px)
    best = np.zeros_like(pred)
    for d_y, d_x, kk in zip(dy, dx, k):
        if kk <= 0.0:
            continue
        np.maximum(best, shift_zero(pred, int(d_y), int(d_x)) * kk, out=best)
    return best


def components(pred: np.ndarray, target: np.ndarray) -> dict:
    """Official distance-weighted Tversky components (page 967), exactly."""
    from scipy import ndimage

    p = np.clip(np.asarray(pred, dtype=np.float64), 0.0, 1.0)
    g = np.asarray(target).astype(bool)
    n_gt = int(g.sum())
    pos = p > 0.0
    n_pos = int(pos.sum())
    if n_gt == 0:
        d_to_gt = np.zeros(p.shape)
    else:
        d_to_gt = ndimage.distance_transform_edt(~g, sampling=1.0)
    k_nearest = np.maximum(1.0 - d_to_gt / RADIUS_PX, 0.0)
    fp_w = float((p * (1.0 - k_nearest))[pos].sum()) if n_pos else 0.0
    if n_gt == 0:
        tp_w = fn_w = 0.0
    else:
        m = best_weighted_prediction(p)
        mg = m[g]
        tp_w = float(mg.sum())
        fn_w = float((1.0 - mg).sum())
    denom = tp_w + ALPHA * fp_w + BETA * fn_w
    return {
        "dti": float(tp_w / denom) if denom > 0 else 0.0,
        "tp_w": tp_w, "fp_w": fp_w, "fn_w": fn_w,
        "n_pos_pred": n_pos, "n_gt": n_gt,
        "mass": float(p.sum()),
    }


def load(path: Path) -> np.ndarray:
    with rasterio.open(path) as s:
        return s.read(1)


def evaluate(pred_path: Path, labels: np.ndarray, truth: np.ndarray,
             truth_px: int, dilate: int = 0, restrict_off_catalogue: bool = False
             ) -> dict:
    from scipy import ndimage

    pred = np.nan_to_num(load(pred_path).astype(np.float64), nan=0.0)
    pred = np.clip(pred, 0.0, 1.0)
    masked = labels == 1
    out: dict = {
        "pred": str(pred_path),
        "emission_px": int((pred > 0).sum()),
        "emission_on_catalogue_px": int(((pred > 0) & masked).sum()),
    }
    if dilate:
        pred = np.where(ndimage.binary_dilation(pred > 0, iterations=dilate), 1.0, 0.0)
        out["dilated_px"] = dilate
        out["emission_px_after_dilation"] = int((pred > 0).sum())
        out["emission_on_catalogue_px_after_dilation"] = int(((pred > 0) & masked).sum())
    if restrict_off_catalogue:
        pred = np.where(masked, 0.0, pred)
        out["restricted_to_off_catalogue"] = True

    # the platform's rule: predictions on masked (training-label) pixels are deleted
    pred_masked = np.where(masked, 0.0, pred)

    out["unmasked_proxy"] = components(pred, truth)
    out["MASKED_proxy"] = components(pred_masked, truth)
    out["truth_px"] = truth_px
    out["mass_removed_by_mask"] = out["unmasked_proxy"]["mass"] - out["MASKED_proxy"]["mass"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred")
    ap.add_argument("--batch", help="JSON list of {name, path, dilate?, off_catalogue_only?}")
    ap.add_argument("--labels", required=True)
    ap.add_argument("--proxy", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dilate", type=int, default=0)
    args = ap.parse_args()
    if not args.pred and not args.batch:
        ap.error("give --pred or --batch")

    labels = load(Path(args.labels))
    proxy = load(Path(args.proxy))
    truth = proxy == 2
    truth_px = int(truth.sum())

    # Sanity: the proxy code-2 pixels must be >R from every training label, else
    # "the mask does not apply to known faults" would be doing work here.
    from scipy import ndimage
    d_to_labels = ndimage.distance_transform_edt(~(labels == 1))
    assert d_to_labels[truth].min() > RADIUS_PX, (
        "proxy code-2 pixels are not all beyond R from a training label; "
        "this tool assumes they are")

    results: dict = {
        "_what_this_is": "rule-correct (masked-catalogue) proxy evaluation, "
                         "computed by tools/masked_proxy_eval.py",
        "labels": args.labels, "proxy": args.proxy,
        "truth_px": truth_px,
        "rule": {
            "source": "https://community.drivendata.org/t/11516 (staff, 2026-09-16 and 2026-09-21)",
            "mask": "pixel-exact: identical to the provided training fault labels",
            "unmasked_penalty": "a predicted pixel near a known fault but far from "
                                "new-fault truth is fully penalized",
            "truth": "proxy code 2 = SGMC faults with no training label within 300 m",
        },
        "metrics": {},
    }

    if args.pred:
        results["metrics"][Path(args.pred).name] = evaluate(
            Path(args.pred), labels, truth, truth_px, dilate=args.dilate)
    if args.batch:
        for item in json.loads(Path(args.batch).read_text()):
            results["metrics"][item["name"]] = evaluate(
                Path(item["path"]), labels, truth, truth_px,
                dilate=int(item.get("dilate", 0)),
                restrict_off_catalogue=bool(item.get("off_catalogue_only", False)))

    # Two baselines that the mask rule makes interesting:
    results["baselines"] = {}
    results["baselines"]["catalogue_copy"] = evaluate_from_array(
        (labels == 1).astype(np.float64), labels, truth, truth_px)
    results["baselines"]["blanket_ones_inside_footprint"] = evaluate_from_array(
        (labels != -1).astype(np.float64), labels, truth, truth_px)

    Path(args.out).write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {args.out}")
    print(f"truth: {truth_px:,} px of proxy-only faults "
          f"(all >{RADIUS_PX:g} px from every training label)")
    for name, r in results["metrics"].items():
        print(f"  {name:<48s} unmasked {r['unmasked_proxy']['dti']:.4f}  "
              f"MASKED {r['MASKED_proxy']['dti']:.4f}  "
              f"({r['emission_px']:,} px, {r['emission_on_catalogue_px']:,} on catalogue)")
    for name, r in results["baselines"].items():
        print(f"  [baseline] {name:<37s} unmasked {r['unmasked_proxy']['dti']:.4f}  "
              f"MASKED {r['MASKED_proxy']['dti']:.4f}")
    return 0


def evaluate_from_array(pred: np.ndarray, labels: np.ndarray, truth: np.ndarray,
                        truth_px: int) -> dict:
    pred = np.clip(np.nan_to_num(pred, nan=0.0), 0.0, 1.0)
    masked = labels == 1
    return {
        "emission_px": int((pred > 0).sum()),
        "emission_on_catalogue_px": int(((pred > 0) & masked).sum()),
        "unmasked_proxy": components(pred, truth),
        "MASKED_proxy": components(np.where(masked, 0.0, pred), truth),
        "truth_px": truth_px,
    }


if __name__ == "__main__":
    raise SystemExit(main())
