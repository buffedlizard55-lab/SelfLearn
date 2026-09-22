# Sources and provenance

Every factual statement this engine publishes is a quotation from a document it
retrieved from one of the sources below. This document records what those sources
are, who operates them, what evidence class each carries, and what rules the engine
follows when reading them.

## The register

There are 36 registered sources. Eighteen publish official data, nine are primary
sources, three are peer-reviewed indexes, four are reputable secondary compilations
and two are commentary. Four require a credential; the engine will not call those
APIs unless the credential is present in the environment.

| Source id | Name | Operator | Evidence class | Key required | Official documentation |
| --- | --- | --- | --- | --- | --- |
| `arxiv` | arXiv API | Cornell University (arXiv) | Original data, official API response, official document or dataset. | no | <https://info.arxiv.org/help/api/index.html> |
| `census_us` | U.S. Census Bureau API | U.S. Census Bureau, Department of Commerce | Data published by a government, standards body or international agency. | no | <https://www.census.gov/data/developers/data-sets.html> |
| `cisa_kev` | CISA Known Exploited Vulnerabilities Catalog | U.S. Cybersecurity and Infrastructure Security Agency | Data published by a government, standards body or international agency. | no | <https://www.cisa.gov/known-exploited-vulnerabilities-catalog> |
| `clinicaltrials` | ClinicalTrials.gov API v2 | U.S. National Library of Medicine | Original data, official API response, official document or dataset. | no | <https://clinicaltrials.gov/data-api/api> |
| `crossref` | Crossref REST API | Crossref (DOI registration agency, not-for-profit) | Peer-reviewed publication indexed by a DOI registry or PubMed. | no | <https://www.crossref.org/documentation/retrieve-metadata/rest-api/> |
| `datacite` | DataCite REST API | DataCite (international consortium, DOI agency for research data) | Original data, official API response, official document or dataset. | no | <https://support.datacite.org/docs/api> |
| `doaj` | DOAJ API | Directory of Open Access Journals | Peer-reviewed publication indexed by a DOI registry or PubMed. | no | <https://doaj.org/api/v3/docs> |
| `eia` | U.S. Energy Information Administration API v2 | U.S. Energy Information Administration | Data published by a government, standards body or international agency. | yes (EIA_API_KEY) | <https://www.eia.gov/opendata/documentation.php> |
| `eurostat` | Eurostat API (Statistics Explained / dissemination) | European Commission, Eurostat | Data published by a government, standards body or international agency. | no | <https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started> |
| `fred` | FRED API | Federal Reserve Bank of St. Louis | Data published by a government, standards body or international agency. | yes (FRED_API_KEY) | <https://fred.stlouisfed.org/docs/api/fred/> |
| `gbif` | GBIF Occurrence API | Global Biodiversity Information Facility (intergovernmental) | Data published by a government, standards body or international agency. | no | <https://techdocs.gbif.org/en/openapi/> |
| `github` | GitHub REST API | GitHub, Inc. (Microsoft) | Original data, official API response, official document or dataset. | no | <https://docs.github.com/en/rest> |
| `hackernews` | Hacker News API (via Algolia index) | Y Combinator (Hacker News); Algolia operates the search index | Expert commentary, editorial, blog post by a named practitioner. | no | <https://hn.algolia.com/api> |
| `imf` | IMF Data API (SDMX) | International Monetary Fund | Data published by a government, standards body or international agency. | no | <https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service> |
| `nasa_api` | NASA Open APIs | National Aeronautics and Space Administration | Data published by a government, standards body or international agency. | no | <https://api.nasa.gov/> |
| `ncei` | NOAA NCEI Climate Data Online API | U.S. National Oceanic and Atmospheric Administration, National Centers for Environmental Information | Data published by a government, standards body or international agency. | yes (NCEI_TOKEN) | <https://www.ncei.noaa.gov/cdo-web/webservices/v2> |
| `nvd` | NIST National Vulnerability Database API | U.S. National Institute of Standards and Technology | Data published by a government, standards body or international agency. | no | <https://nvd.nist.gov/developers/vulnerabilities> |
| `nws` | National Weather Service API | U.S. National Weather Service, NOAA | Data published by a government, standards body or international agency. | no | <https://www.weather.gov/documentation/services-web-api> |
| `oecd` | OECD Data Explorer API (SDMX) | Organisation for Economic Co-operation and Development | Data published by a government, standards body or international agency. | no | <https://data.oecd.org/fr/api/sdmx-json-documentation/> |
| `openalex` | OpenAlex API | OurResearch (non-profit) | Encyclopaedic or established secondary compilation. | no | <https://docs.openalex.org/> |
| `openlibrary` | Open Library API | Internet Archive (non-profit) | Encyclopaedic or established secondary compilation. | no | <https://openlibrary.org/developers/api> |
| `osv` | OSV (Open Source Vulnerabilities) API | Google Open Source Security Team, with the OSV community | Original data, official API response, official document or dataset. | no | <https://google.github.io/osv.dev/api/> |
| `patentsview` | USPTO Open Data Portal API (PatentsView data) | U.S. Patent and Trademark Office (Open Data Portal) | Data published by a government, standards body or international agency. | yes (USPTO_ODP_API_KEY) | <https://data.uspto.gov/apis/getting-started> |
| `pubchem` | PubChem PUG-REST | U.S. National Library of Medicine, NCBI | Original data, official API response, official document or dataset. | no | <https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest> |
| `pubmed` | NCBI E-utilities (PubMed) | U.S. National Library of Medicine, National Center for Biotechnology Information | Peer-reviewed publication indexed by a DOI registry or PubMed. | no | <https://www.ncbi.nlm.nih.gov/books/NBK25497/> |
| `rcsb_pdb` | RCSB Protein Data Bank Data API | RCSB PDB (Rutgers/UCSD/UCSF) for the wwPDB consortium | Original data, official API response, official document or dataset. | no | <https://data.rcsb.org/redoc/index.html> |
| `sec_edgar` | SEC EDGAR submissions and full-text search | U.S. Securities and Exchange Commission | Data published by a government, standards body or international agency. | no | <https://www.sec.gov/search-filings/edgar-application-programming-interfaces> |
| `semantic_scholar` | Semantic Scholar Academic Graph API | Allen Institute for AI (non-profit) | Encyclopaedic or established secondary compilation. | no | <https://www.semanticscholar.org/product/api> |
| `stackexchange` | Stack Exchange API | Stack Exchange Inc. | Expert commentary, editorial, blog post by a named practitioner. | no | <https://api.stackexchange.com/docs> |
| `un_sdg` | UN SDG API (United Nations Statistics Division) | United Nations Statistics Division | Data published by a government, standards body or international agency. | no | <https://unstats.un.org/sdgapi/swagger/> |
| `uniprot` | UniProt REST API | UniProt Consortium (EMBL-EBI, Swiss Institute of Bioinformatics, PDB) | Original data, official API response, official document or dataset. | no | <https://www.uniprot.org/help/api> |
| `usgs_earthquake` | USGS Earthquake Catalog (FDSN event service) | U.S. Geological Survey | Data published by a government, standards body or international agency. | no | <https://earthquake.usgs.gov/fdsnws/event/1/> |
| `who_gho` | WHO Global Health Observatory OData API | World Health Organization | Data published by a government, standards body or international agency. | no | <https://www.who.int/data/gho/info/gho-odata-api> |
| `wikimedia` | Wikimedia REST API (Wikipedia) | Wikimedia Foundation | Encyclopaedic or established secondary compilation. | no | <https://api.wikimedia.org/wiki/Main_Page> |
| `worldbank` | World Bank Indicators API | World Bank Group (international organisation) | Data published by a government, standards body or international agency. | no | <https://datahelpdesk.worldbank.org/knowledgebase/topics/125589> |
| `zenodo` | Zenodo REST API | CERN (OpenAIRE) | Original data, official API response, official document or dataset. | no | <https://developers.zenodo.org/> |

