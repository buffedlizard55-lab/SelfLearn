"""Central configuration: paths, budgets, thresholds and versioned constants.

Every tunable number the engine relies on lives here so that a reviewer can see
the complete set of assumptions in one place. Values changed by the
self-calibration experiment are recorded in ``state/calibration.json`` and are
*reported on the site*, never applied silently.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# The repository root. SELFLEARN_ROOT lets a run be pointed at another directory
# (a temporary root in tests, a clean checkout in CI) so that a smoke run never
# writes into the repository's own library.
ROOT = Path(os.environ.get("SELFLEARN_ROOT") or Path(__file__).resolve().parent.parent).resolve()

# The checkout the code itself lives in. It differs from ROOT only when
# SELFLEARN_ROOT is set. Things that ship with the code - the experiment scripts
# - are resolved against this, not against the library root: a run pointed at an
# empty directory must still be able to run the experiments it was shipped with.
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# --- Paths -----------------------------------------------------------------
DATA_DIR = ROOT / "data"
SEED_DIR = DATA_DIR / "seeds"
FIXTURE_DIR = DATA_DIR / "fixtures"
EVIDENCE_DIR = ROOT / "evidence" / "snapshots"
LIBRARY_DIR = ROOT / "library"          # append-only structured memory
REPORTS_DIR = ROOT / "reports"
STATE_DIR = ROOT / "state"
SITE_DIR = ROOT / "docs"          # GitHub Pages serves this repository from /docs
SITE_DATA_DIR = SITE_DIR / "data"
SITE_STATIC_DIR = SITE_DIR / "static"
DOCS_DIR = ROOT / "docs"
EXPERIMENT_DIR = PACKAGE_ROOT / "experiments"

# Structured-memory streams (append-only JSONL). The relative paths are the
# authoritative definition; STREAMS resolves them against the repository root so
# that a run can be pointed at any other root (a temporary directory in tests, a
# checkout in CI) and still find every stream.
STREAM_FILES: dict[str, str] = {
    "evidence": "library/evidence_index.jsonl",
    "claims": "library/claims.jsonl",
    "topics": "library/topics.jsonl",
    "questions": "library/questions.jsonl",
    "strategies": "library/strategies.jsonl",
    "attacks": "library/attacks.jsonl",
    "experiments": "library/experiments.jsonl",
    "discoveries": "library/discoveries.jsonl",
    "failures": "library/failures.jsonl",
    "irregularities": "library/irregularities.jsonl",
    "audit": "library/audit_log.jsonl",
    "contradictions": "library/contradictions.jsonl",
    "tournaments": "library/tournaments.jsonl",
    "tasks": "library/tasks.jsonl",
}
STREAMS = {name: ROOT / relative for name, relative in STREAM_FILES.items()}

IRREGULARITIES_MD = REPORTS_DIR / "irregularities.md"
LOOP_STATE = STATE_DIR / "loop_state.json"
ELO_STATE = STATE_DIR / "elo.json"
CALIBRATION_STATE = STATE_DIR / "calibration.json"

# --- Evidence hierarchy ----------------------------------------------------
# Ordering taken verbatim from the project design document (section 5).
# Rank 1 is the strongest evidence class; 9 is the weakest.
EVIDENCE_HIERARCHY: tuple[tuple[int, str, str], ...] = (
    (1, "direct_experiment", "An experiment run by this engine with recorded inputs, outputs and hashes."),
    (2, "reproduced_experiment", "A previous experiment re-run and confirmed by this engine."),
    (3, "primary_source", "Original data, official API response, official document or dataset."),
    (4, "peer_reviewed", "Peer-reviewed publication indexed by a DOI registry or PubMed."),
    (5, "official_data", "Data published by a government, standards body or international agency."),
    (6, "reputable_secondary", "Encyclopaedic or established secondary compilation."),
    (7, "commentary", "Expert commentary, editorial, blog post by a named practitioner."),
    (8, "unverified_claim", "Assertion with no traceable provenance."),
    (9, "ai_speculation", "Machine-generated text that is not grounded in retrieved evidence."),
)
EVIDENCE_RANK = {name: rank for rank, name, _ in EVIDENCE_HIERARCHY}
EVIDENCE_LABEL = {name: label for rank, name, label in EVIDENCE_HIERARCHY}

# Classes the engine will accept as grounds for a *factual* claim.
FACT_ELIGIBLE_CLASSES = frozenset(
    {"direct_experiment", "reproduced_experiment", "primary_source", "peer_reviewed", "official_data"}
)


# --- Verification thresholds ----------------------------------------------
@dataclass(frozen=True)
class VerificationThresholds:
    """Cut-offs for the deterministic support check.

    ``supported`` requires every numeric and temporal literal in the claim to be
    present in the source *and* token coverage at or above ``supported``.
    Lowering these increases recall and increases the false-support rate - the
    self-calibration experiment measures exactly that trade-off on a labelled
    fixture set and the chosen values are published on the site.
    """

    supported: float = 0.80
    partially_supported: float = 0.55
    # A verbatim quote of at least this many characters promotes a claim to
    # "strongly supported" regardless of token coverage, because a quote match
    # is strictly stronger evidence than a token-overlap heuristic.
    quote_min_chars: int = 24

    def as_dict(self) -> dict[str, float]:
        return {
            "supported": self.supported,
            "partially_supported": self.partially_supported,
            "quote_min_chars": float(self.quote_min_chars),
        }


THRESHOLDS = VerificationThresholds()

# --- Research budgets ------------------------------------------------------
@dataclass
class Budget:
    """Hard limits for one loop cycle, so an unattended run cannot run away."""

    max_seconds: int = 900           # wall clock for a single cycle
    max_http_requests: int = 60      # network calls per cycle
    max_topics_per_cycle: int = 4
    max_evidence_per_topic: int = 12
    max_claims_per_topic: int = 60
    max_candidates_per_topic: int = 6
    max_experiments_per_cycle: int = 3
    request_timeout: int = 20
    min_seconds_between_requests: float = 1.0   # per host, polite crawling
    max_retries: int = 3

    def as_dict(self) -> dict[str, float | int]:
        return dict(self.__dict__)


BUDGET = Budget()

# --- Tournament criteria ---------------------------------------------------
# Weights and definitions derived from design document section 10. The weights
# are relative; the scoring function normalises them.
TOURNAMENT_CRITERIA: tuple[tuple[str, str, float, str], ...] = (
    ("correctness", "Correctness", 0.18, "Every factual element traces to a verified claim; no numeric mismatch."),
    ("evidence_quality", "Evidence quality", 0.16, "Mean evidence-hierarchy rank of the supporting claims."),
    ("reproducibility", "Reproducibility", 0.13, "A third party can re-derive the result from the cited sources and commands."),
    ("adversarial_survival", "Survives criticism", 0.15, "Share of critic attacks the candidate survives."),
    ("robustness", "Robustness", 0.12, "Stable when evidence order and weights are perturbed."),
    ("experimental_performance", "Experimental performance", 0.10, "Measured result relative to the recorded baseline, when a test exists."),
    ("simplicity", "Simplicity", 0.07, "Fewer unsupported assumptions and fewer moving parts is better."),
    ("scalability", "Scalability", 0.05, "Plausible to apply beyond the single case studied."),
    ("computational_cost", "Computational cost", 0.04, "Cheaper to run and verify is better."),
)

# --- Concept/specification version ----------------------------------------
DESIGN_DOC_SECTIONS = tuple(range(1, 21))
REQUIREMENTS_VERSION = "1.0"

# --- Agent personas --------------------------------------------------------
# Design document section 3: six independent thinkers with different briefs.
PERSONAS: tuple[tuple[str, str, str], ...] = (
    ("A", "Conventional", "Find the strongest solution using established, well-evidenced knowledge."),
    ("B", "Contrarian", "Assume the conventional approach is wrong; find evidence-backed alternatives."),
    ("C", "First principles", "Derive a solution from fundamental constraints and published base rates."),
    ("D", "Cross-domain", "Look for solutions that worked in a completely different field."),
    ("E", "Optimization", "Find the cheapest, fastest or most scalable option given the sourced numbers."),
    ("F", "Experimental", "Design a falsifiable test that could determine which idea is actually correct."),
)

# --- Idea lifecycle (design document section 7) ---------------------------
LIFECYCLE_STATES = (
    "new",
    "researching",
    "hypothesis",
    "competing",
    "testing",
    "validated",
    "deployed",
    "monitored",
    "rejected",
)

# --- Runtime mode labels ---------------------------------------------------
# Used verbatim in published output so a reader always knows how the evidence
# was obtained. `fixture` results are explicitly not presented as live research.
EVIDENCE_MODES = {
    "live": "Retrieved directly from the publisher's API during this run.",
    "snapshot": "Replayed from a stored evidence snapshot; the stored content hash is what was verified.",
    "fixture": "Synthetic, constructed for testing the pipeline. NOT real-world evidence.",
}

DEFAULT_USER_AGENT = (
    "SelfLearn/0.1 (autonomous research engine; "
    "https://github.com/buffedlizard55-lab/SelfLearn) "
    "python-urllib"
)


@dataclass
class RuntimeFlags:
    """Switches that alter how far the engine is allowed to go."""

    allow_network: bool = True
    evidence_mode: str = "snapshot"
    strict: bool = False          # in strict mode, unsupported claims abort publication
    offline_reasons: list[str] = field(default_factory=list)

    def note_offline(self, reason: str) -> None:
        if reason not in self.offline_reasons:
            self.offline_reasons.append(reason)


FLAGS = RuntimeFlags()
