# GEMSDOE review — 2026-09-26

Review of the GEMSDOE-family repositories and the live entry sites, run against the
seven items in the brief. Everything below is either a measurement made in this
sandbox against the official rasters, or a quote from an official source with the
link. Section 8 lists what is *not* verified.

Repository state: `buffedlizard55-lab/6GEMSDOE` @ `d67dd19` (2026-09-25) is treated as the
canonical entry (its own `ACCOUNT_STATUS.md` designates it as the single entry and
site). Working data: the official rasters, reassembled from the repository's own
bridge and hash-verified against the pins in `src/gems/spec.py` (all three match).

---

## 0. Headline

**The submission strategy is aimed at the wrong population, and the entry's own
best-scoring artifact already points at the better one.**

Under the competition's published rule — verified from DrivenData staff posts this
session — the pixels of the supplied catalogue are *masked out of evaluation*, and
"a predicted pixel that is near a known fault trace but far from a new-fault ground
truth pixel will be fully penalized". The newest entry artifact
(`gems6_hgb88-topk03_33cec71ff0.tif`, 155,021 px, of which 23,605 sit on the
catalogue) scores **0.0348** against the only local new-fault-like population
available. The older artifact `ens12-adopted-floor0.1-w0/submission.tif`
(172,974 px, 6,455 on the catalogue) scores **0.1014** on the same population —
roughly **3× better with a comparable pixel budget**. Both are beaten by a
predict-everything baseline (0.0592). Numbers, method and caveats: §4.

---

## 1. Feature engineering against the research priorities

The brief's priorities are already implemented in `src/gems/features.py`
(`build_feature_stack`), and the implementation is sound in structure: HGM, tilt,
analytic signal and MGD on the magnetic and gravity layers; total/profile/plan/
Gaussian curvature plus slope-of-slope on the detrended DEM; structure-tensor
lineaments on elevation/TMI/gravity/conductivity at three scales; and explicit
products between the strain, conductivity/basement and seismicity layers. Three
findings from measuring the built stack:

1. **The magnetic tilt derivative is a dead channel.** `mag_tilt =
   atan2(tmi_vg, |tmi_hg|)` never leaves ±3.1° (p99 of |TDR| over the whole
   footprint), because the supplied `tmi_vg` is ~256× smaller than `tmi_hg`
   (median |·| 0.0090 vs 13.15). The ±45° contours the tilt-depth method needs
   occur in **2.2 × 10⁻⁵** of pixels. The "tilt derivative on magnetic layers"
   priority is therefore *claimed but not delivered*.
2. **`mag_asa` is an exact duplicate of `tmi_hg`.** `sqrt(hg²+vg²)` with
   `vg ≈ 0` gives Pearson r = 1.000000 against the already-present band. One of the
   88 channels carries no new information.
3. **The gravity equivalents are fine**, and that is what makes the first two a bug
   rather than a data limitation: `iso_grav_anom_vg` is the same order as its
   horizontal counterpart, so `grav_asa` and `grav_tilt` are genuine, independent
   channels (p99 |grav_tilt| = 88.8°).

Measured in `evidence/tilt_derivative_audit.json`; the audit script also builds a
Fourier `|k|` vertical derivative from the RTP grid as a candidate replacement. It
produces a realistic TDR (37% of pixels beyond ±45°) but is **not validated**: it
does not separate mapped faults better than the provided `tmi_hg`. It is recorded
as an open lead, not a fix. (The first version of that construction omitted the
per-metre scaling and was wrong by a factor of 100 — kept in the script as a
comment because the mistake is easy to repeat.)

Cross-referencing strain rate, conductivity anomalies and earthquake density is
implemented as three products plus the raw bands. The dossier in §6 shows the
consequence: the *large* flagged structures are almost entirely strain/seismicity
objects, while the magnetic-edge evidence is concentrated in the small, isolated
ones.

## 2. Cross-validation is spatially blocked and buffered

**Confirmed, and not by inspection alone.** `src/gems/cv.py::make_folds` builds
`n_blocks × n_blocks` rectangular blocks, deals them to folds in a strided pattern,
and `train_test_masks` excludes both the held-out blocks and a `buffer_px` dilation
around them from *training*, while scoring only the held-out blocks. The default
buffer is 3 px = 300 m = one full kernel support, and the docstring records that an
earlier revision defaulted to 300 *(pixels)* — a units bug that would have held out
30 km — with a test pinning the corrected default. `tests/test_spec_and_cv.py`
exercises the geometry. There is no random pixel split anywhere in the training
path; the only `permutation` call in the repository is the reference solution's,
quoted in the module docstring as the leak the design avoids.

