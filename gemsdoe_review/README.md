# GEMSDOE review — 2026-09-26 (sessions 1–3)

Read `REVIEW.md` first; it is the deliverable, and every claim in it points at one of
the files below.

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
