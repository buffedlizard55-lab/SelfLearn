# GEMSDOE review — 2026-09-26

Review of `buffedlizard55-lab/6GEMSDOE` (the designated single entry) and the rest of
the GEMS repository family, against the seven items in the brief. Everything below is
either a command that was run in this session, quoted from an official source, or
explicitly labelled as not verified.

## 0. Headline

1. **The scoring rule was wrong in the brief, and the correct one is now recorded and
   implemented.** A staff post on 2026-09-20 (`community.drivendata.org/t/11516`, post
   4) states that the catalogue mask is *"pixel-exact — it is identical to the
   provided set of training fault labels"*, that a prediction near a known fault but
   far from new-fault truth is *"fully penalized"*, and that new-fault truth pixels
   *"can indeed lie within 300 m of a known fault trace"* because corrections are a
   target. This session fetched the thread, quoted it verbatim in
   `evidence/scoring_rule_clarification.json`, and implemented it in
   `tools/masked_proxy_eval.py`. Measured effect on the shipped file: **+0.0021 DTI**
   — the rule is real but it is not the lever. (Earlier framing in this session's own
   notes over-weighted it; the measurement corrected that.)
2. **The lever is the emission, not the mask — and the shipped emission is the weak
   point on the only new-fault population we can measure.** On 61,664 px of USGS SGMC
   faults absent from the training labels, the shipped file scores **0.0348** while the
   older `GEMSDOE` artifact `ens12-adopted-floor0.1-w0` scores **0.1014** at a
   comparable budget. Dilating the shipped file by 6 px lifts it to 0.0599 — still
   below `ens12`, and still only level with a *predict-everything* baseline (0.0585).
   An independent 4-fold blocked CV confirms the mechanism: a freshly trained model
   gains **+21%** from a 3-px dilation at a 3% budget, and the 5% budget beats 3% in
   every fold (§2). Caveats are strong and are given in §6; this is the finding that
   should drive the next submission decision.
3. **Feature priority #1 is implemented but one third of it is dead code.**
   `mag_asa` is numerically identical to the provided `tmi_hg` (r = 1.000000) and
   `mag_tilt` is a dead channel — |TDR| never exceeds 3.1° for 99.9% of the grid,
   because the supplied `tmi_vg` is ~256× smaller than `tmi_hg`. The gravity twins of
   both features are fine, which makes this a units/scaling defect rather than a data
   limitation. `evidence/tilt_derivative_audit.json`; the fix is measured and does not
   transfer on its own (§2).
4. **The brief's five "our" scores belong to other people.** `0.1563` is rank 22
   (`extradr19`, one submission), `0.1560` is rank 23 (`smashi34`), and
   `0.1193 / 0.1152 / 0.0830` are ranks 39/40/49 (`smrtdoog5`, `SDCF9`, `wbg1`). Two
   of the three "GEMSDOE3" numbers exist in that repository only as scalar DTI values
   inside a local cross-validation file, and its own `README.md` says
   *"Unscored. No upload has been made."* Full trace in
   `evidence/score_attribution.json`. Adopting any of these into the entry's narrative
   is exactly the "score contamination" its own `ACCOUNT_STATUS.md` names as an A.12
   exposure.
5. **Item 6 is now a real deliverable.** `tools/geology_dossier.py` +
   `tools/geology_report.py` produce a per-candidate dossier for every flagged
   structure (193 candidates on the `ens12` artifact — the file §6 favours — of which
   10 carry full hand-written readings),
   with explicit confidences, the measured discordance against the local mapped trend,
   and — deliberately — **no depth estimate**, because the supplied bands cannot
   support one.

Verified this session on the shipped file: format gate **13/13 PASS**, sha256
`33cec71ff0…`, all three official rasters re-hashed against the pins, `pytest` **44
passed**, blocked-CV harness numbers reproduced from `data/evidence/experiments*.json`.

---

## 1. Where the work stands (context for the findings)