## 3. Metric-aware placement

**Intact, and the "4–5 px spacing" hypothesis is answered in the code and settled by
the entry's own experiment.** `src/gems/placement.py` derives the break-even
posterior `q* = α(1−k)/(k(1+β) + α(1−k))` (q* = 0.0526 at d = 1 px), implements
Zhang–Suen thinning, densification, and the budget selectors (`topk_hard@frac`,
`topk_soft@frac`), and the shipped strategy is `topk_hard@0.03` with `p → 1.0` —
correct, because `DTI = TP_w/(β·n_gt + α·FP_w + (1−β)·TP_w)` is strictly increasing
under p → λp, so fractional probabilities give away score.

The GEMSDOE3 line tested the spacing question directly (`configs/pindrop-v4.json`,
published 2026-09-25T15:24Z): at a fixed emitted-pixel budget, a node schedule
spaced at the kernel's Nyquist limit loses nothing on the audit fold, because a
second prediction 4 px along the same trace adds no TP_w credit but still pays its
own FP weight. That is the opposite conclusion from `placement.py`'s docstring
argument (which considers densifying a *true* line, where densification genuinely
helps). Both are right about different things: densification helps only if the
probability field is right on the line; with a mis-centred or noisy ridge, the
spacer's FP saving dominates. **This is the open disagreement to close with a
measurement on the masked proxy, not with prose.**

## 4. The submission generator — and the scoring rule that changes what it should emit

**Format gates: re-verified, all pass.** `evidence/masked_proxy_eval.json` was
produced after re-reading the shipped raster from its bytes; `tools/check_entry_docs.py`
re-runs the 13-check gate on
`downloads/gems6_hgb88-topk03_33cec71ff0.tif` and re-verifies the pinned sha256 of
all three official rasters (all match), the submission report's hash/size/channel
count, `finite_pixels == FOOTPRINT_PIXELS (5,167,373)`, zero NaN inside the
footprint, values in [0, 1], and the 155,021 positive pixels.

**The rule.** Quoted verbatim in `evidence/scoring_rule_clarification.json` from
DrivenData staff (forum topic 11516, posts 2 and 4,
<https://community.drivendata.org/t/11516>):

- "Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded from
  evaluation, so they do not count towards penalty terms."
- "The mask is indeed pixel-exact - it is identical to the provided set of training
  fault labels."
- "Only new-fault ground truth is considered for scoring purposes. A predicted pixel
  that is near a known fault trace but far from a new-fault ground truth pixel will
  be fully penalized, i.e., the buffer does not apply to known faults."
- "A new-fault ground truth pixel can indeed lie within 300m of a known fault trace.
  Such pixels would constitute corrections or modifications to existing fault
  traces."

The entry's own new-fault proxy evaluation (`GEMSDOE/scripts/eval_proxy_catalogue.py`,
generated 2026-09-17) predates these posts and implements the **unmasked** metric.
`tools/masked_proxy_eval.py` implements the rule-correct one and runs both side by
side. Results on the SGMC new-fault-like population (61,664 px, all > 300 m from any
training label):

| candidate | emitted px | on catalogue | unmasked DTI | **MASKED DTI** |
| --- | --- | --- | --- | --- |
| `ens12-adopted-floor0.1-w0/submission.tif` (GEMSDOE, 7f00890a…) | 172,974 | 6,455 | 0.0999 | **0.1014** |
| `riftline-context-distance…7b6010637a.tif` (GEMSDOE3) | 352,506 | 13,386 | 0.1303 | 0.1333 |
| `local-sandbox-smoke/submission.tif` (GEMSDOE) | 207,906 | 2,313 | 0.0864 | 0.0868 |
| `35042805806/submission.tif` (GEMSDOE, the 21,492 px policy) | 21,492 | 2,593 | 0.0247 | 0.0249 |
| **`gems6_hgb88-topk03_33cec71ff0.tif` (6GEMSDOE, shipped)** | 155,021 | 23,605 | 0.0327 | **0.0348** |
| same, dilated 3 px | 439,759 | — | 0.0474 | 0.0503 |
| blanket 1.0 inside the footprint *(baseline)* | 5,167,373 | 60,988 | 0.0585 | 0.0592 |
| catalogue copy *(baseline)* | 60,988 | 60,988 | 0.0000 | 0.0000 |

