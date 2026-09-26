# Per-candidate geological dossier

Generated 2026-09-26T00:47:55Z from `data/evidence/geology_dossier.json` by `scripts/geology_report.py`.

**Submission analysed:** `ens12.tif` — 172,974 predicted pixels, of which 6,455 sit on a mapped fault and 166,519 do not. Grouped with a 5 px closing into 6,769 components; the 193 of them at or above 200 px are the candidates below. Classes: 3 halo, 123 extension, 67 **isolated**.

This document answers `NEXT_STEPS.md` item 9 — the geological reasoning behind the structures the model flags — and it is written to be auditable. The tables are rendered from the measured JSON; the paragraphs marked *Reading* are hand-written, and each one names the measurements it relies on and the strongest argument against its own conclusion.

## Why the strike column matters

`strike` is the azimuth of each candidate's principal axis, degrees clockwise from north. `Δ trend` is that strike minus the local orientation of the **mapped** fault network measured by a structure tensor on the label raster — so a candidate with a small Δ follows the mapped grain and one with a large Δ cuts across it. Neither is automatically better: along-strike extensions of mapped faults are explicitly part of the competition's new-fault population (`community.drivendata.org/t/11516`, staff post 4), while cross-structures are what a genuinely new fault looks like. The number is there so the argument can be made with it rather than without it.

## The candidate set at a glance

| rank | px | km² | strike | Δ trend | elongation | class | families | lon | lat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | 1,963 | 19.6 | N128°E | 20° | 2.8 | extension | 3/6 | -118.086 | 39.184 |
| 47 | 824 | 8.2 | N58°E | 2° | 4.5 | extension | 3/6 | -118.043 | 38.640 |
| 102 | 394 | 3.9 | N81°E | 23° | 1.8 | isolated | 3/6 | -118.320 | 38.653 |
| 107 | 378 | 3.8 | N153°E | 47° | 1.7 | extension | 3/6 | -118.051 | 39.182 |
| 131 | 291 | 2.9 | N44°E | 46° | 3.0 | isolated | 3/6 | -118.554 | 38.651 |
| 179 | 218 | 2.2 | N18°E | 52° | 2.4 | isolated | 3/6 | -118.297 | 39.140 |
| 2 | 12,021 | 120.2 | N82°E | 86° | 1.9 | extension | 2/6 | -118.442 | 38.012 |
| 4 | 5,404 | 54.0 | N76°E | 86° | 4.5 | extension | 2/6 | -118.345 | 38.491 |
| 14 | 2,484 | 24.8 | N87°E | 5° | 4.3 | extension | 2/6 | -118.513 | 38.431 |
| 17 | 2,276 | 22.8 | N148°E | 72° | 2.6 | extension | 2/6 | -118.376 | 39.279 |
| 35 | 1,181 | 11.8 | N51°E | 2° | 3.0 | extension | 2/6 | -118.411 | 38.823 |
| 36 | 1,097 | 11.0 | N156°E | 30° | 3.4 | extension | 2/6 | -118.191 | 39.234 |
| 37 | 1,073 | 10.7 | N148°E | 5° | 1.3 | extension | 2/6 | -116.770 | 40.075 |
| 42 | 971 | 9.7 | N95°E | 22° | 1.3 | isolated | 2/6 | -118.257 | 39.058 |
| 48 | 804 | 8.0 | N39°E | 22° | 4.7 | extension | 2/6 | -118.212 | 38.765 |
| 50 | 734 | 7.3 | N34°E | 60° | 2.4 | extension | 2/6 | -118.223 | 39.115 |
| 51 | 730 | 7.3 | N120°E | 9° | 3.4 | extension | 2/6 | -118.019 | 38.421 |
| 53 | 726 | 7.3 | N158°E | 72° | 2.0 | isolated | 2/6 | -118.481 | 39.324 |
| 55 | 709 | 7.1 | N29°E | 9° | 2.1 | extension | 2/6 | -118.013 | 38.290 |
| 63 | 644 | 6.4 | N12°E | 29° | 1.7 | extension | 2/6 | -118.123 | 38.599 |
| 66 | 606 | 6.1 | N78°E | 24° | 2.4 | extension | 2/6 | -118.258 | 38.670 |
| 67 | 594 | 5.9 | N72°E | 29° | 2.8 | extension | 2/6 | -117.944 | 38.520 |
| 68 | 580 | 5.8 | N53°E | 0° | 2.5 | extension | 2/6 | -117.808 | 38.488 |
| 71 | 561 | 5.6 | N71°E | 19° | 1.2 | isolated | 2/6 | -118.686 | 40.278 |
| 80 | 498 | 5.0 | N16°E | 40° | 5.4 | extension | 2/6 | -118.372 | 38.718 |
| 82 | 488 | 4.9 | N174°E | 54° | 3.5 | extension | 2/6 | -118.027 | 37.732 |
| 84 | 475 | 4.8 | N83°E | 7° | 2.7 | isolated | 2/6 | -118.623 | 40.237 |
| 89 | 434 | 4.3 | N106°E | 55° | 3.7 | extension | 2/6 | -118.596 | 40.149 |
| 97 | 399 | 4.0 | N140°E | 4° | 6.2 | extension | 2/6 | -118.080 | 40.646 |
| 103 | 391 | 3.9 | N7°E | 82° | 4.7 | extension | 2/6 | -119.313 | 40.491 |
| 115 | 349 | 3.5 | N41°E | 6° | 1.8 | isolated | 2/6 | -118.126 | 38.724 |
| 117 | 347 | 3.5 | N151°E | 36° | 4.2 | isolated | 2/6 | -118.119 | 38.982 |
| 128 | 305 | 3.0 | N36°E | 25° | 4.4 | extension | 2/6 | -116.862 | 40.704 |
| 135 | 281 | 2.8 | N165°E | 59° | 3.4 | isolated | 2/6 | -118.502 | 39.186 |
| 148 | 259 | 2.6 | N24°E | 70° | 2.6 | extension | 2/6 | -118.394 | 39.093 |
| 153 | 253 | 2.5 | N158°E | 41° | 3.0 | extension | 2/6 | -116.168 | 40.126 |
| 157 | 244 | 2.4 | N167°E | 62° | 3.1 | extension | 2/6 | -118.256 | 40.561 |
| 158 | 244 | 2.4 | N3°E | 72° | 4.7 | extension | 2/6 | -118.248 | 40.404 |
| 162 | 239 | 2.4 | N1°E | 33° | 2.9 | isolated | 2/6 | -116.160 | 40.074 |
| 175 | 225 | 2.2 | N34°E | 22° | 2.5 | halo | 2/6 | -118.089 | 38.629 |

