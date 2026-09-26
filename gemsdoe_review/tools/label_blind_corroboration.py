#!/usr/bin/env python3
"""Session 6: does each flagged structure survive a model that never saw local labels?

Why this exists
---------------
The local candidate is produced by a model trained on EVERY catalogue pixel, so
near a mapped trace its probability partly reflects memorised labels rather than
geophysics. The prize scores NEW faults, and for most of them no label will ever
have been nearby. The outer models of the session-6 nested check are exactly the
right instrument: the model that predicts quadrant q was trained with q, a 300 m
Euclidean buffer and every fault system touching q removed. Its probability map
on q is therefore a label-blind reading of that ground.

For each large component of the candidate (identical construction to
geology_dossier.py: off-catalogue emitted pixels, 5x5 closing, 8-connectivity,
>= 200 closed px) this tool reports, over the component's EMITTED pixels:

  * oof_percentile_median - median rank of the label-blind probability inside its
    own quadrant's scored area (0.5 = what a random location gets);
  * oof_top3_fraction     - fraction of emitted pixels in the label-blind model's
    own top 3% (0.03 = random expectation).

A component is called
  * "label-blind corroborated" if oof_percentile_median >= 0.90,
  * "label-dependent"          if oof_percentile_median <  0.50,
  * "intermediate"             otherwise.
Thresholds are descriptive and were fixed before looking at the output.

Not a fault confirmation and not a score: a label-blind model can share the full
model's biases (same features, same catalogue population elsewhere).

    python label_blind_corroboration.py --entry ../entry-src \\
        --pred /scratch/candidate.tif --dossier dossier.json \\
        --oof-dir /scratch/s6/maps88 --out corroboration.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

TOOLS = Path(__file__).resolve().parent
CORROBORATED, DEPENDENT = 0.90, 0.50


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def quadrant_percentiles(oof: np.ndarray, score_masks: list[np.ndarray]) -> np.ndarray:
    """Rank of each scored pixel's probability within its own quadrant, in [0, 1]."""
    pct = np.full(oof.shape, np.nan, dtype=np.float32)
    for m in score_masks:
        idx = np.flatnonzero(m)
        order = np.argsort(oof.ravel()[idx], kind="stable")
        ranks = np.empty(idx.size, dtype=np.float64)
        ranks[order] = np.arange(idx.size)
        pct.ravel()[idx] = ranks / max(idx.size - 1, 1)
    return pct