Reading the table:

- **The mask rule *raises* every score** (it deletes mass that the unmasked metric
  charges for). It does not change the ranking, and it does not rescue the newest
  artifact: 6GEMSDOE's file remains ~3× worse than GEMSDOE's `ens12` on the only
  independent new-fault-like population we have, with a comparable budget.
- **Catalogue copy scores 0.0000**, which is the identity the entry already asserts:
  the new-fault-like population is disjoint from the catalogue by construction. It
  also means covering the catalogue is *free but worthless* — the right response is
  to stop spending the budget there, which is what the 23,605 on-catalogue pixels of
  the shipped file are doing (15.2% of its mass; `ens12` spends 3.7%).
- **Dilating the shipped file helps on this population (+45%)**, consistent with the
  entry's own crossover analysis (`GEMSDOE/data/evidence/emission_decision.json`):
  the wider policy wins once the scored truth set is large. The crossovers are
  13,224 px for wide-vs-shipped and 61,072 px for blanket-vs-shipped. The SGMC proxy
  has 61,664 px of truth and therefore sits at the *wide* end; the real new-fault
  set is unknown and probably smaller, which is exactly why the crossover table, not
  the proxy score alone, has to drive the decision.
- **GEMSDOE3's high proxy scores are circular and must not be used to select it.**
  `configs/pindrop-v4.json` sets `positives: ["known", "sgmc"]` — those arms *train*
  on the SGMC catalogue — and `gapfinder-v2-sgmc-gap` is simply the proxy
  rasterised — its 61,664 px equal `proxy_only_px` exactly, and it scores 1.0000 on
  itself. The table is included for
  completeness with this warning attached; the non-circular comparisons are the ones
  between artifacts that never saw SGMC.

**Recommendation.** Before the next upload, choose between `ens12` and the 6GEMSDOE
file on the masked-proxy evidence, and prefer `ens12` unless a larger evaluation says
otherwise. Do not upload any SGMC-derived artifact expecting the proxy score to
transfer.

## 5. Executive summary / "how to submit" accuracy

`tools/check_entry_docs.py` re-reads every claim it can from the artifacts rather
than from the prose. Current state: **36 of 37 checks pass.** The failure is real
and is the one the brief's item-4 wording is about:

- `limitations-cover-masking` — `LIMITATIONS.md` does not mention the pixel-exact
  catalogue mask or the "no buffer for known faults" rule, so the entry's stated
  limitations still describe the pre-clarification metric. Fix the text (the
  verified quotes are in `evidence/scoring_rule_clarification.json`).
- The tool also asserts that none of the five scores the brief attributes to this
  account's repositories (0.1563, 0.1560, 0.1193, 0.1152, 0.0830) appears in the
  entry's own prose as ours. All five currently pass. On the public board those five numbers appear under five
  *different* participant names, each with exactly one submission (see
  `evidence/leaderboard_snapshot.json`) — so nothing in this account's own evidence
  supports calling any of them ours, and the entry must not adopt them.

One correction to the brief: the leaderboard shows participant handles, not
repository names, so it cannot by itself tell us which rows are ours — but nothing
we can read links the five numbers in the brief to this account. The field high on the public board is 0.3049 (DARD); the
organizers' own account sits at 0.1847. Our 0.1563 is not on the board under any
name we control, and no site in the family reports a score (GEMSDOE3's says
"Unknown").

## 6. Geological reasoning for every flagged candidate

This did not exist before; it does now.

- `tools/geology_dossier.py` measures each connected group of predicted pixels at
  ≥ 200 px: geometry (area, principal axes, strike, elongation), 21 diagnostics
  expressed as percentiles of the whole scored footprint with the fault-favourable
  direction of each stated, agreement across six independent physical families,
  distance to the mapped catalogue, and the local metric value of those pixels.
- `evidence/geology_dossier.md` renders that with **hand-written readings** for the
  ten most informative candidates, each naming the measurements it rests on, the
  measured discordance from the local mapped trend, and an explicit confidence.
