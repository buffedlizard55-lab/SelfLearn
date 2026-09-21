"""Deterministic text/number/IO helpers used across the engine.

Everything here is pure and side-effect free except the small IO helpers at the
bottom. No third-party imports. No randomness that is not seeded explicitly.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------


def utcnow() -> datetime:
    """Timezone-aware UTC now."""
    return datetime.now(timezone.utc)


def utcnow_iso() -> str:
    """Second-resolution ISO-8601 UTC timestamp, e.g. ``2026-09-21T12:00:00Z``."""
    return utcnow().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: str | None) -> datetime | None:
    """Parse an ISO-8601 string, tolerating a trailing ``Z`` and date-only input."""
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def days_between(earlier: str | None, later: str | None) -> float | None:
    """Whole-ish days between two ISO timestamps, or ``None`` if unparseable."""
    a, b = parse_iso(earlier), parse_iso(later)
    if a is None or b is None:
        return None
    return (b - a).total_seconds() / 86400.0


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def stable_id(prefix: str, *parts: Any) -> str:
    """Deterministic short identifier derived from content.

    Used wherever the engine must be able to re-derive the same identifier from
    the same inputs on a later run (idempotent re-processing).
    """
    joined = "\u0001".join("" if p is None else str(p) for p in parts)
    return f"{prefix}-{hashlib.sha256(joined.encode('utf-8')).hexdigest()[:12]}"


# ---------------------------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------------------------

_UNICODE_FOLD = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u00a0": " ",
    "\u202f": " ",
    "\u2009": " ",
}

_WS_RE = re.compile(r"\s+")


def normalize_ws(text: str) -> str:
    """Collapse all whitespace runs to single spaces and strip the ends."""
    return _WS_RE.sub(" ", text or "").strip()


def normalize_for_match(text: str) -> str:
    """Aggressive normalisation used for substring/quote matching.

    NFKC, unicode quote/dash folding, casefold, whitespace collapse. Deliberately
    *does not* strip punctuation, so that a matched quote still reads correctly
    when displayed back to a human reviewer.
    """
    if not text:
        return ""
    out = unicodedata.normalize("NFKC", text)
    for src, dst in _UNICODE_FOLD.items():
        out = out.replace(src, dst)
    return normalize_ws(out).casefold()


def normalized_contains(haystack: str, needle: str, *, min_needle_chars: int = 12) -> bool:
    """True when ``needle`` appears verbatim in ``haystack`` after normalisation.

    Quotes shorter than ``min_needle_chars`` are rejected: a 4-character
    "quote" would match almost anything and would be worthless as evidence.
    """
    if not needle or len(needle.strip()) < min_needle_chars:
        return False
    return normalize_for_match(needle) in normalize_for_match(haystack)


_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\u201c\"'(])")


def split_sentences(text: str) -> list[str]:
    """Lightweight sentence splitter.

    Not a linguistic parser - intentionally so. It only needs to be good enough
    to cut a source document into quotable spans, and it must be deterministic.
    """
    flat = normalize_ws(text)
    if not flat:
        return []
    parts = _SENTENCE_RE.split(flat)
    return [p.strip() for p in parts if p.strip()]


# Words with no discriminating power when checking whether a document supports
# a claim. Kept small and explicit so the behaviour is inspectable.
STOPWORDS: frozenset[str] = frozenset(
    """
    a about above after again against all am an and any are aren as at be because been
    before being below between both but by can cannot could couldn did didn do does
    doesn doing don down during each few for from further had hadn has hasn have haven
    having he her here hers herself him himself his how i if in into is isn it its
    itself just me more most mustn my myself no nor not now of off on once only or
    other ought our ours ourselves out over own same shan she should shouldn so some
    such than that the their theirs them themselves then there these they this those
    through to too under until up very was wasn we were weren what when where which
    while who whom why with won would wouldn you your yours yourself yourselves
    also may might one two new using used use however therefore thus per via et al
    abstract introduction results discussion conclusion figure table section
    percent percentage pct cent approximately roughly about
    """.split()
)

_WORD_RE = re.compile(r"[a-z][a-z0-9'\-]{2,}")


def content_tokens(text: str) -> set[str]:
    """Discriminating lowercase word tokens (>=3 chars, stopwords removed)."""
    if not text:
        return set()
    folded = normalize_for_match(text)
    return {w for w in _WORD_RE.findall(folded) if w not in STOPWORDS}


# ---------------------------------------------------------------------------
# Number / date extraction (the anti-hallucination guard)
# ---------------------------------------------------------------------------

# Matches 1,234 | 12.5 | 12% | 12.5% | -3 | 2026 | 2026-09-21
_NUMBER_RE = re.compile(r"(?<![\w.])(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)\s?(%|percent|pct)?", re.I)
_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_YEAR_RE = re.compile(r"\b(1[6-9]\d{2}|20\d{2}|21\d{2})\b")


def _canon_number(raw: str) -> str:
    """Canonical form of a numeric literal.

    ``1,234.50`` -> ``1234.5``; ``-0`` -> ``0``; ``007`` -> ``7``.
    Thousands separators and trailing zeros are removed so that formatting
    differences between a claim and its source do not create false mismatches.
    """
    cleaned = raw.replace(",", "").strip()
    negative = cleaned.startswith("-")
    cleaned = cleaned.lstrip("+-")
    if "." in cleaned:
        whole, _, frac = cleaned.partition(".")
        whole = whole.lstrip("0") or "0"
        frac = frac.rstrip("0")
        out = f"{whole}.{frac}" if frac else whole
    else:
        out = cleaned.lstrip("0") or "0"
    return ("-" + out) if negative and out != "0" else out


# Long identifiers minted by this engine or by an API (claim ids, evidence ids,
# content hashes) contain digit groups that are not quantities. Extracting them
# would create phantom numbers and make the numeric guard fire on a claim id, so
# they are removed before any number is read.
_IDENTIFIER_RES = (
    re.compile(r"sha256:[0-9a-f]{8,}", re.I),
    re.compile(r"\b[a-z][a-z0-9]{1,}-[0-9][0-9a-f]{5,}\b"),
    re.compile(r"\b[0-9a-f]{32,}\b", re.I),
)


def strip_identifiers(text: str) -> str:
    """Remove opaque identifiers so their digits cannot be read as quantities."""
    if not text:
        return ""
    out = text
    for pattern in _IDENTIFIER_RES:
        out = pattern.sub(" ", out)
    return out


def extract_numbers(text: str) -> set[str]:
    """All numeric literals in ``text`` as canonical strings, percent-marked.

    Percentages are canonicalised to ``<value>%`` so that "12 percent", "12%"
    and "12 pct" all collapse to the same token. Plain numbers are canonicalised
    without a unit suffix - the engine never invents a unit.
    """
    text = strip_identifiers(text)
    if not text:
        return set()
    found: set[str] = set()
    for match in _NUMBER_RE.finditer(text):
        value = _canon_number(match.group(1))
        unit = (match.group(2) or "").lower()
        if unit in {"%", "percent", "pct"}:
            found.add(f"{value}%")
        else:
            found.add(value)
    return found


def extract_years(text: str) -> set[str]:
    """4-digit years present in the text (used for temporal claims)."""
    return set(_YEAR_RE.findall(text or ""))


def extract_dates(text: str) -> set[str]:
    """ISO dates present in the text."""
    return {f"{y}-{m}-{d}" for y, m, d in _DATE_RE.findall(text or "")}


def missing_numbers(claim_text: str, source_text: str) -> set[str]:
    """Numbers in the claim that do *not* appear in the source text.

    A non-empty result is a hard verification failure: the claim contains a
    quantitative assertion the source does not support. This is the single most
    important guard against fabricated statistics.
    """
    claim_nums = extract_numbers(claim_text)
    if not claim_nums:
        return set()
    source_nums = extract_numbers(source_text)
    return {n for n in claim_nums if n not in source_nums}


def coverage(claim_text: str, source_text: str) -> float:
    """Fraction of the claim's content tokens that occur in the source.

    Returns ``0.0`` when the claim has no content tokens (so an unverifiable
    empty claim can never score as supported).
    """
    claim_tokens = content_tokens(claim_text)
    if not claim_tokens:
        return 0.0
    return len(claim_tokens & content_tokens(source_text)) / len(claim_tokens)


# ---------------------------------------------------------------------------
# Similarity (dedupe, near-duplicate detection, contradiction candidates)
# ---------------------------------------------------------------------------


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def similarity(text_a: str, text_b: str) -> float:
    """Token-set Jaccard similarity of two texts in ``[0, 1]``."""
    return jaccard(content_tokens(text_a), content_tokens(text_b))


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def slugify(text: str, *, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:max_len].rstrip("-") or "untitled"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def truncate(text: str, limit: int) -> str:
    flat = normalize_ws(text)
    if len(flat) <= limit:
        return flat
    return flat[: max(0, limit - 1)].rstrip() + "\u2026"


# ---------------------------------------------------------------------------
# Deterministic JSON IO
# ---------------------------------------------------------------------------


def to_jsonable(obj: Any) -> Any:
    """Recursively convert dataclasses/sets/paths into JSON-safe primitives."""
    if hasattr(obj, "to_dict"):
        return to_jsonable(obj.to_dict())
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, set | frozenset):
        return sorted(to_jsonable(v) for v in obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return obj


def save_json(path: Path | str, payload: Any, *, indent: int = 2) -> Path:
    """Write JSON deterministically (sorted keys, trailing newline, atomic).

    Sorted keys + atomic replace mean that re-running the engine on unchanged
    inputs produces byte-identical files, which is what makes the published site
    diffable and auditable.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(to_jsonable(payload), indent=indent, sort_keys=True, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=".tmp-", suffix=target.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return target


def load_json(path: Path | str, default: Any = None) -> Any:
    target = Path(path)
    if not target.exists():
        return default
    with target.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def append_jsonl(path: Path | str, records: Iterable[dict[str, Any]]) -> int:
    """Append records to a JSONL file. Returns the number written."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(to_jsonable(record), sort_keys=True, ensure_ascii=False) + "\n")
            count += 1
    return count


def read_jsonl(path: Path | str) -> Iterator[dict[str, Any]]:
    """Iterate records from a JSONL file, skipping unparseable lines.

    Malformed lines are skipped rather than raised so that one corrupt record
    cannot take the whole engine offline. The line number is preserved in-band
    as ``_line`` for traceability during audits.
    """
    target = Path(path)
    if not target.exists():
        return
    with target.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                record.setdefault("_line", lineno)
                yield record


def write_text(path: Path | str, text: str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def read_text(path: Path | str, default: str = "") -> str:
    target = Path(path)
    if not target.exists():
        return default
    return target.read_text(encoding="utf-8")
