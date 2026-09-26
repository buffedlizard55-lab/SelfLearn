#!/usr/bin/env python3
"""Build a *local, unsubmitted* single-entry candidate from a paired-CV result.

The fixed, documented hypothesis is: drop two nearly redundant magnetic columns
(`mag_asa`, `mag_tilt`) and use topk_hard@0.05 instead of the canonical 3%.
The 3%/5% and channel effects were isolated in feature_ablation_cv.py on the
catalogue-trained model with the same seed, parameters, train sample and folds.
The SGMC validation is NOT a competition score and does not validate corrections
within 300 m of mapped faults. The probability stack is rebuilt on demand from
sha256-pinned official files; no model or large feature stack is committed here.

The generated .tif is ALWAYS written to a temporary path, run through the
canonical `raster.check_submission` hard gate, then renamed on a clean pass.
Nothing updates the live site, existing submission, or DrivenData account.

    python gemsdoe_review/tools/build_local_candidate.py \\
      --entry /tmp/gems_entry \\
      --features /tmp/gems_entry/data/evidence/features.f32.npy \\
      --out /tmp/gems_candidate_drop2_topk05.tif \\
      --report gemsdoe_review/evidence/local_candidate_2026-09-26.json
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

if __package__:
    from .evaluate_emission_holdout import disk, sha256
else:
    from evaluate_emission_holdout import disk, sha256

DROP = {"mag_asa", "mag_tilt"}
STRATEGY = "topk_hard@0.05"


def build(root: Path, features: Path, out: Path, report_path: Path,
          dilation_px: int = 0) -> dict:
    if dilation_px not in (0, 3):
        raise ValueError("only the predeclared 0/3-px widths were assessed in CV")
    sys.path.insert(0, str(root / "src"))
    from gems import placement, raster, spec  # noqa: E402

    if out.exists():
        raise ValueError(f"refusing to replace any candidate: {out}")
    for name, pin in spec.PINS.items():
        p = root / "data" / name
        if not p.exists() or p.stat().st_size != pin["bytes"] or sha256(p) != pin["sha256"]:
            raise ValueError(f"official data pin failed: {p}")
    meta_path = root / "data/evidence/features_meta.json"
    meta = json.loads(meta_path.read_text())
    channels = meta["channels"][:88]
    if (len(channels) != 88 or not DROP.issubset(channels) or
            meta["features_sha256"] != spec.PINS["training_features.tif"]["sha256"]):
        raise ValueError("feature metadata does not match the pinned 88-column stack")
    mm = np.load(features, mmap_mode="r")
    if mm.shape != (spec.HEIGHT, spec.WIDTH, len(meta["channels"])):
        raise ValueError("feature stack shape differs from the metadata")
    keep = np.array([i for i, c in enumerate(channels) if c not in DROP], dtype=int)
    if keep.size != 86:
        raise ValueError("wrong number of retained features")
    sample = root / "data/sample_submission.tif"
    with rasterio.open(sample) as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(root / "data/labels.tif") as src:
        truth = src.read(1) == 1

    # Exact sampling and HGB hyperparameters of 6GEMSDOE/build_submission.py.
    seed, max_neg, iters = 7, 400_000, 300
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero((truth & footprint).ravel())
    neg_pool = np.flatnonzero((~truth & footprint).ravel())
    neg = rng.choice(neg_pool, size=min(neg_pool.size, max_neg), replace=False)
    sy, sx = np.unravel_index(np.concatenate((pos, neg)), truth.shape)
    X = np.asarray(mm[sy, sx, :88], dtype=np.float32)[:, keep]
    y = truth[sy, sx].astype(np.uint8)
    n_train = len(y)
    del sy, sx, pos, neg, neg_pool
    model = HistGradientBoostingClassifier(
        max_iter=iters, learning_rate=0.08, max_leaf_nodes=31,
        min_samples_leaf=40, l2_regularization=1.0, random_state=seed,
        early_stopping=False,
    )
    t0 = time.monotonic()
    model.fit(X, y)
    fit_s = round(time.monotonic() - t0, 1)
    print(f"Fit {n_train:,} catalogue samples, {len(keep)} channels in {fit_s}s", flush=True)
    del X, y
    gc.collect()

    prob = np.zeros(truth.shape, dtype=np.float32)
    for r0 in range(0, spec.HEIGHT, 256):
        r1 = min(r0 + 256, spec.HEIGHT)
        ry, rx = np.nonzero(footprint[r0:r1])
        if ry.size:
            prob[r0 + ry, rx] = model.predict_proba(
                np.asarray(mm[r0 + ry, rx, :88], dtype=np.float32)[:, keep]
            )[:, 1].astype(np.float32)
    del model
    placed = placement.get_strategy(STRATEGY, prob, footprint, threshold=0.3)
    del prob
    if not np.array_equal(np.unique(placed), [0.0, 1.0]):
        raise ValueError("candidate emission was not binary")
    if dilation_px:
        # Dilation happens *after* ranking at 5%, and is clipped to the official
        # finite footprint before the same canonical writer and hard gate.
        placed = (ndimage.binary_dilation(placed > 0, structure=disk(dilation_px))
                  & footprint).astype(np.float32)

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".unvalidated.tif")
    if tmp.exists():
        raise ValueError(f"refusing to replace scratch file: {tmp}")
    try:
        raster.write_submission(placed, tmp, sample, footprint=footprint)
        gate = raster.check_submission(tmp, template=sample)
        if not gate.ok:
            raise ValueError("REFUSING to publish an invalid raster:\n" + gate.text())
        tmp.rename(out)
        gate = raster.check_submission(out, template=sample)
        if not gate.ok:
            out.unlink()
            raise ValueError("STOP: moved file fails final-path hard gate")
    finally:
        if tmp.exists():
            tmp.unlink()
    record = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "unsubmitted local experiment, NOT the canonical entry's shipped file",
        "official_sources": {
            "format": spec.URLS["problem"] + "#submission-format",
            "known_mask": "https://community.drivendata.org/t/11516/4"},
        "inputs": {name: pin["sha256"] for name, pin in spec.PINS.items()},
        "feature_stack_sha256": sha256(features),
        "feature_meta_sha256": sha256(meta_path),
        "model": {"seed": seed, "max_neg": max_neg, "max_iter": iters,
                  "n_train": n_train, "fit_seconds": fit_s,
                  "kept_channels": list(np.array(channels)[keep]),
                  "dropped_channels": sorted(DROP)},
        "emission": {"strategy": STRATEGY, "dilation_px": dilation_px,
                     "positive_px": int((placed > 0).sum()),
                     "on_known_px": int(((placed > 0) & truth).sum())},
        "output": {"path": str(out), "sha256": sha256(out),
                   "bytes": out.stat().st_size, "gate": gate.as_dict()},
        "caveats": ["No DrivenData account or leaderboard score was accessed.",
                    "The two dropped columns may carry information on the hidden target.",
                    "The 5% budget is tuned against an SGMC proxy that cannot see "
                    "corrections near known traces, and the model has no 1 m DEM."],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Local candidate {out}: {record['output']['sha256']}; "
          f"13/13 gate {'PASS' if gate.ok else 'FAIL'}. Not uploaded.", flush=True)
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", required=True, type=Path)
    ap.add_argument("--features", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--dilation-px", type=int, choices=(0, 3), default=0,
                    help="post-ranking Euclidean dilation; 0 or predeclared 3px")
    a = ap.parse_args()
    build(a.entry.resolve(), a.features.resolve(), a.out.resolve(),
          a.report.resolve(), dilation_px=a.dilation_px)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
