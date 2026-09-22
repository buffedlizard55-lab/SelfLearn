# Build passes and audit log

The brief asked for the work to be done line by line, to be checked rather than
asserted, and to be re-checked after it was built. This document records what each
pass did, what it found wrong with the previous pass, and how each claim about the
implementation can be checked again.

The numbering is chronological. Nothing here is a plan: everything listed as fixed was
verified after the fix with the command shown.

## Pass 1 - build and first end-to-end run

Built the engine, the data files, the experiment scripts, the test suite and the
published site. First live run against the real sources.

What the first run exposed:

| Defect | Evidence | Fix |
| --- | --- | --- |
| The library could not load: `KeyError: 'tasks'` | first live run | Stream definitions were replaced by a single `STREAM_FILES` table that lists every stream, including contradictions, tournaments and tasks |
| Claim ids minted phantom numbers (`'9'` from a hex id) | the audit reported invented numerics | `util.strip_identifiers` removes `sha256:<hex>`, `<word>-<hex>` and long hex runs before numbers are extracted |
| Derived statements ("this question is supported by N claims") had no document to be checked against | 11 error irregularities on the first live run | Derived claims became a first-class kind: `claim_kind=derived`, `context_numbers`, a stored computation record, re-checked by `verify_derived`, and exempted from the link check only when they carry their figures |
| GitHub search returned popular but off-topic repositories | the `readme` qualifier matched README text | Query narrowed to `in:name,description`; a relevance filter drops results sharing no meaningful token with the query and reports how many were dropped |
| Every retrieved document began with scaffolding that could be lifted as a claim | a claim reading "Values are copied from the response without change" appeared in the library | `render_attributed_record` gives every sentence a named subject, and `grounding.strip_scaffolding` removes scaffolding lines before claims are cut |
| `TypeError: object of type 'int' has no len()` in the run summary | second live run | `SourceStatus.items` is a count; the summary now sums it and the figure is named `documents_retrieved` |
| A closed TLS session was retried three times per request | 13 warnings and a slower run | Session-close errors are classified as terminal *unreachable* and recorded as a gap with a remedy |

Result at the end of Pass 1: a live cycle that completed, 141 claims from 32 stored
documents, 4 topics, 24 competing candidates, 170 recorded criticisms, 8
contradictions, 2 experiments, and a site of 27 files - with one warning: five
registered sources were unreachable from the build environment.

## Pass 2 - review for bugs, missing requirements and edge cases

Reviewed the whole repository against the brief and the design document, looking for
things that were wrong, missing or unproven. Fixes, each with the evidence that
prompted it:

| Defect | Evidence | Fix |
| --- | --- | --- |
| Both the live and the fixture path crashed with `EvidenceRecord.__init__() got an unexpected keyword argument 'topics'` | `run --mode live`, `run --mode fixture --offline` | The stray keyword was removed from two constructors; only `SourceStatus` carries a topic stamp |
| Per-topic source tables showed every source, not this topic's | reading the rendered page | `SourceStatus.topics` is stamped by the collector and the report filters on it, keeping unstamped rows visible rather than dropping them |
| A reversed direction of change was accepted as `supported` ("improves degradation" against a passage that said degradation occurs) | a verification probe | Direction-pair and universality-versus-hedge rules were added as *caps*: the claim is published as needing review with the reason. Two labelled cases (`c25`, `c26`) and four unit tests were added |
| Three registered sources pointed at documentation pages the operators had moved; PatentsView had been folded into the USPTO Open Data Portal | live web checks | The register's documentation URLs were corrected and the PatentsView migration is flagged for review in `docs/SOURCES.md` |
| The published limitations claimed an optional language-model adapter existed | `grep` found no model code anywhere | The limitation was rewritten to state that no model is called at any stage, and to say what adding one would require |
| Running `selflearn calibrate` erased the record of the thresholds actually in force | `state/calibration.json` showed `applied: false` after a cycle had applied a calibration | A non-applying sweep now carries the applied record forward; a fresh process reads the applied set from the state file instead of silently reverting to the defaults |
| Topic page URLs were derived from the title rather than the topic's stored slug | the published topic files were long and would move if a title changed | One `topic_slug` helper is used everywhere, so addresses are short and stable |
| `verify/__init__.py` did not export the verification surface; `think/tournament.py` held a dead helper; `competition.py` imported `Persona` twice | code review | Exports completed (19 names, asserted by a test); dead code removed; duplicate import removed |
| Requirements cited documents that did not exist (`docs/ARCHITECTURE.md` and six others), the repository had no README, no workflows and no tools | the requirements matrix itself | The seven documents were written, the README was written, two workflows were added, and four reviewer tools were added under `tools/` |
| The workflow's smoke cycle had nowhere to run without polluting the repository | designing the CI job | `SELFLEARN_ROOT` lets a run be pointed at another root; CI runs a real cycle into a temporary directory |
| The experiment reproducibility tool compared wall-clock fields and reported a false difference | running `tools/reproduce_experiment.py` | Comparison is recursive and ignores timing fields explicitly, reporting how many were ignored: the comparison counts, which are what the engine claims, match exactly |

