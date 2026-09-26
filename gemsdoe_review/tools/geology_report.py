#!/usr/bin/env python3
"""Render the per-candidate geological dossier (markdown) from the measured JSON.

Machine numbers come from `data/evidence/geology_dossier.json` (produced by
`scripts/geology_dossier.py`). The *readings* below are hand-written and are kept
separate on purpose: each one names the measurement it rests on, states the
structural discordance (candidate strike minus the local mapped trend), and gives
an explicit confidence, so a geologist can audit the reasoning rather than trust
a label.

    python scripts/geology_report.py            # writes data/evidence/geology_dossier.md
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

OUT_MD = REPO_ROOT / "data" / "evidence" / "geology_dossier.md"
OUT_JSON = REPO_ROOT / "data" / "evidence" / "geology_dossier.json"

READINGS: dict[int, str] = {
    21: (
        "**Reading.** The strongest multi-family candidate in the file: 1,963 px over "
        "19.6 km², a 19.0 × 6.8 km body striking N129°E at 39.184°N 118.086°W. It "
        "carries three families at once — magnetics (HGM 0.93, analytic signal 0.93), "
        "strain (second invariant 0.95, shear rate 0.94) and seismicity (density 0.92) "
        "— and it is *conductivity-dark* (0.01, i.e. among the driest 1% of the "
        "footprint). That combination is diagnostic of an **active, unaltered "
        "structure**: the high strain and high earthquake density say it is moving "
        "now, while the absence of a conductivity anomaly says there is no clay cap "
        "or fluid pathway at the surface. Its measured discordance from the "
        "local mapped trend is only 20 degrees - it is not following the mapped "
        "traces, but it is not cutting across them either; at this location the "
        "mapped grain itself runs ESE. So the strike is consistent with either a "
        "splay of the mapped system or a lithological contact, and the three "
        "families cannot separate those. "
        "**Confidence: high that this is a real structural feature, low that it is a fault rather than a contact.** It sits at the southern end of the 1954 Fairview Peak-Dixie "
        "Valley rupture belt, which is why the strain and seismicity agree."
    ),
    47: (
        "**Reading.** 824 px over 8.2 km², 16.6 × 3.7 km striking N58°E at 38.640°N "
        "118.043°W, 2.8 px from the mapped catalogue (54% of it inside 300 m). "
        "Magnetics (HGM 0.90) with dilatation (0.93) and earthquake density (0.92), "
        "and again conductivity-dark (0.09). Its measured discordance from the "
        "local mapped trend is only 2 degrees: this candidate runs ALONG the "
        "mapped grain. The arguments *for* are the strong elongation, the magnetic "
        "edge and the strain agreement; the argument *against* is the proximity to "
        "**new-fault** truth pixel lies within 300 m, and a 15 km body 300 m off the "
        "map is exactly the 'correction to an existing trace' the staff post names as "
        "one of the competition's intended outcomes. **Confidence: moderate, and it "
        "is a bet on the correction population rather than on a discovery.**"
    ),
    102: (
        "**Reading.** One of the file's *isolated* candidates, and therefore one of "
        "the few that could earn credit for a genuinely new structure: 394 px over "
        "3.9 km², 4.9 × 2.7 km striking N81°E at 38.653°N 118.321°W, its nearest "
        "mapped trace 19.5 px (1.95 km) away, only 3.8% of its pixels within 300 m of "
        "the catalogue. Magnetics (HGM 0.90), RTP (0.96, i.e. a strong magnetic high), "
        "dilatation (0.95) and earthquake density (0.96) all agree, and it is close "
        "to seismicity (distance-to-event in the nearest 4%). A magnetic high with "
        "high dilatation next to earthquakes is a candidate **igneous or "
        "hydrothermally altered body**, not obviously a fault: at 1.8:1 it is a blob, "
        "not a lineament. **Confidence: low as a fault; it is listed because it is "
        "isolated and multi-family, which is the population the prize actually "
        "scores.**"
    ),
    107: (
        "**Reading.** 378 px, 6.1 × 3.5 km striking N153°E at 39.182°N 118.051°W — "
        "the same small area as candidate 21, five pixels away, and it repeats that "
        "candidate's signature in miniature: magnetic edge (0.96, the strongest in "
        "the file), strain (second invariant 0.96, shear rate 0.96), seismicity "
        "(0.90) and conductivity-dark (0.02). Two independent groups landing on the "
        "same 10 × 10 km patch with the same four signals is the most defensible "
        "statement in this dossier: **something structural and currently deforming "
        "is there.** Its measured discordance from the local mapped trend is 47 "
        "degrees - it crosses the mapped grain rather than following it, which is "
        "what a transfer or cross-structure looks like. "
        "**Confidence: high that the anomaly is real; the fault-versus-contact "
        "question is unresolved and would need the 1 m DEM or field check.**"
    ),
    131: (
        "**Reading.** The second isolated candidate, and the one with the most "
        "different kind of evidence: 291 px, 11.1 × 3.8 km at 4.7:1 striking N44°E "
        "at 38.654°N 118.554°W, nearest mapped trace 3.2 km away (0.7% within 300 m). "
        "It has *no* magnetic signal (RTP 0.07 — a strong low, and no HGM), but it is "
        "high in dilatation (0.98), conductivity (0.96), earthquake density (0.96) "
        "and close to seismicity (0.95). **A conductive, dilatant, seismically "
        "active, magnetically quiet NNE lineament is the most geothermal-looking "
        "object in this file**: clay alteration and fluid pathways produce exactly "
        "that conductivity signature, and the magnetic quiet is what you get when "
        "hydrothermal alteration destroys magnetite. Its measured discordance "
        "from the local mapped trend is 46 degrees: it cuts across the mapped "
        "grain, which is consistent with a transfer structure and also with an "
        "unrelated lithological boundary. **Confidence: moderate; this is the candidate I "
        "independent of the magnetic field and therefore of the method's main "
        "assumption.**"
    ),
    179: (
        "**Reading.** 218 px, the smallest of the three-family set, 3.0 × 1.3 km at "
        "2.4:1 striking N18°E at 39.140°N 118.298°W, isolated (nothing mapped within "
        "1.77 km). Magnetic edge (0.91), dilatation (0.91), earthquake density (0.94) "
        "and conductivity-dark (0.03). **Short, magnetic, deforming, dry, and "
        "unmapped.** Its measured discordance from the local mapped trend is 52 "
        "degrees, so it does NOT follow the local mapped grain: it is a "
        "cross-cutting orientation rather than an along-strike continuation. "
        "fault system that the map did not carry. The counter-argument is its size: "
        "at 218 px it is at the floor this dossier uses, and a 3 km feature is within "
        "the range of a noise cluster. **Confidence: low-to-moderate as a new fault; "
        "worth naming in a Phase-2 narrative precisely because it is small, "
        "magnetic, on-trend and unmapped.**"
    ),
    2: (
        "**Reading.** The largest candidate in the file by area: 12,021 px over "
        "120 km², 28.0 × 14.7 km at only 1.9:1 (a broad zone, not a line), striking "
        "N82°E at 38.012°N 118.442°W. Its evidence is almost purely *geodetic and "
        "seismic*: second invariant 1.00 (the top of the distribution), shear rate "
        "1.00, dilatation 0.91, earthquake density 0.96, and it is near seismicity "
        "(distance-to-event 0.93). Exactly zero magnetic and zero gravity families. "
        "**A 120 km² zone of the highest strain rate in the region with no "
        "potential-field expression is a diffuse deforming volume, not a fault.** "
        "The correct geological reading is that this is where the geodetic field is "
        "concentrated; its measured discordance from the local mapped trend is "
        "86 degrees, i.e. it is almost exactly perpendicular to the mapped "
        "traces. The emission here is really a *strain anomaly* that a "
        "budget-driven selector promoted to a fault candidate. "
        "needs it, present it as a deformation zone and use the isolated candidates "
        "for the fault claims.**"
    ),
    4: (
        "**Reading.** 5,404 px over 54 km², 37.6 × 8.3 km at 4.5:1, striking N76°E at "
        "38.491°N 118.345°W, 0.9 km from the mapped catalogue. Dilatation 0.97, "
        "earthquake density 0.99 (the highest in the file), near seismicity (0.98) "
        "and moderately high second invariant (0.95); no potential-field family. "
        "**An east–west, 38 km long, almost perfectly seismogenic band with no "
        "magnetic or gravity edge.** Its measured discordance from the local "
        "mapped trend is 86 degrees: it is perpendicular to the mapped grain. "
        "Two readings are possible and the measurement "
        "earthquake catalogue itself (an E–W alignment of events produces exactly "
        "this). The second is more parsimonious, since the same band is high in both "
        "earthquake layers and low in every geophysical one. **Confidence: low as a "
        "fault; high as a description of the seismicity field.**"
    ),
    14: (
        "**Reading.** 2,484 px over 24.8 km², 21.1 × 4.9 km striking N87°E at "
        "38.431°N 118.514°W. Like candidate 2, its support is geodetic and seismic "
        "(dilatation 1.00, earthquake density 1.00, near seismicity 0.95, second "
        "invariant 0.98) plus one magnetic term — TMI in the lowest 7% of the "
        "footprint, a magnetic *low*. **A magnetic low coincident with the highest "
        "dilatation in the region is what a sediment-filled, actively extending "
        "trough looks like**, and that reading is geologically coherent here: it is "
        "the Excelsior Mountains / Huntoon Valley area at the southern end of the "
        "Walker Lane step-over, where extension is accommodated by basins between "
        "ranges. **Confidence: moderate as a structural depression, low as a single "
        "fault trace** — 4.9:1 elongation is lineament-like but the body is 25 km "
        "across its width, which is a basin, not a fault."
    ),
}


def local_mapped_trend(labels: np.ndarray, sigma_smooth: float = 1.0,
                       sigma_tensor: float = 6.0) -> np.ndarray:
    """Dominant orientation of the mapped fault network, in degrees clockwise from
    north, folded to [0, 180). Computed with a structure tensor: the gradient of a
    smoothed binary raster is perpendicular to the trace, so the trace direction is
    the tensor's minor eigenvector."""
    g = ndimage.gaussian_filter(labels.astype(np.float32), sigma_smooth)
    gy, gx = np.gradient(g)
    jxx = ndimage.gaussian_filter(gx * gx, sigma_tensor)
    jyy = ndimage.gaussian_filter(gy * gy, sigma_tensor)
    jxy = ndimage.gaussian_filter(gx * gy, sigma_tensor)
    # major eigenvector of [[jxx, jxy], [jxy, jyy]] points across the trace
    # The major eigenvector of the structure tensor points ACROSS the trace
    # (the direction of steepest change); the trace itself runs 90 degrees from
    # it. The first version of this function forgot the +90 and every
    # discordance in the table was wrong by 90 degrees.
    across = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    trace_dir = (np.degrees(across) + 90.0) % 180.0
    energy = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy ** 2)
    trace_dir[energy < np.percentile(energy, 50)] = np.nan
    return trace_dir


