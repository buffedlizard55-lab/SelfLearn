"""A small, polite, auditable HTTP client built on the standard library.

Design notes
------------
* Every request is logged with a sha256 of the exact bytes received. That hash
  is what the verification layer checks evidence against, so a later reviewer
  can confirm the site's claims correspond to bytes the engine really saw.
* Per-host rate limiting and a retry policy with exponential backoff keep the
  engine inside the published usage guidance of the APIs it calls.
* A DNS/connection failure raises :class:`NetworkUnavailable` rather than an
  opaque ``URLError`` so the caller can degrade to snapshot replay *and record
  an irregularity*, instead of pretending the fetch worked.
"""

from __future__ import annotations

import json
import logging
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from ..config import BUDGET, DEFAULT_USER_AGENT
from ..util import sha256_bytes, utcnow_iso
from .robots import RobotsDecision, RobotsDisallowed, RobotsGate

LOG = logging.getLogger("selflearn.fetch")


class NetworkUnavailable(RuntimeError):
    """Raised when a host cannot be reached at all (DNS, refused, filtered)."""


class HttpError(RuntimeError):
    """Raised when a host is reachable but returns an error status."""

    def __init__(self, status: int, url: str, body: str = "") -> None:
        super().__init__(f"HTTP {status} for {url}")
        self.status = status
        self.url = url
        self.body = body[:400]


@dataclass
class HttpResult:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
    content_type: str
    retrieved_at: str
    attempts: int
    from_cache: bool = False
    request_count: int = 1

    @property
    def text(self) -> str:
        """Decode the body, preferring UTF-8 and never raising on bad bytes."""
        charset = "utf-8"
        ctype = self.headers.get("content-type", "")
        if "charset=" in ctype:
            charset = ctype.split("charset=", 1)[1].split(";", 1)[0].strip().strip('"') or "utf-8"
        try:
            return self.body.decode(charset, errors="replace")
        except LookupError:
            return self.body.decode("utf-8", errors="replace")

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.body)

    def json(self) -> Any:
        return json.loads(self.text)


