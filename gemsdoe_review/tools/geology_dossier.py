#!/usr/bin/env python3
"""Per-candidate geological dossier for a submission.

WHY THIS EXISTS
---------------
`NEXT_STEPS.md` item 9 asks for geological reasoning behind every structure the
model flags, and the competition's own framing rewards it: both prize phases score
expert-mapped faults, and the Phase-2 test set is "updated by expert review of all
Phase 1 submissions" (DrivenData staff, forum topic 11527 post 7, 2026-09-23). A
submission that says *why* a structure is plausibly a fault is legible to that
process in a way a bare pixel mask is not.

The entry had no such document. This script produces the measurement half of it:
for each connected group of predicted pixels it reports

  * geometry            - pixel count, area, principal-axis length/width, strike,
                          elongation (how lineament-like the group actually is);
  * diagnostics         - the median over the group's ACTUALLY EMITTED pixels,
                          compared to sampled valid pixels in the scored footprint
                          (closing only defines component topology); the favourable
                          direction of each diagnostic is explicit;
  * agreement           - how many of six diagnostic families (not statistically
                          independent measurements: magnetic edge, gravity edge,
                          slope break, strain, conductivity, seismicity) have an
                          extreme regional value, each counting once;
  * relation to the map - distance to the supplied catalogue, and how much of the
                          group sits within the 300 m metric kernel of a mapped
                          trace;
  * metric              - NOT estimated locally; the hidden new-fault labels are
                          unavailable and a catalogue-crop score would mislead;
  * tilt-depth          - an explicit NOT ESTIMABLE flag: the supplied bands
                          cannot support the required +/-45 degree contours.

These are measured diagnostics, NOT expert interpretations or confirmed faults.
`current_geology_report.py` generates a separate cautious geological hypothesis
and counterargument for every candidate from these measurements; expert review
and high-resolution DEM validation remain outstanding.

    python scripts/geology_dossier.py --pred downloads/<submission>.tif \\
        --fragment-out data/evidence/geology_fragments.csv
    python scripts/current_geology_report.py --dossier data/evidence/geology_dossier.json --out data/evidence/geology_dossier.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from gems import features as F  # noqa: E402
from gems import metric, raster, spec  # noqa: E402

KM2_PER_PX = (spec.PIXEL_SIZE_M / 1000.0) ** 2  # 0.01 km^2 per pixel


# ---------------------------------------------------------------------------
# diagnostics: (band, family, favourable direction, human description)
# ---------------------------------------------------------------------------
DIAGNOSTICS: list[tuple[str, str, str, str]] = [
    ("tmi", "magnetic", "extremity",
     "total magnetic intensity (provided, nT-scale)"),
    ("mag_hgm", "magnetic_edge", "high",
     "horizontal gradient of TMI - sharp magnetic contact"),
    ("mag_asa", "magnetic_edge", "high",
     "sqrt(provided TMI hg² + vg²); almost the same as TMI hg on this grid"),
    # The supplied tmi_vg is too small relative to hg for a physical tilt-depth
    # reading. Keep the measurement for audit, but never count it as independent
    # positive magnetic-edge evidence (see tilt_derivative_audit.json).
    ("tdr_mag", "untrusted_tilt", "untrusted",
     "atan2(tmi_vg, |tmi_hg|); NOT calibrated as a physical magnetic tilt"),
    ("mgd", "untrusted_magnetic_ratio", "untrusted",
     "tmi_hg / mag_asa; nearly constant because mag_asa ≈ tmi_hg"),
    ("rtp", "magnetic", "extremity", "reduced-to-pole magnetic anomaly"),
    ("iso_grav_anom", "gravity", "extremity", "isostatic gravity anomaly"),
    ("grav_hgm", "gravity_edge", "high",
     "horizontal gradient of the isostatic gravity anomaly - density contact"),
    ("grav_asa", "gravity_edge", "high", "analytic-signal amplitude of gravity"),
    ("det_elev", "topography", "extremity",
     "detrended elevation - positive = high ground"),
    ("elev_hgm", "topography_edge", "high",
     "horizontal gradient of detrended elevation = slope"),
    ("slope_of_slope", "slope_break", "high",
     "rate of change of slope - breaks in slope, a scarp indicator"),
    ("curv_total", "curvature", "extremity", "total curvature of the DEM"),
    ("curv_plan", "curvature", "extremity", "plan curvature (across-slope bending)"),
    ("geod_2ndinv", "strain", "high",
     "second invariant of the geodetic strain-rate tensor"),
    ("geod_shearrate", "strain", "high", "geodetic shear rate"),
    ("geod_dilaterate", "strain", "high", "geodetic dilatation rate"),
    ("cond_surf", "conductivity", "high",
     "conductivity surface - clay alteration / fluid pathway proxy"),
    ("depth_to_base_surf", "conductive_base_depth", "high",
     "depth to conductive base surface (NOT a direct basement depth)"),
    ("ieq_n100a15", "seismicity", "high", "earthquake density/intensity"),
    ("deq_n100a15", "seismicity", "low", "distance to nearest earthquake"),
]

# families that can flag a fault, each counting at most once toward agreement
FAMILIES = ("magnetic_edge", "gravity_edge", "slope_break", "strain",
            "conductivity", "seismicity")

DERIVED = {
    "mag_hgm": "tmi_hg",
    "mag_asa": "tmi_asa_computed",
    "mgd": "mag_mgd",
    "tdr_mag": "tdr_mag",
    "grav_hgm": "iso_grav_anom_hg",
    "grav_asa": "grav_asa",
    "elev_hgm": "det_elev_hgm_computed",
    "slope_of_slope": "slope_of_slope",
    "curv_total": "curv_total",
    "curv_plan": "curv_plan",
}


def read_grid(path: Path) -> np.ndarray:
    with rasterio.open(path) as s:
        return s.read(1)


def build_diagnostics(features_path: Path) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Compute every diagnostic named above on the full grid, NaN outside the
    valid mask, and return (diagnostics, valid)."""
    names = [n for n, _ in spec.FEATURE_BANDS]
    bands, invalid = F.load_bands(str(features_path), names)
    valid = ~invalid
    out: dict[str, np.ndarray] = {}
    for key in ("tmi", "rtp", "iso_grav_anom", "det_elev", "geod_2ndinv",
                "geod_shearrate", "geod_dilaterate", "cond_surf",
                "depth_to_base_surf", "ieq_n100a15", "deq_n100a15"):
        out[key] = bands[key]
    out["mag_hgm"] = bands["tmi_hg"]
    out["grav_hgm"] = bands["iso_grav_anom_hg"]
    # analytic signal from the provided horizontal gradient
    out["mag_asa"] = np.sqrt(bands["tmi_hg"] ** 2 + bands["tmi_vg"] ** 2)
    out["grav_asa"] = np.sqrt(bands["iso_grav_anom_hg"] ** 2
                              + bands["iso_grav_anom_vg"] ** 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        out["mgd"] = bands["tmi_hg"] / np.where(out["mag_asa"] > 0,
                                                out["mag_asa"], np.nan)
        out["tdr_mag"] = np.degrees(np.arctan2(bands["tmi_vg"],
                                               np.abs(bands["tmi_hg"])))
        gx, gy = F.derivatives(bands["det_elev"], spec.PIXEL_SIZE_M)
        elev_hgm = np.hypot(gx, gy)
        out["elev_hgm"] = elev_hgm
        curv = F.curvature(bands["det_elev"], spec.PIXEL_SIZE_M)
        out["slope_of_slope"] = curv.slope_of_slope
        out["curv_total"] = curv.total
        out["curv_plan"] = curv.plan  # profile is a different curvature axis
    return out, valid


def percentile_of_medians(values: dict[str, np.ndarray], valid: np.ndarray,
                          n_regional: int = 750_000, seed: int = 20
                          ) -> dict[str, np.ndarray]:
    """For each diagnostic, the sorted sample of regional values used to turn a
    candidate median into a percentile. Sampling (rather than sorting 5.2M values
    per band) keeps the memory honest and the percentile stable."""
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(valid.ravel())
    if idx.size > n_regional:
        idx = rng.choice(idx, size=n_regional, replace=False)
    idx.sort()
    rows, cols = np.unravel_index(idx, valid.shape)
    out = {}
    for k, v in values.items():
        sample = v[rows, cols]
        sample = sample[np.isfinite(sample)]
        if sample.size == 0:
            raise ValueError(f"no finite regional reference for diagnostic {k}")
        out[k] = np.sort(sample)
    return out


def percentile(sorted_sample: np.ndarray, x: float) -> float:
    if not np.isfinite(x):
        return float("nan")
    return float(np.searchsorted(sorted_sample, x, side="right") / sorted_sample.size)


def candidate_geometry(rows: np.ndarray, cols: np.ndarray) -> dict:
    """PCA geometry. Strike is the azimuth of the major axis, degrees clockwise
    from north, folded to [0, 180)."""
    x = cols.astype(np.float64)
    y = rows.astype(np.float64)
    cx, cy = x.mean(), y.mean()
    cov = np.cov(np.vstack([x - cx, y - cy]))
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    major = 4.0 * np.sqrt(max(vals[0], 0.0))   # length of the +/-2 sigma PCA axis
    minor = 4.0 * np.sqrt(max(vals[1], 0.0))
    vx, vy = vecs[0, 0], vecs[1, 0]
    # Raster rows increase SOUTH; geographic north is negative row direction.
    az = float(np.degrees(np.arctan2(vx, -vy)) % 180.0)
    return {
        "pixels": int(rows.size),
        "area_km2": round(float(rows.size) * KM2_PER_PX, 3),
        "centroid_row": int(round(cy)),
        "centroid_col": int(round(cx)),
        "bbox_rows": [int(rows.min()), int(rows.max())],
        "bbox_cols": [int(cols.min()), int(cols.max())],
        "major_axis_km": round(major * spec.PIXEL_SIZE_M / 1000.0, 2),
        "minor_axis_km": round(minor * spec.PIXEL_SIZE_M / 1000.0, 2),
        "elongation": round(float(major / minor) if minor > 0 else float("inf"), 2),
        "azimuth_deg_from_north": round(az, 1),
    }


def lonlat_of(row: float, col: float) -> tuple[float, float]:
    from rasterio.warp import transform as warp_transform

    with rasterio.open(REPO_ROOT / "data" / "labels.tif") as s:
        t = s.transform
        crs = s.crs
    x, y = t * (col + 0.5, row + 0.5)
    lon, lat = warp_transform(crs, "EPSG:4326", [x], [y])
    return float(lon[0]), float(lat[0])


def tilt_depth_bins(diag: dict[str, np.ndarray], rows: np.ndarray,
                    cols: np.ndarray) -> dict:
    """Tilt-depth estimate, or an explicit statement that it is not available.

    The standard method (Miller & Singh 1994; Salem et al. 2007) halves the
    horizontal distance between the +45 and -45 degree tilt-derivative contours
    that bracket a target. Measured by `scripts/tilt_derivative_audit.py`, the
    supplied magnetic vertical-derivative band `tmi_vg` is ~256x smaller than
    `tmi_hg`, so the supplied-data tilt derivative never leaves +/-3.1 degrees
    (|TDR| >= 45 deg in 2.2e-5 of pixels) and the contours the method needs do not
    are not reliably available as a bracket for geological depth inversion.
    Rather than invent a number, this returns the measurement and no depth.
    """
    tdr = diag["tdr_mag"][rows, cols]
    tdr = tdr[np.isfinite(tdr)]
    frac = float((np.abs(tdr) >= 45.0).mean()) if tdr.size else float("nan")
    return {
        "status": "not estimable from the supplied bands",
        "why": "the uncalibrated magnetic tilt has |TDR| >= 45 deg on "
               f"{frac:.2e} of this candidate's emitted pixels; this does not "
               "establish trustworthy, bracketing +45/-45 degree contours "
               "(see gemsdoe_review/evidence/tilt_derivative_audit.json)",
        "candidate_fraction_abs_tdr_ge_45": frac,
        "what_would_be_needed": "a magnetic vertical derivative that is not three "
                                "orders of magnitude smaller than the horizontal "
                                "one - either the original survey grid or a "
                                "Fourier |k| derivative whose low-pass and scaling "
                                "have been validated (the naive construction is "
                                "tested in the audit script and is not yet trusted)",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--min-pixels", type=int, default=200)
    ap.add_argument("--closing", type=int, default=5)
    ap.add_argument("--regional-sample", type=int, default=750_000,
                    help="fixed-seed regional percentile reference (sampled to bound RAM)")
    ap.add_argument("--out", default=str(REPO_ROOT / "data/evidence/geology_dossier.json"))
    ap.add_argument("--fragment-out", type=Path,
                    help="optional inventory of ALL components below min-pixels; "
                         "these are too small for geological interpretation")
    args = ap.parse_args()
    if args.regional_sample < 1 or args.min_pixels < 1 or args.closing < 1 or args.closing % 2 != 1:
        ap.error("regional-sample and min-pixels must be positive; closing must be positive and odd")

    t0 = time.time()
    pred_path = Path(args.pred)
    feature_path = REPO_ROOT / "data" / "training_features.tif"
    label_path = REPO_ROOT / "data" / "labels.tif"
    for name, path in (("training_features.tif", feature_path),
                       ("labels.tif", label_path)):
        pin = spec.PINS[name]
        if (not path.is_file() or path.stat().st_size != pin["bytes"] or
                raster.sha256_file(path) != pin["sha256"]):
            raise SystemExit(f"STOP: official raster failed SHA-256 pin: {path}")
    gate = raster.check_submission(pred_path)
    if not gate.ok:
        raise SystemExit("STOP: refusing to interpret an ungated raster:\n" + gate.text())
    sub = read_grid(pred_path)
    pred = np.isfinite(sub) & (sub > 0)
    labels = read_grid(REPO_ROOT / "data" / "labels.tif")
    catalogue = labels == 1
    print(f"[{time.time()-t0:5.1f}s] {pred_path.name}: {int(pred.sum()):,} predicted px, "
          f"{int((pred & catalogue).sum()):,} on the catalogue", flush=True)

    diag, valid = build_diagnostics(feature_path)
    regional = percentile_of_medians(diag, valid & np.isfinite(sub),
                                     n_regional=args.regional_sample)
    print(f"[{time.time()-t0:5.1f}s] diagnostics ready ({len(diag)} bands)", flush=True)

    # candidates = predicted pixels off the catalogue, closed, labelled
    off = pred & ~catalogue
    closed = ndimage.binary_closing(off, structure=np.ones((args.closing, args.closing),
                                                           dtype=bool))
    lab, n_lab = ndimage.label(closed, structure=np.ones((3, 3), dtype=int))
    sizes = ndimage.sum_labels(np.ones_like(lab, dtype=np.int64), lab,
                               index=np.arange(1, n_lab + 1))
    keep = np.flatnonzero(sizes >= args.min_pixels) + 1
    print(f"[{time.time()-t0:5.1f}s] {n_lab:,} components, {keep.size} of them "
          f">= {args.min_pixels} px", flush=True)

    dist_to_cat = ndimage.distance_transform_edt(~catalogue, sampling=1.0)

    # Account for the BELOW-THRESHOLD positives, too. They were not screened
    # for geology here; some may be narrow real lineaments. Inventory locations
    # with an explicit 'not identified' status rather than calling discoveries.
    fragment_info = None
    if args.fragment_out is not None:
        small = np.flatnonzero(sizes < args.min_pixels) + 1
        boxes = ndimage.find_objects(lab)
        fragments = []
        x_projected, y_projected = [], []
        with rasterio.open(label_path) as s:
            transform, crs = s.transform, s.crs
        for cid in small:
            box = boxes[cid - 1]
            if box is None:
                raise ValueError(f"missing bounds for small component {cid}")
            yy, xx = np.nonzero(lab[box] == cid)
            yy += box[0].start
            xx += box[1].start
            emitted = off[yy, xx]
            erows, ecols = yy[emitted], xx[emitted]
            x, y = transform * (float(xx.mean()) + 0.5, float(yy.mean()) + 0.5)
            x_projected.append(x)
            y_projected.append(y)
            fragments.append({
                "component_id": int(cid), "closed_px": int(yy.size),
                "emitted_px": int(erows.size),
                "centroid_row": round(float(yy.mean()), 2),
                "centroid_col": round(float(xx.mean()), 2),
                "median_distance_to_known_m": (round(float(np.median(
                    dist_to_cat[erows, ecols])) * spec.PIXEL_SIZE_M, 1)
                    if erows.size else ""),
                "assessment": f"below {args.min_pixels}-closed-px screen; "
                              "NOT an identified fault; inspect shape, bands "
                              "and 1m/field data",
            })
        from rasterio.warp import transform as warp_transform
        longitudes, latitudes = (warp_transform(crs, "EPSG:4326", x_projected, y_projected)
                                 if fragments else ([], []))
        for r, lon, lat in zip(fragments, longitudes, latitudes):
            r["centroid_lon"] = round(float(lon), 4)
            r["centroid_lat"] = round(float(lat), 4)
        args.fragment_out.parent.mkdir(parents=True, exist_ok=True)
        with args.fragment_out.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, lineterminator="\n", fieldnames=(
                "component_id", "closed_px", "emitted_px", "centroid_row",
                "centroid_col", "centroid_lon", "centroid_lat",
                "median_distance_to_known_m", "assessment"))
            writer.writeheader()
            writer.writerows(fragments)
        unassigned = int((off & (lab == 0)).sum())
        fragment_emitted = sum(r["emitted_px"] for r in fragments)
        fragment_info = {"file": args.fragment_out.name,
                         "sha256": hashlib.sha256(args.fragment_out.read_bytes()).hexdigest(),
                         "components": len(fragments), "emitted_px": fragment_emitted,
                         "emitted_lost_to_closing_px": unassigned,
                         "reason": "below min-pixels; not an identified fault"}

    records = []
    for cid in keep:
        rows, cols = np.nonzero(lab == cid)
        rec = candidate_geometry(rows, cols)
        rec["candidate_id"] = int(cid)
        # A closing bridges and FILLS pixels that were never predicted. Use the
        # closed footprint for grouping/PCA but only emitted pixels for physical
        # readings and distances. These are distinct counts by design.
        was_emitted = off[rows, cols]
        emitted_rows, emitted_cols = rows[was_emitted], cols[was_emitted]
        if emitted_rows.size == 0:
            raise ValueError(f"component {cid} contains no emitted predictions")
        rec["emitted_pixels"] = int(emitted_rows.size)
        lon, lat = lonlat_of(rec["centroid_row"], rec["centroid_col"])
        rec["centroid_lonlat"] = [round(lon, 4), round(lat, 4)]
        d = dist_to_cat[emitted_rows, emitted_cols]
        rec["distance_to_catalogue_px"] = {
            "median": round(float(np.median(d)), 2),
            "mean": round(float(d.mean()), 2),
            "fraction_within_300m": round(float((d <= metric.RADIUS_PX).mean()), 3),
        }
        rec["diagnostics"] = {}
        for name, (family, direction, desc) in {k: v for k, v in
                                                ((d0[0], d0[1:]) for d0 in DIAGNOSTICS)}.items():
            v = diag[name][emitted_rows, emitted_cols]
            v = v[np.isfinite(v)]
            if v.size == 0:
                rec["diagnostics"][name] = None
                continue
            med = float(np.median(v))
            pct = percentile(regional[name], med)
            fav = (False if direction == "untrusted" else
                   (pct >= 0.9) if direction == "high" else
                   (pct <= 0.1) if direction == "low" else
                   (pct >= 0.9 or pct <= 0.1))
            rec["diagnostics"][name] = {
                "family": family, "description": desc,
                "median_value": round(med, 6), "regional_percentile_median": round(pct, 4),
                "direction": direction, "favourable": bool(fav),
            }
        fams = sorted({rec["diagnostics"][n]["family"]
                       for n in rec["diagnostics"]
                       if rec["diagnostics"][n] and rec["diagnostics"][n]["favourable"]
                       and rec["diagnostics"][n]["family"] in FAMILIES})
        rec["agreement"] = {
            "n_families_of_6": len(fams), "families": fams,
            "rule": "a family counts once when any of its diagnostics is in the "
                    "fault-favourable decile of the regional distribution",
        }
        rec["tilt_depth"] = tilt_depth_bins(diag, emitted_rows, emitted_cols)
        # A cropped catalogue DTI is NOT a fault diagnosis: that crop includes
        # other components and is evaluated on the wrong population. Omit it.
        records.append(rec)

    if fragment_info is not None:
        large_emitted = sum(r["emitted_pixels"] for r in records)
        assert large_emitted + fragment_info["emitted_px"] + fragment_info[
            "emitted_lost_to_closing_px"] == int(off.sum()), (
            "large, small and closing-lost emission counts do not reconcile")
    records.sort(key=lambda r: (-r["pixels"],))
    for i, r in enumerate(records, 1):
        r["rank_by_size"] = i

    classes = {"halo": 0, "near_trace": 0, "isolated": 0}
    for r in records:
        near = r["distance_to_catalogue_px"]["fraction_within_300m"]
        # Distance is NOT evidence of an along-strike extension; avoid that
        # geological label until the trend has been independently verified.
        cls = "halo" if near >= 0.75 else ("near_trace" if near >= 0.10 else "isolated")
        r["class"] = cls
        classes[cls] += 1

    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "gemsdoe_review/tools/geology_dossier.py",
        "submission": pred_path.name,
        "input_sha256": {"submission": raster.sha256_file(pred_path),
                         "training_features": raster.sha256_file(
                             REPO_ROOT / "data" / "training_features.tif"),
                         "labels": raster.sha256_file(REPO_ROOT / "data" / "labels.tif")},
        "counts": {
            "predicted_pixels": int(pred.sum()),
            "predicted_on_catalogue": int((pred & catalogue).sum()),
            "predicted_off_catalogue": int(off.sum()),
            "catalogue_pixels": int(catalogue.sum()),
            "closing_px": int(args.closing),
            "min_pixels": int(args.min_pixels),
            "components": int(n_lab),
            "candidates": int(keep.size),
            "class_counts": classes,
        },
        "regional_sample": {"n_max": args.regional_sample, "seed": 20,
                            "unit": "valid grid pixels, sampled without replacement"},
        "family_rule": "families: " + ", ".join(FAMILIES) +
                       "; untrusted magnetic tilt and nearly constant ratio do "
                       "not vote; no defensible depth bin from supplied bands",
        "fragment_inventory": fragment_info,
        "candidates": records,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1, allow_nan=False) + "\n")
    print(f"[{time.time()-t0:5.1f}s] wrote {args.out} ({len(records)} candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