| repository | role | state |
| --- | --- | --- |
| `6GEMSDOE` | **the designated single entry and single published site** | canonical; ships `gems6_hgb88-topk03_33cec71ff0.tif` |
| `GEMSDOE` | earlier session | full site + data bridge; holds the best non-leaky artifact on the new-fault population (`ens12-adopted-floor0.1-w0`) |
| `GEMSDOE2` | earlier session | full site; four-arm emission study |
| `GEMSDOE3` | earlier session | Pindrop portfolio (three files), plus the SGMC-trained arms |
| `GEMSDOE4`, `5GEMSDOE`, `7GEMSDOE`, `8GEMSDOE`, `GEMSDOE9`, `GEMSDOE10`, `11GEMSDOE` | duplicate copies and stubs | eleven published URLs for one challenge — flagged in §7 |

The entry's own `NEXT_STEPS.md` (read first, as instructed) puts accuracy work in the
order: P0 eligibility/duplication/allowance/narratives, P1 leaderboard-readout →
attack the actual target → 1 m DEM → reference architecture → per-candidate geology,
P2 reproducibility and tests. This review does the two P1 items the sandbox can do
(items 5 and 6 below), verifies the P2 claims, and leaves the rest where they belong.

## 2. Item 1 — feature engineering against the stated research priorities

The brief's priorities are implemented in `scripts/build_features.py` and audited in
`src/gems/features.py`. Mapping them to the actual channels of the shipped 88-column
stack:

| priority in the brief | channels | status |
| --- | --- | --- |
| horizontal gradient magnitude, magnetics | `tmi_hg`, `mag_asa`, `tmi_hgm_computed`, `hgm_tmi_s1.5/3/6`, `hgm_mag_anom_s*`, `hgm_rtp_s*` | present; **`mag_asa` duplicates `tmi_hg`** |
| horizontal gradient magnitude, gravity | `iso_grav_anom_hg`, `grav_asa`, `grav_hgm_computed`, `hgm_iso_grav_anom_s*` | present and non-redundant (the provided gravity `_hg` band is *not* the HGM of the provided gravity anomaly, r = 0.028) |
| tilt derivative, magnetics | `mag_tilt`, `tdr_tmi_s1.5`, `tdr_tmi_s3` | **dead**: p99 of \|TDR\| = 3.08° |
| tilt derivative, gravity | `grav_tilt`, `tdr_iso_grav_anom_s*` | present and alive (p99 \|TDR\| = 88.8°) |
| curvature and slope-break on the DEM | `curv_total/profile/plan/gaussian`, `slope_computed`, `slope_of_slope`, scale-explicit `_s1.5/_s3`, `det_elev_hgm_computed` | present |
| strain rate / conductivity / earthquake-density cross-referencing | `x_geod_shearrate__geod_dilaterate`, `x_cond_surf__depth_to_base_surf`, `x_ieq_n100a15__deq_n100a15` | present as three products, plus the raw bands |

**The measured defect.** `mag_tilt = atan2(tmi_vg, |tmi_hg|)` with `tmi_vg` a factor of
~256 smaller than `tmi_hg` (median |·| 0.0090 vs 13.15) is not a tilt angle: it is a
signed copy of `tmi_hg` scaled by a constant near zero. Consequences measured over
the whole footprint: \|TDR\| ≥ 45° in 2.2 × 10⁻⁵ of pixels, so the +45°/−45° contours
the tilt-depth method requires do not exist; and `mag_asa = sqrt(hg²+vg²)` collapses
onto `tmi_hg` with r = 1.000000, i.e. one of the 88 columns carries no information.

`tools/tilt_derivative_audit.py` also builds the physically correct replacement (a
Fourier |k| vertical derivative of the RTP grid with a raised-cosine low-pass) and
measures it. It produces a realistic TDR (37% of pixels beyond ±45°) **but it does not
separate mapped faults better than the provided `tmi_hg`**, so it is recorded as an
open lead, not as a fix. The first version of that construction omitted the per-metre
scaling and was wrong by a factor of 100; the script keeps the comment, because the
mistake is easy to repeat.

**Do the 40 extra channels pay?** Two independent measurements, both this session.

