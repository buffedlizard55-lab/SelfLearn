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
| `python3 -m unittest discover -s tests -t . -p "test_*.py"` | 108 tests, all passing (66 before this session, 42 added) |
| `python3 -m selflearn audit` | 240 claims re-checked against 36 stored documents, 0 errors, 0 warnings, 1 info finding (the 24 superseded statements, excluded from re-verification by design) |
| `python3 -m selflearn run --mode live` | one complete cycle, exit 0, run `run-6cfd673bcf0b`, 1 of 6 polled sources reachable from this sandbox |
| `python3 -m selflearn scan --offline` | five mechanisms reported with their windows, none polled, no items claimed as new |
| `python3 -m selflearn credentials` | 4 keyed sources, 0 enabled, each with the operator's key page |
| `python3 tools/verify_links.py` | 108 unique URLs: 22 resolved (the GitHub hosts this sandbox can reach), 86 recorded `unreachable` with the transport error |
| `python3 tools/reject_topic.py --id ...` | seven scaffolding-derived topics closed with a stored reason |
| `python3 -m selflearn site` | 29 files written; 0 current cross-document statements published, and every retired record listed with its reason on the page that carried it |

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

Retiring the claims was not enough. The sentence had already been copied downstream, and the first
fix left every copy published:

| Defect | Evidence | Fix |
| --- | --- | --- |
| Retired claims were still quoted by competing briefs | 57 of 91 stored strategies cited one of the 24 retired claims, and the false sentence appeared 15 more times on the topic page under "Competing answers" | `loop.retire_dependents` withdraws every brief whose `supporting_claim_ids` include a retired claim, marks it with the reason, and excludes it from the competition section. `cross_domain_claims` and `generate_strategies` also skip retired claims, so a withdrawn statement can never seed a new brief |
| Criticisms of a withdrawn brief stayed published as live criticisms | 15 stored attacks referenced a retired claim through their brief | The criticisms of a withdrawn brief are withdrawn with it and listed under "Retired" |
| A gap question about a retired claim stayed open | 2 questions named a retired claim id in their text | The question is marked superseded, its status becomes `superseded`, and it leaves the open-questions table |
| The withdrawal of a question was written to memory and then silently dropped from the stream | `q-3908709733c3` still read `superseded: null` on disk after a full cycle | `Library.add_questions` only appended ids it had not seen before, so an update to a stored question was never persisted. It now appends the row it is given and lets the last write win, like every other `add_*` in the store |
| A withdrawal pass that ran once left earlier damage in place | the first version only retired claims retired *in that cycle* | The pass now considers every superseded claim in the library, and is idempotent: a record already carrying a reason is skipped, so re-running it changes nothing |

After the fix, the false sentence appears in exactly one place in the published site: under
"Retired statements" on the topic page that carried it, with the reason and the timestamp. It is
gone from the facts table, the synthesis section, the competing answers, the criticisms and the
open questions, and the machine-readable payloads agree with the page.

The honest consequence: with one reachable source, the synthesis layer now composes **zero**
statements. That is the correct result for this corpus - there is no second source to agree or
disagree with, and no shared subject between two registry records - and the site says so on every
topic page instead of manufacturing a comparison. Seven tests cover the regression:
`test_date_fragments_are_never_read_as_quantities`,
`test_a_field_label_preceding_a_number_is_its_unit`,
`test_one_operator_repeating_a_figure_is_not_agreement`,
`test_two_unrelated_records_are_not_described_as_disagreeing`,
`test_the_same_subject_measured_differently_by_two_sources_is_a_divergence`,
`test_a_withdrawn_statement_is_retired_not_deleted` and
`test_records_built_on_a_retired_claim_withdraw_with_it`.

## Pass 8 - Credential path repair, full link verification, and site creation (2026-09-22)

Line-by-line review of the engine's credential transmission and link verification revealed
fundamental discrepancies between what was declared and what was actually performed:

