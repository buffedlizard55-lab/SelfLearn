#!/usr/bin/env python3
"""Render Phase-2-style per-candidate geological narratives.

NEXT_STEPS.md item 9 (6GEMSDOE): Phase 2 pays five times Phase 1 and is graded
by geologists reviewing what we flagged; for each high-confidence lineament we
need the trend relative to Walker Lane / Basin-and-Range kinematics, the
independent signals that agree, the depth estimate status, and a confidence.

This renderer reads the measured per-group dossier produced by
`tools/current_geology_report.py` (which pins the submission SHA-256 and gates
the raster) and composes, for EVERY >=200-closed-px candidate group:

  * the measured geometry (PCA axes, elongation, azimuth) and, only when the
    body is actually elongated (elongation >= 2), its relation to the three
    regional trend families (NW Walker Lane dextral, N Basin-and-Range normal,
    NE accommodation) - labelled interpretation, not identification;
  * the families whose diagnostics fall in the fault-favourable regional
    decile (the dossier's own six-family rule; the untrusted magnetic
    tilt/ratio diagnostics are excluded from voting by the dossier itself);
  * the tilt-depth status exactly as measured (on these bytes it is not
    estimable - the audit found the supplied magnetic tilt angle-dead);
  * a distance class (halo / near_trace / isolated) with the staff masking
    consequence: mass within 300 m of training pixels is not exempt from
    false-positive cost and cannot be claimed as a hidden discovery;
  * a composed geological hypothesis WITH its main counterinterpretation, and
    a measured confidence tier (never higher than "provisional").

Nothing here is a verified fault, a depth estimate, or a score. The narrative
exists so a reviewing geologist can see the reasoning attached to each mask.

    python gemsdoe_review/tools/phase2_narrative.py \
        --dossier gemsdoe_review/evidence/current_shipped_geology_2026-09-26.json \
        --outdir gemsdoe_review/evidence
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

# Regional trend families. Sources for the FRAME (not for any local claim):
#   * GeoDAWN region "associated with the Walker Lane and western Great Basin":
#     https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
#   * Walker Lane as a zone of northwest-trending right-lateral shear:
#     https://pubs.usgs.gov/dds/dds-058/Ch_I.pdf (USGS DDS-58, ch. I)
#   * Basin-and-Range normal faults trending northerly, north-trending basins
#     and ranges: https://pubs.usgs.gov/publication/ofr6711 (USGS OFR 67-11);
#     normal faulting as the extensional response:
#     https://www.usgs.gov/faqs/what-a-fault-and-what-are-different-types
TREND_FAMILIES = [
    ("NW (Walker Lane dextral shear)", 300.0, 345.0,
     "consistent with the northwest-striking, right-lateral shear of the "
     "Walker Lane belt that the GeoDAWN survey area was designed to cover"),
    ("N (Basin-and-Range normal)", 345.0, 25.0,
     "consistent with the northerly-trending high-angle normal faults that "
     "characterise Basin-and-Range extension in this part of Nevada"),
    ("NE (accommodation/cross-grain)", 25.0, 70.0,
     "in the orientation of the northeast-striking accommodation structures "
     "reported along the margins of the Walker Lane"),
]
UNORIENTED = (70.0, 300.0)  # E-W through SW: treat with least commitment


def trend_reading(az: float) -> tuple[str, str]:
    for name, lo, hi, why in TREND_FAMILIES:
        in_band = (lo <= az <= hi) if lo <= hi else (az >= lo or az <= hi)
        if in_band:
            return name, why
    return ("outside the three regional trend families",
            "not aligned with any of the three cited regional trend families; "
            "in this province such an orientation (E-W through SW) is least "
            "specific and should not be promoted on trend alone")


def confidence_of(rec: dict) -> str:
    """Measured confidence tier. 'provisional' is the CEILING by construction."""
    fams = rec["agreement"]["n_families_of_6"]
    elong = rec["elongation"]
    emitted = rec["emitted_pixels"]
    if rec["class"] == "isolated" or fams == 0:
        return "low"
    if fams >= 3 and elong >= 2.0 and emitted >= 1000:
        return "provisional"
    return "low-to-provisional"


def halo_sentence(rec: dict) -> str:
    d = rec["distance_to_catalogue_px"]
    cls = rec["class"]
    if cls == "halo":
        return ("This group lies essentially ON the mapped catalogue "
                f"(median {d['median']:.1f} px): under the staff masking rule "
                "these pixels sit inside the excluded training-label band, so "
                "their score contribution is masked rather than evidence of a "
                "hidden fault.")
    if cls == "near_trace":
        return (f"Median distance to the catalogue is {d['median']:.1f} px "
                f"({d['fraction_within_300m']:.0%} of emitted pixels within "
                "300 m): close enough to a mapped trace that the model may be "
                "thickening or bridging known structure. New-fault truth may "
                "include corrections within 300 m of mapped faults, but this "
                "group cannot be counted as an independent discovery.")
    return (f"Median distance to the catalogue is {d['median']:.1f} px "
            f"({d['fraction_within_300m']:.0%} of emitted pixels within "
            "300 m): the farthest-off population. Isolation raises interest "
            "and, equally, the false-positive risk - isolation alone has no "
            "confirmatory weight.")


def family_sentence(rec: dict) -> str:
    fams = rec["agreement"]["families"]
    n = rec["agreement"]["n_families_of_6"]
    if n == 0:
        return ("No family reaches the fault-favourable regional decile "
                "(0/6; magnetic tilt and its ratio are excluded from voting - "
                "see tilt_derivative_audit.json).")
    fav = []
    for k, dgn in rec["diagnostics"].items():
        if dgn.get("favourable") and dgn.get("family") not in (
                "untrusted_tilt", "untrusted_magnetic_ratio"):
            fav.append(f"{k} ({dgn['direction']}, regional percentile "
                       f"{dgn['regional_percentile_median']:.2f})")
    fav_txt = ("Strongest measured support: " + "; ".join(fav[:4]) + ".") \
        if fav else ""
    return (f"{n}/6 signal families reach the fault-favourable regional "
            f"decile: {', '.join(fams)}. {fav_txt} These families co-vary "
            "(measured strain|seismicity Spearman 0.77 at catalogue pixels - "
            "feature_priorities_audit_2026-09-26.json), so n families is not "
            "n independent confirmations.").replace("  ", " ")


def geometry_sentence(rec: dict) -> str:
    az = rec["azimuth_deg_from_north"]
    geo = (f"Closed group {rec['candidate_id']}: {rec['emitted_pixels']:,} "
           f"emitted px ({rec['area_km2']:.1f} km2), PCA axes "
           f"{rec['major_axis_km']:.1f} x {rec['minor_axis_km']:.1f} km, "
           f"elongation {rec['elongation']:.2f}, centroid "
           f"{rec['centroid_lonlat'][0]:.3f}E {rec['centroid_lonlat'][1]:.3f}N.")
    if rec["elongation"] < 2.0:
        return geo + (" The body is too equant for its principal axis to be "
                      "called a lineation; treat any azimuth reading below as "
                      "weak.")
    name, why = trend_reading(az)
    return geo + (f" Measured principal-axis azimuth {az:.0f}deg - {name}: "
                  f"{why}. This is a kinematic consistency statement, not an "
                  "identification of faulting style.")


def counter_sentence(rec: dict) -> str:
    if rec["major_axis_km"] >= 10.0:
        return ("Counterinterpretation: bodies of this width are more "
                "consistent with a broad structural corridor (damage zone, "
                "basin-fill thickness change, or alteration halo) than with a "
                "single discrete fault trace; the mask may be enclosing a "
                "zone rather than a plane.")
    return ("Counterinterpretation: at 100 m raster resolution a compact "
            "group like this can be produced by a detrended-elevation "
            "curvature artefact, a lithological contact, or local noise; none "
            "of these is excluded by the measured diagnostics.")


def depth_sentence(rec: dict) -> str:
    td = rec["tilt_depth"]
    if td.get("status") == "not estimable from the supplied bands":
        return ("Depth: not estimable from the supplied bands - the provided "
                "magnetic vertical gradient is ~230x smaller than its "
                "horizontal counterpart, so the +/-45 deg tilt-depth contours "
                "do not exist on these bytes "
                "(tilt_derivative_audit.json). No depth is claimed.")
    return f"Depth: {td.get('status')}"


def compose(rec: dict) -> dict:
    return {
        "candidate_id": rec["candidate_id"],
        "rank_by_size": rec["rank_by_size"],
        "class": rec["class"],
        "confidence": confidence_of(rec),
        "n_families_of_6": rec["agreement"]["n_families_of_6"],
        "families": rec["agreement"]["families"],
        "azimuth_deg_from_north": rec["azimuth_deg_from_north"],
        "elongation": rec["elongation"],
        "emitted_pixels": rec["emitted_pixels"],
        "narrative": " ".join([
            geometry_sentence(rec),
            family_sentence(rec),
            halo_sentence(rec),
            depth_sentence(rec),
            counter_sentence(rec),
        ]),
    }


HEADER = """# Phase-2 candidate narratives — shipped file — 2026-09-26

