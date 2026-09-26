#!/usr/bin/env python3
"""Session 6: strictly NESTED spatial check of the placement policy.

Why this exists
---------------
Session 5 froze "full88 + 4 px spacing + 3% budget" after comparing spacings
1/4/5 on the SAME four purged quadrants it then reported (0.2345 mean fold DTI).
The policy was therefore tuned and scored on the same geography. Session 4 and
session 5 both listed that as the open gap. This driver closes it:

  outer loop  : for each geographic quadrant q (2x2 blocks, 4 folds, 3 px
                Euclidean buffer, every fault system touching q purged globally)
                an OUTER model is trained exactly like session 5 (full88,
                400k negatives, 300 iterations, seed 7+q) and predicts q.
  inner loop  : for every other quadrant j != q an INNER model is trained with
                BOTH q and j (and every system touching either) excluded, and
                predicts j. The inner models never see quadrant q's labels,
                directly or through a model.
  selection   : for outer fold q, the policy (surface x budget x spacing) that
                maximises the unweighted mean inner DTI over the three j is
                chosen - using no information from q.
  evaluation  : that one policy is scored ONCE on the outer map of q.

The mean of those four outer scores is the honest estimate of "tune the
placement on the data we have, then apply it to unseen geography".

Policy grid (pre-specified, printed by --print-rule before any model runs):
  surface  : raw probability; kconv = probability convolved with the metric's own
             300 m triangular kernel (expected kernel-weighted coverage of a point
             placed at x); gauss3 = Gaussian sigma 3 px smoothing.
  fraction : 1, 1.5, 2, 3, 4, 5, 6, 8 % of the scored footprint.
  spacing  : minimum Chebyshev separation 1..6 px (budget_nodes semantics:
             probability-ordered suppression; underfill is reported).

Matched controls: the three frozen label-blind random-priority seeds of session 5
(17, 29, 43), passed through the SAME surface transform and placement, are
scored on every outer fold for every policy.

Reproduction check: the outer models use exactly session 5's sampling and
hyperparameters, so raw/3%/spacing4 on the outer maps must reproduce session 5's
per-fold full88 numbers; the greedy placement is asserted to be identical to
spatial_system_cv.budget_nodes for raw/3%/spacing {1,4,5}.

Not a leaderboard score. The truth is the mapped catalogue on held-out geography
(a transfer proxy), not the hidden new-fault labels.

    python nested_policy_cv.py --print-rule
    python nested_policy_cv.py --entry ../entry-src --scratch /tmp/s6 --out nested.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

TOOLS = Path(__file__).resolve().parent
SURFACES = ("raw", "kconv", "gauss3")
FRACTIONS = (0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08)
SPACINGS = (1, 2, 3, 4, 5, 6)
FROZEN = ("raw", 0.03, 4)
NULL_SEEDS = (17, 29, 43)
DECISION_RULE = {
    "selection": ("for outer fold q choose argmax over the grid of the unweighted mean inner DTI "
                  "over the three inner quadrants j != q (ties: first in surface, fraction, spacing order)"),
    "N1": "nested estimate (mean outer DTI of the inner-selected policies) > frozen policy raw/3%/s4 mean outer DTI",
    "N2": "the inner-selected policy beats the frozen policy on >= 3 of 4 outer folds",
    "N3": "the inner-selected policy beats the max of the three matched null seeds (same policy) on every outer fold",
    "N4_stability": "the same surface is selected on >= 3 of 4 outer folds",
    "adopt": ("change the local candidate's policy only if N1, N2, N3 and N4 all hold; otherwise keep "
              "raw/3%/s4 and report the nested estimate as its honest generalisation number"),
    "F1_feature_arm": ("separate pre-specified outer-only run with --n-channels 105 (the 17 label-free "
                       "strain/seismicity/conductivity family-rank and agreement channels the shipped model does not use): "
                       "adopt 105 only if its frozen-policy outer mean DTI > full88's AND it wins >= 3 of 4 outer folds"),
    "not_permission": "a pass is still not upload permission (registration, allowance and AI disclosure are human-only)",
}

# Session-6, pass 2: pre-specified AFTER the nested run and BEFORE this arm ran.
GRAV_FIX_RULE = {
    "defect": ("the supplied band iso_grav_anom_hg is the signed east-west derivative dG/dx (Spearman 0.95 vs "
               "numerical dG/dx, ~0 vs |grad G|), not the horizontal-gradient magnitude; the entry's grav_asa "
               "(channel 25) = sqrt(hg^2+vg^2) and grav_tilt (channel 26) = atan2(vg,|hg|) therefore ignore "
               "north-south gradients"),
    "G1_arm": ("outer-only run, frozen policy raw/3%/s4, channels 25/26 replaced by sqrt(H^2+vg^2) and "
               "atan2(vg,H) with H = s*|grad G|, s = least-squares scale of hg on numerical dG/dx (so H is in "
               "the supplied hg units); everything else identical to full88"),
    "G1_adopt": ("correctness fix, so adopt if NON-INFERIOR: G1 outer mean >= full88 outer mean - 0.005 AND no "
                 "fold worse than full88 by more than 0.01; otherwise report and keep the shipped channels"),
    "G1b_arm_added_after_F1": ("F1 adopted the 105-channel set (0.2418 vs 0.2345, 3/4 folds), so the same fix is "
                               "also measured on 105 channels: G1b = --n-channels 105 --grav-fix, compared with the "
                               "F1 105-channel run under the same non-inferiority rule"),
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def kernel_weights(radius_px: float = 3.0) -> np.ndarray:
    r = int(np.ceil(radius_px))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return np.maximum(1.0 - np.hypot(yy, xx) / radius_px, 0.0)


def make_surface(prob: np.ndarray, score: np.ndarray, kind: str) -> np.ndarray:
    """Label-free transform of a probability map; zero outside the score area."""
    p = np.where(score, prob, 0.0).astype(np.float64)
    if kind == "raw":
        s = p
    elif kind == "kconv":
        s = ndimage.correlate(p, kernel_weights(), mode="constant", cval=0.0)
    elif kind == "gauss3":
        s = ndimage.gaussian_filter(p, sigma=3.0, mode="constant", cval=0.0)
    else:
        raise ValueError(kind)
    s = np.where(score, s, 0.0)
    m = s.max()
    return (s / m if m > 0 else s).astype(np.float32)


def greedy_sequence(surface: np.ndarray, score: np.ndarray, spacing: int, max_budget: int) -> np.ndarray:
    """Emission order of budget_nodes, up to max_budget points (flat indices).

    Identical semantics to spatial_system_cv.budget_nodes: stable descending order,
    square (Chebyshev) suppression of radius spacing-1. Any prefix of length b is
    exactly budget_nodes' output for budget b.
    """
    flat = np.flatnonzero(score)
    order = flat[np.argsort(-surface.ravel()[flat], kind="stable")]
    if spacing == 1:
        return order[:max_budget]
    h, w = score.shape
    blocked = np.zeros(score.shape, dtype=bool)
    rad = spacing - 1
    out = []
    for idx in order.tolist():
        r, c = divmod(idx, w)
        if blocked[r, c]:
            continue
        out.append(idx)
        blocked[max(0, r - rad):r + rad + 1, max(0, c - rad):c + rad + 1] = True
        if len(out) == max_budget:
            break
    return np.asarray(out, dtype=np.int64)


def crop_box(mask: np.ndarray):
    rr = np.flatnonzero(mask.any(1))
    cc = np.flatnonzero(mask.any(0))
    return slice(rr[0], rr[-1] + 1), slice(cc[0], cc[-1] + 1)


def fast_components(pred_bool, gt_c, k_near, alpha=0.2, beta=0.8, radius_px=3.0):
    """Exact DTI for a BINARY prediction.

    For p in {0,1}, max_{x in S, d<=R} p(x) k(d(x,g)) = k(distance from g to the nearest
    emitted pixel) because k is decreasing; FP_w = sum over emitted of 1 - k(Dg(x)).
    Cross-checked against gems.metric.components on every map (see score_grid).
    """
    n_gt = int(gt_c.sum())
    fp_w = float((1.0 - k_near[pred_bool]).sum())
    if n_gt == 0 or not pred_bool.any():
        tp_w = 0.0
    else:
        d = ndimage.distance_transform_edt(~pred_bool)
        tp_w = float(np.maximum(1.0 - d[gt_c] / radius_px, 0.0).sum())
    fn_w = n_gt - tp_w
    denom = tp_w + alpha * fp_w + beta * fn_w
    return tp_w, fp_w, fn_w, (tp_w / denom if denom > 0 else 0.0)


def score_grid(prob_c, score_c, gt_c, metric):
    """Every policy in the grid on one cropped map. Exact: all mass and GT lie inside the crop."""
    k_near = np.maximum(1.0 - ndimage.distance_transform_edt(~gt_c) / 3.0, 0.0)
    checked = False
    n_score = int(score_c.sum())
    budgets = {f: max(1, int(round(f * n_score))) for f in FRACTIONS}
    bmax = max(budgets.values())
    res = {}
    for surf in SURFACES:
        s = make_surface(prob_c, score_c, surf)
        for sp in SPACINGS:
            seq = greedy_sequence(s, score_c, sp, bmax)
            for f in FRACTIONS:
                pred = np.zeros(score_c.shape, dtype=bool)
                pred.ravel()[seq[:budgets[f]]] = True
                tp_w, fp_w, fn_w, dti = fast_components(pred, gt_c, k_near)
                if (surf, f, sp) == FROZEN or not checked:
                    comp = metric.components(pred.astype(np.float32), gt_c)
                    if not np.isclose(comp.dti, dti, rtol=1e-9, atol=1e-12):
                        raise AssertionError(f"fast scorer {dti} != official {comp.dti}")
                    checked = True
                res[f"{surf}|{f}|{sp}"] = {"dti": dti, "tp_w": tp_w, "fp_w": fp_w,
                                           "fn_w": fn_w, "emitted": int(min(len(seq), budgets[f])),
                                           "budget": budgets[f]}
    return res


def corrected_gravity(entry: Path) -> dict:
    """Gravity ASA and tilt from the true horizontal-gradient magnitude (label-free, per-pixel)."""
    from gems import features as F  # noqa: PLC0415
    b, invalid = F.load_bands(str(entry / "data/training_features.tif"),
                              ["iso_grav_anom", "iso_grav_anom_hg", "iso_grav_anom_vg"])
    G = b["iso_grav_anom"].astype(np.float64)
    gy, gx = np.gradient(G, 100.0)
    inner = ndimage.binary_erosion(~invalid, iterations=2) & np.isfinite(gx) & np.isfinite(b["iso_grav_anom_hg"])
    hg = b["iso_grav_anom_hg"][inner].astype(np.float64)
    x = gx[inner]
    scale = float((hg * x).sum() / (x * x).sum())
    H = scale * np.hypot(gx, gy)
    vg = b["iso_grav_anom_vg"].astype(np.float64)
    asa = np.sqrt(H * H + vg * vg)
    tilt = F.tilt_angle(vg, H)
    asa[invalid] = np.nan
    tilt = np.where(invalid, np.nan, tilt)
    rs = np.random.default_rng(0).choice(np.flatnonzero(inner.ravel()), 200000, replace=False)
    from scipy.stats import spearmanr  # noqa: PLC0415
    diag = {"scale_hg_per_numerical_dGdx": scale,
            "spearman_hg_vs_dGdx": float(spearmanr(b["iso_grav_anom_hg"].ravel()[rs], gx.ravel()[rs]).statistic),
            "spearman_hg_vs_H": float(spearmanr(b["iso_grav_anom_hg"].ravel()[rs], H.ravel()[rs]).statistic)}
    return {"asa": asa.astype(np.float32), "tilt": np.asarray(tilt, dtype=np.float32), "diag": diag}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", type=Path)
    ap.add_argument("--scratch", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--max-neg", type=int, default=400_000)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--buffer-px", type=float, default=3.0)
    ap.add_argument("--n-channels", type=int, default=88)
    ap.add_argument("--print-rule", action="store_true")
    ap.add_argument("--outer-only", action="store_true", help="outer models + grid only (feature arm F1)")
    ap.add_argument("--grav-fix", action="store_true", help="G1: replace channels 25/26 with corrected gravity ASA/tilt")
    args = ap.parse_args()
    grid = {"surfaces": SURFACES, "fractions": FRACTIONS, "spacings": SPACINGS, "frozen": FROZEN,
            "null_seeds": NULL_SEEDS}
    if args.print_rule:
        print(json.dumps({"decision_rule": DECISION_RULE, "grid": grid, "grav_fix_rule": GRAV_FIX_RULE}, indent=2))
        return 0
    if not (args.entry and args.scratch and args.out):
        ap.error("--entry, --scratch and --out are required unless --print-rule")

    entry = args.entry.resolve()
    args.scratch.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(entry / "src"))
    from gems import metric, spec  # noqa: PLC0415
    from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: PLC0415
    cv = load_module("spatial_system_cv", TOOLS / "spatial_system_cv.py")

    pins = {}
    for name in ("labels.tif", "sample_submission.tif", "training_features.tif"):
        actual = sha256(entry / "data" / name)
        if actual != spec.PINS[name]["sha256"]:
            raise ValueError(f"{name}: official pin mismatch")
        pins[name] = actual
    with rasterio.open(entry / "data/labels.tif") as src:
        gt = src.read(1) == 1
    with rasterio.open(entry / "data/sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    meta = json.loads((entry / "data/evidence/features_meta.json").read_text())
    if meta["features_sha256"] != pins["training_features.tif"]:
        raise ValueError("feature stack source mismatch")
    mm = np.load(entry / "data/evidence/features.f32.npy", mmap_mode="r")
    grav_fix = None
    if args.grav_fix:
        grav_fix = corrected_gravity(entry)
        if meta["channels"][25] != "grav_asa" or meta["channels"][26] != "grav_tilt":
            raise ValueError("unexpected channel order for the gravity fix")

    def get_X(rows, cols):
        X = np.asarray(mm[rows, cols, :args.n_channels], dtype=np.float32)
        if grav_fix is not None:
            X[:, 25] = grav_fix["asa"][rows, cols]
            X[:, 26] = grav_fix["tilt"][rows, cols]
        return X

    traces, n = ndimage.label(gt, structure=np.ones((3, 3), int))
    systems = cv.exact_systems(traces, n, 5000.0)[traces]
    fold_ids = cv.spatial_folds(gt.shape, 2, 4)
    folds = list(range(4))
    score_of = {k: (fold_ids == k) & footprint for k in folds}
    held_of = {}
    for k in folds:
        ids = np.unique(systems[score_of[k]])
        ids = ids[ids > 0]
        held_of[k] = np.isin(systems, ids) & (systems > 0)

    def train_mask(excluded):
        exclusion = np.zeros(gt.shape, dtype=bool)
        for k in excluded:
            exclusion |= (fold_ids == k) | held_of[k]
        train = footprint & (ndimage.distance_transform_edt(~exclusion) > args.buffer_px)
        audit = {"excluded_folds": list(excluded), "train_pixels": int(train.sum()),
                 "train_positive_pixels": int((train & gt).sum())}
        for k in excluded:
            d = ndimage.distance_transform_edt(~score_of[k])
            shared = np.intersect1d(np.unique(systems[train & (systems > 0)]),
                                    np.unique(systems[score_of[k] & (systems > 0)]))
            audit[f"fold{k}"] = {"train_score_overlap": int((train & score_of[k]).sum()),
                                 "train_within_buffer": int((train & (d <= args.buffer_px)).sum()),
                                 "train_on_held_systems": int((train & held_of[k]).sum()),
                                 "shared_positive_systems": shared.tolist()}
            if (audit[f"fold{k}"]["train_score_overlap"] or audit[f"fold{k}"]["train_within_buffer"]
                    or audit[f"fold{k}"]["train_on_held_systems"] or len(shared)):
                raise ValueError(f"isolation failed: {audit}")
        if not audit["train_positive_pixels"]:
            raise ValueError("no training positives")
        audit["train_mask_sha256"] = hashlib.sha256(np.packbits(train).tobytes()).hexdigest()
        return train, audit

    def fit_predict(train, rng_seed, target_fold):
        pos = np.flatnonzero((train & gt).ravel())
        pool = np.flatnonzero((train & ~gt).ravel())
        neg = np.random.default_rng(rng_seed).choice(pool, min(args.max_neg, len(pool)), replace=False)
        sel = np.concatenate([pos, neg])
        rows, cols = np.unravel_index(sel, gt.shape)
        y = gt[rows, cols].astype(np.uint8)
        X = get_X(rows, cols)
        model = HistGradientBoostingClassifier(max_iter=args.iters, learning_rate=0.08, max_leaf_nodes=31,
                                               min_samples_leaf=40, l2_regularization=1, random_state=rng_seed,
                                               early_stopping=False)
        model.fit(X, y)
        del X
        prob = np.zeros(gt.shape, dtype=np.float32)
        rr, cc = np.nonzero(score_of[target_fold])
        for s0 in range(0, len(rr), 50000):
            r, c = rr[s0:s0 + 50000], cc[s0:s0 + 50000]
            prob[r, c] = model.predict_proba(get_X(r, c))[:, 1]
        return prob, {"n_pos": int(pos.size), "n_neg": int(neg.size), "rng_seed": rng_seed}

    t0 = time.time()
    out = {"kind": "strictly nested spatial policy selection; mapped-fault transfer proxy; NOT a leaderboard score",
           "decision_rule": DECISION_RULE, "grid": grid, "design": {k: str(v) for k, v in vars(args).items()},
           "official_sha256": pins, "tool_sha256": sha256(Path(__file__)),
           "placement_tool_sha256": sha256(TOOLS / "spatial_system_cv.py"),
           "n_traces": int(n), "n_systems": int(systems.max()), "outer": {}, "inner": {},
           "grav_fix": (grav_fix["diag"] | {"rule": GRAV_FIX_RULE}) if grav_fix is not None else None}

    def save():
        out["elapsed_seconds"] = round(time.time() - t0, 1)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=1, default=str) + "\n")

    for q in folds:
        # ---- outer model: identical to session 5 (seed + q) -------------------------
        cache = args.scratch / f"outer_q{q}.npy"
        train, audit = train_mask([q])
        if cache.exists():
            prob = np.load(cache)
            info = {"cached": True}
        else:
            prob, info = fit_predict(train, args.seed + q, q)
            np.save(cache, prob)
        box = crop_box(score_of[q])
        sc, gc, pc = score_of[q][box], (gt & score_of[q])[box], prob[box]
        # placement equivalence with the frozen implementation
        for sp in (1, 4, 5):
            ref = cv.budget_nodes(pc, sc, fraction=0.03, spacing=sp)
            seq = greedy_sequence(make_surface(pc, sc, "raw"), sc, sp, max(1, int(round(0.03 * sc.sum()))))
            mine = np.zeros(sc.shape, dtype=np.float32)
            mine.ravel()[seq] = 1
            if not np.array_equal(ref, mine):
                raise AssertionError(f"greedy_sequence != budget_nodes for spacing {sp}")
        grid_scores = score_grid(pc, sc, gc, metric)
        nulls = {}
        for seed in NULL_SEEDS:
            rp = np.random.default_rng(seed).random(gt.shape, dtype=np.float32)[box]
            nulls[str(seed)] = score_grid(rp, sc, gc, metric)
        out["outer"][str(q)] = {"geometry": audit, "train": info, "n_gt": int(gc.sum()),
                                "score_pixels": int(sc.sum()), "scores": grid_scores, "nulls": nulls}
        print(f"[{time.time()-t0:7.1f}s] outer q{q}: frozen {grid_scores['raw|0.03|4']['dti']:.4f}", flush=True)
        save()
        if args.outer_only:
            continue
        # ---- inner models: q AND j excluded -----------------------------------------
        for j in folds:
            if j == q:
                continue
            cache = args.scratch / f"inner_q{q}_j{j}.npy"
            train, audit = train_mask([q, j])
            if cache.exists():
                prob = np.load(cache)
                info = {"cached": True}
            else:
                prob, info = fit_predict(train, args.seed + 100 + 10 * q + j, j)
                np.save(cache, prob)
            box = crop_box(score_of[j])
            res = score_grid(prob[box], score_of[j][box], (gt & score_of[j])[box], metric)
            out["inner"][f"{q}-{j}"] = {"geometry": audit, "train": info, "scores": res}
            best = max(res, key=lambda k: res[k]["dti"])
            print(f"[{time.time()-t0:7.1f}s] inner q{q} j{j}: frozen {res['raw|0.03|4']['dti']:.4f} "
                  f"best {best} {res[best]['dti']:.4f}", flush=True)
            save()

    if args.outer_only:
        out["complete"] = True
        save()
        return 0
    # ---- selection and verdict ---------------------------------------------------------
    keys = [f"{s}|{f}|{sp}" for s in SURFACES for f in FRACTIONS for sp in SPACINGS]
    sel = {}
    for q in folds:
        inner_mean = {k: float(np.mean([out["inner"][f"{q}-{j}"]["scores"][k]["dti"] for j in folds if j != q]))
                      for k in keys}
        best = max(keys, key=lambda k: inner_mean[k])  # max() keeps the first on ties
        o = out["outer"][str(q)]
        null_max = max(o["nulls"][str(s)][best]["dti"] for s in NULL_SEEDS)
        frozen_key = "|".join(map(str, FROZEN))
        sel[str(q)] = {"selected": best, "inner_mean_selected": inner_mean[best],
                       "inner_mean_frozen": inner_mean[frozen_key],
                       "outer_selected": o["scores"][best]["dti"], "outer_frozen": o["scores"][frozen_key]["dti"],
                       "outer_null_max_selected_policy": null_max,
                       "outer_null_max_frozen_policy": max(o["nulls"][str(s)][frozen_key]["dti"] for s in NULL_SEEDS),
                       "outer_oracle_best": max(keys, key=lambda k: o["scores"][k]["dti"]),
                       "outer_oracle_best_dti": max(o["scores"][k]["dti"] for k in keys),
                       "top5_inner": sorted(keys, key=lambda k: -inner_mean[k])[:5]}
    nested = float(np.mean([v["outer_selected"] for v in sel.values()]))
    frozen = float(np.mean([v["outer_frozen"] for v in sel.values()]))
    surfaces = [v["selected"].split("|")[0] for v in sel.values()]
    verdict = {
        "nested_estimate": nested, "frozen_outer_mean": frozen,
        "N1": nested > frozen,
        "N2": sum(v["outer_selected"] > v["outer_frozen"] for v in sel.values()) >= 3,
        "N3": all(v["outer_selected"] > v["outer_null_max_selected_policy"] for v in sel.values()),
        "N4_stability": max(surfaces.count(s) for s in set(surfaces)) >= 3,
    }
    verdict["adopt"] = all(verdict[k] for k in ("N1", "N2", "N3", "N4_stability"))
    out["selection"] = sel
    out["verdict"] = verdict
    out["complete"] = True
    save()
    print(json.dumps({"selection": sel, "verdict": verdict}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
