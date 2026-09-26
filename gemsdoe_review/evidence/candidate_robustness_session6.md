# Candidate robustness (session 6, item 6): corrected dossier + label-blind check

Subject: the session-5 local candidate `candidate_spacing4-topk03.tif`
(sha256 `f807dccf…77c0`, 1,764,117 B; rebuilt byte-identically in session 6).
Machine-readable: `spacing4_candidate_geology_gravfix_session6.json` (dossier, gravity fixed)
and `label_blind_corroboration_session6.json` (this analysis). Tools:
`tools/geology_dossier.py`, `tools/label_blind_corroboration.py`.

**Nothing here says a fault exists.** These are screens that say which flags deserve a
geologist's time first. Coordinates are lon/lat (WGS84) of component centroids.

## 1. What the gravity fix changed in the session-5 dossier

The supplied `iso_grav_anom_hg` is the signed E-W derivative dG/dx, not the gradient
magnitude (`grav_hg_identity_session6.json`). The session-5 dossier had read it as
"high = density contact", so its gravity-edge votes were really "gravity rising to the east".

| | session 5 (hg) | session 6 (`iso_grav_anom_slope`) |
|---|---|---|
| components with a gravity-edge vote | 104 | 69 |
| components whose family set changed | – | 63 of 943 (only gravity changed) |
| 0 / 1 / 2 / 3 / 4 families | 473 / 319 / 126 / 23 / 2 | 497 / 302 / 123 / 19 / 2 |
| components with ≥ 3 families | 25 | **21** |

The session-5 statement "25 have three or more families" is superseded by **21**.

## 2. Label-blind check: does the flag survive a model that never saw local labels?

The full-data model saw every catalogue pixel. Near mapped traces, its probability partly
reflects that it memorised the labels. For each component I read the probability of the
**outer model of the component's own quadrant**. That model was trained with the quadrant,
a 300 m Euclidean buffer and every fault system touching the quadrant removed (session-6
nested run, `maps88/outer_q*.npy`). The reported number is the median within-quadrant
percentile of that label-blind probability over the component's emitted pixels. A random
location gets 0.5. The thresholds (≥ 0.90 corroborated, < 0.50 label-dependent) were fixed
in the tool before it was run.

| class | n | median percentile | corroborated | label-dependent | mean top-3% fraction (random 0.03) |
|---|---|---|---|---|---|
| all | 943 | 0.648 | 118 | **293** | 0.064 |
| isolated (> 300 m from catalogue) | 491 | 0.669 | 66 | 147 | 0.067 |
| near_trace | 451 | 0.631 | 52 | 146 | 0.061 |

* On average the flags carry some signal that works in new ground (median 0.65 > 0.5, top-3%
  fraction about twice random). Still, **31% (293) of flagged components are label-dependent**:
  the label-blind model ranks them below its own median.
* **Multi-family geophysical support is negatively related to label-blind rank.** The
  Spearman correlation between family count and percentile is −0.20. The multi-family flags
  sit in the high-strain, high-seismicity central Walker Lane belt, where the catalogue is
  dense. In that belt, "high strain" does not separate one pixel from another within the
  quadrant, and the full model's local confidence comes from nearby labels.

### Session-5's named multi-family candidates do not pass

| id | lon, lat | families (corrected) | label-blind percentile | class |
|---|---|---|---|---|
| 20871 | −118.491, 39.239 | conductivity, magnetic_edge, seismicity, strain | 0.22 | label-dependent |
| 21434 | −118.492, 39.165 | magnetic_edge, seismicity, strain | 0.13 | label-dependent |
| 21229 | −118.412, 39.204 | conductivity, seismicity, strain | 0.40 | label-dependent |
| 24935 | −118.413, 38.625 | conductivity, seismicity, slope_break, strain | 0.20 | label-dependent |
| 24621 | −118.552, 38.656 | conductivity, seismicity, strain | 0.53 | intermediate |
| 24431 | −118.436, 38.693 | conductivity, seismicity, strain | 0.46 | label-dependent |
| 24951 | −118.331, 38.625 | magnetic_edge, seismicity, strain | 0.33 | label-dependent |
| 21101 | −118.127, 39.222 | magnetic_edge, seismicity, strain | 0.66 | intermediate |