The same register is published as machine-readable data at
`docs/data/sources.json`, and the site's sources page adds the live status of each
source from the most recent run.

## The rules the engine follows

1. **Identify itself.** Every request carries a User-Agent naming the project and the
   repository URL.
2. **Wait its turn.** Requests to the same host are spaced by a politeness delay
   (default one second) and the client retries at most three times with backoff.
3. **Stay inside a budget.** A cycle is capped at 60 HTTP requests and 900 seconds.
   When the budget runs out the engine records that it stopped early rather than
   silently returning less.
4. **Never use a credential it does not have.** A source whose key is missing is
   reported as `credential_required`, with the environment variable to set and the
   operator's own key-request page.
5. **Record the licence.** Each document carries the licence named in the register,
   and the topic page shows it next to the source.
6. **Store before use.** The response body is hashed and written to
   `evidence/snapshots/` before any claim is cut from it.
7. **Distinguish unreachable from wrong.** A closed TLS session or a DNS failure is
   recorded as `unreachable`; a non-2xx response is recorded as `error` with its
   status code. The two produce different remedies.
8. **Check relevance.** A result whose text shares no meaningful token with the query
   is dropped, and the number dropped is reported.

## What each source can and cannot establish

The evidence hierarchy places original data and official API responses above
secondary compilations, and both above commentary. That ordering is why the register
records a class per source rather than a single "trusted" flag.

