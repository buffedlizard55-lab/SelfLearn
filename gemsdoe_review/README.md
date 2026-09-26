# GEMSDOE review — 2026-09-26

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
| `evidence/tilt_derivative_audit.json` | the magnetic tilt-derivative channel audit: a dead channel, a duplicated channel, and a candidate replacement |
| `evidence/geology_dossier.json` | per-candidate measurements for all 193 flagged structures (5-px closing, ≥ 200 px) |
| `evidence/geology_dossier.md` | those measurements rendered with hand-written geological readings and explicit confidences |
| `tools/*.py` | the six scripts that produced everything above; each prints what it measured and states what it does not measure |
| `patches/PROPOSED_ENTRY_CHANGES.md` | the changes that belong in `buffedlizard55-lab/6GEMSDOE`, which this session cannot push to (HTTP 403) |

Nothing here is a leaderboard score. The only local measurements of the new-fault-like
population are the `masked_proxy_eval*` and `proxy_cv_fold0` files, and they are
explicitly proxies: USGS SGMC surface mapping, not the competition's expert labels.
