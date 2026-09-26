#!/usr/bin/env python3
"""Session-3 measurements on the SHIPPING AXIS (blocked catalogue CV).

Session 2 measured the dead/duplicate magnetic channels (`mag_asa` ≈ |tmi_hg|,
`mag_tilt` p99 ≈ 3°) on the SGMC *proxy* with a 4-strip fold layout. This script
re-measures them on the yardstick the shipped file was actually chosen on — the
canonical 4×4 blocked, buffered folds of `6GEMSDOE` (`experiments_round2.json`
design: buffer 3 px, 400 000 negatives, 300 iterations, seed 0), scored with the
entry's own `src/gems/metric.py` on the public catalogue and on trace-reduced
ground truth.

Two measurements:

  ABLATION (`--mode ablation`)
    full88    channels[:88] — must reproduce the shipped decision number
              (topk_hard@0.03 mean DTI 0.1698); if it does not, the harness or
              the stack is wrong and the other rows are void.
    drop2     88 minus {mag_asa, mag_tilt}
    drop4     drop2 minus {tdr_tmi_s1.5, tdr_tmi_s3.0} (the angle-active but
              non-separating smoothed magnetic tilts, session-2 audit)
    All three are fit on IDENTICAL training rows (same fold masks, same
    negative sampling with the canonical rng) and scored identically, so any
    difference is attributable to the channel set alone.

  SEMISUP (`--mode semisup`)
    NEXT_STEPS P1.6's "still open" item: use the model's own high-confidence
    off-catalogue predictions, verified against independent signal families,
    as additional weighted positives for a second training pass.

    Protocol (spatially honest): for each fold k,
      M_{-k}  trains on blocks 1..3 only (exactly the canonical fold model);
      S_k     = pseudo-positives in held-out region k: off-catalogue pixels
                with p_{-k} >= 0.5 AND n_agree_top25 >= 4 (>= 4 of the 6
                source families in their top quartile — the entry's own gate
                machinery; global percentile ranks are hash-pinned, so no
                label information enters);
      M_final trains on the same 400k sampled negatives + all catalogue
                positives of blocks 1..3 + S_k (weight 0.5);
      M_final is scored in region k.
    M_final never sees the true labels of region k: its pseudo-labels there
    came from M_{-k}, which was trained without region k. Pooled score =
    mean over folds, compared with the canonical fold models (the ABLATION
    `full88` rows are the baseline, same folds/placement).

Neither mode writes anything into the entry; output is a single JSON evidence
file. Nothing here is a leaderboard score.

  python gemsdoe_review/tools/shipping_axis_ablation.py \
      --entry /tmp/gems_entry --mode ablation \
      --features /tmp/gems_entry/data/evidence/features.f32.npy \
      --out gemsdoe_review/evidence/ablation_shipping_axis_2026-09-26.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

DEFAULT_SEED = 0
NEG_SEED_BASE = 1000  # canonical: default_rng(1000 + k)
TRACE_SEED = 20240925  # canonical kept_trace_mask seed
TRACE_KEEP = (1.0, 0.5, 0.25)
TOPK_FRACS = (0.02, 0.03, 0.05)
PSEUDO_MIN_PROB = 0.5
PSEUDO_MIN_AGREE = 4
PSEUDO_WEIGHT = 0.5
DROP2 = {"mag_asa", "mag_tilt"}
DROP4 = DROP2 | {"tdr_tmi_s1.5", "tdr_tmi_s3.0"}


def sha256_file(path: Path, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_truth(entry: Path):
    from gems import spec
    with rasterio.open(entry / "data" / "labels.tif") as src:
        lab = src.read(1)
    with rasterio.open(entry / "data" / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    gt = lab == 1
    del lab
    trace_id, n_trace = ndimage.label(gt, structure=np.ones((3, 3), dtype=int))
    return gt, footprint, trace_id, int(trace_id.max()), spec


def kept_trace_table(trace_id: np.ndarray, n_trace: int, keep: float,
                     seed: int = TRACE_SEED) -> np.ndarray:
    if keep >= 1.0:
        return np.ones(n_trace + 1, dtype=bool)
    rng = np.random.default_rng(seed)
    keep_ids = rng.choice(n_trace, size=int(round(keep * n_trace)),
                          replace=False) + 1
    table = np.zeros(n_trace + 1, dtype=bool)
    table[keep_ids] = True
    return table


def fit_fold(mm, gt, footprint, folds, k: int, col_idx: np.ndarray,
             max_neg: int, iters: int, seed: int,
             extra_pos: np.ndarray | None = None,
             extra_pos_w: float | None = None):
    """Canonical run_fold training step (identical rows for identical k).

    `col_idx` holds the ABSOLUTE channel positions in the (possibly wider)
    memmap, because the drop variants are not contiguous slices.
    """
    from sklearn.ensemble import HistGradientBoostingClassifier
    from gems import spec

    shape = (spec.HEIGHT, spec.WIDTH)
    train_mask, test_mask = folds.train_test_masks(shape, k)
    train_mask &= footprint

    pos_idx = np.flatnonzero((gt & train_mask).ravel())
    neg_idx = np.flatnonzero((~gt & train_mask).ravel())
    rng = np.random.default_rng(NEG_SEED_BASE + k)
    n_neg = min(neg_idx.size, max_neg)
    neg_idx = rng.choice(neg_idx, size=n_neg, replace=False)
    sel = np.concatenate([pos_idx, neg_idx])
    w = None
    ep = None
    if extra_pos is not None and extra_pos.any():
        ep = np.flatnonzero(extra_pos.ravel())
        sel = np.concatenate([sel, ep])
        w = np.ones(sel.size, dtype=np.float32)
        # the pseudo-positives are the LAST len(ep) rows of sel
        w[sel.size - ep.size:] = extra_pos_w
    rows, cols = np.unravel_index(sel, shape)
    X = np.ascontiguousarray(mm[rows, cols][:, col_idx], dtype=np.float32)
    y = gt[rows, cols].astype(np.uint8)
    if extra_pos is not None and extra_pos.any():
        y = y.copy()
        y[-ep.size:] = 1  # the pseudo-positives are the last len(ep) rows
    del rows, cols, sel, pos_idx, neg_idx

    t0 = time.time()
    model = HistGradientBoostingClassifier(
        max_iter=iters, learning_rate=0.08, max_leaf_nodes=31,
        min_samples_leaf=40, l2_regularization=1.0, random_state=seed + k,
        early_stopping=False)
    model.fit(X, y, sample_weight=w)
    fit_s = round(time.time() - t0, 1)
    del X, y, w
    return model, test_mask, fit_s, int(n_neg), int((gt & train_mask).sum())


def predict_score(model, mm, score_mask: np.ndarray, col_idx: np.ndarray
                  ) -> np.ndarray:
    srows, scols = np.nonzero(score_mask)
    order = np.argsort(srows, kind="stable")
    srows, scols = srows[order], scols[order]
    grid_pred = np.zeros(score_mask.shape, dtype=np.float32)
    step = 200_000
    for i in range(0, srows.size, step):
        sl = slice(i, min(i + step, srows.size))
        grid_pred[srows[sl], scols[sl]] = model.predict_proba(
            np.ascontiguousarray(mm[srows[sl], scols[sl]][:, col_idx],
                                 dtype=np.float32))[:, 1]
    return grid_pred


def predict_full(model, mm, valid: np.ndarray, col_idx: np.ndarray,
                 chunk: int = 400_000) -> np.ndarray:
    """Probability surface on every valid pixel (pseudo-label pass)."""
    rows, cols = np.nonzero(valid)
    out = np.zeros(valid.shape, dtype=np.float32)
    for i in range(0, rows.size, chunk):
        sl = slice(i, min(i + chunk, rows.size))
        out[rows[sl], cols[sl]] = model.predict_proba(
            np.ascontiguousarray(mm[rows[sl], cols[sl]][:, col_idx],
                                 dtype=np.float32))[:, 1]
    return out


def topk_hard(p: np.ndarray, valid: np.ndarray, frac: float) -> np.ndarray:
    """Byte-identical to scripts/experiment.py::placements topk_hard."""
    p = np.clip(np.nan_to_num(p, nan=0.0), 0.0, 1.0)
    p = np.where(valid, p, 0.0)
    n_valid = int(valid.sum())
    k = max(1, int(round(frac * n_valid)))
    if k >= n_valid:
        return valid.astype(np.float32)
    inside = p[valid]
    thr = float(np.partition(inside, n_valid - k)[n_valid - k])
    return np.where((p >= thr) & valid, 1.0, 0.0).astype(np.float32)


def score_fold(metric, grid_pred: np.ndarray, score_mask: np.ndarray,
               gt: np.ndarray, trace_id: np.ndarray, n_trace: int,
               fracs: tuple[float, ...] = TOPK_FRACS) -> dict:
    """Canonical crop scoring (margin = ceil(R) + 1 around the held-out block)."""
    from gems import spec
    shape = (spec.HEIGHT, spec.WIDTH)
    ys, xs = np.nonzero(score_mask)
    margin = int(np.ceil(3.0)) + 1
    r0, r1 = max(0, int(ys.min()) - margin), min(spec.HEIGHT, int(ys.max()) + margin + 1)
    c0, c1 = max(0, int(xs.min()) - margin), min(spec.WIDTH, int(xs.max()) + margin + 1)
    sl = (slice(r0, r1), slice(c0, c1))
    crop_pred = grid_pred[sl]
    crop_valid = score_mask[sl]
    crop_gt_full = (gt & score_mask)[sl]
    crop_trace = trace_id[sl]
    n_gt_full = int(crop_gt_full.sum())
    rec: dict = {"n_gt": n_gt_full,
                 "crop": [int(r0), int(r1), int(c0), int(c1)],
                 "gt_full": {}, "trace_subsample": {}}
    cands = {f"topk_hard@{f:g}": topk_hard(crop_pred, crop_valid, f)
             for f in fracs}
    for name, arr in cands.items():
        comp = metric.components(arr, crop_gt_full)
        rec["gt_full"][name] = {"dti": comp.dti, "tp_w": comp.tp_w,
                                "fp_w": comp.fp_w, "fn_w": comp.fn_w,
                                "n_pos_pred": comp.n_pos_pred}
    for keep in TRACE_KEEP:
        if keep >= 1.0:
            continue
        table = kept_trace_table(trace_id, n_trace, keep)
        sub_gt = crop_gt_full & table[crop_trace]
        sub = {"n_gt_kept": int(sub_gt.sum())}
        for name in cands:
            comp = metric.components(cands[name], sub_gt)
            sub[name] = {"dti": comp.dti}
        rec["trace_subsample"][f"keep{keep:g}"] = sub
    return rec


def aggregate(folds_rec: list[dict], key_path: tuple[str, ...]) -> dict:
    agg: dict[str, list[float]] = {}
    for f in folds_rec:
        node: dict = f
        for part in key_path:
            node = node[part]
        for key, v in node.items():
            if isinstance(v, dict) and "dti" in v:
                agg.setdefault(key, []).append(v["dti"])
    return {k: {"mean_dti": round(float(np.mean(v)), 6),
                "min_dti": round(float(np.min(v)), 6),
                "max_dti": round(float(np.max(v)), 6),
                "per_fold": [round(x, 6) for x in v], "n_folds": len(v)}
            for k, v in sorted(agg.items(),
                               key=lambda kv: -float(np.mean(kv[1])))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--features", type=Path, required=True)
    ap.add_argument("--meta", type=Path, default=None,
                    help="features_meta.json (channel list); default <entry>/data/evidence/features_meta.json")
    ap.add_argument("--mode", choices=["ablation", "semisup"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--buffer", type=int, default=3)
    ap.add_argument("--max-neg", type=int, default=400_000)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = ap.parse_args()

    src = args.entry.resolve() / "src"
    sys.path.insert(0, str(src))
    from gems import cv as gcv  # noqa: E402
    from gems import metric  # noqa: E402
    from gems import spec  # noqa: E402

    meta_path = args.meta or (args.entry / "data" / "evidence" / "features_meta.json")
    meta = json.loads(Path(meta_path).read_text())
    channels: list[str] = meta["channels"]
    assert len(channels) >= 88, "stack must contain the 88 shipped channels first"
    mm = np.load(args.features, mmap_mode="r")

    gt, footprint, trace_id, n_trace, _ = load_truth(args.entry)
    folds = gcv.make_folds(n_blocks=args.blocks, n_folds=args.folds,
                           buffer_px=args.buffer)

    idx_of = {c: i for i, c in enumerate(channels)}
    if args.mode == "ablation":
        config_sets = {
            "full88": channels[:88],
            "drop2": [c for c in channels[:88] if c not in DROP2],
            "drop4": [c for c in channels[:88] if c not in DROP4],
        }
        colmap = {name: np.asarray([idx_of[c] for c in names], dtype=np.intp)
                  for name, names in config_sets.items()}
        folds_by_config: dict[str, list[dict]] = {}
        for name in config_sets:
            recs = []
            for k in range(args.folds):
                t0 = time.time()
                model, test_mask, fit_s, n_neg, n_pos = fit_fold(
                    mm, gt, footprint, folds, k, colmap[name],
                    args.max_neg, args.iters, args.seed)
                grid = predict_score(model, mm, test_mask & footprint,
                                     colmap[name])
                rec = score_fold(metric, grid, test_mask & footprint, gt,
                                 trace_id, n_trace)
                rec.update({"fold": k, "n_train_pos": n_pos,
                            "n_train_neg_used": n_neg, "fit_seconds": fit_s,
                            "wall_seconds": round(time.time() - t0, 1)})
                recs.append(rec)
                print(f"[{name}] fold {k}: " + " ".join(
                    f"topk@{f:g}={rec['gt_full'][f'topk_hard@{f:g}']['dti']:.4f}"
                    for f in TOPK_FRACS), flush=True)
                del model, grid
            folds_by_config[name] = recs

        out_configs = {}
        for name, names in config_sets.items():
            recs = folds_by_config[name]
            out_configs[name] = {
                "n_channels": len(names),
                "channels": names,
                "folds": recs,
                "aggregate_gt_full": aggregate(recs, ("gt_full",)),
                "aggregate_keep0.5": aggregate(recs, ("trace_subsample", "keep0.5")),
                "aggregate_keep0.25": aggregate(recs, ("trace_subsample", "keep0.25")),
            }
        configs = out_configs
    else:  # semisup
        assert "n_agree_top25" in channels
        i_agree = channels.index("n_agree_top25")
        nch = 88
        col88 = np.arange(88, dtype=np.intp)
        agree25 = np.asarray(mm[:, :, i_agree] >= PSEUDO_MIN_AGREE, dtype=bool)
        recs_base, recs_ss = [], []
        for k in range(args.folds):
            t0 = time.time()
            # Stage 1: canonical fold model (trained without region k)
            model, test_mask, fit_s, n_neg, n_pos = fit_fold(
                mm, gt, footprint, folds, k, col88, args.max_neg, args.iters,
                args.seed)
            region = test_mask & footprint
            p_full = predict_full(model, mm, footprint, col88)
            # Stage 2: verified pseudo-positives in the held-out region
            pseudo = (region & ~gt & (p_full >= PSEUDO_MIN_PROB) & agree25)
            n_pseudo = int(pseudo.sum())
            del p_full
            # Stage 3: second pass with the pseudo-positives (weight 0.5)
            model2, _, fit_s2, _, _ = fit_fold(
                mm, gt, footprint, folds, k, col88, args.max_neg, args.iters,
                args.seed, extra_pos=pseudo, extra_pos_w=PSEUDO_WEIGHT)
            grid_b = predict_score(model, mm, region, col88)
            grid_s = predict_score(model2, mm, region, col88)
            rec_b = score_fold(metric, grid_b, region, gt, trace_id, n_trace)
            rec_s = score_fold(metric, grid_s, region, gt, trace_id, n_trace)
            rec_b.update({"fold": k, "n_train_pos": n_pos,
                          "n_train_neg_used": n_neg, "fit_seconds": fit_s})
            rec_s.update({"fold": k, "n_train_pos": n_pos,
                          "n_train_neg_used": n_neg,
                          "n_pseudo_pos": n_pseudo,
                          "pseudo_min_prob": PSEUDO_MIN_PROB,
                          "pseudo_min_agree": PSEUDO_MIN_AGREE,
                          "pseudo_weight": PSEUDO_WEIGHT,
                          "fit_seconds_second_pass": fit_s2,
                          "wall_seconds": round(time.time() - t0, 1)})
            recs_base.append(rec_b)
            recs_ss.append(rec_s)
            print(f"[semisup] fold {k}: pseudo={n_pseudo:,} px | " +
                  "  ".join(f"base@{f:g}={rec_b['gt_full'][f'topk_hard@{f:g}']['dti']:.4f}"
                            f" ss@{f:g}={rec_s['gt_full'][f'topk_hard@{f:g}']['dti']:.4f}"
                            for f in TOPK_FRACS), flush=True)
            del model, model2, grid_b, grid_s
        configs = {
            "baseline_fold_models": {
                "n_channels": nch, "folds": recs_base,
                "aggregate_gt_full": aggregate(recs_base, ("gt_full",)),
                "aggregate_keep0.5": aggregate(recs_base, ("trace_subsample", "keep0.5")),
                "aggregate_keep0.25": aggregate(recs_base, ("trace_subsample", "keep0.25")),
            },
            "semisup_second_pass": {
                "n_channels": nch, "folds": recs_ss,
                "aggregate_gt_full": aggregate(recs_ss, ("gt_full",)),
                "aggregate_keep0.5": aggregate(recs_ss, ("trace_subsample", "keep0.5")),
                "aggregate_keep0.25": aggregate(recs_ss, ("trace_subsample", "keep0.25")),
            },
        }

    out = {
        "_what_this_is": (
            f"Session-3 {args.mode} measurement on the canonical shipping-axis "
            "yardstick (4x4 blocked buffered folds, 400k negatives, 300 iters, "
            "seed 0; scripts/experiment.py::run_fold protocol replicated "
            "line-by-line). Catalogue proxy only — not a leaderboard score."),
        "mode": args.mode,
        "entry_root": str(args.entry.resolve()),
        "entry_git_head": git_head(args.entry),
        "feature_stack": {
            "path": str(args.features),
            "sha256": sha256_file(Path(args.features)),
            "shape": list(mm.shape),
            "n_channels_total": len(channels),
            "meta_sha256": sha256_file(Path(meta_path)),
        },
        "official_pins": {
            "labels_sha256": sha256_file(args.entry / "data" / "labels.tif"),
            "sample_submission_sha256":
                sha256_file(args.entry / "data" / "sample_submission.tif"),
        },
        "design": {
            "n_blocks": args.blocks, "n_folds": args.folds,
            "buffer_px": args.buffer, "max_train_px": args.max_neg,
            "iters": args.iters, "seed": args.seed,
            "neg_sampling_seed_base": NEG_SEED_BASE,
            "trace_keep": list(TRACE_KEEP), "trace_keep_seed": TRACE_SEED,
            "topk_fractions": list(TOPK_FRACS),
            "cv_sha256": sha256_file(src / "gems" / "cv.py"),
            "metric_sha256": sha256_file(src / "gems" / "metric.py"),
        },
        "configs": configs,
        "caution": ("full88 must reproduce experiments_round2.json "
                    "(topk_hard@0.03 mean DTI 0.1698) before any other row is "
                    "interpreted; catalogue CV is a proxy for the public "
                    "catalogue, not the private new-fault test set."),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {args.out}", flush=True)
    return 0


def git_head(entry: Path) -> str:
    import subprocess
    try:
        r = subprocess.run(["git", "-C", str(entry), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