- Headline findings: of 193 candidates on `ens12`, **64% are "extension" and 35%
  "isolated"** — i.e. the emission is *mostly* not hugging the catalogue, and a
  third of it is in unmapped ground. The largest candidates are strain/seismicity
  objects with no potential-field expression (candidate 2: 120 km², second invariant
  above the 99.7th percentile, shear rate above the 99.9th, zero magnetic or gravity
  families, 86° discordant from the local mapped trend — a deforming volume, not a
  fault). The best fault candidates are the small isolated ones:
  candidate 131 (11.1 × 3.8 km at 38.654°N 118.554°W) is conductive (96th
  percentile), dilatant (98th), seismically active (96th) and magnetically quiet —
  the classic hydrothermal-alteration signature; candidate 179 (3.0 × 1.3 km,
  nothing mapped within 1.77 km) is the most plausible *new* structure in the file.
- **A depth estimate is not offered, deliberately.** The ±45° tilt contours the
  method needs do not exist in the supplied bands (§1). A number here would be
  invented; the dossier says so with the measurement attached.

## 7. Where we sit against the field, and ownership

- **Ownership: resolved, in the direction that matters.** All 14 repositories under
  `buffedlizard55-lab` (11 competition-named plus SelfLearn/MasterSelfLearn/MasterSite)
  are owned by one account, none is a fork, and Pages is enabled on every one of
  them (`evidence/ownership_audit.json`). Commit authors across the family are arena
  agent identities (`agent@arena.ai`, `agent@arena.local`, `agent@5gemsdoe.local`,
  `arena-ai-coding-agent[bot]`) plus the owner — i.e. these are prior arena sessions
  of the *same* entry, not another entrant's work. `6GEMSDOE` is the designated
  canonical repo/site. The live-site rule is nonetheless violated in *form*: eleven
  competition-named sites exist. Remediation is to archive the duplicates after
  relocating the data path (the bridge lives in `GEMSDOE`), which is a human action.
- **Where we sit:** no leaderboard-verified score. The only local numbers are
  proxies, and the strongest of them (0.1698 blocked-CV on the catalogue) is measured
  on the population the competition masks. Against the new-fault-like population the
  honest figure for the shipped file is 0.0348 and for `ens12` 0.1014 — both well
  below what a field that scores 0.30 on the real metric is presumably doing. The
  gap is not tuning; it is that the model is trained to reproduce the catalogue and
  is then scored on faults the catalogue does not contain.
- **Blocking (human-only):** DrivenData credentials/registration, eligibility §1.3,
  the state of the weekly 3-submission allowance, and which artifacts have already
  been uploaded. The sandbox cannot read the leaderboard, cannot reach the 1 m DEM
  (3DEP egress blocked), and has no write access to `6GEMSDOE` (HTTP 403) — so any
  code change must be applied by a human or from a session with push rights.

## 8. What is *not* verified

- **The SGMC proxy is not the scored set.** SGMC faults were mapped by state
  geologists from surface geology; the competition's are expert identifications from
  GeoDAWN geophysics. The entry's own docstring says to use it to compare policies,
  never to predict a leaderboard position, and that instruction is followed here.
- **The `ens12` score is selection-biased.** Its shaping policy was chosen from ~32
  policies evaluated on the same proxy, so 0.1014 is optimistic for that file.
  6GEMSDOE's 0.0348 carries no such bias (it never saw the proxy) — which makes the
  comparison conservative in the direction of the recommendation, not against it.
- **The Phase-2 rule is quoted but not modelled.** Staff state (topic 11527 post 7)
  that the Phase-2 test set "is updated by expert review of all Phase 1 submissions".
  No local evaluation can price that, and no claim here depends on it.
- **The gate checks are re-run, not re-derived**: they verify the file the repo
  already ships, they do not re-train it.

## 9. If I had one more session

1. Close the mask rule in the entry's own words: patch `LIMITATIONS.md`, re-run
   `tools/check_entry_docs.py` to 37/37.
2. Re-run `tools/masked_proxy_eval.py` over the full artifact inventory **including
   the GEMSDOE3 arms restricted to their audit fold only**, which is the only way to
   use those candidates without circularity.
3. Replace the dead magnetic tilt channel (`mag_tilt`) and the duplicate `mag_asa`,
   and re-measure on the masked proxy with the blocked CV untouched — a 2-channel
   change that costs one retrain.
4. Decide `ens12` vs 6GEMSDOE's file on that evidence, then upload.

---

Artifacts and provenance: `evidence/` (all measurements, with the tool that made
each one named inside the file) and `tools/` (the five scripts, each of which prints
what it measured and states what it does not). The two scripts that belong in the
entry repository rather than here (`geology_dossier.py`, `geology_report.py`, plus
`tilt_derivative_audit.py`) are written against its `src/gems` API and paths and can
be copied into `scripts/` unchanged.
