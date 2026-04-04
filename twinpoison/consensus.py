from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

from .core import DigitalTwin, PlanResult


@dataclass
class ConsensusReport:
    score: float
    majority_action: str
    actions: List[str]
    results: List[PlanResult]


class CrossTwinConsensus:
    """Compare planner outputs across multiple twins."""

    def evaluate(self, twins: Iterable[DigitalTwin]) -> ConsensusReport:
        results = [t.plan() for t in twins]
        actions = [r.chosen_action for r in results]
        counts = Counter(actions)
        majority_action, majority_count = counts.most_common(1)[0]
        score = majority_count / max(len(actions), 1)
        return ConsensusReport(
            score=score,
            majority_action=majority_action,
            actions=actions,
            results=results,
        )