def fnum(x, nd=2):
    if x is None:
        return "n/a"
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--dossier", default=str(OUT_JSON))
    ap.add_argument("--out", default=str(OUT_MD))
    args = ap.parse_args()

    d = json.loads(Path(args.dossier).read_text())
    counts = d["counts"]
    with rasterio.open(REPO_ROOT / "data" / "labels.tif") as s:
        labels = s.read(1)
    trend = local_mapped_trend(labels == 1)

    L: list[str] = []
    A = L.append
    A("# Per-candidate geological dossier")
    A("")
    A(f"Generated {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} from "
      f"`data/evidence/geology_dossier.json` by `scripts/geology_report.py`.")
    A("")
    A(f"**Submission analysed:** `{d['submission']}` — "
      f"{counts['predicted_pixels']:,} predicted pixels, of which "
      f"{counts['predicted_on_catalogue']:,} sit on a mapped fault and "
      f"{counts['predicted_off_catalogue']:,} do not. Grouped with a "
      f"{counts['closing_px']} px closing into {counts['components']:,} components; "
      f"the {counts['candidates']} of them at or above {counts['min_pixels']} px are "
      f"the candidates below. Classes: {counts['class_counts']['halo']} halo, "
      f"{counts['class_counts']['extension']} extension, "
      f"{counts['class_counts']['isolated']} **isolated**.")
    A("")
    A("This document answers `NEXT_STEPS.md` item 9 — the geological reasoning "
      "behind the structures the model flags — and it is written to be auditable. "
      "The tables are rendered from the measured JSON; the paragraphs marked "
      "*Reading* are hand-written, and each one names the measurements it relies on "
      "and the strongest argument against its own conclusion.")
    A("")
    A("## Why the strike column matters")
    A("")
    A("`strike` is the azimuth of each candidate's principal axis, degrees clockwise "
      "from north. `Δ trend` is that strike minus the local orientation of the "
      "**mapped** fault network measured by a structure tensor on the label raster "
      "— so a candidate with a small Δ follows the mapped grain and one with a large "
      "Δ cuts across it. Neither is automatically better: along-strike extensions of "
      "mapped faults are explicitly part of the competition's new-fault population "
      "(`community.drivendata.org/t/11516`, staff post 4), while cross-structures are "
      "what a genuinely new fault looks like. The number is there so the argument "
      "can be made with it rather than without it.")
    A("")
    A("## The candidate set at a glance")
    A("")
    A("| rank | px | km² | strike | Δ trend | elongation | class | families | lon | lat |")
    A("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    rows = sorted(d["candidates"], key=lambda r: (-r["agreement"]["n_families_of_6"],
                                                 -r["pixels"]))
    for r in rows[:40]:
        A(f"| {r['rank_by_size']} | {r['pixels']:,} | {r['area_km2']:.1f} | "
          f"N{r['azimuth_deg_from_north']:.0f}°E | "
          f"{_delta(r, trend)} | {r['elongation']:.1f} | {r['class']} | "
          f"{r['agreement']['n_families_of_6']}/6 | "
          f"{r['centroid_lonlat'][0]:.3f} | {r['centroid_lonlat'][1]:.3f} |")
    A("")
    A(f"({len(rows) - 40:,} further candidates are in the JSON; the table shows the "
      f"{min(40, len(rows))} strongest by family agreement, then size. Family "
      "agreement counts each of magnetic edge, gravity edge, slope break, strain, "
      "conductivity and seismicity once, when any of its diagnostics is in the "
      "fault-favourable decile of the regional distribution.)")
    A("")
    A("## Readings")
    A("")
    by_rank = {r["rank_by_size"]: r for r in d["candidates"]}
    for rank in sorted(READINGS):
        r = by_rank.get(rank)
        if r is None:
            continue
        strong = [f"{k} {v['regional_percentile_median']:.2f}"
                  for k, v in r["diagnostics"].items()
                  if v and (v["regional_percentile_median"] >= 0.9
                            or v["regional_percentile_median"] <= 0.1)]
        A(f"### Candidate {rank} — {r['pixels']:,} px, {r['area_km2']:.1f} km², "
          f"{r['agreement']['n_families_of_6']}/6 families, {r['class']}")
        A("")
        A(f"* `{r['centroid_lonlat'][1]:.4f}°N {_ew(r['centroid_lonlat'][0])}`  ·  "
          f"{r['major_axis_km']:.1f} × {r['minor_axis_km']:.1f} km  ·  "
          f"strike N{r['azimuth_deg_from_north']:.0f}°E  ·  "
          f"elongation {r['elongation']:.1f}:1  ·  "
          f"nearest mapped trace {r['distance_to_catalogue_px']['median']:.1f} px "
          f"({r['distance_to_catalogue_px']['median'] * 100:.0f} m), "
          f"{100 * r['distance_to_catalogue_px']['fraction_within_300m']:.0f}% of "
          f"pixels within 300 m")
        A(f"* extreme diagnostics (regional percentile): "
          f"{', '.join(strong) if strong else 'none in the favourable decile'}")
        A(f"* depth: {r['tilt_depth']['status']} — {r['tilt_depth']['why']}")
        A("")
        A(READINGS[rank])
        A("")
    A("## The pattern the whole set shows")
    A("")
    A("Three things hold across all "
      f"{counts['candidates']} candidates and are worth more than any single "
      "reading above.")
    A("")
    A("1. **The strain and seismicity layers dominate.** Every large candidate is "
      "carried by `geod_2ndinv`, `geod_shearrate`, `geod_dilaterate` or "
      "`ieq_n100a15`; the potential-field families appear mainly in the small, "
      "isolated ones. A budget-driven selector asked to spend 172,974 pixels found "
      "the deforming volume of the region before it found its magnetic edges.")
    A("2. **Conductivity is bimodal, and the dark side is the interesting one.** "
      "Several of the best candidates (21, 47, 107, 179) are in the *driest* 1–9% "
      "of the conductivity surface while others (131) are in the wettest 4%. Those "
      "are two physically different targets — an active dry structure versus an "
      "altered, fluid-bearing one — and a single conductivity threshold would "
      "erase one of them.")
    A("3. **Only the isolated few can score as new faults.** Under the rule verified "
      "this session, mass that hugs a mapped trace is fully penalised unless it "
      "lands within 300 m of a *new*-fault pixel. "
      f"{counts['class_counts']['isolated']} of the {counts['candidates']} candidates "
      f"are isolated; they are candidates 102, 131, 179 and their peers, and they "
      "are the only part of this file that can earn credit for a discovery rather "
      "than for a correction.")
    A("")
    A("## What would falsify these readings")
    A("")
    A("* The mapped-trend field is a structure tensor on a binary raster at 100 m; "
      "where the catalogue is sparse it is noisy, and Δ trend should not be read to "
      "better than about ±15°.")
    A("* No depth estimate is offered. The supplied magnetic vertical derivative "
      "(`tmi_vg`) is ~256× smaller than the horizontal one, so the tilt derivative "
      "it implies never leaves ±3.1° and the ±45° contours the tilt-depth method "
      "needs do not exist — measured, with the numbers, in "
      "`data/evidence/tilt_derivative_audit.json`. A depth claim here would be "
      "invented.")
    A("* Every reading names a fault-versus-lithological-contact ambiguity it cannot "
      "settle. Settling it needs the 1 m DEM (slope-break and scarp geometry), which "
      "this sandbox cannot reach (the USGS 3DEP bucket is egress-blocked).")
    A("")
    A("*None of this is a score.* The population that is scored is not public; the "
      "only local measurements of it are the SGMC proxy in "
      "`data/evidence/masked_proxy_eval_all.json` and the reasoning above.")
    A("")

    Path(args.out).write_text("\n".join(L) + "\n")
    print(f"wrote {args.out} ({len(L)} lines)")
    return 0


def _ew(lon: float) -> str:
    return f"{abs(lon):.4f}\u00b0{'W' if lon < 0 else 'E'}"


def _delta(r: dict, trend: np.ndarray) -> str:
    """Candidate strike minus the local mapped trend at its centroid."""
    rr, cc = r["centroid_row"], r["centroid_col"]
    t = trend[rr, cc]
    if not np.isfinite(t):
        return "n/a"
    dd = abs(r["azimuth_deg_from_north"] - t)
    return f"{min(dd, 180 - dd):.0f}°"


if __name__ == "__main__":
    raise SystemExit(main())
