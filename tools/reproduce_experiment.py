#!/usr/bin/env python3
"""Re-run a stored experiment and compare the fresh result with the recorded one.

Every experiment row in `library/experiments.jsonl` records the command, the seed,
the SHA-256 of the script that ran and the result. This tool repeats the run from the
stored command and reports whether the new result matches field by field, which is
the reproducibility claim the site makes about every experiment.

Usage:
    python3 tools/reproduce_experiment.py                 # the most recent experiment
    python3 tools/reproduce_experiment.py sorting-comparisons-v1
    python3 tools/reproduce_experiment.py --list
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.config import LIBRARY_DIR  # noqa: E402
from selflearn.util import sha256_text  # noqa: E402

# Fields that cannot be reproduced by design: wall-clock measurements and the
# environment the run happened in. They are reported as ignored rather than as a
# difference, because a comparison count is the claim the engine makes - not a speed.
COMPARISON_SKIP = {"environment", "ran_at", "duration_seconds", "out_path", "generated_at"}
TIMING_KEY_MARKERS = ("second", "elapsed", "duration", "timestamp", "seconds")


def load_experiments() -> list[dict]:
    path = LIBRARY_DIR / "experiments.jsonl"
    if not path.exists():
        raise SystemExit(f"No experiments recorded at {path}. Run: python3 -m selflearn experiments")
    rows: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row.get("experiment_id", "")] = row
    return [row for row in rows.values() if row.get("experiment_id")]


def stored_result(row: dict) -> dict:
    """The result the engine recorded, as stored in the row."""
    payload = row.get("result_json") or row.get("result")
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str) and payload.strip().startswith("{"):
        return json.loads(payload)
    return {}


def is_timing(key: str) -> bool:
    lowered = key.casefold()
    return any(marker in lowered for marker in TIMING_KEY_MARKERS)


def compare(stored, fresh, path: str = "") -> tuple[list[str], list[str]]:
    """Walk two result trees; return (differences, ignored wall-clock paths)."""
    differences: list[str] = []
    ignored: list[str] = []
    if isinstance(stored, dict) and isinstance(fresh, dict):
        for key in sorted(set(stored) | set(fresh)):
            child = f"{path}.{key}" if path else key
            if key in COMPARISON_SKIP or is_timing(key):
                if stored.get(key) != fresh.get(key):
                    ignored.append(child)
                continue
            sub_diffs, sub_ignored = compare(stored.get(key), fresh.get(key), child)
            differences.extend(sub_diffs)
            ignored.extend(sub_ignored)
        return differences, ignored
    if stored != fresh:
        differences.append(f"{path or '(root)'}: stored={stored!r} fresh={fresh!r}")
    return differences, ignored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment_id", nargs="?", help="experiment id; defaults to the most recent")
    parser.add_argument("--list", action="store_true", help="list recorded experiments and exit")
    args = parser.parse_args(argv)

    rows = load_experiments()
    rows.sort(key=lambda row: row.get("ran_at", ""), reverse=True)
    if not rows:
        raise SystemExit("No experiments have been recorded yet.")

    if args.list:
        for row in rows:
            print(f"{row['experiment_id']:32} {row.get('status', '?'):12} {row.get('ran_at', '')}")
        return 0

    row = rows[0]
    if args.experiment_id:
        matches = [r for r in rows if r["experiment_id"] == args.experiment_id]
        if not matches:
            raise SystemExit(f"No experiment {args.experiment_id}. Use --list.")
        row = matches[0]

    print(f"experiment : {row['experiment_id']}")
    print(f"hypothesis : {row.get('hypothesis', '')[:160]}")
    print(f"command    : {row.get('command', '(not recorded)')}")

    script = ROOT / (row.get("script_path") or row.get("script") or "")
    if script.exists():
        digest = sha256_text(script.read_text(encoding="utf-8"))
        recorded = row.get("script_sha256", "")
        state = "MATCH" if digest == recorded else "MISMATCH"
        print(f"script hash: {state} (recorded {str(recorded)[:24]}...)")
        if state == "MISMATCH":
            print("             the script changed since the result was recorded; the comparison below is advisory")
    else:
        print(f"script     : missing at {script}")

    command = row.get("command") or ""
    if not command:
        raise SystemExit("The stored row does not record a command, so this experiment cannot be repeated here.")

    fresh_path = ROOT / "state" / f"reproduce-{row['experiment_id']}.json"
    fresh_path.parent.mkdir(parents=True, exist_ok=True)
    # The recorded command points at the temporary directory of the original run, so
    # the --out argument is redirected to a fresh file rather than reused.
    command = re.sub(r"--out\s+\S+", f"--out {fresh_path}", command)
    print(f"re-running : {command}")
    completed = subprocess.run(
        command,
        shell=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=int(row.get("timeout_seconds") or 300),
    )
    if completed.returncode != 0:
        print(completed.stdout[-2000:])
        print(completed.stderr[-2000:])
        return 1
    if not fresh_path.exists():
        raise SystemExit(f"The re-run produced no file at {fresh_path}; nothing to compare.")
    fresh = json.loads(fresh_path.read_text(encoding="utf-8"))
    stored = stored_result(row)
    differences, ignored = compare(stored, fresh)
    print(f"result file: {fresh_path.relative_to(ROOT)}")
    if ignored:
        print(f"ignored    : {len(ignored)} wall-clock field(s), e.g. {', '.join(sorted(set(ignored))[:3])}")
    if differences:
        print("RESULT     : differs from the recorded result")
        for line in differences[:20]:
            print("  -", line)
        return 1
    print("RESULT     : identical to the recorded result on every compared field")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
