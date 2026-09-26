#!/usr/bin/env python3
"""Independent Euclidean-distance check of canonical fold geometry.

A Manhattan 3 px buffer is not always a Euclidean 3 px buffer. Examine the
ACTUAL historical fold layouts, not just a contrived synthetic counterexample.
This script reads only the canonical cv.py implementation and pinned grid size;
no models/scores are computed or changed. Do not mistake a potentially leaked
training-mask pixel for a necessarily sampled labelled training point.

  python gemsdoe_review/tools/audit_cv_geometry.py --entry /tmp/gems_entry \\
    --out gemsdoe_review/evidence/cv_geometry_audit_2026-09-26.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy import ndimage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    src = args.entry.resolve() / "src"
    cv_file = src / "gems" / "cv.py"
    sys.path.insert(0, str(src))
    from gems import cv, spec  # noqa: E402

    shape = (spec.HEIGHT, spec.WIDTH)
    results = {}
    # The 4/4 and 6/6 configurations are found in the canonical experiment
    # evidence; the 5/3 and 6/4 layouts demonstrate the latent diagonal bug.
    for n_blocks, n_folds in ((4, 4), (6, 6), (5, 3), (6, 4)):
        key = f"{n_blocks}x{n_blocks}/{n_folds}folds"
        folds = cv.make_folds(n_blocks=n_blocks, n_folds=n_folds, buffer_px=3)
        rec = []
        for k in range(n_folds):
            train, score = folds.train_test_masks(shape, k)
            euclidean_dist = ndimage.distance_transform_edt(~score)
            leaking = train & (euclidean_dist <= 3.0)
            n = int(leaking.sum())
            rec.append({"fold": k, "potential_training_mask_pixels_inside_300m": n,
                        "sample_coordinates_row_col": np.argwhere(leaking)[:3].tolist()})
            print(f"{key} fold{k}: {n} potential buffer misses", flush=True)
            del train, score, euclidean_dist, leaking
        results[key] = rec
    output = {"kind": "cv Euclidean-buffer audit, NOT fault scores",
              "cv_sha256": hashlib.sha256(cv_file.read_bytes()).hexdigest(),
              "grid_shape": list(shape), "pixel_size_m": spec.PIXEL_SIZE_M,
              "radius_px": 3, "method": "scipy EDT on complement of held-out fold; count "
              "train pixels at Euclidean distance <=3 px",
              "caution": "Training-mask geometry only; actual catalogue sample and "
              "score not recomputed. Historical 4/4 and 6/6 may be unaffected "
              "even when other fold assignments have diagonal gaps.",
              "layouts": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
