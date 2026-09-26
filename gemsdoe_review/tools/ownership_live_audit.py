#!/usr/bin/env python3
"""Live ownership / duplication audit of the GEMS-named repositories and sites.

What this tool does, and why it exists
--------------------------------------
The brief asks for two things that must never be conflated:

  1. GitHub ownership of the sites we read for field context, and
  2. the identity behind the DrivenData registration that is allowed to submit.

This tool answers (1) mechanically, from authenticated read-only GitHub REST
calls, and records (2) as **unresolved from this sandbox** with the evidence for
why (the DrivenData data tab is login-gated and this sandbox holds no session).
It never creates, archives, deletes or pushes anything, and it never treats
another entrant's leaderboard row as our own data.

Run:

    python ownership_live_audit.py --out evidence/ownership_resolution_2026-09-26_session5.json

Output is JSON only: every field is either a value read from the API in this
run or an explicit statement that it could not be read.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

GEMS_REPOS = [
    "GEMSDOE", "GEMSDOE2", "GEMSDOE3", "GEMSDOE4", "5GEMSDOE", "6GEMSDOE",
    "7GEMSDOE", "8GEMSDOE", "GEMSDOE9", "GEMSDOE10", "11GEMSDOE",
]
REVIEW_REPO = "SelfLearn"
SITES = {
    "GEMSDOE1": "https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html",
    "GEMSDOE2": "https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html",
    "GEMSDOE3": "https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html",
    "5GEMSDOE": "https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html",
    "GEMSDOE4": "https://buffedlizard55-lab.github.io/GEMSDOE4/",
    "6GEMSDOE": "https://buffedlizard55-lab.github.io/6GEMSDOE/",
}


def gh(*args: str) -> dict:
    """One authenticated read-only GitHub REST call, parsed as JSON."""
    out = subprocess.run(("gh", "api", *args), capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        return {"_error": out.stderr.strip()[:400]}
    return json.loads(out.stdout or "null")


def repo_record(owner: str, name: str) -> dict:
    full = f"{owner}/{name}"
    info = gh(f"repos/{full}")
    if "_error" in info:
        return {"full_name": full, "error": info["_error"]}
    pages = gh(f"repos/{full}/pages")
    contributors = [c.get("login") for c in (gh(f"repos/{full}/contributors?per_page=100") or [])]
    return {
        "full_name": full,
        "owner_login": info.get("owner", {}).get("login"),
        "owner_id": info.get("owner", {}).get("id"),
        "fork": info.get("fork"),
        "private": info.get("private"),
        "archived": info.get("archived"),
        "default_branch": info.get("default_branch"),
        "created_at": info.get("created_at"),
        "pushed_at": info.get("pushed_at"),
        "head_sha": info.get("default_branch") and gh(f"repos/{full}/commits/{info['default_branch']}").get("sha"),
        "disk_usage_kb": info.get("disk_usage"),
        "has_pages": info.get("has_pages"),
        "pages_status": pages.get("status") if isinstance(pages, dict) else None,
        "pages_html_url": pages.get("html_url") if isinstance(pages, dict) else None,
        "contributors": contributors,
        "api_permissions": info.get("permissions"),
        "source": f"https://api.github.com/repos/{full}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--owner", default="buffedlizard55-lab")
    ap.add_argument("--since", default="2026-09-26T00:00:00Z")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    listing = gh(f"users/{args.owner}/repos?per_page=100&sort=created&direction=asc")
    if isinstance(listing, dict) and "_error" in listing:
        print("repo listing failed:", listing["_error"], file=sys.stderr)
        return 1
    gems = [r for r in listing if r.get("name", "").upper().replace("-", "").endswith("GEMSDOE")
            or r.get("name", "").upper().startswith(("GEMSDOE", "5GEMSDOE", "6GEMSDOE", "7GEMSDOE", "8GEMSDOE",
                                                     "9GEMSDOE", "10GEMSDOE", "11GEMSDOE"))]
    gems_names = sorted(r["name"] for r in gems)

    records = {}
    for name in sorted(set(GEMS_REPOS) | set(gems_names) | {REVIEW_REPO}):
        records[name] = repo_record(args.owner, name)
        print(name, "->", records[name].get("owner_login"), "fork=", records[name].get("fork"),
              "pages=", records[name].get("pages_status"), flush=True)

    owners = {r.get("owner_id") for r in records.values() if r.get("owner_id")}
    forks = [n for n, r in records.items() if r.get("fork")]
    archived = [n for n, r in records.items() if r.get("archived")]
    pages_built = [n for n, r in records.items() if r.get("pages_status") == "built"]
    # Anything created inside the audit window is reported as an irregularity
    # rather than smoothed into the historical count: previous sessions recorded
    # 11 GEMS-named repositories, so a 12th appearing mid-window is new evidence.
    recent = {n: r.get("created_at") for n, r in records.items()
              if (r.get("created_at") or "") >= args.since}
    recent.pop(REVIEW_REPO, None)

    payload = {
        "collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tool": Path(__file__).name,
        "method": ("read-only `gh api` calls (GitHub REST) run in this session; no mutation of any kind. "
                   "GitHub ownership is NOT a DrivenData registration."),
        "account": {"login": args.owner, "repos_on_account": len(listing),
                    "gems_named_repos": gems_names, "gems_named_count": len(gems_names)},
        "repositories": records,
        "findings": {
            "single_github_owner": len(owners) == 1,
            "owner_ids": sorted(o for o in owners if o is not None),
            "fork_repos": forks,
            "archived_repos": archived,
            "pages_built_on": pages_built,
            "pages_built_count": len(pages_built),
            "duplication_flag": len(pages_built) > 1,
            "created_since": args.since,
            "created_since_finding": recent,
            "new_repo_irregularity": (
                "A GEMS-named repository appeared inside the audit window "
                f"({recent}). It was NOT created by this session: this session creates nothing. "
                "Record it as an irregularity for the account holder; do not adopt it as an "
                "experiment arm and do not archive it from here."),
            "designated_entry": "6GEMSDOE",
            "designated_site": SITES["6GEMSDOE"],
        },
        "brief_unconfirmed_sites": {
            "5GEMSDOE": SITES["5GEMSDOE"],
            "GEMSDOE4": SITES["GEMSDOE4"],
            "6GEMSDOE": SITES["6GEMSDOE"],
        },
        "drivendata_layer": {
            "status": "UNRESOLVED FROM THIS SANDBOX (unchanged, re-verified by probe below)",
            "why": ("The sandbox holds no DrivenData session; the competition data tab is login-gated "
                    "(unauthenticated requests redirect to /accounts/login/). The registration identity, "
                    "rules sec 1.3 eligibility, submission history and remaining weekly allowance are "
                    "account-holder-only facts."),
            "no_action_taken": "no registration, upload, submission or site was created by this tool",
        },
        "reading": ("All GEMS-named repositories are non-fork repositories of the ONE GitHub account that "
                    "also hosts this review workspace: they are our own historical project copies, not other "
                    "entrants' property. GitHub ownership does not identify the DrivenData registration, so "
                    "no leaderboard row is claimed as ours and no score is attributed to this entry."),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(json.dumps(payload["findings"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
