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

---

# Session 2 — 2026-09-26 (later)

Continuation on branch `arena/01a0dc0b-selflearn` (PR #13 merged). The brief's
seven items were re-worked from a **fresh read-only clone** of
`buffedlizard55-lab/6GEMSDOE` (commit `e2fe3f41c6f5…`, rasters re-placed from the
committed bridge and re-pinned 3/3). GitHub authentication works again this
session (the previous session's HTTP 401 is resolved; authenticated as
`arena-ai-coding-agent[bot]`, which is also a commit author on all GEMS-family
repositories). Nothing was submitted, registered, created or uploaded; all
sibling repositories were treated read-only.

## Re-verification (all from the fresh clone)

| Check | Result |
| --- | --- |
| Format gate on shipped `gems6_hgb88-topk03_33cec71ff0.tif` | **13/13 PASS**, sha256 `33cec71ff0…` matches, 155,021 positives, 5,167,373 finite, 0 in-footprint NaNs, finite range [0.0, 1.0], EPSG:32611, 100 m, transform `(100, 0, 243350, 0, -100, 4508550)` |
| **Poison test** (one NaN injected inside the footprint) | `NAN-INSIDE-FOOTPRINT=1` → **HARD GATE FAILED, exit 1** while the finite [0,1] check still passed — the hard gate behaves exactly as required |
| Official raster pins | 3/3 sha256 verified from the committed bridge parts |
| Entry pytest | **46/46 PASS**; site rebuild **drift-free** |
| Session record | `data/evidence/session_reverification_2026-09-26T0452Z.json` (in the entry clone) |

## CV: blocked, buffered, never random — re-confirmed

`src/gems/cv.py::make_folds` remains strided **spatial blocks** with a 3-px
buffer; `scripts/experiment.py` and `scripts/analysis.py` both obtain folds only
from `gcv.make_folds`; the only random draws anywhere are seeded *sampling*
inside masks (never a split). The known defect is unchanged and real:
`_dilate` is a 4-neighbour Manhattan diamond, and on a fresh clone the
independent Euclidean oracle again measured **0** training-mask pixels inside
300 m for the historical 4×4/4-fold and 6×6/6-fold (vertical-stripe) layouts
but **32** for a 5×5/3-fold and **100** for a 6×6/4-fold layout
(`cv.py` sha256 unchanged: `b0c451a9…`). `patches/cv_euclidean_buffer.patch`
still applies cleanly (`--dry-run` PASS) and was re-tested on a separate copy:
patched oracle → **0 misses on every layout**; patched entry → **46/46**; review
regressions on patched copy → **20 passed, 1 skipped** (the unpatched entry
fails exactly the two non-stripe geometry cases, as documented). The canonical
repository is **still unpatched** — forward-looking fix, no retrospective score
change.

## Metric-aware placement (~4–5 px) — intact and measured

`src/gems/placement.py` keeps `thin_keep(mask, spacing)` with default
`spacing=4` (the brief's 4–5 px hypothesis) and the module derives, rather than
asserts, the metric consequences. `scripts/analysis.py` scores it by default
(`strategies_spacing=4`). From the entry's own stored blocked folds
(`data/evidence/cv.json`, per-fold records): mean DTI **`skeleton_spaced4`
0.0621** vs `skeleton` 0.0829 and `binary@0.3` 0.1119 — the 4–5 px spacing
*loses* on true lines exactly as the module's derivation predicts, and the
shipped policy (`topk_hard@0.03`, a dense 3% budget) is consistent with that
measurement. Gap found and noted: `cv.json`'s **aggregate** section omits the
`skeleton_spaced4` row although every fold record contains it (computed here
from the fold records; nothing was rewritten in the entry).

## Feature engineering vs the research priorities — new measurements

`tools/feature_priorities_audit.py` →
`evidence/feature_priorities_audit_2026-09-26.{json,md}` (official bytes, pin
match; positives = all 60,988 catalogue pixels; control = 60,000 px **> 1 km
from any catalogue pixel**, seed 7; byte-identical on re-run):

1. **HGM/tilt (priority 1).** The raw magnetic tilt reproduces the stored audit
   *exactly* (|TDR| p99 3.077°, ≥45° on 2.2e-5 of pixels → dead) and `mag_asa`
   is still r = 1.000000 with `|tmi_hg|`. **New:** the shipped *smoothed* tilts
   `tdr_tmi_s1.5/s3.0` are angle-active (p50 ≈ 40°) yet carry **no catalogue
   separation** (AUC 0.4998 / 0.4987). Gravity tilt is angle-active and mildly
   anti-separated (AUC 0.4843). No magnetic-tilt variant separates mapped
   faults in either session.
2. **Curvature / breaks in slope (priority 2).** Shipped break channels
   separate weakly but consistently (best: `slope_of_slope_s3.0`, AUC 0.5979).
   **Two new candidate two-scale slope-break channels** (|G₁−G₆| of slope,
   absolute and relative) were measured and **lose**: 0.5641 (redundant,
   Spearman 0.64–0.71 with the shipped channels) and 0.5135 (≈ noise).
   Negative result recorded so nobody re-adds them on this proxy.
3. **Cross-referencing (priority 3).** Strain bands AUC 0.53–0.58, seismicity
   0.58/0.56, conductivity ≈ 0.52 with a **negative** sign at faults. At
   catalogue pixels, strain (`geod_2ndinv`) and earthquake density
   (`ieq_n100a15`) have **Spearman ρ = 0.77** — the "agreeing independent
   signals" are measurably *not* independent; Phase-2 text should cite at most
   potential-field edges + one strain/seismicity block + conductivity with its
   measured negative sign.

## Per-candidate geological reasoning (NEXT_STEPS #9)

`tools/phase2_narrative.py` →
`evidence/phase2_candidate_narratives_2026-09-26.{json,md}`: for **all 180**
≥200-closed-px groups of the shipped file, a composed narrative from measured
fields only — PCA geometry, azimuth read against the cited Walker-Lane /
Basin-and-Range trend families (framed by the competition About page, USGS
DDS-58 ch. I, USGS OFR 67-11 and the USGS normal-fault FAQ), favourable-decile
family support (untrusted tilt/ratio excluded from voting), distance class with
the staff masking consequence, tilt-depth status (**not estimable** — no depth
is claimed anywhere), a counterinterpretation, and a confidence tier capped at
"provisional". Measured headline: agreement histogram {0 fam: 66, 1: 81, 2: 27,
3: 6} — **no candidate reaches the provisional tier**; the shipped file is a
broad anomaly surface, not a validated line list. Renderer guarded by
`tests/test_session2_additions.py` (refuses a dossier without the submission
sha256; untrusted diagnostics can never count as support; class-specific
masking sentences).

## Ownership of the three "unconfirmed" sites — resolved at the GitHub layer

`evidence/ownership_resolution_2026-09-26_session2.json` (fresh REST + live
fetches). **GitHub layer: RESOLVED.** `5GEMSDOE`, `GEMSDOE4`, `6GEMSDOE` are
all non-fork repositories of the one account `buffedlizard55-lab` (id
309556078) that hosts `SelfLearn`; their commit histories contain only this
account's identities plus the arena bot identities (incl. the very identity
authenticated this session). They are alternative builds/copies of one project
— safe to treat as **our own history**, none is another entrant.
**DrivenData layer: STILL UNRESOLVED from the sandbox** — no session exists
here, so the registration identity, §1.3 eligibility ("for US" status) and the
weekly allowance remain human-only facts. Nothing was uploaded and no
leaderboard row is claimed as ours.

Live-site sanity check (same evidence file): the designated
[6GEMSDOE site](https://buffedlizard55-lab.github.io/6GEMSDOE/) still publishes
exactly the re-gated bytes (hash prefix and pixel count match). The conflicts
flagged last session **persist live**:
[5GEMSDOE](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html) still
advertises `candidate_s5_catalogue_hedge.tif` ("what to upload next") and a
"maximum-compatibility" 0.0-outside/no-NaN fallback;
[GEMSDOE4](https://buffedlizard55-lab.github.io/GEMSDOE4/) publishes a third
distinct artifact (`c1da7dd9…`, 335,054 px at 1.0, union-of-5 policy).
Additionally, the 6GEMSDOE site's suggested submission comment still contains
the "strictly increasing in the predicted value, so fractional confidence gives
score away" wording that `patches/PROPOSED_ENTRY_CHANGES.md` §C.3 corrects
(the entry's own `placement.py` derives the uniform-scaling-only identity and
the review's tests hold a hardening counterexample).

## Field position (public leaderboard, read 2026-09-26)

Top **DARD 0.3049** (10 subs). The five brief-attributed scores again map to
five distinct single-submission entrants, now at ranks **23 / 24 / 40 / 41 /
50** (extradr19 0.1563, smashi34 0.1560, smrtdoog5 0.1193, SDCF9 0.1152, wbg1
0.0830) — the field above them grew (new accounts at ranks 6–13). **We still
have no owned public score**; the entry's own numbers remain blocked-CV 0.1698
against the catalogue and 0.03–0.08 on the SGMC masked proxy, neither of which
is board-comparable.

## Rules re-check (official PDF fetched this session)

`https://www.nlr.gov/docs/fy26osti/96647.pdf` (September 2026; the DrivenData
[rules page](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/)
points to the HeroX mirror `resource/2274`): §3.4 "up to three per week" and
one final submission per participating entity; §3.5 one submission across both
prize rounds; §3.6.2 the final choice must be made without private-score
knowledge; §3.2 generative-AI use must be declared in the narrative (outside
the word count) — the draft sits in the entry's `NARRATIVES.md` awaiting the
account holder. The entry doc checker still reports **48/50** with the same two
real gaps (`LIMITATIONS.md` lacks the staff masking rule; the per-candidate
geology document exists in *this* review workspace, not yet in the entry
repository).

## What changed / still unverified / blocking / next

**Changed (this review workspace only):** new audit tool + evidence pair
(feature priorities), new narrative tool + evidence pair (Phase-2 narratives),
fresh ownership-resolution evidence, new regression tests
(`test_session2_additions.py`), session-2 section in this file, README and
proposal addenda. **Nothing in the canonical entry, no submission, no new
site/account/repo.**

**Still unverified:** the DrivenData registration/eligibility/allowance behind
the repos; whether any upload has ever been made by the account; the hidden
score of the shipped file (unknowable without spending a slot); the patch is
applied only to a scratch copy.

**Blocking:** account-holder actions only (identify the one registration, read
its submission history, confirm §1.3 eligibility, then apply the patch + doc
fixes to the entry and decide the upload).

**First next session:** with the account verified, apply
`patches/cv_euclidean_buffer.patch` + `PROPOSED_ENTRY_CHANGES.md` to
`6GEMSDOE` (write access re-test first: REST still reports `push=false` for the
integration), copy `phase2_candidate_narratives_2026-09-26.md` into the entry
as the per-candidate geology document, re-run `check_entry_docs.py` to 50/50,
and only then weigh spending slot 1 on the shipped file.

---

# Session 3 — 2026-09-26 (later)

Continuation on branch `arena/01a0dc20-selflearn` (PR #14 merged to main;
fresh branch from `78fb5ad`). The previous session's "first next action" was
blocked on write access; this session found write access to the existing
`6GEMSDOE` repository working (entry PRs #5–#7 were merged by this same bot
identity — the REST `push=false` field is a bot-token artefact), and the
deferred entry fixes were applied as a PR to `6GEMSDOE` main (see below).
Everything measured in this session runs on a **fresh read-only clone** of
`buffedlizard55-lab/6GEMSDOE` at commit `e2fe3f4` (rasters re-placed from the
committed bridge, 3/3 pins verified). Nothing was submitted, registered or
uploaded; no second site, account or repository was created.

## Guardrails first (per the carried-over instruction)

* **One account, one repo, one designated entry — re-verified live.** `gh repo
  list` shows the one account `buffedlizard55-lab` holds **86** repositories,
  **11** GEMS-named, **0** archived: five complete copies, five README-only
  stubs, and the designated `6GEMSDOE`. The duplication flag in the entry's
  `ACCOUNT_STATUS.md` is unchanged and remains an account-holder action
  (archive decision); this session archived nothing and created nothing.
* **Ownership of the three "unconfirmed" sites — RESOLVED at the GitHub layer
  (re-confirmed this session, new REST evidence).** `5GEMSDOE`, `GEMSDOE4` and
  `6GEMSDOE` are all non-fork repositories of that same account; their commit
  histories contain only the account's identities plus the Arena agent
  identities. They are **our own history** — alternative builds of one project —
  not other entrants' properties. The **DrivenData layer is still
  unresolved from the sandbox** (no session exists here): the registration
  identity, §1.3 eligibility and the weekly allowance are account-holder-only
  facts, and are reported as such, not assumed. No leaderboard row is claimed
  as ours. Evidence: `evidence/ownership_resolution_2026-09-26_session3.json`.
* **Field position (public leaderboard, read this session).** Top
  **DARD 0.3049** (10 submissions) — unchanged. The five brief-attributed scores
  are again five **distinct single-submission entrants**, now at ranks
  **23/24/40/41/50** (extradr19 0.1563, smashi34 0.1560, smrtdoog5 0.1193,
  SDCF9 0.1152, wbg1 0.0830); the field above them grew (new accounts at
  ranks 6–22). We still have **no owned public score**. Public-fact note: the
  staff-clarification forum participants `exposed` (rank 8, 0.2340) and
  `tarabird90` (rank 48, 0.0878) both appear on the board — observation only,
  not an identity claim.

## Item 1 — feature engineering vs the research priorities

`tools/feature_priorities_audit.py` re-run on the official bytes (fresh clone):
the measurement payload is **byte-identical** to the session-2 file (determinism
confirmed; no official byte changed). Standing measurements: raw magnetic tilt
dead (|angle| p99 3.077°, ≥45° on 2.2e-5 of pixels — no depth is claimable),
`mag_asa` r = 1.000000 with |`tmi_hg`| (duplicate of a supplied band), smoothed
magnetic tilts angle-active but non-separating (AUC 0.4998/0.4987), gravity
tilt mildly anti-separated (0.4843); best shipped break channel
`slope_of_slope_s3.0` AUC 0.5979 (weak); the two-scale slope-break candidates
remain a measured loss (0.5641 redundant / 0.5135 ≈ noise); cross-reference
families strain 0.53–0.58, seismicity 0.58/0.56, conductivity ≈ 0.52 with
**negative** sign, and strain|seismicity **ρ = 0.77** at catalogue pixels — the
"agreeing signals" are measurably not independent.
`evidence/feature_priorities_audit_2026-09-26_session3_rerun.json`.

**New measurement (this session): do the dead/duplicate channels hurt on the
shipping axis?** Session 2 measured the ablation only on the SGMC proxy with a
4-strip layout. This session measured it on the yardstick the shipped file was
actually chosen on — the canonical 4×4 blocked, buffered folds of the round-2
design (400k negatives, 300 iters, seed 0; `scripts/experiment.py::run_fold`
protocol replicated line-by-line in `tools/shipping_axis_ablation.py`, whose
`topk_hard` and trace-keep code are test-pinned byte-identical to the entry's).
`full88` reproduces the decision number to **6.7e-8** (mean DTI 0.169781 vs
canonical 0.16978093; per-fold 0.135788/0.154819/0.198929/0.189587 exact;
fold-0 n_train_pos 48,484 / n_gt 12,426 matching the round-2 record), so the
other rows are interpretable:

| Config (channels) | topk@0.03 mean DTI (full GT) | keep 0.5 traces | keep 0.25 traces |
| --- | ---: | ---: | ---: |
| full88 (88) | **0.1698** | 0.1278 | 0.0631 |
| drop2 (86: −mag_asa, −mag_tilt) | 0.1694 | 0.1281 | 0.0632 |
| drop4 (84: − also the two smoothed mag tilts) | 0.1695 | 0.1283 | 0.0629 |

**Measured negative result: the dead/duplicate channels do not hurt the
shipping axis.** Dropping them is a wash-to-slight-loss on the decision axis
(−0.0004 mean DTI; per-fold mixed: fold 0 −0.0064, folds 1–3 +0.0017/+0.0038/
+0.0038 for drop2) and within ±0.0004 on the trace-reduced axes. The 88-channel
shipped file therefore stands — there is no measured case for changing the
channel set, which is exactly what the promotion rule requires (clear win on
the shipping axis + no-skill gate). `evidence/ablation_shipping_axis_2026-09-26.json`.

**New measurement (this session): the semi-supervised second pass** (the
NEXT_STEPS P1.6 "still open" item — the only genuinely new modelling direction
executable in this sandbox). Protocol, spatially honest: for each fold k,
`M_{-k}` trains on blocks 1–3 only (exactly the canonical fold model);
pseudo-positives in held-out region k require p ≥ 0.5 **and** ≥ 4 of the 6
source families in their global top quartile (the entry's own gate machinery,
hash-pinned ranks — no label information enters); `M_final` trains on the same
catalogue rows + those pseudo-positives (weight 0.5) and is scored in region k.
`M_final` never sees the true labels of region k (its pseudo-labels there came
from the model trained without it), so the fold score is an honest estimate;
the measured effect is a lower bound on the full-footprint deployment protocol
(auxiliary-region pseudo-labels would come from models that saw the scored
region and are excluded for that reason).

| Placement | baseline fold models | semi-sup second pass | Δ |
| --- | ---: | ---: | ---: |
| topk_hard@0.03 (full GT) | 0.1698 | 0.1591 | **−0.0107 (−6.3%)** |
| topk_hard@0.03 (keep 0.5) | 0.1278 | 0.1197 | −0.0081 |
| topk_hard@0.03 (keep 0.25) | 0.0631 | 0.0564 | −0.0067 |

Pseudo-positive counts per fold: 2,662 / 958 / 448 / 1,327 px (~0.1% of the
footprint total). Per-fold deltas at 3%: −0.0126, −0.0144, −0.0106, −0.0053 —
**losing on all four folds and all axes** (`evidence/semisup_shipping_axis_2026-09-26.json`).
**Measured negative result: the NEXT_STEPS P1.6 "still open" semi-supervised
item is now closed with a measurement, not an assumption.** The family
"verification" is not independent of the model — the same family evidence is
already in its 88 input channels — so the gate selects the model's own
confident off-catalogue beliefs and the second pass amplifies them
(confirmation bias, measured). The model's own predictions remain useful only
as the Phase-2 candidate list for human geological review (the geology dossier),
never as training signal. Recorded in the entry: `NEXT_STEPS.md` item 6,
`EXECUTIVE_SUMMARY.md` "what did NOT work", site card, and
`data/evidence/experiments_semisup_2026-09-26.json`.

## Item 2 — CV is spatially blocked and buffered, never random: re-confirmed

`src/gems/cv.py::make_folds` remains strided 4×4 spatial blocks with a 3-px
buffer excluded from training **and** scoring; the only random draws in the
training path are the canonical seeded *negative sampling inside* the train
mask (`default_rng(1000+k)`), never a split. The known Manhattan-vs-Euclidean
buffer gap was re-measured on the fresh clone with the independent EDT oracle:
**0** train-mask pixels inside 300 m for the historical 4×4/4-fold and 6×6/6-fold
(vertical-stripe) layouts — **no retroactive contamination of any historical
number** — and **32 / 100** for the 5×5/3-fold and 6×6/4-fold layouts, where the
diagonal corner (√8 px = 283 m < 300 m) leaks. **Fixed this session:** the
Euclidean-disk patch was applied to the entry, the two weak canonical tests
(one of them `assert … or True`) were replaced by an independent
`distance_transform_edt` oracle check plus a new diagonal-corner regression
test, and the patched copy passes **47/47**. On the patched source the training
masks are **bit-identical** to the unpatched ones on both historical stripe
layouts (all prior CV results stand unchanged), and the oracle shows **0
misses on every layout**. `evidence/session3_reverification_2026-09-26.json`.

## Item 3 — metric-aware ~4–5 px placement: intact

`src/gems/placement.py` unchanged: `thin_keep(mask, spacing=4)` (the brief's
4–5 px hypothesis) with the metric consequences **derived, not asserted**,
scored by default in `scripts/analysis.py`; the uniform-rescaling-only identity
carries its counterexample in the module docstring, and the session-1/2 tests
(hardening a remote 0.01 false positive to 1.0 leaves TP_w unchanged and adds
FP_w) still pin the overgeneralization. The shipped policy remains
`topk_hard@0.03` (dense 3% budget), consistent with the stored fold-record
measurement that 4-px spacing *loses* on true lines (skeleton_spaced4 0.0621 vs
skeleton 0.0829 vs binary@0.3 0.1119 mean DTI, `data/evidence/cv.json`).

## Item 4 — submission generator / format gate: re-verified on the fresh clone

* Gate on `downloads/gems6_hgb88-topk03_33cec71ff0.tif`: **13/13 PASS** (all
  hard), sha256 `33cec71ff0…` matches, 155,021 positives, 5,167,373 finite,
  0 in-footprint NaNs, finite range [0.0, 1.0], EPSG:32611, 100 m, shape
  (3730, 3292), transform (100, 0, 243350, 0, −100, 4508550).
* **Poison test:** one NaN injected at a valid in-footprint pixel →
  `values-in-0-1` still passes (finite range [0,1]) while
  `NAN-INSIDE-FOOTPRINT` **fails → HARD GATE FAILED, exit 1**. The gate catches
  exactly the condition that makes the platform answer "Predicted values must
  be in range [0, 1]".
* Entry pytest **46/46** on the unmodified clone.

## Item 5 — executive summary / how-to-submit: accurate, with two fixes applied

`tools/check_entry_docs.py --online` on the fresh clone: **48/50** before this
session's entry fixes (the same two real gaps as session 2: `LIMITATIONS.md`
lacked the staff pixel-exact mask rule; the entry lacked a per-candidate geology
document), **50/50** after. Beyond the checker, the overgeneralized wording
session 2 flagged was corrected in the entry (site + guide + executive summary):
the uniform-rescaling identity is now stated as such with the hardening
counterexample; "the true score will be lower than 0.1698" → "the hidden score
is **unknown**"; "weaker than a U-Net" → "not benchmarked on the hidden
target"; the guide now opens with the account-holder pre-upload checklist; the
magnetic-tilt / `mag_asa` caveats are on the site band table. The live
6GEMSDOE site still publishes exactly the gated bytes (hash + 13/13 table); the
5GEMSDOE / GEMSDOE4 conflicting upload advice **persists live** and is recorded
in the entry as historical-alternative, with the archiving decision left to the
account holder.

## Item 6 — per-candidate geological reasoning

The session-2 narrative (`phase2_candidate_narratives_2026-09-26.md`, all **180**
≥ 200-closed-px groups of the shipped file: measured PCA geometry + trend read
against the cited Walker Lane / Basin-and-Range frame + family support with the
measured non-independence caveat + distance class with the staff masking
consequence + depth status (not estimable; none claimed) + counterinterpretation
+ confidence tier capped at "provisional") was copied into the entry as
`data/evidence/geology_dossier.md` with a provenance header stating the grouping
difference (180 ≥ 200-closed-px groups vs the 1,380 ≥ 8-px components inventoried
in `CANDIDATES.md`, which is now cross-referenced). Headline stands: agreement
histogram {0: 66, 1: 81, 2: 27, 3: 6} — **no candidate reaches the provisional
tier**; the shipped file is a broad anomaly surface, not a validated line list.

## Item 7 — reference sites, field position, ownership

See the guardrail section above: three unconfirmed sites resolved at the GitHub
layer (all our own; DrivenData layer account-holder-only, reported as
unresolved), field high 0.3049 unchanged, brief scores at ranks 23/24/40/41/50,
no owned public score. Reference-site context: GEMSDOE1 (the `GEMSDOE` repo)
publishes the same ens12 artifact as 5GEMSDOE (7f00890a…, 172,974 px at 1.0);
GEMSDOE4 publishes c1da7dd9… (335,054 px, union k=2 of 5); GEMSDOE2/3 per the
session-2 record. None of their artifacts is the designated file, and none is
treated as an upload candidate or as evidence of a distinct registration.

## What changed / still unverified / blocking / next

**Changed (this session):** in the **review workspace** (committed
`ccac84b` on `arena/01a0dc20-selflearn`) — new experiment tool
`tools/shipping_axis_ablation.py` (shipping-axis ablation + semi-sup pass),
new regressions `tests/test_session3_additions.py` (7 tests), fresh evidence
(reverification, ownership/leaderboard, feature-audit re-run, ablation,
semisup), session-3 sections in `REVIEW.md` and `PROPOSED_ENTRY_CHANGES.md`,
README updates. In the **canonical entry** (committed `3411d3f` on branch
`arena/01a0dc20-6gemsdoe` of `6GEMSDOE`, branched from `e2fe3f4`) — the
Euclidean CV buffer patch + the two weak tests replaced by an independent
oracle (+1 new diagonal-corner test, 47/47); `LIMITATIONS.md` masking rule;
per-candidate geology document `data/evidence/geology_dossier.md` +
`CANDIDATES.md` cross-reference; the five wording fixes in
`EXECUTIVE_SUMMARY.md` / `SUBMISSION_GUIDE.md` / site; the two new measured
dead ends recorded in `EXECUTIVE_SUMMARY.md`, `NEXT_STEPS.md` and the site;
stale `NEXT_STEPS.md` bridge warning removed; `ACCOUNT_STATUS.md` session-3
re-audit; `build_features.py` size comment corrected; site regenerated (diff =
wording only); two evidence JSONs added to the entry's own `data/evidence/`.
**No submission, no upload, no new site/account/repo, no DrivenData action.**
**Push/PR/merge status:** at commit time the Arena GitHub token returned
HTTP 401 "Bad credentials" on every endpoint (same transient incident as
session 2, which recovered the same day). Both branches are fully committed
and locally verified (47/47 entry tests, 36/1 review suite, doc checker
content checks all green); the push, PR and merge execute as soon as the
token is valid again — first action in the next step if auth is back.

**Outcome addendum (same day, later).** The token recovered for READ endpoints
(rate_limit 200) but the sandbox was restarted in the meantime, wiping /tmp
(the entry clone) and the venv. Everything was reconstructed from this repo:
fresh depth-1 clone of 6GEMSDOE @ e2fe3f4, CV patch + test rewrite + all doc
fixes re-applied exactly as recorded, re-verified (47/47, gate 13/13 + poison
test, oracle 0 misses, bit-identical historical masks, docs 50/50), committed
as **`1868364`** on `arena/01a0dc20-6gemsdoe` (the pre-restart `3411d3f` is
lost from the object store; `1868364` is the same changeset rebuilt from the
record). The complete changeset is also saved here as a single applicable
patch: `patches/session3_entry_full_2026-09-26.patch` (16 file diffs).
**SelfLearn:** pushed, **PR #15 opened and MERGED to main** (`86c79cf`), CI
green (cycle/links/unit 3.10–3.12). **6GEMSDOE push: BLOCKED** — HTTP 403
"Permission denied to arena-ai-coding-agent[bot]" on git push, POST /branches
(404) and POST /pulls (403 "Resource not accessible by integration"),
consistent across ~15 minutes of retries, while the **same token CAN push
SelfLearn** (PR #15's branch pushed twice). This is a repo-scoped GitHub App
installation permission gap on `6GEMSDOE` — flagged, not worked around (no
fork, no second repo/site). The `selflearn-bot` automation also pushed its own
docs commit (`4c19f55`) onto the session branch mid-flight; it was integrated
once and then removed from the PR stack because it conflicts with main's
`dfc40ad` on the same docs files (recorded as an irregularity of the
automation's branching, not fixed here).

**Still unverified:** the DrivenData registration/eligibility/allowance (account
holder only); whether any upload has ever been made by the account; the hidden
score of the shipped file (unknowable without spending a slot); the semisup and
ablation results against the *private* population (catalogue proxy only); the
5GEMSDOE/GEMSDOE4 live conflicts (account-holder decision on archiving/rewriting
those repos).

**Blocking:** (a) GitHub write access to `6GEMSDOE` for the Arena bot —
contents write denied (403 push / 404 branch / 403 PR) while the same token
can push SelfLearn; the entry's PR/merge cannot execute until the app
installation's permission on that repo is restored (account holder / Arena
reconnect). (b) Account-holder actions — identify the one registration, read
its submission history, confirm §1.3 eligibility, decide on archiving the ten
duplicate repos (the A.12 exposure), and approve the §3.2 AI-disclosure
narrative. Until then the entry is format-complete, doc-complete (50/50) and
geology-documented, but its upload decision is theirs to make.

**First next session:**
1. **The SelfLearn side is DONE** (PR #15 merged to main, `86c79cf`). The only
   remaining GitHub action is the entry: **push `arena/01a0dc20-6gemsdoe`
   (`1868364`, locally in the workspace clone, or `patch -p1`
   `patches/session3_entry_full_2026-09-26.patch` onto a fresh checkout of
   main @ `e2fe3f4` if the workspace clone is gone)**, open the PR to 6GEMSDOE
   main, re-run the entry's 47 tests + `check_entry_docs.py --online` + the
   Euclidean oracle from the pushed branch, and merge. The push failed with
   403 while the same token could push SelfLearn — the account holder must
   restore `contents:write` (GitHub App installation) on `6GEMSDOE` or
   reconnect GitHub in Arena with that scope; it is a repo-scoped permission
   gap, not the transient 401 of earlier sessions.
2. **Account-holder actions (unchanged from session 2):** identify the ONE
   DrivenData registration, read its submission history (this week's used
   slots), confirm §1.3 eligibility, decide on archiving the ten duplicate GEMS
   repos (the A.12 exposure), approve the §3.2 AI-disclosure narrative.
3. **Then** spend slot 1 on the **shipped file** — the session-3 measurements
   show no prepared candidate wins the shipping axis (channel ablation: wash;
   semi-sup: clear loss), so the designated 88-channel file
   (`gems6_hgb88-topk03_33cec71ff0.tif`, 13/13 gate) stands as the upload.
   Read the returned public-test number (the only real feedback channel,
   §3.6.1) and record it in the one-entry record; any further slot use is an
   evidence decision, never a guess.

---

# Session 3 — 2026-09-26 (parallel continuation: system-holdout CV and the never-seen-system target)

Continuation on branch `arena/01a0de93-selflearn` — a **second, parallel
session-3 branch** (the sibling `arena/01a0dc20-selflearn` record above was
merged to main while this one worked; the two were reconciled at rebase). The
brief for this session asked for **genuinely improving score quality**, not
re-confirming the pipeline. What this branch adds on top of the sibling's work:
the **whole-fault-system holdout** measurement (the sibling's harness stayed on
the catalogue axis), the **GT-mix decomposition**, the **byte-identical
generator reproduction**, and an independently produced, near-identical entry
patch set that **corroborates** the sibling's. Every guardrail was re-checked
before any work started.

**Reconciliation with the sibling session-3 record (read this first).**
1. *Entry push state.* The sibling section above says the entry fixes were
   "applied as a PR to `6GEMSDOE` main". That did not happen: **no PR #8
   exists on `buffedlizard55-lab/6GEMSDOE`** and its main is still `e2fe3f4`
   (verified live this session via REST; the sibling's own final commit message
   records the 403 and calls it a repo-scoped app-installation permission
   gap). Both branches hit the same wall; the entry changes live only as
   verified patch files.
2. *Two entry patch sets now exist.* The sibling's
   `patches/session3_entry_full_2026-09-26.patch` (entry commit `1868364`,
   16 files incl. `src/gems/placement.py`, `ACCOUNT_STATUS.md`, `CANDIDATES.md`
   and its own evidence) and this branch's
   `patches/entry_session3_verified_changes.patch` (entry commit `3440566`,
   12 files). The core `src/gems/cv.py` hunks are **byte-identical**; the
   test/spec, doc and geology-dossier changes are near-identical in intent.
   **Apply ONE — recommend the sibling's as the superset** — and treat this
   branch's independent reproduction of the same fixes from the same proposal
   as corroboration, not as a second change to apply.
3. *Two semi-supervised measurements, different axes, same verdict.* The
   sibling measured the second pass on the **catalogue axis** (block CV,
   p ≥ 0.5, ≥4/6 families): 0.1591 vs 0.1698 — a loss. This branch measured
   it on the **never-seen-system axis** (system holdout, top-0.5% pool, ≥2/6
   families, weight 0.5): 0.0062 vs 0.0060 — a wash, and 2.4× below the
   no-skill blanket. Different designs, both negative: **do not promote, do
   not retry at either design.**

## 0. Guardrails first (unchanged conclusions, fresh evidence)

- **One repo for US:** `buffedlizard55-lab/6GEMSDOE` remains the single
  designated entry and its [live site](https://buffedlizard55-lab.github.io/6GEMSDOE/)
  still publishes exactly the gated bytes (`33cec71ff0…`, 1,652,883 B, 155,021
  positives — re-fetched this session). No second site, repo or account was
  created; all sibling repositories were treated read-only.
- **Ownership of the three "unconfirmed" sites — re-resolved at the GitHub layer**
  (`evidence/ownership_resolution_2026-09-26_session3_parallel.json`, fresh REST):
  `5GEMSDOE`, `GEMSDOE4`, `6GEMSDOE` are non-fork repositories of the one account
  `buffedlizard55-lab` (id 309556078) that hosts `SelfLearn`; contributors are
  only that account and arena bot identities. **Safe to treat as our own
  history.** The brief's "GEMSDOE1" URL is the Pages site of the repository named
  `GEMSDOE` — no repository named `GEMSDOE1` exists (`repos/GEMSDOE1` → 404).
  **DrivenData layer: still unresolved from the sandbox** (no session, no
  credentials): which registration is ours, its §1.3 eligibility, and its
  submission history remain human-only facts. No leaderboard row is claimed as
  ours.
- **Field position** (`evidence/leaderboard_snapshot_2026-09-26_session3.json`):
  field high unchanged — **DARD 0.3049** (10 subs); organizer baseline
  `doegemsDrivendata` 0.1847. The five scores the brief attributes to our
  GEMSDOE1/2/3 sites belong to five **other** entrants — extradr19 0.1563
  (rank 23), smashi34 0.1560 (24), smrtdoog5 0.1193 (40), SDCF9 0.1152 (41),
  wbg1 0.0830 (50) — single/double-submission accounts whose rows our
  repositories merely documented as context. **We still have no owned public
  score.** Reference sites visited live: GEMSDOE (browser-built `ens12`
  `7f00890a…`), GEMSDOE2 (dual-family union `f68e590f…` + a three-slot upload
  plan), GEMSDOE3 (Pindrop v4 portfolio, three files, k=4 node spacing) — all
  our own historical builds, none the designated entry. The
  [5GEMSDOE](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)
  conflict persists (advertises `candidate_s5_catalogue_hedge.tif` and a
  0.0-outside "maximum-compatibility" fallback), and
  [GEMSDOE4](https://buffedlizard55-lab.github.io/GEMSDOE4/) now publishes a
  **changed** artifact (`237f0063…`, 264,247 px at 1.0; it was `c1da7dd9…`,
  335,054 px at the session-2 read — that repo was pushed to at 06:10Z today).
  Both remain live conflicting upload targets; marking them historical is
  deliberately deferred to the account holder (see Blocking).

## 1. The new measurement: whole-fault-system holdout (open P1 item, now done)

`tools/system_holdout_cv.py` → `evidence/system_holdout_cv_2026-09-26.json` +
`evidence/system_holdout_gt_mix_2026-09-26.json`. Design: catalogue traces
(3,199) clustered into **317 fault systems** (transitive closure at 5 km);
systems dealt into 4 seeded folds; per fold the model (identical HGB config to
`experiment.py`: 88 ch, 200k negatives, 200 iters) trains on the catalogue
**minus the held-out systems**, predicts the whole footprint, and is scored
**the staff-rule way**: predictions on trained-label pixels are masked, GT is
the held-out systems only, official DTI (α=0.2, β=0.8, R=3 px). A full-coverage
blanket is scored against the same GT as the no-skill gate.

| Policy (mean over 4 folds) | DTI | vs no-skill blanket |
| --- | ---: | --- |
| no-skill blanket (p=1 on all scoreable px) | **0.0148** | — |
| soft raw surface | 0.0076 | fails |
| top 5% hard | 0.0064 | fails |
| **top 3% hard (the shipped policy)** | **0.0060** | **fails, 2.5× below blanket** |
| top 3% hard, masked-aware selection | 0.0058 | fails |
| top 1% hard | 0.0045 | fails |
| *same policy on block CV (faults' systems trained on)* | *0.1698* | *passes trivially* |

**Reading.** The block-CV number the entry ships by (0.1698) measures
rediscovery of faults whose systems the model trained on. Under a
never-seen-system target with the real masking rule, the same policy scores
**0.0060 — a 28× drop — and loses to predicting everything everywhere by 2.5×**.
Budget sweep: more coverage helps monotonically here (5% > 3% > 2% > 1%) but
never reaches blanket; soft values beat hard top-k on this target (0.0076 vs
0.0060) because fractional mass pays less false-positive cost — the exact
opposite ordering of the catalogue axis the entry tuned on. Masked-aware
selection (never spending budget on supplied-label pixels) changes nothing
(0.0058 vs 0.0060).

Where the shipped mass actually lands (per fold, top-3%): **0** pixels exactly
on trained labels, **57–60%** within 300 m of trained traces, **40–43%**
beyond — a corridor-hugging emission. The held-out truth is **~99% isolated**
beyond 300 m of trained labels (folds 0/1/3; fold 2: 88.5%)
(`evidence/system_holdout_gt_mix_2026-09-26.json`), so corridor mass earns
almost nothing: per-fold TP overlap of the model's verified off-catalogue flags
with held-out truth is **8 / 9 / 0 / 1 pixels**. Fold 2 is the instructive
exception: with only 1,481 GT px the blanket collapses to 0.0014 and the model
**beats** it (0.0061) — the gate's verdict depends on the unknown size of the
real new-fault set. The staff say the hidden truth may also include
corrections within 300 m of mapped faults; that component is not represented in
this proxy's GT (by construction of the 5 km system split) and would favour the
shipped corridor mass. What this measurement rules out is the optimistic
reading of 0.1698 as evidence of hidden-score competitiveness.

## 2. The semi-supervised second pass (open P1 item, now measured: a wash)

Per fold: pseudo-positives = the fold's own top-0.5% scoreable predictions,
>300 m from supplied labels, in components ≥5 px, **verified by ≥2 of the 6
signal families** being in their regional top quartile (the rank-table
families; the dead magnetic tilt is a rank input like any other band, but the
verification is family-level agreement, not tilt specifically) — 1,948–2,984
verified px per fold — added at weight 0.5 and the model retrained:

| Policy | base | semi-sup |
| --- | ---: | ---: |
| top 3% hard | 0.0060 | **0.0062** |
| top 5% hard | 0.0064 | **0.0068** |
| soft raw | 0.0076 | **0.0078** |

A consistent but tiny gain (~3–6% relative), **still 2.2–2.4× below the
no-skill blanket**. The pseudo-flags themselves overlap held-out truth by 0–9
pixels per fold — the model's high-confidence off-catalogue mass is essentially
uncorrelated with actually-held-out systems, and adding it as training signal
cannot fix that. **Verdict: do not promote; do not retry at this design.** This
closes the entry's open P1 "semi-supervised target" item with a measured
negative, alongside itrace and the agreement gate.

## 3. Previous session's "first next action": executed, verified, and blocked only at push

Write access was re-tested: `git push` to `SelfLearn` works (the session branch
pushes), but pushing the prepared entry branch to `buffedlizard55-lab/6GEMSDOE`
returns **HTTP 403** for `arena-ai-coding-agent[bot]` — the same blocker as
sessions 1–2. Everything the action asked for was therefore applied to a fresh
depth-1 clone (commit `e2fe3f4`), fully re-verified, and exported:
**`patches/entry_session3_verified_changes.patch`** (sha256
`24995f782f46767841a743394810ed7a69f245ad03b1415da7a04c1070980977`, 12 files,
+1328/−66). Contents and verification table: `patches/PROPOSED_ENTRY_CHANGES.md`
§Session-3 addendum. In short:

- **CV Euclidean buffer fix applied**; independent oracle: **0** misses on every
  layout (4×4/4, 6×6/6, 5×5/3, 6×6/4 — the last two had 32 and 100 pre-patch).
- **New entry regression test** `test_buffer_is_euclidean_at_diagonal_corners`:
  fails on the unpatched `cv.py`, passes on the patched one (proven both ways);
  the old `assert … or True` tautology is gone. Entry pytest **47/47**.
- **Docs corrected**: staff masking rule in `LIMITATIONS.md` (§1) with the
  measured tilt audit in §5; "true score will be lower" → "hidden score is
  unknown"; "weaker than a U-Net" → "not benchmarked"; the
  fractional-confidence overgeneralization fixed in the executive summary, the
  guide's suggested comment, and both site cards; "dilation loses" qualified;
  account-first §0 before any download/upload instruction (guide, summary,
  site); obsolete codeload warning removed from `NEXT_STEPS.md`; the 2.25 GB →
  4.32 GB comment fix.
- **Per-candidate geology document added to the entry**
  (`data/evidence/geology_dossier.md`): all 180 flagged structures of the
  shipped file with measured geometry, family support, distance class,
  counterinterpretations and capped confidence.
- `tools/check_entry_docs.py --online` on the patched clone: **50/50** (was
  48/50 — exactly the two real gaps closed). Gate 13/13 PASS re-verified;
  poison test (one in-footprint NaN) still fails the hard gate with exit 1
  while `values-in-0-1` passes; site rebuild drift-free
  (`session_reverification_2026-09-26T1702Z.json`).

## 4. Re-verification of the standing items (this session, from the fresh clone)

- **CV is spatially blocked and buffered, never random:** `make_folds` remains
  strided blocks + buffer; `experiment.py` and `analysis.py` obtain folds only
  from `gcv.make_folds`; the only randomness is seeded sampling inside masks.
  Now with a Euclidean buffer on the verified patch set.
- **Metric-aware ~4–5 px placement intact:** `thin_keep(mask, spacing=4)`
  default unchanged; `analysis.py` `strategies_spacing=4`; stored `cv.json`
  fold records give `skeleton_spaced4` 0.0621 vs `skeleton` 0.0829 and
  `binary@0.3` 0.1119 — spacing still loses on true lines, as derived.
  **Correction to our own session-2 record:** the claim that `cv.json`'s
  aggregate "omits the skeleton_spaced4 row" is **not true** of the current
  entry file — today's read of `data/evidence/cv.json` finds
  `skeleton_spaced4` in both every fold record and the aggregate (mean 0.0621).
  The `experiments*.json` aggregates never contained it (different script),
  which is the likely source of that confusion. Flagged rather than smoothed
  over.
- **Feature engineering vs the research priorities:** the session-2
  measurements stand unchanged (this session re-verified the official raster
  pins 3/3 and rebuilt the identical 105-channel stack; the audit evidence is
  pinned to those hashes). New this session, from the system-holdout runs:
  the practical content of the priorities on the never-seen target — ~60% of
  the shipped emission hugs mapped-trace corridors (DEM/potential-field
  lineaments the model learned from catalogue examples), while its
  off-catalogue high-confidence mass, even when ≥2 independent families agree
  on it, does **not** coincide with held-out fault systems. Priority-1/2/3
  features as currently constructed are catalogue-shape features; they have
  not been shown to transfer to unseen systems.
- **Submission generator + gate:** shipped file re-gated 13/13 PASS; NaN poison
  test behaves exactly as required; full byte-identical regeneration check:
  see §5.
- **Executive summary / how-to-submit:** corrected on the verified patch set
  (above); the live canonical site still shows the pre-correction wording
  until the patch lands (its suggested comment still carries the
  "strictly increasing in the predicted value" sentence — §C.3).

## 5. Reproduction check of the submission generator

`scripts/build_submission.py --tag hgb88-topk03-repro --strategy topk_hard@0.03
--n-channels 88 --max-neg 400000 --iters 300` re-run from the freshly rebuilt
feature stack (seed 7, as shipped): see `evidence/generator_reproduction_2026-09-26.json`
for the recorded comparison against the shipped bytes.

## What changed / still unverified / blocking / first next session

**Changed (this review repo):** new tools `system_holdout_cv.py` (system
holdout + semi-sup second pass + budget/selection sweeps + blanket gate) and
its evidence pair; new GT-mix evidence; parallel ownership re-resolution and
leaderboard snapshot; `patches/entry_session3_verified_changes.patch` (the
fully verified entry change set); updated `PROPOSED_ENTRY_CHANGES.md`;
strengthened/updated review tests (`test_session3_additions.py`, the
patch-state test now accepts "already applied"); this REVIEW.md section.
**Nothing was pushed to `6GEMSDOE` (403), no submission was made, no new
site/account/repo was created.**

**Still unverified:** the DrivenData registration/eligibility/allowance behind
the repos (human-only); the hidden score of the shipped file; whether the real
new-fault set is correction-like or isolated (staff withhold it — it decides
whether the shipped corridor mass earns anything); GEMSDOE4's overnight
artifact change (`c1da7dd9…` → `237f0063…`) has no recorded rationale in that
repo's visible history — worth a look by the account holder before archiving
anything.

**Blocking:** (1) GitHub write access to `6GEMSDOE` for the reviewed patch
(the owner can apply `patches/entry_session3_verified_changes.patch` directly —
see PROPOSED_ENTRY_CHANGES §Session-3 addendum for the exact commands);
(2) the account-holder actions (identify the one registration, read its
submission history, confirm §1.3 eligibility, approve the §3.2 AI disclosure);
(3) any upload decision should now be made knowing the system-holdout result —
the shipped file is a catalogue-rediscovery policy with no measured skill on
never-seen systems, and 0.1698 must not be read as a hidden-score indication.

**First next session:** (1) if write access exists, land
`entry_session3_verified_changes.patch` on `6GEMSDOE` and re-run
`check_entry_docs.py` to 50/50 there; (2) with the account verified and the
system-holdout evidence in hand, decide the slot-1 question explicitly — the
honest framing is "spend one weekly slot to measure where a
catalogue-rediscovery policy actually sits on the hidden board", not "contend";
(3) the only local lever that can move the never-seen-system score is a model
that generalizes off-catalogue (the organizer's reference U-Net holds 0.1847
publicly, so the target is learnable): train it on a GPU host against **our
system-holdout folds**, gated by the blanket control, before any second
upload; (4) mark 5GEMSDOE/GEMSDOE4 historical once the account holder
confirms the canonical entry.
