#!/usr/bin/env python3
"""Audit the magnetic tilt-derivative channels, and test a working replacement.

FINDING (measured by this script, over the whole valid footprint)
-----------------------------------------------------------------
The 88-channel stack carries three magnetic channels built from the supplied
vertical-derivative band `tmi_vg`:

    mag_asa  = sqrt(tmi_hg^2 + tmi_vg^2)
    mag_tilt = atan2(tmi_vg, |tmi_hg|)          (the tilt derivative, TDR)

On the official data `tmi_vg` is ~1,300x smaller than `tmi_hg`
(median -0.0090 vs 13.15; IQR 0.101 vs 25.5). Two consequences follow, both of
which this script prints rather than asserts:

  * `mag_asa` is a numerical duplicate of the already-present `tmi_hg`
    (Pearson r = 1.000000 at float32 precision) — a wasted channel;
  * `mag_tilt` is a dead channel: |TDR| < 3.1 degrees for 99% of the footprint,
    so the +45/-45 degree contours that the tilt-depth method needs essentially
    do not exist (2e-5 of pixels). The gravity equivalents are NOT affected —
    `iso_grav_anom_vg` is the same order as its horizontal counterpart, so
    `grav_asa` and `grav_tilt` are genuine, independent channels.

The task brief's first research priority is "horizontal gradient magnitude /
tilt derivative on magnetic and gravity layers". The horizontal half is
implemented; the magnetic tilt half is not — the channel exists but carries
almost no information.

THE FIX TESTED HERE
-------------------
A vertical derivative IS constructible from a 2-D potential-field grid: for an
analytic field continued upward, multiplying the Fourier transform by the radial
wavenumber |k| gives dT/dz (this is the standard aeromagnetic technique behind
the tilt derivative; Salem et al. 2007, and every TDR implementation that is not
handed a measured vertical gradient). Doing so is a modelling choice — |k| is a
noise amplifier, so a low-pass is part of the operator, not an optional extra —
and the script states the cut-off it used.

This script builds TDR from `rtp` with a Fourier vertical derivative plus a
raised-cosine low-pass, and measures whether it separates mapped faults from the
rest of the footprint better than the dead channel does. That is a weak test
(it uses the catalogue, which is the wrong population for the prize) but it is
the only labelled set available, and a channel that cannot clear it is not worth
retraining for.

    python scripts/tilt_derivative_audit.py --out data/evidence/tilt_derivative_audit.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from gems import features as F  # noqa: E402
from gems import spec  # noqa: E402


def vertical_derivative_fourier(grid: np.ndarray, valid: np.ndarray,
                                cutoff_px: float) -> np.ndarray:
    """d/dz of a potential field: |k| in the Fourier domain, low-passed.

    `grid` must already be NaN-free (this function fills by nearest neighbour and
    tapers the frame). `cutoff_px` is the shortest wavelength retained, in pixels.
    """
    filled = grid.copy()
    bad = ~np.isfinite(filled)
    if bad.any():
        _, idx = ndimage.distance_transform_edt(bad, return_indices=True)
        filled = filled[tuple(idx)]

    h, w = filled.shape
    # cosine taper toward the frame mean over `taper` px, so the FFT is not
    # dominated by a discontinuity where the footprint ends
    taper = 64
    wy = np.ones(h)
    wx = np.ones(w)
    r = np.arange(taper) / taper
    ramp = 0.5 * (1.0 - np.cos(np.pi * r))
    wy[:taper] = ramp
    wy[-taper:] = ramp[::-1]
    wx[:taper] = ramp
    wx[-taper:] = ramp[::-1]
    mean = float(filled[valid].mean())
    work = (filled - mean) * wy[:, None] * wx[None, :]

    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    k = 2.0 * np.pi * np.sqrt(fy ** 2 + fx ** 2)     # rad / pixel
    kc = 2.0 * np.pi / cutoff_px
    with np.errstate(over="ignore"):
        low = np.where(k <= kc, 0.5 * (1.0 + np.cos(np.pi * k / kc)), 0.0)
    dz_per_px = np.fft.ifft2(np.fft.fft2(work) * (k * low)).real
    # k is in cycles per PIXEL, so the result is dT/dz with z in pixels; the
    # horizontal gradients below are finite differences with a 100 m spacing
    # (metres). Divide by the pixel size to put both on the same footing - the
    # first version of this audit forgot that and the vertical term then
    # dominated by a factor of 100.
    dz = dz_per_px / 100.0
    return np.where(valid, dz, np.nan)


def percentile_of(sorted_sample: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.searchsorted(sorted_sample, x, side="right") / sorted_sample.size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO_ROOT / "data/evidence/tilt_derivative_audit.json"))
    ap.add_argument("--cutoff-px", type=float, default=6.0)
    ap.add_argument("--sample", type=int, default=400_000)
    args = ap.parse_args()
    t0 = time.time()

    bands, invalid = F.load_bands(str(REPO_ROOT / "data" / "training_features.tif"),
                                  [n for n, _ in spec.FEATURE_BANDS])
    valid = ~invalid
    labels = np.zeros(valid.shape, dtype=np.uint8)
    import rasterio
    with rasterio.open(REPO_ROOT / "data" / "labels.tif") as s:
        labels = s.read(1)
    catalogue = labels == 1

    out: dict = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "generated_by": "scripts/tilt_derivative_audit.py",
                 "cutoff_px": args.cutoff_px}

    # ---- 1. the supplied bands are not on the same footing -------------------
    stats = {}
    for name in ("tmi_hg", "tmi_vg", "iso_grav_anom_hg", "iso_grav_anom_vg"):
        v = bands[name][valid]
        v = v[np.isfinite(v)]
        stats[name] = {"median": round(float(np.median(v)), 6),
                       "iqr": round(float(np.percentile(v, 75) - np.percentile(v, 25)), 6),
                       "abs_p95": round(float(np.percentile(np.abs(v), 95)), 6)}
    stats["ratio_tmi_hg_over_vg_median_abs"] = round(
        float(np.median(np.abs(bands["tmi_hg"][valid]))
              / max(np.median(np.abs(bands["tmi_vg"][valid])), 1e-30)), 1)
    out["supplied_derivative_bands"] = stats
    print(f"[{time.time()-t0:5.1f}s] supplied bands: tmi_hg median "
          f"{stats['tmi_hg']['median']}, tmi_vg median {stats['tmi_vg']['median']} "
          f"(ratio {stats['ratio_tmi_hg_over_vg_median_abs']})", flush=True)

    # ---- 2. the current magnetic tilt channel is dead ------------------------
    hg, vg = bands["tmi_hg"], bands["tmi_vg"]
    mag_asa = np.sqrt(hg ** 2 + vg ** 2)
    mag_tilt = np.degrees(np.arctan2(vg, np.abs(hg)))
    out["current_channels"] = {
        "mag_asa_pearson_r_vs_tmi_hg": round(float(np.corrcoef(
            mag_asa[valid][::17], hg[valid][::17])[0, 1]), 6),
        "mag_tilt_abs_p99_deg": round(float(np.percentile(np.abs(mag_tilt[valid]), 99)), 3),
        "mag_tilt_abs_max_deg": round(float(np.nanmax(np.abs(mag_tilt[valid]))), 3),
        "mag_tilt_fraction_abs_ge_45deg": float((np.abs(mag_tilt[valid]) >= 45).mean()),
    }
    print(f"[{time.time()-t0:5.1f}s] mag_asa r={out['current_channels']['mag_asa_pearson_r_vs_tmi_hg']} "
          f"vs tmi_hg; mag_tilt |p99|={out['current_channels']['mag_tilt_abs_p99_deg']} deg; "
          f"|TDR|>=45 in {out['current_channels']['mag_tilt_fraction_abs_ge_45deg']:.2e} of px",
          flush=True)

    # ---- 3. a working TDR from the RTP grid ---------------------------------
    rtp = bands["rtp"]
    dz = vertical_derivative_fourier(rtp, valid, args.cutoff_px)
    gx, gy = F.derivatives(rtp, spec.PIXEL_SIZE_M)
    hgm_rtp = np.hypot(gx, gy)
    tdr_new = np.degrees(np.arctan2(dz, hgm_rtp))
    good = valid & np.isfinite(tdr_new)
    out["constructed_tdr"] = {
        "source_band": "rtp",
        "vertical_derivative": f"Fourier |k| with raised-cosine low-pass at {args.cutoff_px} px",
        "abs_p99_deg": round(float(np.percentile(np.abs(tdr_new[good]), 99)), 3),
        "fraction_abs_ge_45deg": float((np.abs(tdr_new[good]) >= 45).mean()),
        "fraction_abs_ge_30deg": float((np.abs(tdr_new[good]) >= 30).mean()),
    }
    print(f"[{time.time()-t0:5.1f}s] constructed TDR: |p99|="
          f"{out['constructed_tdr']['abs_p99_deg']} deg, "
          f"|TDR|>=45 in {out['constructed_tdr']['fraction_abs_ge_45deg']:.4f} of px", flush=True)

    # ---- 4. does either channel separate mapped faults from the footprint? ---
    rng = np.random.default_rng(11)
    idx = np.flatnonzero(good.ravel())
    take = rng.choice(idx.size, size=min(args.sample, idx.size), replace=False)
    idx = np.sort(idx[take])
    rows, cols = np.unravel_index(idx, good.shape)
    cat_here = catalogue[rows, cols]

    def separation(field: np.ndarray) -> dict:
        v = np.abs(field[rows, cols])
        v = np.where(np.isfinite(v), v, np.nan)
        sample = np.sort(v[np.isfinite(v)])
        p_fault = percentile_of(sample, v[cat_here & np.isfinite(v)])
        p_back = percentile_of(sample, v[(~cat_here) & np.isfinite(v)])
        return {
            "median_percentile_at_mapped_faults": round(float(np.median(p_fault)), 4),
            "median_percentile_elsewhere": round(float(np.median(p_back)), 4),
            "separation": round(float(np.median(p_fault) - np.median(p_back)), 4),
        }

    out["separation_test"] = {
        # The tilt derivative locates a contact at its ZERO crossing, so the
        # discriminative statistic for TDR is -|TDR| (low absolute value = on the
        # edge), the opposite of the horizontal-gradient channels.
        "constructed_tdr_neg_abs": separation(-np.abs(tdr_new)),
        "n_sample": int(idx.size),
        "n_mapped_fault_px_in_sample": int(cat_here.sum()),
        "caveat": "the catalogue is the wrong population for the prize; this is a "
                  "sanity test that the channel carries structure at all, not a score",
        "current_mag_tilt": separation(mag_tilt),
        "constructed_tdr_rtp": separation(tdr_new),
        "provided_tmi_hg": separation(hg),
        "provided_tmi_vg": separation(vg),
    }
    print(f"[{time.time()-t0:5.1f}s] separation (faults minus elsewhere, median pct):")
    for k, v in out["separation_test"].items():
        if isinstance(v, dict):
            print(f"    {k:24s} {v['separation']:+.4f}")

    # ---- 5. what a tilt-depth method would need -----------------------------
    out["tilt_depth_feasibility"] = {
        "needs": "both the +45 and the -45 degree TDR contours through each target",
        "with_current_mag_tilt": "not feasible: contours essentially absent",
        "with_constructed_tdr": {
            "plus45_px": int((tdr_new[good] >= 45).sum()),
            "minus45_px": int((tdr_new[good] <= -45).sum()),
        },
    }
    print(f"[{time.time()-t0:5.1f}s] tilt-depth contours available with the "
          f"constructed TDR: +45 {out['tilt_depth_feasibility']['with_constructed_tdr']['plus45_px']:,} px, "
          f"-45 {out['tilt_depth_feasibility']['with_constructed_tdr']['minus45_px']:,} px")

    Path(args.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
