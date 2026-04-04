from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

import networkx as nx


PlannerFn = Callable[["DigitalTwin"], "PlanResult"]


@dataclass
class PlanResult:
    """Represents a planner output derived from a twin."""

    scenario: str
    chosen_action: str
    cost: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvariantFinding:
    name: str
    passed: bool
    severity: str
    message: str


@dataclass
class SimulationIntegrityDecision:
    action: str
    reasons: List[str]
    findings: List[InvariantFinding]
    consensus_score: float


@dataclass
class DigitalTwin:
    """Graph-backed digital twin with scenario metadata and planner binding."""

    name: str
    graph: nx.DiGraph
    scenario: str
    planner: Optional[PlannerFn] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self, new_name: Optional[str] = None) -> "DigitalTwin":
        copied = nx.DiGraph()
        copied.add_nodes_from((n, dict(attrs)) for n, attrs in self.graph.nodes(data=True))
        copied.add_edges_from((u, v, dict(attrs)) for u, v, attrs in self.graph.edges(data=True))
        return DigitalTwin(
            name=new_name or f"{self.name}_copy",
            graph=copied,
            scenario=self.scenario,
            planner=self.planner,
            metadata=dict(self.metadata),
        )

    def plan(self) -> PlanResult:
        if self.planner is None:
            raise ValueError(f"Twin '{self.name}' has no planner bound.")
        return self.planner(self)

    def set_node(self, node: str, **attrs: Any) -> None:
        self.graph.nodes[node].update(attrs)

    def set_edge(self, source: str, target: str, **attrs: Any) -> None:
        self.graph.edges[source, target].update(attrs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "scenario": self.scenario,
            "metadata": self.metadata,
            "nodes": [
                {"id": node, **attrs} for node, attrs in self.graph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **attrs}
                for u, v, attrs in self.graph.edges(data=True)
            ],
        }


def score_policy_decision(
    findings: Iterable[InvariantFinding],
    consensus_score: float,
    consensus_threshold: float = 0.6,
) -> SimulationIntegrityDecision:
    findings = list(findings)
    reasons: List[str] = []
    action = "allow"

    failed_high = [f for f in findings if not f.passed and f.severity.lower() == "high"]
    failed_med = [f for f in findings if not f.passed and f.severity.lower() == "medium"]

    if failed_high:
        action = "block"
        reasons.extend(f"high-severity invariant failed: {f.name}" for f in failed_high)
    elif failed_med or consensus_score < consensus_threshold:
        action = "review"
        reasons.extend(f"invariant requires review: {f.name}" for f in failed_med)
        if consensus_score < consensus_threshold:
            reasons.append(
                f"cross-twin consensus below threshold ({consensus_score:.2f} < {consensus_threshold:.2f})"
            )
    else:
        reasons.append("integrity checks passed")

    return SimulationIntegrityDecision(
        action=action,
        reasons=reasons,
        findings=findings,
        consensus_score=consensus_score,
    )
