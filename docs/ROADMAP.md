# Roadmap

Ordered by what most increases the value of the output per unit of work. Each item
says why it matters, what it needs, and how we would know it worked.

## 1. Reach more sources (highest value)

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

## 2. Finish the credential path

**Why.** `eia`, `fred`, `ncei` and `patentsview` are registered but never called,
because no key is present. Those are exactly the sources that answer quantitative
questions about energy, economics and climate.

**What it needs.** Repository secrets named as the register says
(`EIA_API_KEY`, `FRED_API_KEY`, `NCEI_TOKEN`, `PATENTSVIEW_API_KEY`), free in each
case. The workflow already passes them through when present.

**How we would know.** The sources page shows them as reachable with `credential_required`
cleared, and claims appear with those sources named.

## 3. Repair the PatentsView adapter

**Why.** PatentsView was folded into the USPTO Open Data Portal; the adapter still
calls the older host. This is flagged in `docs/SOURCES.md`.

**What it needs.** The portal's endpoint shape and a key, then an adapter update and a
fixture-based test.

**How we would know.** A patent query returns records, and the flagged item is closed
with a note rather than deleted.

## 4. Substance filter for claims

**Why.** A verified claim can still be trivial. "The record for X reports licence
MIT" is checkable but not knowledge. The engine should prefer claims that carry a
quantity, a date, a comparison or a mechanism, and say so when it only has metadata.

**What it needs.** A published scoring rule over claim features (numbers, dates,
comparatives, negations, sentence length, evidence class), applied when selecting what
to show first, plus honest labelling of the rest as metadata.

**How we would know.** The share of claims carrying a quantity or date rises, and the
topic pages lead with them.

## 5. Cross-document synthesis, with the same discipline

**Why.** The most valuable output of a research loop is a statement that holds across
several sources. Today every claim is single-source.

**What it needs.** Aggregation across documents that keeps the discipline: a
multi-source statement must be composed only of figures present in the sources it
cites, and it must record the set of evidence ids behind it. The derived-claim
machinery (`claim_kind=derived`, `context_numbers`, re-checked by the audit) is the
existing foundation.

**How we would know.** A new claim kind appears whose audit re-check recomputes the
same numbers from the cited claims, and disagreement counts stay at zero.

## 6. Change-driven scanning (design section 1)

**Why.** The engine currently answers questions. The design document also asks it to
notice change: new papers, new datasets, new releases.

**What it needs.** Per-source "what changed since the last run" support. Several
registered APIs already offer it: Crossref `from-index-date`, arXiv's sorted feeds,
NASA and USGS date filters, GitHub `pushed:>` and release feeds.

**How we would know.** A run reports items seen for the first time, with the window
used, and the discovery layer turns them into questions.

## 7. Topic proposal from an open scan (design section 12)

**Why.** Seed topics are still human-authored.

**What it needs.** A novelty measure computed from what the engine already holds
(vocabulary overlap against the existing library), the importance and potential
components that already exist in `think/discovery.py`, and a rule for promoting a
candidate to a topic.

**How we would know.** A new topic appears whose provenance is a set of claims and
whose score components are published.

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

## 10. Reviewer workflow

**Why.** Irregularities and contradictions are published but there is no way for a
reviewer to mark one resolved in the repository.

**What it needs.** A rule for accepting a resolution record (who, when, why, with a
link), and rendering it next to the original finding rather than replacing it.

**How we would know.** The review page shows resolved items with their resolution and
keeps the original text visible.

## Deliberately not planned

- **A language model in the extraction path.** It would increase recall and destroy the
  property that every published sentence is a span of a document. If a model is ever
  added, it will be as a *proposer* whose output must survive the same numeric and
  citation guards before publication.
- **Scraping sites that forbid it.** The register is API-first on purpose.
- **Any claim of "understanding".** The engine compares, counts and quotes. That is
  all it does, and the site says so.
