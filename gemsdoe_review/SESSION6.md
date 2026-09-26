# Session 6: nested check, a gravity-band bug, 105 channels, label-blind candidate screen

Date 2026-09-26 (UTC). Review repo branch `arena/01a0df55-selflearn` (from `61103a2`).
Entry under review: `buffedlizard55-lab/6GEMSDOE` at `e2fe3f4` (unchanged all session).
**No submission was made. No site, account or repository was created or modified. Nothing
was pushed to any GEMS repository.** Every DTI below is a spatial-CV transfer proxy on the
mapped catalogue, **not a leaderboard score**.

## Executive result

1. **Nested policy check: do not adopt.** For each outer quadrant, placement surface, budget
   and spacing were selected on the other three quadrants and scored on the held-out one.
   That gives 0.2547 against 0.2345 for the frozen raw / 3% / spacing-4 policy. The
   pre-registered rule needed four conditions. N3 (beat the matched null seeds on every
   fold) and N4 (a stable surface choice) failed. The extra score is **coverage, not
   skill**: the selected policies beat their own random controls by only
   +0.001…+0.017, against +0.031 for the frozen policy.
2. **A real feature bug, in the entry and in our session-5 review tool.** The supplied band
   `iso_grav_anom_hg` is the **signed E-W derivative dG/dx** (Spearman 0.95), not the
   gradient magnitude (−0.0002). `iso_grav_anom_slope` is the magnitude (0.96). `tmi_hg` is
   fine (1.0). The entry's `grav_asa`/`grav_tilt` (channels 25/26) and the session-5
   dossier's gravity-edge votes were built on the wrong reading. Fixing channels 25/26
   helps at 88 channels (0.2397 vs 0.2345, passes) but not at 105 channels (0.2381 vs
   0.2419; fails its fold clause by 0.0003). The stack already carries correct gravity
   gradient and tilt channels (27, 57–59, 72, 74), so this is a **correctness fix, not a
   score lever**.
3. **105 channels adopted** under the pre-registered F1 rule: 0.2419 vs 0.2345, better on
   3 of 4 folds. It is also better at every other budget and spacing checked, and skill over
   the matched null rises from +0.031 to +0.038. Single seed; see "still unverified".
4. **Candidate screen:** many flags depend on nearby labels, and session 5's "best" ones
   are among them. Only 118 of 943 flagged components (99 of 918 on the 105-channel
   candidate) survive a model that never saw the local labels; 293 (287) are
   label-dependent. Every one of session 5's eight named multi-family candidates is
   label-dependent or intermediate. The flags that do survive, and recur in both
   candidates, are listed in `evidence/candidate_robustness_session6.md`.
5. The session-5 candidate was **rebuilt byte-identically** (sha256 `f807dccf…`). A new
   105-channel candidate `5ff242cd…` was built and gated. It stays in scratch, not in Git.

## Pass 1: implementation and measurements (brief items 1–7)

### 0. Guardrail and ownership (item 7), checked first

`tools/ownership_live_audit.py` → `evidence/ownership_resolution_2026-09-26_session6.json`.

* **GitHub layer: resolved.** All 12 GEMS-named repositories, including **5GEMSDOE,
  GEMSDOE4 and 6GEMSDOE**, are owned by `buffedlizard55-lab` (account id 309556078), with
  0 forks. So those three are *our GitHub account's* repositories.
* **DrivenData layer: not resolvable from here** (it needs a login). Which registration, if
  any, uploaded any file is unknown. **No leaderboard row is claimed as ours, and no other
  site's file or score was used as our data or as a test arm.** One account and one entry
  (6GEMSDOE) remain the working assumption. No second site or account was created.
* **IRREGULARITY:** pushes today to 7GEMSDOE, 8GEMSDOE, LEARNGEMSDOE, 5GEMSDOE and
  GEMSDOE4, all outside this session. 6GEMSDOE is unchanged (`e2fe3f41`). They were not
  touched here, only flagged.

### 1. Field position and the brief's score table

