#!/usr/bin/env python3
"""RETIRED diagnostic — NOT spatially isolated CV (session-4 audit).

Do not run for model selection. Use spatial_system_cv.py instead. Historical
functions remain here solely to reproduce/explain archived session-3 evidence.
The old split sampled training negatives in the scoring geography, pseudo-trained
there too (sometimes with contradictory duplicate negatives), and omitted fault
pixels in system clustering. The reported 317 systems are 40 with exact linkage.
The quantitative 0.0060-vs-0.0148 conclusion is NOT a validated spatial-CV result.

Original description (historical, superseded):
Whole-fault-system holdout CV + semi-supervised second pass (session 3).

WHAT THIS MEASURES
------------------
The entry's blocked CV (mean DTI 0.1698 at top-3%) holds out spatial BLOCKS but
still trains on every fault that crosses a training block, including faults whose
continuation runs through the scored block. The competition target is faults that
are entirely absent from training. `NEXT_STEPS.md` P1 item 6 lists two open ideas
this tool implements and measures:

  A. whole-fault-SYSTEM holdout — cluster catalogue traces into systems (transitive
     closure of "any pixel of one trace within D km of any pixel of the other"),
     hold out entire systems per fold, train without them, and score the model's
     surface against exactly those systems as ground truth.
  B. semi-supervised second pass — from each fold's own base model (which never saw
     the held-out systems' labels), take high-confidence OFF-catalogue predictions
     that are independently verified (>= 2 of 6 signal families in their top
     quartile, per the rank tables), add them as pseudo-positives with weight w,
     retrain, and score the second model the same way.

SCORING RULE (the staff-clarified real rule, applied to the analogue)
---------------------------------------------------------------------
Staff: only the supplied training-label pixels are masked from evaluation. So in
each fold, predictions are zeroed on the pixels of the TRAINED catalogue (the
analogue of the supplied labels), everything else is scored: TP against the
held-out systems, FP for predicted mass in empty space (including 1-3 px OFF
trained catalogue pixels — the staff rule does not exempt those).
A no-skill blanket (p = 1 on every unmasked footprint pixel) is scored against the
same ground truth as the gate: a policy that cannot beat blanket on this proxy has
no evidence of skill on the new-fault-like population.

WHAT THIS DOES NOT MEASURE
--------------------------
The held-out systems are still CATALOGUE faults (mapped, digitised, typically the
cleaner expressions). New competition faults may be shorter, subtler, or near
mapped traces. This is a generalisation test, not a hidden-score prediction.
No leaderboard value is produced or implied.

Usage (from a checkout of this review repo, with the entry clone path):
    GEMSDOE_ENTRY_ROOT=/tmp/gems_entry6 python3 \\
        gemsdoe_review/tools/system_holdout_cv.py \\
        --entry /tmp/gems_entry6 --out gemsdoe_review/evidence/...json
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
from scipy.spatial import cKDTree

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "gemsdoe_review" / "tools"))


def load_entry(entry: Path):
    sys.path.insert(0, str(entry / "src"))
    from gems import metric, spec  # noqa: E402
    import gems.cv as gcv  # noqa: E402
    return metric, spec, gcv


def load_truth(entry: Path):
    with rasterio.open(entry / "data" / "labels.tif") as src:
        lab = src.read(1)
    with rasterio.open(entry / "data" / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    gt = lab == 1
    trace_id, n_trace = ndimage.label(gt, structure=np.ones((3, 3), dtype=int))
    return gt, footprint, trace_id, n_trace


def build_systems(trace_id: np.ndarray, n_trace: int, threshold_m: float,
                  pixel_m: float = 100.0) -> np.ndarray:
    """Union-find traces into systems: same system iff within threshold.

    Returns `system_of_trace` (length n_trace+1; index 0 is background).
    """
    thr_px = threshold_m / pixel_m
    # subsample each trace's pixels for the KD-tree (every 4th pixel along the
    # raster order is enough: trace width is 1-2 px, threshold >= 25 px)
    ys, xs = np.nonzero(trace_id > 0)
    ids = trace_id[ys, xs]
    step = 4
    ys, xs, ids = ys[::step], xs[::step], ids[::step]
    tree = cKDTree(np.column_stack([ys, xs]).astype(np.float64))
    pairs = tree.query_pairs(r=thr_px, output_type="ndarray")
    parent = np.arange(n_trace + 1)

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    n_merge = 0
    for a, b in pairs:
        ia, ib = ids[a], ids[b]
        if ia == ib:
            continue
        ra, rb = find(int(ia)), find(int(ib))
        if ra != rb:
            parent[rb] = ra
            n_merge += 1
    sys_of_trace = np.array([find(i) for i in range(n_trace + 1)])
    # renumber systems densely 0..S (0 = background stays 0)
    uniq = np.unique(sys_of_trace[1:])
    remap = {s: i + 1 for i, s in enumerate(uniq)}
    out = np.zeros(n_trace + 1, dtype=np.int32)
    for i in range(1, n_trace + 1):
        out[i] = remap[sys_of_trace[i]]
    print(f"  systems: {n_trace} traces -> {len(uniq)} systems "
          f"(threshold {threshold_m/1000:.1f} km, {n_merge} merges)", flush=True)
    return out


def predict_full(mm, channels_n: int, model, footprint: np.ndarray,
                 shape: tuple[int, int], chunk: int = 200_000) -> np.ndarray:
    """Model probability over the whole footprint, chunked (memmap-friendly)."""
    prob = np.zeros(shape, dtype=np.float32)
    ys, xs = np.nonzero(footprint)
    for i in range(0, ys.size, chunk):
        sl = slice(i, min(i + chunk, ys.size))
        X = np.asarray(mm[ys[sl], xs[sl], :channels_n], dtype=np.float32)
        prob[ys[sl], xs[sl]] = model.predict_proba(X)[:, 1]
    return prob


def topk_hard(prob: np.ndarray, valid: np.ndarray, frac: float) -> np.ndarray:
    inside = prob[valid]
    k = max(1, int(round(frac * inside.size)))
    thr = float(np.partition(inside, inside.size - k)[inside.size - k])
    return ((prob >= thr) & valid).astype(np.float32)


def score_rule_analogue(prob: np.ndarray, gt_test: np.ndarray,
                        trained_labels: np.ndarray, footprint: np.ndarray,
                        metric,
                        budgets=(0.01, 0.02, 0.03, 0.05)):
    """Score a probability surface the staff-rule way.

    pred is zeroed on trained-label pixels (the 'supplied labels' analogue);
    everything else is scored against gt_test with the official metric.
    The top-k budget is a fraction of the SCOREABLE footprint
    (footprint minus trained-label pixels), matching how a real submission's
    budget lands: the platform masks supplied-label pixels, so mass placed
    there is wasted, not charged.
    """
    scoreable = footprint & ~trained_labels
    pred_eval = np.where(trained_labels, 0.0, prob).astype(np.float32)
    out = {}
    for frac in budgets:
        hard = topk_hard(pred_eval, scoreable, frac)
        comp = metric.components(hard, gt_test)
        out[f"topk_hard@{frac:g}"] = comp.as_dict()
        # shipped-style: select the top-k over the WHOLE footprint (the way
        # scripts/build_submission.py does), then let the rule mask the pixels
        # that sit on supplied labels; the effective emission is smaller.
        hard_ship = topk_hard(np.where(footprint, prob, 0.0), footprint, frac)
        hard_ship = np.where(trained_labels, 0.0, hard_ship)
        comp_ship = metric.components(hard_ship, gt_test)
        out[f"topk_hard_shipsel@{frac:g}"] = comp_ship.as_dict()
    soft = np.where(trained_labels, 0.0, prob)
    out["soft_raw"] = metric.components(soft, gt_test).as_dict()
    # no-skill gate: p = 1 on every scoreable pixel (full blanket)
    blanket = scoreable.astype(np.float32)
    out["blanket_full"] = metric.components(blanket, gt_test).as_dict()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--features", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--system-threshold-m", type=float, default=5000.0)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--n-channels", type=int, default=88)
    ap.add_argument("--max-neg", type=int, default=200_000)
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--pseudo-frac", type=float, default=0.005,
                    help="top fraction of footprint as pseudo-positive pool")
    ap.add_argument("--pseudo-weight", type=float, default=0.5)
    ap.add_argument("--pseudo-min-agree", type=int, default=2,
                    help="min families in top quartile to verify a pseudo pixel")
    ap.add_argument("--skip-semisup", action="store_true")
    args = ap.parse_args()

    entry = args.entry.resolve()
    metric, spec, gcv = load_entry(entry)
    feats_path = args.features or (entry / "data" / "evidence" / "features.f32.npy")
    meta = json.loads((entry / "data" / "evidence" / "features_meta.json").read_text())
    channels = meta["channels"]
    if len(channels) < args.n_channels:
        print(f"ERROR: stack has only {len(channels)} channels", file=sys.stderr)
        return 2
    mm = np.load(feats_path, mmap_mode="r")
    print(f"feature stack {mm.shape}, using first {args.n_channels} channels "
          f"of {len(channels)}", flush=True)

    gt, footprint, trace_id, n_trace = load_truth(entry)
    print(f"footprint={int(footprint.sum())} gt={int(gt.sum())} "
          f"traces={n_trace}", flush=True)

    sys_of_trace = build_systems(trace_id, n_trace, args.system_threshold_m)
    n_sys = int(sys_of_trace[1:].max())
    system_of_px = sys_of_trace[trace_id]

    # deal systems into folds (seeded, deterministic)
    rng = np.random.default_rng(20260926)
    fold_of_system = np.zeros(n_sys + 1, dtype=int)
    fold_of_system[1:] = rng.permutation(n_sys) % args.folds

    # agreement channels for pseudo-verification (indices in the 105-ch stack)
    shape = (spec.HEIGHT, spec.WIDTH)
    fam_names = ["famrank_mag", "famrank_grav", "famrank_strain",
                 "famrank_seis", "famrank_cond", "famrank_topo"]
    fam_idx = {f: channels.index(f) for f in fam_names}
    # regional top-quartile thresholds + agreement map, measured ONCE on
    # finite footprint pixels (identical every fold; monotone per-pixel
    # transforms of the official bands, no label information)
    fam_thr = {}
    n_agree = np.zeros(shape, dtype=np.int32)
    for f, i in fam_idx.items():
        vals = np.asarray(mm[:, :, i], dtype=np.float32)
        fin = vals[footprint & np.isfinite(vals)]
        fam_thr[f] = float(np.quantile(fin, 0.75))
        n_agree += (vals >= fam_thr[f]).astype(np.int32)
        del vals
    print("family top-quartile thresholds: "
          + ", ".join(f"{f}={v:.3f}" for f, v in fam_thr.items()), flush=True)

    from sklearn.ensemble import HistGradientBoostingClassifier

    records = []
    t00 = time.time()
    for k in range(args.folds):
        t0 = time.time()
        held_sys = fold_of_system[system_of_px] == k
        held = gt & held_sys
        trained_labels = gt & ~held_sys
        print(f"\n=== fold {k}: held-out systems "
              f"{int(fold_of_system[1:][fold_of_system[1:] == k].size)} "
              f"({int(held.sum())} gt px); trained labels {int(trained_labels.sum())}",
              flush=True)

        # ---- base model: never sees the held-out systems as positives ---------
        pos_idx = np.flatnonzero(trained_labels.ravel())
        neg_pool = np.flatnonzero((~gt & footprint).ravel())
        r2 = np.random.default_rng(1000 + k)
        neg_idx = r2.choice(neg_pool, size=min(neg_pool.size, args.max_neg),
                            replace=False)
        sel = np.concatenate([pos_idx, neg_idx])
        rows, cols = np.unravel_index(sel, shape)
        X = np.asarray(mm[rows, cols, :args.n_channels], dtype=np.float32)
        y = gt[rows, cols].astype(np.uint8)
        model = HistGradientBoostingClassifier(
            max_iter=args.iters, learning_rate=0.08, max_leaf_nodes=31,
            min_samples_leaf=40, l2_regularization=1.0,
            random_state=args.seed + k, early_stopping=False)
        model.fit(X, y)
        del X, y, rows, cols, sel
        print(f"  base fit done [{time.time()-t0:.0f}s]", flush=True)

        prob = predict_full(mm, args.n_channels, model, footprint, shape)
        base_scores = score_rule_analogue(prob, held, trained_labels, footprint, metric)

        # diagnostics: where does the top-3% budget land?
        pred_eval = np.where(trained_labels, 0.0, prob)
        hard3 = topk_hard(pred_eval, footprint & ~trained_labels, 0.03) > 0
        d_cat = ndimage.distance_transform_edt(~trained_labels)
        rec = {
            "fold": k,
            "n_held_gt_px": int(held.sum()),
            "n_trained_label_px": int(trained_labels.sum()),
            "base": base_scores,
            "budget_landing@0.03": {
                "selected_px": int(hard3.sum()),
                "on_trained_labels_masked": int((hard3 & trained_labels).sum()),
                "within_3px_of_trained": int((hard3 & (d_cat <= 3.0)).sum()),
                "beyond_3px_of_trained": int((hard3 & (d_cat > 3.0)).sum()),
            },
        }
        del d_cat

        # ---- semi-supervised second pass --------------------------------------
        if not args.skip_semisup:
            # pseudo pool: top fraction of the fold's own surface, further than
            # 300 m from the SUPPLIED (trained) labels — the deployment rule:
            # new faults may sit anywhere, including near mapped traces
            d_trained = ndimage.distance_transform_edt(~trained_labels)
            pool = (pred_eval >= np.quantile(
                pred_eval[footprint & ~trained_labels], 1 - args.pseudo_frac))
            pool &= footprint & ~trained_labels & (d_trained > 3.0)
            del d_trained
            # independent-signal verification: >= N families in their top quartile
            pseudo = pool & (n_agree >= args.pseudo_min_agree)
            # keep only the largest linear-ish components (>= 5 px)
            lab_p, n_p = ndimage.label(pseudo, structure=np.ones((3, 3), int))
            if n_p:
                sizes = np.bincount(lab_p.ravel())
                keep = np.zeros(n_p + 1, dtype=bool)
                keep[1:] = sizes[1:] >= 5
                pseudo = keep[lab_p]
            n_pseudo = int(pseudo.sum())
            rec["pseudo"] = {
                "pool_px": int(pool.sum()),
                "verified_px": n_pseudo,
                "pseudo_gt_overlap_px": int((pseudo & held).sum()),
                "weight": args.pseudo_weight,
            }
            print(f"  pseudo: pool={int(pool.sum())} verified={n_pseudo} "
                  f"(overlap with held truth {int((pseudo & held).sum())})",
                  flush=True)
            if n_pseudo:
                pos2 = np.concatenate([pos_idx, np.flatnonzero(pseudo.ravel())])
                sel2 = np.concatenate([pos2, neg_idx])
                rows2, cols2 = np.unravel_index(sel2, shape)
                X2 = np.asarray(mm[rows2, cols2, :args.n_channels],
                                dtype=np.float32)
                y2 = np.zeros(len(sel2), dtype=np.uint8)
                y2[:len(pos2)] = 1  # catalogue positives AND pseudo-positives
                w2 = np.ones(len(sel2), dtype=np.float32)
                w2[len(pos_idx):len(pos_idx) + n_pseudo] = args.pseudo_weight
                model2 = HistGradientBoostingClassifier(
                    max_iter=args.iters, learning_rate=0.08, max_leaf_nodes=31,
                    min_samples_leaf=40, l2_regularization=1.0,
                    random_state=args.seed + 100 + k, early_stopping=False)
                model2.fit(X2, y2, sample_weight=w2)
                del X2, y2, w2, rows2, cols2, sel2
                print(f"  semi-sup fit done [{time.time()-t0:.0f}s]", flush=True)
                prob2 = predict_full(mm, args.n_channels, model2, footprint, shape)
                rec["semisup"] = score_rule_analogue(
                    prob2, held, trained_labels, footprint, metric)
                del prob2
        records.append(rec)
        print(f"  fold {k} base topk@0.03 DTI="
              f"{base_scores['topk_hard@0.03']['dti']:.4f} "
              f"blanket={base_scores['blanket_full']['dti']:.4f} "
              f"[{time.time()-t0:.0f}s]", flush=True)
        del prob, pred_eval, hard3

    # ---- aggregate ------------------------------------------------------------
    def agg(key: str) -> dict:
        out = {}
        names = set()
        for r in records:
            if key in r:
                names |= set(r[key])
        for n in names:
            vals = [r[key][n]["dti"] for r in records if key in r and n in r[key]]
            if vals:
                out[n] = {"mean_dti": float(np.mean(vals)),
                          "min_dti": float(np.min(vals)),
                          "max_dti": float(np.max(vals)),
                          "n_folds": len(vals)}
        return dict(sorted(out.items(), key=lambda kv: -kv[1]["mean_dti"]))

    out = {
        "_what_this_is": (
            "Whole-fault-system holdout CV and semi-supervised second pass, "
            "scored with the staff-clarified masking rule on the official "
            "catalogue. NOT a leaderboard value and NOT a private-score "
            "prediction; held-out systems are still mapped catalogue faults."),
        "design": {
            "entry_commit": None,  # filled by caller notes
            "system_threshold_m": args.system_threshold_m,
            "n_systems": n_sys,
            "folds": args.folds,
            "n_channels": args.n_channels,
            "max_neg": args.max_neg,
            "iters": args.iters,
            "model": ("HistGradientBoostingClassifier(lr=0.08, "
                      "max_leaf_nodes=31, min_samples_leaf=40, "
                      "l2_regularization=1.0)"),
            "scoring_rule": (
                "predictions zeroed on trained-label pixels (staff: only the "
                "supplied training-label pixels are masked); GT = held-out "
                "systems; official DTI (alpha 0.2, beta 0.8, R=3 px)"),
            "pseudo_policy": {
                "frac": args.pseudo_frac,
                "weight": args.pseudo_weight,
                "min_agree_families_top_quartile": args.pseudo_min_agree,
                "min_off_catalogue_distance_px": 3,
                "min_component_px": 5,
            },
        },
        "folds": records,
        "aggregate_base": agg("base"),
        "aggregate_semisup": agg("semisup"),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(f"\nwrote {args.out} [{time.time()-t00:.0f}s total]")
    print("\naggregate base (top 6):")
    for n, v in list(out["aggregate_base"].items())[:6]:
        print(f"  {n}: {v['mean_dti']:.4f}")
    if out["aggregate_semisup"]:
        print("aggregate semi-sup (top 6):")
        for n, v in list(out["aggregate_semisup"].items())[:6]:
            print(f"  {n}: {v['mean_dti']:.4f}")
    return 0


if __name__ == "__main__":
    print("RETIRED: this diagnostic is not spatially isolated CV. "
          "Use spatial_system_cv.py; see SESSION4.md.", file=sys.stderr)
    raise SystemExit(2)
