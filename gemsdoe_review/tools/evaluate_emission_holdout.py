#!/usr/bin/env python3
"""Choose an emission width on SGMC proxy *training* geography, audit elsewhere.

This is a **policy** holdout, not model CV and not a leaderboard estimate: the
canonical classifier was fitted on catalogue labels everywhere, but never on
SGMC code-2 labels. We tune only the post-processing radius on two western
spatial blocks, then audit the frozen radius on two eastern blocks. Every block
loses a 3-pixel edge to prevent truth in the other blocks entering its FP term.
The unmodified canonical file is the control. A candidate is written only if the
frozen width beats it on BOTH audit blocks and also beats no-skill blanket coverage
on the pooled audit area. The no-skill gate was added in bug/gap review after the
first readout; it is a safety rule, not another independent pre-registered test.

Use read-only checkouts/snapshots of 6GEMSDOE (format gate, metric, CV, writer)
and GEMSDOE (the independent GtContext implementation used in the prior audit).
Nothing is submitted, published to a site, or replaced in the entry repository.

    python gemsdoe_review/tools/evaluate_emission_holdout.py \\
      --entry /path/to/6GEMSDOE --metrics-src /path/to/GEMSDOE \\
      --proxy /path/to/proxy_catalogue.tif \\
      --out /tmp/emission_holdout.json [--candidate-out /tmp/candidate.tif]

Requirements for this optional review tool: numpy, scipy, rasterio. Inputs are
verified against the entry's SHA-256 pins and the official sample footprint.
Official metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric
Mask rule: https://community.drivendata.org/t/11516/4
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

PROXY_SHA256 = "7563e187171f7210d70295f958b0b2714c1fa504afa35f9a4688fc99b1e1122a"
WIDTHS = (0, 1, 2, 3, 4, 6)  # predeclared; no tuning on the two eastern blocks
RADIUS_PX = 3  # 300 m / 100 m, from the official metric


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def disk(radius: int) -> np.ndarray:
    if radius < 0:
        raise ValueError("radius must not be negative")
    yy, xx = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    return yy * yy + xx * xx <= radius * radius


def emit(source: np.ndarray, footprint: np.ndarray, known: np.ndarray,
         radius: int) -> np.ndarray:
    """One Euclidean dilation, clipped to the *official* footprint, not a box.

    Known-label pixels are removed by the official pixel-exact evaluation mask.
    This does NOT remove their 300 m neighbourhood: corrections can live there.
    """
    base = (np.isfinite(source) & (source > 0) & footprint)
    result = base if radius == 0 else ndimage.binary_dilation(base, structure=disk(radius))
    return result & footprint & ~known


def cores(fold_ids: np.ndarray, footprint: np.ndarray, known: np.ndarray,
          n_folds: int = 4, guard: int = RADIUS_PX) -> list[np.ndarray]:
    """Non-overlapping scored regions, with ≥ R px between each and another fold.

    A truth pixel in a *different* fold cannot influence the FP weight in a
    scored core, even though the context is built on the full proxy. All pixels
    excluded at the fold boundaries are explicitly unscored (not called TNs).
    """
    if fold_ids.shape != footprint.shape or known.shape != footprint.shape:
        raise ValueError("folds / footprint / known shapes differ")
    return [ndimage.binary_erosion(fold_ids == k, structure=disk(guard),
                                   border_value=0) & footprint & ~known
            for k in range(n_folds)]


def by_fold(ctx, prediction: np.ndarray, fold_cores: list[np.ndarray]) -> list[dict]:
    """Decompose the *official* TP and FP definitions by scored pixel geography.

    GtContext.credit_vector gives best weighted prediction for each truth pixel;
    fp_weight is 1-max(kernel(distance to truth)) per prediction pixel. We use
    its full-grid truth only where the guarded core guarantees another fold's
    truth is farther than the kernel. Both TP and FP exclude known-label pixels.
    Pool TP/FP/FN first, then calculate DTI; never average per-block ratios.
    """
    if prediction.shape != ctx.shape or any(c.shape != ctx.shape for c in fold_cores):
        raise ValueError("scoring shape mismatch")
    if np.any(prediction < 0) or np.any(prediction > 1):
        raise ValueError("predictions outside [0, 1]")
    credit = ctx.credit_vector(prediction.astype(np.float32, copy=False))
    fpw = ctx.fp_weight()
    out = []
    for k, core in enumerate(fold_cores):
        on_truth = core[ctx.gy, ctx.gx]
        tp = float(credit[on_truth].sum())
        n_gt = int(on_truth.sum())
        positions = core & (prediction > 0)
        fp = float((prediction[positions] * fpw[positions]).sum())
        out.append(components(tp, fp, n_gt, int(positions.sum()), fold=k,
                              scored_pixels=int(core.sum())))
    return out


def components(tp: float, fp: float, n_gt: int, n_emitted: int,
               **extra: object) -> dict:
    fn = n_gt - tp
    dti = tp / (tp + 0.2 * fp + 0.8 * fn + 1e-7) if n_gt else 0.0
    return {**extra, "n_gt": n_gt, "emitted_px": n_emitted, "tp_w": tp,
            "fp_w": fp, "fn_w": fn, "dti": dti}


def pooled(folds: list[dict]) -> dict:
    return components(sum(f["tp_w"] for f in folds), sum(f["fp_w"] for f in folds),
                      sum(f["n_gt"] for f in folds), sum(f["emitted_px"] for f in folds),
                      scored_pixels=sum(f["scored_pixels"] for f in folds))


def decide(scores: dict[str, dict], blanket: dict) -> dict:
    """Freeze radius on western blocks; audit on eastern blocks exactly once.

    A second, conservative safety gate compares to no-skill blanket coverage.
    This was added *after* the first untouched-block readout showed the original
    improvement still lost to blanket in the east. Do not retroactively call
    this independent pre-registration or repurpose the eastern blocks for tuning.
    """
    base = scores["dilate0"]
    selected = max(WIDTHS, key=lambda w: (scores[f"dilate{w}"]["tune"]["dti"], -w))
    chosen = scores[f"dilate{selected}"]
    baseline_audit_pass = bool(selected > 0
                               and chosen["tune"]["dti"] > base["tune"]["dti"]
                               and chosen["heldout"]["dti"] > base["heldout"]["dti"]
                               and all(chosen["folds"][k]["dti"] > base["folds"][k]["dti"]
                                       for k in (2, 3)))
    no_skill_pass = chosen["heldout"]["dti"] > blanket["heldout"]["dti"]
    return {"selected_radius_px": selected,
            "audit_pass": baseline_audit_pass, "no_skill_pass": no_skill_pass,
            "ready_for_external_test": baseline_audit_pass and no_skill_pass,
            "selection_folds": [0, 1], "untouched_audit_folds": [2, 3],
            "criterion": "tune pooled DTI maximum (tie: smaller radius); must beat "
                         "original on both eastern blocks and their pooled DTI",
            "no_skill_gate_note": "Conservative post-readout safety gate added in review: "
                                  "must also beat no-skill blanket on the east. "
                                  "It is not a pre-registered independent test.",
            "baseline_tune_dti": base["tune"]["dti"],
            "selected_tune_dti": chosen["tune"]["dti"],
            "baseline_audit_dti": base["heldout"]["dti"],
            "selected_audit_dti": chosen["heldout"]["dti"],
            "blanket_audit_dti": blanket["heldout"]["dti"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", required=True, type=Path,
                    help="read-only 6GEMSDOE snapshot containing code and pinned files")
    ap.add_argument("--metrics-src", required=True, type=Path,
                    help="read-only GEMSDOE snapshot containing src/metrics.py")
    ap.add_argument("--pred", type=Path, default=None,
                    help="default: the canonical shipped file, NEVER another entrant's")
    ap.add_argument("--proxy", required=True, type=Path,
                    help="SGMC code-2 proxy raster; not the competition's expert labels")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--candidate-out", type=Path,
                    help="optional *scratch* output, only when untouched blocks pass")
    args = ap.parse_args()

    entry = args.entry.resolve()
    sys.path.insert(0, str(entry / "src"))
    sys.path.insert(0, str(args.metrics_src.resolve()))
    from gems import cv, raster, spec  # noqa: E402
    from src.metrics import GtContext  # noqa: E402

    lab_path = entry / "data/labels.tif"
    template_path = entry / "data/sample_submission.tif"
    sub_path = args.pred or entry / "downloads/gems6_hgb88-topk03_33cec71ff0.tif"
    for name, path in (("labels.tif", lab_path), ("sample_submission.tif", template_path)):
        pin = spec.PINS[name]
        if not path.is_file() or path.stat().st_size != pin["bytes"] or sha256(path) != pin["sha256"]:
            raise SystemExit(f"STOP: official raster pin mismatch: {path}")
    if sha256(args.proxy) != PROXY_SHA256:
        raise SystemExit("STOP: proxy raster changed; verify its origin before evaluation")
    report = raster.check_submission(sub_path, template=template_path)
    if not report.ok:
        raise SystemExit("STOP: prediction fails hard format gate:\n" + report.text())

    with rasterio.open(template_path) as s:
        footprint = np.isfinite(s.read(1))
        crs, transform = s.crs, s.transform
    with rasterio.open(lab_path) as s:
        known = s.read(1) == 1
    with rasterio.open(args.proxy) as s:
        if (s.shape != footprint.shape or s.transform != transform or s.crs != crs):
            raise SystemExit("STOP: proxy grid does not match the official template")
        truth = (s.read(1) == 2) & footprint
    if not truth.any() or np.any(truth & known):
        raise SystemExit("STOP: invalid proxy truth (empty / overlaps known pixels)")
    # The code-2 proxy deliberately discards *all* traces within 3 px of known.
    # Record the blind spot. Do not infer that the real expert corrections are absent.
    near_known = ndimage.binary_dilation(known, structure=disk(RADIUS_PX))
    if np.any(truth & near_known):
        raise SystemExit("STOP: proxy code-2 labels are not disjoint from 3-px known halo")
    del near_known
    with rasterio.open(sub_path) as s:
        source = s.read(1)

    fold_spec = cv.make_folds(n_blocks=4, n_folds=4, buffer_px=RADIUS_PX)
    fold_ids = cv.block_ids(footprint.shape, fold_spec)
    core_masks = cores(fold_ids, footprint, known)
    if min(int((truth & c).sum()) for c in core_masks) == 0:
        raise SystemExit("STOP: one scored fold has no proxy truth")
    ctx = GtContext(truth, R_pixels=RADIUS_PX)
    # A no-skill calibration, computed on the same guarded geography and mask.
    # A candidate that only matches blanket coverage has not learned structure.
    blanket_folds = by_fold(ctx, footprint & ~known, core_masks)
    blanket = {"folds": blanket_folds, "tune": pooled(blanket_folds[:2]),
               "heldout": pooled(blanket_folds[2:])}
    scores = {}
    for width in WIDTHS:
        candidate = emit(source, footprint, known, width)
        f = by_fold(ctx, candidate, core_masks)
        scores[f"dilate{width}"] = {"full_emitted_px": int(candidate.sum()),
                                    "folds": f, "tune": pooled(f[:2]),
                                    "heldout": pooled(f[2:])}
        print(f"dilate{width}: train {scores[f'dilate{width}']['tune']['dti']:.5f} "
              f"audit {scores[f'dilate{width}']['heldout']['dti']:.5f}", flush=True)
    decision = decide(scores, blanket)
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "spatial policy holdout on SGMC, NOT a leaderboard/public-CV score",
        "method": "6GEMSDOE shipped emission, Euclidean dilation on full map, catalogue "
                  "pixels removed, 4 vertical spatial blocks, 3px score-edge guard; "
                  "pooled weighted terms rather than average of block DTI",
        "official_sources": {
            "metric": spec.URLS["problem"] + "#performance-metric",
            "pixel_exact_known_mask": "https://community.drivendata.org/t/11516/4",
        },
        "inputs": {"shipped_sha256": sha256(sub_path),
                   "labels_sha256": sha256(lab_path),
                   "sample_sha256": sha256(template_path),
                   "proxy_sha256": sha256(args.proxy),
                   "proxy_code2_px": int(truth.sum()),
                   "footprint_px": int(footprint.sum()),
                   "shipped_gate": {"ok": report.ok, "checks": len(report.checks)}},
        "warnings": [
            "SGMC proxy is not the expert-labelled GeoDAWN fault population.",
            "Proxy code 2 *excludes* faults within 300 m of known traces; it cannot "
            "evaluate the corrections/trace extensions organizers explicitly score.",
            "Classifier fitted on all catalogue geography; only postprocessing "
            "was selected without looking at the eastern SGMC proxy labels.",
            "Four vertical strips are heterogeneous, not four independent model fits.",
        ],
        "no_skill_blanket": blanket, "widths": scores, "decision": decision,
    }
    if args.candidate_out:
        if not decision["ready_for_external_test"]:
            print("No candidate written: baseline and no-skill safety gates not both passed.",
                  file=sys.stderr)
        else:
            target = args.candidate_out.resolve()
            if target.exists():
                raise SystemExit(f"STOP: candidate destination exists: {target}")
            tmp = target.with_name(target.stem + ".unvalidated.tif")
            if tmp.exists():
                raise SystemExit(f"STOP: scratch destination exists: {tmp}")
            candidate = emit(source, footprint, known, decision["selected_radius_px"])
            raster.write_submission(candidate.astype(np.float32), tmp, template_path,
                                    footprint=footprint)
            gated = raster.check_submission(tmp, template=template_path)
            if not gated.ok:
                tmp.unlink()
                raise SystemExit("STOP: candidate fails hard format gate:\n" + gated.text())
            tmp.rename(target)
            result["candidate"] = {"path": str(target), "sha256": sha256(target),
                                   "positive_px": int(candidate.sum()),
                                   "gate_ok": gated.ok, "gate_checks": len(gated.checks)}
            print(f"Local experimental candidate {target}: {gated.text()}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {args.out}. Frozen-width baseline audit: "
          f"{'PASS' if decision['audit_pass'] else 'FAIL'}; "
          f"no-skill safety gate: {'PASS' if decision['no_skill_pass'] else 'FAIL'}. "
          "No leaderboard claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
