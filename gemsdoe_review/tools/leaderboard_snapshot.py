#!/usr/bin/env python3
"""Parse a saved public-leaderboard transcript into the session evidence JSON.

The DrivenData leaderboard renders client-side and this sandbox has no TLS egress
to drivendata.org, so the page is read with the platform page fetcher and saved
verbatim as a markdown transcript (evidence/leaderboard_raw_*.md). This tool parses
THAT file: it never invents a row, and it reports what the transcript does and does
not contain. Re-run it against a fresh transcript to refresh the field context.

    python leaderboard_snapshot.py --raw evidence/leaderboard_raw_2026-09-26_session5.md \\
        --out evidence/leaderboard_snapshot_2026-09-26_session5.json

It also answers the brief's attribution question mechanically: for each score the
brief attaches to one of our sites, which participant rows carry it today.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

BRIEF_SCORES = {
    "GEMSDOE1": 0.1563,
    "GEMSDOE2": 0.1560,
    "GEMSDOE3 (entrant A)": 0.1193,
    "GEMSDOE3 (entrant B)": 0.0830,
    "GEMSDOE3 (entrant C)": 0.1152,
}
ORGANIZER = "doegemsDrivendata"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse(md: str) -> list[dict]:
    rows = []
    for line in md.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([0-9.]+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|$", line)
        if not m:
            continue
        rank, name, score, subs, last = m.groups()
        rows.append({"rank": int(rank), "participant": name.strip(), "score": float(score),
                     "submissions": int(subs), "last_submission": last.strip()})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    text = args.raw.read_text()
    rows = parse(text)
    if not rows:
        raise SystemExit("no leaderboard rows parsed from the transcript")
    ranks = [r["rank"] for r in rows]
    if ranks != list(range(1, len(rows) + 1)):
        raise SystemExit("transcript rows are not a contiguous 1..N ranking")
    by_score: dict[float, list[dict]] = {}
    for r in rows:
        by_score.setdefault(r["score"], []).append(r)
    attributed = []
    for label, score in BRIEF_SCORES.items():
        holders = by_score.get(score, [])
        attributed.append({"brief_calls_it": label, "score": score,
                           "rows_on_board_today": holders,
                           "reading": ("held by " + ", ".join(f"{h['participant']} (#{h['rank']}, "
                                                             f"{h['submissions']} submission(s))"
                                                             for h in holders)) if holders
                           else "NOT on the visible board today"})
    payload = {
        "_what_this_is": ("Public leaderboard snapshot parsed from the verbatim transcript "
                          f"{args.raw.name}. Other participants' data only; no row is claimed as ours."),
        "source_url": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
        "transcript_sha256": sha256(args.raw),
        "tool": Path(__file__).name,
        "rows_visible": len(rows),
        "field_high": rows[0],
        "organizer_row": next((r for r in rows if r["participant"] == ORGANIZER), None),
        "brief_attributed_scores_today": attributed,
        "top_10": rows[:10],
        "rows": rows,
        "reading": {
            "field_high_unchanged": rows[0]["participant"] == "DARD" and rows[0]["score"] == 0.3049,
            "organizer_reference": 0.1847,
            "owned_public_score": None,
            "note": ("No DrivenData account is connected to this workspace. GitHub ownership of the "
                     "GEMS-named repositories does not identify a registration, so no row above is our "
                     "score and none is used as a test arm of our own experiment."),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    for a in attributed:
        print(f"{a['brief_calls_it']:24} {a['score']:.4f} -> {a['reading']}")
    print("field high:", rows[0]["participant"], rows[0]["score"], "| organizer:", payload["organizer_row"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
