"""Registry of public data sources, with the provenance a reviewer needs.

Every source carries: who operates it, the official documentation URL, whether a
credential is required and where a free one is issued, the applicable licence or
terms, and the evidence class it is allowed to contribute.

Rules encoded here (and enforced in :mod:`selflearn.fetch.sources`):

1. A source is only registered if it is operated by the body that owns the data
   (a laboratory, an agency, a registry, a standards body) or by a non-profit
   that publishes the authoritative index. Aggregators of unknown provenance are
   not registered.
2. A source that requires a credential is *listed* but never called without one.
   It is published as ``credential_required`` so the gap is visible rather than
   silently missing.
3. Nothing here asserts a fact about the world. It asserts where a fact can be
   looked up. Facts only enter the library through retrieved evidence.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..config import EVIDENCE_RANK, SEED_DIR


@dataclass
class SourceSpec:
    source_id: str
    name: str
    operator: str
    base_url: str
    docs_url: str
    evidence_class: str
    requires_key: bool = False
    key_env: str | None = None
    key_url: str | None = None
    license_name: str = ""
    license_url: str = ""
    terms_url: str = ""
    rate_limit_note: str = ""
    topics: list[str] = field(default_factory=list)
    notes: str = ""
    enabled: bool = True

    @property
    def evidence_rank(self) -> int:
        return EVIDENCE_RANK.get(self.evidence_class, 9)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_rank"] = self.evidence_rank
        return payload


def _spec(**kwargs: Any) -> SourceSpec:
    return SourceSpec(**kwargs)


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------
REGISTRY: dict[str, SourceSpec] = {}


def _register(spec: SourceSpec) -> SourceSpec:
    if spec.source_id in REGISTRY:  # pragma: no cover - guard against typos
        raise ValueError(f"duplicate source id: {spec.source_id}")
    if spec.evidence_class not in EVIDENCE_RANK:
        raise ValueError(f"{spec.source_id}: unknown evidence class {spec.evidence_class!r}")
    REGISTRY[spec.source_id] = spec
    return spec


# === Scholarly literature ==================================================
_register(
    _spec(
        source_id="crossref",
        name="Crossref REST API",
        operator="Crossref (DOI registration agency, not-for-profit)",
        base_url="https://api.crossref.org",
        docs_url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
        evidence_class="peer_reviewed",
        license_name="Metadata: CC0; abstracts remain publisher copyright",
        license_url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
        rate_limit_note="Polite pool: include a mailto parameter. No hard published cap for modest use.",
        topics=["all academic fields", "DOI resolution", "journal articles", "conference papers"],
        notes="The DOI registration agency. A DOI found here is a durable identifier for the record of the work itself.",
    )
)

_register(
    _spec(
        source_id="arxiv",
        name="arXiv API",
        operator="Cornell University (arXiv)",
        base_url="https://export.arxiv.org/api",
        docs_url="https://info.arxiv.org/help/api/index.html",
        evidence_class="primary_source",
        license_name="Author-deposited preprints; individual licences vary (often CC-BY)",
        license_url="https://info.arxiv.org/help/license/index.html",
        rate_limit_note="arXiv asks for a 3 second delay between requests and a descriptive User-Agent.",
        topics=["physics", "mathematics", "computer science", "quantitative biology", "economics"],
        notes="Preprints: the authors' own manuscript, NOT peer reviewed. Claims from arXiv are labelled accordingly.",
    )
)

_register(
    _spec(
        source_id="openalex",
        name="OpenAlex API",
        operator="OurResearch (non-profit)",
        base_url="https://api.openalex.org",
        docs_url="https://docs.openalex.org/",
        evidence_class="reputable_secondary",
        license_name="CC0",
        license_url="https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication",
        rate_limit_note="Polite pool via mailto; 10 requests/second, 100,000 requests/day.",
        topics=["all academic fields", "citation graph", "research trend detection"],
        notes="A catalogue of works and citations, i.e. a secondary index. The underlying work is what counts as primary evidence.",
    )
)

_register(
    _spec(
        source_id="datacite",
        name="DataCite REST API",
        operator="DataCite (international consortium, DOI agency for research data)",
        base_url="https://api.datacite.org",
        docs_url="https://support.datacite.org/docs/api",
        evidence_class="primary_source",
        license_name="Metadata CC0; datasets carry their own licences",
        license_url="https://datacite.org/legal/",
        rate_limit_note="No key required for public reads.",
        topics=["research datasets", "software citations", "repositories"],
        notes="DOI registry for datasets and software, distinct from Crossref's literature scope.",
    )
)

_register(
    _spec(
        source_id="pubmed",
        name="NCBI E-utilities (PubMed)",
        operator="U.S. National Library of Medicine, National Center for Biotechnology Information",
        base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        docs_url="https://www.ncbi.nlm.nih.gov/books/NBK25497/",
        evidence_class="peer_reviewed",
        license_name="U.S. Government work: generally public domain; some records carry publisher terms",
        license_url="https://www.ncbi.nlm.nih.gov/home/about/policies/",
        rate_limit_note="3 requests/second without an API key; 10 requests/second with one.",
        key_env="NCBI_API_KEY",
        key_url="https://www.ncbi.nlm.nih.gov/account/settings/",
        topics=["biomedicine", "clinical research", "public health", "genomics"],
        notes="Biomedical literature index. The API key is optional but raises the permitted request rate.",
    )
)

_register(
    _spec(
        source_id="clinicaltrials",
        name="ClinicalTrials.gov API v2",
        operator="U.S. National Library of Medicine",
        base_url="https://clinicaltrials.gov/api/v2",
        docs_url="https://clinicaltrials.gov/data-api/api",
        evidence_class="primary_source",
        license_name="U.S. Government work: public domain",
        license_url="https://clinicaltrials.gov/about-site/terms-conditions",
        rate_limit_note="No key required; NLM asks that clients keep to a modest request rate.",
        topics=["clinical trials", "medicine", "study design", "interventions"],
        notes="The trial registry of record for studies conducted under U.S. law. Registry entries, not results publications.",
    )
)

_register(
    _spec(
        source_id="doaj",
        name="DOAJ API",
        operator="Directory of Open Access Journals",
        base_url="https://doaj.org/api",
        docs_url="https://doaj.org/api/v3/docs",
        evidence_class="peer_reviewed",
        license_name="Metadata CC0 per DOAJ terms",
        license_url="https://doaj.org/terms/",
        rate_limit_note="Public endpoints are rate limited; a free API key is available for higher limits.",
        key_env="DOAJ_API_KEY",
        key_url="https://doaj.org/apply-for-api-key/",
        topics=["open access journals", "peer-reviewed articles"],
        notes="Index of vetted open-access journals; used to confirm that a venue is genuinely peer reviewed.",
    )
)

_register(
    _spec(
        source_id="semantic_scholar",
        name="Semantic Scholar Academic Graph API",
        operator="Allen Institute for AI (non-profit)",
        base_url="https://api.semanticscholar.org/graph/v1",
        docs_url="https://www.semanticscholar.org/product/api",
        evidence_class="reputable_secondary",
        license_name="See API terms; some fields carry S2-specific terms",
        license_url="https://www.semanticscholar.org/product/api/license",
        rate_limit_note="Unauthenticated requests are shared-pool rate limited; a free key raises limits.",
        key_env="S2_API_KEY",
        key_url="https://www.semanticscholar.org/product/api",
        topics=["all academic fields", "abstracts", "citation counts"],
        notes="Secondary index with abstracts; used for discovery and cross-checking, not as the primary record.",
    )
)

_register(
    _spec(
        source_id="zenodo",
        name="Zenodo REST API",
        operator="CERN (OpenAIRE)",
        base_url="https://zenodo.org/api",
        docs_url="https://developers.zenodo.org/",
        evidence_class="primary_source",
        license_name="Metadata CC0; each deposit carries its own licence",
        license_url="https://about.zenodo.org/policies/",
        rate_limit_note="No key required for public reads; access tokens are only needed to deposit.",
        topics=["research data", "software releases", "preprints", "reports"],
        notes="CERN-operated repository giving every deposit a DOI.",
    )
)

# === Government and intergovernmental data =================================
_register(
    _spec(
        source_id="worldbank",
        name="World Bank Indicators API",
        operator="World Bank Group (international organisation)",
        base_url="https://api.worldbank.org/v2",
        docs_url="https://datahelpdesk.worldbank.org/knowledgebase/topics/125589",
        evidence_class="official_data",
        license_name="CC BY 4.0",
        license_url="https://datacatalog.worldbank.org/public-licenses",
        rate_limit_note="No key required; responses paginate at 1000 rows per request.",
        topics=["development economics", "energy", "health", "education", "infrastructure"],
        notes="Country-level indicators with documented definitions and methodology notes.",
    )
)

_register(
    _spec(
        source_id="eurostat",
        name="Eurostat API (Statistics Explained / dissemination)",
        operator="European Commission, Eurostat",
        base_url="https://ec.europa.eu/eurostat/api/dissemination",
        docs_url="https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started",
        evidence_class="official_data",
        license_name="CC BY 4.0 unless otherwise stated",
        license_url="https://ec.europa.eu/eurostat/web/main/help/copyright-notice",
        rate_limit_note="No key required; the API is documented for programmatic access.",
        topics=["European statistics", "energy", "labour", "industry", "environment"],
        notes="Official statistics for the EU; series codes are the stable identifier.",
    )
)

_register(
    _spec(
        source_id="oecd",
        name="OECD Data Explorer API (SDMX)",
        operator="Organisation for Economic Co-operation and Development",
        base_url="https://sdmx.oecd.org/public/rest/v1",
        docs_url="https://data.oecd.org/fr/api/sdmx-json-documentation/",
        evidence_class="official_data",
        license_name="OECD terms and conditions; largely CC BY 4.0",
        license_url="https://www.oecd.org/termsandconditions/",
        rate_limit_note="No key required. SDMX REST returns XML or CSV via the format parameter.",
        topics=["economic policy", "education", "health systems", "taxation", "innovation"],
        notes="Cross-country comparable indicators produced by an intergovernmental body.",
    )
)

_register(
    _spec(
        source_id="imf",
        name="IMF Data API (SDMX)",
        operator="International Monetary Fund",
        base_url="https://api.imf.org/external/sdmx",
        docs_url="https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service",
        evidence_class="official_data",
        license_name="IMF terms of use",
        license_url="https://www.imf.org/en/About/terms",
        rate_limit_note="No key required for public datasets.",
        topics=["macroeconomics", "balance of payments", "fiscal policy", "exchange rates"],
        notes="Official macroeconomic aggregates published by the Fund.",
    )
)

_register(
    _spec(
        source_id="un_sdg",
        name="UN SDG API (United Nations Statistics Division)",
        operator="United Nations Statistics Division",
        base_url="https://unstats.un.org/SDGAPI/v1",
        docs_url="https://unstats.un.org/sdgapi/swagger/",
        evidence_class="official_data",
        license_name="UN terms of use for statistical data",
        license_url="https://www.un.org/en/about-us/terms-of-use",
        rate_limit_note="No key required.",
        topics=["sustainable development goals", "global development", "indicators"],
        notes="Official SDG indicator series with custodian-agency attributions.",
    )
)

_register(
    _spec(
        source_id="who_gho",
        name="WHO Global Health Observatory OData API",
        operator="World Health Organization",
        base_url="https://ghoapi.azureedge.net/api",
        docs_url="https://www.who.int/data/gho/info/gho-odata-api",
        evidence_class="official_data",
        license_name="CC BY-NC-SA 3.0 IGO for WHO publications; check per indicator",
        license_url="https://www.who.int/about/policies/publishing/copyright",
        rate_limit_note="OData reads are open; no key documented.",
        topics=["global health", "mortality", "immunisation", "health systems"],
        notes="WHO indicator data, each indicator carrying its own metadata record.",
    )
)

_register(
    _spec(
        source_id="census_us",
        name="U.S. Census Bureau API",
        operator="U.S. Census Bureau, Department of Commerce",
        base_url="https://api.census.gov/data",
        docs_url="https://www.census.gov/data/developers/data-sets.html",
        evidence_class="official_data",
        key_env="CENSUS_API_KEY",
        key_url="https://api.census.gov/data/key_signup.html",
        license_name="U.S. Government work: public domain",
        license_url="https://www.census.gov/data/developers/about/terms-of-service.html",
        rate_limit_note="Works without a key up to a low daily cap; a free key raises it.",
        topics=["population", "housing", "business", "income", "demographics"],
        notes="Official decennial and survey data for the United States.",
    )
)

_register(
    _spec(
        source_id="fred",
        name="FRED API",
        operator="Federal Reserve Bank of St. Louis",
        base_url="https://api.stlouisfed.org/fred",
        docs_url="https://fred.stlouisfed.org/docs/api/fred/",
        evidence_class="official_data",
        requires_key=True,
        key_env="FRED_API_KEY",
        key_url="https://fredaccount.stlouisfed.org/apikeys",
        license_name="Series carry source-specific terms; many are U.S. Government public domain",
        license_url="https://fred.stlouisfed.org/legal/",
        rate_limit_note="Free key required; documented usage limits apply per key.",
        topics=["interest rates", "inflation", "employment", "monetary aggregates"],
        notes="A distribution platform for series produced by the issuing agencies; the series' own source is authoritative.",
    )
)

_register(
    _spec(
        source_id="eia",
        name="U.S. Energy Information Administration API v2",
        operator="U.S. Energy Information Administration",
        base_url="https://api.eia.gov/v2",
        docs_url="https://www.eia.gov/opendata/documentation.php",
        evidence_class="official_data",
        requires_key=True,
        key_env="EIA_API_KEY",
        key_url="https://www.eia.gov/opendata/register.php",
        license_name="U.S. Government work: public domain",
        license_url="https://www.eia.gov/about/copyrights_reuse.php",
        rate_limit_note="Free key required; documented request limits per key.",
        topics=["energy supply", "electricity", "emissions", "petroleum", "renewables"],
        notes="Official U.S. energy statistics with documented methodologies.",
    )
)

_register(
    _spec(
        source_id="ncei",
        name="NOAA NCEI Climate Data Online API",
        operator="U.S. National Oceanic and Atmospheric Administration, National Centers for Environmental Information",
        base_url="https://www.ncei.noaa.gov/cdo-web/api/v2",
        docs_url="https://www.ncei.noaa.gov/cdo-web/webservices/v2",
        evidence_class="official_data",
        requires_key=True,
        key_env="NCEI_TOKEN",
        key_url="https://www.ncdc.noaa.gov/cdo-web/token",
        license_name="U.S. Government work: public domain",
        license_url="https://www.noaa.gov/information-technology/open-data-dissemination",
        rate_limit_note="Free token required; 5 requests/second and 10,000 requests/day per token.",
        topics=["climate", "temperature", "precipitation", "station records"],
        notes="Daily and monthly station observations from the U.S. national archive.",
    )
)

_register(
    _spec(
        source_id="nws",
        name="National Weather Service API",
        operator="U.S. National Weather Service, NOAA",
        base_url="https://api.weather.gov",
        docs_url="https://www.weather.gov/documentation/services-web-api",
        evidence_class="official_data",
        license_name="U.S. Government work: public domain",
        license_url="https://www.weather.gov/disclaimer",
        rate_limit_note="No key, but a descriptive User-Agent is mandatory and documented as such.",
        topics=["weather forecasts", "severe weather alerts", "observations"],
        notes="The operational forecast API of the U.S. National Weather Service.",
    )
)

_register(
    _spec(
        source_id="usgs_earthquake",
        name="USGS Earthquake Catalog (FDSN event service)",
        operator="U.S. Geological Survey",
        base_url="https://earthquake.usgs.gov/fdsnws/event/1",
        docs_url="https://earthquake.usgs.gov/fdsnws/event/1/",
        evidence_class="official_data",
        license_name="U.S. Government work: public domain",
        license_url="https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
        rate_limit_note="No key required; USGS asks clients not to send rapid repeated queries.",
        topics=["seismology", "hazards", "geophysics"],
        notes="Authoritative seismic event catalogue with per-event review status.",
    )
)

_register(
    _spec(
        source_id="nasa_api",
        name="NASA Open APIs",
        operator="National Aeronautics and Space Administration",
        base_url="https://api.nasa.gov",
        docs_url="https://api.nasa.gov/",
        evidence_class="official_data",
        key_env="NASA_API_KEY",
        key_url="https://api.nasa.gov/#signUp",
        license_name="U.S. Government work: public domain",
        license_url="https://www.nasa.gov/nasa-brand-center/images-and-media/",
        rate_limit_note="DEMO_KEY works for exploration at 30 requests/hour and 50 requests/day; a free key raises this.",
        topics=["planetary science", "near-earth objects", "space weather", "earth observation"],
        notes="Aggregated first-party NASA data services; each endpoint has its own upstream dataset.",
    )
)

_register(
    _spec(
        source_id="sec_edgar",
        name="SEC EDGAR submissions and full-text search",
        operator="U.S. Securities and Exchange Commission",
        base_url="https://data.sec.gov",
        docs_url="https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
        evidence_class="official_data",
        license_name="U.S. Government work: public domain",
        license_url="https://www.sec.gov/privacy#dissemination",
        rate_limit_note="SEC requires a declared User-Agent with contact details and caps automated access at 10 requests/second.",
        topics=["public company filings", "financial statements", "corporate disclosure"],
        notes="The primary filing repository for U.S. public companies. Filings are primary documents.",
    )
)

_register(
    _spec(
        source_id="nvd",
        name="NIST National Vulnerability Database API",
        operator="U.S. National Institute of Standards and Technology",
        base_url="https://services.nvd.nist.gov/rest/json",
        docs_url="https://nvd.nist.gov/developers/vulnerabilities",
        evidence_class="official_data",
        key_env="NVD_API_KEY",
        key_url="https://nvd.nist.gov/developers/request-an-api-key",
        license_name="U.S. Government work: public domain",
        license_url="https://www.nist.gov/oism/copyrights",
        rate_limit_note="Without a key NVD permits 5 requests per 30 seconds; with a key 50 per 30 seconds.",
        topics=["software vulnerabilities", "CVSS scoring", "CVE records"],
        notes="U.S. national vulnerability repository; each CVE carries an analysis record.",
    )
)

_register(
    _spec(
        source_id="cisa_kev",
        name="CISA Known Exploited Vulnerabilities Catalog",
        operator="U.S. Cybersecurity and Infrastructure Security Agency",
        base_url="https://www.cisa.gov/sites/default/files/feeds",
        docs_url="https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        evidence_class="official_data",
        license_name="U.S. Government work: public domain",
        license_url="https://www.cisa.gov/about/website-policies",
        rate_limit_note="Published as a static JSON feed; no key.",
        topics=["exploited vulnerabilities", "remediation deadlines", "cybersecurity"],
        notes="Authoritative list of vulnerabilities known to be exploited in the wild.",
    )
)

_register(
    _spec(
        source_id="osv",
        name="OSV (Open Source Vulnerabilities) API",
        operator="Google Open Source Security Team, with the OSV community",
        base_url="https://api.osv.dev/v1",
        docs_url="https://google.github.io/osv.dev/api/",
        evidence_class="primary_source",
        license_name="Per-database licences; OSV aggregates upstream advisory databases",
        license_url="https://osv.dev/docs/",
        rate_limit_note="No key required for read queries.",
        topics=["open source vulnerabilities", "package advisories", "supply chain"],
        notes="Aggregates upstream advisory sources (for example the GitHub Advisory Database) and keeps their identifiers.",
    )
)

_register(
    _spec(
        source_id="gbif",
        name="GBIF Occurrence API",
        operator="Global Biodiversity Information Facility (intergovernmental)",
        base_url="https://api.gbif.org/v1",
        docs_url="https://techdocs.gbif.org/en/openapi/",
        evidence_class="official_data",
        license_name="Per-dataset licences, typically CC BY or CC0",
        license_url="https://www.gbif.org/terms",
        rate_limit_note="No key required; GBIF publishes usage guidance for automated clients.",
        topics=["biodiversity", "species distribution", "ecology", "taxonomy"],
        notes="Aggregator of museum and survey records; each record names its publishing institution.",
    )
)

_register(
    _spec(
        source_id="uniprot",
        name="UniProt REST API",
        operator="UniProt Consortium (EMBL-EBI, Swiss Institute of Bioinformatics, PDB)",
        base_url="https://rest.uniprot.org",
        docs_url="https://www.uniprot.org/help/api",
        evidence_class="primary_source",
        license_name="CC BY 4.0",
        license_url="https://www.uniprot.org/help/license",
        rate_limit_note="No key required; the consortium asks that heavy clients throttle.",
        topics=["protein sequences", "protein function", "molecular biology"],
        notes="The reference protein sequence database, curated by hand at reviewed-entry level.",
    )
)

_register(
    _spec(
        source_id="rcsb_pdb",
        name="RCSB Protein Data Bank Data API",
        operator="RCSB PDB (Rutgers/UCSD/UCSF) for the wwPDB consortium",
        base_url="https://data.rcsb.org/rest/v1",
        docs_url="https://data.rcsb.org/redoc/index.html",
        evidence_class="primary_source",
        license_name="PDB data are available under CC0",
        license_url="https://www.rcsb.org/pages/policies",
        rate_limit_note="No key required.",
        topics=["protein structure", "structural biology", "crystallography"],
        notes="The single worldwide archive of experimentally determined macromolecular structures.",
    )
)

_register(
    _spec(
        source_id="pubchem",
        name="PubChem PUG-REST",
        operator="U.S. National Library of Medicine, NCBI",
        base_url="https://pubchem.ncbi.nlm.nih.gov/rest/pug",
        docs_url="https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest",
        evidence_class="primary_source",
        license_name="U.S. Government work; some depositor records carry their own terms",
        license_url="https://pubchem.ncbi.nlm.nih.gov/docs/programmatic-access",
        rate_limit_note="No key required; NCBI asks that clients stay under 5 requests/second.",
        topics=["chemical compounds", "bioassays", "substance properties"],
        notes="The NIH chemical information repository, with per-record depositor attribution.",
    )
)

_register(
    _spec(
        source_id="patentsview",
        name="PatentsView API",
        operator="U.S. Patent and Trademark Office (data platform)",
        base_url="https://search.patentsview.org/api/v1",
        docs_url="https://developer.uspto.gov/api-catalog/patentsview",
        evidence_class="official_data",
        requires_key=True,
        key_env="PATENTSVIEW_API_KEY",
        key_url="https://patentsview.org/apis/keyrequest",
        license_name="U.S. Government work: public domain",
        license_url="https://patentsview.org/about",
        rate_limit_note="Free API key required; documented per-key limits apply.",
        topics=["patents", "inventors", "technology trends", "assignees"],
        notes="USPTO patent data, useful for measuring whether a technology area is accelerating. Review flag: PatentsView was folded into the USPTO Open Data Portal, so this endpoint may be superseded; see docs/SOURCES.md for the flagged migration.",
    )
)

# === Reference and cultural ================================================
_register(
    _spec(
        source_id="wikimedia",
        name="Wikimedia REST API (Wikipedia)",
        operator="Wikimedia Foundation",
        base_url="https://api.wikimedia.org/core/v1",
        docs_url="https://api.wikimedia.org/wiki/Main_Page",
        evidence_class="reputable_secondary",
        license_name="CC BY-SA 4.0 for text; CC0 for some metadata",
        license_url="https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use",
        rate_limit_note="No key; a descriptive User-Agent is required by Wikimedia policy.",
        topics=["definitions", "background", "orientation on an unfamiliar field"],
        notes="Secondary compilation. Used only to orient and to surface citation trails, never as grounds for a factual claim.",
    )
)

_register(
    _spec(
        source_id="openlibrary",
        name="Open Library API",
        operator="Internet Archive (non-profit)",
        base_url="https://openlibrary.org",
        docs_url="https://openlibrary.org/developers/api",
        evidence_class="reputable_secondary",
        license_name="Data is openly available; page images may differ",
        license_url="https://openlibrary.org/developers/api",
        rate_limit_note="No key; the Internet Archive asks heavier clients to identify themselves.",
        topics=["books", "bibliographic records", "reading lists"],
        notes="Bibliographic records only. Presence of a book is not evidence of its contents.",
    )
)

_register(
    _spec(
        source_id="hackernews",
        name="Hacker News API (via Algolia index)",
        operator="Y Combinator (Hacker News); Algolia operates the search index",
        base_url="https://hn.algolia.com/api/v1",
        docs_url="https://hn.algolia.com/api",
        evidence_class="commentary",
        license_name="User-generated content; Algolia index terms apply",
        license_url="https://hn.algolia.com/api",
        rate_limit_note="No key published; the service asks clients to be reasonable.",
        topics=["technology trends", "practitioner discussion", "attention signals"],
        notes="Used ONLY as an attention/trend signal. Forum commentary is never grounds for a factual claim.",
    )
)

_register(
    _spec(
        source_id="stackexchange",
        name="Stack Exchange API",
        operator="Stack Exchange Inc.",
        base_url="https://api.stackexchange.com/2.3",
        docs_url="https://api.stackexchange.com/docs",
        evidence_class="commentary",
        license_name="Post content is CC BY-SA per Stack Exchange terms",
        license_url="https://stackoverflow.com/legal/terms-of-service/public",
        rate_limit_note="300 requests/day without a key; a free key raises this to 10,000/day.",
        key_env="STACKEXCHANGE_KEY",
        key_url="https://stackapps.com/apps/oauth/register",
        topics=["practitioner problems", "implementation pitfalls", "tooling"],
        notes="Attention and difficulty signal only. Never used as grounds for a factual claim.",
    )
)

_register(
    _spec(
        source_id="github",
        name="GitHub REST API",
        operator="GitHub, Inc. (Microsoft)",
        base_url="https://api.github.com",
        docs_url="https://docs.github.com/en/rest",
        evidence_class="primary_source",
        key_env="GITHUB_TOKEN",
        key_url="https://github.com/settings/tokens",
        license_name="Repository content carries each repository's own licence",
        license_url="https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api",
        rate_limit_note="60 requests/hour unauthenticated; 5,000 requests/hour with a token.",
        topics=["open source activity", "software releases", "adoption signals", "reference implementations"],
        notes="Repository metadata is the maintainers' own artefact. Repository activity is an adoption signal, not proof of correctness.",
    )
)


def get_source(source_id: str) -> SourceSpec:
    if source_id not in REGISTRY:
        raise KeyError(f"unknown source: {source_id}")
    return REGISTRY[source_id]


def source_matrix() -> list[dict[str, Any]]:
    """The full registry as plain dicts, sorted for stable publishing."""
    return [REGISTRY[key].to_dict() for key in sorted(REGISTRY)]


def registry_summary() -> dict[str, Any]:
    by_class: dict[str, int] = {}
    for spec in REGISTRY.values():
        by_class[spec.evidence_class] = by_class.get(spec.evidence_class, 0) + 1
    keyed = [s.source_id for s in REGISTRY.values() if s.requires_key]
    return {
        "total": len(REGISTRY),
        "by_evidence_class": dict(sorted(by_class.items())),
        "credential_required": sorted(keyed),
        "open_no_key": sorted(s.source_id for s in REGISTRY.values() if not s.requires_key),
    }


def load_source_matrix(path: Path | None = None) -> list[dict[str, Any]]:
    """Load a previously published source matrix, falling back to the registry."""
    target = path or (SEED_DIR / "sources.json")
    if target.exists():
        with target.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list) and payload:
            return payload
    return source_matrix()