@dataclass
class RequestLogEntry:
    url: str
    status: int | None
    bytes_read: int
    sha256: str
    retrieved_at: str
    attempts: int
    seconds: float
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class HttpClient:
    """Rate-limited HTTP client with retries and an in-memory request log."""

    user_agent: str = DEFAULT_USER_AGENT
    timeout: int = BUDGET.request_timeout
    max_retries: int = BUDGET.max_retries
    min_interval: float = BUDGET.min_seconds_between_requests
    max_requests: int = BUDGET.max_http_requests
    allow_network: bool = True
    log: list[RequestLogEntry] = field(default_factory=list)
    #: Optional RFC 9309 access-policy gate. When set, every URL is checked
    #: against its host's robots.txt *before* a request is made, and a refused
    #: URL raises :class:`RobotsDisallowed` instead of being fetched. It is a
    #: field on the client rather than a call in each caller so that no code path
    #: can bypass it by forgetting to ask.
    robots: RobotsGate | None = None
    robots_refusals: list[RobotsDecision] = field(default_factory=list)

    _last_request_at: dict[str, float] = field(default_factory=dict, init=False)
    _request_count: int = field(default=0, init=False)

    # -- public API --------------------------------------------------------
    @property
    def request_count(self) -> int:
        return self._request_count

    def get_json(self, url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        return self.get(url, params=params, headers=headers).json()

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResult:
        """GET ``url`` with retries. Raises on unreachable host or error status."""
        if params:
            url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
        host = urllib.parse.urlparse(url).netloc
        if not self.allow_network:
            raise NetworkUnavailable(f"network disabled by configuration; refused GET {url}")
        if self.robots is not None:
            decision = self.robots.check(url)
            if not decision.allowed:
                if decision not in self.robots_refusals:
                    self.robots_refusals.append(decision)
                raise RobotsDisallowed(decision)
        if self._request_count >= self.max_requests:
            raise NetworkUnavailable(
                f"request budget exhausted ({self.max_requests} per cycle); refused GET {url}"
            )

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            self._sleep_for_politeness(host)
            started = time.monotonic()
            try:
                result = self._raw_get(url, headers=headers, attempts=attempt)
            except NetworkUnavailable:
                raise
            except urllib.error.HTTPError as exc:  # reachable, bad status
                body = ""
                try:
                    body = exc.read(2048).decode("utf-8", errors="replace")
                except Exception:  # pragma: no cover - defensive
                    pass
                elapsed = time.monotonic() - started
                self._record(url, exc.code, 0, "", attempt, elapsed, error=str(exc))
                # 4xx (except 429) will not improve on retry.
                if exc.code < 500 and exc.code != 429:
                    raise HttpError(exc.code, url, body) from exc
                last_error = HttpError(exc.code, url, body)
                self._backoff(attempt)
                continue
            except urllib.error.URLError as exc:
                elapsed = time.monotonic() - started
                self._record(url, None, 0, "", attempt, elapsed, error=str(exc.reason))
                reason = str(getattr(exc, "reason", exc))
                # DNS/connection-level failures are terminal for this run.
                if _is_unreachable(reason):
                    raise NetworkUnavailable(f"{host} unreachable: {reason}") from exc
                last_error = exc
                self._backoff(attempt)
                continue
            except (TimeoutError, socket.timeout) as exc:
                elapsed = time.monotonic() - started
                self._record(url, None, 0, "", attempt, elapsed, error="timeout")
                last_error = exc
                self._backoff(attempt)
                continue
            except json.JSONDecodeError:
                raise
            except Exception as exc:  # pragma: no cover - defensive
                elapsed = time.monotonic() - started
                self._record(url, None, 0, "", attempt, elapsed, error=repr(exc))
                raise NetworkUnavailable(f"unexpected transport failure for {url}: {exc!r}") from exc

            self._record(url, result.status, len(result.body), result.sha256, attempt, time.monotonic() - started)
            return result

        raise NetworkUnavailable(f"all {self.max_retries} attempts failed for {url}: {last_error}")

    # -- internals ---------------------------------------------------------
    def _raw_get(self, url: str, *, headers: dict[str, str] | None, attempts: int) -> HttpResult:
        request = urllib.request.Request(url, method="GET")
        request.add_header("User-Agent", self.user_agent)
        request.add_header("Accept", "application/json, application/xml, text/plain, text/html;q=0.8, */*;q=0.5")
        request.add_header("Accept-Encoding", "identity")
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = response.read()
            return HttpResult(
                url=response.geturl(),
                status=response.status,
                headers={k.lower(): v for k, v in response.headers.items()},
                body=body,
                content_type=response.headers.get("content-type", ""),
                retrieved_at=utcnow_iso(),
                attempts=attempts,
            )

    def _sleep_for_politeness(self, host: str) -> None:
        last = self._last_request_at.get(host)
        if last is not None:
            wait = self.min_interval - (time.monotonic() - last)
            if wait > 0:
                time.sleep(wait)
        self._last_request_at[host] = time.monotonic()

    @staticmethod
    def _backoff(attempt: int) -> None:
        time.sleep(min(2 ** (attempt - 1), 8))

    def _record(
        self,
        url: str,
        status: int | None,
        size: int,
        digest: str,
        attempts: int,
        seconds: float,
        *,
        error: str = "",
    ) -> None:
        self._request_count += 1
        entry = RequestLogEntry(url, status, size, digest, utcnow_iso(), attempts, round(seconds, 3), error)
        self.log.append(entry)
        if error:
            LOG.warning("request failed url=%s status=%s error=%s", url, status, error)
        else:
            LOG.info("request ok url=%s status=%s bytes=%s", url, status, size)


def _is_unreachable(reason: str) -> bool:
    """Heuristics for 'this host is not reachable from here at all'."""
    lowered = reason.lower()
    markers = (
        "name or service not known",
        "nodename nor servname",
        "temporary failure in name resolution",
        "connection refused",
        "network is unreachable",
        "no route to host",
        "connection reset by peer",
        "certificate verify failed",
        "unknown url type",
        # A sandbox or proxy that refuses egress closes the TLS session. Retrying
        # the same request three times only makes the run slower and the log
        # noisier, so this is treated as a terminal reachability failure and the
        # caller records it as a gap.
        "tls/ssl connection has been closed",
        "eof occurred in violation of protocol",
        "ssl: wrong version number",
        "certificate is not trusted",
    )
    return any(marker in lowered for marker in markers)
