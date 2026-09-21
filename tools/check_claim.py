#!/usr/bin/env python3
"""Check one claim by hand, end to end.

This is the reviewer's tool. Given a claim id it prints everything needed to decide
whether the claim should have been published:

* the claim text and the quoted span,
* the document it was cut from, with the stored hash and the file the hash covers,
* the verification result recomputed *now* from the stored bytes,
* the source URL to open in a browser for manual review.

Usage:
    python3 tools/check_claim.py                 # the most recent claim
    python3 tools/check_claim.py cl-1a2b3c4d     # a specific claim
    python3 tools/check_claim.py --list 10       # the newest ten claims
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.config import EVIDENCE_DIR, LIBRARY_DIR  # noqa: E402
from selflearn.learn.calibration import active_thresholds  # noqa: E402
from selflearn.util import sha256_text  # noqa: E402
from selflearn.verify.audit import recheck_claims  # noqa: E402


def load_claims() -> list[dict]:
    path = LIBRARY_DIR / "claims.jsonl"
    if not path.exists():
        raise SystemExit(f"No claims found at {path}. Run a cycle first: python3 -m selflearn run --mode live")
    rows: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["claim_id"]] = row  # later rows supersede earlier ones
    return list(rows.values())


def snapshot_path(claim: dict) -> Path:
    return EVIDENCE_DIR / f"{claim['evidence_id']}.json"


def report(claim: dict) -> int:
    thresholds = active_thresholds()
    problems = 0
    print("=" * 78)
    print(f"claim      : {claim['claim_id']}")
    print(f"kind       : {claim.get('claim_kind', 'direct')}")
    print(f"verdict    : {claim['verification']['verdict']} (coverage {claim['verification']['coverage']})")
    print(f"confidence : {claim['confidence']}")
    print(f"claim text : {claim['text']}")
    if claim.get("quote"):
        print(f"quote      : {claim['quote']}")
    print(f"source     : {claim['source_name']} [{claim['evidence_class']} rank {claim['evidence_rank']}]")
    print(f"open this  : {claim['url'] or '(no link - derived claim)'}")

    if claim.get("claim_kind") == "derived":
        figures = claim.get("context_numbers") or []
        print(f"figures    : {figures} (a derived claim is checked against these, not a document)")
        problems += len(recheck_claims([_as_claim(claim)], EVIDENCE_DIR))
        return problems

    path = snapshot_path(claim)
    if not path.exists():
        print(f"MISSING    : no snapshot at {path}")
        return problems + 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    text = payload.get("text", "")
    recorded = payload.get("content_hash", "")
    actual = sha256_text(text)
    match = recorded == actual
    print(f"snapshot   : {path.relative_to(ROOT)}")
    print(f"hash       : recorded {recorded[:24]}... actual {actual[:24]}... -> {'MATCH' if match else 'MISMATCH'}")
    problems += 0 if match else 1

    verbatim = bool(claim.get("quote")) and claim["quote"] in text
    print(f"quote in stored text : {'yes' if verbatim else 'no' if claim.get('quote') else 'no quote recorded'}")
    findings = recheck_claims([_as_claim(claim)], EVIDENCE_DIR)
    print(f"re-check now : {'agrees with what was published' if not findings else 'DISAGREES'}")
    for finding in findings:
        print(f"  - [{finding.severity}] {finding.summary}: {finding.detail[:160]}")
    problems += len(findings)

    print(f"thresholds in force : supported>={thresholds.supported} partial>={thresholds.partially_supported} "
          f"quote>={thresholds.quote_min_chars} chars")
    print(f"still passes       : {'yes' if claim['verification']['verdict'] == 'supported' else 'no'}")
    print("manual step        : open the link above and search the page for the quoted span.")
    return problems


def _as_claim(row: dict):
    """Rebuild a Claim object from its stored JSONL row (the same loader the audit uses)."""
    from selflearn.learn.store import _claim_from_row

    return _claim_from_row(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("claim_id", nargs="?", help="claim id to inspect; defaults to the newest claim")
    parser.add_argument("--list", type=int, default=0, metavar="N", help="list the newest N claims and exit")
    args = parser.parse_args(argv)

    claims = load_claims()
    if not claims:
        raise SystemExit("The library holds no claims yet.")
    claims.sort(key=lambda row: row.get("recorded_at", ""), reverse=True)

    if args.list:
        for row in claims[: args.list]:
            print(f"{row['claim_id']}  {row['verification']['verdict']:20} {row['text'][:96]}")
        return 0

    if args.claim_id:
        matches = [row for row in claims if row["claim_id"] == args.claim_id]
        if not matches:
            raise SystemExit(f"No claim with id {args.claim_id}. Use --list to see the ids.")
        claim = matches[0]
    else:
        claim = claims[0]

    return 0 if report(claim) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
