"""Independent re-verification of everything the engine intends to publish.

This module is the "flag any irregularities for review" requirement made
concrete. It runs *after* generation and never mutates the library: it only
reports. Findings are written to ``reports/irregularities.md`` and rendered on
the site, including the count of findings of each severity.

Checks
------
1. **Re-derivation.** Every stored claim is re-verified from its stored
   evidence snapshot. If the re-computed verdict or coverage differs from what
   was recorded at publication time, that is a regression and is reported.
2. **Snapshot integrity.** The snapshot's text is re-hashed and compared with the
   recorded hash. A mismatch means the stored bytes changed after verification.
3. **Link validity.** Every published URL must be absolute ``http(s)``. Relative
   or missing URLs cannot be manually reviewed and are reported.
4. **Fixture leakage.** Fixture evidence must never appear in published output.
5. **Narrative arithmetic.** Figures in a generated summary must exist in the
   verified claim set for that topic.
6. **Coverage gaps.** Topics with no evidence, or sources that were unreachable,
   are reported so that the gap is visible rather than silent.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

from ..config import THRESHOLDS
from ..models import Claim, EvidenceRecord, Irregularity, SourceStatus, Topic
from ..util import sha256_text, stable_id
from .verifier import audit_narrative, verify_claim, verify_derived, verify_synthesis

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _irregularity(
    severity: str,
    stage: str,
    topic_id: str | None,
    summary: str,
    detail: str = "",
    *,
    url: str | None = None,
    suggested_action: str = "",
) -> Irregularity:
    return Irregularity(
        irregularity_id=stable_id("irr", stage, summary, topic_id or ""),
        severity=severity,
        stage=stage,
        topic_id=topic_id,
        summary=summary,
        detail=detail[:2000],
        url=url,
        suggested_action=suggested_action,
    )


# ---------------------------------------------------------------------------
# 1 + 2: re-derivation and snapshot integrity
# ---------------------------------------------------------------------------


def recheck_claims(claims: Iterable[Claim], snapshot_dir: Path) -> list[Irregularity]:
    """Re-verify every claim from its stored provenance.

    Three paths, because there are three kinds of claim:

    * ``direct`` claims are re-checked against the stored document, with the same
      verifier that accepted them;
    * ``derived`` claims are statements the engine computed about its own library,
      so they are re-checked against the figures recorded on the claim
      (:func:`~selflearn.verify.verifier.verify_derived`). Checking a derived
      statement against a document would be meaningless: there is no document.
    * ``synthesis`` claims combine figures from several documents, so they are
      re-checked against the claims they cite
      (:func:`~selflearn.verify.verifier.verify_synthesis`). If a cited claim has
      been withdrawn or edited, the recomputation fails and the finding is raised
      rather than the statement being silently kept.
    """
    snapshot_dir = Path(snapshot_dir)
    claims = list(claims)
    claims_by_id = {claim.claim_id: claim for claim in claims}
    findings: list[Irregularity] = []
    superseded = [claim for claim in claims if claim.superseded]
    if superseded:
        # The count lives in the detail, not the summary: the finding id is a
        # hash of the summary, so a count in the summary would open a fresh row
        # (and strand the old one) every time a cycle retires more statements.
        findings.append(
            _irregularity(
                "info",
                "audit",
                None,
                "Stored claims are marked superseded and are excluded from re-verification",
                f"{len(superseded)} claim(s) currently carry a supersession reason. A superseded claim is one a "
                "later cycle no longer produces. It remains in the library with the reason recorded on it, and "
                "is not published as a current finding.",
                suggested_action="Nothing to do unless a reviewer believes a retired statement was correct.",
            )
        )
    for claim in claims:
        if claim.superseded:
            continue
        if claim.claim_kind == "derived":
            recheck = verify_derived(claim.text, claim.context_numbers)
            if recheck.verdict != claim.verification.verdict:
                findings.append(
                    _irregularity(
                        "error",
                        "audit",
                        claim.topic_id,
                        f"Re-computation changed the verdict for derived claim {claim.claim_id}",
                        f"Recorded '{claim.verification.verdict}' against figures {claim.context_numbers}, "
                        f"recomputed '{recheck.verdict}'. " + " ".join(recheck.reasons[:2]),
                        suggested_action="The recorded figures no longer support the sentence; regenerate this topic.",
                    )
                )
            continue

        if claim.claim_kind == "synthesis":
            cited = [claims_by_id[cid] for cid in claim.cited_claim_ids if cid in claims_by_id]
            unresolved = [cid for cid in claim.cited_claim_ids if cid not in claims_by_id]
            if unresolved:
                findings.append(
                    _irregularity(
                        "error",
                        "audit",
                        claim.topic_id,
                        f"Synthesis claim {claim.claim_id} cites claims that are not in the library",
                        "Unresolvable citations: " + ", ".join(unresolved)
                        + ". A cross-document statement cannot be re-checked if a claim it depends on is gone.",
                        suggested_action="Regenerate this topic so the statement is rebuilt from the current library.",
                    )
                )
                continue
            recheck = verify_synthesis(claim.text, cited, claim.context_numbers)
            if recheck.verdict != claim.verification.verdict:
                findings.append(
                    _irregularity(
                        "error",
                        "audit",
                        claim.topic_id,
                        f"Re-computation changed the verdict for synthesis claim {claim.claim_id}",
                        f"Recorded '{claim.verification.verdict}', recomputed '{recheck.verdict}' from the "
                        f"{len(cited)} cited claim(s). " + " ".join(recheck.reasons[:2]),
                        suggested_action="The statement no longer follows from its citations; regenerate this topic.",
                    )
                )
            elif len({c.evidence_id for c in cited}) < 2:
                findings.append(
                    _irregularity(
                        "error",
                        "audit",
                        claim.topic_id,
                        f"Synthesis claim {claim.claim_id} cites fewer than two documents",
                        f"Cited documents: {sorted({c.evidence_id for c in cited})}.",
                        suggested_action="A cross-document statement needs two documents; regenerate this topic.",
                    )
                )
            continue

        snapshot_path = snapshot_dir / f"{claim.evidence_id}.json"
        if not snapshot_path.exists():
            findings.append(
                _irregularity(
                    "error",
                    "audit",
                    claim.topic_id,
                    f"Claim {claim.claim_id} cites evidence {claim.evidence_id} with no stored snapshot",
                    "The cited document is not in evidence/snapshots, so the claim cannot be re-checked by a reviewer.",
                    url=claim.url,
                    suggested_action="Re-run the collection stage or remove the claim from the library.",
                )
            )
            continue
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            findings.append(
                _irregularity(
                    "error",
                    "audit",
                    claim.topic_id,
                    f"Snapshot {snapshot_path.name} could not be read",
                    str(exc)[:300],
                    suggested_action="Inspect the file; it may be truncated or corrupt.",
                )
            )
            continue

        text = payload.get("text", "")
        stored_hash = payload.get("content_hash", "")
        recomputed_hash = sha256_text(text)
        if stored_hash and stored_hash != recomputed_hash:
            findings.append(
                _irregularity(
                    "error",
                    "audit",
                    claim.topic_id,
                    f"Snapshot {snapshot_path.name} hash mismatch",
                    f"Recorded {stored_hash[:23]} but the stored text hashes to {recomputed_hash[:23]}.",
                    suggested_action="The snapshot changed after verification. Restore it or re-verify the claim.",
                )
            )

        recheck = verify_claim(claim.text, claim.quote, text, thresholds=THRESHOLDS)
        if recheck.verdict != claim.verification.verdict:
            findings.append(
                _irregularity(
                    "error",
                    "audit",
                    claim.topic_id,
                    f"Re-verification changed the verdict for {claim.claim_id}",
                    f"Recorded '{claim.verification.verdict}', recomputed '{recheck.verdict}'. "
                    + " ".join(recheck.reasons[:2]),
                    url=claim.url,
                    suggested_action="Investigate before trusting the published claim.",
                )
            )
        elif abs(recheck.coverage - claim.verification.coverage) > 0.02:
            findings.append(
                _irregularity(
                    "warning",
                    "audit",
                    claim.topic_id,
                    f"Re-verification changed coverage for {claim.claim_id}",
                    f"Recorded {claim.verification.coverage:.2f}, recomputed {recheck.coverage:.2f}.",
                    url=claim.url,
                    suggested_action="Usually a rounding change; confirm the snapshot is unchanged.",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# 3: link validity
# ---------------------------------------------------------------------------


def check_links(claims: Iterable[Claim]) -> list[Irregularity]:
    """Every claim must carry a resolvable link, except computed ones.

    Derived claims describe a computation, so they have no source to link to. That
    exemption is narrow and explicit: a claim is only exempt if it is marked
    ``derived`` *and* carries the figures it was computed from.

    Synthesis claims combine several documents, so they carry no single URL of
    their own; they are exempt only if they name the claims they were built from,
    and each of those claims carries its own link. An exemption without citations
    is reported as an error.
    """
    findings: list[Irregularity] = []
    seen: set[str] = set()
    for claim in claims:
        if claim.claim_kind == "synthesis":
            if not claim.cited_claim_ids:
                findings.append(
                    _irregularity(
                        "error",
                        "audit",
                        claim.topic_id,
                        f"Synthesis claim {claim.claim_id} cites no claims",
                        "A cross-document statement without citations cannot be reviewed or re-checked.",
                        suggested_action="Regenerate this topic; this indicates a bug in the synthesis stage.",
                    )
                )
            continue
        if claim.claim_kind == "derived":
            if not claim.context_numbers:
                findings.append(
                    _irregularity(
                        "error",
                        "audit",
                        claim.topic_id,
                        f"Derived claim {claim.claim_id} carries no figures to check it against",
                        "A derived claim with an empty context set can never be re-verified.",
                        suggested_action="Regenerate the topic; this indicates a bug in the aggregation stage.",
                    )
                )
            continue
        url = (claim.url or "").strip()
        if not url:
            findings.append(
                _irregularity(
                    "error",
                    "audit",
                    claim.topic_id,
                    f"Claim {claim.claim_id} has no source link",
                    "A claim without a resolvable link cannot be manually reviewed.",
                    suggested_action="Drop the claim or restore its source URL.",
                )
            )
            continue
        if url in seen:
            continue
        seen.add(url)
        if not url.startswith(("http://", "https://")):
            findings.append(
                _irregularity(
                    "warning",
                    "audit",
                    claim.topic_id,
                    f"Non-HTTP source link in claim {claim.claim_id}: {url[:80]}",
                    "Only absolute http(s) URLs are usable for manual review.",
                    suggested_action="Map the identifier to a resolvable URL in the source adapter.",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# 4: fixture leakage
# ---------------------------------------------------------------------------


def check_fixtures(records: Iterable[EvidenceRecord], claims: Iterable[Claim]) -> list[Irregularity]:
    findings: list[Irregularity] = []
    fixture_records = [r for r in records if r.is_fixture]
    if fixture_records:
        findings.append(
            _irregularity(
                "warning",
                "audit",
                None,
                f"{len(fixture_records)} synthetic fixture document(s) present in this run",
                "Fixtures exist to test the pipeline. Output that depends on them must be labelled and must not be "
                "presented as real-world research.",
                suggested_action="Confirm the published pages label these as fixtures, or rerun in live/snapshot mode.",
            )
        )
    fixture_ids = {r.evidence_id for r in fixture_records}
    leaked = [c.claim_id for c in claims if c.evidence_id in fixture_ids]
    if leaked:
        findings.append(
            _irregularity(
                "error",
                "audit",
                None,
                f"{len(leaked)} claim(s) rest on fixture evidence",
                "Claims derived from fixtures cannot be published as findings: " + ", ".join(leaked[:10]),
                suggested_action="Run the loop against live sources, or mark the publish output as a test run.",
            )
        )
    return findings


# ---------------------------------------------------------------------------
# 5: narrative arithmetic
# ---------------------------------------------------------------------------


def audit_run_summary(text: str, claims: Iterable[Claim], extra_allowed: Iterable[str] = ()) -> list[Irregularity]:
    """Check that a generated summary quotes no figure absent from the claims."""
    allowed = {n for c in claims for n in (c.verification.missing_numbers or [])}  # always empty by construction
    allowed_numeric = set()
    for claim in claims:
        from ..util import extract_numbers

        allowed_numeric |= extract_numbers(claim.text)
    allowed_numeric |= {str(n) for n in extra_allowed}
    unbacked = audit_narrative(text, allowed_numeric)
    if unbacked:
        return [
            _irregularity(
                "error",
                "audit",
                None,
                "Generated summary contains figures not present in any verified claim",
                "Figures: " + ", ".join(unbacked),
                suggested_action="Remove the figure or add a verified claim that supports it.",
            )
        ]
    del allowed
    return []


# ---------------------------------------------------------------------------
# 6: coverage gaps
# ---------------------------------------------------------------------------


def check_coverage(
    topics: Iterable[Topic],
    claims: Iterable[Claim],
    statuses: Iterable[SourceStatus],
) -> list[Irregularity]:
    findings: list[Irregularity] = []
    by_topic: dict[str, int] = {}
    for claim in claims:
        by_topic[claim.topic_id] = by_topic.get(claim.topic_id, 0) + 1
    for topic in topics:
        count = by_topic.get(topic.topic_id, 0)
        if count == 0:
            findings.append(
                _irregularity(
                    "warning",
                    "audit",
                    topic.topic_id,
                    f"Topic '{topic.title}' produced no verified claims",
                    "Either every source failed, or the retrieved documents did not contain quotable content.",
                    suggested_action="Check the source status table for this topic and add or repair sources.",
                )
            )
    statuses = list(statuses)
    unreachable = sorted({s.source_id for s in statuses if s.live_status in {"unreachable", "error"}})
    if unreachable:
        findings.append(
            _irregularity(
                "warning",
                "audit",
                None,
                f"{len(unreachable)} source(s) were not reachable during this run",
                "Unavailable sources: " + ", ".join(unreachable),
                suggested_action="Confirm network egress from the runner, or accept snapshot replay for these sources.",
            )
        )
    return findings


# ---------------------------------------------------------------------------
# Aggregation and rendering
# ---------------------------------------------------------------------------


def summarise(findings: Iterable[Irregularity]) -> dict[str, Any]:
    findings = list(findings)
    counts: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return {"total": len(findings), "by_severity": counts}


def merge_findings(findings: Iterable[Irregularity]) -> list[Irregularity]:
    """One row per irregularity id, the last row's content winning, while a
    reviewer's decision survives the engine re-detecting the finding.

    A cycle passes the stored findings plus the ones it raised itself; an audit
    rule that fires again produces the same id twice (or, over time, many times).
    The published list is the current state, so it carries each id once with the
    newest content - but a plain last-wins dedupe would silently drop
    ``resolved``/``resolution`` from the stored copy, because the fresh
    re-detection never carries them. This merge keeps the reviewer fields from
    whichever copy has them, which is what ``store.add_irregularities`` already
    does on the write path; using the same rule here is what keeps the report,
    the JSON export and the store from disagreeing.
    """
    by_id: dict[str, Irregularity] = {}
    for finding in findings:
        previous = by_id.get(finding.irregularity_id)
        if previous is not None and (previous.resolved or previous.resolution or previous.resolved_at or previous.resolution_link):
            if not (finding.resolved or finding.resolution):
                finding = replace(
                    finding,
                    resolved=previous.resolved,
                    resolved_at=previous.resolved_at,
                    resolution=previous.resolution,
                    resolution_link=previous.resolution_link,
                )
        by_id[finding.irregularity_id] = finding
    return list(by_id.values())


def render_markdown(findings: Iterable[Irregularity], *, generated_at: str) -> str:
    findings = sorted(
        merge_findings(findings),
        key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.stage, f.summary),
    )
    stats = summarise(findings)
    resolved = sum(1 for f in findings if f.resolved)
    lines = [
        "# Irregularities for review",
        "",
        f"Generated: {generated_at}",
        "",
        "This file is produced by the audit stage. It lists everything the engine could not",
        "reconcile on its own. Nothing here is a conclusion; each entry is a request for a human",
        "decision, with the evidence needed to make it.",
        "",
        f"**Totals** - error: {stats['by_severity'].get('error', 0)}, "
        f"warning: {stats['by_severity'].get('warning', 0)}, "
        f"info: {stats['by_severity'].get('info', 0)}; resolved by a reviewer: {resolved}.",
        "",
    ]
    if not findings:
        lines.append("No irregularities were detected in this run.")
        lines.append("")
        return "\n".join(lines)

    current_stage = None
    for finding in findings:
        if finding.stage != current_stage:
            current_stage = finding.stage
            lines.extend([f"## Stage: {current_stage}", ""])
        marker = {"error": "ERROR", "warning": "WARNING", "info": "INFO"}.get(finding.severity, "NOTE")
        lines.append(f"### [{marker}] {finding.summary}")
        lines.append("")
        lines.append(f"- **id:** `{finding.irregularity_id}`")
        lines.append(f"- **topic:** {finding.topic_id or 'n/a'}")
        if finding.url:
            lines.append(f"- **link:** <{finding.url}>")
        if finding.detail:
            lines.append(f"- **detail:** {finding.detail}")
        if finding.suggested_action:
            lines.append(f"- **suggested action:** {finding.suggested_action}")
        lines.append(f"- **detected:** {finding.created_at}")
        if finding.resolved:
            lines.append(f"- **resolved by a reviewer:** {finding.resolved_at or 'date not recorded'}")
            if finding.resolution:
                lines.append(f"- **reviewer's reason:** {finding.resolution}")
            if finding.resolution_link:
                lines.append(f"- **reference:** <{finding.resolution_link}>")
        lines.append("")
    return "\n".join(lines)
