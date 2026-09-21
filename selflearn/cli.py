"""Command line interface.

    python -m selflearn run [--mode live|snapshot|fixture] [--topics N] [--offline]
    python -m selflearn audit
    python -m selflearn site
    python -m selflearn sources [--probe]
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
from .publish.report import build_site_data
from .publish.site import build_site
from .util import load_json, save_json, slugify, utcnow_iso
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
    """Re-verify the whole library against its stored snapshots."""
    library = Library.load(ROOT, run_id="audit")
    snapshots = ROOT / "evidence" / "snapshots"
    claims = list(library.claims.values())
    findings = []
    findings.extend(recheck_claims(claims, snapshots))
    findings.extend(check_links(claims))
    findings.extend(check_fixtures(library.evidence.values(), claims))
    findings.extend(check_coverage(library.active_topics(), claims, []))
    stats = summarise(findings)
    print(f"claims re-checked: {len(claims)}")
    print(f"documents on file: {len(library.evidence)}")
    print("findings: " + json.dumps(stats["by_severity"]))
    for finding in sorted(findings, key=lambda f: f.severity)[: args.limit]:
        print(f"  [{finding.severity}] {finding.stage}: {finding.summary}")
    if args.write:
        (ROOT / "reports").mkdir(parents=True, exist_ok=True)
        (ROOT / "reports" / "irregularities.md").write_text(
            render_markdown(findings, generated_at=utcnow_iso()), encoding="utf-8"
        )
        print("wrote reports/irregularities.md")
    return 0 if stats["by_severity"].get("error", 0) == 0 else 1


def cmd_site(args: argparse.Namespace) -> int:
    """Rebuild the site from the stored library and the last calibration."""
    library = Library.load(ROOT, run_id="site-rebuild")
    calibration = run_calibration(FIXTURE_DIR / "verification_cases.jsonl", apply=False) if (FIXTURE_DIR / "verification_cases.jsonl").exists() else {}
    data = build_site_data(
        library,
        source_matrix=source_matrix(),
        source_status=[],
        irregularities=list(library.irregularities.values()),
        failures=list(library.failures.values()),
        elo_payload=load_json(STATE_DIR / "elo.json", {}) or {},
        calibration=calibration or thresholds_in_force(CALIBRATION_STATE),
        requirements=load_json(ROOT / "data" / "requirements.json", []) or [],
        methodology={
            "engine_version": __version__,
            "evidence_hierarchy": [
                {"rank": rank, "name": name, "description": description} for rank, name, description in EVIDENCE_HIERARCHY
            ],
            "thresholds": thresholds_in_force(CALIBRATION_STATE),
        },
        mode=args.mode,
        run_summary=load_json(ROOT / "reports" / "run_summary.json", {}) or {},
    )
    data["experiment_catalogue"] = catalogue()
    written = build_site(data, SITE_DIR, write_root_entry=True)
    print(f"wrote {len(written)} file(s) to {SITE_DIR}")
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
    print(json.dumps(
        {
            "topics": len(library.topics),
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


def cmd_selftest(args: argparse.Namespace) -> int:
    import unittest

    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    outcome = runner.run(suite)
    return 0 if outcome.wasSuccessful() else 1


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
    site.add_argument("--mode", choices=("live", "snapshot", "fixture"), default="snapshot")
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
