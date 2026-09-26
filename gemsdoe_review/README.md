# GEMSDOE review — 2026-09-26 (sessions 1–6)

Read **[SESSION6.md](SESSION6.md) first** for the current handoff; [SESSION5.md](SESSION5.md)
is the previous one. `SESSION4.md` records an earlier phase (its spacing-4 number was
measured at 10% of the shipping budget and superseded in session 5). `REVIEW.md`
preserves sessions 1–3, including a now-retired whole-system diagnostic whose
0.0060/0.0148 conclusion is not clean spatial CV.

Session 6, in brief:
- **Nested policy check:** keep raw / 3% / spacing 4. The nested gain was coverage, not
  skill.
- **Gravity bug:** the supplied `iso_grav_anom_hg` is dG/dx, not |∇G|. This affects the
  entry's channels 25/26 and the session-5 dossier's gravity-edge votes. It is a
  correctness fix; measured score effect ±0.005.
- **105 channels adopted by rule:** 0.2419 vs 0.2345, 3/4 folds, single seed.
- **Label-blind screen:** only about 12% of flagged components survive it, and none of
  session 5's named multi-family flags does.
- **Nothing submitted, created or pushed to any GEMS repository.**

Session 5 re-ran session 4's open question **at the shipping budget** (400k negatives /
300 iterations), on freshly rebuilt official bytes, with the pre-specified
exact-system-purged 4-fold CV, three frozen label-blind null seeds at the same emitted
budget, and two pre-specified layout/buffer sensitivities. The hypothesis holds:
**full88 + 4-px spacing scores 0.2345 mean fold DTI against 0.0925 for the dense
policy the shipped artifact uses, and 0.2345 clears every null seed in every fold**,
while the dense policy (0.0925) falls **below** the matched-budget random control
(0.1722). Sensitivities keep the sign (3×3 blocks: 0.2203 vs 0.0907; 5 px buffer:
0.2435 vs 0.0965). Engineered features beat raw19 at both policies; drop2 is a wash.
**Neither number is a leaderboard score.** No canonical artifact, site, account or
submission was changed; one local candidate GeoTIFF was built, gated 13/13, read
geologically and left in the session scratch directory.

## Session-5 evidence index

