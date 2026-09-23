"""Per-source request builders and response parsers.

Two kinds of adapter exist, deliberately:

* **Mapped adapters** (:data:`MAPPED`) declare a request and a field map. They
  cover the majority of JSON APIs and keep the code small enough to audit.
* **Custom adapters** (:class:`ArxivSource`, :class:`PubMedSource`,
  :class:`EurostatSource`, the JSON-stat and generic fallbacks) handle response
  shapes that need real logic: Atom XML, plain-text abstracts, JSON-stat cubes.

The universal safety net is :class:`GenericSource`: if a response cannot be
parsed into items by the mapped adapter, the *raw* response is still recorded as
evidence, rendered as a flat ``path = value`` text so that a reviewer can see
exactly what the API returned. Nothing is invented, and nothing is dropped
silently.
"""

from __future__ import annotations

import csv
import html
import io
import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, replace
from typing import Any, Iterable

from ..util import sha256_text, split_sentences
from .net import HttpResult, RequestLogEntry  # noqa: F401  (re-export for typing)
from .registry import REGISTRY, SourceSpec, get_source

MAX_ITEM_TEXT = 6000
MAX_ITEMS_PER_REQUEST = 10
MAX_FLATTEN_LINES = 220


# ---------------------------------------------------------------------------
# Request / item containers
# ---------------------------------------------------------------------------


@dataclass
class Request:
    url: str
    params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    method: str = "GET"
    json_body: dict[str, Any] | None = None
    label: str = ""


@dataclass
class ParsedItem:
    """One candidate evidence document produced by an adapter."""

    identifier: str
    title: str
    url: str
    text: str
    published_at: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")


def strip_markup(value: str) -> str:
    """Remove HTML/JATS markup and unescape entities.

    APIs frequently return abstracts as JATS XML or HTML fragments. The engine
    needs plain text so that a claim can quote the source verbatim.
    """
    if not value:
        return ""
    text = re.sub(r"(?i)</(p|sec|abstract|title|jats:p)>", " ", value)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def dig(obj: Any, path: str, default: Any = None) -> Any:
    """Fetch ``a.b.0.c`` out of nested dict/lists; ``default`` when absent."""
    if not path:
        return default
    current = obj
    for part in path.split("."):
        if current is None:
            return default
        if isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return default
            if index >= len(current) or index < -len(current):
                return default
            current = current[index]
        else:
            return default
    return default if current is None else current


