# Session 5 — the spacing-4 hypothesis survives the shipping budget

2026-09-26 · review workspace `buffedlizard55-lab/SelfLearn` · designated entry
[`buffedlizard55-lab/6GEMSDOE`](https://github.com/buffedlizard55-lab/6GEMSDOE) at
revision [`e2fe3f4`](https://github.com/buffedlizard55-lab/6GEMSDOE/commit/e2fe3f41c6f5dd2dcb2fc91958ee67698f114ada)

**Read this before `REVIEW.md` and `SESSION4.md`.** Session 4's handoff asked for
exactly one thing before any promotion decision: re-measure the spacing-4 gain at the
**shipping** training budget (400k negatives / 300 iterations), with the same
exact-system isolation, matched-budget null controls and a pre-specified
layout/buffer sensitivity. That is what this session did, in full, on freshly rebuilt
official bytes.

No account, repository, site, submission or replacement artifact was created. One
local candidate GeoTIFF was built, hard-gated and read geologically; it lives in the
session scratch directory and is **not** committed, published or uploaded.

## Executive result

**The pre-specified hypothesis holds at the shipping budget, on all three
pre-specified layouts.** 88 engineered features with a genuine 4-pixel minimum
spacing beats the dense policy the shipped artifact uses — and beats every frozen
label-blind null seed in every fold — while the dense policy *loses* to a
matched-budget random control.

| 3% budget, 400k negatives / 300 iterations, mean fold DTI | dense (spacing 1) | **spacing 4** | spacing 5 (underfills) | null dense | null s4 |
|---|---:|---:|---:|---:|---:|
| raw 19 bands | 0.0696 | 0.2213 | 0.2056 | 0.1722 | 0.2037 |
| **engineered 88 (shipped model)** | 0.0925 | **0.2345** | 0.2100 | 0.1722 | 0.2037 |
| drop magnetic tilt + ASA | 0.0911 | 0.2344 | 0.2094 | — | — |

Unweighted means over four geographic quadrants (2×2 blocks, 4 folds, 3 px Euclidean
buffer, every system touching a test quadrant purged globally). Null = three frozen
random-priority seeds, identical score masks and budget. Evidence:
[models](evidence/spatial_system_models_shipping_session5.json),
[controls](evidence/spatial_controls_shipping_session5.json),
[comparison](evidence/spatial_comparison_shipping_session5.json),
[geometry](evidence/spatial_system_geometry_session5.json),
[driver manifest](evidence/shipping_budget_manifest_session5.json).

**Pre-specified rule, written into the driver before the run** (`--print-rule`):
H1 = full88 spacing4 mean > full88 dense mean AND full88 spacing4 above the maximum
of the three null seeds in every fold; H2 = the sign of (spacing4 − spacing1) is
positive on both alternative layouts. **H1 holds. H2 holds** (3×3 blocks/3 px:
0.2203 vs 0.0907; 2×2 blocks/5 px: 0.2435 vs 0.0965 — see
[evidence/spatial_system_models_sens1_session5.json](evidence/spatial_system_models_sens1_session5.json)
and [sens2](evidence/spatial_system_models_sens2_session5.json)).

Three findings that matter more than the headline number:

1. **The shipped dense policy scores below random at the same budget on held-out
   geography** (0.0925 vs 0.1722, every fold). Its mass is concentrated near mapped
   traces, which the purged folds deliberately contain none of.
2. **The gain is in the placement, not the features.** full88 spacing4 0.2345 vs
   raw19 spacing4 0.2213 is a real but small feature effect (+0.013); spacing4 vs
   dense is a factor of 2.5.
3. **drop2 ≈ full88** (0.2344 vs 0.2345). Session 4's +0.0003 was noise, and this
   session confirms it: **do not drop the magnetic channels on this evidence.**

**None of this is a leaderboard score.** The truth is the mapped catalogue on held-out
geography — a transfer proxy. It says nothing directly about the hidden expert labels,
and the campaign's field high is 0.3049 ([DARD](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)).

## Pass 1 — implementation and measurements

### 0. Guardrail and ownership, checked first

`tools/ownership_live_audit.py` (new, read-only `gh api`): all GEMS-named repositories
are non-fork repositories of the ONE GitHub account `buffedlizard55-lab` (owner id
309556078), which also hosts this workspace —
[evidence](evidence/ownership_resolution_2026-09-26_session5.json). That resolves the
brief's three "ownership unconfirmed" sites **at the GitHub layer**: 5GEMSDOE,
GEMSDOE4 and 6GEMSDOE are our own historical project copies, not another entrant's
property. The **DrivenData layer remains unresolved** — no session exists here, the
data tab is login-gated, and registration identity, §1.3 eligibility, submission
history and weekly allowance are account-holder-only facts. No row on the board is
claimed as ours.

**Irregularity found this session (flagged, not smoothed):** a **12th** GEMS-named
repository, `buffedlizard55-lab/LEARNGEMSDOE`, was created at
2026-09-26T18:18:32Z — about ten minutes before this session started — with a single
`# LEARNGEMSDOE` README and Pages built. It was **not** created by this session (the
commit author is the account holder, `buffedlizard55@gmail.com`). It is a stub, not a
project copy, but it publishes a 12th challenge URL. The entry's own doc checker now
fails two checks because of it (`account-repo-count`, `account-table-LEARNGEMSDOE`),
which is the mechanical proof that the entry's "eleven repositories" claim is stale.

### 1. Data and feature stack, rebuilt from pinned bytes this session

* `data/training_features.tif` reassembled from the committed bridge parts and
  re-verified: 418,912,844 B, sha256 `4371c82e…` (3/3 official rasters OK).
* `scripts/build_rank_tables.py` and `scripts/build_features.py` re-run from those
  bytes: 105 channels, 7,113,320 invalid / 5,165,840 all-band-valid pixels — identical
  to the pinned geometry.
* **New provenance finding:** the entry pins `rank_tables_sha256 = 64a62c3b…` in
  `features_meta.json`, but `build_rank_tables.py` writes `built_utc` into that JSON,
  so the file hash can never be reproduced. Two independent builds differ only by that
  timestamp; the content is deterministic. The pin that *is* reproducible is the
  official raster's sha256, which `RankTables.check_sha` enforces.
  [evidence](evidence/rank_tables_pin_audit_session5.json) · A hash pin that cannot be
  re-derived is not a verification; reported as an irregularity.

### 2. Feature engineering against the research priorities

`tools/feature_priorities_audit.py` re-run on the freshly rebuilt bytes:
[evidence](evidence/feature_priorities_session5.json). Session 4's measurements
reproduce:

* **Magnetics/gravity HGM and tilt.** The supplied magnetic tilt still has |angle|
  p99 ≈ **3.08°** and reaches ±45° on **2.2e-5** of pixels — it cannot bracket a depth
  inversion, and no depth claim is made anywhere. `mag_asa` still duplicates
  |TMI horizontal gradient| at **r = 1.000**, so "magnetic gradient" and "analytic
  signal" are one measurement, not two. The recomputed smoothed tilt derivative
  (`tdr_tmi_s1.5/s3.0`) is angle-active (p50 ≈ 40°, 44% of pixels beyond ±45°) but has
  catalogue AUC ≈ **0.50** against a far background. Gravity tilt is angle-active and
  anti-separated (AUC ≈ 0.484). Multiscale HGM is present and weakly informative
  (ASA AUC ≈ 0.535).
* **DEM curvature and slope breaks.** On the **100 m detrended** elevation (not 1 m
  lidar): `slope_of_slope_s3.0` AUC ≈ **0.598**, `slope_of_slope_s1.5` 0.589,
  `slope_computed` 0.574, |Laplacian| 0.556. Two candidate two-scale slope-break
  channels measured this session: `|G1(slope) − G6(slope)|` AUC 0.564 and the relative
  version 0.514 — **neither beats the shipped `slope_of_slope_s3.0`**, so nothing was
  added to the stack.
* **Strain / conductivity / earthquake cross-reference.** Per-band far-background AUC:
  `geod_2ndinv` 0.584, `geod_shearrate` 0.581, `ieq_n100a15` 0.583, `deq` (polarity
  corrected) 0.560, `cond_surf` 0.520, `depth_to_base_surf` 0.514. Pairwise Spearman
  **on catalogue positives**: strain|seismicity **0.77**, strain|conductivity −0.22,
  conductivity|seismicity −0.14. Strain and seismicity are the *same* signal for
  practical purposes; counting them as independent confirmations is the error the
  brief's third priority invites, and it is not made here.

### 3. Spatial CV — blocked, buffered, whole-system purged (re-verified)

All three layouts (primary 2×2/4 folds/3 px; sensitivity 3×3/4 folds/3 px;
sensitivity 2×2/4 folds/5 px) show, per fold: **0** train/test overlap, **0** training
pixels within the buffer of the score area, **0** training pixels on a held system,
**0** shared positive systems, and both classes present. 3,199 traces cluster into
**40** exact systems (all-pixel single linkage at 5 km — no subsampling).
[geometry evidence](evidence/spatial_system_geometry_session5.json). Never a random
pixel split: negatives are subsampled only inside the already-isolated training mask.

The canonical entry's own `src/gems/cv.py` still dilates with a **Manhattan**
(4-neighbour) structuring element, so a 3-px buffer leaks at diagonal corners — the
defect sessions 3 and 4 documented. It is unchanged at `e2fe3f4`, the verified patch
still cannot be pushed from here (HTTP 403), and the review tests still fail against
the unpatched entry *by design* (they encode the defect). See Pass 2.

### 4. Metric-aware placement

The shipped `topk_hard@0.03` artifact is **dense**: 155,021 pixels, and its generator
has no spacing option. The session-5 diagnostic implements probability-ordered
suppression (`budget_nodes`, minimum Chebyshev separation, deterministic tie-breaks,
explicit budget). Dense and spacing-4 emit **exactly the same 155,021 pixels** across
the four folds, so the comparison is an equal-actual-budget one; spacing 5 underfills
and is reported as such. The session-5 CV also records the fractional (`soft`) policy,
which collapses to 0.017–0.045 — consistent with the entry's own measurement that
binarising helps *on this population*, while the general claim it publishes is false
(see §5).

### 5. Submission format and generator path — 13/13, and the poison test still bites

* Shipped artifact re-gated from the entry's own committed bytes: **13/13 PASS** —
  EPSG:32611, 100 m, 3730 × 3292, transform `(100, 0, 243350, 0, -100, 4508550)`, NaN
  nodata, finite range [0,1], 0 infinities, 0 NaNs inside the footprint, 0 finite
  pixels outside it ([evidence](evidence/submission_gate_session5.json)).
* **Negative test:** one in-footprint NaN written into a copy of the shipped bytes
  passes `values-in-0-1` and fails **NAN-INSIDE-FOOTPRINT with exit 1**
  ([evidence](evidence/nan_poison_session5.json)). The hard gate is intact.
* The entry's own `session_reverify.py` re-run: gate 13/13, rasters 3/3, pytest 46/46,
  site rebuild drift-free ([evidence](evidence/session_reverification_2026-09-26_session5.json)).
  Its repo audit still reports **11** GEMS-named repositories — stale, see §0.
* **The published metric claim is false and still live.** The 6GEMSDOE page and
  `EXECUTIVE_SUMMARY.md` say the metric "is strictly increasing in the predicted value,
  so fractional confidence gives score away". The uniform-rescaling identity is true
  (verified over 24 values of λ); the hardening inference is not — measured with the
  entry's own metric, raising a remote false positive from 0.01 to 1.0 takes DTI from
  **0.998 to 0.833** ([evidence](evidence/metric_claim_check_session5.json)). The
  session-3 patch fixes the sentence; it is still not deployed.

### 6. Executive summary / how-to-submit accuracy

`tools/check_entry_docs.py` on the canonical pre-patch entry: **35/37 offline,
47/51 online**. The four failures are: the missing masking-rule discussion, the
missing per-candidate dossier, and the two new repository-count failures from the
12th repository ([offline](evidence/entry_docs_offline_session5.txt),
[online](evidence/entry_docs_online_session5.txt)). The upload instructions still put
"download → submit" ahead of account/eligibility confirmation.

### 7. Geological reasoning for the candidates the model flags

* **Shipped artifact re-verified byte-identically.** Re-running
  `geology_dossier.py` on the pinned bytes reproduces the committed dossier
  (`285002cf…` for the rendered markdown, `a202e84c…` for the fragment inventory)
  ([evidence](evidence/shipped_geology_rerun_session5.json)). 180 large components,
  2,409 small ones, 93 pixels lost to closing — unchanged.
* **One new local candidate, with its own reasoning.**
  `candidate_spacing4-topk03.tif` (sha256 `f807dccf…`, 155,021 px, 13/13 gate PASS) is
  the shipped model with only the placement policy changed. Its dossier is
  [evidence/spacing4_candidate_geology_2026-09-26.{json,md}](evidence/spacing4_candidate_geology_2026-09-26.md)
  — all **943** large components, each with hypothesis, measured support,
  counterinterpretation and capped confidence — and the hand-written reading for six
  named ones is in
  [evidence/spacing4_candidate_geology_session5.md](evidence/spacing4_candidate_geology_session5.md).
  What the policy change does to the geology: emitted pixels on the supplied catalogue
  fall from **23,605 to 4,106**; large components more than 300 m from any mapped trace
  rise from **1 to 491**; the best-corroborated flags form two coherent clusters
  (~39.2°N 118.5°W and ~38.65°N 118.45°W); half of all large components have **no**
  diagnostic family in their favourable decile, and no depth is estimable for any of
  them (|tilt derivative| ≥ 45° on 0.00% of emitted pixels).

### 8. Field context and the brief's score table

`tools/leaderboard_snapshot.py` (new) parses a verbatim transcript of the public board
([raw](evidence/leaderboard_raw_2026-09-26_session5.md),
[snapshot](evidence/leaderboard_snapshot_2026-09-26_session5.json)):

* Field high unchanged: **DARD 0.3049** (#1, last submission 3d 19h ago). Organizer
  reference **0.1847** (#14).
* The brief's five numbers have drifted: **0.1563 is now held by two entrants**
  (extradr19 #24 and SDCF9 #25), 0.1560 is smashi34 (#26), 0.1193 is smrtdoog5 (#41),
  0.0830 is wbg1 (#50), and **0.1152 is no longer on the visible board** (SDCF9 moved
  to 0.1563). GEMSDOE2's live page still calls 0.1563 "the recall-union's board
  score" — that attribution is unsubstantiated and is not repeated here.
* All six reference sites were re-read this session
  ([evidence](evidence/live_site_claims_2026-09-26_session5.md)). Session 3's open
  question about GEMSDOE4's artifact change is **resolved**: it is recorded in that
  repository's history (commit `ef0fd2ee`, "Session 34: fold-scoped selection, the
  union holdout audit, and the k = 3 adoption").
* Concurrent sessions pushed to 5GEMSDOE (17:28Z) and GEMSDOE4 (05:59Z) today. At the
  GitHub layer that is our own history; against rules §3.4 any *upload* from more than
  one copy multiplies the weekly allowance. Nothing was uploaded from anywhere here.

## Pass 2 — bugs, gaps and review

* New tools: `ownership_live_audit.py`, `leaderboard_snapshot.py`,
  `metric_claim_check.py`, `rank_tables_pin_audit.py`,
  `shipping_budget_confirmation.py`, `build_spaced_candidate.py`.
* New regressions: `tests/test_session5_additions.py` — 13 tests, all passing
  (independent DTI oracle for both metric claims, `budget_nodes` budget/spacing/
  determinism/underfill/rejection oracles, evidence pins for ownership, leaderboard,
  doc checks, the rank-tables pin, gate + poison, and per-fold CV isolation on all
  three layouts). CI's `gemsdoe-review` job now runs the session-4 **and** session-5
  files; the earlier session files stay out of that job because they encode the
  unpatched entry's defect and need an entry checkout.
* **Three review tests fail against the canonical entry, and should.**
  `test_cv_excludes_full_euclidean_metric_kernel[5-3-shape1]`,
  `[6-4-shape2]` and `test_entry_cv_is_patched_euclidean` fail on `e2fe3f4` because
  `cv.py` dilates in Manhattan metric. This is the standing defect record, not a
  regression.
* **The patch still works, and was re-applied this session to prove it.** Applying
  `patches/session3_entry_full_2026-09-26.patch` to a scratch copy of `e2fe3f4` turns
  the review suite green (75 passed, 1 skipped), the entry's own suite green (47
  passed), the offline doc check 37/37, and restores a true disk in `_dilate`
  (5/13/29/49/113/169 pixels at radii 1/2/3/4/6/9, corner (2,2) included at radius 3).
  The scratch copy was then reverted to a pristine `e2fe3f4`
  ([evidence](evidence/entry_patch_verification_session5.json)). **New defect found in
  the patches directory:** the small standalone `cv_euclidean_buffer.patch` no longer
  applies with `git apply` (docstring context drift) — it needs `patch --fuzz=3`.
  Regenerate it from `e2fe3f4` before quoting it as ready to apply.
* Repo-size decision: the candidate's 943-component dossier JSON and rendered
  markdown are committed (6.4 MB + 1.0 MB), following the existing convention that
  evidence is the audit trail. Its 30,467-component fragment inventory (4.3 MB) is
  **not** committed; the dossier's own `counts` block records the component and pixel
  totals, and the rendered markdown states explicitly that the small components were
  not interpreted.
* Fixed during the session: the driver's `--print-rule` path (argparse), and a
  double-counting bug in my first ownership-audit run that reported `LEARNGEMSDOE`
  twice in the GEMS-named list.

## Pass 3 — prompt and rules recheck

Official sources re-read this session: the
[problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
(submission format, metric, worked example), the
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) §§1.3, 3.2, 3.4–3.6, and the
staff [pixel-exact mask clarification](https://community.drivendata.org/t/11516/4).

* One designated entry (6GEMSDOE); no registration, upload, site or final selection.
  Weekly limit three per entity; one final selection across both rounds — gates, not
  permission to use another account.
* Generative-AI involvement must be disclosed (§3.2); the existing draft still needs
  account-holder approval. US eligibility is not inferred from GitHub location.
* The staff mask is pixel-exact, so the session-5 CV's held-out labels are a proxy
  analogue, not private truth. No external dataset was incorporated; licensed
  provenance must precede any 1 m DEM or external-label use.
* Proxy evidence cannot establish public or private performance; no discovered fault,
  calibrated depth or prize competitiveness is claimed anywhere in this session.

## What changed / still unverified / blocking / first next session

**Changed (this review repo only):** the shipping-budget confirmation of the
spacing-4 hypothesis with two pre-specified sensitivity layouts and matched-budget
nulls; one gated local candidate plus its own 943-component geological dossier and a
hand-written reading of six named candidates; fresh feature-priority measurements on
rebuilt official bytes; a fresh ownership/site audit (which found a 12th GEMS-named
repository created during the session window); a fresh leaderboard snapshot showing
the brief's score table has drifted; the metric-claim check that refutes the entry's
published sentence; the rank-tables pin audit; six new tools, 13 new regressions, a
wider CI job, and this handoff. **Nothing was pushed to 6GEMSDOE (403), no submission
was made, no site/account/repo was created, and the shipped artifact is unchanged.**

**Still unverified:** the DrivenData registration, §1.3 eligibility, submission
history and remaining weekly allowance (human-only); the hidden score of any file;
whether the real new-fault set is correction-like or isolated (staff withhold it);
the geological identity of every flagged component; whether the `LEARNGEMSDOE`
repository was deliberate.

**Blocking, in order:** (1) **this session's work is committed locally on
`arena/01a0def8-selflearn` but could not be pushed or opened as a pull request: the
sandbox GitHub token expired during the session** (`gh auth status` reports "the
github.com token in GH_TOKEN is no longer valid"; unauthenticated API calls return
401). Reconnecting GitHub in Arena is the first thing to do — the commit and the clean
working tree are intact, so only the push and the PR remain. (2) GitHub write access
to 6GEMSDOE for the already-verified patch — the account holder can apply it directly.
(3) The account-holder actions (identify the one registration, read its submission
history, confirm eligibility, approve the §3.2 disclosure). (4) No GPU and no licensed
1 m DEM were provisioned, so the levers that would most improve *geological*
credibility (scarp morphology, contact continuity) are still unavailable.

**First next session:**
1. Read this file. Re-check the canonical account/entry state, including whether
   `LEARNGEMSDOE` was deliberate and whether the entry's "eleven repositories" prose
   has been corrected.
2. **Freeze full88 + spacing4 + 3% at the shipping budget as the working hypothesis**
   (this session's evidence), and treat drop2 as a wash. The remaining local lever
   that does not need a GPU: a *nested* spatial check — select the spacing/budget on
   one half of the region and score it on the other, so the tuning is not scored on
   the geography it was tuned on. Session 4 flagged exactly this and it is still open.
3. Decide the slot-1 question explicitly with the account holder. The honest framing
   is now stronger than session 4's: the shipped policy is measurably *below* a
   matched-budget random control on held-out geography, so spending one weekly slot to
   measure a spaced candidate on the hidden board is a measurement, not a contention.
4. Keep the candidate's bytes out of Git and out of any site until the registration,
   allowance and AI disclosure are verified; then land the entry patch and the
   candidate's own dossier together, never the candidate alone.

### Reproduction (entry data and feature stack required; ignored, not committed)

```bash
python3 -m venv ../venv && ../venv/bin/pip install numpy scipy rasterio scikit-learn pytest
git clone --depth 1 https://github.com/buffedlizard55-lab/6GEMSDOE.git ../entry-src
cd ../entry-src && ../venv/bin/python scripts/fetch_and_verify_data.py
../venv/bin/python scripts/build_rank_tables.py
../venv/bin/python scripts/build_features.py --tile-rows 512      # ~18 min on 2 CPUs
cd ../SelfLearn
OMP_NUM_THREADS=2 ../venv/bin/python gemsdoe_review/tools/shipping_budget_confirmation.py \
    --entry ../entry-src --scratch /tmp/session5 --configs raw19 full88 drop2 \
    --max-neg 400000 --iters 300 --seed 7
../venv/bin/python gemsdoe_review/tools/build_spaced_candidate.py \
    --entry ../entry-src --scratch /tmp/session5 --tag spacing4-topk03
cp ../entry-src/scripts/geology_dossier.py ../entry-src/scripts/_gd.py   # REPO_ROOT must be the entry
GEMSDOE_ENTRY_ROOT=../entry-src ../venv/bin/python -m pytest gemsdoe_review/tests -q
```
