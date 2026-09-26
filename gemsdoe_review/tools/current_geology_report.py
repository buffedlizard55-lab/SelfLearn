#!/usr/bin/env python3
"""Render *measured, provisional* reasoning for EVERY flagged large component.

Unlike the archived geology_report.py, this NEVER joins handwritten paragraphs
by rank: ranks are not stable between submission rasters. There are no invented
formation names, depths, causal diagnoses, or expert confirmations. Each reading
states a fault hypothesis, measured support, a non-fault explanation and the
specific observation that would arbitrate it. The six diagnostic families are
not assumed statistically independent or fault-specific.

    python gemsdoe_review/tools/current_geology_report.py \\
      --dossier gemsdoe_review/evidence/current_shipped_geology_2026-09-26.json \\
      --out gemsdoe_review/evidence/current_shipped_geology_2026-09-26.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

FAMILY_WORDS = {
    "magnetic_edge": ("mag_hgm", "magnetic gradient/contact"),
    "gravity_edge": ("grav_hgm", "gravity-gradient/density boundary"),
    "slope_break": ("slope_of_slope", "slope break on the 100 m detrended elevation"),
    "strain": ("geod_2ndinv", "regional geodetic strain"),
    "conductivity": ("cond_surf", "conductivity anomaly"),
    "seismicity": ("ieq_n100a15", "earthquake-related intensity/density band"),
}


def diagnostic_text(record: dict) -> list[str]:
    """Name the ACTUAL supporting band (including whether low means favourable)."""
    out = []
    for fam in record["agreement"]["families"]:
        primary, words = FAMILY_WORDS[fam]
        support = [(name, v) for name, v in record["diagnostics"].items()
                   if v and v["family"] == fam and v["favourable"]]
        if not support:
            raise ValueError(f"{fam}: listed as support but no favourable diagnostic")
        name, d = next((nv for nv in support if nv[0] == primary), support[0])
        if name == "deq_n100a15":
            words = "short distance to earthquakes (not the density band)"
        elif name != primary:
            words = d["description"]
        side = "low" if d["direction"] == "low" else "high"
        out.append(f"{words} ({name}, {side} {d['regional_percentile_median']:.2f} "
                   "regional percentile of the component median)")
    return out


def assessment(record: dict) -> tuple[str, str, str]:
    """Hypothesis, counter-hypothesis, confidence; NONE is a verified fault."""
    dist = record["distance_to_catalogue_px"]
    c = record["class"]
    if c == "isolated":
        setting = ("A lineament spatially separate from the supplied mapped trace "
                   "could be an unmapped fault if the anomaly tracks a break in "
                   "geologic structure.")
        alternative = ("A lithological contact or drainage-aligned surface feature "
                       "could be equally isolated; distance from a map is not proof of a new fault.")
    elif c == "near_trace":
        setting = ("A mapped-trace extension, a nearby splay, or a corrected trace "
                   "position is possible; distance alone does NOT distinguish "
                   "them. Such a correction can be new-fault truth under the "
                   "organizers' pixel-exact known-fault mask.")
        alternative = ("Prediction near a catalogued trace could instead be "
                       "its geophysical halo with no new fault at all; nearby "
                       "off-catalogue pixels still pay false-positive cost.")
    else:
        setting = ("This hugs a known trace and might flag a location correction "
                   "or an adjacent splay, but no distinct new structure is established.")
        alternative = ("It may only rediscover the mapped fault's surrounding "
                       "anomaly. The mask excludes the exact mapped pixels, "
                       "not this surrounding area.")
    line = record["elongation"] >= 3.0 and record["minor_axis_km"] <= 2.0
    if not line:
        alternative += (" Its PCA footprint is broad or weakly elongated "
                        f"({record['elongation']:.1f}:1; "
                        f"minor axis {record['minor_axis_km']:.1f} km), "
                        "not a thin fault trace.")
    # Elevated values are from several related geophysical layers; at most a
    # cautious moderate rating for an isolated narrow feature with >=3 families.
    n = record["agreement"]["n_families_of_6"]
    confidence = ("provisional moderate as a target for expert checking"
                  if c == "isolated" and line and n >= 3
                  else "low as a fault identification")
    if n == 0:
        confidence = "very low (no diagnostic family in its favourable regional decile)"
    if dist["fraction_within_300m"] >= 0.75:
        confidence += "; mapped-trace halo dominates"
    return setting, alternative, confidence


def render(d: dict) -> str:
    if not d.get("input_sha256", {}).get("submission"):
        raise ValueError("dossier lacks a submission SHA-256; refusing rank-based join")
    rows = d["candidates"]
    count = d["counts"]
    fragments = d.get("fragment_inventory")
    if fragments and fragments["components"] != count["components"] - len(rows):
        raise ValueError("small-component inventory does not reconcile with dossier")
    if len(rows) != count["candidates"] or len({r["candidate_id"] for r in rows}) != len(rows):
        raise ValueError("candidate count or IDs inconsistent")
    if {r["rank_by_size"] for r in rows} != set(range(1, len(rows) + 1)):
        raise ValueError("candidate ranks are not a bijection")
    small_note = (f"The remaining {count['components'] - len(rows):,} smaller components "
                  "have not been geologically interpreted and must not be called "
                  "discovered faults.")
    if fragments:
        small_note += (f" All are accounted for in the "
                       f"[fragment inventory]({fragments['file']}) "
                       f"({fragments['emitted_px']:,} emitted px, each assessed "
                       "'not an identified fault by this screen'). A further "
                       f"{fragments['emitted_lost_to_closing_px']:,} off-catalogue "
                       "emitted px were not retained by closing and were not "
                       "assigned to a component (the grid boundary can cause this).")
    lines = [
        "# Geological hypotheses for the current model's flagged components",
        "",
        f"**Raster:** `{d['submission']}`; SHA-256 "
        f"`{d['input_sha256']['submission']}`. This is a pixel prediction, "
        "**not an expert-verified fault map or a leaderboard result**.",
        f"**Method:** 5×5-pixel morphological closing of "
        f"{count['predicted_off_catalogue']:,} off-catalogue positive pixels "
        f"produced {count['components']:,} components. The {len(rows)} at "
        f"≥{count['min_pixels']} closed pixels are reviewed below, **all "
        f"{len(rows)}** (not just the top ten). {small_note}",
        f"Class is a **distance heuristic**, not a geological label: "
        f"{count['class_counts']['isolated']} isolated, "
        f"{count['class_counts']['near_trace']} near a mapped trace, "
        f"{count['class_counts']['halo']} mapped-trace halos. The closed component "
        "defines groups/PCA and can contain non-predicted bridging pixels; band "
        "summaries and mapped-trace distances use **emitted, off-catalogue pixels** only.",
        "",
        "Signals are medians over emitted pixels expressed as regional percentiles "
        "of all-band-valid locations on the pinned 100 m feature raster "
        "([official band descriptions](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features)); "
        "90th/10th-percentile thresholds are "
        "descriptive, not validated likelihoods. Magnetic gradients and gravity "
        "gradients may be lithological contacts; slope breaks may be erosional; "
        "strain and earthquake layers may describe broad zones; conductivity can "
        "reflect lithology as well as fluids. The supplied magnetic tilt is not "
        "calibrated to derive depth and is excluded from agreement. None of the "
        "six families is asserted to be statistically independent of the others.",
        "",
        "The [official metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) "
        "uses a 300 m kernel, while [DrivenData staff](https://community.drivendata.org/t/11516/4) "
        "clarified that the known-fault mask is **pixel-exact**, not buffered: "
        "a correction may be within 300 m of a known trace, but a halo with no "
        "new fault is penalized. [Staff also declined to disclose test-fault "
        "sources, types, or coverage](https://community.drivendata.org/t/11527/7). "
        "Do not use this page to assert those unknowns.",
        "",
        "The [official study context](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/#about-the-data) "
        "mentions the Walker Lane and western Great Basin, but NO individual "
        "component is assigned to a specific fault system or regime from PCA "
        "orientation alone. PCA strike is an axis, not a verified fault trend. "
        "Original 1 m DEM/field observations and a mapped system-level geologist "
        "review are required to choose between each hypothesis and its counterexample. "
        "**No depth estimates are offered.**",
        "",
        "## Assessments (every ≥200 px component)",
        "",
    ]
    for r in sorted(rows, key=lambda item: item["rank_by_size"]):
        h, alt, conf = assessment(r)
        evidence = diagnostic_text(r)
        support = (", ".join(evidence) if evidence else
                   "No diagnostic family in its fault-favourable regional decile")
        distance = r["distance_to_catalogue_px"]
        lon, lat = r["centroid_lonlat"]
        lines.extend([
            f"### S-{r['rank_by_size']:03d} · component {r['candidate_id']} "
            f"({r['class']}; {r['pixels']:,} closed / "
            f"{r['emitted_pixels']:,} emitted px)",
            f"Centroid {lat:.4f}°N, {abs(lon):.4f}°W; "
            f"PCA axis azimuth {r['azimuth_deg_from_north']:.1f}° clockwise from north, "
            f"elongation {r['elongation']:.1f}:1, "
            f"axes {r['major_axis_km']:.1f} × {r['minor_axis_km']:.1f} km. "
            f"Median distance to mapped trace {distance['median'] * 100:.0f} m; "
            f"{100 * distance['fraction_within_300m']:.1f}% within 300 m.",
            f"**Measured support:** {support} "
            f"({r['agreement']['n_families_of_6']}/6 diagnostic families.)",
            f"**Fault hypothesis:** {h}",
            f"**Counterinterpretation:** {alt}",
            f"**Assessment:** {conf}. Seek 1 m scarp geometry, mapped contact "
            "continuity and expert cross-section/field check before calling "
            "this a fault; depth unestimated.",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dossier", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    d = json.loads(args.dossier.read_text())
    if d.get("fragment_inventory"):
        inv = d["fragment_inventory"]
        file = args.dossier.parent / inv["file"]
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != inv["sha256"]:
            raise SystemExit(f"fragment inventory absent or hash mismatch: {file}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(d))
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
