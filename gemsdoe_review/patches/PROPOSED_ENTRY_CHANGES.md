# Proposed changes to the entry repository (`buffedlizard55-lab/6GEMSDOE`)

This session has **no write access** to that repository (`git push --dry-run` → HTTP
403; the API reports `permissions.push = false` for the agent identity). Everything
below is therefore written to be applied by a human or from a session with push
rights, without further editing. Each item names the measurement that justifies it.

---

## 0. The one change worth more than any model work (highest priority)

Two independent measurements this session say the emission is the weak link:

| measurement | result |
| --- | --- |
| shipped file, SGMC new-fault population, dilation sweep (`tools/masked_proxy_eval.py`) | 0.0348 at width 0 → **0.0599 at width 6 px** |
| 4-fold blocked CV on that population (`tools/experiment_proxy_cv.py`) | 3% budget 0.0593 → **0.0719 with a 3-px dilation** (+21%) |
| same CV, budget | **5% beats 3% in all four folds** (0.0737 vs 0.0593 un-dilated) |

So: rebuild once with a wider emission — `--strategy topk_hard@0.05` and a 3-px
dilation of the emitted band, or an equivalent — and re-run the gate. This is a
one-command change; it does not need the model to be retrained. Do it *after* reading
the public score for the current file (below), so the comparison is one variable at a
time.

The reason the entry currently does the opposite is that `research.html` and
`LIMITATIONS.md` §6 measure dilation on the catalogue, where it loses (0.0803 vs
0.0879). Both are true; they are about different populations, and the scored one is
the new-fault population.

## 1. Read the public leaderboard before spending the second slot

The entry's own `NEXT_STEPS.md` P1 item 5 already says this. Nothing in this sandbox
can do it (`/accounts/login/`). Record the number in the one-entry table in
`SUBMISSION_GUIDE.md`; only then is the artifact choice a decision instead of a guess.

## 2. Repair or drop three dead/duplicate channels

Measured in `evidence/tilt_derivative_audit.json`, over the whole footprint:

1. `mag_asa = sqrt(tmi_hg² + tmi_vg²)` is a duplicate of the supplied `tmi_hg`
   (Pearson r = 1.000000): `tmi_vg` is ~256× smaller than `tmi_hg` (median |·| 0.0090
   vs 13.15).
2. `mag_tilt = atan2(tmi_vg, |tmi_hg|)` is dead: |TDR| never leaves ±3.1° (p99), so the
   ±45° contours the tilt-depth method needs occur in 2.2 × 10⁻⁵ of pixels. The
   `tdr_tmi_s1.5` and `tdr_tmi_s3` columns inherit the defect.
3. The gravity equivalents are **not** affected (`iso_grav_anom_vg` is the same order
   as its horizontal counterpart; p99 |grav_tilt| = 88.8°), which is what makes 1 and 2
   a scaling bug rather than a property of the data.

Minimal fix, to be validated by the blocked CV before shipping: either drop the two
columns, or normalise before the arctangent —
`atan2(vg · std(hgm)/std(vg), |hgm|)` — which is the standard treatment for a
vertical-gradient band whose units differ from the horizontal one.

The supplied `tc` band remains unidentified (it is neither `atan2(tmi_vg,|tmi_hg|)`
nor the Laplacian of TMI, r = 0.013 and 0.000 respectively). It is in the stack;
`band_identities.json` already says the description is ambiguous.

Do **not** replace the magnetic tilt derivative with a Fourier |k| derivative on the
strength of this review: `tools/tilt_derivative_audit.py` implements that and it does
not separate mapped faults better than `tmi_hg` does.

## 3. State the masking rule where the limitations are stated

`scripts/check_entry_docs.py` fails exactly one check out of 37,
`limitations-cover-masking`: `LIMITATIONS.md` never mentions that the catalogue is
masked out of evaluation. Source (DrivenData staff, posts 2 and 4):
<https://community.drivendata.org/t/11516>. Verbatim quotes and the consequences are in
`evidence/scoring_rule_clarification.json`. Proposed paragraph:

> **Known faults are masked out of the score.** DrivenData staff state that pixels
> corresponding to known USGS/INGENIOUS faults are "masked / excluded from evaluation,
> so they do not count towards penalty terms", and that the mask "is indeed
> pixel-exact — it is identical to the provided set of training fault labels". Three
> consequences for the numbers in this repository. (1) Our blocked-CV scores are
> measured against the catalogue, which is not the scored population: they are
> optimistic where a prediction hugs a mapped trace and silent about the population the
> prize scores. (2) A predicted pixel near a known fault but far from new-fault truth
> "will be fully penalized, i.e., the buffer does not apply to known faults" — so mass
> a few pixels off a mapped trace is priced differently by the platform than by our
> proxy. (3) New-fault truth "can indeed lie within 300 m of a known fault trace",
> because "corrections or modifications to existing fault traces" are an intended
> outcome, so thin along-strike corridors are not worthless — they are simply
> unmeasurable locally. Measured effect of implementing the rule on the shipped file:
> +0.0021 DTI (0.0327 → 0.0348 on the SGMC new-fault population).

## 4. Two accuracy fixes in the prose

* `EXECUTIVE_SUMMARY.md`, `index.html` and `SUBMISSION_GUIDE.md` advertise a *"tilt
  derivative"* among the derived channels. That is true of the column list and false of
  the physics for magnetics (item 2 above). Say what the channels are, or fix them
  first.
* `research.html` states *"Measured, dilation loses: the densified placement scored
  0.0803 against 0.0879"*. Restate it as conditional: dilation loses on the catalogue
  for this detector, and gains 21% on the new-fault population. Both curves are in
  `evidence/`.
* `scripts/build_features.py`'s docstring says the stack is "≈ 2.25 GB". It is
  4,322,264,448 B = 4.32 GB (3730 × 3292 × 88 × 4).

## 5. Site-claim additions worth making (all measured here)

* the per-candidate geological dossier (`geology_dossier.md`, 193 candidates, ten
  written readings) — P1 item 9 asks for exactly this, and Phase 2 is where the prize
  money is;
* the explicitly **absent** depth estimate, with the measurement that shows why
  (a submission that invents a tilt-depth number is worse than one that says it cannot);
* the score-attribution table, so that no reader can mistake another participant's
  leaderboard row (`extradr19` 0.1563, `smashi34` 0.1560, `smrtdoog5` 0.1193, `SDCF9`
  0.1152, `wbg1` 0.0830) for this entry's — `evidence/score_attribution.json`.

## 6. Repository hygiene (human action)

`ACCOUNT_STATUS.md` designates `6GEMSDOE` as the single canonical entry, but eleven
competition-named repositories under the same account all have GitHub Pages built, five
of them complete copies of the project. The entry is exposed to an Appendix A.12
due-diligence finding until the duplicates are archived. Order of operations, as
`ACCOUNT_STATUS.md` already requires: relocate the sha256-pinned bridge into this
repository first (it currently resolves through `GEMSDOE`), verify the three rasters,
*then* archive.

## 7. New scripts to add (`scripts/`)

Copied from `gemsdoe_review/tools/`; they already import `gems.spec`, `gems.metric`
and `gems.features` and default to the repository root, so they run unmodified:

| file | what it does | runtime on 2 CPUs |
| --- | --- | --- |
| `geology_dossier.py` | per-candidate geometry, 21 diagnostics as regional percentiles, six-family agreement, distance to catalogue, local metric | ~5 min |
| `geology_report.py` | renders the dossier markdown, keeping hand-written readings separate from measurements | ~3 s |
| `tilt_derivative_audit.py` | the channel audit behind item 2 | ~1 min |
| `masked_proxy_eval.py` | rule-correct proxy evaluation and dilation sweep (needs `GEMSDOE`'s `src/metrics.py`, or a port of it) | ~10 s per candidate |
| `experiment_proxy_cv.py` | blocked CV scored on the new-fault population; the harness behind item 0 | ~8 min for 2 configs × 4 folds |
| `check_entry_docs.py` | re-reads the entry's own prose claims from its artifacts before an upload (36/37 today) | ~3 s |
