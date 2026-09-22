# Roadmap

Ordered by what most increases the value of the output per unit of work. Each item
says why it matters, what it needs, and how we would know it worked. Items marked
**done** shipped in this repository with the test that proves them; the rest are open.
The current order of the open items is 1, 2, 8, 9, 10, 11.

## 1. Reach more sources (highest value) - open, blocked on the environment

**Why.** In the build sandbox only GitHub was reachable, so most accepted claims are
repository metadata rather than domain knowledge. Every additional source converts
directly into claims a reader can check.

**What it needs.** Nothing new in code: run the loop on a host with unrestricted
egress (the bundled workflow does this on GitHub's runners), then re-run
`python3 -m selflearn sources --probe` and confirm the previously unreachable sources
answer.

**How we would know.** The sources page shows more than one reachable source, and the
per-topic source tables show evidence classes above `primary_source` (peer-reviewed
papers, official statistics).

## 2. Finish the credential path - open, blocked on secrets (the code path is now complete)

**Why.** `eia`, `fred`, `ncei` and `patentsview` are registered but never called,
because no key is present. Those are exactly the sources that answer quantitative
questions about energy, economics and climate.

**What it needs.** Repository secrets named as the register says
(`EIA_API_KEY`, `FRED_API_KEY`, `NCEI_TOKEN`, `USPTO_ODP_API_KEY`), free in each
case. The workflow already passes them through when present.

**What shipped.** `python3 -m selflearn credentials` now prints, for every keyed
source, whether its variable is set, whether the credential is required or optional,
whether the adapter actually transmits it, the operator's own key-request page, and the
rate-limit note; the scheduled workflow runs it on every cycle, and the CI workflow
runs the link check and commits the result so a moved page is visible rather than
discovered by a failed run.

Line-by-line review of the credential path on 2026-09-22 discovered that `GenericSource`
never placed credentials on requests: `eia`, `fred` and `ncei` were accepted as enabled
when secrets were set, but all HTTP requests went out unauthenticated. This is now fixed
with `CREDENTIAL_MECHANISMS` in `selflearn/fetch/sources.py`, quoting the operator's own
documentation and verifying how each credential is sent (`api_key` parameter for `eia`
and `fred`, `token` header for `ncei`, `Authorization: Bearer` for `github`).
`research-loop.yml` passes `USPTO_ODP_API_KEY` (replacing the retired
`PATENTSVIEW_API_KEY`), the optional keys, and `GITHUB_TOKEN`.
Sources whose transmission mechanism has not yet been transcribed are honestly published
as `declared_but_not_transmitted` rather than silently assumed to work. A dedicated
**Official links** page (`docs/links.html`) and root landing entry point publish the
exact status of all 120 URLs checked from an unrestricted runner.

**How we would know.** The sources page shows them as reachable with `credential_required`
cleared, and claims appear with those sources named.

## 3. Repair the PatentsView adapter - done 2026-09-21

**Why.** PatentsView was folded into the USPTO Open Data Portal; the adapter still
calls the older host. This is flagged in `docs/SOURCES.md`.

**What it needs.** The portal's endpoint shape and a key, then an adapter update and a
fixture-based test.

**How we would know.** A patent query returns records, and the flagged item is closed
with a note rather than deleted.

**What shipped.** The register now points at the Open Data Portal
(`https://api.uspto.gov/api/v1`, key `USPTO_ODP_API_KEY`), and `UsptoOdpSource` queries
both documented endpoints: `/patent/applications/search` (`q`, `limit`) and
`/datasets/products/search` (`productTitle`). The bulk-products response is parsed from
the field names the operator publishes; an unmodelled shape is stored verbatim instead of
being guessed at. Five tests in `tests/test_layers.py::UsptoOdpAdapterTests` cover the
endpoints, the key header, the parse and the verbatim fallback. The flag in
`docs/SOURCES.md` is closed with the operator's own statements and links, not deleted.
Still unverified against a live key: none is configured, so the adapter has been proven
against the operator's documented request and response shapes and not against a real
response.

## 4. Substance filter for claims - done 2026-09-21

**Why.** A verified claim can still be trivial. "The record for X reports licence
MIT" is checkable but not knowledge. The engine should prefer claims that carry a
quantity, a date, a comparison or a mechanism, and say so when it only has metadata.

**What it needs.** A published scoring rule over claim features (numbers, dates,
comparatives, negations, sentence length, evidence class), applied when selecting what
to show first, plus honest labelling of the rest as metadata.

**How we would know.** The share of claims carrying a quantity or date rises, and the
topic pages lead with them.

**What shipped.** `selflearn/learn/substance.py` publishes an eight-feature rule
(quantity, date, comparison, mechanism, caveat, specificity, verification, evidence)
whose weights sum to 1 and are rendered on the method page. Every claim carries its
score, its components and one of three labels (`substantive`, `descriptive`,
`metadata`); topic pages are ordered by it and show the label in the facts table; the
index page reports the library-wide split and the metadata share, with the reason it is
high. Six tests in `tests/test_layers.py::SubstanceRuleTests` pin the rule, including
the one that matters most: an unsupported claim can never outrank an equivalent
supported one.

## 5. Cross-document synthesis, with the same discipline - done 2026-09-21

**Why.** The most valuable output of a research loop is a statement that holds across
several sources. Today every claim is single-source.

**What it needs.** Aggregation across documents that keeps the discipline: a
multi-source statement must be composed only of figures present in the sources it
cites, and it must record the set of evidence ids behind it. The derived-claim
machinery (`claim_kind=derived`, `context_numbers`, re-checked by the audit) is the
existing foundation.

**How we would know.** A new claim kind appears whose audit re-check recomputes the
same numbers from the cited claims, and disagreement counts stay at zero.

**What shipped.** `claim_kind="synthesis"`, produced by `selflearn/learn/synthesis.py`
in three forms - agreement on a figure, the range of values sharing a unit, and a
published disagreement. A statement needs two distinct documents, may contain only
figures that appear in the claims it cites plus the document and source counts recorded
beside it, and is rejected outright (not published with a warning) if
`verify_synthesis` does not support it. The audit recomputes every synthesis claim from
its citations and raises an error if a cited claim has gone or the recomputation
disagrees. Seven tests in `tests/test_layers.py::SynthesisTests`, including the one that
proves an invented average is refused.

## 6. Change-driven scanning (design section 1) - done 2026-09-21

**Why.** The engine currently answers questions. The design document also asks it to
notice change: new papers, new datasets, new releases.

**What it needs.** Per-source "what changed since the last run" support. Several
registered APIs already offer it: Crossref `from-index-date`, arXiv's sorted feeds,
NASA and USGS date filters, GitHub `pushed:>` and release feeds.

**How we would know.** A run reports items seen for the first time, with the window
used, and the discovery layer turns them into questions.

**What shipped.** `selflearn/fetch/changes.py` implements the five mechanisms whose
operators document a change filter (Crossref `from-index-date`, arXiv
`sortBy=submittedDate`, GitHub `pushed:>=`, NVD `lastModStartDate`/`lastModEndDate`,
USGS `starttime`/`endtime`), each with the operator's documentation URL published next
to it. `python3 -m selflearn scan` reports the window, the request, the items returned
and the items not seen before; `--discover` turns new items into questions. A cycle runs
the scan when it has network access, and a source with no documented filter is reported
as having none rather than polled. Nine tests in `tests/test_layers.py::ChangeScanTests`
pin every parameter name to the documented one. Not yet observed against live sources
from this repository, for the reason in item 1.

## 7. Topic proposal from an open scan (design section 12) - done 2026-09-21, narrowed

**Why.** Seed topics are still human-authored.

**What it needs.** A novelty measure computed from what the engine already holds
(vocabulary overlap against the existing library), the importance and potential
components that already exist in `think/discovery.py`, and a rule for promoting a
candidate to a topic.

**How we would know.** A new topic appears whose provenance is a set of claims and
whose score components are published.

**What shipped.** `selflearn/think/invention.py` scores candidates as
novelty x importance x potential, with three gates (at least two documents, novelty at
or above 0.5, total at or above 0.45) and at most three promotions per cycle. Every
candidate - including the rejected ones, with the reason - is published on the index
page. Provenance is the set of claim ids behind the phrase.

**The narrowing, stated plainly.** The candidate pool is the documents this engine has
already retrieved, not an open crawl of the web, so "novel" means novel to this
library. The alternative is inventing subjects from the engine's own vocabulary, which
is the failure mode this project exists to avoid. The first run proved the risk was
real: before the fix, the engine proposed seven topics out of its own rendering
scaffolding ("Sentence below names"), because the adapters write the same provenance
lines into every document. Candidates are now drawn only from a source's own prose, with
the engine's field labels and boilerplate stripped, and its own records excluded
entirely. A regression test pins that behaviour.

## 8. Storage migration

**Why.** JSONL is auditable and does not scale. The design document's reference stack
exists for a reason.

**What it needs.** A writer per stream into PostgreSQL, with the existing ids as
primary keys, and a read path that keeps the current guarantees (append-only, hashed,
replayable). A vector index over claims would then make cross-domain retrieval real
rather than keyword-based.

**How we would know.** The same site builds from the database, and the audit reports
identical verdicts.

## 9. More experiment families

**Why.** Three computational experiments cannot settle much. The catalogue is the part
of the design document marked most partial (section 8: "thousands of iterations").

**What it needs.** Seeded, dependency-free scripts in `experiments/` with a declared
hypothesis, a falsifier and a metric, plus keywords so the manager can match them to
questions. Candidate areas: scheduling policies, sampling and estimation error,
search-pruning strategies, compression trade-offs, queueing models.

**How we would know.** The experiments page lists several families, each with a
reproduce command and a stored result hash.

## 10. Reviewer workflow - partial: topic rejection shipped, finding resolution open

**Why.** Irregularities and contradictions are published but there was no way for a
reviewer to mark one resolved in the repository.

**What shipped.** `tools/reject_topic.py` closes a topic without destroying its history:
it appends a new record for the same primary key with `status="rejected"`, a timestamp,
the reason and an optional link, and records an `info` irregularity saying a reviewer
acted. The original record stays in `library/topics.jsonl`. Seven topics proposed from
the engine's own rendering scaffolding were closed this way rather than edited out.

**What it still needs.** The same mechanism for *findings*: a resolution record attached
to an irregularity or a contradiction, rendered next to the original text on the review
page rather than replacing it. Today a contradiction can only be resolved by writing its
`resolution` field by hand.

**How we would know.** The review page shows resolved items with their resolution and
keeps the original text visible.

## 11. Make the substance and synthesis layers pay off

**Why.** Both layers are now in place, but with one source reachable the corpus they
rank is mostly repository metadata. Their value shows up as source coverage grows.

**What it needs.** Nothing new in code. Re-run a cycle where arXiv, Crossref, PubMed and
the official statistical APIs answer, then compare the substantive share and the number
of cross-document statements before and after.

**How we would know.** The index page's substance figures move, and topic pages carry
synthesis statements that cite documents from different operators.

## Deliberately not planned

- **A language model in the extraction path.** It would increase recall and destroy the
  property that every published sentence is a span of a document. If a model is ever
  added, it will be as a *proposer* whose output must survive the same numeric and
  citation guards before publication.
- **Scraping sites that forbid it.** The register is API-first on purpose.
- **Any claim of "understanding".** The engine compares, counts and quotes. That is
  all it does, and the site says so.