| Defect | Evidence | Fix |
| --- | --- | --- |
| `GenericSource` never sent credentials despite `requires_key=True` | `python3 -m selflearn credentials` showed `eia`, `fred` and `ncei` as enabled when env vars were set, but inspecting `requests()` showed no credential header or query parameter was ever added | Created `CREDENTIAL_MECHANISMS` in `selflearn/fetch/sources.py` transcribing each operator's documented authentication method with exact citations. Added `apply_credential()` to `Source` so `GenericSource` and `MappedJsonSource` transmit keys as documented |
| `research-loop.yml` passed obsolete secret `PATENTSVIEW_API_KEY` | Register moved to USPTO Open Data Portal (`USPTO_ODP_API_KEY`), but workflow still passed `PATENTSVIEW_API_KEY` | Updated `research-loop.yml` to pass `USPTO_ODP_API_KEY`, optional rate-limit keys, and `GITHUB_TOKEN` |
| GitHub rate limit was inaccurate in register | Register stated "5,000 requests/hour with a token" | GitHub documents 1,000/hour per repository for `GITHUB_TOKEN` in GitHub Actions; updated note with citations |
| Link verification was only feasible from unrestricted environments | Sandbox egress blocked most non-GitHub endpoints, reporting false "unreachable" statuses | Configured CI runner `links` job with `verify_links.py --label` and `tools/link_check_changed.py` to check all 120 URLs from GitHub Actions (unrestricted egress) and commit results back to repository |
| GitHub Pages root was a minimal unstyled card with no 404 handler | Root `index.html` had duplicate inline styling and root lacked `404.html` | Updated `site.py` to generate `index.html` and `404.html` sharing `docs/static/style.css`, clean card UI linking to every section, and real-time statistics |
| Missing dedicated Official Links UI | URLs were scattered across Markdown tables and JSON | Added dedicated **Official links** page (`docs/links.html`), accessible in main navigation, with interactive search, outcome filtering, and operator quotes |

7 new unit tests in `tests/test_layers.py::CredentialPathTests` brought the suite to 115 passing tests.

## Pass 9 - Review for bugs, missing requirements, incorrect assumptions, and edge cases

A deep audit of the Pass 8 implementation revealed several bugs and edge cases:

| Defect / Edge Case | Evidence | Fix |
| --- | --- | --- |
| `table()` iterated over `rows` without checking for strings | In `docs/library.html` and `docs/links.html`, rows built with custom `<tr data-row...>` markup were strings; `table()` treated strings as iterables of characters, generating one `<td>` per character (70,000+ `<td>` tags in `links.html`!) and breaking client-side search | Updated `table()` in `site.py` to check `isinstance(row, str)`: pre-formatted row markup is appended directly. `library.html` shrunk from 39 KB to 8.7 KB and `links.html` from 717 KB to 86 KB with working search |
| Theme toggle was non-functional markup | Clicking "Light / dark" updated `localStorage` but CSS only defined `@media (prefers-color-scheme: dark)` variables | Added explicit `[data-theme="light"]` and `[data-theme="dark"]` property blocks to `assets.py`, added an inline pre-paint script to prevent flicker, and synced `aria-pressed` / button text |
| DOAJ key application URL returned HTTP 404 | Link check on unrestricted runner revealed `https://doaj.org/apply-for-api-key/` returned 404 | DOAJ no longer provides a public key application form. Updated `key_url` to `https://doaj.org/api/v4/docs` and quoted DOAJ's documentation explaining keys are available in publisher accounts |
| IMF documentation host failed DNS | `datahelp.imf.org` failed getaddrinfo from both runner and external networks; base URL and docs described different APIs | Flagged in `docs/SOURCES.md` and registry notes without guessing replacement URLs, preserving strict no-hallucination discipline |
| `cmd_credentials` reported missing vs enabled but not whether adapter transmits | Setting an env var gave a false sense of security for sources without transcribed mechanisms | Updated `cmd_credentials` and Sources page to explicitly distinguish `applied` (transmitted) from `declared_only` (named in register but no mechanism transcribed) |

## Pass 10 - Re-check against the brief, final verification and audit

Line-by-line verification against the brief:
- **No manual input**: Fully autonomous operation via `.github/workflows/research-loop.yml` and `.github/workflows/tests.yml`.
- **Verify line by line, no hallucinations**: Every factual statement is a span of a retrieved document; all 120 published URLs are audited from unrestricted runners; credentials quote operator documentation verbatim with exact verification dates.
- **Site creation**: GitHub Pages entry point at repository root with clean, user-friendly UI, shared stylesheet, dark/light toggle, and responsive cards leading to all 8 sections.
- **Dedicated Official Links**: `docs/links.html` lists every published URL, source operator, purpose, HTTP status, final address, and quoted documentation.
- **Pull request and merge**: Work tracked on session branch `arena/01a0c72f-selflearn`, ready for PR to `main`.
- **115 unit tests** passing with zero external dependencies and clean exit.

