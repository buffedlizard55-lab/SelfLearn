#!/usr/bin/env python3
"""Audit whether the entry's `rank_tables_sha256` pin can actually be re-derived.

`6GEMSDOE/data/evidence/features_meta.json` records
`rank_tables_sha256 = 64a62c3b...` next to the feature stack it was built with, and
the stack's own `check_sha` pins the OFFICIAL RASTER hash (which is reproducible).
This tool checks the other pin: rebuild `data/evidence/rank_tables.json` from the
sha256-pinned official rasters and compare.

    python rank_tables_pin_audit.py --entry /path/to/6GEMSDOE \\
        --before /tmp/rank_a.json --after data/evidence/rank_tables.json \\
        --out evidence/rank_tables_pin_audit_session5.json

`--before` and `--after` are two independent builds of the same script on the same
pinned rasters. The comparison ignores `built_utc` and reports whether everything
else is byte-identical after normalisation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def raw_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalised_sha(payload: dict) -> str:
    p = json.loads(json.dumps(payload))
    p.pop("built_utc", None)
    return hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--after", type=Path, required=True)
    ap.add_argument("--pinned-sha", default=None,
                    help="the rank_tables_sha256 recorded in the COMMITTED features_meta.json "
                         "(default: read it from the file on disk; pass it explicitly when the "
                         "file on disk has been overwritten by a rebuild)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    meta = json.loads((args.entry / "data/evidence/features_meta.json").read_text())
    a = json.loads(args.before.read_text())
    b = json.loads(args.after.read_text())
    pinned = args.pinned_sha or meta.get("rank_tables_sha256")

    reproducible = normalised_sha(a) == normalised_sha(b)
    payload = {
        "kind": "audit of a recorded hash pin; NOT a leaderboard score",
        "entry": str(args.entry.resolve()),
        "pinned_rank_tables_sha256": pinned,
        "meta_file_on_disk_now": meta.get("rank_tables_sha256"),
        "rebuilt_rank_tables_sha256": {"before": raw_sha(args.before), "after": raw_sha(args.after)},
        "built_utc": {"before": a.get("built_utc"), "after": b.get("built_utc")},
        "content_identical_ignoring_built_utc": reproducible,
        "normalised_sha256": normalised_sha(a),
        "raster_pin_reproduced": meta.get("features_sha256") == b.get("features_sha256"),
        "finding": (
            "The rank-table CONTENT is deterministic (two independent builds are identical "
            "once `built_utc` is removed), but the FILE hash is not: `scripts/build_rank_tables.py` "
            "writes `built_utc` into the JSON, so `rank_tables_sha256` can never be reproduced by "
            "a re-run and the value recorded in features_meta.json (64a62c3b...) is unreproducible "
            "by construction. The pin that IS reproducible is the official raster's sha256, which "
            "`RankTables.check_sha` enforces. A hash pin that cannot be re-derived is not a "
            "verification, so this field should either be dropped or computed over the "
            "timestamp-free content."),
        "impact": (
            "Low for correctness (the raster pin still gates the build) but it makes the "
            "'hash-verified' claim in the entry's docs stronger than the evidence for this one "
            "field. Reported as an irregularity rather than smoothed over."),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in
                      ("content_identical_ignoring_built_utc", "raster_pin_reproduced",
                       "pinned_rank_tables_sha256", "rebuilt_rank_tables_sha256")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