(153 further candidates are in the JSON; the table shows the 40 strongest by family agreement, then size. Family agreement counts each of magnetic edge, gravity edge, slope break, strain, conductivity and seismicity once, when any of its diagnostics is in the fault-favourable decile of the regional distribution.)

## Readings

### Candidate 2 — 12,021 px, 120.2 km², 2/6 families, extension

* `38.0117°N 118.4422°W`  ·  28.0 × 14.7 km  ·  strike N82°E  ·  elongation 1.9:1  ·  nearest mapped trace 5.0 px (500 m), 35% of pixels within 300 m
* extreme diagnostics (regional percentile): geod_2ndinv 1.00, geod_shearrate 1.00, geod_dilaterate 0.91, ieq_n100a15 0.96, deq_n100a15 0.93
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** The largest candidate in the file by area: 12,021 px over 120 km², 28.0 × 14.7 km at only 1.9:1 (a broad zone, not a line), striking N82°E at 38.012°N 118.442°W. Its evidence is almost purely *geodetic and seismic*: second invariant 1.00 (the top of the distribution), shear rate 1.00, dilatation 0.91, earthquake density 0.96, and it is near seismicity (distance-to-event 0.93). Exactly zero magnetic and zero gravity families. **A 120 km² zone of the highest strain rate in the region with no potential-field expression is a diffuse deforming volume, not a fault.** The correct geological reading is that this is where the geodetic field is concentrated; its measured discordance from the local mapped trend is 86 degrees, i.e. it is almost exactly perpendicular to the mapped traces. The emission here is really a *strain anomaly* that a budget-driven selector promoted to a fault candidate. needs it, present it as a deformation zone and use the isolated candidates for the fault claims.**

### Candidate 4 — 5,404 px, 54.0 km², 2/6 families, extension

