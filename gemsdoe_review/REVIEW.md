# GEMSDOE score-quality and entry review — 2026-09-26

**Entry under review:** [`buffedlizard55-lab/6GEMSDOE`](https://github.com/buffedlizard55-lab/6GEMSDOE),
with the [one designated published site](https://buffedlizard55-lab.github.io/6GEMSDOE/).
This is a review in `SelfLearn`, **not an edit to the canonical entry**, a second
registration, an upload, or a leaderboard score. We began with that entry's
`NEXT_STEPS.md` (P0 account/eligibility/allowance; P1 target quality, terrain and
geology; P2 tests), as requested. GitHub repository ownership does **not** identify
the DrivenData registration. Where that distinction is material, it remains a
blocker, not an assumption.

## Decision first: do not promote the local candidates

The only available new-fault *proxy* is a rasterized [USGS SGMC fault catalogue](https://doi.org/10.5066/F7WH2N65),
not the expert-selected GeoDAWN labels. SGMC code 2 means no **training** fault
within 300 m, **not** a verified hidden discovery. Its code-2 target deliberately
misses [new-fault corrections near mapped traces, which DrivenData staff allow](https://community.drivendata.org/t/11516/4).
[Staff explicitly withhold the hidden test sources, fault types and coverage](https://community.drivendata.org/t/11527/7).
Repeated use of SGMC here makes it unsuitable as a fresh, independent test.

| Experiment, mask and geography | Shipped | Alternative | No-skill blanket | Result |
| --- | ---: | ---: | ---: | --- |
| Shipped-emission width study, **east audit blocks**, SGMC code 2 | 0.03526 | 6-px dilation **0.07578** | **0.08235** | The predeclared gain over shipped survived, but the post-readout no-skill gate **failed**. |
| Post-selection **full footprint**, SGMC code 2 | **0.03480** | 86-feature/5% top-k: **0.04539**; same +3-px dilation: **0.05723** | **0.05919** | Both scratch masks remain unsubmitted; the larger still loses to blanket on this proxy. |

The first row evaluates a fixed full-catalogue model with held-out **postprocessing**
selection, not a separately held-out model fit. The second is a repeatedly inspected,
post-selection, full-fit diagnostic. Their scores and fold-restricted CV below use
**different scored geography, models and emission budgets**; do not subtract them to
claim a numerical generalization gap or predict a public score. The positive result
of widening some masks is **not** enough to recommend an upload, especially when
blanket coverage does as well or better. Evidence: `evidence/emission_spatial_holdout_2026-09-26.json`,
`evidence/local_candidate_proxy_comparison_2026-09-26.json`.

The two local files are in `/tmp/gems_entry/` only (not Git or the site):

| Scratch file | SHA-256 | Positive pixels | Gate |
| --- | --- | ---: | --- |
| `gems6_experiment_drop2_topk05.tif` | `cf62c32b686ee536393cafecc0d4beda65e8fb0c3ef6a752422746eb2915d5d2` | 258,369 | 13/13 PASS |
| `gems6_experiment_drop2_topk05_w3.tif` | `1f551a93c6764acfe75bead7fdf9d1432c251e5dd4edde2b9fefc97c672d8cda` | 678,009 | 13/13 PASS |

Passing the format gate says **nothing** about geological credibility or hidden score.

## Pass 1 — implementation and controlled measurements

### Features and placement

Audited the shipped 88-feature construction against the three priorities:

- Magnetic/gravity horizontal gradients, analytic-signal amplitude and tilt,
  including matched-scale derivatives, are present. `mag_asa` is almost a duplicate
  of supplied `tmi_hg` (measured r≈1.000000). Provided `tmi_vg` is about 256× smaller
  than `tmi_hg`; the derived magnetic tilt's 99th-percentile absolute angle is
  ~3.1°, so it cannot support reliable ±45° **depth** contours. Gravity tilt is
  numerically active. This does **not** prove the raw magnetic field lacks useful
  structure or that a replacement gradient improves hidden-fault prediction.
  `evidence/tilt_derivative_audit.json` records the measurements.
- Detrended **100 m** elevation curvature (total, profile, **plan**, Gaussian),
  slope and slope-of-slope are implemented. They are not the omitted 1 m DEM;
  scarps, erosion and contacts cannot be separated by curvature alone.
- Raw geodetic shear/dilatation/second invariant, conductivity and earthquake
  features plus explicit interaction products are present. They can be correlated
  or broad, not six independent fault confirmations.

`tools/feature_ablation_cv.py` compared identical sampled catalogue positives/
negatives, fit settings and **four buffered spatial folds**, with a 3-px Euclidean
train exclusion and scored held-out **interiors**. `full88`, `drop_2` (remove
`mag_asa`, `mag_tilt`) and `drop_4` (also remove two smoothed magnetic tilts) share
those rows. Pooled [300 m distance-weighted Tversky](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric)
on SGMC code 2:

| Policy on each test interior | full88 | drop_2 | Interpretation |
| --- | ---: | ---: | --- |
| top 3%, undilated | 0.05895 | **0.06016** | Small exploratory proxy gain. |
| top 5%, undilated | 0.06904 | **0.07067** | 5% helps this proxy; it emits more mass. |
| top 3%, +3 px disk | 0.06845 | **0.06936** | Dilation changes the budget greatly. |
| top 5%, +3 px disk | **0.07072** | 0.07046 | Drop-two **does not** win here. |

`drop_4` generally trailed `drop_2`. Four vertical strips share geology and the
proxy was already examined; **neither statistical independence nor a hidden-score
gain is established**. A blanket-coverage control and a fresh withheld geological
reference are essential before promoting any variant. The old full-feature catalogue
CV `0.1698` is a **different target** from this table, never an owned leaderboard
score. Evidence: `evidence/feature_ablation_cv_2026-09-26.json`,
`evidence/local_candidate_drop2_topk05{,_w3}_2026-09-26.json`.

**Metric-aware 4–5 px placement:** on a *truly faulted* one-pixel-wide line,
regularly spacing predictions every 4–5 pixels loses weighted TP at the skipped
pixels (kernel radius 3 px). But hardening every predicted probability to 1 or
expanding every line is **not universally optimal** when some pixels are false.
A counterexample in `tests/test_review_regressions.py` keeps a true pixel at 1 and
raises a remote false-positive pixel from 0.01 to 1: TP is unchanged while FP and
therefore the denominator rise. The guide's “fractional confidence always gives
score away” is an overgeneralization of a valid **uniform-scaling** identity, not
of binarization under uncertain locations.

### Per-candidate geology tied to exact raster bytes

`tools/geology_dossier.py` and `tools/current_geology_report.py` now produce
hash-identified, cautious *hypotheses with counterinterpretations*, not field
identifications. The dossier confirms the official input pins and format gate,
corrects the plan-curvature field and a reversed north/south PCA azimuth, samples
finite valid regional pixels, and measures signals **only on emitted** off-catalogue
pixels (morphological closing can add bridging pixels). Magnetic tilt and its
nearly constant ratio cannot vote as evidence. There is **no** made-up depth bin,
local catalogue-crop “fault score,” or rank-joined paragraph from another raster.

| Raster | Large components (5×5 closing; ≥200 closed px) | Distance-only triage | Key caution |
| --- | ---: | --- | --- |
| **Shipped**, SHA `33cec71f…` | **180** of 2,589 groups | 92 mapped-trace halos, 87 near trace, **1 isolated** | 66/180 have no family in the favourable regional decile. Even the one isolated group (S-172; 207 closed / 143 emitted px) has 0/6 families and is **not** a discovery. |
| **Unsubmitted scratch**, SHA `1f551a93…` | **343** of 957 groups | 15 halos, 274 near trace, **54 isolated** | 166/343 have 0/6 families; several isolated groups are broad. Quantity does not verify fault identity. |

Class is only fraction of emitted pixels within 300 m of training traces, **not** an
expert fault type or proof of an along-strike extension. PCA footprints are often
broad volumes, not thin lines. One large shipped near-trace body has ~29 × 9 km PCA
axes and elevated regional strain/seismicity, which also fits a diffuse anomaly.
No parcel of this 100 m raster is independently validated against the original
1 m DEM or geologist field mapping. All **180** shipped ≥200-px groups and **343**
scratch ≥200-px groups are individually listed with measured support, geological
alternatives, low/provisional confidence and checks needed in:

- `evidence/current_shipped_geology_2026-09-26.{json,md}`
- `evidence/local_candidate_w3_geology_2026-09-26.{json,md}`

The **2,409** smaller shipped components (**26,040 emitted px**) are separately
inventoried by component ID, centroid, size and distance in
`evidence/current_shipped_geology_fragments_2026-09-26.csv`; 93 more emitted
pixels are not retained by closing. Thus ~20% of off-catalogue emitted mass is
**not** given individual geological interpretation. Some sub-200-px fragments
could be narrow real faults, so “not identified by this screen” is **not** proof
of fault absence. The scratch raster's 614 smaller groups (41,755 px, plus 508
unassigned) have an analogous inventory. Do not call them discovered faults.
The prior `evidence/geology_dossier.md` has been
**withdrawn**: it applied to `ens12` (172,974 emitted pixels), used rank-attached
handwritten descriptions, had the plan/azimuth mistakes and made unsupported
alteration and activity claims. The raw historical JSON is only an explicitly
flagged audit trail; `tools/geology_report.py` now refuses unsafe rank-based output.

## Pass 2 — bug and reproducibility review

**Real canonical CV bug, patch proposed rather than silently changing results.**
`src/gems/cv.py` does *four-neighbour/Manhattan* 3-px dilation, although the
[metric kernel is Euclidean](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric).
It can admit `(2,2)` corner-neighbours at ~283 m to training when a held-out block
is scored. One canonical test has `assert ... or True` and another checks
separation using the same faulty `_dilate`. On the **full 3,730×3,292 grid**, an
independent Euclidean-distance oracle measured **zero** buffer misses for the
historical 4×4/4-fold **and** 6×6/6-fold *vertical-stripe* assignments, but **32**
for a 5×5/3-fold layout and **100** for a 6×6/4-fold layout (all folds pooled).
Thus the bug is real for general block assignments, **not evidence that the
existing stripe-based score tables leaked**. `evidence/cv_geometry_audit_2026-09-26.json`
records every fold. The oracle failed on the offending unmodified test layouts,
then passed against a **separate patched source copy**. The 46 canonical tests
also passed on that copy. See `patches/cv_euclidean_buffer.patch`; this is a
forward-looking fix, not a retrospective score revision. The canonical repository
is still unpatched.

**Metric and format:** the official formula uses `α=0.2`, `β=0.8`, a triangular
300 m/3-px kernel and a max over predictions for each ground-truth pixel. Eight
hand-derived soft-probability offsets, max-not-sum, no border wrapping, 4–5-px
spacing and the hardening counterexample passed the independent tests. The
SGMC evaluator's fast metric agreed on TP/FP/FN and DTI with the canonical
implementation on a soft-prediction toy grid after matching its documented
`ε=10⁻⁷` convention (the official page does not specify ε). All **21** review
regressions passed on a separately patched CV copy; the original CV correctly
fails only the two non-stripe geometry cases. On the unmodified canonical snapshot,
its **46 tests passed** when run from the correct entry root. The shipped GeoTIFF SHA-256 is
`33cec71ff00b3f32d0d59c81c156f3f1488ffef46baa4b6499094e24ea1875ab`:
**155,021** positives, **5,167,373** finite scored pixels, **0** in-footprint NaNs,
**13/13** canonical format checks. A separate deliberately poisoned NaN *inside*
the footprint failed the **hard** gate and returned status 1 even while its finite
`[0,1]` range check passed. No invalid file was published.

**Reference text/site:** a read-only fetch of the entry's `EXECUTIVE_SUMMARY.md`,
`SUBMISSION_GUIDE.md`, `LIMITATIONS.md`, `index.html` and `research.html`, plus the
pinned rasters/evidence, was checked by `tools/check_entry_docs.py --online`.
After removing its always-true board-score condition and repairing its broken
GitHub inventory API field, **48/50 checks passed**. Two *real* failures remain in
the canonical entry: `LIMITATIONS.md` has no [pixel-exact known-fault masking rule](https://community.drivendata.org/t/11516/4),
and the canonical entry has no per-candidate geology document. Passing its other
checks establishes specific hash/count/prose tokens, **not** all geological or
statistical claims. Additional incorrect or overconfident statements and exact
proposed language are in `patches/PROPOSED_ENTRY_CHANGES.md`: hidden score “will be
lower,” unconditional binarization/width claims, unqualified magnetic tilt,
“weaker than U-Net” without matched tests, and the guide opening with an upload
instruction **before** account checks. The 88-channel float32 feature stack is
4,322,264,320 bytes, not ~2.25 GB. The entry's first-party data bridge is **already
in `6GEMSDOE/data/bridge/`**; an older `NEXT_STEPS.md` instruction to move it is
obsolete. No entry text or site was changed here.

**Cross-site consistency warning:** the live [5GEMSDOE reference site](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)
currently suggests uploading a *different* `candidate_s5_catalogue_hedge.tif` and
advertises a “maximum-compatibility” zero-outside-footprint fallback. The live
[GEMSDOE4 site](https://buffedlizard55-lab.github.io/GEMSDOE4/docs/index.html)
offers yet another browser-built mask. Neither is this entry's content-addressed
file, and the official template plus canonical gate require NaN outside the scored
footprint. Their rendered recommendations conflict with the designated
[6GEMSDOE site's](https://buffedlizard55-lab.github.io/6GEMSDOE/) one-file framing;
treat those as historical alternatives, **not** upload instructions or evidence
of a distinct DrivenData registration. No browser-generated raster was re-gated
in this review.

## Pass 3 — rules, identity and go/no-go re-check

**GitHub account, not DrivenData identity:** GitHub REST confirms
`5GEMSDOE`, `GEMSDOE4`, and `6GEMSDOE` are non-fork repositories owned by
`buffedlizard55-lab`. The API found **11** GEMS-named repositories with GitHub Pages
and the [designated site is built](https://buffedlizard55-lab.github.io/6GEMSDOE/).
That is confusing and may complicate recordkeeping, but **no rule says eleven
sites prove multiple contest registrations**, and it is *not* itself an Appendix
A.12 disqualification. Do not count another entrant's public score as ours.

**Actual standing remains unknown.** The [public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
viewed today showed e.g. top `0.3049`, fifth `0.2589`, and other accounts around
`0.16`; those scores are **other participants'** and the ranks may move.
`0.1698` is catalogue CV; the SGMC values above are local proxies with different
labels. Neither predicts this owner's rank or whether a specific file can contend.
No signed-in submission history or verified identity has been obtained.

The [official rules §§1.3, 3.2, 3.4–3.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
require competitor eligibility; **disclosure of the extent and use of generative
AI in the narrative if applicable** (outside the word count); up to **three**
automated scores per **participating entity per week**; and **one selected final
submission** scored in both prize phases. The one-entry guide leaves the account,
slot count, eligibility and AI disclosure blank: correctly unknown here.
[Official submission specs](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format)
require one float32 GeoTIFF at 100 m, EPSG:32611, correct bounds and `[0,1]`
inside the template footprint. The review has not submitted or claimed compliance
for any particular *person* or account.

**PR / merge:** none. Earlier REST permissions returned `push=false` for both
`SelfLearn` and `6GEMSDOE`; a later `gh api` request returned **HTTP 401 Bad
credentials**, so the GitHub connection also now needs attention. The entry's
score policy has not been verified on hidden labels, and the DrivenData
registration is unknown. It would be misleading to merge a score policy or a
site claim as “verified.” This review and the tested patch remain on the
session's existing `arena/01a0dba8-selflearn` branch. No other branch, site or
account was created. **Reconnect GitHub in Arena** with access to the existing
repository before trying a PR; no passwords or tokens should be shared in chat.

### First next action

**Account holder: identify the ONE DrivenData registration corresponding to
`6GEMSDOE`, confirm eligibility and this week's remaining submissions, and read
*that account's* submission history before making any upload decision.** Do not
share credentials. Then arrange write access to the existing repositories for a
reviewed PR, apply/test the Euclidean CV patch and correct the entry narrative;
seek **new independent fault validation / expert geologic review** before
considering a scratch raster. Re-run the exact format gate on whichever bytes the
verified account eventually selects. Do not present any local proxy as a public
score, or upload just to test a speculation.
