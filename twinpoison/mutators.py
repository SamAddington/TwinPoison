from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from .core import DigitalTwin


@dataclass
class MutationRecord:
    kind: str
    target: str
    before: Dict[str, Any]
    after: Dict[str, Any]
    note: str


class TwinMutator:
    """Safe mutation operators for toy digital twins."""

    def __init__(self) -> None:
        self.history: list[MutationRecord] = []

    def _record(self, kind: str, target: str, before: Dict[str, Any], after: Dict[str, Any], note: str) -> None:
        self.history.append(MutationRecord(kind=kind, target=target, before=before, after=after, note=note))

    def edge_cost_shift(self, twin: DigitalTwin, source: str, target: str, factor: float, note: str = "") -> None:
        edge = twin.graph.edges[source, target]
        before = dict(edge)
        edge["cost"] = round(float(edge.get("cost", 1.0)) * factor, 3)
        if "latency" in edge:
            edge["latency"] = round(float(edge.get("latency", 1.0)) * factor, 3)
        after = dict(edge)
        self._record("edge_cost_shift", f"{source}->{target}", before, after, note or f"multiplied cost by {factor}")

    def edge_capacity_shift(self, twin: DigitalTwin, source: str, target: str, delta: float, note: str = "") -> None:
        edge = twin.graph.edges[source, target]
        before = dict(edge)
        edge["capacity"] = round(float(edge.get("capacity", 0.0)) + delta, 3)
        after = dict(edge)
        self._record("edge_capacity_shift", f"{source}->{target}", before, after, note or f"shifted capacity by {delta}")

    def phantom_edge(
        self,
        twin: DigitalTwin,
        source: str,
        target: str,
        *,
        cost: float,
        capacity: float = 1.0,
        trust: str = "unverified",
        note: str = "",
    ) -> None:
        before: Dict[str, Any] = {}
        twin.graph.add_edge(source, target, cost=cost, capacity=capacity, trust=trust, phantom=True)
        after = dict(twin.graph.edges[source, target])
        self._record("phantom_edge", f"{source}->{target}", before, after, note or "inserted phantom edge")

    def remove_edge(self, twin: DigitalTwin, source: str, target: str, note: str = "") -> None:
        before = dict(twin.graph.edges[source, target])
        twin.graph.remove_edge(source, target)
        after: Dict[str, Any] = {}
        self._record("remove_edge", f"{source}->{target}", before, after, note or "removed edge")

    def node_label_flip(self, twin: DigitalTwin, node: str, field: str, value: Any, note: str = "") -> None:
        attrs = twin.graph.nodes[node]
        before = dict(attrs)
        attrs[field] = value
        after = dict(attrs)
        self._record("node_label_flip", node, before, after, note or f"changed {field}")

    def queue_priority_shift(self, twin: DigitalTwin, node: str, new_priority: int, note: str = "") -> None:
        attrs = twin.graph.nodes[node]
        before = dict(attrs)
        attrs["priority"] = new_priority
        after = dict(attrs)
        self._record("queue_priority_shift", node, before, after, note or "changed triage priority")

    def inventory_shift(self, twin: DigitalTwin, node: str, delta: int, note: str = "") -> None:
        attrs = twin.graph.nodes[node]
        before = dict(attrs)
        attrs["stock"] = int(attrs.get("stock", 0)) + int(delta)
        after = dict(attrs)
        self._record("inventory_shift", node, before, after, note or f"shifted stock by {delta}")

    def apply_recipe(self, twin: DigitalTwin, recipe: Iterable[Dict[str, Any]]) -> list[MutationRecord]:
        self.history.clear()
        for step in recipe:
            op = step["op"]
            kwargs = {k: v for k, v in step.items() if k != "op"}
            method = getattr(self, op)
            method(twin, **kwargs)
        return list(self.history)