*On the catalogue* (the entry's own harness, identical folds): 0.1628 (48 ch) →
**0.1698** (88 ch) at the shipped hyperparameters, and 0.1729 → 0.1730 at the round-1
ones. `LIMITATIONS.md` §5 already says this honestly: *"on this 100 m grid the score is
limited by the label set, not by the number of derivative channels."*

*On the population that is scored* (new, `tools/experiment_proxy_cv.py`): train on the
catalogue as always, but score on held-out blocks of the SGMC new-fault population
instead. Four blocked folds, identical folds and hyperparameters for both stacks:

| policy | 48 ch | 88 ch | delta |
| --- | --- | --- | --- |
| `topk_hard@0.02` | 0.0483 | 0.0493 | +0.0010 |
| `topk_hard@0.02` dilated 3 px | 0.0652 | 0.0696 | +0.0044 |
| `topk_hard@0.03` (shipped policy) | 0.0569 | 0.0593 | +0.0024 |
| `topk_hard@0.03` dilated 1 px | 0.0623 | 0.0664 | +0.0041 |
| `topk_hard@0.03` dilated 3 px | 0.0681 | 0.0719 | +0.0038 |
| `topk_hard@0.05` | 0.0697 | 0.0737 | +0.0041 |
| `topk_hard@0.05` dilated 3 px | 0.0724 | 0.0774 | +0.0050 |

The 40 channels win on this population too, in every policy, by +0.001 to +0.005
(+2% to +9% relative). So they are worth keeping — my working suspicion that they were
bloat was wrong, and the measurement is what settled it. Two of the forty remain
degenerate (§2 above) and should still be repaired or dropped, which is a change that
can only help.

**What this table also shows, and it contradicts the site.** At a 2–3% budget, dilating
the emission by 3 px gains **+20%** (48 ch: 0.0569 → 0.0681; 88 ch: 0.0593 → 0.0719) on
the new-fault population — while `research.html` states, from a catalogue measurement,
that *"dilation loses"*. Both measurements are correct about their own population; only
one of them is about the population the competition scores. See §6.

## 3. Item 2 — cross-validation is spatially blocked and buffered

**Confirmed.** `src/gems/cv.py::make_folds` cuts the grid into `n_blocks × n_blocks`
rectangular blocks and deals them to folds in a strided pattern;
`train_test_masks` returns `(~dilate(test_block, buffer_px))` as the training mask and
the held-out blocks as the scored mask, so no training pixel lies within one kernel
support (3 px = 300 m, in pixels — the docstring records that an earlier revision
defaulted to 300 *pixels* and that a test pins the corrected default) of a scored
pixel. There is no random pixel split anywhere in the training path. `tests/` covers
the geometry. Verified by reading the module and by running the suite (44 passed).

## 4. Item 3 — metric-aware placement

**Intact, and the 4–5 px spacing question is answered with the metric.** The break-even
posterior at a one-pixel localisation error is `q* = α(1−k)/(k(1+β)+α(1−k)) = 5.26%`
in `src/gems/placement.py`; `topk_hard@frac` implements the budget selector, and the
shipped placement is `topk_hard@0.03` with `p → 1.0`, which is right for this metric
because DTI is strictly increasing under `p → λp` for λ ≤ 1 (the `β·n_gt` term does not
scale). The two families in this account disagree about spacing:

* `6GEMSDOE`'s `LIMITATIONS.md` §6 argues a 300 m kernel does not imply 4–5 px spacing;
* `GEMSDOE3`'s `configs/pindrop-v4.json` uses a node schedule at exactly that spacing
  and reports it wins the audit fold.

The disagreement is not resolvable by algebra, because it depends on the model's
localisation error. §6 measures both sides of it on the new-fault population and finds
that **width helps a badly localised emission and hurts a well localised one** — the
same surface, opposite conclusions, depending on the detector. The site's own claim
(*"Measured, dilation loses: the densified placement scored 0.0803 against 0.0879"*) is
therefore true on the catalogue and not true in general.

## 5. Item 4 — the submission generator and the format gate

**Re-verified end to end, in this session, on the shipped file:**

```
python scripts/validate_submission.py downloads/gems6_hgb88-topk03_33cec71ff0.tif
→ HARD GATE PASSED, 13/13
   crs-epsg32611 · resolution-100m · shape (3730, 3292) · geotransform
   (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0) · nodata nan · values [0,1]
   · no-inf · template-verified (footprint 5,167,373 px)
   · NAN-INSIDE-FOOTPRINT: 0 non-finite pixels inside the footprint
   · footprint-matches-official: 0 finite pixels outside it
```

`scripts/build_submission.py` refuses to publish a file that fails the gate
(`if not report.ok: "REFUSING to publish a file that fails the gate."`), so the gate
is enforced at generation time and not only on demand. The NaNs are outside the
footprint only (7,111,787 of them), and the file carries exactly two values, 0.0 and
1.0. `tests/test_gate.py` constructs the NaN-inside-footprint file and asserts it is
rejected, so the check is a test, not a hope.

**The generator now has a known blind spot**, though — not a format defect but a
target defect: it optimises and reports against the catalogue. See §6.

## 6. The measurement the entry was missing: score on the population that is scored

Both prize rounds score faults *absent* from the catalogue. The entry's only
new-fault-like measurement (`GEMSDOE/scripts/eval_proxy_catalogue.py`) predates the
staff clarification, so its false-positive sum charges for mass on the catalogue,
which the platform does not. This session re-ran it on the shipped file
(`evidence/proxy_eval_gems6_shipped.json`: DTI **0.0327**, TP_w 2,614 of a possible
61,664) and then implemented the rule-correct version
(`tools/masked_proxy_eval.py`, `evidence/masked_proxy_eval.json`).

| artifact | emitted px | on catalogue | raw DTI | **masked DTI** | best dilation |
| --- | --- | --- | --- | --- | --- |
| `ens12-adopted-floor0.1-w0` (GEMSDOE) | 172,974 | 6,455 | 0.0999 | **0.1014** | worse at every width (0.077 at 6 px) |
| `local-sandbox-smoke` (GEMSDOE) | 207,906 | 2,313 | 0.0864 | 0.0868 | worse (0.0605 at 6 px) |
| **`gems6_hgb88-topk03_33cec71ff0` (6GEMSDOE, shipped)** | 155,021 | 23,605 | 0.0327 | **0.0348** | **better: 0.0599 at 6 px** |
| `35042805806` (GEMSDOE, tiny precise emission) | 21,492 | 2,593 | 0.0247 | 0.0249 | much better: 0.0655 at 6 px |
| blanket 1.0 inside the footprint *(no skill)* | 5,167,373 | 60,988 | 0.0585 | 0.0592 | — |
| catalogue copy *(no skill here)* | 60,988 | 60,988 | 0.0000 | 0.0000 | — |

Readings, in order of how much weight they carry:

1. **The mask is a small, favourable correction** (+0.001 to +0.002), not a reversal.
   The catalogue pixels are free; the shipped file wastes 15.2% of its mass there
   (`ens12` wastes 3.7%), but free-and-worthless is only a small loss.
2. **The shipped file is 3× behind a sibling artifact on the only new-fault
   population available**, at a comparable budget. That is the single most
   decision-relevant number in this review. Its own measurements say it is *better*
   than the baseline 48-channel model on the catalogue, so the two populations are
   ranking the two models differently — which is the whole reason to look at this
   population at all.
3. **The width lever has opposite signs for the two artifacts.** Dilating the shipped
   file monotonically helps (0.0348 → 0.0599 at 6 px) because its emission misses the
   proxy faults by more than the kernel; dilating `ens12` monotonically hurts (0.1014
   → 0.0770) because its emission is already within the kernel. The same inversion
   appears in the CV harness of §2, where a freshly trained 88-channel model gains
   +0.0126 (+21%) from a 3-px dilation at a 3% budget. Any statement of the form
   "dilation wins/loses" is a statement about one detector at one budget, not about
   the metric — and the entry currently publishes the version measured on the wrong
   population.
4. **The budget question reopens.** The 3% budget was chosen as minimax-regret by
   re-scoring against ground truth thinned to whole traces on the *catalogue*; on the
   new-fault population the ranking reverses — 5% is better than 3% in all four folds
   of §2, and more mass still is better again. That is expected for a detector whose
   emission misses the proxy faults by more than the kernel, and it is a direct
   argument for spending the extra allowance where the score is actually computed.
   It is *not* a licence to blanket the map: see the next point.
5. **The no-skill baseline is a calibration, not a recommendation.** Predicting 1.0
   everywhere inside the footprint scores 0.0585 here, i.e. better than the shipped
   file. It carries no information and would be worthless in a Phase-2 geological
   review, but it says the metric is recall-hungry: with `n_gt` fixed, blanket scores
   `1/(0.8 + 0.2·F/n_gt)`, so anything that finds more than a few percent of a sparse
   truth set clears the bar the shipped file currently clears.

**How far to trust this.** The proxy is USGS SGMC — state-geological-survey surface
mapping — while the scored faults are expert picks from GeoDAWN geophysics. The proxy
population is 2,083 components with a median of 12 px, i.e. dominated by short
segments, which is a harsh test for a model whose emission is thin lines. The
published leaderboard argues that the real target is *easier* than this proxy: the top
score is 0.3049, which requires covering roughly two-thirds of the truth at high
precision, whereas our best model covers 13.6% of the proxy truth (TP_w 8,378 of
61,664) and would need that same detector to be right about a great many more faults
than it currently is. Both readings point the same way for the *decision* — the
shipped emission is the weakest link — but the *magnitude* of the gap is not
transferable, and this review does not claim it is.

**What to do with it.** Follow the entry's own P1 item 5: spend one of the three weekly
slots on the current file and read the public score — the only real feedback channel,
and §3.6.2 requires the final choice to be blind to the *private* scores only. Then use
the proxy to choose the second attempt. The two changes it supports are cheap and
independent: **dilate the emitted band by ~3 px** (measured +21% at a 3% budget on the
new-fault population, +45% on the shipped file's own sweep) and **move the budget from
3% to 5%** (±0.017 on the catalogue, +0.015 to +0.020 on the proxy). Both make the
submission *wider*, which is the direction the metric rewards when the detector's
localisation error exceeds the kernel — and the opposite of what the entry currently
does. Do not select the final file on these proxies.

## 7. Item 7 — reference sites, ownership, and where we actually sit

**Ownership is resolved, and it is the opposite of the brief's suspicion.** Every
repository named in the brief belongs to the single account `buffedlizard55-lab`
(`evidence/ownership_audit.json`): 14 repositories, no forks, GitHub Pages enabled on
all of them, commit authors limited to the owner plus arena agent identities. So
`5GEMSDOE`, `GEMSDOE4` and `6GEMSDOE` are not another entrant's — they are earlier
sessions of this same entry. The real problem is the one `ACCOUNT_STATUS.md` already
flags: **eleven published sites for one challenge**, five of them complete copies.
That is an A.12 due-diligence exposure and a submission-multiplication risk, and it is
a *human* action to fix: relocate the data bridge into the canonical repo first
(`6GEMSDOE`'s pinned transport currently resolves through `GEMSDOE`), then archive the
duplicates.

**Where we sit: unknown, and the brief's numbers do not fill the gap.**
`evidence/score_attribution.json` traces all five: they are other participants' rows
on the public leaderboard, and two of the three "GEMSDOE3" values appear in that
repository only as local DTI scalars inside
`legacy/data/evidence/block_holdout/fold1_complement.json`. The family's own pages say
so: GEMSDOE3's `README.md` — *"Unscored. No upload has been made."*; 6GEMSDOE's
`ACCOUNT_STATUS.md` — *"No live submission is made from this sandbox."* The field
reference points are: leader 0.3049, organizers' own account 0.1847, and around 0.15
at ranks 22–25. Our best *local* numbers are 0.1698 (blocked CV on the catalogue) and
0.1014 (best non-leaky artifact on the new-fault proxy). Neither is a leaderboard
score, and §6 explains why the second one is probably pessimistic. The honest
statement for the executive summary is: **we are well-formed, reproducible, and not
demonstrably competitive; the next submission is a measurement, not a gamble.**

**Reference-site check (item 5 of the brief).** `tools/check_entry_docs.py` re-reads
37 prose claims from the artifacts rather than trusting the prose: **36 pass, 1 fails**
(`limitations-cover-masking`). It also confirms the entry's prose quotes none of the
five board scores that the brief attributes to it. The site content lives in the
repository, so every claim was checked against the artifact it describes rather than
against a rendered page (github.io is not reachable from this sandbox — verified:
`curl https://buffedlizard55-lab.github.io/…` → `SSL_ERROR_SYSCALL`). Result: the
executive summary and the submission guide are accurate on every checkable number —
file name, size 1,652,883 B, sha256 `33cec71ff0…`, 155,021 px = 3.00% of the
5,167,373-px footprint, gate 13/13, model hyperparameters, the CV table
(0.1628/0.1698, 0.1729/0.1730, 0.1119, 0.1750), and the budget table. Two corrections
are needed:

* the methodology note on the site and in `SUBMISSION_GUIDE.md` advertises a *"tilt
  derivative"* among the derived channels; for magnetics that channel is dead (§2).
  The claim is true of the column list and false of the physics;
* `LIMITATIONS.md` does not mention the catalogue mask or the no-buffer rule, so the
  entry's stated limitations describe the pre-clarification metric. `ACCOUNT_STATUS.md`
  and the site's verification table should carry the same paragraph.

## 8. Item 6 — geological reasoning for every flagged structure

New in this session, and the answer to `NEXT_STEPS.md` P1 item 9.

* `tools/geology_dossier.py` groups the emitted pixels of
  `GEMSDOE/data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif` (5-px closing),
  keeps the 193 candidates at ≥ 200 px, and for each one measures: area and elongation; principal-axis
  strike; distance to the mapped catalogue; agreement across six independent physical
  families (magnetic edge, gravity edge, slope break, strain, conductivity, seismicity),
  each expressed as the candidate's percentile of the whole 5.1 M-px footprint with the
  fault-favourable direction stated per diagnostic; and the candidate's local DTI.
* `tools/geology_report.py` renders `evidence/geology_dossier.md` — a table of the
  strongest candidates plus **ten hand-written readings**, each naming the measurements
  it rests on, the measured discordance from the local mapped trend, and an explicit
  confidence with the strongest argument against its own conclusion.
* **No depth estimate is offered, deliberately.** The tilt-depth method needs the ±45°
  TDR contours, and §2 shows they do not exist in the supplied bands (2.2 × 10⁻⁵ of
  pixels). A number here would be invented, and the dossier says so with the
  measurement attached.

Headline geology from the dossier: of 193 candidates, 64% are "extension" (touching the
catalogue), 35% are **isolated** and 1.6% are halo — a third of the emission sits on
unmapped ground. Per-candidate areas are measured on the 5-px-closed mask, which is
about 11% larger than the emitted set (191,792 px over 193 candidates vs 172,974 px
emitted), so the areas are upper bounds and the geometry is unaffected.
The largest candidates are strain/seismicity objects with little or no potential-field
expression (candidate 2: 12,021 px = 120 km², second invariant in the top 0.3%,
seismicity and strain the only families present, striking 86° across the local mapped
grain — a deforming volume, not a fault). The strongest *fault* candidates are small and isolated:
candidate 131 (11.1 × 3.8 km at 38.65°N 118.55°W) is conductive (96th percentile),
dilatant (98th), seismically active (96th) and magnetically quiet — the
hydrothermal-alteration signature; candidate 179 (3.0 × 1.3 km, nothing mapped within
1.77 km) is the most plausible genuinely new structure in the file.

## 9. Defects and irregularities found (with the fix for each)

| # | severity | finding | fix |
| --- | --- | --- | --- |
| 1 | high | the emission policy, not the detector, loses the new-fault score (§6): a thinned 3% budget, no dilation, chosen on the catalogue | widen — dilation 3 px and a 5% budget both win on the new-fault population; rebuild and re-gate |
| 2 | high | `research.html` publishes "dilation loses" as a general result; it is true on the catalogue and false on the new-fault population (§2, §6) | restate it as conditional, with both measured curves |
| 3 | medium | 40 extra channels had never been scored on the scored population; two of them were dead weight (§2) | measured: they pay (+2% to +9%); drop or repair `mag_tilt`/`tdr_tmi_*` and `mag_asa`, then re-run |
| 4 | medium | `mag_tilt` / `tdr_tmi_*` dead; `mag_asa` duplicate (§2) | drop the two columns or normalise `tmi_vg` by `std(tmi_hg)/std(tmi_vg)` before the arctangent, then re-run the blocked CV |
| 5 | medium | `LIMITATIONS.md` and the site do not state the mask rule (§7) | add the quoted paragraph; the text is in `patches/PROPOSED_ENTRY_CHANGES.md` |
| 6 | medium | eleven published sites for one entry (§7) | relocate the transport, then archive the duplicates — human action |
| 7 | medium | `1,533 px` discrepancy: the feature builder's union-invalid mask (7,113,320 px) and the catalogue's nodata (7,111,787 px); `valid_all_band_pixels` 5,165,840 vs footprint 5,167,373 | document the two masks; they are correct for different purposes, but the site currently shows one number where two exist |
| 8 | low | `build_features.py`'s docstring says the stack is "≈ 2.25 GB"; it is 4.32 GB (3730 × 3292 × 88 × 4 B) | fix the comment |
| 9 | operational | `/home/user/out/**` is **not** persisted between sessions in this environment: the 4.3 GB feature stack and the data bridge placed under `out/gems6` were lost at the session boundary and had to be rebuilt/re-fetched | build derived artifacts under a persisted path, or accept a ~11-minute rebuild each session |

Reproducibility of the derived stack: rebuilding it in this session gave
`shape [3730, 3292, 88]`, `invalid_pixels 7,113,320` and `valid_all_band_pixels
5,165,840` — identical to the committed `features_meta.json` (672.8 s vs 643.1 s). The
derived artifact itself is not committed; it is rebuilt on demand.

Not defects, checked and cleared: the CV contains no random split; `validate_submission.py`
hard-gates NaN-inside-footprint and `build_submission.py` refuses to publish on failure;
`pytest` 44/44; all three official rasters match their sha256 pins; the site's numbers
match the artifacts; the metric implementation matches the published formula and the
worked example.

## 10. What is *not* verified

* **No leaderboard score, for any file, ours or otherwise** (§7).
* The SGMC proxy is not the scored population (§6), and its difficulty is probably
  harsher than the real target's; the ranking it produces is the usable signal, not the
  level.
* The two-sided dilation result was measured on binary emissions; a retrained model
  with a different localisation error will have its own optimum width.
* The 1 m DEM is still not incorporated (`LIMITATIONS.md` §4) — the single largest
  untapped signal, and unreachable from this sandbox (USGS 3DEP egress blocked).
* Eligibility (§1.3), the account that is the official entry, and the remaining weekly
  allowance are human unknowns, unchanged by this review.

## 11. Next actions, in order

1. **Human:** fill in the one-entry record in `SUBMISSION_GUIDE.md` (account, allowance,
   generative-AI disclosure), then archive the duplicate repositories after relocating
   the bridge.
2. **Human:** upload the current file on slot 1 and record the public score. It is the
   only real feedback available and the decision in §6 depends on it.
3. Apply the three text fixes (mask rule in `LIMITATIONS.md`, dead-channel claim in the
   methodology note, the 2.25 GB → 4.32 GB comment), and re-state the dilation result as
   conditional on the detector rather than absolute.
4. Rebuild the submission once with `--strategy topk_hard@0.05` plus a 3-px dilation
   (or the equivalent wider policy) and gate it — this is a one-command change that two
   independent measurements say is worth more than any model rebuild available in this
   sandbox.
5. Re-run the blocked CV with the magnetic tilt channel repaired *and* with the two
   degenerate columns dropped, to see whether the fix pays before shipping it.
6. Then, and only then, decide between the artifacts — with the leaderboard score in
   hand rather than the proxy alone.

---

### Provenance

Every number in this review was produced this session by one of the six scripts in
`tools/`: `check_entry_docs.py` (36/37), `masked_proxy_eval.py`,
`experiment_proxy_cv.py`, `geology_dossier.py`, `geology_report.py`,
`tilt_derivative_audit.py`. Raw outputs and the artifacts they describe are in
`evidence/`; anything not produced here is attributed to the file it came from. The raw
outputs are in `evidence/` alongside the script that wrote each one. `patches/` holds
the proposed changes to `6GEMSDOE`, which this session cannot push (the token has no
write access to that repository: `git push --dry-run` → HTTP 403).
