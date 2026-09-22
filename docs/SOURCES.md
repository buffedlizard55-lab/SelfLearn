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
- OECD's SDMX documentation is published at
  <https://data.oecd.org/fr/api/sdmx-json-documentation/>.
- DOAJ API v3 documentation is at <https://doaj.org/api/v3/docs>.
- GBIF's API reference is at <https://techdocs.gbif.org/en/openapi/>.
- WHO's Global Health Observatory OData API is documented at
  <https://www.who.int/data/gho/info/gho-odata-api>.

### Every published URL, resolved from a host with unrestricted egress

The whole register is not spot-checked; it is resolved in full on every push, by the
`links` job of `.github/workflows/tests.yml`, which runs `tools/verify_links.py` on a
GitHub runner and commits the result to `reports/link_check.json`. The site publishes
that file on its **Official links** page with the machine that produced it named.

The run of 2026-09-22T03:49:20Z (`GitHub Actions ubuntu-latest (unrestricted egress)`)
resolved **120 published URLs: 103 resolved, 17 did not**. Reading the 17 rather than
counting them is what makes the number useful:

| Outcome | Count | What it means |
| --- | --- | --- |
| HTTP 403 / 401 / 422 on an API host | 15 | The host answered and refused an unauthenticated or parameterless request. `api.uspto.gov` answers `Missing Authentication Token`; `api.github.com/search/repositories` answers that the `q` parameter is missing. Both are the endpoint working as documented, not a broken link. |
| HTTP 403 on an operator's HTML page | 8 | Bot protection. `cisa.gov`, `imf.org`, `sec.gov`, `noaa.gov`, `gbif.org` and `oecd.org` returned "Access Denied" or a "Just a moment..." interstitial to a non-browser client. The page is not gone; it declines automated requests. |
| HTTP 404 | 1 | **Genuinely moved.** `https://doaj.org/apply-for-api-key/` no longer exists. Fixed - see below. |
| Name does not resolve | 1 | **Genuinely unreachable.** `datahelp.imf.org` failed DNS. Flagged, not replaced - see below. |
| Read timeout | 1 | `export.arxiv.org/api/query` timed out on all three attempts from a runner with unrestricted egress. arXiv asks for a 3 second delay between requests and rate-limits; this is a finding about arXiv's export host, not about the adapter. |

The counts above overlap: the 403s appear in both the first and second rows depending
on whether the host is an API or a web page.

Two corrections came out of that run, and both are recorded rather than quietly made:

- **DOAJ's key-request page returned HTTP 404.** There is no public key-application
  page. DOAJ's own API documentation states: "API keys are usually only available to
  publishers who submit data to DOAJ. If you already have an account, please log in,
  click 'My Account' and 'Settings' to see your API key." (<https://doaj.org/api/v4/docs>,
  read 2026-09-22.) `key_url` now points at that page, and the register's rate-limit
  note carries the quotation, because a link to a page that says how to get a key is
  worth more than a link to a form that no longer exists.
- **The IMF documentation host does not resolve.** `datahelp.imf.org` failed DNS from
  the runner and from a second, unrelated network. `https://api.imf.org/` answered
  HTTP 502 when it was checked. The pages that do describe the `api.imf.org` SDMX 3.0
  endpoints are third-party profiles, and this register does not cite third parties as
  an operator's documentation. The URL is therefore **flagged, not replaced**:
  substituting an address that could not be verified against an IMF-operated page is
  precisely the failure this project exists to avoid. There is a second problem behind
  it - the register's `base_url` is `https://api.imf.org/external/sdmx`, while the
  linked page documents the older `http://dataservices.imf.org/REST/SDMX_JSON.svc`
  service, so the documentation and the endpoint describe different APIs. Resolving
  this needs a human to open IMF's own data portal and record the page.

A reviewer can re-run either check themselves:

```
python3 -m selflearn sources --probe      # can each source be reached?
python3 tools/verify_links.py             # does every published URL resolve?
python3 tools/link_check_changed.py       # did any URL change outcome?
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
   - From **18 August 2026** the USPTO.gov profile must carry four additional fields of
     information, and "failure to do so will result in loss of access to ODP products and
     API key" - relevant to anyone provisioning `USPTO_ODP_API_KEY` for this register:
     <https://data.uspto.gov/support/transition-guide/patentsview> (re-read 2026-09-22).
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
5. **A configured credential was not being sent - found and fixed 2026-09-22.** Reading
   the credential path line by line showed that `eia`, `fred` and `ncei` declare
   `requires_key=True` and a `key_env`, and `python3 -m selflearn credentials`
   reported them as enabled once the variable was set - but no adapter ever put the
   credential on the request. `GenericSource.requests()` built the request from the
   endpoint and its extra parameters only, so setting the secret changed nothing and
   every call would have gone out unauthenticated and been refused. Separately,
   `.github/workflows/research-loop.yml` passed `PATENTSVIEW_API_KEY`, the name the
   register stopped reading when it moved to the USPTO Open Data Portal.

   Both are fixed. Each mechanism is now transcribed in `CREDENTIAL_MECHANISMS`
   (`selflearn/fetch/sources.py`) with the operator's own page and their own words
   beside it, verified 2026-09-22:

   | Source | Mechanism | Operator's documentation |
   | --- | --- | --- |
   | `eia` | `?api_key=<key>` | "To use an API key, place it as a parameter after the route." <https://www.eia.gov/opendata/documentation.php> |
   | `fred` | `?api_key=<key>` | <https://fred.stlouisfed.org/docs/api/fred/series_search.html> |
   | `ncei` | `token: <token>` header | 'Assigned token is required to use these queries and must be in the header.' <https://www.ncei.noaa.gov/cdo-web/webservices/v2> |
   | `github` | `Authorization: Bearer <token>` | <https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api> |
   | `pubmed` | `?api_key=<key>` (both stages) | "After creating the key, users should include it in each E-utility request by assigning it to the api_key parameter." <https://www.ncbi.nlm.nih.gov/books/NBK25497/> |
   | `census_us` | `?key=<key>` | "Once you have a key, insert &key= followed by your key code at the end of your API data calls: &key=your key here" <https://www.census.gov/data/developers/guidance/api-user-guide.API_Key.html> |
   | `nvd` | `apiKey: <key>` header | "API keys are passed in the request header using apiKey:{key value}. Please note, the {key value} is case sensitive" <https://nvd.nist.gov/developers/api-workflows> |
   | `semantic_scholar` | `x-api-key: <key>` header | "If you are using an API key, it must be set in the header x-api-key (case-sensitive)." <https://api.semanticscholar.org/api-docs/> |
   | `stackexchange` | `Authorization: Bearer <key>` header | "Your application's API key or access token must be provided using the authorization header Authorization: Bearer {API key or access token}." <https://api.stackexchange.com/docs/authentication> |
   | `doaj` | `?api_key=<key>` (authenticated routes) | OpenAPI parameter `{"in": "query", "name": "api_key"}` in <https://doaj.org/api/v4/swagger.json> |
   | `nasa_api` | `?api_key=<key>` (adapter-applied, DEMO_KEY fallback) | <https://api.nasa.gov/> |
   | `patentsview` | `X-API-KEY: <key>` header (adapter-applied) | <https://data.uspto.gov/apis/getting-started> |

   All twelve keyed sources now transmit their credential; `declared_but_not_transmitted`
   is empty. The `declared, not sent` label stays in the code for any future
   registration without a transcription, so a variable can never again be named
   without a mechanism and look as though it worked. Guessing an authentication
   scheme is not an option; transcribing the operator's page is.

   The line-by-line pass on 2026-09-22 also found that `PubMedSource` built both of
   its requests (`esearch`, then `efetch`) without calling `apply_credential`, so
   even a transcribed key would have authenticated the search and then spent the
   abstract fetch unauthenticated. Both stages now go through the shared path, and
   `CredentialPathTests.test_pubmed_stages_both_carry_the_key` pins it.
   Covered by `tests/test_layers.py::CredentialPathTests`, including the test that
   every keyed source in the register transmits and none is gated on a credential
   the engine then fails to send.
6. **The GitHub rate-limit note was wrong for the token the scheduled run has.** The
   register said "5,000 requests/hour with a token". GitHub documents 5,000/hour for a
   *personal access token* and **1,000/hour per repository** for the `GITHUB_TOKEN`
   built into GitHub Actions - which is the token the workflow has
   (<https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>,
   read 2026-09-22). The note now states all three figures and cites the page.
7. **The IMF documentation host is unreachable and the endpoint is unaligned - flagged 2026-09-22.**
   When every URL was checked from a runner with unrestricted egress,
   `datahelp.imf.org` failed DNS, and it failed from a second, unrelated network as
   well. `https://api.imf.org/` answered HTTP 502. Furthermore, the register's
   `base_url` is `https://api.imf.org/external/sdmx` while the linked page documents
   the legacy `http://dataservices.imf.org/REST/SDMX_JSON.svc` service. The URL is
   flagged rather than silently swapped with a third-party directory. A human reviewer
   needs to visit IMF's data portal to verify the current official documentation URL.

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
| `nvd` | `lastModStartDate` **and** `lastModEndDate` (both required; range at most 120 days; extended ISO-8601 datetimes, e.g. `2026-09-15T00:00:00.000+00:00` - the API 1.0 nonstandard form answers HTTP 404 "Invalid ISO 8601 date/time format", observed 2026-09-22) | `https://services.nvd.nist.gov/rest/json/cves/2.0` | <https://nvd.nist.gov/developers/vulnerabilities>, transition guide <https://nvd.nist.gov/general/news/api-20-announcements> |
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