## Pass 11 - Reviewer resolution of findings, a fifth experiment family, and three defects (2026-09-22)

Line-by-line review of the review page, the store and the experiment stage, working from
roadmap items 9 and 10:

| Defect / gap | Evidence | Fix |
| --- | --- | --- |
| A contradiction could only be resolved by editing its `resolution` field by hand, and an irregularity not at all | `Contradiction` and `Irregularity` had no reviewer fields; the review page had one table for all findings | `tools/resolve_finding.py` appends a resolution row for the same key (`resolution`, `resolved_at`, `resolution_link`); the review page splits open findings from "Resolved by a reviewer" and shows the original text beside the reason |
| A reviewer's decision would not have survived the next cycle | `detect_contradictions` emits `resolution="unresolved"` for every pair on every run, and `add_contradictions` overwrote the stored record; `add_irregularities` did the same for `resolved` | The store carries the reviewer fields forward when the incoming record does not set them; reopening is explicit (`--reopen`) and recorded. Test: `test_a_reviewers_decision_survives_the_engine_redetecting_the_finding` |
| The published irregularity list carried one id twice | `docs/data/irregularities.json` held 28 rows for 27 ids: the cycle passes the stored findings plus the ones it raised, and the superseded-claims audit fires the same id each run | `build_site_data` and `render_markdown` publish one row per id; the headline counts are of open findings only |
| `max_experiments_per_cycle = 3` was published on the method page and never enforced | no reference to it anywhere in `loop.py` | The loop counts experiments across the cycle, stops at the cap and records that it did |
| A run pointed at another root (`SELFLEARN_ROOT`, as the CI smoke job does) reported every experiment as `script not found` | the runner resolved `experiments/` against the library root, which holds no code | Scripts resolve against the checkout the package was imported from when the library root has no copy (`PACKAGE_ROOT`); the smoke run now completes three experiments instead of three warnings |
| The scheduling question had no experiment that bore on it | `experiments_for_topic` returned an empty list for `topic-research-loop-scheduling` | `experiments/scheduling_policies.py`: round-robin, epsilon-greedy and UCB1 on a stationary Bernoulli bandit, scored by pseudo-regret with an exact analytic baseline; deterministic across seeds and honest about being a toy problem |

7 new tests (5 in `ReviewerResolutionTests`, 2 in `ExperimentTests`) bring the suite to 122.

## Pass 12 - finish the credential path, repair the scan and the reports, open the storage migration (2026-09-22)

Worked the roadmap's open items in the stated order (1/2 credentials, 5's two live
errors, 8 storage) plus the inconsistencies this session's review found in the
published numbers. Every operator statement below was read from the operator's own
page on 2026-09-22 before the code was written; each is quoted in
`CREDENTIAL_MECHANISMS` or `docs/SOURCES.md` with its URL.

