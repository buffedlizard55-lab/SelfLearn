# Live site and page reads — 2026-09-26 (session 5)

Read with the platform page fetcher in this session, one fetch per URL. Direct
HTTPS from this sandbox fails TLS for `*.github.io` and `drivendata.org`
(re-verified this session: `OpenSSL SSL_ERROR_SYSCALL` on connect), so every
page read below came through the platform fetcher and is quoted from what it
returned. Nothing on any of these pages is our score.

Ownership (GitHub layer, mechanical, this session):
`evidence/ownership_resolution_2026-09-26_session5.json` — all six URLs are
non-fork repositories of the ONE account `buffedlizard55-lab` (owner id
309556078), which also hosts this review workspace. That resolves the brief's
"ownership unconfirmed" list **at the GitHub layer**: they are our own historical
project copies, not another entrant's property. It does **not** resolve the
DrivenData layer (see the bottom of this file).

## 1. 6GEMSDOE — the designated entry (unchanged bytes, unchanged claims)

<https://buffedlizard55-lab.github.io/6GEMSDOE/>

* Publishes exactly one file: `gems6_hgb88-topk03_33cec71ff0.tif`, 1,652,883 B,
  sha256 `33cec71ff00b3f32d0d59c81c156f3f1…`, 155,021 positive pixels — the same
  artifact re-gated in this session at 13/13 PASS
  (`evidence/submission_gate_session5.json`).
* The **methodology note still contains the false metric claim**, verbatim:

  > "the published metric reduces to DTI = TP_w/(0.8\*n_gt + 0.2\*FP_w + 0.2\*TP_w),
  > which is strictly increasing in the predicted value, so fractional confidence
  > gives score away."

  The first clause is a valid uniform-rescaling identity; the second does not
  follow from it. Measured this session with the entry's own metric
  implementation (`evidence/metric_claim_check_session5.json`): uniform
  rescaling is monotone (verified over 24 values of λ), and hardening a remote
  false positive from 0.01 to 1.0 takes DTI from **0.998 to 0.833**. The
  session-3 patch fixes this sentence; the patch is still **not deployed**.
* The page's own §"Account / repo status" block still says **eleven**
  GEMS-named repositories. The live inventory is now **twelve**
  (`evidence/ownership_resolution_2026-09-26_session5.json`), and the entry's own
  offline doc checker fails two checks because of it
  (`evidence/entry_docs_offline_session5.json`).
* Upload instructions are still step 1 "Download", step 2 "Open the competition
  page and click Submit", i.e. ahead of any account/eligibility confirmation.

## 2. GEMSDOE1 — <https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html>

* Adopted artifact `7f00890a62878d61…` (570,890 B, 172,974 px at 1.0), built in the
  browser from an RLE payload. The page states the blanket-coverage floor as
  **DTI 0.0956** and the catalogue coverage as 1.18%.
* This is the "recall-union" line. It is **not** the designated entry.

## 3. GEMSDOE2 — <https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html>

* Leads with the dual-family union `f68e590f…` (568,065 B, 183,642 emitted px)
  and publishes a three-arm "one-week upload plan".
