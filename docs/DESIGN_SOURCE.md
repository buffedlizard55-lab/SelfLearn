# Design source

This project was built to a supplied specification, not to a specification invented
along the way. This document records what that specification asked for, where each
part of it landed in the code, and where the implementation deliberately differs.

## The specification

The brief was a shared design document, *Design Autonomous Research System*:

- Share link (public): <https://chatgpt.com/share/6ab1612a-2f14-83e8-9de6-808d21a48e53>
- Retrieved for implementation through the share API endpoint that backs that page
  (`https://chatgpt.com/backend-api/share/6ab1612a-2f14-83e8-9de6-808d21a48e53`).
- The design document names OpenAI, the Crossref REST API, NOAA NCEI CDO web
  services, the Semantic Scholar API, SEC EDGAR APIs and the GitHub REST API as
  reference material for the world-scanning layer.

The document describes a twenty-part system. The table below maps each part to what
was built. *Status* uses the same vocabulary as the requirements matrix on the
published site: **implemented** means the behaviour is in the code and exercised by
a test or by the run that publishes the site; **partial** means something real
exists but is narrower than the document describes, and the narrowing is stated.

| Section | What the document asks for | Where it lives | Status |
| --- | --- | --- | --- |
| 1 World scanner | Watch papers, code, government data, filings, patents, news and APIs for what changed | `selflearn/fetch/registry.py`, `selflearn/fetch/sources.py`, `selflearn/fetch/collector.py`, `selflearn/fetch/changes.py` | implemented for the five sources whose operators document a change filter (Crossref, arXiv, GitHub, NVD, USGS); the rest are polled question by question and are reported as having no change filter |
| 2 Topic record | Facts, open questions, competing theories, evidence, experiments, confidence, next questions | `selflearn/models.py::Topic`, `library/*.jsonl`, topic pages under `docs/topics/` | implemented |
| 3 Six researchers | Conventional, contrarian, first-principles, cross-domain, optimisation, experimental | `selflearn/think/personas.py`, `selflearn/think/competition.py` | implemented |
| 4 Critics | Attack assumptions, contradictions, failure modes, simpler explanations, citation accuracy, reproducibility | `selflearn/think/critic.py` (eleven named rules) | implemented |
| 5 Evidence hierarchy | Nine ranked classes, each claim carrying provenance | `selflearn/config.py::EVIDENCE_HIERARCHY`, every `Claim` records class and rank | implemented |
| 6 Memory layers | Raw, knowledge, reasoning, experiments and meta-knowledge | `library/*.jsonl` (raw and reasoning), `library/experiments.jsonl`, `selflearn/learn/memory.py` (meta-knowledge) | implemented, as files rather than a database |
| 7 Lifecycle | New, researching, hypothesis, competing, testing, validated, deployed, monitored, rejected | `selflearn/config.py::LIFECYCLE_STATES`, `selflearn/think/manager.py::topic_transition` | implemented; `validated` and beyond require an experiment to have passed |
| 8 Automatic experimentation | Thousands of iterations, seeded and repeatable | `selflearn/experiment/` (catalogue, runner, four scripts) | partial: four experiment families, not thousands of variants |
| 9 Benchmark everything | The winner is criticised, reproduced and independently tested before promotion | `selflearn/think/tournament.py`, `selflearn/experiment/runner.py` | partial: the in-house reproduction step exists, an independent third party does not |
| 10 Tournaments | Score on correctness, reproducibility, evidence quality, experimental performance, robustness, simplicity, cost and scalability, never persuasiveness | `selflearn/config.py::TOURNAMENT_CRITERIA`, `selflearn/think/tournament.py` | implemented; weights and measured-versus-heuristic method are published per criterion |
| 11 Curiosity chains | Every answer produces further questions | `selflearn/think/discovery.py` | implemented |
| 12 Trending discovery | Novelty times importance times research potential | `selflearn/think/discovery.py::score_topic`, `selflearn/think/invention.py` | partial: scoring and promotion gates are implemented and candidates are published with their components, but the candidate pool is the engine's own retrieval, not an open scan of the web |
| 13 Central manager | One component decides what to work on next | `selflearn/think/manager.py`, `selflearn/loop.py::run_cycle` | implemented |
| 14 Result card | A fixed, stable layout for every result | `selflearn/publish/site.py::page_topic` | implemented |
| 15 Reference stack | Python, PostgreSQL, vector database, knowledge graph, object storage, Redis and sandboxes, model router | none of it; see *Deviations* below | not implemented, by design |
| 16 Cadence | Event-driven rather than literally nonstop | `selflearn/loop.py::run_forever`, `.github/workflows/research-loop.yml` | implemented |
| 17 Entities | Entities from topics down to benchmarks | `selflearn/models.py` dataclasses, `library/*.jsonl` | implemented |
| 18 Say UNKNOWN | When the evidence does not settle a question, say so and give the next experiment | `selflearn/publish/report.py` unknowns block, `selflearn/think/discovery.py` | implemented |
| 19 Epistemic state | Know, think we know, assume, do not know, what would change the conclusion, what experiment resolves it | claim verdicts, strategy assumptions and falsifiers, `docs/LIMITATIONS.md` | implemented |
| 20 Loop | Scanner through to CONTINUE | `selflearn/loop.py`, `.github/workflows/research-loop.yml` | implemented |

