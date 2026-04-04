from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from .consensus import ConsensusReport, CrossTwinConsensus
from .core import DigitalTwin, PlanResult, SimulationIntegrityDecision, score_policy_decision
from .invariants import InvariantSuite
from .mutators import MutationRecord, TwinMutator


@dataclass
class HarnessRun:
    clean_result: PlanResult
    poisoned_result: PlanResult
    mutations: List[MutationRecord]
    consensus: ConsensusReport
    decision: SimulationIntegrityDecision
    twin_snapshot: Dict[str, Any] = field(default_factory=dict)


class TwinPoisonHarness:
    def __init__(self, invariants: InvariantSuite | None = None) -> None:
        self.mutator = TwinMutator()
        self.consensus = CrossTwinConsensus()
        self.invariants = invariants or InvariantSuite()

    def run(
        self,
        baseline: DigitalTwin,
        recipe: Iterable[Dict[str, Any]],
        consensus_twins: Iterable[DigitalTwin] | None = None,
        consensus_threshold: float = 0.6,
    ) -> HarnessRun:
        clean = baseline.clone(new_name=f"{baseline.name}_clean")
        poisoned = baseline.clone(new_name=f"{baseline.name}_poisoned")

        clean_result = clean.plan()
        mutations = self.mutator.apply_recipe(poisoned, recipe)
        poisoned_result = poisoned.plan()

        twins_for_consensus = [poisoned]
        if consensus_twins:
            twins_for_consensus.extend(list(consensus_twins))
        else:
            twins_for_consensus.append(clean)

        consensus = self.consensus.evaluate(twins_for_consensus)
        findings = self.invariants.run(poisoned)
        decision = score_policy_decision(findings, consensus.score, consensus_threshold=consensus_threshold)

        return HarnessRun(
            clean_result=clean_result,
            poisoned_result=poisoned_result,
            mutations=mutations,
            consensus=consensus,
            decision=decision,
            twin_snapshot=poisoned.to_dict(),
        )
