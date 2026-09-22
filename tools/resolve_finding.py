#!/usr/bin/env python3
"""Resolve an irregularity or a contradiction without destroying its record.

    python3 tools/resolve_finding.py --id irr-569286381eaf --reason "..." [--link URL]
    python3 tools/resolve_finding.py --id con-0a1b2c3d4e5f --reason "..." [--link URL]
    python3 tools/resolve_finding.py --list            # every open finding
    python3 tools/resolve_finding.py --list --all      # resolved ones too

This is the second half of the reviewer workflow that ``tools/reject_topic.py``
started. The library is append-only, so resolving a finding means writing a new
record for the same primary key that carries the reviewer's reason, the time and
an optional link. The original summary, detail and claim ids are copied unchanged
onto that record; nothing is edited and nothing is deleted. On the review page the
finding moves to the "Resolved" table with the reason shown next to the original
text.

The engine's own passes never write the reviewer fields. When a later cycle
re-detects the same irregularity or the same contradicting pair, the store carries
the reviewer's decision forward rather than reopening it, so a decision made here
survives the next run. A reviewer can reopen a finding explicitly with ``--reopen``.

The id prefix decides the stream: ``irr-`` is an irregularity in
``library/irregularities.jsonl``, ``con-`` is a contradiction in
``library/contradictions.jsonl``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.learn.store import Library  # noqa: E402
from selflearn.models import Contradiction, Irregularity  # noqa: E402
from selflearn.util import utcnow_iso  # noqa: E402


def list_findings(library: Library, *, include_resolved: bool) -> None:
    irregularities = sorted(library.irregularities.values(), key=lambda f: (f.resolved, f.severity, f.irregularity_id))
    contradictions = sorted(library.contradictions.values(), key=lambda c: (c.resolution != "unresolved", c.contradiction_id))
    printed = 0
    for finding in irregularities:
        if finding.resolved and not include_resolved:
            continue
        state = "resolved" if finding.resolved else "open"
        print(f"{finding.irregularity_id:20} {state:9} {finding.severity:8} {finding.stage:12} {finding.summary}")
        printed += 1
    for contradiction in contradictions:
        if contradiction.resolution != "unresolved" and not include_resolved:
            continue
        print(
            f"{contradiction.contradiction_id:20} {contradiction.resolution:9} {contradiction.severity:8} "
            f"{'contradict':12} {contradiction.claim_a} vs {contradiction.claim_b} ({contradiction.kind})"
        )
        printed += 1
    if not printed:
        print("no open findings" if not include_resolved else "no findings")


def resolve_irregularity(finding: Irregularity, *, reason: str, link: str, reopen: bool) -> Irregularity:
    if reopen:
        finding.resolved = False
        finding.resolution = f"Reopened {utcnow_iso()}: {reason}" + (f" Reference: {link}" if link else "")
        finding.resolved_at = ""
        finding.resolution_link = link
        return finding
    finding.resolved = True
    finding.resolution = reason
    finding.resolved_at = utcnow_iso()
    finding.resolution_link = link
    return finding


def resolve_contradiction(contradiction: Contradiction, *, reason: str, link: str, reopen: bool) -> Contradiction:
    if reopen:
        contradiction.resolution = "unresolved"
        contradiction.resolution_note = f"Reopened {utcnow_iso()}: {reason}" + (f" Reference: {link}" if link else "")
        contradiction.resolved_at = ""
        contradiction.resolution_link = link
        return contradiction
    contradiction.resolution = "resolved"
    contradiction.resolution_note = reason
    contradiction.resolved_at = utcnow_iso()
    contradiction.resolution_link = link
    return contradiction


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve (or reopen) an irregularity or contradiction, with a recorded reason.")
    parser.add_argument("--id", dest="finding_id", default="", help="irr-... or con-... id as shown on the review page")
    parser.add_argument("--reason", default="", help="why it is resolved; stored on the record and shown on the review page")
    parser.add_argument("--link", default="", help="optional URL supporting the decision")
    parser.add_argument("--reopen", action="store_true", help="reopen a finding a reviewer closed earlier")
    parser.add_argument("--root", default=str(ROOT), help="library root (defaults to the repository)")
    parser.add_argument("--list", action="store_true", help="list open findings and exit")
    parser.add_argument("--all", action="store_true", help="with --list, include resolved findings")
    args = parser.parse_args(argv)

    root = Path(args.root)
    library = Library.load(root, run_id=f"review-{utcnow_iso()[:10]}")

    if args.list or not args.finding_id:
        list_findings(library, include_resolved=args.all)
        return 0
    if not args.reason:
        print("--reason is required: the record must say why a reviewer acted", file=sys.stderr)
        return 2

    if args.finding_id.startswith("irr-"):
        finding = library.irregularities.get(args.finding_id)
        if finding is None:
            print(f"no irregularity with id {args.finding_id}", file=sys.stderr)
            return 1
        if finding.resolved and not args.reopen:
            print(f"{args.finding_id} is already resolved ({finding.resolved_at}): {finding.resolution}", file=sys.stderr)
            return 1
        if not finding.resolved and args.reopen:
            print(f"{args.finding_id} is not resolved; nothing to reopen", file=sys.stderr)
            return 1
        library.add_irregularities([resolve_irregularity(finding, reason=args.reason, link=args.link, reopen=args.reopen)])
        verb = "reopened" if args.reopen else "resolved"
        print(f"{verb} {finding.irregularity_id} ('{finding.summary}')")
    elif args.finding_id.startswith("con-"):
        contradiction = library.contradictions.get(args.finding_id)
        if contradiction is None:
            print(f"no contradiction with id {args.finding_id}", file=sys.stderr)
            return 1
        if contradiction.resolution != "unresolved" and not args.reopen:
            print(
                f"{args.finding_id} is already resolved ({contradiction.resolved_at}): {contradiction.resolution_note}",
                file=sys.stderr,
            )
            return 1
        if contradiction.resolution == "unresolved" and args.reopen:
            print(f"{args.finding_id} is not resolved; nothing to reopen", file=sys.stderr)
            return 1
        library.add_contradictions(
            [resolve_contradiction(contradiction, reason=args.reason, link=args.link, reopen=args.reopen)]
        )
        verb = "reopened" if args.reopen else "resolved"
        print(f"{verb} {contradiction.contradiction_id} ({contradiction.claim_a} vs {contradiction.claim_b})")
    else:
        print("the id must start with 'irr-' (irregularity) or 'con-' (contradiction)", file=sys.stderr)
        return 2
    print("rebuild the site with 'python3 -m selflearn site'")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
