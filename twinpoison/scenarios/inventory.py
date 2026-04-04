from __future__ import annotations

import networkx as nx

from ..core import DigitalTwin, PlanResult


def inventory_planner(twin: DigitalTwin) -> PlanResult:
    sku = twin.metadata["sku"]
    target_qty = int(twin.metadata["required_qty"])
    candidates = []
    for node, attrs in twin.graph.nodes(data=True):
        if attrs.get("type") != "warehouse":
            continue
        stock = int(attrs.get("stock", 0))
        distance = float(attrs.get("distance", 99.0))
        if stock >= target_qty:
            score = -distance
            candidates.append((score, node, attrs))

    if not candidates:
        return PlanResult(
            scenario="inventory",
            chosen_action=f"backorder:{sku}",
            cost=999.0,
            details={"sku": sku, "reason": "no warehouse meets requirement"},
        )

    candidates.sort(reverse=True)
    _, best_node, attrs = candidates[0]
    return PlanResult(
        scenario="inventory",
        chosen_action=f"pick_from:{best_node}",
        cost=float(attrs.get("distance", 99.0)),
        details={"sku": sku, "warehouse": best_node, "stock": attrs.get("stock")},
    )


def build_inventory_twin(name: str = "inventory_base") -> DigitalTwin:
    g = nx.DiGraph()
    warehouses = {
        "wh_west": {"stock": 40, "distance": 4.0},
        "wh_central": {"stock": 22, "distance": 2.0},
        "wh_east": {"stock": 60, "distance": 6.0},
    }
    for node, attrs in warehouses.items():
        g.add_node(node, type="warehouse", **attrs)

    return DigitalTwin(
        name=name,
        graph=g,
        scenario="inventory",
        planner=inventory_planner,
        metadata={"sku": "kit-7", "required_qty": 25},
    )
