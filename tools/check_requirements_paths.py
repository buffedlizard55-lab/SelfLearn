#!/usr/bin/env python3
"""Check every repository path cited by the requirements matrix.

    python3 tools/check_requirements_paths.py

Pass 12's table claims that a script walks every `evidence` path and every
backticked path in `how_to_verify` across all rows of ``data/requirements.json``.
This is that script, committed so the claim stays re-runnable: the ``evidence``
field is a list of repository paths (files or directories), and the prose fields
may cite paths inside backticks, sometimes as ``file#anchor``. It exits non-zero
when a cited path (or the file half of a ``file#anchor`` citation) does not exist
in the working tree.

Backticked phrases that are not paths (commands, figures, prose) and URLs are
skipped; a fragment after ``#`` is dropped before the existence check.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "data" / "requirements.json"
BACKTICK = re.compile(r"`([^`]+)`")
SKIP_PREFIX = ("http://", "https://", "python", "grep", "$", "cd ")


def _looks_like_path(token: str) -> bool:
    if token.startswith(SKIP_PREFIX):
        return False
    if " " in token and "/" not in token:
        return False
    return "/" in token or token.endswith((".md", ".py", ".json", ".yml", ".yaml"))


def main() -> int:
    rows = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    checked = 0
    missing: list[tuple[str, str, str]] = []
    anchors: list[tuple[str, str, str]] = []

    def check(rid: str, field: str, token: str) -> None:
        nonlocal checked
        if not _looks_like_path(token):
            return
        path_part, _, anchor = token.partition("#")
        checked += 1
        if not (ROOT / path_part).exists():
            missing.append((rid, field, token))
        elif anchor:
            anchors.append((rid, field, token))

    for row in rows:
        rid = str(row.get("id", "?"))
        evidence = row.get("evidence") or []
        if isinstance(evidence, str):
            evidence = [evidence]
        for item in evidence:
            check(rid, "evidence", str(item))
        for field in ("how_to_verify", "source", "gap", "requirement"):
            value = str(row.get(field) or "")
            for token in BACKTICK.findall(value):
                check(rid, field, token)

    print(f"rows: {len(rows)} | path citations checked: {checked}")
    if anchors:
        print(f"file#anchor citations (files exist): {len(anchors)}")
        for rid, field, token in anchors:
            print(f"  {rid} {field}: {token}")
    if missing:
        print("MISSING PATHS:")
        for rid, field, token in missing:
            print(f"  {rid} {field}: {token}")
        return 1
    print("all cited repository paths exist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