Per-candidate geological reasoning for every >=200-closed-px group the model
flags in the **shipped** submission (SHA-256 `{sha}`, first 12: `{sha12}`),
rendered by `tools/phase2_narrative.py` from the measured dossier
`current_shipped_geology_2026-09-26.json`. The mask is a hypothesis list, not
a fault map.

**Regional frame (cited sources only).** The GeoDAWN survey area covers
ground "associated with the Walker Lane and western Great Basin"
([competition About page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)).
The Walker Lane is documented as a belt of northwest-trending, right-lateral
shear ([USGS DDS-58 ch. I](https://pubs.usgs.gov/dds/dds-058/Ch_I.pdf));
Basin-and-Range extension in Nevada is expressed as northerly-trending
high-angle normal faults forming north-trending basins and ranges
([USGS OFR 67-11](https://pubs.usgs.gov/publication/ofr6711);
[USGS FAQ on normal faults](https://www.usgs.gov/faqs/what-a-fault-and-what-are-different-types)).
These sources justify using NW ~300-345 deg, N ~345-25 deg and NE ~25-70 deg
as *interpretation aids* for measured azimuths. They do not identify any
specific structure.

**What every entry below is:** a measured geometry + measured signal-decile
support + measured distance class + the depth status, composed into a
hypothesis with its counterinterpretation. **What none of them is:** a
verified fault, a depth estimate, or a prediction of hidden score. Tilt-depth
is not estimable on the supplied bands (dead magnetic tilt); where this file
says a group is 'isolated', isolation is a distance heuristic, not a
discovery. Under the staff masking rule, mass within 300 m of the training
labels is not exempt from false-positive cost.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dossier", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()

    d = json.loads(args.dossier.read_text())
    sha = (d.get("input_sha256") or {}).get("submission")
    if not sha:
        raise SystemExit("dossier has no input_sha256.submission - refusing "
                         "to attach narratives to unidentified bytes")
    recs = [compose(c) for c in d["candidates"]]

    fam_hist: dict[int, int] = {}
    for c in d["candidates"]:
        fam_hist[c["agreement"]["n_families_of_6"]] = \
            fam_hist.get(c["agreement"]["n_families_of_6"], 0) + 1

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_json = args.outdir / f"phase2_candidate_narratives_{stamp}.json"
    out_md = args.outdir / f"phase2_candidate_narratives_{stamp}.md"

    payload = {
        "kind": "Phase-2-style per-candidate narratives; hypotheses with "
                "counterinterpretations, composed only from measured fields",
        "dossier": str(args.dossier),
        "submission_sha256": sha,
        "n_candidates": len(recs),
        "n_families_histogram": {str(k): v for k, v in sorted(fam_hist.items())},
        "confidence_counts": {
            k: sum(1 for r in recs if r["confidence"] == k)
            for k in sorted({r["confidence"] for r in recs})},
        "class_counts": {
            k: sum(1 for r in recs if r["class"] == k)
            for k in sorted({r["class"] for r in recs})},
        "regional_frame_sources": [
            "https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/",
            "https://pubs.usgs.gov/dds/dds-058/Ch_I.pdf",
            "https://pubs.usgs.gov/publication/ofr6711",
            "https://www.usgs.gov/faqs/what-a-fault-and-what-are-different-types",
        ],
        "candidates": recs,
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [HEADER.format(sha=sha, sha12=sha[:12])]
    order = sorted(recs, key=lambda r: (-r["emitted_pixels"]))
    n_prov = sum(1 for r in recs if r["confidence"] == "provisional")
    n3 = sum(v for k, v in fam_hist.items() if k >= 3)
    lines.append(
        f"**Measured headline for this file:** {len(order)} candidates; "
        f"agreement histogram {dict(sorted(fam_hist.items()))} (families of 6) "
        f"— only {n3} of {len(order)} reach 3/6 families, and **no candidate "
        f"reaches the 'provisional' tier** (needs >=3 families AND elongation "
        f">= 2 AND >= 1,000 emitted px). The shipped flags are, at group "
        f"level, weakly supported; treat the whole file as a broad anomaly "
        f"surface, not a line list.\n")
    lines.append(f"## {len(order)} candidates, largest first\n")
    lines.append("| # | id | class | conf | fam/6 | az | elong | emitted px |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | ---: |")
    for i, r in enumerate(order, 1):
        lines.append(
            f"| {i} | {r['candidate_id']} | {r['class']} | {r['confidence']} "
            f"| {r['n_families_of_6']} | {r['azimuth_deg_from_north']:.0f} "
            f"| {r['elongation']:.2f} | {r['emitted_pixels']:,} |")
    lines.append("")
    for i, r in enumerate(order, 1):
        lines.append(f"### {i}. candidate {r['candidate_id']} "
                     f"({r['class']}, confidence {r['confidence']})\n")
        lines.append(r["narrative"] + "\n")
    out_md.write_text("\n".join(lines) + "\n")
    print("wrote", out_json)
    print("wrote", out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
