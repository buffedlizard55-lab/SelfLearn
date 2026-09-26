#!/usr/bin/env python3
"""Score candidate submissions on the new-fault-like population, with and without
the official mask rule, and sweep emission-width policies.

WHY THIS EXISTS
---------------
1. Every quality number the 6GEMSDOE repository publishes is measured against
   `labels.tif` — the faults the catalogue ALREADY contains. The competition's own
   scoring note (community.drivendata.org/t/11516) says the scored faults are the ones
   the catalogue does not contain, and that the catalogue pixels are removed from
   evaluation before the metric is computed. `GEMSDOE/scripts/eval_proxy_catalogue.py`
   scores on the right *population* (USGS SGMC faults absent from the labels, prepared
   by `build_proxy_catalogue.py`) but with the catalogue pixels still counted as
   false positives. This script implements the rule, so the numbers can be compared.

2. The rule does not merely rescale the score: under it, mass sitting on a mapped
   trace is free, and the optimal emission WIDTH changes. The shipped 6GEMSDOE file
   emits thinned 1-px lines and no dilation. `--sweep-width` measures what widening
   would do to the only score we can compute locally.

WHAT THE NUMBER IS AND IS NOT
-----------------------------
It is a policy comparison on real mapped faults absent from the training labels. It is
not a leaderboard prediction: the scored faults were chosen by experts from GeoDAWn
geophysics, the SGMC faults were drawn by state-map geologists from surface mapping,
and the proxy population is dominated by short segments (2,083 components, median
12 px) while the scored set is likely to be longer structures. Directional comparisons
between policies are the intended use; absolute values are not.

USAGE
    python masked_proxy_eval.py \
        --pred /path/a.tif /path/b.tif --labels /path/labels.tif \
        --proxy /path/proxy_catalogue.tif --sweep-width 0,1,2,3,4,6 \
        --out evidence/masked_proxy_eval.json

`--metrics-src` must point at a checkout of the GEMSDOE repository, which is where the
exact metric implementation (`GtContext`) lives; this script reuses it rather than
re-deriving it, so the two agree by construction.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

RULE_SOURCE = ("https://community.drivendata.org/t/scoring-clarification-are-known-usgs-"
               "ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516")
RULE_QUOTES = {
    "mask_excludes_catalogue": "Pixels corresponding to known USGS/INGENIOUS faults are masked / "
                               "excluded from evaluation, so they do not count towards penalty terms.",
    "mask_is_pixel_exact": "The mask is indeed pixel-exact - it is identical to the provided set of "
                           "training fault labels.",
    "no_buffer_for_known": "A predicted pixel that is near a known fault trace but far from a "
                           "new-fault ground truth pixel will be fully penalized, i.e., the buffer "
                           "does not apply to known faults.",
    "truth_may_be_near_known": "A new-fault ground truth pixel can indeed lie within 300m of a known "
                              "fault trace. Such pixels would constitute corrections or modifications "
                              "to existing fault traces.",
}
CODE_ONLY = 2          # proxy raster: 2 = SGMC fault with no training label within R
R_PIXELS = 3           # 300 m at 100 m pixels


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def disk(r: int) -> np.ndarray:
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (yy * yy + xx * xx) <= r * r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred", nargs="+", required=True)
    ap.add_argument("--labels", required=True, help="the provided catalogue raster (the mask)")
    ap.add_argument("--proxy", required=True, help="proxy catalogue; code 2 = new-fault-like")
    ap.add_argument("--out", required=True)
    ap.add_argument("--metrics-src", default="/home/user/scratch/r1",
                    help="checkout of the GEMSDOE repository (provides src.metrics)")
    ap.add_argument("--sweep-width", default="0,1,2,3,4,6",
                    help="dilation radii, in px, applied to the prediction before scoring")
    ap.add_argument("--note", default=None)
    args = ap.parse_args()

    sys.path.insert(0, str(Path(args.metrics_src).resolve()))
    from src.metrics import GtContext                                     # noqa: E402

    lab = rasterio.open(args.labels).read(1)
    catalogue = lab == 1
    valid = lab != -1                      # the scored footprint
    with rasterio.open(args.proxy) as s:
        proxy = s.read(1)
    truth = proxy == CODE_ONLY
    print(f"truth (proxy-only) px = {int(truth.sum())};  catalogue px = {int(catalogue.sum())};  "
          f"footprint px = {int(valid.sum())}", flush=True)

    # The proxy is only meaningful if its pixels are genuinely absent from the labels.
    from scipy.ndimage import distance_transform_edt
    d_to_lab = distance_transform_edt(~catalogue)
    bad = truth & (d_to_lab <= R_PIXELS)
    assert not bad.any(), f"{int(bad.sum())} proxy pixels sit within {R_PIXELS} px of a label"

    ctx = GtContext(truth, R_pixels=R_PIXELS)
    fpw = ctx.fp_weight()                  # 1 - max_g k(d(x,g)); the per-pixel FP weight
    assert ctx.n_gt == int(truth.sum())

    widths = [int(w) for w in args.sweep_width.split(",")]
    report: dict = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "gemsdoe_review/tools/masked_proxy_eval.py",
        "purpose": "score candidate submissions on faults the training labels do not contain, "
                   "under the official mask rule and without it, and sweep the emission width",
        "rule_source": RULE_SOURCE,
        "rule_quotes": RULE_QUOTES,
        "metric": {"R_pixels": R_PIXELS, "R_meters": 300, "alpha": 0.2, "beta": 0.8},
        "inputs": {
            "labels": {"path": str(Path(args.labels).resolve()),
                       "sha256": sha256(Path(args.labels)),
                       "catalogue_px": int(catalogue.sum())},
            "proxy": {"path": str(Path(args.proxy).resolve()),
                      "sha256": sha256(Path(args.proxy)),
                      "truth_px": int(truth.sum()),
                      "footprint_px": int(valid.sum())},
        },
        "rules": {
            "raw": "the official metric as written: every predicted pixel counts towards FP_w",
            "masked_fp": "FP_w excludes predicted pixels that fall on the catalogue mask "
                         "(the mask is identical to the labels raster); TP_w unchanged",
            "masked_both": "as masked_fp, and predictions on the mask are also removed before "
                           "the TP_w credit is taken (a masked pixel cannot earn credit)",
        },
        "predictions": {},
        "baselines": {},
        "note": args.note,
    }
    if args.note is None:
        report.pop("note")

    def score(pred: np.ndarray) -> dict:
        credit = ctx.credit_vector(pred)
        tp = float(credit.sum())
        fn = float(ctx.n_gt - tp)
        out = {}
        for rule in ("raw", "masked_fp", "masked_both"):
            p = pred
            if rule == "masked_both":
                p = np.where(catalogue, 0.0, pred)
                credit_r = ctx.credit_vector(p)
                tp_r = float(credit_r.sum())
                fn_r = float(ctx.n_gt - tp_r)
            else:
                tp_r, fn_r = tp, fn
            pos = p > 0
            if rule == "raw":
                fp = float((p[pos] * fpw[pos]).sum())
            else:
                sel = pos & ~catalogue
                fp = float((p[sel] * fpw[sel]).sum())
            denom = tp_r + 0.2 * fp + 0.8 * fn_r + 1e-7
            out[rule] = {"dti": tp_r / denom, "TP_w": tp_r, "FP_w": fp, "FN_w": fn_r,
                         "emission_px": int(pos.sum())}
        return out

    # ---- baselines -------------------------------------------------------------
    zeros = np.zeros(lab.shape, dtype=np.float32)
    blanket = valid.astype(np.float32)
    catcopy = catalogue.astype(np.float32)
    for name, arr in (("zeros", zeros), ("blanket_ones_in_footprint", blanket),
                      ("catalogue_copy", catcopy)):
        report["baselines"][name] = score(arr)
        print(f"  baseline {name:26s} raw DTI {report['baselines'][name]['raw']['dti']:.4f}")

    # ---- candidates ------------------------------------------------------------
    for path in args.pred:
        p = Path(path)
        with rasterio.open(p) as s:
            pred = s.read(1).astype(np.float32)
        pred = np.nan_to_num(pred, nan=0.0)
        entry = {
            "path": str(p.resolve()), "sha256": sha256(p), "bytes": p.stat().st_size,
            "emitted_px": int((pred > 0).sum()),
            "emitted_on_catalogue_px": int(((pred > 0) & catalogue).sum()),
            "policy_sweep": {},
        }
        for w in widths:
            arr = pred if w == 0 else binary_dilation(pred > 0, disk(w)).astype(np.float32)
            entry["policy_sweep"][f"dilate{w}"] = score(arr)
        entry["as_provided"] = entry["policy_sweep"]["dilate0"]
        report["predictions"][p.name] = entry
        best = max(entry["policy_sweep"].items(), key=lambda kv: kv[1]["masked_both"]["dti"])
        print(f"  {p.name}")
        print(f"      as-provided: raw {entry['as_provided']['raw']['dti']:.4f} | "
              f"masked_fp {entry['as_provided']['masked_fp']['dti']:.4f} | "
              f"masked_both {entry['as_provided']['masked_both']['dti']:.4f}")
        for w in widths:
            c = entry["policy_sweep"][f"dilate{w}"]["masked_both"]
            print(f"      dilate{w}: masked_both DTI {c['dti']:.4f} "
                  f"(TP_w {c['TP_w']:.0f}, FP_w {c['FP_w']:.0f}, px {c['emission_px']})")
        print(f"      best under masked_both: {best[0]} at {best[1]['masked_both']['dti']:.4f}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=1) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
