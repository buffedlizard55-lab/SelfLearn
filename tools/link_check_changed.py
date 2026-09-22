#!/usr/bin/env python3
"""Decide whether a fresh link check is worth committing.

    python3 tools/link_check_changed.py [--report reports/link_check.json]

The report carries volatile fields - the timestamp, and how long each request
took - so a naive ``git diff`` reports a change on every run and the workflow
would commit on every push. What a reviewer actually cares about is whether any
URL's *outcome* moved: resolved, redirected somewhere else, or stopped
resolving.

This compares the committed report against the fresh one on ``(url, status,
final_url, ok)`` only and exits 0 when that set differs, 1 when it does not.
A missing committed report counts as a change, so the first run always lands.

Exit codes: 0 = commit it, 1 = nothing meaningful changed, 2 = unreadable input.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def outcomes(report: dict) -> set[tuple[str, str, str, bool]]:
    """The part of a link-check report that means something to a reader."""
    out = set()
    for row in report.get("results", []) or []:
        out.add(
            (
                str(row.get("url", "")),
                str(row.get("status")),
                str(row.get("final_url", "")),
                bool(row.get("ok")),
            )
        )
    return out


def committed(path: Path) -> dict | None:
    """The report as stored in git at HEAD, or None if it is not there."""
    try:
        raw = subprocess.run(
            ["git", "show", f"HEAD:{path.relative_to(ROOT)}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, ValueError, OSError):
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Has any published URL changed its outcome?")
    parser.add_argument("--report", default="reports/link_check.json")
    args = parser.parse_args(argv)

    fresh_path = ROOT / args.report if not Path(args.report).is_absolute() else Path(args.report)
    try:
        fresh = json.loads(fresh_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read the fresh report: {exc}", file=sys.stderr)
        return 2

    previous = committed(fresh_path)
    if previous is None:
        print("no committed link check yet: this one is a change by definition")
        return 0

    before, after = outcomes(previous), outcomes(fresh)
    if before == after:
        print(f"{len(after)} URL outcome(s) unchanged; only timings and timestamps differ")
        return 1

    gone = before - after
    new = after - before
    print(f"{len(gone)} outcome(s) gone, {len(new)} new")
    for url, status, final_url, ok in sorted(new)[:40]:
        print(f"  now  {status:>6} ok={ok!s:5} {url}")
    for url, status, final_url, ok in sorted(gone)[:40]:
        print(f"  was  {status:>6} ok={ok!s:5} {url}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
