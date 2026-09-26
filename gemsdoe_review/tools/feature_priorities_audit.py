#!/usr/bin/env python3
"""Measure the shipped feature stack against the task brief's three research
priorities, on the OFFICIAL rasters, with a distance-controlled background.

Priorities (task brief, page 967, as recorded in 6GEMSDOE/src/gems/features.py):

  1. horizontal gradient magnitude / tilt derivative on the magnetic and
     gravity layers;
  2. curvature and breaks in slope on the detrended DEM;
  3. cross-referencing strain rate, conductivity anomalies and earthquake
     density.

What this script MEASURES (everything from pinned official bytes; entry root
passed with --entry so the audited revision is explicit):

  A. The magnetic tilt-derivative channels on this revision's bytes: the
     angle range of the shipped `mag_tilt` and smoothed `tdr_tmi_s1.5/s3.0`
     (same formula as scripts/build_features.py: tilt = atan2(G_sigma(vg),
     |gradmag(G_sigma(tmi))|)), the share of the footprint that could ever
     support +/-45 deg tilt-depth contours, and the duplication of `mag_asa`
     with |tmi_hg|. Gravity equivalents are measured as the contrast.
  B. The DEM break-in-slope priority: AUC of the SHIPPED break channels
     (`det_elev_slope`, `slope_computed`, `slope_of_slope`,
     `slope_of_slope_s1.5/3.0`, |curv_total|) on catalogue positives vs a FAR
     background (>= 1 km from any catalogue pixel, so the score is not a
     halo artefact), then the same AUC for two candidate two-scale
     slope-break channels that are NOT in the 88-channel stack:
       slope_break_abs_s1_s6 = | G_1(slope) - G_6(slope) |
       slope_break_rel_s1_s6 = 2|G_1-G_6| / (G_1+G_6+eps)
     plus Spearman rank redundancy of each candidate against every shipped
     break-family channel on the far background. A 300-1000 m halo band is
     reported descriptively, never pooled into the far-background score.
  C. The cross-reference families: per-band far-background AUC for strain
     (geod_2ndinv, geod_shearrate, geod_dilaterate), seismicity
     (ieq_n100a15, polarity-corrected deq_n100a15) and conductivity
     (cond_surf, depth_to_base_surf), then pairwise Spearman BETWEEN family
     lead bands measured ON catalogue positives - i.e. how independent the
     "agreeing signals" actually are at the pixels we would cite them for.

What this script does NOT do: it does not train a model, does not touch the
submission file, and does not claim any hidden-score prediction. Catalogue
faults are MAPPED faults; AUC against them is a proxy for signal presence,
not for the competition target (faults missing from the catalogue). Spearman
ranks here are ordinal (ties broken by order), computed on large samples.

    python gemsdoe_review/tools/feature_priorities_audit.py \
        --entry /tmp/gems_entry \
        --out gemsdoe_review/evidence/feature_priorities_audit_2026-09-26.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

EPS = 1e-12


def sha256_file(path: Path, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_band(src, idx: int, invalid_below: float) -> np.ndarray:
    arr = src.read(idx).astype(np.float32)
    return np.where(arr < invalid_below, np.nan, arr)


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """Mann-Whitney AUC of pos vs neg (P(pos > neg) + 0.5 P(equal))."""
    x = np.concatenate([pos, neg])
    y = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
    order = np.argsort(x, kind="mergesort")
    xs, ys = x[order], y[order]
    ranks = np.empty(xs.size, dtype=np.float64)
    i = 0
    while i < xs.size:  # average ranks within tie groups
        j = i
        while j + 1 < xs.size and xs[j + 1] == xs[i]:
            j += 1
        ranks[i:j + 1] = 0.5 * (i + j) + 1.0
        i = j + 1
    r_pos = ranks[ys == 1].sum()
    n_pos, n_neg = pos.size, neg.size
    return float((r_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def sep(a: float) -> tuple[float, str]:
    """Separation either direction, with the winning polarity."""
    return (max(a, 1.0 - a), "+" if a >= 0.5 else "-")


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def smooth(a: np.ndarray, sigma: float) -> np.ndarray:
    """NaN-guarded Gaussian, same convention as gems.features.nan_gaussian."""
    badm = ~np.isfinite(a)
    r = int(np.ceil(3 * sigma))
    res = ndimage.gaussian_filter(np.where(badm, 0.0, a), sigma)
    grown = ndimage.binary_dilation(badm, iterations=r)
    return np.where(grown, np.nan, res)


def grad_mag(a: np.ndarray, spacing: float = 100.0) -> np.ndarray:
    """Central-difference |grad|, NaN-propagating, as gems.features.derivatives."""
    badm = ~np.isfinite(a)
    z = np.where(badm, 0.0, a)
    gx = np.zeros_like(z)
    gy = np.zeros_like(z)
    gx[:, 1:-1] = (z[:, 2:] - z[:, :-2]) / (2.0 * spacing)
    gy[1:-1, :] = (z[2:, :] - z[:-2, :]) / (2.0 * spacing)
    gx[:, 0] = (z[:, 1] - z[:, 0]) / spacing
    gx[:, -1] = (z[:, -1] - z[:, -2]) / spacing
    gy[0, :] = (z[1, :] - z[0, :]) / spacing
    gy[-1, :] = (z[-1, :] - z[-2, :]) / spacing
    halo = ndimage.binary_dilation(badm, iterations=1)
    return np.where(halo, np.nan, np.sqrt(gx * gx + gy * gy))


def tilt_stats(a: np.ndarray, finite: np.ndarray) -> dict:
    v = a[finite]
    v = v[np.isfinite(v)]
    av = np.abs(v)
    return {
        "abs_percentiles_deg": {f"p{q}": round(float(np.degrees(
            np.percentile(av, q))), 4) for q in (50, 90, 99, 99.9)},
        "share_abs_gt_45deg": float((av > np.pi / 4).mean()),
        "share_abs_gt_30deg": float((av > np.pi / 6).mean()),
        "n_finite": int(av.size),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n-background", type=int, default=60000)
    ap.add_argument("--n-halo", type=int, default=20000)
    args = ap.parse_args()

    entry = args.entry.resolve()
    sys.path.insert(0, str(entry / "src"))
    import rasterio  # entry dependency, audited environment
    from gems import spec

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=entry,
                          capture_output=True, text=True).stdout.strip()
    raster_path = entry / "data" / "training_features.tif"
    labels_path = entry / "data" / "labels.tif"
    sample_path = entry / "data" / "sample_submission.tif"

    with rasterio.open(sample_path) as s:
        footprint = np.isfinite(s.read(1))
    with rasterio.open(labels_path) as s:
        gt = (s.read(1) == 1)
    raster_sha = sha256_file(raster_path)
    pin_ok = raster_sha == spec.PINS["training_features.tif"]["sha256"]

    B = spec.BAND_INDEX
    bad = spec.FEATURE_INVALID_BELOW

    pos_mask = gt & footprint
    n_pos_total = int(pos_mask.sum())
    rng = np.random.default_rng(args.seed)
    dist_to_fault = ndimage.distance_transform_edt(~pos_mask) * spec.PIXEL_SIZE_M
    far_mask = (dist_to_fault > 1000.0) & footprint
    halo_mask = (dist_to_fault >= 300.0) & (dist_to_fault <= 1000.0) & footprint

    out: dict = {
        "kind": "feature-priority audit on official bytes; proxy AUCs against the "
                "MAPPED catalogue, never hidden-score predictions",
        "entry_root": str(entry),
        "entry_commit": head,
        "features_raster_sha256": raster_sha,
        "features_raster_sha256_matches_pin": bool(pin_ok),
        "pixel_size_m": spec.PIXEL_SIZE_M,
        "n_catalogue_positive_pixels": n_pos_total,
        "sampling": {
            "positives": "all catalogue positive pixels finite in the compared "
                         "channels (per-section n reported)",
            "far_background": f"footprint pixels >1000 m from any catalogue pixel, "
                              f"n<={args.n_background}, seed {args.seed}",
            "halo_band": "300-1000 m ring, descriptive only, never pooled",
        },
    }

    def sample_idx(mask: np.ndarray, finite: np.ndarray, n: int):
        m = mask & finite
        ys, xs = np.nonzero(m)
        if ys.size > n:
            sel = rng.choice(ys.size, size=n, replace=False)
            ys, xs = ys[sel], xs[sel]
        return ys, xs

    def chan_auc(pos_idx, bg_idx, a: np.ndarray, use_abs: bool) -> dict:
        pr, pc = pos_idx
        br, bc = bg_idx
        p = a[pr, pc]
        p = np.abs(p) if use_abs else p
        p = p[np.isfinite(p)].astype(np.float64)
        q = a[br, bc]
        q = np.abs(q) if use_abs else q
        q = q[np.isfinite(q)].astype(np.float64)
        a_ = auc(p, q)
        s, pol = sep(a_)
        return {"auc_pos_vs_far_bg": round(a_, 4), "separation": round(s, 4),
                "polarity": pol, "n_pos": int(p.size), "n_bg": int(q.size)}

    # ======================================================================
    # A. potential-field HGM / tilt priority
    # ======================================================================
    print("A: magnetic/gravity gradient + tilt channels", flush=True)
    with rasterio.open(raster_path) as src:
        hg = load_band(src, B["tmi_hg"], bad)
        vg = load_band(src, B["tmi_vg"], bad)
        ghg = load_band(src, B["iso_grav_anom_hg"], bad)
        gvg = load_band(src, B["iso_grav_anom_vg"], bad)
        tmi = load_band(src, B["tmi"], bad)

    finiteA = (np.isfinite(hg) & np.isfinite(vg) & np.isfinite(ghg)
               & np.isfinite(gvg) & np.isfinite(tmi) & footprint)

    mag_tilt = np.arctan2(vg, np.abs(hg))
    mag_asa = np.sqrt(hg * hg + vg * vg)
    grav_tilt = np.arctan2(gvg, np.abs(ghg))
    grav_asa = np.sqrt(ghg * ghg + gvg * gvg)
    # shipped smoothed tilts: tdr_<src>_s<sigma> = atan2(G_s(vg), |gradmag(G_s(tmi))|)
    tdr15 = np.arctan2(smooth(vg, 1.5), np.abs(grad_mag(smooth(tmi, 1.5))))
    tdr30 = np.arctan2(smooth(vg, 3.0), np.abs(grad_mag(smooth(tmi, 3.0))))
    del tmi

    posA = np.flatnonzero(pos_mask & finiteA)
    piA = np.unravel_index(posA, footprint.shape)
    bgA = sample_idx(far_mask, finiteA, args.n_background)

    secA = {
        "mag_tilt_raw": tilt_stats(mag_tilt, finiteA),
        "tdr_tmi_s1.5": tilt_stats(tdr15, finiteA),
        "tdr_tmi_s3.0": tilt_stats(tdr30, finiteA),
        "grav_tilt_raw": tilt_stats(grav_tilt, finiteA),
        "mag_asa_vs_abs_tmi_hg_pearson_r": round(float(np.corrcoef(
            mag_asa[finiteA].astype(np.float64),
            np.abs(hg[finiteA]).astype(np.float64))[0, 1]), 6),
        "grav_asa_vs_abs_isograv_hg_pearson_r": round(float(np.corrcoef(
            grav_asa[finiteA].astype(np.float64),
            np.abs(ghg[finiteA]).astype(np.float64))[0, 1]), 6),
        "scale_contrast_median_abs": {
            "tmi_vg_over_tmi_hg": float(np.median(
                np.abs(vg[finiteA]) / np.maximum(np.abs(hg[finiteA]), EPS))),
            "isograv_vg_over_isograv_hg": float(np.median(
                np.abs(gvg[finiteA]) / np.maximum(np.abs(ghg[finiteA]), EPS))),
        },
        "auc_pos_vs_far_bg": {
            "mag_tilt_abs": chan_auc(piA, bgA, mag_tilt, True),
            "tdr_tmi_s1.5_abs": chan_auc(piA, bgA, tdr15, True),
            "tdr_tmi_s3.0_abs": chan_auc(piA, bgA, tdr30, True),
            "grav_tilt_abs": chan_auc(piA, bgA, grav_tilt, True),
            "mag_asa": chan_auc(piA, bgA, mag_asa, False),
            "grav_asa": chan_auc(piA, bgA, grav_asa, False),
        },
    }
    out["A_potential_field_gradient_tilt"] = secA
    del hg, vg, ghg, gvg, mag_tilt, mag_asa, grav_tilt, grav_asa, tdr15, tdr30

    # ======================================================================
    # B. DEM curvature / break-in-slope priority, incl. the new candidates
    # ======================================================================
    print("B: DEM curvature + slope-break channels", flush=True)
    with rasterio.open(raster_path) as src:
        elev = load_band(src, B["det_elev"], bad)
        det_elev_slope = load_band(src, B["det_elev_slope"], bad)

    slope = grad_mag(elev)
    s1 = smooth(slope, 1.0)
    s6 = smooth(slope, 6.0)
    cand_abs = np.abs(s1 - s6)
    cand_rel = 2.0 * np.abs(s1 - s6) / (s1 + s6 + EPS)
    del s1, s6
    sos_raw = grad_mag(slope)                    # shipped `slope_of_slope`
    sos_15 = grad_mag(smooth(elev, 1.5))         # shipped `slope_of_slope_s1.5`
    sos_30 = grad_mag(smooth(elev, 3.0))         # shipped `slope_of_slope_s3.0`
    del elev
    # |Laplacian| as the |curv_total| stand-in (identical discrete operator:
    # r + t central second differences, as gems.features.curvature builds it)
    with rasterio.open(raster_path) as src:
        elev2 = load_band(src, B["det_elev"], bad)
    bade = ~np.isfinite(elev2)
    ze = np.where(bade, 0.0, elev2)
    lap = np.zeros_like(ze)
    lap[:, 1:-1] = (ze[:, 2:] - 2 * ze[:, 1:-1] + ze[:, :-2]) / 1e4
    lap[1:-1, :] += (ze[2:, :] - 2 * ze[1:-1, :] + ze[:-2, :]) / 1e4
    lap = np.where(ndimage.binary_dilation(bade, iterations=1), np.nan, lap)
    lap = np.abs(lap)
    del elev2, ze, bade

    finiteB = (np.isfinite(slope) & np.isfinite(sos_raw) & np.isfinite(sos_15)
               & np.isfinite(sos_30) & np.isfinite(cand_abs)
               & np.isfinite(cand_rel) & np.isfinite(lap)
               & np.isfinite(det_elev_slope) & footprint)
    posB = np.unravel_index(np.flatnonzero(pos_mask & finiteB), footprint.shape)
    bgB = sample_idx(far_mask, finiteB, args.n_background)
    hlB = sample_idx(halo_mask, finiteB, args.n_halo)

    channels = {
        "det_elev_slope_official": (det_elev_slope, True),
        "slope_computed": (slope, False),
        "slope_of_slope_raw": (sos_raw, False),
        "slope_of_slope_s1.5": (sos_15, False),
        "slope_of_slope_s3.0": (sos_30, False),
        "curv_total_abs_laplacian": (lap, True),
        "CANDIDATE_slope_break_abs_s1_s6": (cand_abs, False),
        "CANDIDATE_slope_break_rel_s1_s6": (cand_rel, False),
    }
    rows = {}
    for k, (a, ab) in channels.items():
        r = chan_auc(posB, bgB, a, ab)
        hv = a[hlB[0], hlB[1]]
        hv = np.abs(hv) if ab else hv
        hv = hv[np.isfinite(hv)]
        r["halo_median"] = float(np.median(hv)) if hv.size else None
        rows[k] = r
    red = {}
    bgi = bgB
    for cand, cval, cabs in (("slope_break_abs_s1_s6", cand_abs, False),
                             ("slope_break_rel_s1_s6", cand_rel, False)):
        red[cand] = {}
        cv = cval[bgi[0], bgi[1]]
        if cabs:
            cv = np.abs(cv)
        m = np.isfinite(cv)
        for k in ("slope_of_slope_raw", "slope_of_slope_s1.5",
                  "slope_of_slope_s3.0", "curv_total_abs_laplacian",
                  "slope_computed"):
            sv = channels[k][0][bgi[0], bgi[1]]
            if channels[k][1]:
                sv = np.abs(sv)
            mm = m & np.isfinite(sv)
            red[cand][k] = round(spearman(cv[mm].astype(np.float64),
                                          sv[mm].astype(np.float64)), 4)
    out["B_dem_curvature_slope_break"] = {
        "auc_pos_vs_far_bg": rows,
        "spearman_candidates_vs_shipped_on_far_bg": red,
        "note": "candidate two-scale slope-break channels are NOT in the "
                "88-channel stack; AUC here is catalogue-proxy signal presence "
                "only; `slope_of_slope_*` are |grad| of the smoothed slope and "
                "curv_total_abs_laplacian is |r+t| as in gems.features.curvature",
    }
    del slope, sos_raw, sos_15, sos_30, lap, cand_abs, cand_rel, det_elev_slope

    # ======================================================================
    # C. cross-reference families: strain / conductivity / seismicity
    # ======================================================================
    print("C: strain / conductivity / seismicity cross-reference", flush=True)
    fam_bands = {
        "strain": ["geod_2ndinv", "geod_shearrate", "geod_dilaterate"],
        "conductivity": ["cond_surf", "depth_to_base_surf"],
        "seismicity": ["ieq_n100a15", "deq_n100a15"],
    }
    fam_data: dict[str, dict[str, np.ndarray]] = {}
    with rasterio.open(raster_path) as src:
        for fam, names in fam_bands.items():
            fam_data[fam] = {n: load_band(src, B[n], bad) for n in names}

    fam_finite = footprint.copy()
    for fam in fam_data:
        for a in fam_data[fam].values():
            fam_finite &= np.isfinite(a)
    posC = np.unravel_index(
        np.flatnonzero(pos_mask & fam_finite), footprint.shape)
    bgC = sample_idx(far_mask, fam_finite, args.n_background)

    fam_auc = {}
    for fam, names in fam_bands.items():
        fam_auc[fam] = {}
        for n in names:
            a = fam_data[fam][n]
            if n == "deq_n100a15":  # distance: smaller is closer to quakes
                a = -a
                fam_auc[fam][n] = chan_auc(posC, bgC, a, False)
            else:
                fam_auc[fam][n] = chan_auc(posC, bgC, a, True)
    out["C_cross_reference_families"] = {
        "per_band_auc_pos_vs_far_bg": fam_auc,
        "n_pos": int(posC[0].size), "n_bg": int(bgC[0].size),
        "note": "abs-AUC = separation in either tail; deq negated so larger "
                "means closer to earthquakes",
    }

    mat = {}
    fams = list(fam_bands)
    for i, f1 in enumerate(fams):
        for f2 in fams[i + 1:]:
            a1 = fam_data[f1][fam_bands[f1][0]][posC].astype(np.float64)
            a2 = fam_data[f2][fam_bands[f2][0]][posC].astype(np.float64)
            m = np.isfinite(a1) & np.isfinite(a2)
            mat[f"{f1}|{f2}"] = round(spearman(a1[m], a2[m]), 4)
    out["C_cross_reference_families"]["lead_band_spearman_on_positives"] = mat
    del fam_data

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