## Pass 3 - re-check against the original request

Every requirement in the brief and every section of the design document was re-read
and checked against what is actually in the repository. The result is the requirements
matrix in `data/requirements.json` (44 rows), rendered at `docs/requirements.html` and
exported to `docs/data/requirements.json`. Rows that are narrower than the design are
marked `partial` with the gap stated; nothing was marked implemented without a file and
a way to check it.

The commands used for the final check, and what they returned:

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -t . -p "test_*.py"` | 65 tests, all passing |
| `python3 -m selflearn run --mode live` | one complete cycle, exit 0, run `run-538d83841b75` |
| `python3 -m selflearn audit` | 141 claims re-checked against 32 stored documents, 0 findings |
| `python3 -m selflearn calibrate` | 26 labelled cases, accuracy 1.00, macro F1 1.00, 0 false supports |
| `python3 -m selflearn sources --probe` | 32 sources probed, 1 reachable from this environment, 4 requiring credentials |
| `python3 -m selflearn status` | the counts published on the site |
| `python3 tools/check_claim.py` | a claim, its document, its stored hash and a fresh re-check, all agreeing |
| `python3 tools/reproduce_experiment.py sorting-comparisons-v1` | re-run identical to the recorded result on every compared field |
| `python3 -m selflearn run --mode fixture --offline`, `--mode snapshot` | both complete and label their evidence mode on every page |
| `python3 -m selflearn site` | 27 files written, including all seven documents rendered into `documents.html` |

## Pass 4 - the roadmap layers (2026-09-21)

Implemented the next items on the roadmap: the substance filter, cross-document
synthesis, change-driven scanning, topic invention, and the PatentsView repair. Before
writing any adapter code, the operator documentation for every endpoint touched was read
and the parameter names taken from it rather than from memory; each is cited in
`docs/SOURCES.md`.

| Defect | Evidence | Fix |
| --- | --- | --- |
| The PatentsView register entry pointed at an endpoint that no longer serves the API, and the documentation URL redirected to a portal home page | <https://data.uspto.gov/support/transition-guide/patentsview> states the migration date (2026-03-20), that the PatentSearch API has no estimated return, and that old keys are invalid for ODP | The register now points at `https://api.uspto.gov/api/v1` with `USPTO_ODP_API_KEY`; `UsptoOdpSource` queries the two documented endpoints; the flag is closed with the operator's statements rather than deleted |
| Raw-response evidence ids were built from `hash()` of the URL | `hash()` is salted per process, so the same document would be stored again under a new evidence id every run | `raw_identifier()` derives the id from a sha256 of the rendered text; a test asserts stability |
| Topic invention proposed seven topics out of the engine's own scaffolding ("Sentence below names", "Adoption signal") | the first live run published them; the phrase recurs in every document because the adapters write it | Candidates are drawn only from a source's own prose: scaffolding is stripped, field-label lines and raw `path = value` dumps are excluded, the engine's own records are skipped, and a regression test pins it |
| A synthesis statement could in principle quote a digit from a source *name* ("ClinicalTrials.gov API v2") | reading the composed sentence | Source names are kept out of the sentence entirely and rendered as citations instead, so every figure in a synthesis statement comes from a cited document |
| The scan window was one day longer than requested | `scan_window(None, max_days=7)` returned 8 | The day count is computed from the elapsed interval only when there is a previous scan; the first scan uses the requested look-back, and the report says it is a look-back |