* `38.4914°N 118.3450°W`  ·  37.6 × 8.3 km  ·  strike N76°E  ·  elongation 4.5:1  ·  nearest mapped trace 8.9 px (894 m), 21% of pixels within 300 m
* extreme diagnostics (regional percentile): geod_2ndinv 0.95, geod_dilaterate 0.97, ieq_n100a15 0.99, deq_n100a15 0.98
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** 5,404 px over 54 km², 37.6 × 8.3 km at 4.5:1, striking N76°E at 38.491°N 118.345°W, 0.9 km from the mapped catalogue. Dilatation 0.97, earthquake density 0.99 (the highest in the file), near seismicity (0.98) and moderately high second invariant (0.95); no potential-field family. **An east–west, 38 km long, almost perfectly seismogenic band with no magnetic or gravity edge.** Its measured discordance from the local mapped trend is 86 degrees: it is perpendicular to the mapped grain. Two readings are possible and the measurement earthquake catalogue itself (an E–W alignment of events produces exactly this). The second is more parsimonious, since the same band is high in both earthquake layers and low in every geophysical one. **Confidence: low as a fault; high as a description of the seismicity field.**

### Candidate 14 — 2,484 px, 24.8 km², 2/6 families, extension

* `38.4308°N 118.5135°W`  ·  21.1 × 4.9 km  ·  strike N87°E  ·  elongation 4.3:1  ·  nearest mapped trace 17.2 px (1720 m), 13% of pixels within 300 m
* extreme diagnostics (regional percentile): tmi 0.07, geod_2ndinv 0.98, geod_dilaterate 1.00, ieq_n100a15 1.00, deq_n100a15 0.95
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** 2,484 px over 24.8 km², 21.1 × 4.9 km striking N87°E at 38.431°N 118.514°W. Like candidate 2, its support is geodetic and seismic (dilatation 1.00, earthquake density 1.00, near seismicity 0.95, second invariant 0.98) plus one magnetic term — TMI in the lowest 7% of the footprint, a magnetic *low*. **A magnetic low coincident with the highest dilatation in the region is what a sediment-filled, actively extending trough looks like**, and that reading is geologically coherent here: it is the Excelsior Mountains / Huntoon Valley area at the southern end of the Walker Lane step-over, where extension is accommodated by basins between ranges. **Confidence: moderate as a structural depression, low as a single fault trace** — 4.9:1 elongation is lineament-like but the body is 25 km across its width, which is a basin, not a fault.

### Candidate 21 — 1,963 px, 19.6 km², 3/6 families, extension

* `39.1844°N 118.0861°W`  ·  19.0 × 6.8 km  ·  strike N128°E  ·  elongation 2.8:1  ·  nearest mapped trace 11.1 px (1105 m), 12% of pixels within 300 m
* extreme diagnostics (regional percentile): mag_hgm 0.93, mag_asa 0.93, geod_2ndinv 0.95, geod_shearrate 0.94, cond_surf 0.01, ieq_n100a15 0.92
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** The strongest multi-family candidate in the file: 1,963 px over 19.6 km², a 19.0 × 6.8 km body striking N129°E at 39.184°N 118.086°W. It carries three families at once — magnetics (HGM 0.93, analytic signal 0.93), strain (second invariant 0.95, shear rate 0.94) and seismicity (density 0.92) — and it is *conductivity-dark* (0.01, i.e. among the driest 1% of the footprint). That combination is diagnostic of an **active, unaltered structure**: the high strain and high earthquake density say it is moving now, while the absence of a conductivity anomaly says there is no clay cap or fluid pathway at the surface. Its measured discordance from the local mapped trend is only 20 degrees - it is not following the mapped traces, but it is not cutting across them either; at this location the mapped grain itself runs ESE. So the strike is consistent with either a splay of the mapped system or a lithological contact, and the three families cannot separate those. **Confidence: high that this is a real structural feature, low that it is a fault rather than a contact.** It sits at the southern end of the 1954 Fairview Peak-Dixie Valley rupture belt, which is why the strain and seismicity agree.

### Candidate 47 — 824 px, 8.2 km², 3/6 families, extension