* **Unsubstantiated attribution still present**, verbatim: arm 1 "if it scores at
  or below **0.1563** (the recall-union's board score)". 0.1563 is held today by
  two *other* entrants — `extradr19` (#24) and `SDCF9` (#25)
  (`evidence/leaderboard_snapshot_2026-09-26_session5.json`). No evidence
  connects any DrivenData account to this workspace, so the phrase "the
  recall-union's board score" must not be repeated as our history.

## 4. GEMSDOE3 — <https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html>

* The "Pindrop" portfolio: three files at a **155,021-pixel (3.00%) budget**,
  one of them a **spaced-node layer at k = 4 px** and one a dense ridge control
  at the identical budget. This is the same placement hypothesis this review
  measured in session 4 and re-measures at the shipping budget in session 5 —
  which makes GEMSDOE3's own controlled pair (nodes vs dense, same budget) the
  closest published analogue. It is still **not** the designated entry, and its
  local scores are stand-ins, not board scores.

## 5. 5GEMSDOE — <https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html>

* Same adopted artifact as GEMSDOE1 (`7f00890a…`) plus a "catalogue hedge"
  candidate (`candidate_s5_catalogue_hedge.tif`, 227,507 px) that adds the 54,533
  catalogue pixels the platform says it does not charge for. Last push
  2026-09-26T17:28Z ("Session 4 … S5-D corridor + S5-F flagship ship"), i.e. this
  repository is being actively developed by a **concurrent** session.

## 6. GEMSDOE4 — <https://buffedlizard55-lab.github.io/GEMSDOE4/>

* Live artifact is now `237f0063a440b2c6…` (505,882 B, 264,247 px at 1.0), policy
  "union k=3 of 5 members; floored at t0=0.124344, dilated 0 px".
* **Session 3's open question is resolved**: the change from `c1da7dd9…` to
  `237f0063…` *is* recorded in the repository's visible history — commits
  `ef0fd2ee` (2026-09-26T05:46:03Z, "Session 34: fold-scoped selection, the union
  holdout audit, and the k = 3 adoption") and `1726ecad` (05:59:44Z). No
  unexplained artifact swap remains. Last push 05:59Z today, also a concurrent
  session.

## 7. Field context

`evidence/leaderboard_snapshot_2026-09-26_session5.json` (parsed from
`evidence/leaderboard_raw_2026-09-26_session5.md`):

| Fact | Value |
| --- | --- |
| Field high | DARD 0.3049 (#1, last submission 3d 19h ago) |
| Organizer reference | `doegemsDrivendata` 0.1847 (#14) |
| Brief's 0.1563 | held by **two** entrants: extradr19 (#24) and SDCF9 (#25) |
| Brief's 0.1560 | smashi34 (#26) |
| Brief's 0.1193 | smrtdoog5 (#41) |
| Brief's 0.1152 | **no longer on the visible board** (SDCF9 moved to 0.1563) |
| Brief's 0.0830 | wbg1 (#50) |
| Our owned public score | none, and none is claimed |

So the brief's score table has drifted since it was written: one of its five
numbers has left the board and another is now ambiguous. That is a change in the
*field*, not in our entry.

## 8. Irregularities flagged, not smoothed over

1. **A 12th GEMS-named repository appeared today.**
   `buffedlizard55-lab/LEARNGEMSDOE` was created 2026-09-26T18:18:32Z — about
   ten minutes before this session started — with a single `# LEARNGEMSDOE`
   README and GitHub Pages built. It was **not** created by this session (this
   session creates nothing); the commit author is the account holder
   (`buffedlizard55@gmail.com`). It is a stub, not a project copy, but it
   publishes a 12th challenge URL. Reported for the account holder; not adopted
   as an experiment arm; not archived from here.
2. **Concurrent sessions are shipping from other repositories in the family.**
   5GEMSDOE (17:28Z) and GEMSDOE4 (05:59Z) both received pushes today while this
   session worked on the designated entry. At the GitHub layer they are our own
   history; against rules §3.4 (three submissions per week per entity) any
   *upload* from more than one copy is exactly the multiplication the limit
   exists to prevent. No upload was made from anywhere in this session.
3. **The designated entry's own docs are stale in three measurable ways**
   (false metric sentence, 11-vs-12 repository count, download-before-account
   ordering). All three are already covered by the existing, fully verified
   entry patch, which still cannot be pushed from here (HTTP 403).

## 9. DrivenData layer — still unresolved, re-verified

The sandbox has no DrivenData session; `gh` authenticates only to GitHub. The
competition data tab redirects unauthenticated requests to `/accounts/login/`
(verified 2026-09-25 and 2026-09-26 in the entry's own `DATA.md`). The
registration identity behind these repositories, rules §1.3 eligibility, the
submission history and the remaining weekly allowance are account-holder-only
facts. **Nothing in this session creates a registration, an upload, a site or a
second entry, and no leaderboard row is treated as ours.**
