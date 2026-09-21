# SelfLearn

An autonomous research engine that will not publish a sentence it cannot quote from a
document it actually retrieved.

SelfLearn works one question at a time: it plans what to read, fetches documents from
registered public sources, cuts candidate claims out of those documents, verifies each
claim against the document it came from, lets six competing "researchers" build
candidate answers out of the verified claims, attacks those candidates with eleven
deterministic critic rules, scores them on nine published criteria, runs seeded
experiments where a question allows one, derives the next questions, and publishes
everything - claims, sources, criticisms, contradictions, refusals and open
irregularities - as a static site and as machine-readable JSON.

**Live site:** <https://buffedlizard55-lab.github.io/SelfLearn/> (a one-page entry point at the
repository root links into the generated site in `docs/`) ·
**Design specification this was built to:** <https://chatgpt.com/share/6ab1612a-2f14-83e8-9de6-808d21a48e53>

There is no language model anywhere in the pipeline. No model retrieves, extracts,
summarises or reasons. Claims are spans copied out of retrieved documents, and they are
accepted or rejected by string and set operations that anyone can re-run.

## The one-minute version

```
python3 -m selflearn run --mode live     # one complete research cycle, then publish
python3 -m selflearn audit               # re-verify every stored claim from its snapshot
python3 -m selflearn selftest            # the test suite
python3 tools/serve_site.py              # read the published site locally
```

Requirements: Python 3.10 or newer. Nothing else - the project has **no third-party
dependencies**, not even for HTTP or HTML.

## What one cycle does

| Stage | What happens | Where |
| --- | --- | --- |
| Plan | The manager picks the questions to work on and the sources to read for each | `selflearn/think/manager.py` |
| Retrieve | Each source is polled through a politeness- and budget-limited client; failures are classified as unreachable, HTTP error, parse error or missing credential | `selflearn/fetch/` |
| Store | The response is hashed and written to `evidence/snapshots/` **before** anything reads it | `selflearn/fetch/collector.py` |
| Extract | Documents are turned into candidate claims by cutting sentences; scaffolding lines are dropped | `selflearn/verify/grounding.py` |
| Verify | Each candidate is checked against the stored document: numbers, dates, polarity, direction, universality, then quote match and token coverage | `selflearn/verify/verifier.py` |
| Contradict | Claims that disagree are detected and published as review items | `selflearn/verify/contradiction.py` |
| Compete | Six personas build candidate answers made only of quotations plus fixed scaffolding | `selflearn/think/competition.py` |
| Criticise | Eleven named rules attack each candidate; each attack records the rule that fired | `selflearn/think/critic.py` |
| Rank | Nine weighted criteria, with measured and heuristic criteria labelled differently; Elo ratings accumulate across cycles | `selflearn/think/tournament.py`, `elo.py` |
| Experiment | Seeded, dependency-free scripts run in a subprocess with a tamper check on the script hash | `selflearn/experiment/` |
| Derive | New questions are derived from what was retrieved, each with the claims it came from | `selflearn/think/discovery.py` |
| Audit | Every claim is re-verified from its snapshot; links, fixtures, coverage and published prose are checked for numbers that are not in the evidence | `selflearn/verify/audit.py` |
| Publish | A static site, plus JSON for every page | `selflearn/publish/` |

## The evidence discipline

- A claim's text **is** a span of the stored document. It is cut, not rewritten.
- Every claim carries its source, its evidence class, its rank, the quoted span, a
  coverage score and the verifier's reasons.
- A number in a claim that is not in the document is a hard failure, no matter how
  good the wording is. So is a missing date, and so is a polarity flip.
- Generated prose is checked by the same numeric guard: the run summary cannot
  introduce a figure that is not a measured count.
- Statements about the engine's own library are marked `derived` and are re-checked
  against the figures recorded on the claim.
- Anything the engine could not do is published: unreachable sources, missing
  credentials, contradictions, fixture evidence, and the irregularities the audit
  raises against the engine's own output.

## Verify it yourself

| Step | Command or link |
| --- | --- |
| Read the claims and their sources | the [published site](https://buffedlizard55-lab.github.io/SelfLearn/), or `docs/index.html` locally |
| Check one claim end to end | `python3 tools/check_claim.py` |
| Re-verify the whole library | `python3 -m selflearn audit` |
| Repeat an experiment | `python3 tools/reproduce_experiment.py sorting-comparisons-v1` |
| Read the calibration and thresholds in force | `python3 -m selflearn calibrate` |
| Test every registered source for reachability | `python3 -m selflearn sources --probe` |
| Read the engine's own list of what it got wrong | `docs/review.html`, `reports/irregularities.md` |

Every figure on the site is traceable to a claim or to a count the engine recorded, and
the full data behind every page is exported to `docs/data/`.

## Documents

| Document | What it covers |
| --- | --- |
| [docs/DESIGN_SOURCE.md](docs/DESIGN_SOURCE.md) | The specification, section by section, and where each part was implemented |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Modules, data flow, storage layout, guarantees kept and deliberately not kept |
| [docs/SOURCES.md](docs/SOURCES.md) | All 36 registered sources, their operators, classes, licences and access rules |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | The verification rules in order of precedence, and what they cannot see |
| [docs/LIMITATIONS.md](docs/LIMITATIONS.md) | Everything this engine does not do |
| [docs/ROADMAP.md](docs/ROADMAP.md) | What is next, and how we would know it worked |
| [docs/PASSES.md](docs/PASSES.md) | What each build pass changed, including the defects it found |

The same documents are rendered into the site at `docs/documents.html`.

## Continuous operation

The engine is a process, not a daemon: a cycle runs to completion. Continuity comes
from the schedule in `.github/workflows/research-loop.yml`, which runs a cycle every
six hours on GitHub's runners, commits the updated library and pages, and uploads the
run artefacts. `.github/workflows/tests.yml` runs the suite on every push and does a
full cycle into a temporary root, so the pipeline is exercised without touching the
repository's own library.

Sources that need a credential (`eia`, `fred`, `ncei`, `patentsview`) are never called
without one; each records a `credential_required` status naming the secret to set.

## Repository layout

```
selflearn/        the engine (fetch, verify, think, learn, experiment, publish)
data/             seed questions, the labelled calibration cases, the requirements matrix
experiments/      seeded experiment scripts, each with a hypothesis and a falsifier
tests/            67 tests, no network and no credentials required
tools/            reviewer tools: check a claim, reproduce an experiment, export a summary, serve the site
docs/             the published site, plus the hand-written documents listed above
library/          the append-only memory: 14 JSONL streams
evidence/snapshots/   every retrieved document, hashed, exactly as it was verified
reports/          run summary, irregularity list, the exported readable summary
state/            calibration, Elo ratings, the last cycle
```

## Limitations, in one paragraph

The verification layer is lexical, not semantic: it catches fabricated numbers, wrong
dates and reversed polarity, but it cannot catch a unit substitution, and it cannot
tell whether a quoted sentence is being used in the author's sense. The experiment
catalogue is computational - no physical experiments. Only sources that answer without
a credential and are reachable from the runner contribute, so a run's evidence is as
good as its egress. New topics come from a seed file plus derived questions; the
engine does not yet crawl the open web to invent topics. The full list, including what
the published run could not reach, is in [docs/LIMITATIONS.md](docs/LIMITATIONS.md) and
on the site's method page.

## Licence

Code: MIT (see `LICENSE`). Retrieved documents keep their own licences, recorded per
source in the register and shown next to each claim.
