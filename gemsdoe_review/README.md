# GEMSDOE review — 2026-09-26

Read `REVIEW.md` first; it is the deliverable and it links every claim to a file
here.

| path | what it is |
| --- | --- |
| `REVIEW.md` | the review: findings for the seven brief items, the measured evidence, what is not verified |
| `evidence/ownership_audit.json` | every `GEMSDOE*` repository under `buffedlizard55-lab`: owner, fork status, Pages, commit authors |
| `evidence/leaderboard_snapshot.json` | the public leaderboard rows that the brief's five scores correspond to |
| `evidence/scoring_rule_clarification.json` | the official scoring-rule clarification, quoted verbatim, with the consequences for this entry |
| `evidence/masked_proxy_eval.json` | rule-correct (masked-catalogue) proxy scores for the shipped file and its dilated variants |
| `evidence/masked_proxy_eval_all.json` | the same for every candidate artifact found across the repository family |
| `evidence/tilt_derivative_audit.json` | the magnetic tilt-derivative channel audit (dead channel, duplicated channel, candidate replacement) |
| `evidence/geology_dossier.json` | per-candidate measurements for all 193 flagged structures on the `ens12` artifact |
| `evidence/geology_dossier.md` | those measurements rendered with hand-written geological readings and confidences |
| `tools/*.py` | the five scripts that produced the evidence; each prints what it measured and says what it does not |
| `patches/PROPOSED_ENTRY_CHANGES.md` | the changes to apply in `buffedlizard55-lab/6GEMSDOE`, which this session cannot push (HTTP 403) |

Nothing here is a leaderboard score. The only local measurements of the
new-fault-like population are the two `masked_proxy_eval` files, and they are
explicitly proxies.
