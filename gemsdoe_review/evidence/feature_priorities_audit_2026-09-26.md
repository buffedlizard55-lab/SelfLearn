# Feature-priorities audit — 2026-09-26 (session 2)

Source: `feature_priorities_audit_2026-09-26.json`, produced by
`tools/feature_priorities_audit.py` from the official bytes
(`training_features.tif`, sha256 `4371c82e…`, pin match **true**) at entry
commit `e2fe3f41c6f5…`. Positives are the 60,988 catalogue fault pixels; the
control is a 60,000-pixel far background **more than 1 km from any catalogue
pixel** (seed 7), so none of the numbers below is a near-halo artefact.
AUC = Mann–Whitney separation of positives vs that far background; `sep` is
the larger of AUC and 1−AUC, i.e. separation in either direction.

**Every number here is a catalogue-proxy statement about MAPPED faults. None
of it predicts the hidden target (faults missing from the catalogue), and
nothing here changes the shipped 88-channel stack.**

## 1. Horizontal gradient / tilt derivative (priority 1)

| Channel | Angle range (abs p50 / p99) | share > 45° | AUC vs far bg |
| --- | --- | ---: | ---: |
| `mag_tilt` (raw, shipped) | 0.244° / 3.077° | 2.2e-5 | 0.4999 |
| `tdr_tmi_s1.5` (shipped smoothed) | 40.41° / 84.72° | 0.440 | 0.4998 |
| `tdr_tmi_s3.0` (shipped smoothed) | 40.34° / 84.77° | 0.439 | 0.4987 |
| `grav_tilt` (raw, shipped) | 38.13° / 88.84° | 0.422 | 0.4843 |
| `mag_asa` | — | — | 0.5351 |
| `grav_asa` | — | — | 0.5350 |

- **Reproduction:** the raw magnetic tilt numbers are *identical* to the
  previous session's audit (`mag_tilt_abs_p99_deg` 3.077, share ≥45°
  2.2068e-5, `mag_asa` vs `|tmi_hg|` r = 1.000000) — the audit reproduces on
  the fresh clone byte-for-byte.
- **New measurement:** the shipped **smoothed** tilts `tdr_tmi_s1.5/s3.0` are
  *not* angle-dead (median 40°) — smoothing `tmi` before the horizontal
  gradient rescues the angle range that the raw `atan2(tmi_vg, |tmi_hg|)`
  loses (median |tmi_vg|/|tmi_hg| ≈ 0.0043 vs 0.78 for the gravity pair).
  But their absolute values carry **no catalogue separation at all**
  (AUC 0.4998 / 0.4987). Angle range and fault information are different
  properties; on the mapped population both magnetic tilt variants are ~0.50.
  The gravity tilt is angle-active and slightly *anti*-separated
  (0.4843, polarity −).
- `mag_asa` remains a numerical duplicate of `|tmi_hg|` (r = 1.000000);
  `grav_asa` is genuinely distinct from `|iso_grav_anom_hg|` (r = 0.8407).
- Consistent with the previous session's constructed Fourier-|k| TDR test
  (separation −0.0296 on mapped faults): no measurement in either session
  shows any magnetic-tilt variant separating mapped faults.

## 2. Curvature and breaks in slope on the DEM (priority 2)

| Channel (shipped unless marked) | AUC vs far bg | polarity |
| --- | ---: | --- |
| `slope_of_slope_s3.0` | **0.5979** | + |
| `slope_of_slope_s1.5` | 0.5892 | + |
| `slope_of_slope` (raw) | 0.5776 | + |
| `slope_computed` | 0.5737 | + |
| `det_elev_slope` (official band) | 0.5661 | + |
| **CANDIDATE** `slope_break_abs_s1_s6` | 0.5641 | + |
| `curv_total_abs_laplacian` | 0.5558 | + |
| **CANDIDATE** `slope_break_rel_s1_s6` | 0.5135 | + |

- The brief's "breaks in slope" priority **is implemented** (`slope_of_slope`
  and its two smoothed scales), and the coarse scale (s3.0) is the strongest
  single measured channel of this family on the catalogue proxy.
- **New measurement — two candidate two-scale slope-break channels** of the
  classic scarp form |G₁(slope) − G₆(slope)| (absolute and relative). Result:
  **no improvement**. The absolute variant is AUC 0.5641 (below the shipped
  s3.0 channel) and strongly redundant with it (Spearman ≈ 0.70 against every
  shipped break channel); the relative variant is decorrelated (ρ ≈ −0.09…0)
  but at AUC 0.5135 it is indistinguishable from noise on mapped faults.
  **Negative result — do not add these channels** on this evidence.
  Caveat: this is the mapped-catalogue population; a channel that is dead
  here can still be live on the hidden target, but there is no measurement
  anywhere in either session that supports the addition.

## 3. Cross-referencing strain rate, conductivity, earthquake density (priority 3)

| Family | band | AUC vs far bg | separation (either tail) | polarity |
| --- | --- | ---: | ---: | --- |
| strain | `geod_2ndinv` | 0.5838 | 0.5838 | + |
| strain | `geod_shearrate` | 0.5806 | 0.5806 | + |
| strain | `geod_dilaterate` | 0.5326 | 0.5326 | + |
| seismicity | `ieq_n100a15` (density) | 0.5831 | 0.5831 | + |
| seismicity | `deq_n100a15` (distance) | 0.4396 | 0.5604 | − (closer at faults) |
| conductivity | `cond_surf` | 0.4794 | 0.5206 | **−** (lower at faults) |
| conductivity | `depth_to_base_surf` | 0.5135 | 0.5135 | + (≈ noise) |

- Each family is weakly informative on the catalogue proxy; **the families
  are not independent of each other**: at catalogue pixels, strain
  (`geod_2ndinv`) and earthquake density (`ieq_n100a15`) have **Spearman
  ρ = 0.77**; strain|conductivity −0.22; conductivity|seismicity −0.14.
- Consequence for the geological narrative: "magnetics + gravity + strain +
  seismicity + conductivity all agree" is **not** five independent
  confirmations. Strain and seismicity largely co-vary (they share the
  tectonic-setting signal), and conductivity is, on this proxy, slightly
  *lower* at fault pixels. Cross-reference claims in Phase-2 text should cite
  at most: potential-field edges, one strain/seismicity block, and
  conductivity only with its measured negative sign.

## Method notes and limits

- Distance control: positives are all 60,988 catalogue pixels (finite in the
  compared channels, per-channel n reported in the JSON); background is
  > 1 km from any catalogue pixel, so these AUCs measure *independent*
  signal, not the 300 m halo the model could also exploit.
- The 300–1000 m halo medians are recorded per channel in the JSON and were
  never pooled into the background.
- Spearman ranks are ordinal (ties by order) on n ≥ 58k samples; the
  ρ = 0.77 strain|seismicity result is far too large for this to matter.
- Everything is measured on `training_features.tif` sha256 `4371c82e…`
  (pin-verified); a hash change invalidates these numbers
  (entry rule: re-check band-identity conclusions whenever the rasters are
  re-fetched).