Revised reading of these candidates: they look like fault ground because they sit inside a
belt that is already densely faulted. That is the kind of place where a new fault is
*plausible*. But the model's specific placement there is not reproduced once local labels
are withheld, so their exact position is weakly supported. Treat them as "belt-context"
flags, not as targeted discoveries. Of the 21 components with ≥ 3 families, none is
label-blind corroborated. The best of them is 28401 at 0.83 (below).

## 3. Label-blind-corroborated isolated flags: hand reasoning (top by family count)

All of these are more than 300 m from the catalogue (median distance 1.2–3.6 km) and have
a label-blind percentile ≥ 0.90. Percentiles in brackets are the dossier's regional
percentiles of the component median. The components are small, 28–149 emitted pixels
(spacing-4 grid), so per-component statistics are noisy.

1. **18811** (−119.658, 39.464), 2.8 × 2.2 km, not elongated. Strain and seismicity (2nd
   invariant 0.96, shear rate 0.97, ieq 0.93, deq 0.89), total curvature 0.88, magnetic
   gradient 0.74, gravity gradient 0.29. The label-blind top-3% fraction is 0.72, the highest
   here. Reasoning: high deformation plus a topographic curvature break, with no density
   contact. That fits a young, low-throw structure, or one within a single rock package. Its
   equant shape gives no strike, so a field check should look for scarps in any orientation.
2. **19113** (−119.627, 39.427), 4.5 × 1.9 km, azimuth 144°, elongation 2.4, 3.6 km from the
   catalogue. It lies about 5 km from 18811 with the same strain/seismicity signature (0.93 to
   0.94) and magnetic gradient 0.80. Its NW-SE strike is the common Walker Lane dextral
   trend. Reasoning: the most "new-structure-like" flag in this list (farthest from the
   catalogue, elongated, strike consistent with regional shear). Together with 18811 it is
   worth looking at as one possible zone.
3. **20724** (−118.991, 39.263), 5.5 × 3.1 km, azimuth 132°. Strongest magnetic evidence in
   the list (magnetic gradient 0.94, RTP 0.85, TDR 0.68) plus shear rate 0.93. Low gravity
   gradient (0.18), negative dilatation (0.09). Reasoning: a magnetic contact on a NW trend
   in a shear-dominated strain field. It could be a strike-slip boundary juxtaposing
   magnetised rock, or simply a lithologic contact. The magnetic signal is necessary but not
   sufficient.
4. **22742** (−118.112, 38.994), 7.7 × 3.7 km, azimuth 26°. The only flag here with a true
   density contact (corrected gravity gradient 0.93, ASA 0.85), plus dilatation 0.91 and
   slope-of-slope 0.80. Reasoning: NNE strike, a gravity step and extensional strain together
   fit a range-front normal fault bounding a basin. This is the textbook Basin-and-Range
   signature, and this vote only exists because of the gravity fix (session 5 read the
   wrong band). **Top recommendation for inspection.**
5. **27618** (−118.074, 38.066), 5.1 × 2.4 km, azimuth 108°. Seismicity (deq 0.99, ieq 0.91)
   and strain (0.95) at low elevation (detrended elevation 0.06). Reasoning: WNW strike in
   the southern Walker Lane, where WNW-ENE structures are common. It is buried or basin-floor
   (low relief), so any trace would be subtle. Its label-blind top-3% fraction is only 0.15,
   so corroboration is moderate.
6. **20767** (−118.026, 39.247), 8.4 × 5.9 km, the largest (149 emitted px). Strain only
   (0.96/0.93), conductivity very low (0.03). Its label-blind percentile is 0.98.
   Reasoning: the model is confident without the labels, but the component is broad and
   equant, and the evidence is regional strain alone, which is a belt signal. It is more
   likely a bundle of spaced points on a strain high than a single structure.