Leaderboard read ~20:20Z ([leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/);
raw capture `evidence/leaderboard_raw_2026-09-26_session6.md`). DARD's 0.3049 is still #1.
The organiser row doegemsDrivendata is at 0.1847 (#14). The brief's numbers appear under
**other account names**:

| Score | Account |
|---|---|
| 0.1563 | extradr19, SDCF9 |
| 0.1560 | smashi34 |
| 0.1193 | smrtdoog5 |
| 0.0830 | wbg1 |

0.1152 was not visible in the rendered top 50.

**IRREGULARITY (flagged, not interpreted):**
* The brief's "three different entrants submitting to the same GEMSDOE3 site" matches three
  accounts (smashi34, smrtdoog5, wbg1) whose last submissions share one timestamp, about
  2026-09-25 18:00Z. That is shortly after the GEMSDOE3 site published a three-file upload
  portfolio (15:24Z).
* If those accounts are one team, rules §3.4 (a team's members may not submit separately)
  would apply. This cannot be verified from public pages. It is an observation for the
  account holder, not a finding.
* The GEMSDOE3 "nodes" file uses the same policy as our spacing-4 candidate.

### 2. Feature engineering vs research priorities (item 1)

* **HGM / tilt derivative, gravity:** see the bug above. Correct gradient and tilt channels
  exist in the stack, built from `iso_grav_anom` at σ = 1.5/3/6 (57–59, 72, 74). The
  earlier claim "gravity tilt is weak (AUC 0.484)" was measured on the **miscomputed**
  channel 26 and is withdrawn. Evidence: `evidence/grav_hg_identity_session6.json` (tool
  `tools/grav_band_identity.py`, features sha `4371c82e…`).
* **HGM / tilt, magnetic:** `tmi_hg` ≡ |∇TMI|. Magnetic tilt is still limited by the
  supplied bands (p99 |TDR| 3.08°, so the ±45° contour depth method cannot be used).
  Unchanged from session 5.
* **DEM curvature / slope break:** slope_of_slope (AUC 0.598) is the strongest single
  topographic channel. It is unchanged and present.
* **Strain / conductivity / seismicity cross-reference:** strain and seismicity Spearman
  0.77 (largely one belt signal). ieq 0.583, deq 0.560, conductivity 0.520.
* **Channel set:** 105 channels beat 88 (F1, pre-registered at 20:14:53Z per the session
  terminal record). Evidence `evidence/feature_arm_105_session6.json`.

| arm (outer folds, raw / 3% / s4) | q0 | q1 | q2 | q3 | mean |
|---|---|---|---|---|---|
| full88 (shipped) | 0.2311 | 0.2298 | 0.2494 | 0.2276 | 0.2345 |
| F1: 105 channels | 0.2376 | 0.2379 | 0.2488 | 0.2431 | **0.2419** adopted |
| G1: 88 + gravity fix | 0.2337 | 0.2406 | 0.2472 | 0.2371 | 0.2397 passes (non-inferior) |
| G1b: 105 + gravity fix | 0.2408 | 0.2375 | 0.2414 | 0.2328 | 0.2381 fails (q3 −0.0103) |

### 3. Spatial CV (item 2): confirmed blocked, buffered, never a random split

* The review CV uses 2×2 quadrants and 4 folds, a 300 m **Euclidean** buffer and
  whole-fault-system purging. Train/score overlap, pixels inside the buffer and shared
  systems are all zero, and every run records this per fold.
* The nested run added inner isolation (inner train excludes the outer quadrant too). It
  reproduced session 5's four frozen fold values exactly.
* The entry's own `cv.py` still uses a 4-neighbour (Manhattan) buffer.
  `patches/cv_euclidean_buffer.patch` was regenerated as a real diff against e2fe3f4
  (`git apply --check` passes).

### 4. Metric-aware placement (item 3)

* Spacing 4 at 3% is intact and is still the frozen policy.
* The nested check found no policy that beats it on skill.
* Maximum skill over the null is at 1–2% budgets with smoothed surfaces (e.g. gauss3 | 1.5% |
  s4: 0.1732 vs null 0.1178), but those budgets score less in absolute terms.

### 5. Submission format (item 4)

* `validate_submission.py` on the shipped file: 13/13 PASS. NaN poison → exit 1, so the
  hard gate on NaN inside the footprint still bites.
* Both local candidates pass: EPSG:32611, 100 m, template shape/geotransform, values in
  [0, 1], NaN only outside the footprint.

### 6. Exec summary / how-to-submit accuracy (item 5)

* `check_entry_docs.py`: offline 35/37. The two failures are `limitations-cover-masking` and
  `geology-dossier-present`. Online: 47/51.
* Live-site and `SUBMISSION_GUIDE.md` inaccuracies, with proposed wording, are in
  `patches/PROPOSED_ENTRY_CHANGES.md` §H:
  - the "strictly increasing" metric claim;
  - "300 m buffer";
  - "proxy 0.1698" presented as an estimate while recommending the dense file;
  - upload steps placed before account confirmation;
  - "11 repositories" (there are 12).
* Correction of my own earlier note: the site's "4×4 blocks" is **accurate** for the
  entry's `cv.py`, so it is not listed as an error.

### 7. Geological reasoning per flagged candidate (item 6)

`evidence/candidate_robustness_session6.md` contains the corrected dossier diff, the
label-blind test, hand reasoning for seven flags, and the cross-check on the 105-channel
candidate.

* **Most robust flag:** the zone 19113 + 18811 (−119.63…−119.66 E, 39.43…39.46 N). Its
  NW-SE strike matches regional shear, and it is strain- and seismicity-supported.
* **Next:** the gravity-edge + strain area around 22742/23009 (−118.11…−118.13, 38.96…38.99).
  It has an NNE strike and a true density contact, a range-front-normal-fault signature.
  This vote exists only because of the gravity fix.
* No named fault is claimed; no fault database was consulted.

## Pass 2: bugs, gaps and review

| # | finding | action |
|---|---|---|
| B1 | `iso_grav_anom_hg` is dG/dx, not \|∇G\| (entry channels 25/26 and our session-5 dossier) | fixed in `tools/geology_dossier.py`. Dossier re-run: gravity-edge votes 104 → 69; "≥ 3 families" 25 → **21**. Entry fix proposed (§F). G1/G1b measured |
| B2 | session-5 doc gave the candidate size as 1,652,883 B (the shipped file's size) | corrected to 1,764,117 B in place, with a note |
| B3 | `cv_euclidean_buffer.patch` was stale | regenerated against e2fe3f4, applies cleanly |
| B4 | pre-registration provenance: the printed-rule JSONs have **no embedded timestamp**. The committed copy of the first one was re-written at 20:35:56Z, after the nested run started (20:29Z). The 20:14:53Z / 20:19:48Z times come from the session terminal record | stated here, not smoothed. The rule text is byte-identical to the rule stored in the run output (checked). G1 (21:00:51Z) and G1b (21:14:37Z) files predate their runs by mtime |
| B5 | `nested_policy_cv.py` was edited while F1 was running (the G1/G1b additions), so F1's recorded `tool_sha256` (`bbd6a669…`) is not the final file | the F1 code path is unchanged. The G1 code is only reached with `--grav-fix` |
| B6 | the candidate builder needed a gravity-fixed path | added `--grav-fix` via a mirror trainer. It is **bit-identical** to the entry trainer on synthetic data (test). The default path is unchanged and still reproduces f807dccf |
| B7 | I had drafted a "0.058 predict-everywhere" site correction that no committed evidence supports | removed |
| B8 | GitHub token invalid (`gh auth status`) | commit is local only; see Blocking |
| B9 | a session-5 test pinned the *stale* state of `cv_euclidean_buffer.patch` | kept the session-5 evidence as history, added `evidence/entry_patch_verification_session6.json` (regenerated patch applies, radius-3 disk check), and updated the test to require the patch to apply |

Tests: `tests/test_session6_additions.py` has 21 tests, all passing. The `gemsdoe-review` CI job
now also runs it. In a CI-like environment (numpy/scipy/rasterio/pytest only, no entry
checkout), sessions 4–6 give 54 passed and 4 skipped. With the entry and sklearn present,
57 passed and 1 skipped. They cover:
- the gravity identity (synthetic plus evidence pin);
- the dossier reading the slope band;
- label-blind percentiles, classes and evidence consistency;
- the F1 and G1/G1b verdicts re-derived from JSON;
- the mirror trainer's channel swap, and its equality with the entry trainer (skipped
  without an entry checkout).

## Pass 3: recheck against the brief and the rules

* One account, one repo, for us: yes. Nothing was created, and nothing from another
  entrant or site was used. Ownership of 5GEMSDOE, GEMSDOE4 and 6GEMSDOE was resolved at
  the GitHub layer and left explicitly unresolved at the DrivenData layer.
* Official sources only: data sha-pinned. Rules
  [PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) (§3.2 AI disclosure, §3.4 three per
  week and team members may not submit separately, §3.6.2 blind final choice); masking
  rule from the [staff forum thread](https://community.drivendata.org/t/11516/4).
* Irregularities flagged: synchronised accounts around GEMSDOE3; concurrent pushes to
  sibling repos; the rank-tables sha (`2b0bede1…`) ≠ the pinned `64a62c3b…`, as in session 5,
  while the features sha matches the pin; the pre-registration provenance (B4).
* Items 1–7 are all addressed above. No random pixel split anywhere.

## What changed / still unverified / blocking / first next session

**Changed (this review repo only):**
- the nested policy check (verdict: keep the frozen policy);
- the gravity-band bug found, measured and fixed in the review tool;
- 105 channels adopted by rule, with a gated 105-channel candidate (scratch, sha `5ff242cd…`);
- a new label-blind screen of every flagged component in both candidates;
- entry proposals F (gravity), G (Euclidean buffer, regenerated) and H (published text);
- the session-5 size error corrected;
- 3 new tools (`nested_policy_cv.py`, `label_blind_corroboration.py`,
  `grav_band_identity.py`) and 2 extended ones (`build_spaced_candidate.py`: `--surface`,
  `--grav-fix`; `geology_dossier.py`: gravity fix);
- 21 tests.

**Still unverified:**
- **single seed**: the 105-vs-88 gap (+0.007) and the gravity effects (±0.005) have not been
  replicated with other seeds, and could be seed noise;
- the channel-set choice was made on the same outer folds (one pre-registered comparison,
  but not nested);
- the DrivenData registration, eligibility and remaining allowance;
- the hidden score of any file;
- the identity of every flagged structure;
- whether the three synchronised accounts are one team.

**Blocking:**
1. **The sandbox GitHub token is invalid again**, so this session's commit cannot be pushed
   or opened as a PR until GitHub is reconnected in Arena.
2. Write access to 6GEMSDOE for patches F/G/H (account holder).
3. Account-holder decisions: which registration, allowance, §3.2 disclosure, and whether to
   spend a slot measuring a spaced candidate.

**First next session:**
1. Reconnect GitHub. Push `arena/01a0df55-selflearn`, open the PR, let the
   `gemsdoe-review` CI job run, then merge.
2. Replicate F1 with seeds 11 and 13 (outer-only, about 16 min each on 2 CPUs) before
   anyone treats 105 > 88 as settled.
3. If the account holder chooses to measure a spaced candidate, the measured-best local
   file is the 105-channel one (`5ff242cd…`, rebuilt by
   `build_spaced_candidate.py --n-channels 105`). Ship it together with its dossier and
   label-blind screen, never alone.
4. Apply G then F then H to 6GEMSDOE from a permitted working copy, rebuild and re-pin the
   features.

### Reproduction

```bash
# entry at ../entry-src (e2fe3f4) with data + features built as in SESSION5.md
cd gemsdoe_review/tools
P=../../../venv/bin/python
$P nested_policy_cv.py --print-rule
$P nested_policy_cv.py --entry ../../../entry-src --scratch /tmp/m88 --out /tmp/nested.json      # ~26 min
$P nested_policy_cv.py --entry ../../../entry-src --n-channels 105 --outer-only --scratch /tmp/m105 --out /tmp/f105.json
$P nested_policy_cv.py --entry ../../../entry-src --n-channels 88  --outer-only --grav-fix --scratch /tmp/m88g  --out /tmp/g1.json
$P nested_policy_cv.py --entry ../../../entry-src --n-channels 105 --outer-only --grav-fix --scratch /tmp/m105g --out /tmp/g1b.json
$P grav_band_identity.py --entry ../../../entry-src --out /tmp/grav.json
$P build_spaced_candidate.py --entry ../../../entry-src --scratch /tmp/c --n-channels 105 --tag spacing4-topk03-ch105
cp geology_dossier.py ../../../entry-src/scripts/_gd.py
(cd ../../../entry-src && $P scripts/_gd.py --pred /tmp/c/candidate_spacing4-topk03-ch105.tif --out /tmp/d.json)
$P label_blind_corroboration.py --entry ../../../entry-src --pred /tmp/c/candidate_spacing4-topk03-ch105.tif \
    --dossier /tmp/d.json --oof-dir /tmp/m105 --out /tmp/lb.json
```
Each arm needs its own `--scratch` directory, because cache names do not encode the
channel count or `--grav-fix`.