- An API response is a **primary source** for what the publisher said at that
  moment. It is not evidence about the world beyond that publisher's remit: a GitHub
  repository record establishes what GitHub recorded, not that the software works.
- Peer-reviewed indexes (Crossref, PubMed, DOAJ) establish that a paper exists with
  a given title, venue and date. They do not establish that its conclusions hold.
- Official statistical series (Eurostat, World Bank, IMF, OECD, Census, EIA, NCEI,
  WHO, USGS, NASA, UN SDG) establish the published value, with the publisher's own
  revision policy attached.
- Commentary (Hacker News) is recorded as commentary and is never used alone to
  support a fact claim.

## Verification of these links

Each row above lists the operator's own documentation page. During the build of this
project the documentation URLs that were least certain were re-checked against the
live web and corrected where the operator had moved them:

- Eurostat's API guide is now at
  <https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started>
  (the older Confluence wiki page is gone).
- The IMF data service documentation is at
  <https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service>.
- OECD's SDMX documentation is published at
  <https://data.oecd.org/fr/api/sdmx-json-documentation/>.
- DOAJ API v3 documentation is at <https://doaj.org/api/v3/docs>.
- GBIF's API reference is at <https://techdocs.gbif.org/en/openapi/>.
- WHO's Global Health Observatory OData API is documented at
  <https://www.who.int/data/gho/info/gho-odata-api>.

A reviewer can re-run the reachability check themselves:

```
python3 -m selflearn sources --probe
```

## Flagged for review

These are irregularities in the source layer that a reviewer should look at. They are
listed here rather than smoothed over.

1. **PatentsView has moved - resolved on 2026-09-21.** The adapter no longer calls
   `search.patentsview.org`. What the operator states, and where:

   - The legacy PatentsView website began migrating to the USPTO Open Data Portal on
     **20 March 2026**, and the PatentSearch API previously at `search.patentsview.org/api`
     is subject to interruption with **no estimated date** for reintroduction on the
     portal: <https://data.uspto.gov/support/transition-guide/patentsview>.
   - Previously issued PatentsView API keys **are not valid** for Open Data Portal APIs,
     so this source now takes `USPTO_ODP_API_KEY`, issued from
     <https://data.uspto.gov/apikey/key-reveal>.
   - Accessing the portal requires a USPTO.gov account with multi-factor authentication
     from **18 June 2026**: <https://data.uspto.gov/home>.
   - Portal APIs require the key in the `X-API-KEY` header; the documented examples use
     `GET https://api.uspto.gov/api/v1/patent/applications/search`:
     <https://data.uspto.gov/apis/getting-started>.
   - The former PatentsView tables are served as Open Data Portal bulk datasets through
     `GET https://api.uspto.gov/api/v1/datasets/products/search`:
     <https://data.uspto.gov/apis/bulk-data/search>. Bulk file downloads are capped at
     20 per file per year per key, with HTTP 429 on the 21st:
     <https://data.uspto.gov/apis/bulk-data/download>.
   - The `q` free-form query parameter and `offset`/`limit` pagination for the
     application search are documented in the operator's own query specification:
     <https://data.uspto.gov/documents/documents/ODP-API-Query-Spec.pdf>.

   The register keeps the source id `patentsview` so records already in the library stay
   attributable, and the adapter (`UsptoOdpSource` in `selflearn/fetch/sources.py`)
   queries both endpoints above. The bulk-products response is parsed field by field from
   the sample the operator publishes; any other shape is stored verbatim rather than
   guessed at. Covered by `tests/test_layers.py::UsptoOdpAdapterTests`. This source has
   never been called with a real key from this repository, because none is configured;
   that gap is item 3 below.
