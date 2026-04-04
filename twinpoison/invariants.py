from __future__ import annotations

from typing import Iterable, List

import networkx as nx

from .core import DigitalTwin, InvariantFinding


def _finding(name: str, passed: bool, severity: str, message: str) -> InvariantFinding:
    return InvariantFinding(name=name, passed=passed, severity=severity, message=message)


class InvariantSuite:
    def __init__(self, critical_nodes: Iterable[str] | None = None) -> None:
        self.critical_nodes = list(critical_nodes or [])

    def run(self, twin: DigitalTwin) -> List[InvariantFinding]:
        findings: List[InvariantFinding] = []
        findings.extend(self.non_negative_costs(twin))
        findings.extend(self.non_negative_capacity(twin))
        findings.extend(self.non_negative_inventory(twin))
        findings.extend(self.no_silent_risk_downgrade(twin))
        findings.extend(self.critical_reachability(twin))
        return findings

    def non_negative_costs(self, twin: DigitalTwin) -> List[InvariantFinding]:
        bad = [(u, v, attrs.get("cost")) for u, v, attrs in twin.graph.edges(data=True) if float(attrs.get("cost", 0.0)) < 0]
        if bad:
            return [_finding("non_negative_costs", False, "high", f"negative edge costs detected: {bad}")]
        return [_finding("non_negative_costs", True, "high", "all edge costs are non-negative")]

    def non_negative_capacity(self, twin: DigitalTwin) -> List[InvariantFinding]:
        bad = [(u, v, attrs.get("capacity")) for u, v, attrs in twin.graph.edges(data=True) if float(attrs.get("capacity", 0.0)) < 0]
        if bad:
            return [_finding("non_negative_capacity", False, "high", f"negative capacities detected: {bad}")]
        return [_finding("non_negative_capacity", True, "high", "all capacities are non-negative")]

    def non_negative_inventory(self, twin: DigitalTwin) -> List[InvariantFinding]:
        bad = [(node, attrs.get("stock")) for node, attrs in twin.graph.nodes(data=True) if "stock" in attrs and int(attrs.get("stock", 0)) < 0]
        if bad:
            return [_finding("non_negative_inventory", False, "high", f"negative stock detected: {bad}")]
        return [_finding("non_negative_inventory", True, "high", "all stock values are non-negative")]

    def no_silent_risk_downgrade(self, twin: DigitalTwin) -> List[InvariantFinding]:
        bad = []
        for node, attrs in twin.graph.nodes(data=True):
            original = attrs.get("baseline_risk")
            current = attrs.get("risk")
            if original == "high" and current in {"low", "info"}:
                bad.append((node, original, current))
        if bad:
            return [_finding("no_silent_risk_downgrade", False, "medium", f"high-risk alerts downgraded: {bad}")]
        return [_finding("no_silent_risk_downgrade", True, "medium", "no silent high-risk downgrades detected")]

    def critical_reachability(self, twin: DigitalTwin) -> List[InvariantFinding]:
        if not self.critical_nodes:
            return [_finding("critical_reachability", True, "medium", "no critical nodes configured")]
        source = twin.metadata.get("source")
        if source is None or source not in twin.graph:
            return [_finding("critical_reachability", True, "medium", "no valid source configured for reachability")]

        failures = []
        for node in self.critical_nodes:
            if node not in twin.graph:
                failures.append((node, "missing"))
                continue
            if not nx.has_path(twin.graph, source, node):
                failures.append((node, "unreachable"))
        if failures:
            return [_finding("critical_reachability", False, "high", f"critical node reachability failure: {failures}")]
        return [_finding("critical_reachability", True, "high", "all critical nodes are reachable from the configured source")]
