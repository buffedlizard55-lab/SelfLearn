# Session 4 — spatial validation repair and a measured placement improvement

2026-09-26 · review workspace `buffedlizard55-lab/SelfLearn` · designated entry
[`buffedlizard55-lab/6GEMSDOE`](https://github.com/buffedlizard55-lab/6GEMSDOE)

**Read this before the historical REVIEW.md.** Its last handoff was read before
work, then the designated entry's `NEXT_STEPS.md` was read from source revision
[`e2fe3f4`](https://github.com/buffedlizard55-lab/6GEMSDOE/commit/e2fe3f41c6f5dd2dcb2fc91958ee67698f114ada).
No account, repository, site, submission, or replacement submission TIFF was
created. Source/data/feature caches are ignored, not delivered as another entry.

## Executive result

There is a **promising local score-quality improvement**, not a new public score:
**88 features + genuine 4-pixel node spacing** beats the dense policy and
matched-budget no-signal controls on every tested geographic fold. The previous
whole-system experiment was not clean spatial CV; its decisive “28× loss / no
skill on unseen systems” interpretation is withdrawn, not silently carried forward.
The shipped file is unchanged and **no promotion/upload is approved here**.

| 3% budget policy | Raw 19 bands | Engineered 88 | Drop magnetic tilt + ASA | Label-blind control |
|---|---:|---:|---:|---:|
| Dense top-k | 0.0597 | 0.0935 | 0.0947 | 0.1722 |
| **4-pixel minimum spacing** | **0.2258** | **0.2436** | **0.2439** | **0.2037** |
| 5-pixel minimum spacing* | 0.2054 | 0.2105 | 0.2120 | 0.1904 |

Unweighted means over four geographic folds; control averages three frozen seeds
within each fold. These numbers describe a **catalogue-fault transfer proxy**,
not the competition's new expert faults, and cannot be compared numerically with
0.3049 on the public board. *Spacing 5 underfills the requested budget differently
for different probability orders; it is **not** an equal-actual-budget comparison.
The full-blanket control is only 0.0614: passing that weak control alone would
badly overstate model skill under sparse placement.

Evidence: [model folds](evidence/spatial_system_ablation_session4.json),
[null controls](evidence/spatial_controls_session4.json),
[comparison with per-fold gates and actual counts](evidence/spatial_comparison_session4.json).

## Pass 1 — implementation and measurements

### 0. Account/repository guardrail and ownership, checked first

The one **designated** entry is 6GEMSDOE. **One DrivenData account is NOT verified**:
there is no authenticated DrivenData session or account-history evidence here.
Eligibility, existing submissions, weekly allowance, and final selection remain
unknown. Local research is not authorization to upload. No credentials requested.

Fresh GitHub REST evidence resolves all three “unconfirmed” websites:

| Site/repository | Verified GitHub ownership | Operational treatment |
|---|---|---|
| [5GEMSDOE](https://github.com/buffedlizard55-lab/5GEMSDOE) | `buffedlizard55-lab`, owner id 309556078, non-fork | Historical project copy; not an independent entrant/experiment |
| [GEMSDOE4](https://github.com/buffedlizard55-lab/GEMSDOE4) | Same owner/id, non-fork | Historical project copy; not an independent entrant/experiment |
| [6GEMSDOE](https://github.com/buffedlizard55-lab/6GEMSDOE) | Same owner/id, non-fork | Single designated competition entry |

This establishes GitHub ownership, **not** the owner of any DrivenData registration.
`SelfLearn` is the existing review workspace, not a newly created competition repo.
The API exposes no push permission on 6GEMSDOE; its revision remains `e2fe3f4`.
The previous handoff's entry patch could therefore be applied/rechecked **only in
an ignored source archive**, not merged into the live entry. The session is fixed
to its existing SelfLearn branch. Reconnect GitHub in Arena with permission to the
existing entry for a future authorized deployment. API permission booleans alone
are imperfect: SelfLearn's git push dry-run succeeds even though REST push=false.

All six supplied reference URLs were visited via `fetch_page`. Multiple historical
sites remain live and advertise conflicting upload instructions. **“One live site”
is not literally true of the hosting account.** That is an operational irregularity,
not evidence of multiple DrivenData accounts or a proven rules violation.

[Live ownership/site/source audit](evidence/live_audit_session4.json).

### 1. Feature engineering against the priorities

Rebuilt the 105-channel cache from all three hash-verified official rasters; the
models use the named first 19/88 or 86 channels, not all 105. Re-ran the band audit:
[feature measurements](evidence/feature_priorities_session4.json).

- **Magnetics/gravity HGM and tilt:** the engineered stack includes multiscale
  horizontal-gradient magnitude, matched-scale tilt/analytic signal and lineament
  context. The supplied magnetic tilt still has |angle| p99 ≈ **3.08°**; magnetic
  ASA duplicates |TMI horizontal gradient| (r ≈ **1.0**). Recomputed smoothed
  magnetic tilt is angle-active but catalogue AUC ≈ **0.50**. Gravity tilt is
  active but weak/anti-separated (AUC ≈ **0.484**). **No calibrated depth claim**
  follows from these channels. Removing the two magnetic channels gives a tiny,
  mixed-fold change (spacing-4 mean +0.000316), not a reason to change the model.
- **DEM curvature / slope breaks:** multiscale curvature and slope-of-slope are
  present; slope-of-slope at sigma 3 remains weakly informative (AUC ≈ **0.598**).
  This uses the **100 m detrended elevation**, not newly acquired 1 m lidar.
- **Strain / conductivity / earthquake cross-reference:** strain and seismicity
  are not independent confirmations (catalogue Spearman ≈ **0.77**); conductivity
  has weak separation and the measured direction must be respected. Do not count
  correlated layers as independent geological proof.
- **New controlled comparison:** with identical training samples/seeds, adding the
  engineered features improves spacing-4 mean from **0.2258 to 0.2436**, with gains
  in every fold. This supports the stack **as a bundle**; it does not identify
  each feature family as causal or establish unseen expert-fault performance.

Official feature/metric source:
[DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
Descriptive AUC sampling is not CV and is never reported as a validation score.

### 2. Spatial CV — substantive defects found and repaired

The old `system_holdout_cv.py` did not satisfy the requested isolation:

1. `ys[::4], xs[::4], ids[::4]` sampled **global raster order**, dropping small
   traces and linking endpoints. Exact all-pixel linkage at 5 km gives **40**
   systems, not **317**. A singleton-bridge regression and independent all-pairs
   reachability oracle demonstrate the problem without relying on model scores.
2. It sampled negatives from `~gt & footprint`, then scored the whole footprint:
   training negatives were in the evaluation geography. Removing held positive
   labels alone is **not** buffered spatial CV.
3. Its pseudo-label pass trained in scoring geography and could include the same
   location again as a negative. That result cannot establish spatial generalization.

The old CLI now fails closed with a pointer to `spatial_system_cv.py`; historical
functions and numerical evidence remain for audit, with explicit validity warnings.
Do not interpret the historical 0.0060/0.0148 ratio or GT-mix decomposition as a
clean CV conclusion. The earlier **catalogue-axis** shipping ablations are a
separate design and are not invalidated by this specific defect.

**Replacement design:** four geographic quadrants; test pixels assigned by blocks,
never a random pixel split; Euclidean exclusion at least 3 px/300 m; **every system
intersecting a test quadrant is removed globally from training**, with its own
buffer. Both positives **and negatives** obey the train mask. No pseudo-labels.
Scores and prediction budgets use only the held quadrant/valid footprint.
Random subsampling occurs only inside the already-isolated training negatives.

All four folds have zero train/test overlap, zero train pixels within 300 m of
test, and zero shared positive systems. Per-fold mask hashes and counts:
[geometry audit](evidence/spatial_system_geometry_session4.json).
Models: HGB, 100 iterations, up to 50k negatives, seed 7 + fold; same samples for
all three feature configurations. This is **reduced budget**, not the shipped
400k/300 configuration. Test-touching systems can recur across quadrants: fold
scores are not four independent system replicates. Boundary metric contributions
are clipped consistently. Unlabeled feature context is transductive; future CNN
input windows require an exclusion margin covering their receptive field too.

Separately, the canonical entry's existing blocked CV still has the known
Manhattan-vs-Euclidean diagonal bug on some layouts. The previous superset patch
fixes it in scratch; [independent audit](evidence/patched_entry_cv_session4.json)
finds zero misses on all 4/4, 6/6, 5/3 and 6/4 layouts. **Not deployed live.**

### 3. Metric-aware placement — not “intact” as a shipped 4–5 px rule

The actual shipped `topk_hard@0.03` file is **dense**; its generator does not use
4–5-pixel nodes. Its old `thin_keep` helper takes every nth skeleton pixel in
raster order, which does not guarantee geometric spacing. GEMSDOE3's node
portfolio is not the canonical entry and must not be conflated with it.

The new diagnostic `budget_nodes` implements probability-ordered suppression:
spacing 4/5 means **minimum Chebyshev separation**, with deterministic tie-breaking
and an explicit maximum budget. This is not guaranteed maximum along-trace spacing
or free preservation of triangular-kernel credit. Dense and spacing 4 each emit
exactly **155,021 pixels across the four folds**. Spacing 5 underfills.

Full88 spacing 4 beats every frozen null seed in every fold; its per-fold DTI is
0.2345 / 0.2408 / 0.2680 / 0.2309 versus null means
0.2014 / 0.1837 / 0.2269 / 0.2029. This is a more credible improvement than
comparing only with full blanket. Dense full88 loses to the matched-budget random
control in every fold. No prediction raster or upload was generated from the CV.

### 4. Submission format and generator path

Canonical artifact SHA-256 remains
`33cec71ff00b3f32d0d59c81c156f3f1488ffef46baa4b6499094e24ea1875ab`.
[Fresh gate](evidence/submission_gate_session4.json): **13/13 PASS** — single band,
float32, EPSG:32611, 100 m, **3730 × 3292**, transform
`(100, 0, 243350, 0, -100, 4508550)`, NaN nodata, finite [0,1], no infinities,
pinned template, **0 inside-NaNs**, **0 finite outside**.

A one-pixel in-footprint NaN poison file passes the finite-value range check but
**fails NAN-INSIDE-FOOTPRINT with CLI exit 1**:
[negative-test evidence](evidence/nan_poison_session4.json). It is ignored scratch,
not a submission candidate. The entry's writer roundtrip/nonfinite-refusal tests
pass. **Full shipping-model retraining / byte-identical generator reproduction was
not repeated this session**; do not relabel the earlier reproduction as new work.
Direct sandbox HTTP to Pages failed TLS, so the gate checks the canonical source
archive's TIFF; the tool-read live page advertises that same name/hash prefix.

### 5. Executive summary / how to submit

**The live page is not fully accurate.** It still puts download/upload ahead of
account confirmation and claims hardening probabilities independently must help.
That mathematical statement is false: adding weight to a remote FP can lower DTI.
The uniform-rescaling identity is a different claim. Its catalogue proxy is not a
hidden-score estimate, and its “known-good” next steps lag completed experiments.

Applied the existing recommended
`patches/session3_entry_full_2026-09-26.patch` **only to scratch**. The canonical
pre-patch offline doc checker is **35/37** (missing mask discussion and candidate
dossier); scratch after patch is **37/37 offline, 50/50 online**. These are
mechanical checks, not verification of account eligibility or geological truth.
The entry main/site did not change. The new session-4 findings must also be folded
into entry documentation before any revised candidate is offered.

### 6. Geological reasoning, not merely a mask

No new candidate fault map was generated. Re-rendered the existing, byte-pinned
[current shipped dossier](evidence/current_shipped_geology_2026-09-26.md)
**byte-identically** and verified its fragment-inventory hash. It gives the
hypothesis, actual supporting bands, counterinterpretation and follow-up for all
**180 large groups**. There are also **2,409 uninterpreted small components**
(26,040 emitted pixels) plus 93 emitted pixels lost by closing; do not call these
confirmed or individually interpreted faults.

For example, S-001 has high strain and earthquake-density summaries but is broad
(minor PCA axis 8.6 km) and near mapped traces. A splay/correction is possible;
a mapped-fault halo is also plausible. Correlated strain/seismicity is not two
independent confirmations. Scarps/contact continuity at 1 m resolution and expert
review are needed; depth is unestimated. The dossier avoids invented formation
names, fault styles and verified discoveries. Any eventual **new** artifact needs
its **own hash-bound dossier**, not recycled component ranks.

### 7. Field context and ownership/score attribution

The [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
still shows **DARD 0.3049** and the organizer row **0.1847**. The brief's five
numbers are attached to **extradr19 0.1563, smashi34 0.1560, smrtdoog5 0.1193,
SDCF9 0.1152, wbg1 0.0830**. No evidence connects those accounts to this entry.
GEMSDOE2's live text still calls 0.1563 “the recall-union's board score”; that
attribution is **unsubstantiated**, not something to repeat as our history.
Different fetched chunks show inconsistent rank context; do not infer rank changes.

We have **no verified owned public score or defensible field rank**. The new local
lift makes a locked spacing-4 policy worth further testing, not a claim that we
sit near 0.2436 on the leaderboard. Several reference sites still promote other
files; keep them read-only history, not multiple experiment accounts.

## Pass 2 — bugs, gaps and regression review

- Added exact-clustering oracles (including missed singleton bridges), spatial
  distance/buffer checks including diagonal corners, global system purge checks,
  deterministic budget/spacing/tie tests, empty/invalid input checks, test-area
  metric masking, retired-CLI refusal, and evidence/control-mask consistency.
- Added **label-blind matched-budget controls** when review showed blanket alone
  was insufficient. Three seeds are fixed, all reported; no seed selected by score.
- Detected spacing-5 underfill; report emitted counts and flag unequal actual budgets.
- Fixed another provenance bug: an extracted entry archive nested inside SelfLearn
  caused `git rev-parse HEAD` in the feature audit to inherit SelfLearn's commit.
  It now reports `null` unless the entry is itself the Git root. Source revision
  and patch are separately pinned in the [verification manifest](evidence/reverification_session4.json).
- Review tests **62 passed / 1 explicitly skipped** (unavailable historical alternate
  metric source); patched entry **47 passed**; SelfLearn **189 passed**. Initial
  entry tests were launched from the wrong cwd and failed to locate relative data;
  corrected cwd passed. A dedicated lightweight CI job now runs session-4 regressions
  without downloading competition data or changing the standard-library core jobs.

## Pass 3 — prompt/rules recheck

Official sources re-read:
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) §§1.3, 3.2, 3.4–3.6;
[format/metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/);
[staff pixel-exact mask clarification](https://community.drivendata.org/t/11516/4).

- Existing one designated entry only; no registration, upload or final selection.
  Weekly limit **three per entity** and **one final selection for both rounds**
  remain gates, not permission to use another account.
- Generative-AI involvement must be disclosed (§3.2); existing draft still needs
  account-holder approval. US eligibility and participation terms are not inferred
  from GitHub location/ownership.
- Staff mask applies to exact supplied labels, not a free 300 m corridor. The new
  CV holds out all systems touching the test quadrant: its test labels are proxy
  unknown faults, with no trained labels there. This is an analogue, not private GT.
- No new external dataset was incorporated. Licensed access and provenance must
  precede high-resolution DEM/external-label use.
- Proxy evidence cannot establish private/public performance; no claimed discovered
  faults, calibrated depths or prize competitiveness. Format validity is not skill.

## What changed / unverified / blocking / first next session

**Changed:** repaired spatial/system validation; retired unsafe diagnostic execution;
added genuine spacing controls, three feature configurations and matched-budget
nulls; measured a consistent spacing-4 + engineered-feature gain; added regression
CI and provenance guard; refreshed ownership, official-source and format evidence.
No change to the canonical submission/site. SelfLearn PR/merge outcome is reported
separately in the final session response (do not mistake it for an entry deployment).

**Still unverified:** DrivenData identity/eligibility/history/allowance; any owned
public score; real expert-fault generalization; shipping-scale reproducibility of
the new policy; independent geological confirmation; full generator retraining this
session; validity of historical alternative-site score claims.

**Blocking:** entry write/deployment permission and account evidence block publishing
or uploading there. No GPU/high-resolution DEM was provisioned. Local robustness
experiments remain possible without either; there is no need to wait to do research.

**First next session:**
1. Read this file, not the retired “only GPU can help / 28× collapse” conclusion.
   Recheck canonical account/entry state; land the already-reviewed entry CV/doc fix
   only in an authorized session on that existing repository, without making a site.
2. **Freeze full88 + spacing4 + 3% as the hypothesis**, not drop2 based on +0.0003.
   Run shipping-budget 400k/300 confirmation with the same exact-system isolation,
   matched-budget random controls and a pre-specified buffer/layout sensitivity.
   Use nested spatial selection or genuinely untouched licensed labels before
   calling a newly tuned policy independently validated; a different partition of
   these same observed labels is robustness evidence, not untouched ground truth.
3. If gains survive, implement it as an optional canonical generator policy, leaving
   the existing default artifact alone until approved. Generate one local candidate,
   hard-gate its bytes and write its own per-component geological dossier. No upload
   until the one existing registration, allowance and AI disclosure are verified.
4. Have the account holder resolve conflicting historical-site upload advice; do not
   infer multiple registrations or treat another entrant's score as a test arm.

### Reproduction (entry data/feature cache required; ignored, not committed)

```bash
# Existing canonical source snapshot; verify official pins, then build_rank_tables.py
# and build_features.py --tile-rows 128 in that source directory first.
ENTRY=/path/to/existing/6GEMSDOE-source
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python gemsdoe_review/tools/spatial_system_cv.py \
  --entry "$ENTRY" --out /scratch/models.json
python gemsdoe_review/tools/spatial_system_cv.py --entry "$ENTRY" --audit-only \
  --out /scratch/geometry.json
python gemsdoe_review/tools/spatial_controls.py --entry "$ENTRY" \
  --geometry /scratch/geometry.json --out /scratch/controls.json
python gemsdoe_review/tools/summarize_spatial_cv.py --experiment /scratch/models.json \
  --controls /scratch/controls.json --out /scratch/comparison.json
GEMSDOE_ENTRY_ROOT="$ENTRY" python -m pytest gemsdoe_review/tests -q
```