* `38.6396°N 118.0433°W`  ·  16.6 × 3.7 km  ·  strike N58°E  ·  elongation 4.5:1  ·  nearest mapped trace 2.8 px (283 m), 54% of pixels within 300 m
* extreme diagnostics (regional percentile): mag_hgm 0.90, mag_asa 0.90, geod_dilaterate 0.93, cond_surf 0.09, ieq_n100a15 0.92
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** 824 px over 8.2 km², 16.6 × 3.7 km striking N58°E at 38.640°N 118.043°W, 2.8 px from the mapped catalogue (54% of it inside 300 m). Magnetics (HGM 0.90) with dilatation (0.93) and earthquake density (0.92), and again conductivity-dark (0.09). Its measured discordance from the local mapped trend is only 2 degrees: this candidate runs ALONG the mapped grain. The arguments *for* are the strong elongation, the magnetic edge and the strain agreement; the argument *against* is the proximity to **new-fault** truth pixel lies within 300 m, and a 15 km body 300 m off the map is exactly the 'correction to an existing trace' the staff post names as one of the competition's intended outcomes. **Confidence: moderate, and it is a bet on the correction population rather than on a discovery.**

### Candidate 102 — 394 px, 3.9 km², 3/6 families, isolated

* `38.6530°N 118.3205°W`  ·  4.9 × 2.7 km  ·  strike N81°E  ·  elongation 1.8:1  ·  nearest mapped trace 19.5 px (1951 m), 4% of pixels within 300 m
* extreme diagnostics (regional percentile): mag_hgm 0.90, mag_asa 0.90, rtp 0.96, geod_dilaterate 0.95, ieq_n100a15 0.96, deq_n100a15 0.96
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** One of the file's *isolated* candidates, and therefore one of the few that could earn credit for a genuinely new structure: 394 px over 3.9 km², 4.9 × 2.7 km striking N81°E at 38.653°N 118.321°W, its nearest mapped trace 19.5 px (1.95 km) away, only 3.8% of its pixels within 300 m of the catalogue. Magnetics (HGM 0.90), RTP (0.96, i.e. a strong magnetic high), dilatation (0.95) and earthquake density (0.96) all agree, and it is close to seismicity (distance-to-event in the nearest 4%). A magnetic high with high dilatation next to earthquakes is a candidate **igneous or hydrothermally altered body**, not obviously a fault: at 1.8:1 it is a blob, not a lineament. **Confidence: low as a fault; it is listed because it is isolated and multi-family, which is the population the prize actually scores.**

### Candidate 107 — 378 px, 3.8 km², 3/6 families, extension

* `39.1820°N 118.0513°W`  ·  6.1 × 3.5 km  ·  strike N153°E  ·  elongation 1.7:1  ·  nearest mapped trace 5.7 px (566 m), 31% of pixels within 300 m
* extreme diagnostics (regional percentile): mag_hgm 0.96, mag_asa 0.96, geod_2ndinv 0.96, geod_shearrate 0.96, cond_surf 0.02, ieq_n100a15 0.90
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** 378 px, 6.1 × 3.5 km striking N153°E at 39.182°N 118.051°W — the same small area as candidate 21, five pixels away, and it repeats that candidate's signature in miniature: magnetic edge (0.96, the strongest in the file), strain (second invariant 0.96, shear rate 0.96), seismicity (0.90) and conductivity-dark (0.02). Two independent groups landing on the same 10 × 10 km patch with the same four signals is the most defensible statement in this dossier: **something structural and currently deforming is there.** Its measured discordance from the local mapped trend is 47 degrees - it crosses the mapped grain rather than following it, which is what a transfer or cross-structure looks like. **Confidence: high that the anomaly is real; the fault-versus-contact question is unresolved and would need the 1 m DEM or field check.**

### Candidate 131 — 291 px, 2.9 km², 3/6 families, isolated

* `38.6511°N 118.5537°W`  ·  11.1 × 3.8 km  ·  strike N44°E  ·  elongation 3.0:1  ·  nearest mapped trace 31.9 px (3189 m), 1% of pixels within 300 m
* extreme diagnostics (regional percentile): rtp 0.07, geod_dilaterate 0.98, cond_surf 0.96, ieq_n100a15 0.96, deq_n100a15 0.95
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** The second isolated candidate, and the one with the most different kind of evidence: 291 px, 11.1 × 3.8 km at 4.7:1 striking N44°E at 38.654°N 118.554°W, nearest mapped trace 3.2 km away (0.7% within 300 m). It has *no* magnetic signal (RTP 0.07 — a strong low, and no HGM), but it is high in dilatation (0.98), conductivity (0.96), earthquake density (0.96) and close to seismicity (0.95). **A conductive, dilatant, seismically active, magnetically quiet NNE lineament is the most geothermal-looking object in this file**: clay alteration and fluid pathways produce exactly that conductivity signature, and the magnetic quiet is what you get when hydrothermal alteration destroys magnetite. Its measured discordance from the local mapped trend is 46 degrees: it cuts across the mapped grain, which is consistent with a transfer structure and also with an unrelated lithological boundary. **Confidence: moderate; this is the candidate I independent of the magnetic field and therefore of the method's main assumption.**

