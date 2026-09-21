# Architecture

The engine is a single Python package with no third-party dependencies. It runs one
research cycle, writes what it learned to append-only files, and publishes a static
site. This document describes the parts, the data that flows between them, and the
guarantees each part is expected to keep.

## One cycle, end to end

```
data/seeds/topics.json
        |
        v
 think/manager.py ........ pick the questions to work, and the sources to read
        |
        v
 fetch/collector.py ...... poll each source for the question
   fetch/net.py .......... stdlib HTTP: politeness delay, retries, budget, TLS
   fetch/registry.py ..... 36 source specs: operator, class, licence, key, docs
   fetch/sources.py ...... per-source adapters; every record is rendered with attribution
        |
        v
 evidence/snapshots/*.json  the retrieved bytes, hashed, stored before anything uses them
        |
        v
 verify/grounding.py ...... cut candidate claims out of the document (spans only)
 verify/verifier.py ....... accept, downgrade or reject each claim
 verify/contradiction.py .. find claims that pull against each other
        |
        v
 think/competition.py ..... six personas build candidate answers from verified claims
 think/critic.py .......... eleven rules attack each candidate
 think/tournament.py ...... score candidates on nine published criteria; Elo updates
 experiment/ .............. run the experiments a candidate asks for
 think/discovery.py ....... derive the next questions; score what to do next
 think/manager.py ......... move each topic along its lifecycle
        |
        v
 verify/audit.py .......... re-verify every claim, check links, links, fixtures, coverage
        |
        v
 library/*.jsonl .......... the memory: evidence index, claims, strategies, attacks, ...
 reports/ ................. run summary, irregularities, machine-readable state
 docs/ .................... the published site (GitHub Pages serves this folder)
```

Nothing is written to the library before it is written to `evidence/snapshots/`: a
claim always points at a stored document whose SHA-256 is recorded, so a later audit
can re-check the claim against the same bytes.

## Modules

| Module | Responsibility | Test coverage |
| --- | --- | --- |
| `selflearn/util.py` | Time, hashing, stable ids, slugs, tokenisation, number and date extraction, JSON and JSONL IO | via every other test |
| `selflearn/config.py` | Every path, budget, threshold, weight and enumerated constant, in one file | assertions in the test suite |
| `selflearn/models.py` | The record types that make up the memory | round-trip tests |
| `selflearn/fetch/net.py` | HTTP with politeness, retries, budgets and a hard distinction between *unreachable* and *bad response* | exercised offline; network failures are a first-class outcome |
| `selflearn/fetch/registry.py` | The register of 36 sources | registration tests: every source has an operator, a documentation URL, a class and an adapter |
| `selflearn/fetch/sources.py` | Adapters that turn a JSON or XML response into attributed text | parser tests for JSON paths, inverted abstracts, JSON-stat cells |
| `selflearn/fetch/collector.py` | Poll a source for a question, drop irrelevant results, store snapshots, classify failures | budget, fixture replay and relevance tests |
| `selflearn/verify/grounding.py` | Turn a document into candidate claims | scaffolding and attribution tests |
| `selflearn/verify/verifier.py` | Decide whether a document supports a claim | the labelled case set |
| `selflearn/verify/contradiction.py` | Detect claims that conflict on the same subject | polarity tests |
| `selflearn/verify/audit.py` | Re-check the whole library and report irregularities | audit tests |
| `selflearn/think/personas.py` | The six briefs and what each is allowed to cite | selection determinism tests |
| `selflearn/think/competition.py` | Build candidate answers: quotations plus fixed scaffolding, nothing else | "no invented numbers" test |
| `selflearn/think/critic.py` | Eleven attack rules over the library | rule-firing tests |
| `selflearn/think/tournament.py` | Nine-criterion scoring, perturbation robustness, winner selection | ranking and scorecard tests |
| `selflearn/think/elo.py` | Persistent ratings, so standing accumulates across cycles | reproducibility test |
| `selflearn/think/discovery.py` | Derive next questions; score topics for novelty, importance and potential | provenance tests |
| `selflearn/think/manager.py` | Prioritise, choose sources, move lifecycle states | plan and transition tests |
| `selflearn/experiment/` | Catalogue of seeded experiments, sandboxed runner, tamper check | script-existence and run tests |
| `selflearn/learn/store.py` | Append-only library: load, dedupe, snapshot index | round-trip and dedupe tests |
| `selflearn/learn/aggregate.py` | Compose derived statements from the library's own counts | derived-claim tests |
| `selflearn/learn/calibration.py` | Sweep verification thresholds against labelled cases | calibration tests |
| `selflearn/learn/memory.py` | Meta-knowledge: per-source reliability from recorded outcomes | reliability tests |
| `selflearn/publish/report.py` | Assemble per-topic reports and the site dataset | rendering tests |
| `selflearn/publish/site.py` | Static HTML, no third-party scripts | site-build tests |
| `selflearn/publish/markdown.py` | Render the repository documents for the site, escaping everything | renderer and link-safety tests |
| `selflearn/loop.py` | The cycle itself | end-to-end fixture tests |
| `selflearn/cli.py` | `run`, `audit`, `site`, `sources`, `experiments`, `calibrate`, `status`, `selftest` | command tests |

