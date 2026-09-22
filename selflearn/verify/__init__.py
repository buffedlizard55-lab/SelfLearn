"""Deterministic verification: does the retrieved text actually support the claim?"""

from __future__ import annotations

from .audit import (
    audit_run_summary,
    check_coverage,
    check_fixtures,
    check_links,
    merge_findings,
    recheck_claims,
    render_markdown as render_audit_markdown,
    summarise,
)
from .contradiction import detect_contradictions
from .grounding import (
    ClaimProposal,
    derived_proposal,
    ground_evidence,
    is_boilerplate,
    proposal_from_sentence,
    strip_scaffolding,
)
from .verifier import (
    audit_narrative,
    confidence_label,
    independent_source_count,
    verify_claim,
    verify_derived,
    verify_library,
    verify_synthesis,
)

__all__ = [
    "ClaimProposal",
    "audit_narrative",
    "audit_run_summary",
    "check_coverage",
    "check_fixtures",
    "check_links",
    "confidence_label",
    "derived_proposal",
    "detect_contradictions",
    "ground_evidence",
    "independent_source_count",
    "is_boilerplate",
    "merge_findings",
    "proposal_from_sentence",
    "recheck_claims",
    "render_audit_markdown",
    "strip_scaffolding",
    "summarise",
    "verify_claim",
    "verify_derived",
    "verify_library",
    "verify_synthesis",
]
