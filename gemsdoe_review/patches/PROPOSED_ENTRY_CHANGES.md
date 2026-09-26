# Proposed changes to the entry repository (`buffedlizard55-lab/6GEMSDOE`)

These could not be pushed from this session: the GitHub token available here has
**no write access to `6GEMSDOE`** (`git push --dry-run` → HTTP 403; the API reports
`permissions.push = false`). They are written to be applied by a human, or from a
session with push rights, without further edits.

Everything below is either (a) a script that runs against the repository as it
stands, or (b) a text change with the exact wording and the source it cites.

---

## 1. New scripts (copy into `scripts/`, no edits needed)

| file in `gemsdoe_review/tools/` | destination | what it does |
| --- | --- | --- |
| `geology_dossier.py` | `scripts/geology_dossier.py` | per-candidate measurements: geometry, 21 diagnostics as regional percentiles, six-family agreement, distance to catalogue, local metric value. Writes `data/evidence/geology_dossier.json`. |
| `geology_report.py` | `scripts/geology_report.py` | renders `data/evidence/geology_dossier.md` from that JSON, with hand-written readings kept separate from the measurements. |
| `tilt_derivative_audit.py` | `scripts/tilt_derivative_audit.py` | audits the magnetic tilt-derivative channels and tests a Fourier replacement. Writes `data/evidence/tilt_derivative_audit.json`. |
| `masked_proxy_eval.py` | `scripts/masked_proxy_eval.py` | the rule-correct (masked-catalogue) proxy evaluation; see §3. |
| `check_entry_docs.py` | `scripts/check_entry_docs.py` | re-reads the entry's own prose claims from its artifacts before upload. |

They import `gems.spec`, `gems.metric` and `gems.features`, and default their paths
to the repository root, so they run as-is:

```bash
python scripts/geology_dossier.py --pred downloads/gems6_hgb88-topk03_33cec71ff0.tif
python scripts/geology_report.py
python scripts/tilt_derivative_audit.py
python scripts/masked_proxy_eval.py --pred downloads/gems6_hgb88-topk03_33cec71ff0.tif \
    --labels data/labels.tif --proxy data/evidence/proxy/proxy_catalogue.tif \
    --out data/evidence/masked_proxy_eval.json
python scripts/check_entry_docs.py .
```

Cost, measured on a 2-CPU / 4 GB sandbox: the dossier is ~5 min, the tilt audit
~1 min, the proxy evaluation ~10 s per candidate, the doc check ~1 s.

## 2. `LIMITATIONS.md` — the mask rule is missing

`scripts/check_entry_docs.py` fails exactly one check (`limitations-cover-masking`):
the file does not mention that the catalogue is masked out of evaluation. Verified
source: <https://community.drivendata.org/t/11516> (DrivenData staff, posts 2 and 4).
Proposed paragraph, to be added under the scoring-limitations heading:

> **Known faults are masked out of the score.** DrivenData staff state that pixels
> corresponding to known USGS/INGENIOUS faults are "masked / excluded from
> evaluation, so they do not count towards penalty terms", and that the mask "is
> indeed pixel-exact - it is identical to the provided set of training fault
> labels". Two consequences follow for every number in this repository.
> (1) Our blocked-CV scores are measured against the catalogue, which is *not* the
> scored population: they are optimistic where a prediction hugs a mapped trace and
> silent about the population the prize actually scores.
> (2) A predicted pixel that is near a known fault trace but far from a new-fault
> truth pixel "will be fully penalized, i.e., the buffer does not apply to known
> faults" — so mass spent a few pixels off a mapped trace is priced differently by
> the platform than by our proxy. Staff also confirm that new-fault truth can lie
> within 300 m of a known trace, because "corrections or modifications to existing
> fault traces" are an intended outcome, so thin along-strike corridors are not
> worthless - they are simply unmeasurable locally.

## 3. Use the rule-correct proxy for any upload decision

The new-fault proxy evaluation already in the repository
(`scripts/eval_proxy_catalogue.py`, 2026-09-17) predates the clarification and
implements the *unmasked* metric. Measured difference on the SGMC population:
the shipped file moves 0.0327 → 0.0348 and the GEMSDOE `ens12` artifact moves
0.0999 → 0.1014. The ranking is unchanged, but the rule-correct number is the one
to quote, and the difference is largest for submissions that hug the catalogue
(15.2% of the shipped file's mass sits on catalogue pixels).

## 4. Two channel defects to fix in `src/gems/features.py`

Measured in `data/evidence/tilt_derivative_audit.json`:

1. `mag_asa = sqrt(tmi_hg² + tmi_vg²)` is a duplicate of the provided `tmi_hg`
   band (Pearson r = 1.000000), because `tmi_vg` is ~256× smaller than `tmi_hg`
   (median |·| 0.0090 vs 13.15).
2. `mag_tilt = atan2(tmi_vg, |tmi_hg|)` is dead: |TDR| never exceeds 3.1° for 99%
   of the footprint, so the tilt-depth method the next-steps document asks for
   cannot run on the supplied bands. The ±45° contours it needs occur in 2.2e-5 of
   pixels.

The gravity equivalents are unaffected (`iso_grav_anom_vg` is the same order as its
horizontal counterpart; p99 |grav_tilt| = 88.8°), which is what makes these a bug
rather than a property of the data.

Suggested minimal change, to be validated by the blocked CV before it is adopted:
drop the two channels, and if a tilt derivative is wanted for magnetics, build it
from the RTP grid with a Fourier |k| vertical derivative — **but the naive version
of that operator is not yet validated** (it is implemented and tested in
`tilt_derivative_audit.py`; it produces a realistic TDR but does not separate
mapped faults better than the provided `tmi_hg`, so it should not ship on the
strength of this review).

## 5. Site and repository hygiene

`ACCOUNT_STATUS.md` designates `6GEMSDOE` as the single canonical entry, but eleven
competition-named repositories under `buffedlizard55-lab` all have GitHub Pages
enabled, and `5GEMSDOE` was pushed *after* the canonical designation was written
(2026-09-25T23:44 vs 22:07). The one-entry presentation rule is therefore violated
in form. Remediation is a human action: archive the duplicates (the data bridge
path lives in `GEMSDOE` and must be relocated first, as `ACCOUNT_STATUS.md` already
says), and pick exactly one site to publish.
