#!/usr/bin/env python3
"""Write reports/SUMMARY.md: the whole library as one readable page.

The site is organised by topic. This tool produces the other thing a reader wants: a
single document listing, for the current library, what was researched, what is
supported by quotations, what is unknown, what is contradictory and what is waiting
for review. Every line carries its source, and every figure is one the engine
recorded - the same numeric guard used for the site is applied to the text it writes.

Usage:
    python3 tools/export_summary.py
    python3 tools/export_summary.py --out reports/SUMMARY.md --top 12
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.config import LIBRARY_DIR, REPORTS_DIR  # noqa: E402
from selflearn.learn.calibration import thresholds_in_force  # noqa: E402
from selflearn.learn.store import Library  # noqa: E402
from selflearn.util import utcnow_iso  # noqa: E402
from selflearn.verify.audit import audit_run_summary  # noqa: E402


def bullet(text: str, *meta: str) -> str:
    tail = f" — {' · '.join(m for m in meta if m)}" if any(meta) else ""
    return f"- {text}{tail}"


def build(library: Library, *, top: int) -> str:
    counts = {
        "topics": len(library.topics),
        "claims": len(library.claims),
        "documents": len(library.evidence),
        "strategies": len(library.strategies),
        "attacks": len(library.attacks),
        "questions": len(library.questions),
        "experiments": len(library.experiments),
        "contradictions": len(library.contradictions),
    }
    supported = sum(1 for c in library.claims.values() if c.verification.verdict == "supported")
    partial = sum(1 for c in library.claims.values() if c.verification.verdict == "partially_supported")
    rejected = sum(1 for c in library.claims.values() if c.verification.verdict == "unsupported")
    thresholds = thresholds_in_force()

    generated_at = utcnow_iso()
    extracted_numbers = re.findall(r"\d+(?:\.\d+)?", generated_at)
    lines: list[str] = []
    lines.append("# SelfLearn summary")
    lines.append("")
    lines.append(f"Generated {generated_at} from the stored library. Nothing in this file is written by hand.")
    lines.append("")
    lines.append("## What the library holds")
    lines.append("")
    lines.append(f"- {counts['topics']} question(s) under research")
    lines.append(f"- {counts['claims']} claim(s): {supported} supported, {partial} needing review, {rejected} rejected")
    lines.append(f"- {counts['documents']} retrieved document(s) stored and hashed")
    lines.append(f"- {counts['strategies']} competing candidate(s) with {counts['attacks']} recorded criticism(s)")
    lines.append(f"- {counts['questions']} derived open question(s), {counts['experiments']} experiment(s) run")
    lines.append(f"- {counts['contradictions']} contradiction(s) awaiting a human decision")
    lines.append("")
    lines.append(
        "Verification thresholds in force: "
        f"supported at coverage {thresholds['in_force']['supported']}, "
        f"partially supported at {thresholds['in_force']['partially_supported']}, "
        f"verbatim quote minimum {thresholds['in_force']['quote_min_chars']} characters "
        f"({thresholds['source']})."
    )
    lines.append("")

    for topic in sorted(library.topics.values(), key=lambda t: t.topic_id):
        topic_id = topic.topic_id
        topic_claims = [c for c in library.claims.values() if c.topic_id == topic_id]
        topic_sources = {c.source_name for c in topic_claims if c.source_name}
        lines.append(f"## {topic.title}")
        lines.append("")
        lines.append(f"*{topic.question}*")
        lines.append("")
        lines.append(
            f"State {topic.status} · {len(topic_claims)} claim(s) · "
            f"{sum(1 for c in topic_claims if c.verification.verdict == 'supported')} supported · "
            f"{len(topic_sources)} source(s) cited"
        )
        lines.append("")

        claims = [c for c in library.claims.values() if c.topic_id == topic_id]
        ordered = sorted(
            claims,
            key=lambda c: (
                {"supported": 0, "partially_supported": 1, "unsupported": 2, "contradicted": 3}.get(
                    c.verification.verdict, 4
                ),
                c.claim_id,
            ),
        )
        shown = [c for c in ordered if c.verification.verdict == "supported"][:top]
        if shown:
            lines.append(f"### Supported by a quotation (first {len(shown)})")
            lines.append("")
            for claim in shown:
                lines.append(
                    bullet(
                        claim.text.replace("\n", " ")[:400],
                        claim.source_name,
                        f"[{claim.evidence_class}]",
                        claim.url or "computed",
                        f"coverage {claim.verification.coverage}",
                    )
                )
            lines.append("")

        needs_review = [c for c in ordered if c.verification.verdict == "partially_supported"]
        if needs_review:
            lines.append(f"### Marked as needing review ({len(needs_review)})")
            lines.append("")
            for claim in needs_review[:top]:
                reason = (claim.verification.reasons or ["no reason recorded"])[0]
                lines.append(bullet(claim.text.replace("\n", " ")[:300], claim.source_name, reason[:160]))
            lines.append("")

        rejected = [c for c in ordered if c.verification.verdict == "unsupported"]
        if rejected:
            lines.append(f"### Rejected by the verifier ({len(rejected)})")
            lines.append("")
            lines.append(
                "These are shown because the engine records what it refused to accept as well as what it accepted."
            )
            lines.append("")
            for claim in rejected[:top]:
                reason = (claim.verification.reasons or ["no reason recorded"])[0]
                lines.append(bullet(claim.text.replace("\n", " ")[:200], claim.source_name, reason[:140]))
            lines.append("")

        questions = [q for q in library.questions.values() if q.topic_id == topic_id]
        if questions:
            lines.append(f"### Open questions ({len(questions)})")
            lines.append("")
            for question in questions[:top]:
                lines.append(bullet(question.text, question.origin, f"priority {question.priority}"))
            lines.append("")

        conflicts = [c for c in library.contradictions.values() if c.topic_id == topic_id]
        if conflicts:
            lines.append(f"### Contradictions ({len(conflicts)})")
            lines.append("")
            for conflict in conflicts[:top]:
                lines.append(
                    bullet(
                        f"{conflict.kind}: {conflict.claim_a} vs {conflict.claim_b}",
                        conflict.severity,
                        conflict.detail[:200],
                    )
                )
            lines.append("")

        experiments = [e for e in library.experiments.values() if e.topic_id == topic_id]
        if experiments:
            lines.append(f"### Experiments ({len(experiments)})")
            lines.append("")
            for experiment in experiments[:top]:
                lines.append(
                    bullet(
                        experiment.hypothesis[:220],
                        f"status {experiment.status}",
                        f"{experiment.metric}: baseline {experiment.baseline} -> best {experiment.best_value} "
                        f"({experiment.best_variant})",
                        experiment.command or "",
                    )
                )
            lines.append("")

    pending = [i for i in library.irregularities.values() if not i.resolved]
    lines.append("## Waiting for review")
    lines.append("")
    if pending:
        by_severity: dict[str, int] = {}
        for finding in pending:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        lines.append(f"{len(pending)} open irregularit(ies): " + ", ".join(f"{k} {v}" for k, v in sorted(by_severity.items())))
        lines.append("")
        for finding in pending[:top]:
            lines.append(bullet(f"[{finding.severity}] {finding.summary}", finding.stage, finding.suggested_action or ""))
    else:
        lines.append("No open irregularities.")
    lines.append("")
    lines.append("## How to check this file")
    lines.append("")
    lines.append("- `python3 tools/check_claim.py <claim-id>` prints a claim, its stored document and a fresh re-check.")
    lines.append("- `python3 -m selflearn audit` re-verifies every claim in the library.")
    lines.append("- `python3 -m selflearn status` prints the counts this file is built from.")

    text = "\n".join(lines) + "\n"
    # The guard runs over the prose lines of this file, with the engine's own figures
    # (and the generation timestamp) allowed, exactly as the site builder does.
    allowed = (
        [str(value) for value in counts.values()]
        + [str(supported), str(partial), str(rejected)]
        + [str(thresholds["in_force"].get(key)) for key in ("supported", "partially_supported", "quote_min_chars")]
        + [str(len(pending))]
        + extracted_numbers
    )
    findings = audit_run_summary(
        " ".join(line for line in lines if not line.startswith(("-", "#", "*", "|"))),
        library.claims.values(),
        extra_allowed=allowed,
    )
    if findings:
        text += "\n" + "> The numeric guard flagged " + str(len(findings)) + " line(s) in this summary; see reports/irregularities.md.\n"
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(REPORTS_DIR / "SUMMARY.md"), help="where to write the summary")
    parser.add_argument("--top", type=int, default=10, help="maximum entries listed per section")
    args = parser.parse_args(argv)

    if not LIBRARY_DIR.exists():
        raise SystemExit("No library found. Run a cycle first: python3 -m selflearn run --mode live")
    library = Library.load(ROOT)
    text = build(library, top=args.top)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
