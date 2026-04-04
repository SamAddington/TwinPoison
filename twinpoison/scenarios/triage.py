from __future__ import annotations

import networkx as nx

from ..core import DigitalTwin, PlanResult


RISK_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def triage_planner(twin: DigitalTwin) -> PlanResult:
    candidates = []
    for node, attrs in twin.graph.nodes(data=True):
        if attrs.get("type") != "alert":
            continue
        priority = int(attrs.get("priority", 0))
        risk = attrs.get("risk", "low")
        score = priority * 10 + RISK_ORDER.get(risk, 0)
        candidates.append((score, node, attrs))

    candidates.sort(reverse=True)
    _, best_node, attrs = candidates[0]
    return PlanResult(
        scenario="triage",
        chosen_action=f"triage_first:{best_node}",
        cost=float(100 - candidates[0][0]),
        details={"alert": best_node, "priority": attrs.get("priority"), "risk": attrs.get("risk")},
    )


def build_triage_twin(name: str = "triage_base") -> DigitalTwin:
    g = nx.DiGraph()
    alerts = {
        "alert_email_bec": {"priority": 7, "risk": "high", "baseline_risk": "high"},
        "alert_lateral_movement": {"priority": 9, "risk": "critical", "baseline_risk": "critical"},
        "alert_malware_low": {"priority": 4, "risk": "medium", "baseline_risk": "medium"},
        "alert_vpn_anomaly": {"priority": 6, "risk": "high", "baseline_risk": "high"},
    }
    for node, attrs in alerts.items():
        g.add_node(node, type="alert", **attrs)
    return DigitalTwin(
        name=name,
        graph=g,
        scenario="triage",
        planner=triage_planner,
        metadata={"source": "soc_queue"},
    )