def as_text(value: Any) -> str:
    """Coerce any JSON scalar/list into plain text without inventing content."""
    if value is None:
        return ""
    if isinstance(value, str):
        return strip_markup(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return f"{value}"
    if isinstance(value, list):
        return "; ".join(filter(None, (as_text(v) for v in value)))
    if isinstance(value, dict):
        return "; ".join(f"{k}: {as_text(v)}" for k, v in value.items() if as_text(v))
    return str(value)


def flatten_json(obj: Any, *, prefix: str = "", out: list[str] | None = None, limit: int = MAX_FLATTEN_LINES) -> list[str]:
    """Render arbitrary JSON as ``path = value`` lines (bounded).

    Used by the generic fallback so that even an unanticipated response shape
    produces reviewable, quotable text.
    """
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(obj, dict):
        for key in sorted(obj):
            flatten_json(obj[key], prefix=f"{prefix}.{key}" if prefix else str(key), out=out, limit=limit)
            if len(out) >= limit:
                break
    elif isinstance(obj, list):
        for index, value in enumerate(obj[:25]):
            flatten_json(value, prefix=f"{prefix}.{index}", out=out, limit=limit)
            if len(out) >= limit:
                break
    else:
        rendered = as_text(obj)
        if rendered:
            out.append(f"{prefix} = {rendered}")
    return out


def raw_identifier(source_id: str, text: str) -> str:
    """Stable id for a response the engine stores verbatim.

    Deliberately a content hash and not ``hash()``: Python salts string hashing
    per process, so an id built from ``hash()`` changes on every run and the same
    document would be stored again under a new evidence id each cycle.
    """
    return f"{source_id}-raw-{sha256_text(text)[:16]}"


def json_to_evidence_text(payload: Any, *, header: str) -> str:
    lines = flatten_json(payload)
    body = "\n".join(lines) if lines else json.dumps(payload)[:MAX_ITEM_TEXT]
    return f"{header}\n{body}"[:MAX_ITEM_TEXT]


# ---------------------------------------------------------------------------
# Field maps: source_id -> request template + item mapping
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CredentialMechanism:
    """How one source's operator says its credential is transmitted.

    Every row here is transcribed from the operator's own documentation. The page
    it was read from and the operator's own words are kept beside the mechanism,
    because a transcription a reviewer cannot check is exactly the kind of
    statement this project refuses to publish.

    ``verified_at`` is the date the quote was read from ``docs_url``; an empty
    value means the row records what an existing adapter already does and was not
    re-read against the operator's page during that check.
    """

    kind: str  # "query" (a URL parameter) or "header" (an HTTP header)
    name: str  # the parameter or header name the operator documents
    prefix: str = ""  # value prefix, e.g. "Bearer " for an Authorization header
    docs_url: str = ""
    quote: str = ""
    verified_at: str = ""
    applied_by: str = "shared"  # "shared", or the adapter class that applies it itself


#: Documented credential mechanisms for the registered sources that name a
#: ``key_env``. Sources absent from this table are declared as taking a
#: credential but have no transcription of how, and are reported as such rather
#: than being guessed at: see :func:`credential_status`.
CREDENTIAL_MECHANISMS: dict[str, CredentialMechanism] = {
    "eia": CredentialMechanism(
        kind="query",
        name="api_key",
        docs_url="https://www.eia.gov/opendata/documentation.php",
        quote=(
            "To use an API key, place it as a parameter after the route. "
            "https://api.eia.gov/API_route?api_key=xxxxxxx"
        ),
        verified_at="2026-09-22",
    ),
    "fred": CredentialMechanism(
        kind="query",
        name="api_key",
        docs_url="https://fred.stlouisfed.org/docs/api/fred/series_search.html",
        quote=(
            "https://api.stlouisfed.org/fred/series/search?search_text=monetary+service+index"
            "&api_key=abcdefghijklmnopqrstuvwxyz123456"
        ),
        verified_at="2026-09-22",
    ),
    "ncei": CredentialMechanism(
        kind="header",
        name="token",
        docs_url="https://www.ncei.noaa.gov/cdo-web/webservices/v2",
        quote=(
            'header | token | curl -H "token:<token>" "url" | The token obtained from the token request page. '
            "Assigned token is required to use these queries and must be in the header."
        ),
        verified_at="2026-09-22",
    ),
    "github": CredentialMechanism(
        kind="header",
        name="Authorization",
        prefix="Bearer ",
        docs_url="https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api",
        quote=(
            'curl --request GET --url "https://api.github.com/octocat" '
            '--header "Authorization: Bearer YOUR-TOKEN"'
        ),
        verified_at="2026-09-22",
    ),
    "nasa_api": CredentialMechanism(
        kind="query",
        name="api_key",
        docs_url="https://api.nasa.gov/",
        applied_by="NasaSource",
    ),
    "patentsview": CredentialMechanism(
        kind="header",
        name="X-API-KEY",
        docs_url="https://data.uspto.gov/apis/getting-started",
        applied_by="UsptoOdpSource",
    ),
    "pubmed": CredentialMechanism(
        kind="query",
        name="api_key",
        docs_url="https://www.ncbi.nlm.nih.gov/books/NBK25497/",
        quote=(
            "After creating the key, users should include it in each E-utility request "
            "by assigning it to the api_key parameter."
        ),
        verified_at="2026-09-22",
    ),
    "census_us": CredentialMechanism(
        kind="query",
        name="key",
        docs_url="https://www.census.gov/data/developers/guidance/api-user-guide.API_Key.html",
        quote=(
            "Once you have a key, insert &key= followed by your key code at the end of your "
            "API data calls: &key=your key here"
        ),
        verified_at="2026-09-22",
    ),
    "nvd": CredentialMechanism(
        kind="header",
        name="apiKey",
        docs_url="https://nvd.nist.gov/developers/api-workflows",
        quote=(
            "API keys are passed in the request header using apiKey:{key value}. "
            "Please note, the {key value} is case sensitive"
        ),
        verified_at="2026-09-22",
    ),
    "semantic_scholar": CredentialMechanism(
        kind="header",
        name="x-api-key",
        docs_url="https://api.semanticscholar.org/api-docs/",
        quote=(
            "If you are using an API key, it must be set in the header x-api-key "
            "(case-sensitive)."
        ),
        verified_at="2026-09-22",
    ),
    "stackexchange": CredentialMechanism(
        kind="header",
        name="Authorization",
        prefix="Bearer ",
        docs_url="https://api.stackexchange.com/docs/authentication",
        quote=(
            "All API requests must pass authentication details using request headers. "
            "Your application's API key or access token must be provided using the "
            "authorization header Authorization: Bearer {API key or access token}."
        ),
        verified_at="2026-09-22",
    ),
    "doaj": CredentialMechanism(
        kind="query",
        name="api_key",
        docs_url="https://doaj.org/api/v4/swagger.json",
        quote=(
            'OpenAPI parameter {"in": "query", "name": "api_key", "required": true} '
            "with the description: \"Go to 'DASHBOARD' and 'Settings' to find your API key. "
            "If there is no key, click 'Generate a new API key'.\""
        ),
        verified_at="2026-09-22",
    ),
}


def credential_status(spec: SourceSpec) -> dict[str, str]:
    """What the engine actually does with a source's credential, stated plainly.

    ``requires_key`` says the engine will not call the source without one. It does
    not say the credential reaches the request: that depends on a mechanism being
    transcribed above. Reporting the two separately is what keeps "the key is set"
    from being mistaken for "the key is used".
    """
    mechanism = CREDENTIAL_MECHANISMS.get(spec.source_id)
    if not spec.key_env:
        return {"state": "none", "detail": "This source takes no credential."}
    if mechanism is None:
        return {
            "state": "declared_only",
            "detail": (
                f"{spec.key_env} is named in the register, but the operator's documented way of "
                "transmitting it has not been transcribed, so the engine sends no credential and the "
                "source is used within its unauthenticated limits."
            ),
        }
    where = "the shared request layer" if mechanism.applied_by == "shared" else mechanism.applied_by
    if mechanism.kind == "header":
        shape = f"{mechanism.name}: {mechanism.prefix}<value>"
    else:
        shape = f"?{mechanism.name}=<value>"
    checked = (
        " Transcription checked against the operator's page on " + mechanism.verified_at + "."
        if mechanism.verified_at
        else ""
    )
    return {
        "state": "applied",
        "detail": f"{spec.key_env} is sent as {shape} by {where}.{checked}",
    }


@dataclass
class MappedAdapter:
    """Declarative adapter description for a JSON endpoint."""

    endpoint: str
    items_path: str
    param_name: str = "query"
    param_template: str = "{query}"
    extra_params: dict[str, Any] = field(default_factory=dict)
    mapping: dict[str, str] = field(default_factory=dict)
    limit_param: str | None = "limit"
    limit_value: int = MAX_ITEMS_PER_REQUEST
    headers: dict[str, str] = field(default_factory=dict)
    method: str = "GET"
    published_key: str = "published_at"
    identifier_keys: tuple[str, ...] = ("id", "doi", "url")
    # Name of the prose field in this source's response ("abstract" for scholarly
    # records, "description" for repository records). Used verbatim in the rendered
    # sentence so a reader knows what kind of statement they are looking at.
    prose_label: str = "abstract"
    # Field labels that would be misleading if rendered generically.
    label_overrides: dict[str, str] = field(default_factory=dict)


MAPPED: dict[str, MappedAdapter] = {
    "crossref": MappedAdapter(
        endpoint="/works",
        items_path="message.items",
        param_name="query",
        extra_params={"rows": MAX_ITEMS_PER_REQUEST, "select": "DOI,title,abstract,URL,issued,container-title,author,type,publisher,license,is-referenced-by-count,subject"},
        limit_param=None,
        mapping={
            "title": "title.0",
            "abstract": "abstract",
            "url": "URL",
            "doi": "DOI",
            "date": "issued.date-parts.0.0",
            "venue": "container-title.0",
            "type": "type",
            "publisher": "publisher",
    "organisation": "sourceOrganization",
            "citations": "is-referenced-by-count",
            "subject": "subject",
            "authors": "author",
        },
    ),
    "openalex": MappedAdapter(
        endpoint="/works",
        items_path="results",
        param_name="search",
        extra_params={
            "per-page": MAX_ITEMS_PER_REQUEST,
            "select": "id,doi,title,display_name,publication_year,cited_by_count,abstract_inverted_index,primary_location,type,open_access",
        },
        limit_param=None,
        mapping={
            "title": "display_name",
            "url": "primary_location.landing_page_url",
            "doi": "doi",
            "date": "publication_year",
            "citations": "cited_by_count",
            "type": "type",
            "venue": "primary_location.source.display_name",
        },
    ),
    "datacite": MappedAdapter(
        endpoint="/dois",
        items_path="data",
        param_name="query",
        extra_params={"page[size]": MAX_ITEMS_PER_REQUEST},
        limit_param=None,
        mapping={
            "title": "attributes.titles.0.title",
            "abstract": "attributes.descriptions.0.description",
            "doi": "attributes.doi",
            "url": "attributes.url",
            "date": "attributes.published",
            "publisher": "attributes.publisher",
            "type": "attributes.types.resourceTypeGeneral",
            "license": "attributes.rightsList.0.rightsUri",
        },
    ),
    "zenodo": MappedAdapter(
        endpoint="/records",
        items_path="hits.hits",
        param_name="q",
        extra_params={"size": MAX_ITEMS_PER_REQUEST},
        limit_param=None,
        mapping={
            "title": "metadata.title",
            "abstract": "metadata.description",
            "doi": "doi",
            "url": "links.self_html",
            "date": "metadata.publication_date",
            "type": "metadata.resource_type.type",
        },
    ),
    "doaj": MappedAdapter(
        endpoint="/v3/search/articles",
        items_path="results",
        param_name="query",
        extra_params={"pageSize": MAX_ITEMS_PER_REQUEST},
        limit_param=None,
        mapping={
            "title": "bibjson.title",
            "abstract": "bibjson.abstract",
            "date": "bibjson.year",
            "venue": "bibjson.journal.title",
            "identifier": "bibjson.identifier",
            "url": "bibjson.link",
        },
    ),
    "semantic_scholar": MappedAdapter(
        endpoint="/paper/search",
        items_path="data",
        param_name="query",
        extra_params={"limit": MAX_ITEMS_PER_REQUEST, "fields": "title,abstract,year,url,externalIds,citationCount,venue,publicationTypes"},
        limit_param=None,
        mapping={
            "title": "title",
            "abstract": "abstract",
            "url": "url",
            "date": "year",
            "citations": "citationCount",
            "venue": "venue",
            "identifiers": "externalIds",
        },
    ),
    "clinicaltrials": MappedAdapter(
        endpoint="/studies",
        items_path="studies",
        param_name="query.term",
        extra_params={"pageSize": MAX_ITEMS_PER_REQUEST},
        limit_param=None,
        mapping={
            "title": "protocolSection.identificationModule.briefTitle",
            "abstract": "protocolSection.descriptionModule.briefSummary",
            "identifier": "protocolSection.identificationModule.nctId",
            "url": "protocolSection.identificationModule.nctId",
            "status": "protocolSection.statusModule.overallStatus",
            "enrollment": "protocolSection.designModule.enrollmentInfo.count",
            "conditions": "protocolSection.conditionsModule.conditions",
            "interventions": "protocolSection.armsInterventionsModule.interventions",
        },
    ),
    "usgs_earthquake": MappedAdapter(
        endpoint="/query",
        items_path="features",
        param_name="q",
        extra_params={"format": "geojson", "limit": MAX_ITEMS_PER_REQUEST, "orderby": "time"},
        limit_param=None,
        mapping={
            "title": "properties.title",
            "url": "properties.url",
            "date": "properties.time",
            "magnitude": "properties.mag",
            "place": "properties.place",
            "status": "properties.status",
            "tsunami": "properties.tsunami",
            "detail": "properties.detail",
        },
    ),
    "hackernews": MappedAdapter(
        prose_label="story title",
        label_overrides={"date": "created_at"},
        endpoint="/search",
        items_path="hits",
        param_name="query",
        extra_params={"hitsPerPage": MAX_ITEMS_PER_REQUEST, "tags": "story"},
        limit_param=None,
        mapping={
            "title": "title",
            "url": "url",
            "date": "created_at",
            "points": "points",
            "comments": "num_comments",
            "objectID": "objectID",
        },
    ),
    "github": MappedAdapter(
        prose_label="description",
        label_overrides={"date": "pushed_at", "open_issues": "open_issues_count", "stars": "stargazers_count", "forks": "forks_count"},
        endpoint="/search/repositories",
        items_path="items",
        param_name="q",
        param_template="{query} in:name,description",
        extra_params={"per_page": MAX_ITEMS_PER_REQUEST, "sort": "stars", "order": "desc"},
        limit_param=None,
        mapping={
            "title": "full_name",
            "abstract": "description",
            "url": "html_url",
            "date": "pushed_at",
            "stars": "stargazers_count",
            "forks": "forks_count",
            "language": "language",
            "license": "license.spdx_id",
            "topics": "topics",
            "open_issues": "open_issues_count",
        },
    ),
    "gbif": MappedAdapter(
        endpoint="/occurrence/search",
        items_path="results",
        param_name="q",
        extra_params={"limit": MAX_ITEMS_PER_REQUEST},
        limit_param=None,
        mapping={
            "title": "scientificName",
            "url": "references",
            "date": "eventDate",
            "country": "country",
            "basis": "basisOfRecord",
            "dataset": "datasetTitle",
            "publisher": "publishingOrgKey",
        },
    ),
    "uniprot": MappedAdapter(
        endpoint="/uniprotkb/search",
        items_path="results",
        param_name="query",
        extra_params={"size": MAX_ITEMS_PER_REQUEST, "format": "json"},
        limit_param=None,
        mapping={
            "title": "proteinDescription.recommendedName.fullName.value",
            "identifier": "primaryAccession",
            "url": "primaryAccession",
            "organism": "organism.scientificName",
            "sequence_length": "sequence.length",
            "reviewed": "entryType",
            "genes": "genes",
        },
    ),
    "pubchem": MappedAdapter(
        endpoint="/compound/name/{query}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON",
        items_path="PropertyTable.Properties",
        param_name="",
        mapping={
            "identifier": "CID",
            "title": "IUPACName",
            "url": "CID",
            "formula": "MolecularFormula",
            "weight": "MolecularWeight",
            "smiles": "CanonicalSMILES",
        },
    ),
    "npm": MappedAdapter(
        prose_label="description",
        label_overrides={
            "date": "date",
            "version": "version",
            "keywords": "keywords",
            "publisher": "publisher.username",
            "maintainers": "maintainers",
            "repository": "links.repository",
            "quality": "score.detail.quality",
            "popularity": "score.detail.popularity",
            "maintenance": "score.detail.maintenance",
            "search_score": "searchScore",
        },
        endpoint="/-/v1/search",
        items_path="objects",
        param_name="text",
        # `size` is the documented result-count parameter: "how many results should
        # be returned (default 20, max 250)" - REGISTRY-API.md, read 2026-09-22.
        extra_params={"size": MAX_ITEMS_PER_REQUEST},
        limit_param=None,
        mapping={
            "title": "package.name",
            "abstract": "package.description",
            "url": "package.links.npm",
            "date": "package.date",
            "version": "package.version",
            "keywords": "package.keywords",
            "publisher": "package.publisher.username",
            "maintainers": "package.maintainers",
            "repository": "package.links.repository",
            "quality": "score.detail.quality",
            "popularity": "score.detail.popularity",
            "maintenance": "score.detail.maintenance",
            "search_score": "searchScore",
        },
    ),
    "eurostat": MappedAdapter(endpoint="", items_path="__custom__", param_name="", mapping={}),
}


# ---------------------------------------------------------------------------
# Source adapters
# ---------------------------------------------------------------------------


class Source:
    """Base adapter. Subclasses override :meth:`requests` and :meth:`parse`."""

    def __init__(self, spec: SourceSpec) -> None:
        self.spec = spec

    # -- capability ------------------------------------------------------
    @property
    def source_id(self) -> str:
        return self.spec.source_id

    def missing_credential(self) -> str | None:
        """Name of the missing environment variable, if a key is required."""
        if not self.spec.requires_key:
            return None
        env_name = self.spec.key_env or ""
        if env_name and not os.environ.get(env_name):
            return env_name
        return None

    def credential(self) -> str:
        """The configured credential for this source, or an empty string."""
        env_name = self.spec.key_env or ""
        return os.environ.get(env_name, "").strip() if env_name else ""

    def apply_credential(self, request: Request) -> Request:
        """Return ``request`` carrying the credential the operator documents.

        Nothing is guessed: the mechanism comes from :data:`CREDENTIAL_MECHANISMS`,
        which records the operator's own page and words for each row. A source
        whose mechanism has not been transcribed is sent unauthenticated, and
        :func:`credential_status` publishes that fact, so a configured key is
        never silently assumed to have been used.
        """
        mechanism = CREDENTIAL_MECHANISMS.get(self.source_id)
        value = self.credential()
        if mechanism is None or not value or mechanism.applied_by != "shared":
            return request
        if mechanism.kind == "header":
            headers = dict(request.headers)
            headers[mechanism.name] = mechanism.prefix + value
            return replace(request, headers=headers)
        params = dict(request.params)
        params[mechanism.name] = mechanism.prefix + value
        return replace(request, params=params)

    # -- to implement ----------------------------------------------------
    def unusable_query_reason(self, query: str) -> str | None:
        """Why this adapter cannot use ``query`` at all, or ``None`` if it can.

        An operator may document a constraint on the query itself rather than on
        the response. Refusing to build a request that the operator has said it
        will not answer is cheaper than sending it, and the reason is published as
        a source status instead of the request failing silently.
        """
        return None

    def requests(self, query: str) -> list[Request]:  # pragma: no cover - interface
        raise NotImplementedError

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:  # pragma: no cover
        raise NotImplementedError

    # -- shared helpers --------------------------------------------------
    def base_url(self) -> str:
        return self.spec.base_url.rstrip("/")

    def _limit(self, request: Request) -> int:
        for key in ("limit", "rows", "per-page", "size", "pageSize", "hitsPerPage", "per_page"):
            value = request.params.get(key)
            if isinstance(value, int):
                return value
        return MAX_ITEMS_PER_REQUEST


class GenericSource(Source):
    """Fallback adapter: request a documented search endpoint, keep the raw body.

    Used for sources where the response schema is not declared as a field map.
    The retrieved bytes are rendered as flat ``path = value`` text so a reviewer
    can inspect exactly what the API returned. No interpretation happens here.
    """

    def __init__(self, spec: SourceSpec, path: str, param_name: str, extra_params: dict[str, Any] | None = None) -> None:
        super().__init__(spec)
        self.path = path
        self.param_name = param_name
        self.extra_params = extra_params or {}

    def requests(self, query: str) -> list[Request]:
        params: dict[str, Any] = dict(self.extra_params)
        if self.param_name:
            params[self.param_name] = query.strip()
        request = Request(url=self.base_url() + self.path, params=params, label=f"{self.source_id}:list")
        return [self.apply_credential(request)]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        try:
            payload = result.json()
        except json.JSONDecodeError:
            text = result.text[:MAX_ITEM_TEXT]
            return [
                ParsedItem(
                    identifier=raw_identifier(self.source_id, text),
                    title=f"{self.spec.name} response",
                    url=request.url,
                    text=f"{self.spec.name} raw response for {request.url}\n{text}",
                    extra={"raw": True},
                )
            ]
        body = json_to_evidence_text(payload, header=f"{self.spec.name} response for {request.url}")
        return [
            ParsedItem(
                identifier=raw_identifier(self.source_id, body),
                title=f"{self.spec.name} response",
                url=request.url,
                text=body,
                extra={"raw": True},
            )
        ]


class MappedJsonSource(Source):
    """Adapter driven by a :class:`MappedAdapter` field map."""

    def __init__(self, spec: SourceSpec, adapter: MappedAdapter) -> None:
        super().__init__(spec)
        self.adapter = adapter

    def requests(self, query: str) -> list[Request]:
        adapter = self.adapter
        params: dict[str, Any] = dict(adapter.extra_params)
        if adapter.param_name:
            params[adapter.param_name] = adapter.param_template.format(query=query.strip())
        if adapter.limit_param:
            params[adapter.limit_param] = adapter.limit_value
        path = adapter.endpoint.format(query=query.strip())
        request = Request(
            url=self.base_url() + path,
            params=params,
            headers=adapter.headers,
            method=adapter.method,
            label=f"{self.source_id}:list",
        )
        return [self.apply_credential(request)]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        payload = result.json()
        items = dig(payload, self.adapter.items_path, [])
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            items = []
        out: list[ParsedItem] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            mapped = {key: as_text(dig(item, path)) for key, path in self.adapter.mapping.items()}
            mapped = {k: v for k, v in mapped.items() if v}
            # OpenAlex returns abstracts as an inverted index; rebuild them.
            inverted = dig(item, "abstract_inverted_index")
            if inverted:
                mapped["abstract"] = reconstruct_inverted_abstract(inverted)
            title = mapped.get("title") or f"{self.spec.name} record {index + 1}"
            identifier = (
                mapped.get("doi")
                or mapped.get("identifier")
                or mapped.get("objectID")
                or mapped.get("url")
                or f"{self.source_id}-{index}"
            )
            url = _clean_url(mapped.get("url") or mapped.get("doi") or request.url, self.source_id)
            text = self._render(title, mapped)
            out.append(
                ParsedItem(
                    identifier=str(identifier),
                    title=title,
                    url=url,
                    text=text,
                    published_at=_normalise_date(mapped.get("date")),
                    extra={k: v for k, v in mapped.items() if k not in {"title", "abstract", "url"}},
                )
            )
        return out

    def _render(self, title: str, mapped: dict[str, str]) -> str:
        return render_attributed_record(
            title,
            mapped,
            source_name=self.spec.name,
            base_url=self.spec.base_url,
            extra_notes=self.spec.notes,
            prose_label=self.adapter.prose_label,
            label_overrides=self.adapter.label_overrides,
        )

    def _legacy_render(self, title: str, mapped: dict[str, str]) -> str:  # pragma: no cover - retained for reference
        lines = [f"Source: {self.spec.name} ({self.spec.base_url})", f"Title: {title}"]
        label_map = {
            "abstract": "Abstract",
            "venue": "Venue",
            "date": "Date",
            "publisher": "Publisher",
            "type": "Type",
            "doi": "DOI",
            "url": "URL",
            "citations": "Citation count",
            "stars": "Stars",
            "forks": "Forks",
            "open_issues": "Open issues",
            "language": "Primary language",
            "license": "Licence",
            "subject": "Subject",
            "status": "Status",
            "magnitude": "Magnitude",
            "place": "Place",
            "enrollment": "Enrolment",
            "conditions": "Conditions",
            "interventions": "Interventions",
            "organism": "Organism",
            "sequence_length": "Sequence length",
            "formula": "Molecular formula",
            "weight": "Molecular weight",
            "smiles": "Canonical SMILES",
            "points": "Points",
            "comments": "Comments",
            "country": "Country",
            "basis": "Basis of record",
            "dataset": "Dataset",
            "reviewed": "Entry type",
        }
        for key, value in mapped.items():
            if key in {"title", "abstract"}:
                continue
            label = label_map.get(key, key.replace("_", " ").capitalize())
            lines.append(f"{label}: {value}")
        abstract = mapped.get("abstract")
        if abstract:
            lines.append(f"Abstract: {abstract}")
        return "\n".join(lines)[:MAX_ITEM_TEXT]


# Fields whose text is quoted from the record's own author rather than reported
# as a measurement. Marking them separately matters: a description is a claim the
# publisher makes about itself, which is a weaker thing than a measured value, and
# the claim text must say so.
AUTHORED_FIELDS = ("abstract", "description")

FIELD_LABELS = {
    "abstract": "abstract",
    "venue": "venue",
    "date": "date",
    "publisher": "publisher",
    "type": "type",
    "doi": "DOI",
    "url": "URL",
    "citations": "citation count",
    "stars": "stargazers_count",
    "forks": "forks_count",
    "open_issues": "open_issues_count",
    "language": "language",
    "license": "license",
    "subject": "subject",
    "status": "status",
    "magnitude": "magnitude",
    "place": "place",
    "enrollment": "enrolment",
    "conditions": "conditions",
    "interventions": "interventions",
    "organism": "organism",
    "sequence_length": "sequence length",
    "formula": "molecular formula",
    "weight": "molecular weight",
    "smiles": "canonical SMILES",
    "points": "points",
    "comments": "comment count",
    "country": "country",
    "basis": "basis of record",
    "dataset": "dataset",
    "reviewed": "entry type",
    "identifiers": "external identifiers",
    "topics": "topics",
    "identifier": "identifier",
    # Package-registry fields. The label is the response's own field path so a
    # reviewer can find the value in the stored document without a translation
    # table of the engine's invention.
    "version": "version",
    "keywords": "keywords",
    "publisher": "publisher.username",
    "maintainers": "maintainers",
    "repository": "links.repository",
    "quality": "score.detail.quality",
    "popularity": "score.detail.popularity",
    "maintenance": "score.detail.maintenance",
    "search_score": "searchScore",
    "downloads": "downloads",
    "period": "period",
    "period_start": "start",
    "period_end": "end",
    "package": "package",
    "feed": "feed",
    "guid": "guid",
}

FIELDS_PER_SENTENCE = 3


def render_attributed_record(
    title: str,
    mapped: dict[str, str],
    *,
    source_name: str,
    base_url: str,
    extra_notes: str = "",
    prose_label: str = "abstract",
    label_overrides: dict[str, str] | None = None,
) -> str:
    """Render one retrieved record as sentences that each name their subject.

    Why this shape: the grounding stage cuts claims out of this text, and a claim
    that reads as a bare assertion would be published as if the engine had
    established it. Every sentence here therefore begins with the record it
    describes, so a claim lifted out of it reads as
    "The record for <subject> reports <field> <value>" - the attribution travels
    with the claim. Values are copied from the response without modification; only
    the field labels are the adapter's.
    """
    lines = [
        f"Source: {source_name} ({base_url})",
        "Every sentence below names the record it describes. Values are copied from the response without change; "
        "field labels are the adapter's own rendering of the response's field names.",
        f"Record: {title}",
    ]
    reported: list[tuple[str, str]] = []
    authored: list[tuple[str, str]] = []
    overrides = label_overrides or {}
    for key, value in mapped.items():
        if key in {"title", "url"} or not value:
            continue
        # Fall back to the response's own key so a reader can check the raw field
        # name; an anglicised variant ("pushed at") would hide it.
        label = overrides.get(key) or FIELD_LABELS.get(key, key)
        if key in AUTHORED_FIELDS:
            authored.append((prose_label if key == "abstract" else label, value))
        else:
            reported.append((label, value))

    for index in range(0, len(reported), FIELDS_PER_SENTENCE):
        chunk = reported[index : index + FIELDS_PER_SENTENCE]
        pairs = ", ".join(f"{label} {value}" for label, value in chunk)
        lines.append(f"The record for {title} reports: {pairs}.")

    for label, value in authored:
        # Split long prose into sentence-sized quotations, each attributed, so a
        # single claim never has to be truncated mid-sentence.
        for piece in split_sentences(value):
            lines.append(f"The record for {title} states in its own {label}: {piece}")
        if not split_sentences(value):
            lines.append(f"The record for {title} states in its own {label}: {value}")

    if extra_notes:
        lines.append(f"Source note: {extra_notes}")
    return "\n".join(lines)[:MAX_ITEM_TEXT]


class ArxivSource(Source):
    """arXiv Atom API. Preprints - labelled 'primary_source', never 'peer_reviewed'."""

    NAMESPACES = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    def requests(self, query: str) -> list[Request]:
        return [
            Request(
                url=self.base_url() + "/query",
                params={
                    "search_query": f"all:{query.strip()}",
                    "start": 0,
                    "max_results": MAX_ITEMS_PER_REQUEST,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
                label="arxiv:search",
            )
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        try:
            root = ET.fromstring(result.text)
        except ET.ParseError:
            return GenericSource(self.spec, "/query", "search_query").parse(request, result)
        out: list[ParsedItem] = []
        for entry in root.findall("atom:entry", self.NAMESPACES):
            title = _xml_text(entry, "atom:title", self.NAMESPACES)
            abstract = _xml_text(entry, "atom:summary", self.NAMESPACES)
            identifier = _xml_text(entry, "atom:id", self.NAMESPACES)
            published = _xml_text(entry, "atom:published", self.NAMESPACES)
            updated = _xml_text(entry, "atom:updated", self.NAMESPACES)
            authors = [
                (author.findtext("atom:name", "", self.NAMESPACES) or "").strip()
                for author in entry.findall("atom:author", self.NAMESPACES)
            ]
            categories = [c.get("term", "") for c in entry.findall("atom:category", self.NAMESPACES)]
            journal_ref = _xml_text(entry, "arxiv:journal_ref", self.NAMESPACES)
            comment = _xml_text(entry, "arxiv:comment", self.NAMESPACES)
            lines = [
                f"Source: arXiv (Cornell University) preprint record {identifier}",
                f"Title: {title}",
                f"Authors: {', '.join(a for a in authors if a)}",
                f"Submitted: {published}",
                f"Last updated: {updated}",
                f"Subjects: {', '.join(c for c in categories if c)}",
                "Peer review status: preprint, not peer reviewed",
            ]
            if journal_ref:
                lines.append(f"Journal reference: {journal_ref}")
            if comment:
                lines.append(f"Author comment: {comment}")
            lines.append(f"Abstract: {abstract}")
            out.append(
                ParsedItem(
                    identifier=identifier,
                    title=title,
                    url=(identifier or request.url).replace("http://", "https://"),
                    text="\n".join(lines)[:MAX_ITEM_TEXT],
                    published_at=published or None,
                    extra={"authors": authors, "categories": categories, "preprint": True},
                )
            )
        return out


class PubMedSource(Source):
    """NCBI E-utilities: esearch for identifiers, then efetch for the abstract text.

    Both stages go through :meth:`Source.apply_credential`: a two-stage adapter
    that put the key only on the first request would spend the operator's
    documented rate limit on stage one and then fail stage two unauthenticated.
    """

    def requests(self, query: str) -> list[Request]:
        return [
            self.apply_credential(
                Request(
                    url=self.base_url() + "/esearch.fcgi",
                    params={
                        "db": "pubmed",
                        "term": query.strip(),
                        "retmode": "json",
                        "retmax": MAX_ITEMS_PER_REQUEST,
                        "sort": "date",
                    },
                    label="pubmed:esearch",
                )
            )
        ]

    def follow_up(self, result: HttpResult) -> list[Request]:
        """Second-stage requests derived from a response (abstract retrieval)."""
        try:
            payload = result.json()
        except json.JSONDecodeError:
            return []
        ids = dig(payload, "esearchresult.idlist", []) or []
        if not ids:
            return []
        return [
            self.apply_credential(
                Request(
                    url=self.base_url() + "/efetch.fcgi",
                    params={"db": "pubmed", "id": ",".join(ids), "rettype": "abstract", "retmode": "text"},
                    label="pubmed:efetch",
                )
            )
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        if "efetch" in request.url:
            text = result.text.strip()
            if not text:
                return []
            return [
                ParsedItem(
                    identifier=f"pubmed-set-{abs(hash(request.params.get('id', ''))) % 10**8}",
                    title="PubMed abstract set",
                    url=request.url,
                    text=f"Source: PubMed (U.S. National Library of Medicine)\n{text}"[:MAX_ITEM_TEXT],
                    extra={"batch": True},
                )
            ]
        try:
            payload = result.json()
        except json.JSONDecodeError:
            return []
        ids = dig(payload, "esearchresult.idlist", []) or []
        return [
            ParsedItem(
                identifier=nid,
                title=f"PubMed record {nid}",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{nid}/",
                text=f"Source: PubMed (U.S. National Library of Medicine)\nIdentifier: PMID {nid}\nRecord URL: https://pubmed.ncbi.nlm.nih.gov/{nid}/",
                extra={"pmid": nid},
            )
            for nid in ids
        ]


class NasaSource(Source):
    """api.nasa.gov endpoints; DEMO_KEY is supported by the operator."""

    def requests(self, query: str) -> list[Request]:
        return [
            Request(
                url="https://api.nasa.gov/planetary/apod",
                params={"count": min(5, MAX_ITEMS_PER_REQUEST), "api_key": self._key()},
                label="nasa:apod",
            )
        ]

    def _key(self) -> str:
        import os

        return os.environ.get(self.spec.key_env or "NASA_API_KEY", "DEMO_KEY")

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        payload = result.json()
        items = payload if isinstance(payload, list) else [payload]
        out: list[ParsedItem] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", f"NASA APOD {index}"))
            text = (
                f"Source: NASA Open APIs (api.nasa.gov), Astronomy Picture of the Day\n"
                f"Title: {title}\n"
                f"Date: {item.get('date', '')}\n"
                f"Media type: {item.get('media_type', '')}\n"
                f"Explanation: {strip_markup(str(item.get('explanation', '')))}\n"
                f"Copyright: {item.get('copyright', 'public domain / NASA')}"
            )
            out.append(
                ParsedItem(
                    identifier=str(item.get("date", index)),
                    title=title,
                    url=str(item.get("hdurl") or item.get("url") or request.url),
                    text=text[:MAX_ITEM_TEXT],
                    published_at=str(item.get("date", "")) or None,
                )
            )
        return out


class EurostatSource(Source):
    """Eurostat dissemination API returning JSON-stat cubes."""

    DEFAULT_DATASET = "nrg_ind_ren"  # share of renewable energy in gross final energy consumption

    #: A Eurostat dataset code is a short lowercase token with underscores
    #: (``nrg_ind_ren``, ``tipsun20``, ``tec00111``). A research question's query
    #: is prose, and sending prose as the dataset path can only answer 404, so the
    #: query is used only when it already *is* a code. Before this, every query
    #: was interpolated into the path: the source was registered, polled and never
    #: able to answer. Found by asking every adapter to build its requests.
    DATASET_CODE_RE = re.compile(r"^[a-z]{2,5}_[a-z0-9_]+$|^[a-z]{4,10}[0-9]{2,4}$")

    def dataset_for(self, query: str) -> tuple[str, bool]:
        """``(dataset_code, came_from_query)``."""
        candidate = (query or "").strip().casefold()
        if self.DATASET_CODE_RE.match(candidate):
            return candidate, True
        return self.DEFAULT_DATASET, False

    def requests(self, query: str) -> list[Request]:
        dataset, _from_query = self.dataset_for(query)
        return [
            Request(
                url=f"{self.base_url()}/statistics/1.0/data/{dataset}",
                params={"format": "JSON", "lang": "EN"},
                label=f"eurostat:{dataset}" + ("" if _from_query else ":default"),
            )
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        try:
            payload = result.json()
        except json.JSONDecodeError:
            return []
        summary = summarise_jsonstat(payload)
        if not summary:
            return []
        dataset_id = request.url.rsplit("/", 1)[-1]
        return [
            ParsedItem(
                identifier=f"eurostat-{dataset_id}",
                title=f"Eurostat dataset {dataset_id}",
                url=request.url,
                text=f"Source: Eurostat (European Commission)\nDataset: {dataset_id}\n{summary}"[:MAX_ITEM_TEXT],
                extra={"jsonstat": True},
            )
        ]


# ---------------------------------------------------------------------------
# Parsers for specific response shapes
# ---------------------------------------------------------------------------



class UsptoOdpSource(Source):
    """USPTO Open Data Portal (the platform PatentsView migrated to in 2026).

    Two documented endpoints are queried:

    * ``/patent/applications/search`` - Patent File Wrapper search, ``q`` free-form
      query with ``offset``/``limit`` pagination
      (https://data.uspto.gov/documents/documents/ODP-API-Query-Spec.pdf);
    * ``/datasets/products/search`` - Bulk Data Directory search by product title,
      which is where the former PatentsView tables now live
      (https://data.uspto.gov/apis/bulk-data/search).

    Both require the ODP API key in the ``X-API-KEY`` header
    (https://data.uspto.gov/apis/getting-started). The bulk-products response
    shape is modelled field by field because it is published in the
    documentation; any other shape falls back to the verbatim renderer, so a
    response the engine does not understand is still stored exactly as received
    rather than being guessed at.
    """

    KEY_HEADER = "X-API-KEY"

    def _key(self) -> str:
        import os

        return os.environ.get(self.spec.key_env or "", "").strip()

    def requests(self, query: str) -> list[Request]:
        query = query.strip()
        headers = {"accept": "application/json"}
        key = self._key()
        if key:
            headers[self.KEY_HEADER] = key
        return [
            Request(
                url=self.base_url() + "/patent/applications/search",
                params={"q": query, "limit": MAX_ITEMS_PER_REQUEST},
                headers=headers,
                label=f"{self.source_id}:applications",
            ),
            Request(
                url=self.base_url() + "/datasets/products/search",
                params={"productTitle": query},
                headers=headers,
                label=f"{self.source_id}:datasets",
            ),
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        payload = result.json()
        if isinstance(payload, dict) and isinstance(payload.get("bulkDataProductBag"), list):
            return self._parse_bulk_products(request, payload)
        return self._parse_verbatim(request, payload)

    # -- bulk data directory ------------------------------------------------
    def _parse_bulk_products(self, request: Request, payload: dict[str, Any]) -> list[ParsedItem]:
        products: list[dict[str, Any]] = []
        for group in payload.get("bulkDataProductBag") or []:
            if isinstance(group, dict):
                products.append(group)
            elif isinstance(group, list):
                products.extend(item for item in group if isinstance(item, dict))
        out: list[ParsedItem] = []
        for index, product in enumerate(products[:MAX_ITEMS_PER_REQUEST]):
            identifier = as_text(dig(product, "productIdentifier")) or f"{self.source_id}-product-{index}"
            title = as_text(dig(product, "productTitleText")) or f"{self.spec.name} product {index + 1}"
            files = dig(product, "productFileBag.fileDataBag", []) or []
            files = files if isinstance(files, list) else []
            mapped = {
                "description": as_text(dig(product, "productDescriptionText")),
                "frequency": as_text(dig(product, "productFrequencyText")),
                "coverage_from": as_text(dig(product, "productFromDate")),
                "coverage_to": as_text(dig(product, "productToDate")),
                "total_file_size_bytes": as_text(dig(product, "productTotalFileSize")),
                "file_count": as_text(dig(product, "productFileTotalQuantity")),
                "formats": ", ".join(
                    sorted({as_text(mime) for group in (dig(product, "mimeTypeIdentifierArrayText") or [])
                            for mime in (group if isinstance(group, list) else [group]) if as_text(mime)})
                ),
                "last_modified": as_text(dig(product, "lastModifiedDateTime")),
                "files": "; ".join(
                    f"{as_text(dig(f, 'fileName'))} ({as_text(dig(f, 'fileSize'))} bytes, released "
                    f"{as_text(dig(f, 'fileReleaseDate'))})"
                    for f in files[:3]
                    if isinstance(f, dict)
                ),
            }
            mapped = {k: v for k, v in mapped.items() if v}
            download = as_text(dig(files[0], "fileDownloadURI")) if files and isinstance(files[0], dict) else ""
            out.append(
                ParsedItem(
                    identifier=str(identifier),
                    title=title,
                    url=download or request.url,
                    text=render_attributed_record(
                        title,
                        mapped,
                        source_name=self.spec.name,
                        base_url=self.spec.base_url,
                        extra_notes=self.spec.notes,
                        prose_label="description",
                        label_overrides={
                            "coverage_from": "data coverage from",
                            "coverage_to": "data coverage to",
                            "total_file_size_bytes": "total file size in bytes",
                            "file_count": "number of files",
                            "frequency": "release frequency",
                            "formats": "file formats",
                            "last_modified": "last modified",
                            "files": "files",
                        },
                    ),
                    published_at=_normalise_date(as_text(dig(product, "lastModifiedDateTime"))),
                    extra=mapped,
                )
            )
        return out

    # -- anything else ------------------------------------------------------
    def _parse_verbatim(self, request: Request, payload: Any) -> list[ParsedItem]:
        """Store a response the engine has no field map for, exactly as received."""
        body = json_to_evidence_text(payload, header=f"{self.spec.name} response for {request.url}")
        return [
            ParsedItem(
                identifier=raw_identifier(self.source_id, body),
                title=f"{self.spec.name} response",
                url=request.url,
                text=body,
                extra={"raw": True},
            )
        ]



def reconstruct_inverted_abstract(inverted: dict[str, list[int]]) -> str:
    """Rebuild abstract text from OpenAlex's ``abstract_inverted_index``.

    The index maps each token to the positions it occupies. Reconstruction is
    lossless for the tokens the index contains, which is why OpenAlex abstracts
    are usable as quotable evidence.
    """
    positions: dict[int, str] = {}
    for token, indices in inverted.items():
        if not isinstance(indices, list):
            continue
        for index in indices:
            if isinstance(index, int):
                positions[index] = token
    if not positions:
        return ""
    return " ".join(positions[i] for i in sorted(positions))


def summarise_jsonstat(payload: dict[str, Any], *, max_cells: int = 40) -> str:
    """Render the leading cells of a JSON-stat cube as labelled lines.

    JSON-stat encodes a hypercube as ``values`` plus an index of dimension
    categories. This walks the cube deterministically and emits
    ``dimension=category, dimension=category: value`` for the first non-null
    cells, which is enough for a human to see what the dataset says.
    """
    if not isinstance(payload, dict) or "value" not in payload:
        return ""
    values = payload.get("value")
    if not isinstance(values, (list, dict)):
        return ""
    dimension_ids = payload.get("id") or []
    sizes = payload.get("size") or []
    dimensions = payload.get("dimension") or {}
    label = payload.get("label") or ""

    category_labels: dict[str, dict[str, str]] = {}
    for dim_id in dimension_ids:
        category = dig(dimensions, f"{dim_id}.category", {}) or {}
        index = category.get("index", {})
        labels = category.get("label", {})
        if isinstance(index, dict):
            ordered = [k for k, _ in sorted(index.items(), key=lambda kv: kv[1])]
        else:
            ordered = list(index) if isinstance(index, list) else []
        category_labels[dim_id] = {code: labels.get(code, code) for code in ordered}

    lines: list[str] = []
    if label:
        lines.append(f"Dataset label: {label}")
    if payload.get("updated"):
        lines.append(f"Last updated: {payload['updated']}")
    if isinstance(values, dict):
        items = sorted(values.items(), key=lambda kv: str(kv[0]))
    else:
        items = list(enumerate(values))
    emitted = 0
    for flat_index, value in items:
        if value is None:
            continue
        try:
            index = int(flat_index)
        except (TypeError, ValueError):
            continue
        coords: list[str] = []
        remainder = index
        for position, dim_id in enumerate(reversed(dimension_ids)):
            size = sizes[len(sizes) - 1 - position] if position < len(sizes) else 1
            size = max(int(size), 1)
            code = remainder % size
            remainder //= size
            labels_for_dim = category_labels.get(dim_id, {})
            codes = list(labels_for_dim)
            name = labels_for_dim.get(codes[code], codes[code]) if code < len(codes) else str(code)
            coords.append(f"{dim_id}={name}")
        lines.append(f"{', '.join(reversed(coords))}: {value}")
        emitted += 1
        if emitted >= max_cells:
            break
    return "\n".join(lines)


def parse_csv_evidence(text: str, *, header: str, max_rows: int = 40) -> str:
    """Render the leading rows of a CSV response as aligned text."""
    reader = csv.reader(io.StringIO(text))
    rows = []
    for index, row in enumerate(reader):
        if index > max_rows:
            break
        rows.append(row)
    return header + "\n" + "\n".join(" | ".join(cell.strip() for cell in row) for row in rows)


# ---------------------------------------------------------------------------
# Package registries (added 2026-09-22)
# ---------------------------------------------------------------------------


class NpmSearchSource(MappedJsonSource):
    """``GET /-/v1/search`` on the npm registry, with the operator's own constraint.

    The route, its parameters and the response shape are transcribed from
    https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md (read
    2026-09-22), which documents ``text``, ``size`` ("how many results should be
    returned (default 20, max 250)"), ``from``, ``quality``, ``popularity`` and
    ``maintenance`` as query parameters and ``objects[].package`` /
    ``objects[].score`` as the response shape.

    The minimum query length is the operator's, not a guess: npm's rate-limiting
    announcement states "we limit package search requests to queries that are at
    least three characters long"
    (https://blog.npmjs.org/post/164799520460/api-rate-limiting-rolling-out.html,
    read 2026-09-22 - the page carries the operator's own notice that its content
    is deprecated, which is recorded in the register rather than hidden). A query
    below the limit produces no request and a published reason, because sending it
    would spend a request on an answer the operator has said it will not give.
    """

    MIN_SEARCH_CHARS = 3

    def unusable_query_reason(self, query: str) -> str | None:
        text = (query or "").strip()
        if len(text) < self.MIN_SEARCH_CHARS:
            return (
                f"npm limits package search requests to queries of at least "
                f"{self.MIN_SEARCH_CHARS} characters; the query {text!r} is shorter, so no request was made."
            )
        return None


class NpmDownloadsSource(Source):
    """``GET /downloads/point/{period}`` - the registry operator's own download totals.

    Documented at https://github.com/npm/registry/blob/main/docs/download-counts.md
    (read 2026-09-22): "Gets the total downloads for a given period, for all
    packages or a specific package", with the acceptable period values
    ``last-day``, ``last-week``, ``last-month``, ``last-year`` and a specific date
    or ``start:end`` range, and an output of ``{downloads, start, end, package}``
    where "The start and end dates are inclusive" and the ``package`` key "will
    not be present" when no package was requested.

    Only the all-packages form is requested here, because a package name cannot be
    derived from a research question without inventing one. The figures are the
    operator's daily aggregation: the same document says the previous day's logs
    are crunched "once per day, soon after UTC midnight", so a count is always
    about a closed period and the dates travel with it.
    """

    PERIODS: tuple[str, ...] = ("last-day", "last-week", "last-month")

    def requests(self, query: str) -> list[Request]:
        return [
            Request(
                url=self.base_url() + f"/downloads/point/{period}",
                label=f"npm_downloads:{period}",
            )
            for period in self.PERIODS
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        try:
            payload = result.json()
        except json.JSONDecodeError:
            return GenericSource(self.spec, "/downloads/point", "").parse(request, result)
        if not isinstance(payload, dict):
            return []
        period = request.url.rstrip("/").rsplit("/", 1)[-1]
        downloads = payload.get("downloads")
        start = payload.get("start") or ""
        end = payload.get("end") or ""
        package = payload.get("package") or ""
        subject = f"{package} on npm" if package else "all packages on the npm registry"
        title = f"npm download counts for {subject}, period {period}"
        mapped: dict[str, str] = {
            "downloads": as_text(downloads),
            "period": period,
            "period_start": as_text(start),
            "period_end": as_text(end),
        }
        if package:
            mapped["package"] = as_text(package)
        text = render_attributed_record(
            title,
            mapped,
            source_name=self.spec.name,
            base_url=self.spec.base_url,
            extra_notes=self.spec.notes,
            prose_label="description",
        )
        return [
            ParsedItem(
                identifier=f"npm-downloads-{period}-{start}-{end}" + (f"-{package}" if package else ""),
                title=title,
                url=request.url,
                text=text,
                published_at=_normalise_date(end or None),
                extra={"downloads": downloads, "period": period, "start": start, "end": end},
            )
        ]


class PypiFeedSource(Source):
    """PyPI's two documented global RSS feeds.

    Both routes and their descriptions are quoted from
    https://docs.pypi.org/api/feeds/ (read 2026-09-22):

    * Newest Packages Feed, ``https://pypi.org/rss/packages.xml`` - "This feed
      provides the latest newly created projects on PyPI, including the package
      name, description and a link to the project page."
    * Latest Updates Feed, ``https://pypi.org/rss/updates.xml`` - "This feed
      provides the latest newly created releases for individual projects on PyPI,
      including the project name and description, release version, and a link to
      the release page."

    The operator's API policy page directs consumers here for exactly what the
    change scan does: "For periodically checking for new packages or updates to
    existing packages, use our RSS feeds" (https://docs.pypi.org/api/).

    Neither feed takes a query. They are read as published, and the collector's
    relevance rule - not this adapter - decides which items bear on a question,
    reporting how many it dropped. The JSON API documented at
    https://docs.pypi.org/api/json/ is *not* requested: pypi.org/robots.txt
    disallows ``/pypi/*/json`` to every user agent (fetched 2026-09-22), and the
    RFC 9309 gate in :mod:`selflearn.fetch.robots` refuses it.
    """

    FEEDS: tuple[tuple[str, str, str], ...] = (
        ("newest-packages", "/rss/packages.xml", "Newest Packages Feed"),
        ("latest-updates", "/rss/updates.xml", "Latest Updates Feed"),
    )

    def requests(self, query: str) -> list[Request]:
        return [
            Request(url=self.base_url() + path, label=f"pypi:{name}")
            for name, path, _label in self.FEEDS
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        try:
            root = ET.fromstring(result.text)
        except ET.ParseError:
            return GenericSource(self.spec, "/rss", "").parse(request, result)
        label = next(
            (name for name, path, _label in self.FEEDS if request.url.endswith(path)),
            "feed",
        )
        feed_title = (root.findtext("channel/title") or "").strip()
        feed_description = (root.findtext("channel/description") or "").strip()
        out: list[ParsedItem] = []
        for item in root.findall("channel/item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            guid = (item.findtext("guid") or "").strip()
            description = (item.findtext("description") or "").strip()
            author = (item.findtext("author") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            iso_date = _rfc822_to_iso(pub_date)
            mapped: dict[str, str] = {
                "feed": feed_title or label,
                "guid": guid or link,
                "date": iso_date or pub_date,
            }
            if author:
                mapped["publisher"] = author
            text = render_attributed_record(
                title or (guid or request.url),
                {**mapped, "description": description},
                source_name=self.spec.name,
                base_url=self.spec.base_url,
                extra_notes=self.spec.notes,
                prose_label="description",
            )
            if feed_description:
                text = f"Feed description as published by the operator: {feed_description}\n{text}"
            out.append(
                ParsedItem(
                    identifier=guid or link or raw_identifier(self.source_id, title + pub_date),
                    title=title or (guid or request.url),
                    url=link or request.url,
                    text=text[:MAX_ITEM_TEXT],
                    published_at=iso_date,
                    extra={
                        "feed": label,
                        "feed_title": feed_title,
                        "guid": guid,
                        "author": author,
                        "pub_date": pub_date,
                    },
                )
            )
            if len(out) >= MAX_ITEMS_PER_REQUEST:
                break
        return out


class WorldBankSource(Source):
    """World Bank Indicators API, using only the routes the operator documents.

    Quoted from https://datahelpdesk.worldbank.org/knowledgebase/articles/898599-indicator-api-queries
    (read 2026-09-22): "To request all indicators: https://api.worldbank.org/v2/indicator"
    and "To request the indicator GDP (Current US$), use its indicator code,
    NY.GDP.MKTP.CD: https://api.worldbank.org/v2/indicator/NY.GDP.MKTP.CD", with
    ``?format=json`` shown for the JSON form. The same page lists what an
    indicator query returns: "Code, Name, Unit, Source ID, Source Note, Source
    Organization, Topic ID, Topic Name".

    The route this adapter used before asked for
    ``/country/all/indicator/{indicator}`` and interpolated nothing: building a
    request raised ``KeyError: 'indicator'``, so the source was registered and
    could never be polled. Found by asking every registered adapter to build its
    requests for a normal research query. Nothing is invented here: a query that
    is already an indicator code is used as one, and anything else falls back to
    the documented "all indicators" route rather than to a code this engine chose.
    """

    #: A World Bank indicator code is dotted and upper case (``NY.GDP.MKTP.CD``);
    #: the operator's own example is the shape this recognises.
    INDICATOR_CODE_RE = re.compile(r"^[A-Za-z]{1,4}(\.[A-Za-z0-9]{2,}){1,4}$")

    def indicator_for(self, query: str) -> str | None:
        candidate = (query or "").strip()
        return candidate if self.INDICATOR_CODE_RE.match(candidate) else None

    def requests(self, query: str) -> list[Request]:
        indicator = self.indicator_for(query)
        path = f"/indicator/{indicator}" if indicator else "/indicator"
        return [
            Request(
                url=self.base_url() + path,
                params={"format": "json", "per_page": MAX_ITEMS_PER_REQUEST},
                label="worldbank:" + (indicator or "all-indicators"),
            )
        ]

    def parse(self, request: Request, result: HttpResult) -> list[ParsedItem]:
        try:
            payload = result.json()
        except json.JSONDecodeError:
            return GenericSource(self.spec, "/indicator", "").parse(request, result)
        # The documented JSON form is a two-element array: a pagination object and
        # the rows. Both shapes the operator shows are handled, and anything else
        # falls back to the generic renderer so the bytes are still stored.
        rows: Any = payload
        if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[1], list):
            rows = payload[1]
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            return GenericSource(self.spec, "/indicator", "").parse(request, result)
        out: list[ParsedItem] = []
        for row in rows[:MAX_ITEMS_PER_REQUEST]:
            if not isinstance(row, dict):
                continue
            code = as_text(row.get("id") or row.get("code"))
            name = as_text(row.get("name") or row.get("value")) or code
            if not name:
                continue
            source_note = ""
            source_value = row.get("source")
            if isinstance(source_value, dict):
                source_value = source_value.get("value")
            unit = as_text(row.get("unit"))
            note = row.get("sourceNote") or row.get("source_note")
            if isinstance(note, dict):
                note = note.get("value")
            source_note = as_text(note)
            organisation = row.get("sourceOrganization") or row.get("source_organization")
            if isinstance(organisation, dict):
                organisation = organisation.get("value")
            topics = [
                as_text(topic.get("value") if isinstance(topic, dict) else topic)
                for topic in (row.get("topics") or [])
            ]
            mapped = {
                "identifier": code,
                "unit": unit,
                "publisher": as_text(source_value),
                "organisation": as_text(organisation),
                "topics": ", ".join(t for t in topics if t),
            }
            mapped = {key: value for key, value in mapped.items() if value}
            if source_note:
                mapped["abstract"] = source_note
            title = f"{name}" + (f" ({code})" if code and code != name else "")
            out.append(
                ParsedItem(
                    identifier=code or raw_identifier(self.source_id, title),
                    title=title,
                    url=request.url,
                    text=render_attributed_record(
                        title,
                        mapped,
                        source_name=self.spec.name,
                        base_url=self.spec.base_url,
                        extra_notes=self.spec.notes,
                        prose_label="source note",
                    ),
                    published_at=None,
                    extra={"indicator_code": code, "topics": topics},
                )
            )
        return out


def _rfc822_to_iso(value: str | None) -> str | None:
    """Convert an RSS ``pubDate`` to the ISO-8601 date the engine records.

    The feeds publish RFC-822 dates ("Tue, 22 Sep 2026 23:49:52 GMT"). The
    conversion is the standard library's, and only the date part is kept, because
    :func:`_normalise_date` and the verifier compare dates, not clocks.
    """
    if not value:
        return None
    from email.utils import parsedate_to_datetime

    try:
        parsed = parsedate_to_datetime(value.strip())
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    return parsed.strftime("%Y-%m-%d")


def _xml_text(element: ET.Element, path: str, namespaces: dict[str, str]) -> str:
    found = element.findtext(path, "", namespaces)
    return re.sub(r"\s+", " ", (found or "")).strip()


def _clean_url(value: str, source_id: str) -> str:
    """Turn a bare DOI or identifier into a resolvable link."""
    if not value:
        return ""
    if value.startswith("http"):
        return value
    if value.startswith("10."):
        return f"https://doi.org/{value}"
    if source_id == "pubmed" and value.isdigit():
        return f"https://pubmed.ncbi.nlm.nih.gov/{value}/"
    if source_id == "uniprot":
        return f"https://www.uniprot.org/uniprotkb/{value}/entry"
    if source_id == "pubchem":
        return f"https://pubchem.ncbi.nlm.nih.gov/compound/{value}"
    if source_id == "clinicaltrials":
        return f"https://clinicaltrials.gov/study/{value}"
    return value


def _normalise_date(value: str | None) -> str | None:
    """Normalise the many date shapes APIs return into ISO-8601 where possible."""
    if not value:
        return None
    text = str(value).strip()
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match = re.match(r"^(\d{4})-(\d{2})$", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-01"
    match = re.match(r"^(\d{4})$", text)
    if match:
        return f"{match.group(1)}-01-01"
    return text[:32]


# ---------------------------------------------------------------------------
# Adapter factory
# ---------------------------------------------------------------------------

CUSTOM: dict[str, type[Source]] = {
    "arxiv": ArxivSource,
    "pubmed": PubMedSource,
    "nasa_api": NasaSource,
    "eurostat": EurostatSource,
    "patentsview": UsptoOdpSource,
    "worldbank": WorldBankSource,
    "npm": NpmSearchSource,
    "npm_downloads": NpmDownloadsSource,
    "pypi": PypiFeedSource,
}

# Endpoints whose schema the engine does not model as a field map; the raw
# response is preserved and rendered instead.
GENERIC: dict[str, tuple[str, str, dict[str, Any]]] = {
    "sec_edgar": ("/submissions/CIK0000320193.json", "", {}),
    "nvd": ("/cves/2.0", "keywordSearch", {"resultsPerPage": 5}),
    "cisa_kev": ("/known_exploited_vulnerabilities.json", "", {}),
    "osv": ("/vulns", "", {}),
    "rcsb_pdb": ("/core/entry/4HHB", "", {}),
    "wikimedia": ("/page/Main_Page", "", {}),
    "openlibrary": ("/search.json", "q", {"limit": MAX_ITEMS_PER_REQUEST}),
    "stackexchange": ("/search/advanced", "q", {"order": "desc", "sort": "votes", "site": "stackoverflow"}),
    "fred": ("/series/search", "search_text", {"file_type": "json", "limit": 5}),
    "census_us": ("/2023/acs/acs1", "get", {"for": "us:*"}),
    "ncei": ("/datasets", "", {"limit": 5}),
    "eia": ("/electricity/retail-sales/data", "", {"frequency": "monthly", "data[0]": "price"}),
    "imf": ("/dataflow", "", {"format": "jsondata"}),
    "oecd": ("/dataflow", "", {"format": "csv"}),
    "un_sdg": ("/Goal/ListIndicators", "", {}),
    "who_gho": ("/Indicator", "", {}),
}


def build_source(source_id: str) -> Source:
    """Instantiate the adapter for a registered source."""
    spec = get_source(source_id)
    if source_id in CUSTOM:
        klass = CUSTOM[source_id]
        # A mapped adapter described in MAPPED and subclassed in CUSTOM (npm's
        # search adapter, which adds the operator's minimum query length) needs
        # its description; a fully custom adapter takes only the spec.
        if source_id in MAPPED and issubclass(klass, MappedJsonSource):
            return klass(spec, MAPPED[source_id])
        return klass(spec)
    if source_id in MAPPED:
        return MappedJsonSource(spec, MAPPED[source_id])
    if source_id in GENERIC:
        path, param_name, extra = GENERIC[source_id]
        return GenericSource(spec, path, param_name, extra)
    return GenericSource(spec, "", "", {})


def build_all_sources() -> dict[str, Source]:
    return {source_id: build_source(source_id) for source_id in sorted(REGISTRY)}


def source_ids_with_adapters() -> list[str]:
    """Registry entries that have a concrete adapter (mapped, custom or generic)."""
    return sorted(set(CUSTOM) | set(MAPPED) | set(GENERIC))
