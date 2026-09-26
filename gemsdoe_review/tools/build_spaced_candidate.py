#!/usr/bin/env python3
"""Build ONE local candidate with the spacing-4 placement policy (no upload).

What this is for
----------------
Session 4 measured that a genuine 4-pixel minimum spacing beats the dense policy on
spatially purged folds, and session 5 re-measured it at the SHIPPING training
budget (400k negatives, 300 iterations). This tool turns that into a single
concrete artifact so it can be gated and read geologically - which is the only
way to find out what a policy change actually does to the pixels.

Design constraints (deliberate, and checked in the output):

  * the model is trained EXACTLY like the shipped artifact (88 channels, 400k
    sampled negatives, 300 iterations, seed 7, same hyperparameters) on the whole
    official footprint, so the ONLY difference between this file and
    `gems6_hgb88-topk03_33cec71ff0.tif` is the placement policy;
  * placement is `budget_nodes(prob, footprint, 3%, spacing=4)` - probability
    ordered suppression with a minimum Chebyshev separation, the same code path
    the CV used, so the CV number and this file are the same policy;
  * the file is written to a scratch directory OUTSIDE the review repository. It
    is not committed, not published, not uploaded, and not offered for download;
  * the hard gate must pass before anything else is recorded.

    python build_spaced_candidate.py --entry /path/to/6GEMSDOE \\
        --scratch /scratch/session5 --tag spacing4-topk03

Outputs (all under --scratch): the candidate GeoTIFF, `candidate_report.json`
(with the gate result, the sha256, the emitted-pixel count, the pixel overlap
with the shipped artifact, and the in-sample catalogue DTI of both files - the
latter labelled IN-SAMPLE because the catalogue is the training target).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

TOOLS = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--tag", default="spacing4-topk03")
    ap.add_argument("--n-channels", type=int, default=88)
    ap.add_argument("--max-neg", type=int, default=400_000)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--spacing", type=int, default=4)
    ap.add_argument("--fraction", type=float, default=0.03)
    ap.add_argument("--shipped", type=Path, default=None,
                    help="the canonical artifact to compare against "
                         "(default: <entry>/downloads/gems6_hgb88-topk03_33cec71ff0.tif)")
    args = ap.parse_args()
    entry = args.entry.resolve()
    scratch = args.scratch.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(entry / "src"))
    sys.path.insert(0, str(entry / "scripts"))
    from gems import raster, spec  # noqa: PLC0415
    cvmod = load_module("spatial_system_cv", TOOLS / "spatial_system_cv.py")

    t0 = time.time()
    with rasterio.open(entry / "data/labels.tif") as src:
        lab = src.read(1)
    with rasterio.open(entry / "data/sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    gt = lab == 1

    import build_submission as bs  # noqa: PLC0415  (canonical trainer/predictor)
    model, train_info = bs.train_model(entry / "data/evidence/features.f32.npy",
                                      args.n_channels, gt, footprint, args.max_neg,
                                      seed=args.seed, iters=args.iters)
    print(f"[{time.time()-t0:6.1f}s] trained {train_info}", flush=True)
    prob = bs.predict_full(entry / "data/evidence/features.f32.npy", model,
                           footprint, args.n_channels)
    print(f"[{time.time()-t0:6.1f}s] predicted; max={prob.max():.4f}", flush=True)

    placed = cvmod.budget_nodes(prob, footprint, fraction=args.fraction, spacing=args.spacing)
    placed = np.where(footprint, placed, 0.0).astype(np.float32)
    out = scratch / f"candidate_{args.tag}.tif"
    raster.write_submission(placed, out, entry / "data/sample_submission.tif", footprint=footprint)
    report = raster.check_submission(out)
    print(report.text())

    shipped_path = args.shipped or (entry / "downloads/gems6_hgb88-topk03_33cec71ff0.tif")
    shipped_report = raster.check_submission(shipped_path)
    with rasterio.open(shipped_path) as src:
        shipped = np.isfinite(src.read(1)) & (src.read(1) > 0)

    new = np.isfinite(placed) & (placed > 0)
    overlap = int((new & shipped).sum())
    union = int((new | shipped).sum())
    from gems import metric  # noqa: PLC0415
    dti_new = metric.distance_weighted_tversky(placed, gt)
    dti_shipped = metric.distance_weighted_tversky(
        np.where(shipped, 1.0, 0.0).astype(np.float32), gt)

    payload = {
        "kind": "ONE local candidate under the spacing-4 policy; NOT submitted, NOT published",
        "tag": args.tag,
        "file": out.name,
        "sha256": raster.sha256_file(out),
        "bytes": out.stat().st_size,
        "gate_ok": report.ok,
        "gate": report.as_dict(),
        "positive_pixels": int(new.sum()),
        "policy": {"placement": "budget_nodes probability-ordered suppression",
                   "fraction": args.fraction, "spacing_px": args.spacing,
                   "minimum_separation": "Chebyshev spacing px",
                   "identical_training_to_shipped": True},
        "training": train_info | {"seed": args.seed, "n_channels": args.n_channels},
        "shipped_artifact": {
            "path": str(shipped_path), "sha256": raster.sha256_file(shipped_path),
            "positive_pixels": int(shipped.sum()),
            "gate_ok": shipped_report.ok,
        },
        "pixel_overlap_with_shipped": {
            "both": overlap, "only_new": int((new & ~shipped).sum()),
            "only_shipped": int((shipped & ~new).sum()), "union": union,
            "jaccard": (overlap / union) if union else None,
        },
        "catalogue_dti": {
            "IN_SAMPLE_warning": ("the catalogue is the training target, so these two numbers "
                                  "are in-sample and are NOT the blocked-CV estimate"),
            "new_candidate": dti_new, "shipped": dti_shipped,
        },
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seconds": round(time.time() - t0, 1),
    }
    (scratch / f"candidate_report_{args.tag}.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in ("sha256", "positive_pixels", "gate_ok",
                                              "pixel_overlap_with_shipped", "catalogue_dti")},
                     indent=2))
    if not report.ok:
        print("REFUSING: candidate fails the hard gate", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
