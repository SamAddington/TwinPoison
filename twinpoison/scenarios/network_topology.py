from __future__ import annotations

from typing import List

import networkx as nx

from ..core import DigitalTwin, PlanResult


def network_planner(twin: DigitalTwin) -> PlanResult:
    graph = twin.graph
    source = twin.metadata["origin"]
    target = twin.metadata["destination"]
    weight = lambda u, v, attrs: float(attrs.get("latency", attrs.get("cost", 1.0)))
    path = nx.shortest_path(graph, source, target, weight=weight)
    latency = 0.0
    for u, v in zip(path, path[1:]):
        latency += float(graph.edges[u, v].get("latency", graph.edges[u, v].get("cost", 1.0)))
    return PlanResult(
        scenario="network",
        chosen_action=f"reroute:{'->'.join(path)}",
        cost=round(latency, 3),
        details={"path": path, "latency": round(latency, 3)},
    )


def build_network_twin(name: str = "network_base") -> DigitalTwin:
    g = nx.DiGraph()
    nodes: List[str] = ["ingress", "core_a", "core_b", "ids", "siem", "seg_a", "seg_b"]
    for node in nodes:
        kind = "critical_service" if node in {"ids", "siem"} else "network"
        g.add_node(node, type=kind)

    edges = [
        ("ingress", "core_a", 1.0),
        ("ingress", "core_b", 1.2),
        ("core_a", "ids", 0.8),
        ("ids", "siem", 0.6),
        ("core_b", "seg_b", 1.0),
        ("core_a", "seg_a", 1.0),
        ("core_b", "siem", 2.2),
        ("seg_a", "siem", 1.4),
    ]
    for u, v, latency in edges:
        g.add_edge(u, v, latency=latency, cost=latency, capacity=10.0, trust="baseline")

    return DigitalTwin(
        name=name,
        graph=g,
        scenario="network",
        planner=network_planner,
        metadata={
            "origin": "ingress",
            "destination": "siem",
            "source": "ingress",
            "critical_nodes": ["ids", "siem"],
        },
    )