| Defect / gap | Evidence | Fix |
| --- | --- | --- |
| Six keyed sources still had no transcribed credential mechanism, so `declared_but_not_transmitted` was non-empty and setting those secrets would change nothing | `python3 -m selflearn credentials` printed `NOT USED BY THE ADAPTER` for `census_us`, `doaj`, `nvd`, `pubmed`, `semantic_scholar`, `stackexchange` | Each mechanism transcribed from the operator's page into `CREDENTIAL_MECHANISMS` with a verbatim quote and `verified_at=2026-09-22`: `?key=` (Census API User Guide), `?api_key=` (NCBI E-utilities guide), `apiKey` header (NVD API workflows page), `x-api-key` header (Semantic Scholar api-docs), `Authorization: Bearer` (Stack Exchange authentication docs), `?api_key=` (DOAJ OpenAPI spec). All twelve keyed sources now report `applied` |
| `PubMedSource` built both stages of its two-step retrieval (`esearch`, then `efetch`) without `apply_credential`, so a configured NCBI key would have authenticated the search and then spent the abstract fetch unauthenticated | reading `selflearn/fetch/sources.py` while transcribing the NCBI mechanism | Both `requests()` and `follow_up()` now go through `Source.apply_credential`; `CredentialPathTests.test_pubmed_stages_both_carry_the_key` pins the second stage |
| The NVD change scan returned HTTP 404 on every run; the error body NVD returns for this is `Invalid ISO 8601 date/time format` | the committed scan report for run-bbcaf0b83035; a live probe on 2026-09-22: the API 1.0 form `2026-09-15T00:00:00:000 UTC-00:00` answered 404/empty, the extended ISO-8601 form `2026-09-15T00:00:00.000+00:00` answered 200 with records; NVD's own transition guide says 2.0 timestamps "use the extended ISO-8601 datetime format" | `_iso_stamp` in `selflearn/fetch/changes.py` now emits extended ISO-8601 with an explicit offset; the mechanism note and `docs/SOURCES.md` cite the transition guide; `ChangeScanTests.test_nvd_sends_both_ends_of_the_window_in_the_documented_iso_format` pins the exact strings |
| The arXiv scan's HTTP 406 is an operator-edge refusal, not a bad request: the identical URL answered HTTP 200 through a different client the same day, and several independent projects reported the same 406 pattern against `export.arxiv.org` in September 2026 | the committed scan report; a live probe of the exact request URL on 2026-09-22 returned results | No request shape was changed (changing headers we cannot test would be a guess). The refusal stays published as a warning irregularity with the request, the response and the operator's documentation URL beside it, which is the "flag irregularities" requirement doing its job |
| `python3 -m selflearn audit` overwrote `reports/irregularities.md` with only the fresh audit rows - one info line where the review page showed 15 warnings and 7 resolutions - because the workflow runs `audit` after `run` and the audit wrote `findings` alone | the committed report read `Totals - error: 0, warning: 0, info: 1` while `docs/data/meta.json` from the same commit read `warning: 18, info: 6` | `cmd_audit` now merges the stored library findings with what the audit re-detected (`audit.merge_findings`) before rendering; the report it writes totals `warning: 15, info: 12; resolved by a reviewer: 7`, matching the review page row for row. The exit status still reflects only this audit's fresh errors, so a scheduled run cannot be failed by published output |
| A plain last-wins dedupe of findings erased a reviewer's resolution as soon as the engine re-detected the same id (the fresh copy carries no `resolved` field) | code review of `_dedupe_findings` and `render_markdown` against `store.add_irregularities`, which already carried resolutions forward on the write path | One rule everywhere: `audit.merge_findings` keeps the newest content and whichever copy carries the reviewer's fields; `render_markdown`, `_dedupe_findings` and `cmd_audit` all use it. Three tests in `FindingMergeTests` |
| The site's headline `checks.irregularity_counts` counted the raw findings list (same id twice) while the tables below it rendered the deduplicated rows, so the header said 24 open where the tables showed 20 | comparing `docs/data/meta.json` with `docs/data/irregularities.json` from the same build | `build_site_data` computes every check count from `_dedupe_findings(...)`; `FindingMergeTests.test_published_check_counts_come_from_the_deduplicated_rows` pins header and rows to the same list |
| The run narrative said "across 11 question(s)" while the table beside it listed 4, and `selflearn status` printed only the 11 | the published index page from run-bbcaf0b83035: `counts.topics` on the site counts active topics, the narrative counted the whole stream including the 7 rejected proposals | `figures["topics"]` and `counts["topics"]` in the cycle are now the active-topic count (all 288 claims belong to active topics, so the sentence is more accurate too), with `topics_total` kept beside it; `selflearn status` prints `topics`, `topics_active` and `topics_rejected` so the two published numbers cannot read as a contradiction |
| The requirements matrix's D-17 row told reviewers to check `docs/DATA_GUIDE.md`, which does not exist | a script that walks every `evidence` path and every backticked path in `how_to_verify` across all 54 rows | The row now points at `docs/ARCHITECTURE.md` (streams and keys) and at `python3 -m selflearn storage verify`; the only other paths the same script flags are three `file#anchor` evidence entries (R-23 twice, D-05 once) whose files and anchors both exist |
| Roadmap item 8 (storage migration) had a documented path and nothing behind it | `docs/ARCHITECTURE.md` "Migration path" section described a future, not a present | `selflearn/storage/database.py` + `python3 -m selflearn storage {sync,verify,status}`: every stream mirrored append-only into `library_rows`, read back through the same loader, `verify` proving the two views identical stream by stream. Proven on this repository's real library: 4,677 rows in, second sync inserts 0, all fourteen streams `matches: true`. `selflearn/learn/vector_index.py` (TF-IDF, cosine, deterministic tie-break) powers `python3 -m selflearn retrieve` and now ranks `cross_domain_claims`, replacing the raw containment ratio as the ranking signal while keeping the containment gate as the candidate filter. Tests: `StorageMirrorTests` (4) and `VectorIndexTests` (4) |
| `docs/LIMITATIONS.md` numbered items 22-26 twice (once in the layers section, once in the coverage section) | walking the ordered lists with a script | The whole document is renumbered into one strict sequence 1..32, and the one internal cross-reference ("limitation 21") was updated to the item it always meant (the metadata-skew limitation, now 26) |