2. **Five sources were unreachable from the environment this build ran in.** The
   sandbox used for the build permits egress only to `github.com`, `api.github.com`,
   `codeload.github.com`, `pypi.org` and `registry.npmjs.org`. arXiv, Crossref,
   Hacker News, OpenAlex and Semantic Scholar all failed at the TLS layer, and the run
   recorded them as unreachable with a warning. This is a property of the build
   environment, not of the sources: the same probe from an unrestricted network
   reaches them, and the engine's snapshot mode can replay documents retrieved
   elsewhere.
3. **Four sources need credentials that are not configured.** `eia`, `fred`, `ncei`
   and `patentsview` are registered but never called, because no key is present. Each
   question that would have used them records a `credential_required` status naming
   the variable to set.
4. **Two sources cover news and commentary only.** Hacker News is useful for noticing
   that something is being discussed; it is not evidence that the thing is true. Its
   class reflects that, and no `supported` claim about the world rests on it alone.

## Change scanning

The design document asks the engine to notice what changed, not only to answer
questions. A change scan uses a different request shape from a question-driven poll,
and only some operators document one. The engine therefore scans only the sources
below, using only the filter that operator documents, and records the window it used.
A source with no documented filter is reported as having none, rather than being
polled and having its whole result set described as new.

| Source | Documented filter | Endpoint | Official documentation |
| --- | --- | --- | --- |
| `crossref` | `filter=from-index-date:<date>` ("reindexed in the API at or after the given date or time; includes changes from members, Crossref, and external sources") | `https://api.crossref.org/works` | <https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/> |
| `arxiv` | `sortBy=submittedDate` or `lastUpdatedDate` with `sortOrder=ascending\|descending` | `https://export.arxiv.org/api/query` | <https://info.arxiv.org/help/api/user-manual.html> |
| `github` | the `pushed:` qualifier, e.g. `q=<terms> pushed:>=<date>` ("the most recent commit made on any branch") | `https://api.github.com/search/repositories` | <https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories> |
| `nvd` | `lastModStartDate` **and** `lastModEndDate` (both required; range at most 120 days) | `https://services.nvd.nist.gov/rest/json/cves/2.0` | <https://nvd.nist.gov/developers/vulnerabilities> |
| `usgs_earthquake` | `starttime` / `endtime` (ISO-8601, UTC assumed); `updatedafter` for revisions | `https://earthquake.usgs.gov/fdsnws/event/1/query` | <https://earthquake.usgs.gov/fdsnws/event/1/> |

Implementation: `selflearn/fetch/changes.py`; command `python3 -m selflearn scan`.
The window starts where the previous successful scan for that source ended, and the
first scan says plainly that its window is a default look-back rather than a real
interval. Items seen for the first time become *questions*, never claims: nothing from
a change scan has been verified against a document yet.

## Verifying these links yourself

```
python3 tools/verify_links.py          # resolve every URL in the register, the
                                       # change mechanisms and the prose
python3 -m selflearn sources --probe   # reachability of each registered API
python3 -m selflearn credentials       # which keyed sources are enabled, and where
                                       # a free key is issued for the ones that are not
```

`verify_links.py` writes `reports/link_check.json` with the HTTP status, the URL after
redirects and the error for each of the URLs this project publishes. It asserts nothing
about page *content*. A sandbox with restricted egress records `unreachable` with the
transport error, which is a property of the machine and is distinguishable in the report
from a genuine 404.

## Adding a source

Adding a source means three edits, all of which the test suite checks:

1. Register a `SourceSpec` in `selflearn/fetch/registry.py` with operator, base URL,
   documentation URL, evidence class, licence, key requirement and rate-limit note.
2. Add an adapter in `selflearn/fetch/sources.py` that returns `ParsedItem`s whose
   text is rendered by `render_attributed_record`, so every sentence names the record
   it describes.
3. Add the source id to a topic in `data/seeds/topics.json` if it should be polled.

The test `test_every_registered_source_has_an_adapter` fails if step one happens
without step two, which is how the register and the adapters are kept in step.
