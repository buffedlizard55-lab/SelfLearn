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

## Known remaining defects and gaps

These are open, published, and are the honest answer to "what is still wrong":

1. **The claim corpus is metadata-heavy.** In this environment only GitHub was
   reachable, so most accepted claims describe repositories rather than the subject
   matter of the question. This is a consequence of egress, not of the verifier.
2. **Unit substitution is undetectable.** Labelled case `c23` documents it and is
   excluded from calibration with a recorded reason.
3. **PatentsView's endpoint has moved** and the adapter has not been updated.
4. **No keyed source has ever been polled**, because no key is present in this
   environment.
5. **New topics are seeded.** Question derivation is automatic; topic invention from an
   open scan of the web is not implemented (design section 12, marked partial).
6. **The store never compacts.** Append-only streams grow without pruning.
7. **Two of the four experiment families ran in the published cycle.** The catalogue
   holds four; two are matched to the questions the manager chose.