7. **28401** (−118.382, 37.965), 4.0 × 1.7 km, azimuth 134°. The only ≥ 3-family flag with
   meaningful label-blind support (0.83). Gravity gradient 0.80, ASA 0.91, magnetic gradient
   0.89, strain 0.99, curvature 0.85. Reasoning: multiple independent contacts (density and
   magnetic) and topographic breaks on a NW strike in a very high strain field. This is the
   best "geophysics and transferable model agree" case. It is ranked below 1–4 only because
   it misses the 0.90 threshold.

Flags that are label-blind corroborated but have seismicity only, far from strain highs
(4703 at −118.393, 40.464 and 11449 at −118.681, 40.122, with strain percentiles
0.27–0.38), carry model confidence without strain or potential-field support. They rest
on the earthquake density features alone: lower priority.

## 4. Caveats (flagged, not smoothed)

* The label-blind model uses the same features and the same catalogue population elsewhere,
  so it shares the full model's biases. Agreement is necessary, not sufficient.
* Quadrant boundaries: the percentile is within the component's quadrant. Components
  straddling a boundary are scored with each pixel's own quadrant model.
* Components are matched between candidates by nearest centroid (section 5). That is
  crude, because a component can split or merge.
* No public fault database was consulted. No named fault is claimed for any candidate.

## 5. Cross-check on the 105-channel candidate (adopted configuration)

Session 6 adopted the 105-channel stack (F1). I rebuilt the candidate with it
(`candidate_spacing4-topk03-ch105.tif`, sha256 `5ff242cd…277b`, 1,763,914 B, 155,021 px,
gate 13/13 plus the entry's `validate_submission.py`, exit 0). Its dossier and label-blind
check were re-run against the **105-channel** outer models (`maps105/outer_q*.npy`):
`spacing4_candidate_ch105_geology_session6.json`, `label_blind_corroboration_ch105_session6.json`.

* Same ground: 90.2% of the 105-channel nodes lie within 3 px (the metric kernel radius) of
  an 88-channel node, and 96.6% within 4 px. Pixel Jaccard is only 0.118, which is a lattice
  phase shift, not a different map.
* Same pattern: 918 components; 99 label-blind corroborated, 287 label-dependent; family
  count vs label-blind rank Spearman −0.30 (−0.20 before).

| 88-ch flag | 88-ch percentile | nearest 105-ch component (distance) | 105-ch percentile | reading |
|---|---|---|---|---|
| 19113 | 0.97 | 19278 (1.2 km), same families | 0.97 | **most robust flag** |
| 18811 | 0.99 | 18616 (3.2 km) | 0.94 | robust (same zone as 19113) |
| 27618 | 0.91 | 27476 (2.3 km), same families | 0.93 | robust |
| 20767 | 0.98 | 20414 (2.5 km) | 0.98 | robust, but a strain-only belt signal |
| 22742 | 0.96 | 22697 (2.9 km) | 0.78 | component geometry changed. The gravity-edge and strain signature persists 3.9 km away in 23009 (0.91, `gravity_edge`+`strain`). The area is robust; the outline is not. |
| 20724 | 0.97 | 20370 (5.4 km) | 0.84 | weakened |
| 28401 | 0.83 | 27886 (3.5 km) | 0.29 | **not robust**, withdrawn from the shortlist |
| 20871 / 21434 / 24935 (session-5 named) | 0.22 / 0.13 / 0.20 | 21138 / 21555 / 24792 | 0.15 / 0.21 / 0.19 | label-dependent in both |

**Revised inspection order:** 19113 + 18811 (one zone, −119.63…−119.66, 39.43…39.46)
→ the 22742 / 23009 gravity-edge area (−118.11…−118.13, 38.96…38.99) → 27618 → 20767.
The session-5 central Walker Lane clusters remain belt-context flags.