## Pass 5 - review of pass 4

| Defect | Evidence | Fix |
| --- | --- | --- |
| The invention layer had no defence against the engine studying its own vocabulary | the seven rejected topics above | Provenance is published with every proposal, rejected candidates are published with the reason, and `tools/reject_topic.py` lets a reviewer close one without destroying the record; the seven were closed that way and the reason is stored on each |
| The site had no way to show a claim's substance or a synthesis statement's citations | reading the rendered topic page | The facts table gained a Substance column with the label and score, each claim expands to its weighted components, and a new Cross-document synthesis section lists every cited claim with its own verdict and link |
| Old claims had no substance record, so pages built from the stored library would show empty cells | `python3 -m selflearn site` on the pre-existing library | `ensure_substance()` scores any claim without a stored record at render time, so the published score always comes from the rule in force |
| The link check died without writing its report when its output was piped | running `tools/verify_links.py \| head` | The report is written before any long output is printed, and the tool is invoked in CI without a pipe |
| The engine's own experiment records entered the topic candidate pool | `source_ids present: ['github', 'selflearn_experiment']` | Records whose `source_id` starts with `selflearn`, and fixture records, are excluded from the candidate pool |

## Pass 6 - re-check against the brief

Every claim about this session's work was re-derived by running the code rather than
by reading it. The commands used and what they returned are in the table below; the
same commands can be re-run in the order given.

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -t . -p "test_*.py"` | 107 tests, all passing (66 before this session, 41 added) |
| `python3 -m selflearn audit` | 206 claims re-checked against 34 stored documents, 0 errors, 0 warnings, 1 info finding (the 24 superseded statements, excluded from re-verification by design) |
| `python3 -m selflearn run --mode live` | one complete cycle, exit 0, run `run-ea9b18aa72fa`, 1 of 6 polled sources reachable from this sandbox |
| `python3 -m selflearn scan --offline` | five mechanisms reported with their windows, none polled, no items claimed as new |
| `python3 -m selflearn credentials` | 4 keyed sources, 0 enabled, each with the operator's key page |
| `python3 tools/verify_links.py` | 108 unique URLs: 22 resolved (the GitHub hosts this sandbox can reach), 86 recorded `unreachable` with the transport error |
| `python3 tools/reject_topic.py --id ...` | seven scaffolding-derived topics closed with a stored reason |
| `python3 -m selflearn site` | 29 files written; 0 current cross-document statements published, 24 retired ones listed with the reason on the pages that carried them |

The numbers above are re-derived on every cycle rather than typed once. `reports/run_summary.json`
from the run named in the table is the machine-readable copy of the same figures, and the
narrative guard in `selflearn/loop.py` rejects any summary sentence containing a figure that is
not in that dictionary.

## Pass 7 - the defect found in the engine's own published output

Pass 6 verified that the engine ran and that its numbers were consistent. It did not read the
sentences the engine had written. Reading them found a false statement on a published page:

> "Two documents disagree about a value expressed in stargazer: one reports 02 and the other
> reports 04."

The statement was *verifiable* and false. Both digits do appear in the claims it cited, so the
verification gate passed; what it did not check is what the digits meant. They were the day and
the hour of two ISO timestamps in two GitHub records for two unrelated repositories.

| Defect | Evidence | Fix |
| --- | --- | --- |
| The synthesis figure extractor read the components of ISO dates and times as quantities | `figures_with_units("pushed_at 2026-08-02T01:55:40Z, stargazers_count 37459")` returned `2026`, `08`, `02`, `55`, `40` as measured values | `_DATE_TIME_RE` strips ISO dates, timestamps and bare years in 1600-2199 before figures are extracted; the same input now returns `37459` and `2490` only |
| A figure took its unit from the *following* word, which in a rendered field list is the next field's label | the same call returned `37459` labelled `fork` | Adapters render fields as `label value`, so a label immediately before a number (recognised by the underscore the API gave it) is used as the unit; `37459` is now `stargazers_count` |
| "Agreement" was declared between claims from one operator | with only GitHub reachable, every agreement statement compared one source's records to itself | `MIN_SOURCES_FOR_SYNTHESIS = 2`: an agreement or range statement needs at least two distinct `source_name` values, not just two documents |
| "Disagreement" was declared between unrelated subjects | the two cited claims described different repositories that shared no measured quantity | `_shares_subject()` requires at least one shared content word, computed after `strip_rendered_labels()` removes the adapters' field rendering, so "record", "reports" and field labels cannot count as a subject |
| A corrected rule left the old statements published, because the streams are append-only | `library/claims.jsonl` still held all 24 statements composed by the buggy extractor | `Claim.superseded` and `loop.retire_stale_synthesis`: a statement the current rules no longer produce is marked with a reason, excluded from the facts and synthesis sections, excluded from the audit's re-verification, and listed under "Retired statements" on the page that carried it. All 24 were retired this way; none was deleted |

The honest consequence: with one reachable source, the synthesis layer now composes **zero**
statements. That is the correct result for this corpus - there is no second source to agree or
disagree with, and no shared subject between two registry records - and the site says so on every
topic page instead of manufacturing a comparison. Six tests cover the regression:
`test_date_fragments_are_never_read_as_quantities`,
`test_a_field_label_preceding_a_number_is_its_unit`,
`test_one_operator_repeating_a_figure_is_not_agreement`,
`test_two_unrelated_records_are_not_described_as_disagreeing`,
`test_the_same_subject_measured_differently_by_two_sources_is_a_divergence` and
`test_a_withdrawn_statement_is_retired_not_deleted`.

The wider lesson, recorded here because it applies to every future layer: passing the verification
gate proves that a statement's figures exist in the evidence. It does not prove the statement is
*about* what it appears to be about. Anything that composes new sentences from old ones needs a
semantic gate of its own, and the gate has to be written before the layer is published, not after
a reader notices.

## Known remaining defects and gaps

These are open, published, and are the honest answer to "what is still wrong":

1. **The claim corpus is metadata-heavy.** In this environment only GitHub was
   reachable, so most accepted claims describe repositories rather than the subject
   matter of the question. This is a consequence of egress, not of the verifier.
2. **Unit substitution is undetectable.** Labelled case `c23` documents it and is
   excluded from calibration with a recorded reason.
3. **PatentsView's endpoint has moved** - resolved this session: the adapter now targets
   the USPTO Open Data Portal, proven against the operator's documented request and
   response shapes, but not yet against a live response, because no key is configured.
4. **No keyed source has ever been polled**, because no key is present in this
   environment. `python3 -m selflearn credentials` lists exactly which are missing and
   where each free key is issued.
5. **New topics are proposed from the engine's own retrieval.** Invention is implemented
   and gated, but the candidate pool is what the engine has retrieved, not an open crawl
   of the web, so section 12 of the design document stays marked partial.
6. **The store never compacts.** Append-only streams grow without pruning.
7. **Two of the four experiment families ran in the published cycle.** The catalogue
   holds four; two are matched to the questions the manager chose.
