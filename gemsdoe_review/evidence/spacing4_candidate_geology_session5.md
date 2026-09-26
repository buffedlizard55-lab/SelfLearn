# Geological reasoning for the session-5 spacing-4 candidate

**Artifact:** `candidate_spacing4-topk03.tif` — sha256
`f807dccf16869422bd17236833dd44082a0bb85d440c142740ee2cf28f2277c0`, 1,764,117 B
(corrected in session 6: this line originally said 1,652,883 B, which is the *shipped*
file's size; `candidate_spacing4_report_session5.json` and the session-6 byte-identical
rebuild both record 1,764,117 B),
155,021 positive pixels (3.00% of the 5,167,373-pixel footprint), **13/13 format gate
PASS** (`evidence/submission_gate_candidate_session5.json`).
**Not submitted, not published, not offered for download.** It lives in the session
scratch directory; this repository carries the reasoning, not the bytes.

**What it is:** the same model as the shipped artifact — `HistGradientBoosting`,
88 channels, 60,988 catalogue positives + 400,000 sampled negatives, 300 iterations,
seed 7, identical hyperparameters — differing **only** in the placement policy:
probability-ordered suppression with a minimum 4-pixel Chebyshev separation
(`budget_nodes`, the same code path the CV used), instead of a dense top-3%.

**Per-component measurements:** `evidence/spacing4_candidate_geology_2026-09-26.json`
and the rendered `.md` (all 943 components ≥200 closed pixels, each with hypothesis,
measured support, counterinterpretation and confidence). Component IDs below are that
file's `candidate_id`.

## 1. What the policy change does to where the mass lands

| | shipped dense (`33cec71f…`) | session-5 spacing-4 (`f807dccf…`) |
|---|---:|---:|
| emitted pixels | 155,021 | 155,021 |
| emitted **on** the supplied catalogue | 23,605 (15.2%) | **4,106 (2.6%)** |
| pixel overlap with the other file | — | 12,828 (Jaccard 0.043) |
| large components (5×5 closing, ≥200 px) | 180 | **943** |
| of those, >300 m from any mapped trace | 1 | **491** |
| components with 0/6 favourable families | 66/180 (37%) | 473/943 (50%) |
| total closed area of large components | 1,568 km² | 6,401 km² |

Two readings, and they point the same way:

* The dense file spends **15% of its budget on pixels the platform's own
  clarification says are not charged** ([staff post, pixel-exact mask](https://community.drivendata.org/t/11516/4))
  and, on held-out geography, earns almost nothing for them — its corridor mass is
  what made it lose to a matched-budget random control in the session-5 CV
  (0.0925 vs 0.1722, dense policy).
* The spaced file spends that budget off-catalogue instead: **491 of its 943 large
  components sit more than 300 m from any mapped trace**, which is the population the
  prize is actually scored against ("newly identified faults" per the
  [rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) and the
  [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).

**That is not evidence the new pixels are faults.** It is a change in *where the
model is willing to spend budget*, measured on a proxy whose truth is the catalogue
itself.

## 2. Where the corroborated flags are

Only 470 of 943 large components have any diagnostic family in its fault-favourable
regional decile, and only 25 have three or more. Those best-corroborated ones are
small (478–1,172 closed px) and fall into **two geographically coherent clusters**,
which is what a real structural population looks like and what a random emission
does not:

* **northern cluster, ~39.16–39.24°N, 118.41–118.55°W** — components 21434, 20871,
  21229;
* **southern cluster, ~38.62–38.70°N, 118.33–118.55°W** — components 24935, 24621,
  24431, 24951, 21101.

Component azimuths across all 943 are more dispersed than the shipped file's
(which is dominated by the 0–30° and 150–180° bins, i.e. the regional
north–south structural grain). Dispersal is not automatically wrong — the Walker
Lane is a zone of oblique strike-slip cross-cutting the Basin-and-Range grain — but
PCA strike is an axis, not a verified trend, and no component is assigned to a named
fault system here.

## 3. Six candidates, with the reasoning behind them

All numbers are medians over the component's **emitted, off-catalogue** pixels,
expressed as regional percentiles of all-band-valid locations on the pinned official
raster. "Favourable decile" is descriptive, not a validated likelihood.

### 20871 — isolated, 776 closed / 109 emitted px, 39.2394°N 118.4913°W
PCA azimuth 165.0°, axes 6.5 × 5.3 km, elongation 1.2:1, median distance to a mapped
trace 21.6 px (2.2 km).
**Measured support (4/6 families):** magnetic horizontal gradient 0.93 and analytic
signal 0.93 (one signal, see below), geodetic second invariant 0.94, shear rate 0.92,
conductivity 0.91, earthquake-intensity band 0.90.
**Reasoning:** the co-location of a magnetic edge, high geodetic strain and a
conductivity anomaly along a north–south axis, 2 km from the nearest mapped trace, is
the classic surface expression of a faulted, fluid-altered corridor in this setting —
and at 2 km it is *outside* the pixel-exact mask, so it would be scored as new fault
if the experts mapped it.
**Counterinterpretation:** the component is small (6.5 × 5.3 km, 1.2:1) and the
magnetic channels are the *same* measurement twice — `mag_asa` ≈ |TMI horizontal
gradient| (r ≈ 1.000 on this grid), so 4 families here are 3 independent ones, and
strain and seismicity are themselves correlated (Spearman ≈ 0.77 on catalogue
positives). A broad volcanic or hydrothermally altered block, or a lithologic
contact, would produce the same four signals.
**Confidence: low.** Needed: 1 m DEM scarp geometry across the axis, mapped-contact
continuity, and whether the strain/seismicity co-location is a point anomaly or a
regional gradient.

### 21434 — isolated, 1,172 closed / 145 emitted px, 39.1646°N 118.4920°W
PCA azimuth 163.7°, axes 8.0 × 5.9 km, elongation 1.4:1, median distance 13.0 px.
**Measured support (3/6):** dilatation rate 0.98, magnetic gradient 0.93, earthquake
intensity 0.90.
**Reasoning:** 8.3 km north–north-west of 20871 on a near-parallel axis. Two
separately emitted components with the same strike and overlapping signal families,
8 km apart, is what a single through-going structure sampled by a sparse emission
looks like — or two independent structures in one corridor.
**Counterinterpretation:** both are small and weakly elongated; the spacing policy
samples a line every ~4 px, so "two components" may be one line broken by the
suppression rule, and the apparent co-linearity may be an artefact of the placement,
not of the geology.
**Confidence: low.** Needed: the same 1 m DEM check, plus a test of whether the two
components join when the emission is densified.

### 24935 — isolated, 246 closed / 35 emitted px, 38.6249°N 118.4130°W
PCA azimuth 58.1°, axes 5.7 × 2.0 km, elongation 2.9:1, median distance 16.2 px.
**Measured support (4/6):** dilatation rate 0.98, earthquake intensity 0.97,
break-in-slope 0.94, conductivity 0.94.
**Reasoning:** the only well-corroborated component in the set whose strike is
oblique (58°) to the regional grain. A break in slope on the detrended 100 m
elevation, high dilatation and a conductivity anomaly on a 2.9:1 axis is a
geomorphically plausible fault scarp or flexure.
**Counterinterpretation:** the slope break is measured on **100 m** detrended
elevation, not the 1 m DEM, so an erosional escarpment, a depositional edge or a
lithologic contact is an equally good explanation; and 35 emitted pixels is a very
small sample for four percentile claims.
**Confidence: low.** Needed: 1 m lidar/topo profile across the 58° axis; without it
this is a lineament hypothesis, not a fault.

### 24431 — near a mapped trace, 808 closed / 103 emitted px, 38.6931°N 118.4362°W
PCA azimuth 100.2°, axes 7.5 × 5.2 km, median distance 9.0 px (900 m).
**Measured support (3/6):** dilatation rate 0.98, TMI extremity 0.96, earthquake
intensity 0.94, conductivity 0.93.
**Reasoning:** at 900 m from a mapped trace on an east–west axis, the most useful
reading is a **correction** — the mapped trace is offset, or a strand between the
mapped traces is unmapped. Corrections are explicitly allowed as new-fault truth
under the organizers' pixel-exact mask.
**Counterinterpretation:** it is inside the magnetically noisy neighbourhood of the
mapped trace; a geophysical halo with no fault is the simpler explanation, and
near-trace pixels earn nothing if the experts' new labels are elsewhere.
**Confidence: low.** Needed: whether the mapped trace's own geometry shows an offset
at this longitude.

### 14713 — near a mapped trace, 10,258 closed / 1,202 emitted px, 39.8131°N 118.5083°W
PCA azimuth 164.0°, axes 30.6 × 14.1 km, elongation 2.2:1, median distance 11.2 px.
**Measured support: 0/6 families.**
**Reasoning:** the largest component in the file. A 30 km north–south body next to
mapped traces is a candidate for a **basin-bounding fault zone** — the structures
that actually matter for geothermal prospectivity.
**Counterinterpretation:** with no diagnostic family in its favourable decile, and a
14 km minor axis, this is a broad volume rather than a trace: a volcanic field, a
sedimentary trough edge, or the summed halo of several nearby mapped faults. Size is
not evidence.
**Confidence: very low.** Needed: which mapped traces bound it, and whether the
interior shows a single through-going scarp.

### 16651 — isolated, 8,146 closed / 1,012 emitted px, 39.6174°N 119.1506°W
PCA azimuth 142.7°, axes 30.4 × 17.8 km, elongation 1.7:1, median distance 13.4 px.
**Measured support: 0/6 families.**
**Reasoning:** the largest *isolated* component in the file — the kind of structure
that would be a genuine discovery if it is a fault, because it is 1.3 km from the
nearest mapped trace and 30 km long.
**Counterinterpretation:** 0/6 families and 1.7:1 elongation. A broad magnetic/gravity
low, an alluvial corridor, or a model artefact from the spacing policy sampling a
diffuse high-probability region would look exactly like this.
**Confidence: very low.** Needed: everything in §3 above; on current evidence this
is a *region worth a look*, not a candidate fault.

## 4. What this dossier cannot do

* **No depth.** The supplied magnetic tilt derivative reaches |angle| ≥ 45° on
  0.00% of this candidate's emitted pixels (`tilt_depth` in the JSON), so no
  tilt-depth contour or depth bin is offered for any component.
* **No independent confirmation.** The six families are not statistically
  independent: strain and seismicity correlate at ≈ 0.77 on catalogue positives, and
  `mag_asa` duplicates |TMI horizontal gradient| at r ≈ 1.000, so two "agreeing"
  signals are frequently one measurement.
* **No expert labels.** The only truth available here is the supplied catalogue, which
  is also the training target; a component 300 m from a mapped trace is a *distance
  class*, not a fault identity.
* **30,467 smaller components (71,349 emitted px) are not individually interpreted.**
  Some could be narrow real faults; "not identified by this screen" is not proof of
  absence.
* **The candidate's own score is unknown.** The session-5 CV number (0.2345 mean fold
  DTI for full88 + spacing4, vs 0.0925 dense) is measured against the catalogue on
  held-out geography; it is not the hidden expert-fault score, and the in-sample
  catalogue DTI of this file (0.3153) is *lower* than the shipped file's (0.4272) —
  which is exactly the train/test inversion that makes the dense policy look good
  locally and the spaced policy better on held-out ground.
