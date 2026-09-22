"""Command line interface.

    python -m selflearn run [--mode live|snapshot|fixture] [--topics N] [--offline]
    python -m selflearn audit
    python -m selflearn site
    python -m selflearn sources [--probe]
    python -m selflearn scan [--query TEXT] [--sources ids] [--days N] [--discover]
    python -m selflearn credentials
    python -m selflearn storage {sync|verify|status} [--database DSN]
    python -m selflearn retrieve QUERY [-k N]
    python -m selflearn experiments [--id ID]
    python -m selflearn calibrate
    python -m selflearn status
    python -m selflearn selftest

Every command works offline except ``run --mode live`` and ``sources --probe``,
and both degrade to a recorded gap rather than an exception.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from . import ENGINE_REPO_URL, __version__
from .config import CALIBRATION_STATE, EVIDENCE_HIERARCHY, FIXTURE_DIR, ROOT, SITE_DIR, STATE_DIR
from .experiment.catalogue import EXPERIMENTS, catalogue, get_experiment
from .experiment.runner import run_experiment
from .fetch.net import HttpClient, NetworkUnavailable
from .fetch.registry import REGISTRY, registry_summary, source_matrix
from .learn.calibration import run_calibration, thresholds_in_force
from .learn.store import Library
from .models import Irregularity, SourceStatus
from .publish.report import build_site_data
from .publish.site import build_site
from .think.elo import EloTable
from .util import load_json, save_json, slugify, stable_id, utcnow_iso
from .verify.audit import check_coverage, check_fixtures, check_links, recheck_claims, render_markdown, summarise


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    from .loop import run_cycle

    allow_network = args.mode != "fixture" and not args.offline
    result = run_cycle(
        root=ROOT,
        mode=args.mode,
        max_topics=args.topics,
        max_requests=args.max_requests,
        allow_network=allow_network,
        publish=not args.no_publish,
        run_experiments=not args.skip_experiments,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    errors = summarise(result.irregularities)["by_severity"].get("error", 0)
    return 0 if errors == 0 else 0  # irregularities are expected output, not failure


def cmd_audit(args: argparse.Namespace) -> int:
    """Re-verify the whole library against its stored snapshots.

    The report written here is the full picture a reviewer needs: the findings
    already stored on the library (including anything a reviewer resolved)
    merged with whatever this audit re-detected. Writing only the fresh audit
    rows - as this command used to do - replaced the cycle's published warning
    list with a single info line, so ``reports/irregularities.md`` disagreed
    with the review page built from the same library.
    """
    from .verify.audit import merge_findings

    library = Library.load(ROOT, run_id="audit")
    snapshots = ROOT / "evidence" / "snapshots"
    claims = list(library.claims.values())
    fresh: list[Irregularity] = []
    fresh.extend(recheck_claims(claims, snapshots))
    fresh.extend(check_links(claims))
    fresh.extend(check_fixtures(library.evidence.values(), claims))
    fresh.extend(check_coverage(library.active_topics(), claims, []))
    findings = merge_findings(list(library.irregularities.values()) + fresh)
    fresh_stats = summarise(fresh)
    stats = summarise(findings)
    print(f"claims re-checked: {len(claims)}")
    print(f"documents on file: {len(library.evidence)}")
    print("findings (this audit): " + json.dumps(fresh_stats["by_severity"]))
    print("findings (published, merged): " + json.dumps(stats["by_severity"]))
    for finding in sorted(findings, key=lambda f: f.severity)[: args.limit]:
        print(f"  [{finding.severity}] {finding.stage}: {finding.summary}")
    if args.write:
        (ROOT / "reports").mkdir(parents=True, exist_ok=True)
        (ROOT / "reports" / "irregularities.md").write_text(
            render_markdown(findings, generated_at=utcnow_iso()), encoding="utf-8"
        )
        print("wrote reports/irregularities.md")
    # The exit status reflects this audit's own re-verification only: stored
    # findings are published output, not a reason for a scheduled run to fail.
    return 0 if fresh_stats["by_severity"].get("error", 0) == 0 else 1


def cmd_site(args: argparse.Namespace) -> int:
    """Rebuild the site from the stored library and the last calibration.

    Per-source reachability is measured by a cycle, not stored in the library, so
    the rebuild reads it back from the ``reports/site_data.json`` the last cycle
    wrote. Without that, every manual rebuild published an empty sources table and
    "0 of N reachable" for a run that had in fact reached something.
    """
    library = Library.load(ROOT, run_id="site-rebuild")
    calibration = run_calibration(FIXTURE_DIR / "verification_cases.jsonl", apply=False) if (FIXTURE_DIR / "verification_cases.jsonl").exists() else {}
    last_cycle = load_json(ROOT / "reports" / "site_data.json", {}) or {}
    recorded_status = [
        SourceStatus(**{k: v for k, v in row.items() if k in SourceStatus.__dataclass_fields__})
        for row in ((last_cycle.get("sources") or {}).get("status") or [])
        if isinstance(row, dict) and row.get("source_id")
    ]
    mode = args.mode or str(last_cycle.get("mode") or "snapshot")
    data = build_site_data(
        library,
        source_matrix=source_matrix(),
        source_status=recorded_status,
        irregularities=list(library.irregularities.values()),
        failures=list(library.failures.values()),
        # The state file stores ratings and match history; the pages read the
        # derived leaderboard. Loading the table and calling to_dict() is what
        # the cycle does, and passing the raw file emptied the standings table
        # on every manual rebuild.
        elo_payload=EloTable.load(STATE_DIR / "elo.json").to_dict(),
        calibration=calibration or thresholds_in_force(CALIBRATION_STATE),
        requirements=load_json(ROOT / "data" / "requirements.json", []) or [],
        methodology={
            "engine_version": __version__,
            "evidence_hierarchy": [
                {"rank": rank, "name": name, "description": description} for rank, name, description in EVIDENCE_HIERARCHY
            ],
            "thresholds": thresholds_in_force(CALIBRATION_STATE),
        },
        mode=mode,
        run_summary=load_json(ROOT / "reports" / "run_summary.json", {}) or {},
    )
    data["experiment_catalogue"] = catalogue()
    if last_cycle.get("run_id"):
        # The pages name the run whose evidence they show, not the rebuild.
        data["run_id"] = last_cycle["run_id"]
    written = build_site(data, SITE_DIR, write_root_entry=True)
    print(f"wrote {len(written)} file(s) to {SITE_DIR}")
    if recorded_status:
        print(f"source reachability carried over from cycle {last_cycle.get('run_id')} ({len(recorded_status)} status row(s), mode {mode})")
    else:
        print("no recorded cycle found in reports/site_data.json; the sources table shows no reachability")
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    """Print the register, and optionally probe reachability."""
    matrix = source_matrix()
    if not args.probe:
        for spec in matrix:
            key = "key:" + (spec.get("key_env") or "") if spec.get("requires_key") else "open"
            print(f"{spec['source_id']:18} rank {spec['evidence_rank']} {spec['evidence_class']:18} {key:22} {spec['docs_url']}")
        print(json.dumps(registry_summary(), indent=2, sort_keys=True))
        return 0

    client = HttpClient(max_requests=args.max_requests)
    reachable, unreachable, skipped = [], [], []
    for source_id in sorted(REGISTRY):
        spec = REGISTRY[source_id]
        if spec.requires_key and not _has_credential(spec):
            skipped.append(source_id)
            continue
        url = args.url or spec.base_url
        try:
            result = client.get(url)
            reachable.append((source_id, result.status, len(result.body)))
            print(f"reachable   {source_id:18} HTTP {result.status} {len(result.body)} bytes")
        except NetworkUnavailable as exc:
            unreachable.append((source_id, str(exc)[:80]))
            print(f"unreachable {source_id:18} {str(exc)[:90]}")
        except Exception as exc:  # HttpError and friends: reachable but unhappy
            unreachable.append((source_id, str(exc)[:80]))
            print(f"error       {source_id:18} {str(exc)[:90]}")
    print(json.dumps({"reachable": len(reachable), "unreachable": len(unreachable), "credential_required": skipped}, indent=2))
    return 0


def _has_credential(spec) -> bool:
    import os

    names = [spec.key_env] if spec.key_env else []
    if spec.source_id == "github":
        names += ["GITHUB_TOKEN", "GH_TOKEN"]
    return any(os.environ.get(name) for name in names if name)


def cmd_experiments(args: argparse.Namespace) -> int:
    specs = [get_experiment(args.id)] if args.id else list(EXPERIMENTS)
    failed = 0
    for spec in specs:
        run = run_experiment(spec, root=ROOT)
        status = run.status if not run.error else "failed"
        print(f"{spec.experiment_id:32} {status:14} {run.duration_seconds:6.2f}s  {run.error}")
        if args.json:
            print(json.dumps(run.to_dict(), indent=2, sort_keys=True))
        if run.error:
            failed += 1
    return 1 if failed else 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    payload = run_calibration(FIXTURE_DIR / "verification_cases.jsonl", apply=False, state_path=STATE_DIR / "calibration.json")
    selected = payload.get("selected") or {}
    print(json.dumps({
        "cases": payload.get("case_count"),
        "selected": selected.get("thresholds"),
        "accuracy": selected.get("accuracy"),
        "macro_f1": selected.get("macro_f1"),
        "false_supports": selected.get("false_supports"),
        "baseline": (payload.get("baseline") or {}).get("thresholds"),
        "baseline_accuracy": (payload.get("baseline") or {}).get("accuracy"),
        "excluded_cases": [row.get("case_id") for row in payload.get("excluded_cases", [])],
    }, indent=2, sort_keys=True))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    library = Library.load(ROOT, run_id="status")
    total_topics = len(library.topics)
    active_topics = len(library.active_topics())
    print(json.dumps(
        {
            # "topics" is the whole stream, including rejected proposals whose
            # history is kept; "topics_active" is what the site's table counts.
            # Both are printed so the two published numbers cannot be mistaken
            # for a contradiction.
            "topics": total_topics,
            "topics_active": active_topics,
            "topics_rejected": total_topics - active_topics,
            "claims": len(library.claims),
            "documents": len(library.evidence),
            "strategies": len(library.strategies),
            "attacks": len(library.attacks),
            "questions": len(library.questions),
            "experiments": len(library.experiments),
            "irregularities": len(library.irregularities),
            "contradictions": len(library.contradictions),
            "thresholds": thresholds_in_force(CALIBRATION_STATE).get("in_force"),
        },
        indent=2,
        sort_keys=True,
    ))
    if args.topics_list:
        for topic in sorted(library.topics.values(), key=lambda t: t.topic_id):
            claims = library.claims_for_topic(topic.topic_id)
            supported = sum(1 for c in claims if c.verification.verdict == "supported")
            print(f"  {topic.topic_id:16} {topic.status:12} claims={len(claims):<4} verified={supported:<4} {topic.title}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    """Poll the sources that publish a documented change filter.

    Reports, per source, the window used, the request made, how many items came
    back and how many the engine had not seen before. Nothing is published as a
    finding here; with ``--discover`` the new items become questions in the
    library, each naming the item it came from.
    """
    from .fetch.changes import ChangeScanner, mechanism_table, summarise_scan

    client = HttpClient(max_requests=args.max_requests, allow_network=not args.offline)
    scanner = ChangeScanner(client, STATE_DIR / "change_scan.json", allow_network=not args.offline)
    targets = [s.strip() for s in args.sources.split(",") if s.strip()] if args.sources else None
    outcome = scanner.scan(
        args.query,
        source_ids=targets,
        window_days=args.days,
        limit=args.limit,
        run_id=f"scan-{utcnow_iso()[:10]}",
    )
    for scan in outcome.scans:
        print(
            f"{scan.status:12} {scan.source_id:16} {scan.items_seen:4} item(s), {scan.items_new:4} new   "
            f"{scan.window.get('since')}..{scan.window.get('until')}"
        )
        if scan.detail:
            print(f"             {scan.detail[:150]}")
    print(json.dumps(summarise_scan(outcome), indent=2, sort_keys=True))

    (ROOT / "reports").mkdir(parents=True, exist_ok=True)
    save_json(ROOT / "reports" / "change_scan.json", outcome.to_dict())
    print("wrote reports/change_scan.json")

    if args.discover and outcome.items_new:
        from .models import Discovery, Question

        library = Library.load(ROOT, run_id=f"scan-{utcnow_iso()[:10]}")
        questions: list[Question] = []
        discoveries: list[Discovery] = []
        for scan in outcome.scans:
            for row in scan.new_items[: args.limit]:
                text = (
                    f"{scan.source_name} published or updated \"{row['title']}\" inside the window "
                    f"{scan.window.get('since')}..{scan.window.get('until')} "
                    f"({row['url'] or scan.request_url}). What does it change about what this library holds?"
                )
                questions.append(
                    Question(
                        id=stable_id("q", "scan", row["identifier"]),
                        topic_id="",
                        text=text,
                        origin="discovery",
                        priority=0.6,
                    )
                )
                discoveries.append(
                    Discovery(
                        discovery_id=stable_id("disc", "scan", row["identifier"]),
                        topic_id="",
                        text=text,
                        kind="finding",
                        derived_from=[row["identifier"]],
                        confidence="low",
                    )
                )
        library.add_questions(questions)
        library.add_discoveries(discoveries)
        print(f"recorded {len(questions)} question(s) and {len(discoveries)} finding(s) from the scan")

    for finding in outcome.irregularities:
        print(f"[{finding.severity}] {finding.summary}")
    return 0


def cmd_credentials(args: argparse.Namespace) -> int:
    """Report which keyed sources could be enabled, and how.

    The engine never calls a keyed API without a key and never guesses one. This
    command exists so the gap is a checklist rather than a mystery. It answers two
    different questions, because they have different answers:

    1. **required** - sources the engine refuses to call without a credential;
    2. **whether the credential is actually used** - a variable can be set and
       still never reach the request, if the operator's documented way of
       transmitting it has not been transcribed into the adapter. Reporting the
       mechanism beside the variable is what keeps "the key is set" from being
       read as "the key is being used".
    """
    import os

    from .fetch.sources import credential_status

    required: list[dict[str, object]] = []
    optional: list[dict[str, object]] = []
    for spec in sorted(REGISTRY.values(), key=lambda s: s.source_id):
        if not spec.key_env:
            continue
        status = credential_status(spec)
        row = {
            "source_id": spec.source_id,
            "name": spec.name,
            "env": spec.key_env,
            "present": bool(os.environ.get(spec.key_env)),
            "required": spec.requires_key,
            "mechanism_state": status["state"],
            "mechanism": status["detail"],
            "key_url": spec.key_url,
            "docs_url": spec.docs_url,
            "rate_limit_note": spec.rate_limit_note,
        }
        (required if spec.requires_key else optional).append(row)

    for title, rows in (("REQUIRED - the engine will not call these without a credential", required),
                        ("OPTIONAL - raises the operator's rate limit; the source works without one", optional)):
        print(title)
        for row in rows:
            state = "present" if row["present"] else "MISSING"
            used = "used" if row["mechanism_state"] == "applied" else "NOT USED BY THE ADAPTER"
            print(f"  {state:8} {str(row['env']):22} {str(row['source_id']):16} {used:22} {row['key_url'] or row['docs_url']}")
        if not rows:
            print("  none")
        print()

    declared_only = [row for row in required + optional if row["mechanism_state"] == "declared_only"]
    print(
        json.dumps(
            {
                "keyed_sources": len(required) + len(optional),
                "required": len(required),
                "enabled": sum(1 for r in required + optional if r["present"]),
                "missing_required": [str(r["env"]) for r in required if not r["present"]],
                "credential_transmitted": sorted(str(r["source_id"]) for r in required + optional if r["mechanism_state"] == "applied"),
                "declared_but_not_transmitted": sorted(str(r["source_id"]) for r in declared_only),
                "how_to_enable": (
                    "Add each name above as a repository secret under Settings > Secrets and variables > "
                    "Actions; .github/workflows/research-loop.yml already passes them into the cycle when set."
                ),
                "note": (
                    "`credential_transmitted` lists the sources whose operator documents how the credential is "
                    "sent and whose adapter sends it. `declared_but_not_transmitted` lists the sources whose "
                    "variable is named in the register but whose documented mechanism has not been transcribed, "
                    "so setting the variable would change nothing."
                ),
                "sources": required + optional,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def cmd_selftest(args: argparse.Namespace) -> int:
    import unittest

    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    outcome = runner.run(suite)
    return 0 if outcome.wasSuccessful() else 1


def cmd_storage(args: argparse.Namespace) -> int:
    """Mirror the JSONL library into a database and prove the views agree.

    Actions:

    ``sync``    append every stored row the database does not already hold;
                idempotent, append-only, JSONL stays the source of truth.
    ``verify``  compare the JSONL mirror against the database - the raw rows
                stream by stream, and the records decoded from them - and
                exit non-zero unless both agree.
    ``status``  row counts per stream in the database.
    """
    from .storage import (
        connect,
        count_rows,
        dsn_from_environment,
        ensure_schema,
        sync_library,
        verify_views,
    )

    dsn = dsn_from_environment(args.database)
    try:
        connection = connect(dsn)
    except (RuntimeError, ValueError) as exc:
        print(f"storage {args.action}: {exc}", file=sys.stderr)
        return 2
    try:
        if args.action == "sync":
            ensure_schema(connection)
            report = sync_library(ROOT, connection)
            print(json.dumps({"database": dsn, **report}, indent=2, sort_keys=True))
            return 0
        if args.action == "verify":
            report = verify_views(ROOT, connection, dsn=dsn)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report.get("rows_identical") and report.get("library_identical") else 1
        # status
        print(json.dumps({"database": dsn, "rows_by_stream": count_rows(connection)}, indent=2, sort_keys=True))
        return 0
    finally:
        connection.close()


def cmd_retrieve(args: argparse.Namespace) -> int:
    """Search the current claims with the TF-IDF vector index (no model)."""
    from .learn.vector_index import VectorIndex

    library = Library.load(ROOT, run_id="retrieve")
    current = [claim for claim in library.claims.values() if not claim.superseded]
    index = VectorIndex.build(current)
    hits = index.search(args.query, k=args.k)
    rows = []
    for claim_id, score in hits:
        claim = library.claims[claim_id]
        rows.append(
            {
                "claim_id": claim_id,
                "score": round(score, 6),
                "topic_id": claim.topic_id,
                "verdict": claim.verification.verdict,
                "evidence_class": claim.evidence_class,
                "text": claim.text[:220],
                "url": claim.url,
            }
        )
    print(
        json.dumps(
            {
                "query": args.query,
                "indexed_claims": len(current),
                "retired_excluded": len(library.claims) - len(current),
                "hits": rows,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="selflearn",
        description=(
            "SelfLearn - an autonomous research engine that only publishes what it can quote from a retrieved "
            f"document. Repository: {ENGINE_REPO_URL}"
        ),
    )
    parser.add_argument("--version", action="version", version=f"SelfLearn {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="log every HTTP request and decision")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run one research cycle and publish the site")
    run.add_argument("--mode", choices=("live", "snapshot", "fixture"), default="live")
    run.add_argument("--topics", type=int, default=None, help="maximum questions to work this cycle")
    run.add_argument("--max-requests", type=int, default=None, dest="max_requests")
    run.add_argument("--offline", action="store_true", help="refuse network access; replay stored snapshots only")
    run.add_argument("--no-publish", action="store_true", dest="no_publish")
    run.add_argument("--skip-experiments", action="store_true", dest="skip_experiments")
    run.set_defaults(func=cmd_run)

    audit = sub.add_parser("audit", help="re-verify every stored claim against its snapshot")
    audit.add_argument("--limit", type=int, default=40)
    audit.add_argument("--no-write", action="store_false", dest="write", default=True)
    audit.set_defaults(func=cmd_audit)

    site = sub.add_parser("site", help="rebuild the published site from stored data")
    site.add_argument(
        "--mode", choices=("live", "snapshot", "fixture"), default=None,
        help="label for the rebuilt pages; defaults to the mode of the last recorded cycle, or 'snapshot' if none",
    )
    site.set_defaults(func=cmd_site)

    sources = sub.add_parser("sources", help="list the source register, optionally probing reachability")
    sources.add_argument("--probe", action="store_true")
    sources.add_argument("--url", default=None, help="probe a single URL instead of each base URL")
    sources.add_argument("--max-requests", type=int, default=40, dest="max_requests")
    sources.set_defaults(func=cmd_sources)

    experiments = sub.add_parser("experiments", help="run catalogue experiments")
    experiments.add_argument("--id", default=None)
    experiments.add_argument("--json", action="store_true")
    experiments.set_defaults(func=cmd_experiments)

    calibrate = sub.add_parser("calibrate", help="sweep verification thresholds against the labelled cases")
    calibrate.set_defaults(func=cmd_calibrate)

    status = sub.add_parser("status", help="print library counts")
    status.add_argument("--topics", action="store_true", dest="topics_list")
    status.set_defaults(func=cmd_status)

    scan = sub.add_parser("scan", help="poll the sources that publish a documented change filter")
    scan.add_argument("--query", default="research", help="search terms for the change query")
    scan.add_argument("--sources", default=None, help="comma-separated source ids (default: all with a mechanism)")
    scan.add_argument("--days", type=int, default=7, help="maximum look-back window in days")
    scan.add_argument("--limit", type=int, default=10, help="items requested per source")
    scan.add_argument("--max-requests", type=int, default=20, dest="max_requests")
    scan.add_argument("--offline", action="store_true", help="record the window without polling")
    scan.add_argument("--discover", action="store_true", help="turn new items into library questions")
    scan.set_defaults(func=cmd_scan)

    credentials = sub.add_parser("credentials", help="show which keyed sources are enabled and how to enable them")
    credentials.set_defaults(func=cmd_credentials)

    storage = sub.add_parser(
        "storage",
        help="mirror the JSONL library into SQLite/PostgreSQL and verify the two views agree",
    )
    storage.add_argument("action", choices=("sync", "verify", "status"))
    storage.add_argument(
        "--database",
        default=None,
        help="DSN: sqlite:///path.db or postgres://... (default: $SELFLEARN_DATABASE_URL or sqlite:///state/library.sqlite3)",
    )
    storage.set_defaults(func=cmd_storage)

    retrieve = sub.add_parser("retrieve", help="search current claims with the TF-IDF vector index")
    retrieve.add_argument("query", help="the words to search for")
    retrieve.add_argument("-k", type=int, default=10, help="how many claims to return")
    retrieve.set_defaults(func=cmd_retrieve)

    selftest = sub.add_parser("selftest", help="run the test suite")
    selftest.set_defaults(func=cmd_selftest)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.verbose)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:  # pragma: no cover
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
