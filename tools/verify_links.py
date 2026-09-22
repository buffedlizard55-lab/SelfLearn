#!/usr/bin/env python3
"""Check every URL this project publishes or depends on.

    python3 tools/verify_links.py [--strict] [--only SOURCE_ID] [--json]

Three sets of URLs matter, and all three are checked:

1. **The source register** - documentation, key-request, licence and terms links
   for all 36 registered sources. A stale documentation URL is how an adapter
   silently rots, so it is a finding, not a detail.
2. **The change-scan mechanisms** - the operator documentation that authorises
   each "what changed" filter.
3. **The citations in the repository's own prose** - every URL written into
   ``docs/*.md``, ``README.md`` and the requirements matrix, which is what a
   reviewer is asked to open for manual review.

The result is written to ``reports/link_check.json`` with, per URL: the HTTP
status, the URL after redirects, the elapsed time and the error if any. Nothing
is asserted about a page's *content*; this tool proves that a link resolves and
says where it landed, which is the part a human cannot check at a glance across
eighty URLs.

``--strict`` exits non-zero when any URL fails to resolve, for use in CI. Note
that a sandbox with limited egress will report most hosts as unreachable; that is
a property of the machine, and the report records the error so the two cases can
be told apart.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.fetch.changes import mechanism_table  # noqa: E402
from selflearn.fetch.net import HttpClient, HttpError, NetworkUnavailable  # noqa: E402
from selflearn.fetch.registry import REGISTRY  # noqa: E402

PROSE_GLOBS = ("docs/*.md", "README.md", "reports/SUMMARY.md")
URL_RE = re.compile(r"https?://[^\s\)\]>\"'`,]+")

#: Links that are deliberately not fetched: they are examples, placeholders, or
#: machine-readable endpoints that return large payloads.
SKIP_PREFIXES = (
    "https://selflearn.example.invalid",
    "https://api.github.com/repos/OWNER",
    "http://www.w3.org/2000/svg",
)


def register_urls() -> list[dict[str, str]]:
    rows = []
    for spec in sorted(REGISTRY.values(), key=lambda s: s.source_id):
        for field in ("docs_url", "key_url", "license_url", "terms_url"):
            value = getattr(spec, field, "") or ""
            if value.startswith("http"):
                rows.append({"group": "register", "source_id": spec.source_id, "field": field, "url": value})
    return rows


def mechanism_urls() -> list[dict[str, str]]:
    return [
        {"group": "change_mechanism", "source_id": row["source_id"], "field": "docs_url", "url": row["docs_url"]}
        for row in mechanism_table()
    ]


def prose_urls(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for pattern in PROSE_GLOBS:
        for path in sorted(root.glob(pattern)):
            for match in URL_RE.findall(path.read_text(encoding="utf-8", errors="replace")):
                url = match.rstrip(".)")
                if url in seen or url.startswith(SKIP_PREFIXES):
                    continue
                seen.add(url)
                rows.append(
                    {
                        "group": "prose",
                        "source_id": path.name,
                        "field": "citation",
                        "url": url,
                    }
                )
    return rows


def all_urls(root: Path, only: str | None = None) -> list[dict[str, str]]:
    rows = register_urls() + mechanism_urls() + prose_urls(root)
    if only:
        rows = [row for row in rows if row["source_id"] == only]
    unique: dict[str, dict[str, str]] = {}
    for row in rows:
        unique.setdefault(row["url"], row)
    return sorted(unique.values(), key=lambda row: (row["group"], row["url"]))


def check(client: HttpClient, rows: Iterable[dict[str, str]]) -> list[dict[str, Any]]:
    results = []
    for row in rows:
        started = time.monotonic()
        outcome: dict[str, Any] = dict(row)
        outcome["elapsed_seconds"] = 0.0
        try:
            result = client.get(row["url"])
            outcome["status"] = result.status
            outcome["final_url"] = result.url
            outcome["bytes"] = len(result.body)
            outcome["ok"] = 200 <= result.status < 400
            outcome["error"] = ""
        except HttpError as exc:
            outcome["status"] = exc.status
            outcome["final_url"] = row["url"]
            outcome["ok"] = False
            outcome["error"] = (exc.body or "")[:200]
        except NetworkUnavailable as exc:
            outcome["status"] = None
            outcome["final_url"] = row["url"]
            outcome["ok"] = False
            outcome["error"] = f"unreachable: {str(exc)[:160]}"
        except Exception as exc:  # pragma: no cover - defensive
            outcome["status"] = None
            outcome["final_url"] = row["url"]
            outcome["ok"] = False
            outcome["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        outcome["elapsed_seconds"] = round(time.monotonic() - started, 2)
        results.append(outcome)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check every URL the project publishes.")
    parser.add_argument("--strict", action="store_true", help="exit non-zero if any URL fails")
    parser.add_argument("--only", default=None, help="limit to one source id or file name")
    parser.add_argument("--limit", type=int, default=400, help="request budget")
    parser.add_argument("--json", action="store_true", help="print the full report")
    parser.add_argument(
        "--label",
        default=os.environ.get("LINK_CHECK_LABEL", "local machine"),
        help="where this check ran, recorded in the report so a result can be judged by its egress",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="where to write the report (default: reports/link_check.json)",
    )
    args = parser.parse_args(argv)

    rows = all_urls(ROOT, only=args.only)
    client = HttpClient(max_requests=args.limit)
    results = check(client, rows)

    by_status: dict[str, int] = {}
    for row in results:
        key = str(row["status"]) if row["status"] else "unreachable"
        by_status[key] = by_status.get(key, 0) + 1

    failures = [row for row in results if not row["ok"]]
    print(f"checked {len(results)} unique URL(s)")
    print("by status: " + json.dumps(dict(sorted(by_status.items()))))
    for row in failures:
        print(f"  FAIL [{row['group']:16}] {row['url']}\n        {row['error'][:150]}")

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checked": len(results),
        "ok": len(results) - len(failures),
        "failed": len(failures),
        "by_status": dict(sorted(by_status.items())),
        "label": args.label,
        "results": results,
        "note": (
            "Status and final URL only; page content is not asserted here. `label` names the machine that ran the "
            "check, because a host with restricted egress reports 'unreachable' for hosts it cannot reach, which is a "
            "property of the machine and is recorded as such rather than being read as a broken link."
        ),
    }
    out = Path(args.out) if args.out else ROOT / "reports" / "link_check.json"
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} "
          f"({len(results)} URL(s), {len(results) - len(failures)} ok, {len(failures)} failed, label: {args.label!r})")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if (args.strict and failures) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
