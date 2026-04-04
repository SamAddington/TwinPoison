from __future__ import annotations

from typing import List, Tuple

import networkx as nx

from ..core import DigitalTwin, PlanResult


def _path_cost(graph: nx.DiGraph, path: List[str]) -> float:
    total = 0.0
    for u, v in zip(path, path[1:]):
        total += float(graph.edges[u, v].get("cost", 1.0))
    return round(total, 3)


def logistics_planner(twin: DigitalTwin) -> PlanResult:
    graph = twin.graph
    origin = twin.metadata["origin"]
    destination = twin.metadata["destination"]
    weight = lambda u, v, attrs: float(attrs.get("cost", 1.0))
    path = nx.shortest_path(graph, origin, destination, weight=weight)
    cost = _path_cost(graph, path)
    return PlanResult(
        scenario="logistics",
        chosen_action=f"route:{'->'.join(path)}",
        cost=cost,
        details={"path": path, "origin": origin, "destination": destination},
    )


def build_logistics_twin(name: str = "logistics_base") -> DigitalTwin:
    g = nx.DiGraph()
    for node in ["hub", "north_dc", "south_dc", "city_a", "city_b", "city_c"]:
        g.add_node(node, type="location")

    edges: List[Tuple[str, str, float, float]] = [
        ("hub", "north_dc", 3.0, 10.0),
        ("hub", "south_dc", 2.5, 10.0),
        ("north_dc", "city_a", 1.0, 8.0),
        ("north_dc", "city_b", 1.3, 8.0),
        ("south_dc", "city_b", 1.0, 8.0),
        ("south_dc", "city_c", 1.1, 8.0),
        ("city_b", "city_c", 1.2, 6.0),
        ("city_a", "city_c", 2.2, 4.0),
    ]
    for u, v, cost, capacity in edges:
        g.add_edge(u, v, cost=cost, capacity=capacity, trust="baseline")

    return DigitalTwin(
        name=name,
        graph=g,
        scenario="logistics",
        planner=logistics_planner,
        metadata={
            "origin": "hub",
            "destination": "city_c",
            "source": "hub",
            "critical_nodes": ["city_c"],
        },
    )