| path | what it is |
| --- | --- |
| `evidence/spatial_system_models_shipping_session5.json` | the shipping-budget CV: 3 feature sets × dense/spacing4/spacing5, per fold and per system |
| `evidence/spatial_controls_shipping_session5.json` | the three frozen label-blind null seeds at the identical emitted budget (dense/s4/s5) |
| `evidence/spatial_comparison_shipping_session5.json` | the H1/H2 verdict against the pre-specified rule |
| `evidence/spatial_system_models_sens1_session5.json`, `..._sens2_session5.json` | the two pre-specified sensitivities (3×3 blocks/3 px; 2×2 blocks/5 px) |
| `evidence/spatial_system_geometry_session5.json` | per-fold isolation for all three layouts: 0 overlap, 0 buffered training pixels, 0 shared positive systems, 40 exact systems / 3,199 traces |
| `evidence/shipping_budget_manifest_session5.json` | what was run, on which bytes, with which seeds, and what is out of scope |
| `evidence/feature_priorities_session5.json` | priorities 1–3 re-measured on rebuilt bytes: dead tilt, duplicated ASA, slope-break candidate channels, strain/seismicity/conductivity cross-reference |
| `evidence/submission_gate_session5.json` | shipped artifact: 13/13 PASS, EPSG:32611, 100 m, 3730×3292, values [0,1], 0 NaN in footprint |
| `evidence/nan_poison_session5.json` | one in-footprint NaN in a copy: everything else passes, `NAN-INSIDE-FOOTPRINT` fails, exit 1 |
| `evidence/submission_gate_candidate_session5.json` | the same gate on the session-5 local candidate: 13/13 PASS, 155,021 px, sha256 `f807dccf…` |
| `evidence/candidate_spacing4_report_session5.json` | how the candidate was built: same model, only the placement policy changed; 4,106 px on catalogue vs 23,605 shipped; Jaccard 0.043 |
| `evidence/spacing4_candidate_geology_2026-09-26.json` | the candidate's per-component dossier: all 943 components ≥200 px, 21 diagnostics each, no depth claim |
| `evidence/spacing4_candidate_geology_2026-09-26.md` | that dossier rendered with hypothesis / counterinterpretation / capped confidence per component |
| `evidence/spacing4_candidate_geology_session5.md` | the hand-written reading: what the policy change does to the geology, plus six named candidates with their measurements and competing interpretations |
| `evidence/shipped_geology_rerun_session5.json` | the shipped artifact's dossier re-rendered from pinned bytes: byte-identical to the committed one (MD `285002cf…`, fragments `a202e84c…`) |
| `evidence/entry_patch_verification_session5.json` | the session-3 patch re-applied to `e2fe3f4`: 75 review + 47 entry tests green, offline doc check 37/37, true disk in `_dilate`; flags that `cv_euclidean_buffer.patch` no longer applies with `git apply` |
| `evidence/ownership_resolution_2026-09-26_session5.json` | live ownership audit: one account, 0 forks, 12 GEMS-named repositories — **and `LEARNGEMSDOE`, created 2026-09-26T18:18Z during the session window** |
| `evidence/leaderboard_raw_2026-09-26_session5.md`, `leaderboard_snapshot_..._session5.json` | verbatim leaderboard transcript + parse: 50 rows, field high DARD 0.3049, organizer 0.1847 (#14) |
| `evidence/live_site_claims_2026-09-26_session5.md` | all six reference sites re-read, with the claims that are unsupported |
| `evidence/metric_claim_check_session5.json` | uniform rescaling is monotone; the entry's published "hardening always helps" sentence is false (0.998 → 0.833) |
| `evidence/rank_tables_pin_audit_session5.json` | two independent rank-table builds differ only by `built_utc`; the pinned hash can never be re-derived |
| `evidence/entry_docs_offline_session5.txt`, `..._online_session5.txt` | doc check on the unpatched entry: 35/37 offline, 47/51 online (two failures from the 12th repository) |
| `evidence/session_reverification_2026-09-26_session5.json` | the entry's own re-verification: gate 13/13, rasters 3/3, pytest 46/46, site drift-free |
| `tools/shipping_budget_confirmation.py` | the session-5 driver: prints its decision rule before running, then measures it |
| `tools/build_spaced_candidate.py` | builds, gates and reports a local candidate from the shipping model |
| `tools/ownership_live_audit.py` | read-only GitHub audit of the GEMSDOE family |
| `tools/leaderboard_snapshot.py` | parses a verbatim leaderboard transcript into rows + attribution |
| `tools/metric_claim_check.py` | re-measures the published metric claims against the entry's own metric |
| `tools/rank_tables_pin_audit.py` | rebuilds the rank tables twice and reports what the pin does and does not pin |
| `tests/test_session5_additions.py` | 17 regressions: metric oracles, budget oracles, evidence pins, per-layout CV isolation, patch dry-run |

## Session-4 evidence (superseded by the session-5 shipping-budget re-measurement)

| path | what it is |
| --- | --- |
| `evidence/spatial_system_ablation_session4.json` | the reduced-budget CV models (100 iters, up to 50k negatives, 40 exact systems / 3,199 traces): dense 0.0935 / spacing4 0.2436 / spacing5 0.2105 for full88 |
| `evidence/spatial_controls_session4.json` | the three frozen label-blind null seeds at that budget (dense 0.1722, s4 0.2037, s5 0.1904) |
| `evidence/spatial_comparison_session4.json` | session-4 verdict; the shipping-budget re-measurement it asked for is `spatial_comparison_shipping_session5.json` |
| `evidence/spatial_system_geometry_session4.json` | session-4 fold isolation (superseded by `spatial_system_geometry_session5.json`, which covers three layouts) |
| `evidence/spatial_system_ablation_session4.json` (same file) | the raw19/full88/drop2 ablation at that budget — drop2's +0.0003 was noise, confirmed in session 5 |
| `evidence/submission_gate_session4.json`, `nan_poison_session4.json` | 13/13 + the NaN-inside-footprint hard gate, session-4 copies |
| `evidence/feature_priorities_session4.json` | priorities 1–3 measured at reduced budget; re-measured in `feature_priorities_session5.json` |
| `evidence/patched_entry_cv_session4.json` | the Euclidean-buffer patch applied and verified on a scratch clone (re-verified session 5) |
| `evidence/live_audit_session4.json`, `reverification_session4.json` | session-4 ownership audit and re-verification |

Historical evidence index (consult SESSION4.md validity warnings first):

| path | what it is |
| --- | --- |
| `REVIEW.md` | the review: findings against the seven brief items, the measurements behind each, what is not verified, and what to do next |
| `evidence/ownership_audit.json` | every `GEMSDOE*` repository under `buffedlizard55-lab`: owner, fork status, Pages, commit authors |
| `evidence/leaderboard_snapshot.json` | the public leaderboard, including the rows the brief's five scores actually belong to |
| `evidence/score_attribution.json` | the full trace of those five numbers, to their leaderboard rows and to the local files they also appear in |
| `evidence/scoring_rule_clarification.json` | the official masking rule, quoted verbatim from the staff post, with the consequences |
| `evidence/proxy_eval_gems6_shipped.json` | the shipped file scored on the SGMC new-fault population with the entry's own (pre-clarification) script |
| `evidence/masked_proxy_eval.json` | the same population scored the rule-correct way, raw vs masked, plus a dilation sweep over four candidate artifacts and two no-skill baselines |
| `evidence/masked_proxy_eval_all.json` | every candidate artifact found across the repository family, with a warning on each one that is circular |
| `evidence/proxy_cv_fold0.json` | four-fold blocked CV scored on the new-fault population: 48-channel vs 88-channel stacks, with and without dilation |
| `evidence/session3_reverification_2026-09-26.json` | session-3: fresh-clone re-verification — gate 13/13 + poison test, pytest 46/46 (47/47 patched), Euclidean oracle (0 historical / 32+100 non-stripe misses), placement integrity |
| `evidence/ownership_resolution_2026-09-26_session3.json` | session-3: live re-resolution of the three "unconfirmed" sites (all `buffedlizard55-lab`, GitHub layer RESOLVED; DrivenData layer still account-holder-only) + fresh leaderboard read (field high DARD 0.3049; brief scores at ranks 23/24/40/41/50) |
| `evidence/ablation_shipping_axis_2026-09-26.json` | session-3: full88/drop2/drop4 on the shipping axis (round-2 yardstick), incl. trace-reduced GT; `full88` reproduces the 0.1698 decision number |
| `evidence/semisup_shipping_axis_2026-09-26.json` | session-3: semi-supervised second pass (verified pseudo-positives, NEXT_STEPS P1.6) vs the canonical fold models, same folds/placement |
| `evidence/tilt_derivative_audit.json` | the magnetic tilt-derivative channel audit: a dead channel, a duplicated channel, and a candidate replacement |
| `evidence/geology_dossier.json` | per-candidate measurements for all 193 flagged structures (5-px closing, ≥ 200 px) |
| `evidence/geology_dossier.md` | those measurements rendered with hand-written geological readings and explicit confidences |
| `tools/feature_priorities_audit.py` | session-2: measures priorities 1-3 of the brief on the official bytes (deterministic; byte-identical on re-run) |
| `tools/phase2_narrative.py` | session-2: renders Phase-2-style narratives from the measured dossier; refuses unidentified bytes |
| `tools/shipping_axis_ablation.py` | session-3 (sibling branch): dead-channel ablation (full88/drop2/drop4) and the semi-supervised second pass on the canonical shipping-axis yardstick (4x4 blocked folds, 400k/300, seed 0); `full88` must reproduce 0.1698 or the run is void |
| `tools/system_holdout_cv.py` | session-3 (parallel branch): whole-fault-system holdout CV + semi-supervised second pass on the never-seen-system axis, scored with the staff masking rule, with budget/selection sweeps and a no-skill blanket gate |
| `evidence/system_holdout_cv_2026-09-26.json` | session-3 (parallel): the system-holdout + semi-sup measurements (the shipped policy scores 0.0060 vs blanket 0.0148 on never-seen systems; the sibling's catalogue-axis semi-sup run is in `semisup_shipping_axis_2026-09-26.json`) |
| `evidence/system_holdout_gt_mix_2026-09-26.json` | session-3 (parallel): correction-like vs isolated decomposition of each fold's held-out truth (~99% isolated) |
| `evidence/ownership_resolution_2026-09-26_session3_parallel.json` | session-3 (parallel): fresh GitHub-layer ownership re-resolution of the GEMSDOE family (sibling resolution: `..._session3.json`) |
| `evidence/leaderboard_snapshot_2026-09-26_session3.json` | session-3 (parallel): public leaderboard read; field high 0.3049; the five brief-attributed scores are other entrants |
| `patches/entry_session3_verified_changes.patch` | session-3 (parallel): the CV-buffer fix + entry-docs corrections + geology dossier, applied and fully verified on a scratch clone; **cv.py hunks byte-identical to the sibling's `session3_entry_full_2026-09-26.patch`, which is the recommended one to apply (superset)** |
| `tests/test_session2_additions.py` | session-2 regressions: AUC sanity, trend-band logic, narrative guards, evidence-file pins, patch dry-run |
| `tests/test_session3_additions.py` | session-3 regressions: topk_hard / trace-keep byte-identity with the canonical entry harness, drop-config geometry, pseudo-mask region/off-catalogue constraints, evidence pins, patched-CV geometry |
| `tools/*.py` | the six scripts that produced everything above; each prints what it measured and states what it does not measure |
| `patches/PROPOSED_ENTRY_CHANGES.md` | the changes that belong in `buffedlizard55-lab/6GEMSDOE`, which this session cannot push to (HTTP 403) |

Nothing here is a leaderboard score. The only local measurements of the new-fault-like
population are the `masked_proxy_eval*` and `proxy_cv_fold0` files, and they are
explicitly proxies: USGS SGMC surface mapping, not the competition's expert labels.
| `evidence/nested_policy_cv_session6.json` (+ `_log`, `nested_policy_rule_printed_session6*.json`) | session 6: strictly nested placement-policy check; verdict keep raw/3%/s4 (N3, N4 fail) |
| `evidence/feature_arm_105_session6.json` | session 6: F1, 105 vs 88 channels (0.2419 vs 0.2345, adopted by rule) |
| `evidence/grav_fix_arm_session6.json`, `grav_fix_arm_105_session6.json` | session 6: G1 (88 + gravity fix, passes) and G1b (105 + fix, fails fold clause) |
| `evidence/grav_hg_identity_session6.json` | session 6: `iso_grav_anom_hg` is dG/dx, not \|∇G\|; `iso_grav_anom_slope` is \|∇G\| |
| `evidence/spacing4_candidate_geology_gravfix_session6.json`, `spacing4_candidate_ch105_geology_session6.json` | session 6: gravity-corrected dossiers of the 88- and 105-channel candidates |
| `evidence/label_blind_corroboration_session6.json`, `..._ch105_session6.json`, `candidate_robustness_session6.md` | session 6: label-blind screen and hand reasoning per flagged candidate |
| `evidence/candidate_ch105_report_session6.json` | session 6: gate + overlap report of the 105-channel candidate (bytes in scratch only) |
| `evidence/ownership_resolution_2026-09-26_session6.json`, `leaderboard_raw_2026-09-26_session6.md` | session 6: ownership audit and leaderboard capture |