def classify(p: float) -> str:
    if p >= CORROBORATED:
        return "label-blind corroborated"
    if p < DEPENDENT:
        return "label-dependent"
    return "intermediate"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--pred", type=Path, required=True)
    ap.add_argument("--dossier", type=Path, required=True)
    ap.add_argument("--oof-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    spec_cv = importlib.util.spec_from_file_location("spatial_system_cv", TOOLS / "spatial_system_cv.py")
    cv = importlib.util.module_from_spec(spec_cv)
    spec_cv.loader.exec_module(cv)

    with rasterio.open(args.entry / "data/labels.tif") as s:
        catalogue = s.read(1) == 1
    with rasterio.open(args.entry / "data/sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
    with rasterio.open(args.pred) as s:
        sub = s.read(1)
    pred = np.isfinite(sub) & (sub > 0)
    dossier = json.loads(args.dossier.read_text())
    if dossier["input_sha256"]["submission"] != sha256(args.pred):
        raise ValueError("dossier was not built from this prediction file")

    fold_ids = cv.spatial_folds(catalogue.shape, 2, 4)
    masks = [(fold_ids == k) & footprint for k in range(4)]
    oof = np.zeros(catalogue.shape, dtype=np.float32)
    oof_sha = {}
    for k in range(4):
        path = args.oof_dir / f"outer_q{k}.npy"
        part = np.load(path)
        if (part[~masks[k]] != 0).any():
            raise ValueError(f"{path} has mass outside its quadrant")
        oof += part
        oof_sha[path.name] = sha256(path)
    pct = quadrant_percentiles(oof, masks)

    off = pred & ~catalogue
    closed = ndimage.binary_closing(off, structure=np.ones((5, 5), dtype=bool))
    lab, n_lab = ndimage.label(closed, structure=np.ones((3, 3), dtype=int))
    by_id = {c["candidate_id"]: c for c in dossier["candidates"]}
    boxes = ndimage.find_objects(lab)
    rows = []
    for cid, rec in sorted(by_id.items()):
        box = boxes[cid - 1]
        comp = lab[box] == cid
        if int(comp.sum()) != rec["pixels"]:
            raise ValueError(f"component {cid} does not match the dossier geometry")
        em = comp & off[box]
        p = pct[box][em]
        p = p[np.isfinite(p)]
        if not p.size:
            continue
        med = float(np.median(p))
        rows.append({"candidate_id": cid, "class": rec["class"], "pixels": rec["pixels"],
                     "emitted_pixels": rec["emitted_pixels"], "centroid_lonlat": rec["centroid_lonlat"],
                     "azimuth_deg_from_north": rec["azimuth_deg_from_north"], "elongation": rec["elongation"],
                     "median_distance_to_catalogue_px": rec["distance_to_catalogue_px"]["median"],
                     "n_families_of_6": rec["agreement"]["n_families_of_6"],
                     "families": rec["agreement"]["families"],
                     "oof_percentile_median": round(med, 4),
                     "oof_top3_fraction": round(float((p >= 0.97).mean()), 4),
                     "label_blind_class": classify(med)})

    def summary(sel):
        if not sel:
            return {"n": 0}
        m = np.array([r["oof_percentile_median"] for r in sel])
        return {"n": len(sel), "median_of_oof_percentile_median": round(float(np.median(m)), 4),
                "corroborated": int((m >= CORROBORATED).sum()), "dependent": int((m < DEPENDENT).sum()),
                "mean_oof_top3_fraction": round(float(np.mean([r["oof_top3_fraction"] for r in sel])), 4)}

    from scipy.stats import spearmanr  # noqa: PLC0415
    fam = [r["n_families_of_6"] for r in rows]
    med = [r["oof_percentile_median"] for r in rows]
    shortlist = sorted([r for r in rows if r["label_blind_class"] == "label-blind corroborated"
                        and r["class"] == "isolated"],
                       key=lambda r: (-r["n_families_of_6"], -r["oof_percentile_median"], -r["pixels"]))
    out = {"kind": "label-blind corroboration of candidate components; NOT a score and NOT a fault confirmation",
           "pred_sha256": sha256(args.pred), "dossier_sha256": sha256(args.dossier),
           "dossier_generated_by": dossier.get("generated_by"), "oof_maps_sha256": oof_sha,
           "tool_sha256": sha256(Path(__file__)),
           "thresholds": {"corroborated_if_median_ge": CORROBORATED, "dependent_if_median_lt": DEPENDENT,
                          "random_expectation": {"oof_percentile_median": 0.5, "oof_top3_fraction": 0.03}},
           "summary": {"all": summary(rows), **{c: summary([r for r in rows if r["class"] == c])
                                               for c in ("isolated", "near_trace", "halo")}},
           "spearman_families_vs_oof_percentile": float(spearmanr(fam, med).statistic) if len(rows) > 2 else None,
           "shortlist_isolated_corroborated": [r["candidate_id"] for r in shortlist[:25]],
           "components": rows}
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["summary"], indent=1))
    print("spearman families vs oof percentile:", out["spearman_families_vs_oof_percentile"])
    for r in shortlist[:12]:
        print(r["candidate_id"], r["centroid_lonlat"], r["pixels"], r["n_families_of_6"], r["families"],
              r["oof_percentile_median"], r["oof_top3_fraction"], r["median_distance_to_catalogue_px"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
