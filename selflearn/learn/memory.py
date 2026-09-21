"""Meta-knowledge: what the system has learned about its own process.

This is the layer the design document calls "extremely powerful" - not another
paragraph in a store, but knowledge about which sources, which personas and which
critic rules behave how. It is computed from the library and published, so a
reader can see the engine's self-assessment and disagree with it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ..models import Attack, Claim, EvidenceRecord, ExperimentResult, Strategy
from ..util import utcnow_iso


@dataclass
class SourceReliability:
    source_id: str
    source_name: str
    evidence_class: str
    evidence_rank: int
    documents: int = 0
    claims_proposed: int = 0
    claims_supported: int = 0
    partially_supported: int = 0
    unsupported: int = 0
    citations: int = 0

    @property
    def support_rate(self) -> float:
        if not self.claims_proposed:
            return 0.0
        return round(self.claims_supported / self.claims_proposed, 4)

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.__dict__)
        payload["support_rate"] = self.support_rate
        return payload


@dataclass
class RuleProfile:
    rule: str
    fired: int = 0
    survived: int = 0
    conceded: int = 0
    opened: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.__dict__)
        payload["survival_rate"] = round(self.survived / self.fired, 4) if self.fired else 0.0
        return payload


@dataclass
class MetaKnowledge:
    generated_at: str = field(default_factory=utcnow_iso)
    sources: list[dict[str, Any]] = field(default_factory=list)
    rules: list[dict[str, Any]] = field(default_factory=list)
    personas: list[dict[str, Any]] = field(default_factory=list)
    experiments_ok: int = 0
    experiments_total: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "sources": self.sources,
            "rules": self.rules,
            "personas": self.personas,
            "experiments": {"completed": self.experiments_ok, "total": self.experiments_total},
            "notes": self.notes,
        }


def build_meta_knowledge(
    claims: Iterable[Claim],
    evidence: Iterable[EvidenceRecord],
    attacks: Iterable[Attack],
    strategies: Iterable[Strategy],
    experiments: Iterable[ExperimentResult],
    *,
    elo_leaderboard: list[dict[str, Any]] | None = None,
) -> MetaKnowledge:
    """Assemble the meta-knowledge layer from the current library."""
    claims = list(claims)
    evidence = list(evidence)
    attacks = list(attacks)
    strategies = list(strategies)
    experiments = list(experiments)

    # -- source reliability -------------------------------------------------
    reliability: dict[str, SourceReliability] = {}
    for record in evidence:
        row = reliability.setdefault(
            record.source_id,
            SourceReliability(record.source_id, record.source_name, record.evidence_class, record.evidence_rank),
        )
        row.documents += 1
    for claim in claims:
        row = reliability.setdefault(
            claim.source_name,
            SourceReliability(claim.source_name, claim.source_name, claim.evidence_class, claim.evidence_rank),
        )
        row.claims_proposed += 1
        if claim.verification.verdict == "supported":
            row.claims_supported += 1
        elif claim.verification.verdict == "partially_supported":
            row.partially_supported += 1
        else:
            row.unsupported += 1
    for strategy in strategies:
        for claim_id in strategy.supporting_claim_ids:
            for claim in claims:
                if claim.claim_id == claim_id:
                    key = claim.source_name
                    if key in reliability:
                        reliability[key].citations += 1
                    break

    source_rows = sorted(
        (row.to_dict() for row in reliability.values()),
        key=lambda row: (row["evidence_rank"], -row["claims_proposed"], row["source_id"]),
    )

    # -- critic rule profile -------------------------------------------------
    rules: dict[str, RuleProfile] = {}
    for attack in attacks:
        rule_id = attack.critic.split(":", 1)[0].strip()
        profile = rules.setdefault(rule_id, RuleProfile(rule_id))
        profile.fired += 1
        if attack.outcome == "survived":
            profile.survived += 1
        elif attack.outcome == "conceded":
            profile.conceded += 1
        else:
            profile.opened += 1
    rule_rows = sorted((row.to_dict() for row in rules.values()), key=lambda row: (-row["fired"], row["rule"]))

    notes: list[str] = []
    weakest = [row for row in source_rows if row["claims_proposed"] and row["support_rate"] == 0.0]
    if weakest:
        notes.append(
            "Sources that have never yet produced a fully supported claim: "
            + ", ".join(row["source_id"] for row in weakest[:6])
        )
    if not experiments:
        notes.append(
            "No experiment has been run yet. Until one is, every criterion involving measured performance is zero by "
            "construction and the tournament ranks candidates on evidence quality alone."
        )

    return MetaKnowledge(
        sources=source_rows,
        rules=rule_rows,
        personas=list(elo_leaderboard or []),
        experiments_ok=sum(1 for e in experiments if e.status == "completed"),
        experiments_total=len(experiments),
        notes=notes,
    )
