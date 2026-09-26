#!/usr/bin/env python3
"""Re-check the numbers the canonical GEMSDOE entry publishes against its artifacts.

The entry repo (`buffedlizard55-lab/6GEMSDOE`) writes its numbers into prose
(`EXECUTIVE_SUMMARY.md`, `SUBMISSION_GUIDE.md`, `README.md`, `ACCOUNT_STATUS.md`)
and into a generated site (`index.html`, `verification.html`, `research.html`).
`scripts/build_site.py` renders the site from `data/evidence/*.json`, so the site
cannot drift from the evidence — but the *prose* is typed by hand, and the
evidence itself is only as good as the last run. Nothing in the repo re-reads the
shipped GeoTIFF and compares it with the sentences that describe it.

This script does exactly that, and it is meant to be run before any upload:

    python tools/check_entry_docs.py /path/to/6GEMSDOE
    python tools/check_entry_docs.py /path/to/6GEMSDOE --online   # + GitHub API

Exit code 0 = every checked claim matched, 1 = at least one did not. A failure is
a finding, not a warning: the brief for this review says explicitly that the
executive summary and the submit instructions have to still be accurate.

It deliberately does NOT need the 419 MB feature raster: everything checked here
is either committed in the entry repo or re-measurable from the two small rasters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RESULTS: list[tuple[bool, str, str]] = []


def check(ok: bool, name: str, detail: str) -> bool:
    RESULTS.append((bool(ok), name, detail))
    return bool(ok)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("entry", help="path to a 6GEMSDOE checkout")
    ap.add_argument("--online", action="store_true",
                    help="also re-read the GitHub account inventory")
    args = ap.parse_args()
    root = Path(args.entry).resolve()
    if not (root / "src" / "gems" / "spec.py").exists():
        print(f"not a 6GEMSDOE checkout: {root}", file=sys.stderr)
        return 2

    sys.path.insert(0, str(root / "src"))
    from gems import spec  # noqa: E402
    from gems import raster  # noqa: E402

    # ---- 1. the shipped file, re-read from its bytes ------------------------
    rep = json.loads((root / "data" / "evidence" / "submission_report.json").read_text())
    sub = root / "downloads" / rep["file"]
    check(sub.exists(), "shipped-file-present", f"{sub.name}")
    if sub.exists():
        got = sha256(sub)
        check(got == rep["sha256"], "shipped-file-sha256",
              f"report {rep['sha256'][:16]}…  actual {got[:16]}…")
        check(sub.stat().st_size == rep["bytes"], "shipped-file-bytes",
              f"report {rep['bytes']}  actual {sub.stat().st_size}")
        gate = raster.check_submission(sub)
        check(gate.ok, "gate-recheck",
              "; ".join(f"{c.name}={'PASS' if c.ok else 'FAIL'}"
                        for c in gate.checks if not c.ok) or "all checks PASS")
        stats = gate.stats
        check(stats.get("positive_pixels") == 155_021, "positive-pixels",
              f"measured {stats.get('positive_pixels')}, documented 155,021")
        check(stats.get("finite_pixels") == spec.FOOTPRINT_PIXELS,
              "finite-pixels-equal-footprint",
              f"measured {stats.get('finite_pixels')}, pinned {spec.FOOTPRINT_PIXELS}")
        check(stats.get("nan_inside_footprint") == 0, "no-nan-inside-footprint",
              f"measured {stats.get('nan_inside_footprint')}")
        check(stats.get("finite_min") == 0.0 and stats.get("finite_max") == 1.0,
              "value-range", f"[{stats.get('finite_min')}, {stats.get('finite_max')}]")
        check(rep.get("n_channels") == 88, "report-channels",
              f"submission_report n_channels = {rep.get('n_channels')}")

    # ---- 2. the pinned official rasters -------------------------------------
    for name, pin in spec.PINS.items():
        p = root / "data" / name
        if name == "training_features.tif":
            if not p.exists():
                check(True, f"pin-{name}", "not present (gitignored, fetched on demand)")
                continue
        if not p.exists():
            check(False, f"pin-{name}", f"{p} missing")
            continue
        got = sha256(p)
        check(got == pin["sha256"] and p.stat().st_size == pin["bytes"],
              f"pin-{name}",
              f"{p.stat().st_size} B, {got[:16]}… vs pin {pin['bytes']} B, "
              f"{pin['sha256'][:16]}…")

    # ---- 3. the bridge manifest agrees with the pins -------------------------
    man = root / "data" / "bridge" / "manifest.json"
    if man.exists():
        m = json.loads(man.read_text())
        by_canon = {f["canonical"]: f for f in m.get("files", [])}
        for canon, pin in spec.PINS.items():
            f = by_canon.get(canon)
            check(f is not None and f["sha256"] == pin["sha256"],
                  f"manifest-{canon}",
                  "absent from manifest" if f is None else
                  ("hash matches the spec pin" if f["sha256"] == pin["sha256"]
                   else f"manifest {f['sha256'][:16]}… vs spec {pin['sha256'][:16]}…"))
        tf = by_canon.get("training_features.tif")
        if tf:
            check([p["sha256"] for p in tf["parts"]] ==
                  [s for _, _, s in spec.BRIDGE_PARTS],
                  "manifest-bridge-parts",
                  f"{len(tf['parts'])} parts listed")
    else:
        check(False, "manifest-present", f"{man} missing")

    # ---- 4. the prose numbers are in the evidence ---------------------------
    docs = {p.name: read_text(p) for p in root.glob("*.md")}
    docs["index.html"] = read_text(root / "index.html")
    blob = "\n".join(docs.values())
    ev = {}
    for f in (root / "data" / "evidence").glob("*.json"):
        try:
            ev[f.name] = f.read_text()
        except Exception:
            pass
    ev_blob = "\n".join(ev.values())

    def find_number(x: float) -> bool:
        pats = {f"{x:.4f}", f"{x:.3f}", f"{x:.2f}", f"{x:g}"}
        return any(p in ev_blob for p in pats)

    for value, why in [
        (0.1698, "shipped blocked-CV mean DTI"),
        (0.1119, "previous blocked-CV mean DTI"),
        (0.1750, "5% budget on the full catalogue"),
        (0.1589, "2% budget on the full catalogue"),
        (0.1278, "3% budget at 50% of traces"),
        (0.0631, "3% budget at 25% of traces"),
        (0.1628, "extended config without the extra channels"),
        (0.1637, "best lineament post-processing variant"),
    ]:
        check(find_number(value), f"prose-number-{value}",
              f"{why}: {'found' if find_number(value) else 'NOT found'} in "
              f"data/evidence/*.json ({why})")

    for token, why in [("33cec71ff0", "shipped sha prefix"),
                       ("5,167,373", "footprint"),
                       ("60,988", "catalogue positives")]:
        check(token in blob, f"token-{token}", f"{why}: "
              f"{'present' if token in blob else 'not present'} in the prose")

    # The brief attributes five leaderboard scores to this account's repositories.
    # This session resolved every one of them to a *different* DrivenData
    # participant with a single submission (see evidence/leaderboard_snapshot.json),
    # so the correct state of the entry's prose is that it does NOT quote any of
    # them as ours. If one ever appears, this check fails and a human must say
    # where it came from.
    for score, who in [("0.1563", "extradr19"), ("0.1560", "smashi34"),
                       ("0.1193", "smrtdoog5"), ("0.1152", "SDCF9"),
                       ("0.0830", "wbg1")]:
        check(score not in blob.replace("0.1563", "", 0) or True,
              f"unclaimed-board-score-{score}",
              f"attributed by the brief to {who}; present in this entry's prose: "
              f"{score in blob}")
        if score in blob:
            check(False, f"board-score-adopted-{score}",
                  f"the entry's prose states {score}, which belongs to participant "
                  f"{who}; it must not be presented as this entry's score")

    check("1,652,883" in blob or "1652883" in blob, "prose-shipped-bytes",
          "the shipped file size is stated in the prose")

    # ---- 5. the account table, optionally against the live API --------------
    acct = read_text(root / "ACCOUNT_STATUS.md")
    if args.online:
        try:
            out = subprocess.run(
                ["gh", "repo", "list", "buffedlizard55-lab", "--limit", "200",
                 "--json", "name,diskUsage,pushedAt,hasPages"],
                capture_output=True, text=True, check=True).stdout
            live = {r["name"]: r for r in json.loads(out)}
        except Exception as exc:  # pragma: no cover
            check(False, "github-inventory", f"gh failed: {exc}")
            live = {}
        g = [n for n in live if re.search(r"GEMSDOE", n, re.I)]
        check(len(g) == 11, "account-repo-count",
              f"live inventory has {len(g)} GEMS-named repositories: "
              f"{sorted(g)}")
        check(all(live[n].get("hasPages") for n in g), "account-pages",
              "Pages enabled on: "
              f"{sorted(n for n in g if live[n].get('hasPages'))}")
        for name in g:
            check(name in acct, f"account-table-{name}",
                  f"{name} listed in ACCOUNT_STATUS.md")
    else:
        check("eleven" in acct, "account-table-prose",
              "ACCOUNT_STATUS.md states the repository count (not re-verified; "
              "run with --online)")

    # ---- 6. the NEXT_STEPS items that the brief asked about ------------------
    ml = read_text(root / "LIMITATIONS.md")
    check("masked" in ml or "mask" in ml, "limitations-cover-masking",
          "LIMITATIONS.md discusses the masking rule verified 2026-09-26")
    check((root / "NEXT_STEPS.md").exists(), "next-steps-present", "NEXT_STEPS.md")
    check((root / "data" / "evidence" / "geology_dossier.md").exists(),
          "geology-dossier-present",
          "the per-candidate geological write-up exists (NEXT_STEPS item 9)")

    # ---- report -------------------------------------------------------------
    bad = [r for r in RESULTS if not r[0]]
    width = max(len(r[1]) for r in RESULTS)
    for ok, name, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name:<{width}}  {detail}")
    print()
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} checks passed")
    if bad:
        print("\nENTRY DOCS DO NOT MATCH THE ARTIFACTS — fix before uploading.")
        return 1
    print("\nENTRY DOCS MATCH THE ARTIFACTS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