The document's minimum viable product is "Topic Scanner, Researcher, Solver, Critic,
Experimenter, Memory". Those six map to `fetch/`, `think/manager.py`,
`think/competition.py`, `think/critic.py`, `experiment/` and `learn/`.

## Deviations, and why

**Files instead of PostgreSQL, a vector store, a graph database and Redis.** The
design document lists a reference stack. This implementation uses append-only JSONL
streams, JSON snapshots and JSON state files, for three reasons: a reviewer can read
every record with `cat`; the repository has zero third-party dependencies, so the
whole engine runs anywhere Python runs; and a diff of the memory is a diff of the
site. The data model is already normalised — every stream is a list of dataclass
records with a stable id — so moving to a database is a writer change, not a rewrite.
`docs/ARCHITECTURE.md` describes the streams and their keys.

**Retrieval is question-driven, and change-driven where the operator allows it.** The
document's scanner watches for "what changed". Five registered sources publish a change
filter, and `selflearn/fetch/changes.py` polls only those, using only the documented
parameter and recording the window it used; the others are polled per question and are
reported as having no change filter rather than being described as unchanged. Both paths
publish, for each source, whether it answered and how fresh the answers were.

**No language model in the reasoning path.** The document allows a model router. This
implementation removes the model from the loop entirely: claims are spans copied out
of retrieved documents, and they are accepted or rejected by string and set
comparisons. That is a deliberate trade — the engine cannot paraphrase, but it also
cannot invent. Every sentence the engine publishes about the world is either a
quotation from a retrieved document, a count of its own records, or a rule-based
statement about its own analysis.

**Experiments are computational.** The engine runs seeded software experiments
(threshold calibration, sorting and search comparison counts, hash collision rates).
It cannot run physical experiments or surveys, and it does not claim to.

**Topic proposals are seeded, derived and proposed.** New questions are derived from
retrieved evidence by `think/discovery.py`, and `think/invention.py` promotes recurring
phrases from retrieved documents into new topics when they clear the published novelty,
importance and potential gates. The candidate pool is still the engine's own retrieval,
not an open scan of the web, so section 12 remains marked partial - "novel" here means
novel to this library.

## How the interpretation was checked

1. Each section of the design document was turned into one or more rows in
   `data/requirements.json` (`R-*` for the brief's own requirements, `D-*` for
   design-document sections).
2. Every row carries a status, the file that implements it, how a reviewer can check
   it, and the gap where the implementation is narrower than the design.
3. The same rows are rendered on the site's requirements page and exported to
   `docs/data/requirements.json`, so the mapping can be checked without reading
   Python.
4. `docs/PASSES.md` records what each build pass changed, including the defects the
   passes found in this implementation.