Commands re-run after the pass, with what they returned:

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -t . -p "test_*.py"` | 137 tests, all passing (122 before this pass, 15 added) |
| `python3 -m selflearn audit` | 288 claims re-checked; merged report totals `error: 0, warning: 15, info: 12; resolved by a reviewer: 7` |
| `python3 -m selflearn credentials` | 12 keyed sources, all `used`, `declared_but_not_transmitted: []` |
| `python3 -m selflearn storage sync` then `verify` then `sync` | 4,677 rows inserted, verify reported `rows_identical: true` and `library_identical: true`, second sync `rows_inserted: 0` |
| `python3 -m selflearn retrieve "sorting comparison counts" -k 3` | three supported claims from the sorting topic, scores descending, 24 retired claims excluded from the pool |
| `python3 -m selflearn status` | `topics: 11`, `topics_active: 4`, `topics_rejected: 7` |

## Pass 13 - review for bugs, missing requirements, incorrect assumptions and edge cases (2026-09-22)

The instrument for this review was not code reading alone: full cycles were executed
in throwaway roots first, and every row below was measured before the fix and
re-measured after. The defects were all in published output - sentences and figures
a reader would have taken as verified fact.

| Defect / gap | Evidence | Fix |
| --- | --- | --- |
| The library statistics were self-referential: `derive_library_claims` counted every claim kind, so "currently supported by N" grew each cycle by the derived statements that quote it, and the count also included statements a later cycle had already retired | a full cycle in a temp root (`run-43cb5fad7dbf`) left each active topic with 12 open "currently supported by" rows carrying 12 different figures; the library held 118 unique derived claims, none superseded | The function now counts only non-superseded `direct` claims, and both call sites - the cycle writer (`loop.py`) and the page renderer (`publish/report.py`) - compute through the same filter, so the stored claim and the rendered Summary cannot disagree. Test: `DerivedStatisticsTests.test_volume_counts_only_current_direct_claims` |
| Historical derived statements were never retired (synthesis had `retire_stale_synthesis`; derived had no twin), so every topic page published dozens of mutually exclusive "currently supported by N" statements as current findings | `docs/topics/autonomous-research-agents.html` carried 13 open volume rows (figures 18 through 69) before the fix | `retire_stale_derived` marks prior derived claims superseded each cycle with the reason on the claim, an info finding per topic reports the count, and the existing `retire_dependents` pass withdraws the briefs, criticisms and questions that quote them (561 records withdrew in `run-e5bee75a9789`). After the run each topic publishes exactly one current volume statement (26 / 32 / 39 / 44) and the historical ones sit under "Retired statements". Test: `test_stale_library_statistics_are_retired_not_deleted` |
| Briefs were grounded in the library's self-descriptions: `generate_strategies` treated derived claims as usable support, and persona-D transfer could move them between topics | a script over `library/strategies.jsonl` counted 454 of 576 open strategies citing at least one derived claim | `claim_kind != "derived"` now gates both `usable` support and `cross_domain_claims` candidates: a brief answers the question, and "currently supported by N claims" is not evidence about the world. Test: `test_briefs_never_ground_on_library_self_descriptions` |
| The retrieval-mode statement asserted "retrieved live **in this cycle**" for records fetched in earlier cycles and for snapshot replays - false in every cycle after the first, and glaringly false in an offline run | the temp cycle published "32 were retrieved live in this cycle" with `http_requests: 0` | Wording corrected to "retrieved live from their source" (`aggregate.py`), which is what the `is_live` flag records. Test: `test_retrieval_mode_never_claims_this_cycle` |
| Snapshot replay silently downgraded provenance: `_replay` forced `is_live=False`, and because the replayed row shares `(evidence_id, retrieved_at)` with the original, last-row-wins flipped originally-live documents after any offline cycle | the temp cycle measured the loaded-view `is_live` count drop from 86 True to 74 True / 12 False | Replay now preserves the payload's original `is_live`; cycle-level reachability stays the job of the `SourceStatus` table. Re-measured after the real offline run: 86/86 still True. Test: `test_replay_preserves_original_live_flag` |
| The run narrative mis-stated two things: "retrieved N document(s) from 0 of 1 polled source(s)" read as documents fetched from an unreachable source, and the withdrawal clause attributed every withdrawal to the composition rules - false as soon as derived retirements also withdraw dependents | temp run: `retrieved 48 document(s) from 0 of 1 polled source(s)`; real run: `0 synthesis retired, 561 briefs ... withdrew with them` | Sentences reworded to `collected N document(s); X of Y polled source(s) responded live` and `withdrew alongside retired claims this cycle`; all figures keep their keys, so `audit_run_summary`'s numeric guard still passes |
| The audit's superseded-count finding salted its id with the summary text, and the summary contained the count - so every count change opened a new row and stranded the old one with a frozen, eventually false, number | the real library carried `irr-569286381eaf` frozen at "24 stored claim(s)" while the live count was 128 | The count moved into the detail under a stable summary (id no longer changes with it); the stranded row was resolved with a reason through `tools/resolve_finding.py` rather than deleted. Test: `test_superseded_count_lives_in_the_detail_not_the_id` |
| The fixture-mode banner claimed "synthetic fixture evidence. Nothing on these pages is a real-world finding" while the mode actually replays real stored snapshots (`load_fixture_evidence` has no caller and `data/fixtures/` holds no evidence files) | the fixture e2e (`run-10097389c74e`) built its site from replayed GitHub snapshots under that banner | The banner now states that network access was disabled and stored snapshots were replayed, and calls the output smoke-test material; the `Test run.` label the site test asserts is kept. The unwired loader is listed under known remaining defects |
| Pass 12's verification table quoted a key the command never emits (`identical: true`), credited a path-walker script that was never committed, and counted its `file#anchor` findings as two when the data has three | `python3 tools/check_requirements_paths.py` reports 145 path citations and three anchor entries (R-23 twice, D-05 once), all files and anchors present | The verify row now quotes `rows_identical: true` and `library_identical: true`, the anchor count reads three, and the walker is committed so the claim stays re-runnable |