### Candidate 179 — 218 px, 2.2 km², 3/6 families, isolated

* `39.1399°N 118.2971°W`  ·  3.0 × 1.3 km  ·  strike N18°E  ·  elongation 2.4:1  ·  nearest mapped trace 17.7 px (1772 m), 0% of pixels within 300 m
* extreme diagnostics (regional percentile): mag_hgm 0.91, mag_asa 0.91, geod_dilaterate 0.91, cond_surf 0.03, ieq_n100a15 0.94
* depth: not estimable from the supplied bands — the supplied magnetic tilt derivative reaches |TDR| >= 45 deg in 2.21e-05 of pixels (|TDR| p99 = 3.077 deg), so the +45/-45 contours the tilt-depth method needs are absent (see data/evidence/tilt_derivative_audit.json)

**Reading.** 218 px, the smallest of the three-family set, 3.0 × 1.3 km at 2.4:1 striking N18°E at 39.140°N 118.298°W, isolated (nothing mapped within 1.77 km). Magnetic edge (0.91), dilatation (0.91), earthquake density (0.94) and conductivity-dark (0.03). **Short, magnetic, deforming, dry, and unmapped.** Its measured discordance from the local mapped trend is 52 degrees, so it does NOT follow the local mapped grain: it is a cross-cutting orientation rather than an along-strike continuation. fault system that the map did not carry. The counter-argument is its size: at 218 px it is at the floor this dossier uses, and a 3 km feature is within the range of a noise cluster. **Confidence: low-to-moderate as a new fault; worth naming in a Phase-2 narrative precisely because it is small, magnetic, on-trend and unmapped.**

## The pattern the whole set shows

Three things hold across all 193 candidates and are worth more than any single reading above.

1. **The strain and seismicity layers dominate.** Every large candidate is carried by `geod_2ndinv`, `geod_shearrate`, `geod_dilaterate` or `ieq_n100a15`; the potential-field families appear mainly in the small, isolated ones. A budget-driven selector asked to spend 172,974 pixels found the deforming volume of the region before it found its magnetic edges.
2. **Conductivity is bimodal, and the dark side is the interesting one.** Several of the best candidates (21, 47, 107, 179) are in the *driest* 1–9% of the conductivity surface while others (131) are in the wettest 4%. Those are two physically different targets — an active dry structure versus an altered, fluid-bearing one — and a single conductivity threshold would erase one of them.
3. **Only the isolated few can score as new faults.** Under the rule verified this session, mass that hugs a mapped trace is fully penalised unless it lands within 300 m of a *new*-fault pixel. 67 of the 193 candidates are isolated; they are candidates 102, 131, 179 and their peers, and they are the only part of this file that can earn credit for a discovery rather than for a correction.

## What would falsify these readings

* The mapped-trend field is a structure tensor on a binary raster at 100 m; where the catalogue is sparse it is noisy, and Δ trend should not be read to better than about ±15°.
* No depth estimate is offered. The supplied magnetic vertical derivative (`tmi_vg`) is ~256× smaller than the horizontal one, so the tilt derivative it implies never leaves ±3.1° and the ±45° contours the tilt-depth method needs do not exist — measured, with the numbers, in `data/evidence/tilt_derivative_audit.json`. A depth claim here would be invented.
* Every reading names a fault-versus-lithological-contact ambiguity it cannot settle. Settling it needs the 1 m DEM (slope-break and scarp geometry), which this sandbox cannot reach (the USGS 3DEP bucket is egress-blocked).

*None of this is a score.* The population that is scored is not public; the only local measurements of it are the SGMC proxy in `data/evidence/masked_proxy_eval_all.json` and the reasoning above.

