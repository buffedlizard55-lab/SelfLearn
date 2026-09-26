# Proposed changes for the **one** entry: `buffedlizard55-lab/6GEMSDOE`

Status 2026-09-26: **proposal, not applied to the canonical repository or submitted**.
This checkout is `SelfLearn` on branch `arena/01a0dba8-selflearn`, not the entry.
The GitHub bot's REST permission check returned `push=false` for both repositories;
a later GitHub API request failed with **HTTP 401 Bad credentials**. The owner must
reconnect GitHub in Arena with appropriate existing-repository access before a PR
is possible. The DrivenData
registration/eligibility/weekly allowance and any owner-specific score are also
unknown. Do not create a second entry/site/account or silently upload a scratch file.

**Session-2 addendum (later the same day).** GitHub auth works again
(authenticated as `arena-ai-coding-agent[bot]`); REST still reports
`push=false` on `SelfLearn` and `6GEMSDOE`, so these changes still cannot be
applied from here. Re-verified against a fresh clone: the CV patch still
dry-run-applies and fixes every layout (0 oracle misses) with the entry's 46
tests passing on the patched copy; `check_entry_docs.py --online` still reports
48/50 with the same two gaps (masking rule; per-candidate geology document — a
candidate for that document now exists at
`evidence/phase2_candidate_narratives_2026-09-26.md`). The live 6GEMSDOE site's
suggested submission comment still carries the §C.3 overgeneralization
("strictly increasing … fractional confidence gives score away"), and the
5GEMSDOE / GEMSDOE4 sites still advertise their own artifacts and (for
5GEMSDOE) the 0.0-outside fallback — §C.6 remains necessary. Evidence:
`evidence/ownership_resolution_2026-09-26_session2.json`,
`REVIEW.md` session-2 section.

## A. P0: do **not** promote either scratch candidate

Evidence, **SGMC surface-fault proxy only**, not official hidden labels:

| Assessment | Shipped | Tested variant | No-skill reference | Decision |
| --- | ---: | ---: | ---: | --- |
| Eastern held-out *postprocessing* audit | 0.03526 | shipped emission, 6-px dilation **0.07578** | blanket **0.08235** | fails conservative no-skill gate |
| Repeatedly inspected full-grid proxy | 0.03480 | 86-ch, 5% top-k + 3-px dilation **0.05723** | blanket ~**0.0592** | no evidence of useful advantage |