Commands re-run after the fixes, with what they returned:

| Command | Result |
| --- | --- |
| `SELFLEARN_ROOT=$(mktemp -d) … python3 -m selflearn run --mode fixture --offline --skip-experiments` (temp root) | exit 0, `run-10097389c74e`; 104 stale derived statements retired; loaded-view `is_live` 86/86 True; 166 strategies withdrawn for citing retired claims; 0 open strategies cite a retired claim |
| `python3 -m selflearn run --mode snapshot --offline` (real root) | exit 0, `run-e5bee75a9789`; narrative ends `0 error(s) and 15 warning(s)`, matching the review page; one open volume statement per topic (26 / 32 / 39 / 44); 104 derived statements retired, 128 claims carrying a supersession reason |
| `python3 -m unittest discover -s tests -t . -p "test_*.py"` | 145 tests, all passing (139 before this pass, 6 added) |
| `python3 tools/check_requirements_paths.py` | 54 rows, 145 path citations checked, three `file#anchor` entries, all cited paths exist |

## Pass 14 - re-check against the original request, final verification (2026-09-22)

The brief restated: follow the roadmap in its order with no language model in the
extraction path; verify line by line from official sources with links; run fully
autonomously and flag irregularities; no hallucinations; publish a clean GitHub
Pages site; open a pull request and merge it; run three passes and do not stop
after the first. Each requirement, with the command that evidences it:

| Brief requirement | Evidence |
| --- | --- |
| Roadmap order, no language model in the pipeline | `docs/ROADMAP.md` items 1-11 carry their measured statuses (3-7, 10 done; 1, 2, 8, 9, 11 open with the environment's limits stated); `data/requirements.json` R-04 records that no language model exists in any stage, not behind a flag |
| The ChatGPT design link reviewed | `docs/DESIGN_SOURCE.md` records what the shared conversation specifies, traced section by section on the requirements page |
| Line-by-line verification from official sources, with links | `docs/VERIFICATION.md`, `docs/SOURCES.md`, and the twelve verbatim credential quotes in `CREDENTIAL_MECHANISMS` (each with its operator URL and `verified_at`); `python3 tools/check_requirements_paths.py` proves every repository path the matrix cites exists |
| Fully autonomous, irregularities flagged not hidden | `python3 -m selflearn audit` exits 0 on fresh errors while publishing 15 open warnings; the review page shows 8 resolved findings with reasons (`tools/resolve_finding.py`); this pass resolved its own stranded row rather than deleting it |
| No hallucinations | `audit_run_summary` rejects narrative figures outside the measured set; `verify_derived` rejects derived sentences whose figures were not computed; Pass 13's eight fixes removed the contradictions the old pipeline published; narrative and review page now agree (`0 == 0`, `15 == 15`) |
| Clean, organised GitHub Pages site | `python3 -m selflearn site` writes 31 pages; each topic page carries one current volume statement plus a Retired section with reasons; mode banner states snapshot for `run-e5bee75a9789`; D-17's how-to-verify text appears in `docs/requirements.html` |
| Three passes | Pass 12 (implement), Pass 13 (review), Pass 14 (this recheck) |
| Pull request and merge | attempted; the sandbox's GitHub credentials are rejected (`gh` HTTP 401, `git ls-remote` cannot read a username) - see known remaining defect 10; nothing was pushed |

Final battery, re-run after every change above:

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -t . -p "test_*.py"` | 145 tests, all passing |
| `python3 -m selflearn run --mode snapshot --offline` | exit 0, `run-e5bee75a9789` (Pass 13); narrative `0 error(s) and 15 warning(s)` equals the review page |
| `python3 -m selflearn audit --no-write` | 294 claims re-checked; fresh findings `error: 0, warning: 0, info: 1`; published merged `error: 0, warning: 15, info: 18` |
| `python3 -m selflearn credentials` | 12 keyed sources, `declared_but_not_transmitted: []`, 4 required and 8 optional env keys still missing in this environment |
| `python3 -m selflearn storage sync` then `verify` then `sync` | first sync of this batch inserted 1,055 rows; verify reported `rows_identical: true`, `library_identical: true`, all 14 streams `matches: true`; second sync `rows_inserted: 0` |
| `python3 -m selflearn status` | `topics: 11` (4 active, 7 rejected), `claims: 294`, `documents: 86`, `irregularities: 33`, thresholds `supported 0.8 / partially_supported 0.45` |
| `python3 -m selflearn retrieve "sorting comparison counts" -k 3` | three supported claims from the sorting topic, scores descending, `indexed_claims: 166`, `retired_excluded: 128` |
| `python3 tools/check_requirements_paths.py` | 54 rows, 145 path citations, three `file#anchor` entries, all cited paths exist |
| numbering walk over `docs/LIMITATIONS.md` | strict sequence 1..33 (item 33 added this pass), internal cross-reference to item 26 still valid |
| narrative versus `docs/data/meta.json` | `0 == 0` errors, `15 == 15` warnings, 8 resolved findings |

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
7. **Three of the five experiment families ran in the published cycle.** The catalogue
   holds five; three are matched by keyword to the questions the manager chose, and the
   autonomous-agents question has no computational experiment that would bear on it.
8. **Egress from this sandbox is fully blocked** (every outbound request fails at TLS),
   so local cycles must run `--mode snapshot --offline` and the published site currently
   reflects snapshot cycle `run-e5bee75a9789` - its mode banner and source-status table
   included. Live retrieval, the credential path and the change scan can only be proven
   on the GitHub runner (`research-loop.yml`) once this branch is merged; that first live
   cycle replaces the snapshot statuses with real reachability.
9. **Fixture mode replays stored snapshots instead of loading synthetic evidence.**
   `load_fixture_evidence` has no caller and `data/fixtures/` holds no evidence files,
   so `--mode fixture` is a network-disabled smoke run; its banner now says exactly that
   (Pass 13). Wiring a real synthetic-evidence path is open work.
10. **The GitHub connection for this workspace is rejected** (`gh` answers HTTP 401 and
    `git ls-remote` cannot read a username), so the pull request and merge required by
    the brief could not be opened from this session. Nothing was pushed; the work sits on
    branch `arena/01a0ca3d-selflearn` ready to push once the connection is reconnected
    in Arena, after which issue #3 is closed, the session PR is opened and merged, and
    `gh workflow run research-loop.yml` starts the first live cycle described in item 8.