## Storage

| Path | Contents | Written by |
| --- | --- | --- |
| `data/seeds/topics.json` | The questions the engine starts from | hand-edited |
| `data/fixtures/verification_cases.jsonl` | 24 labelled cases for calibration, including cases the verifier is expected to fail | hand-edited |
| `data/requirements.json` | The requirements matrix | hand-edited |
| `evidence/snapshots/<evidence_id>.json` | The retrieved document, its hash, its HTTP status, its licence | `fetch/collector.py` |
| `library/*.jsonl` | 14 append-only streams: evidence index, claims, topics, questions, strategies, attacks, experiments, discoveries, failures, irregularities, audit log, contradictions, tournaments, tasks | `learn/store.py` |
| `state/*.json` | Calibration, Elo ratings, loop state, last cycle summary | `loop.py` |
| `reports/` | Run summary and the human-readable irregularity list | `loop.py`, `verify/audit.py` |
| `docs/` | The published site, plus the hand-written documents in this folder | `publish/site.py` |

Every stream is a list of records with a stable id derived from a SHA-256 of the
record's identity fields. Re-running the engine on unchanged inputs therefore appends
nothing new, which is what makes the published site a reviewable diff rather than a
moving target.

## Guarantees the code is built to keep

1. **Nothing enters the library without a stored document.** A claim records the
   evidence id whose snapshot contains the text it was cut from.
2. **No number appears in generated text that is not in a source or in the engine's
   own computed figures.** Both are checked by `verify/audit.py::audit_narrative`,
   which is run against published prose as well as claims.
3. **A failed source is recorded, not hidden.** Unreachable, HTTP error, parse error
   and missing credential are separate outcomes, each with a remedy, and each appears
   on the sources page.
4. **The engine never calls an API that needs a key it does not have.** Missing keys
   produce a `credential_required` status naming the environment variable to set.
5. **Every published document keeps its licence information** from the register.
6. **Deterministic given the same inputs**: sorts are explicit, ids are hashes, and
   the only wall-clock values are timestamps.

## Deliberate limits of the architecture

- The library is append-only and never compacted. It grows without bound; nothing
  currently prunes superseded records.
- Retrieval is single-threaded and politeness-delayed, so a cycle polls a handful of
  sources, not hundreds.
- The reasoning layer is rule-based, so it cannot synthesise prose across documents.
  Cross-document statements are limited to counts of the library's own contents.
- There is no queue, no worker, and no daemon: a cycle is a process that runs to
  completion. Continuity comes from the schedule that starts it (see
  `.github/workflows/research-loop.yml`), which the design document explicitly allows
  in place of a process that never exits.

## Migration path to the reference stack

The record types are dataclasses with `to_dict()`; the streams are lists of them.
Moving to PostgreSQL means writing each stream's rows to a table with the id as the
primary key, and reading them back through the same loader. A vector search over
claims becomes possible once an embedding model is available, but it is not required
for any guarantee above: nothing in the verification path depends on approximate
similarity, only on exact containment and token coverage.