The 86-channel, undilated 5% scratch file scores 0.04539 on that same full proxy.
Both 86-channel scratch GeoTIFFs passed 13/13 format checks; neither is an upload
recommendation. `evidence/emission_spatial_holdout_2026-09-26.json`,
`evidence/feature_ablation_cv_2026-09-26.json`,
`evidence/local_candidate_proxy_comparison_2026-09-26.json` contain the numerical
records. Full-fit/full-footprint results must **not** be subtracted from fold-restricted
CV scores as if they measured a generalization gap; their models, masks and budgets
differ. The SGMC proxy's code 2 excludes faults within 300 m of training labels,
including the [corrections the staff say are in scope](https://community.drivendata.org/t/11516/4);
its test-fault relationship is unknown. [Staff did not disclose hidden fault
sources/types/coverage](https://community.drivendata.org/t/11527/7).

## B. Fix a real CV geometry bug before citing buffered CV without qualification

The existing `src/gems/cv.py::_dilate` expands in a four-neighbour Manhattan diamond.
Its 3-px exclusion **misses the (2,2) corner**, only √8 px = 283 m from the held-out
block: this is inside the [official 300 m Euclidean kernel](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric).
The canonical test `assert not train[r].any() or True` is always true, and its
other separation test only reapplies the *same* `_dilate` function, so neither
is an independent proof. The **full-grid** audit (`evidence/cv_geometry_audit_2026-09-26.json`)
measured **zero** misses in the historical 4×4/4-fold and 6×6/6-fold layouts,
which are vertical stripes. By contrast, a 5×5/3-fold assignment had **32**
train-mask pixels within 300 m across its three folds, and a 6×6/4-fold layout
had **100** across four folds. This bug **does not retroactively invalidate
those historical stripe-based DTI tables**; it breaks the general buffered-CV
contract and future non-stripe layouts.

`patches/cv_euclidean_buffer.patch` makes `_dilate` use a true Euclidean disk.
The review's `tests/test_review_regressions.py` uses `scipy.ndimage.distance_transform_edt`
as an **independent** oracle: it failed on the unmodified 5-/6-block non-stripe
layouts (10 / 25 misses in fold 0 of the test grids) and passed on a separately
patched copy. The canonical 46 tests also passed post-patch. Apply on the entry
branch *after write access is available*. Re-run any CV where the changed
training mask actually differs. Do not imply that the 4/4 and 6/6 stripe scores
changed merely because the source implementation is being fixed.

```bash
# While in a permitted working copy of the existing 6GEMSDOE repository:
patch -p1 --dry-run -i /path/to/SelfLearn/gemsdoe_review/patches/cv_euclidean_buffer.patch
patch -p1 -i /path/to/SelfLearn/gemsdoe_review/patches/cv_euclidean_buffer.patch
GEMSDOE_ENTRY_ROOT="$PWD" python -m pytest -q /path/to/SelfLearn/gemsdoe_review/tests/test_review_regressions.py
python -m pytest -q tests
```

## C. Correct the published claims, without replacing an entry or a submission

1. `LIMITATIONS.md` omits the scoring mask. Add: “DrivenData staff say *only the
   supplied training-label pixels* are excluded from evaluation in **both** phases.
   Predictions 1–3 px from those pixels are **not** exempt from false-positive cost
   unless they are near **new-fault truth**. New truth may include corrections within
   300 m of mapped faults. Our catalogue blocked-CV DTI is not a score on that
   population.” [Staff posts 2 and 4](https://community.drivendata.org/t/11516/4).
2. `EXECUTIVE_SUMMARY.md`, `SUBMISSION_GUIDE.md` and the site's methodology should
   qualify the supplied magnetic `mag_tilt` and nearly-duplicate `mag_asa` as
   unreliable/redundant for depth inference. The gravity tilt remains useful as a
   descriptive anomaly, not a confirmed fault. Evidence:
   `evidence/tilt_derivative_audit.json`. Calling a **sampled** HGB model “weaker
   than a U-Net” without a controlled target comparison is not supported; instead
   state that different architectures were **not benchmarked** on the hidden target.
3. The executive summary's “the true score **will** be lower than 0.1698” must become
   “the hidden score is **unknown**”: 0.1698 is held-out *catalogue* CV DTI, not a
   leaderboard result. The guide's “strictly increasing in the predicted value,
   so fractional confidence gives score away” confuses **uniform rescaling of
   every probability** (provable with TP>0) with hardening *each* value to 1
   (counterexample: a remote 0.01 false positive becomes 1 and hurts DTI).
   The hard mask is an **empirically selected catalogue policy**, not a theorem
   that all fractions are bad on unknown faults. Likewise, 4–5 px spacing loses
   TP on a true dense fault, but may save FP where the predicted line is wrong;
   geometry alone does not choose a universal emission width.
4. `research.html` “dilation loses” describes a particular catalogue experiment,
   not all faults/detectors. The newer SGMC study shows the opposite *on that
   proxy*, **but fails the held-out no-skill check**; do not replace one absolute
   slogan with “dilation wins”. Both masks and budgets must be stated.
5. The one-entry guide's first instruction is “download and upload.” Precede it
   with “Before **any** upload, account holder confirms the one DrivenData entry,
   eligibility, remaining allowance, genuine score decision and §3.2 generative-AI
   use disclosure; run the format gate on the selected bytes.” The current guide's
   blank human-owned table is honest; do **not** fill it with guessed values.
6. `ACCOUNT_STATUS.md` already records that the **first-party bridge is now in
   `6GEMSDOE/data/bridge/`**. Its older `NEXT_STEPS.md` step claiming the bridge
   still pulls from `GEMSDOE` is stale; remove that dependency warning. Eleven
   GitHub repositories with Pages are a real attribution/maintenance risk, **not**
   proof of eleven DrivenData accounts, a rule violation, or an automatic A.12
   disqualification. Do not archive anything before the account holder verifies
   whether other repositories are needed. Repo owner for `5GEMSDOE`, `GEMSDOE4`
   and `6GEMSDOE` is `buffedlizard55-lab`; DrivenData owner is unverified.
   The live [5GEMSDOE site](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)
   nevertheless advertises a different file to upload and a zero-outside-footprint
   fallback; [GEMSDOE4](https://buffedlizard55-lab.github.io/GEMSDOE4/docs/index.html)
   also offers a separate browser-built raster. Mark those pages historical and
   remove conflicting upload advice **after** the account holder confirms the
   one canonical entry; do not use a zero-outside fallback without the official
   template gate.
7. `scripts/build_features.py` still calls the 88-ch float32 memmap ~2.25 GB;
   `3730 × 3292 × 88 × 4 = 4,322,264,320` bytes (~4.32 decimal GB).
   Fix the comment, not the hash-pinned feature data.

## D. Geological reasoning without rank contamination

`tools/geology_dossier.py` now pins official inputs and gates each raster; fixes
plan vs profile curvature and the raster-row azimuth sign; samples finite regional
values; measures physical indicators/distance on **actually emitted** pixels rather
than pixels added by a 5×5 closing; keeps bad magnetic tilt/ratio out of the
six-family tally; avoids meaningless catalogue-crop scores/depth bins. Its current
outputs are:

- `evidence/current_shipped_geology_2026-09-26.{json,md}`: exact shipped SHA-256,
  **180** groups at ≥200 closed px; 1 isolated by a *distance heuristic*, 87 near a
  mapped trace, 92 halo. Most large objects are not thin independent fault lines.
- `evidence/local_candidate_w3_geology_2026-09-26.{json,md}`: exact **unsubmitted**
  scratch SHA-256, **343** large groups, 54 isolated by the same distance rule;
  inclusion is not a geological or scoring endorsement.

The old `evidence/geology_dossier.md` was withdrawn. Its ten handwritten readings
were joined to *size ranks* on an `ens12` mask with 172,974 emitted pixels and
cannot be attached to the shipped raster or scratch mask. Some claimed specific
alteration or activity without evidence. The replacement renderer refuses a dossier
without a submission hash and makes no verified-fault or depth assertions. The
historical JSON is kept only with an explicit archival warning. Site/narrative
claims about “every fault” must distinguish the ≥200-closed-pixel reviewed groups
from the smaller **uninterpreted** components (all inventoried, not called faults,
including 26,040 shipped emitted pixels in 2,409 small groups and 93 pixels not
retained by closing). Real narrow faults could still be in this remainder.

## E. Recheck and go/no-go criteria

1. The canonical shipment was gate-checked **13/13 PASS** at SHA-256
   `33cec71ff00b3f32d0d59c81c156f3f1488ffef46baa4b6499094e24ea1875ab`:
   155,021 positives, 5,167,373 finite scored pixels and **0 inside-NaNs**.
   A deliberately poisoned in-footprint NaN file failed the *hard* gate with
   a nonzero exit while the finite `[0,1]` test still passed; it was never offered.
2. Re-run `tools/check_entry_docs.py /path/to/6GEMSDOE --online` after text changes
   and adding the *current* geological report. It correctly found **48/50** checks
   passing on a read-only canonical snapshot: `LIMITATIONS.md` lacks the staff's
   mask clarification, and the canonical checkout lacks a per-candidate geology
   document. Its foreign-board-score test is no longer tautologically true; its
   live inventory uses the supported GitHub REST `has_pages` field.
3. Re-run pinned-file and fold/metric tests on the exact entry revision before a
   PR/merge, and avoid claiming a leaderboard position. There is **no owned public
   score** until the one registered account is verified and its submission history
   read. Do not submit a proxy-optimized scratch variant merely because it passes
   format. Fresh, truly independent geological validation (or the 1 m DEM with
   permitted access and qualified review) is needed before choosing a new policy.

**Rules sources:** [official rules PDF §§1.3, 3.2, 3.4–3.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf),
[format and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[staff on the mask](https://community.drivendata.org/t/11516/4),
[staff on unknown test-fault provenance](https://community.drivendata.org/t/11527/7).
