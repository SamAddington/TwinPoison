from __future__ import annotations

from typing import List

from .engine import HarnessRun


def build_stage_script(scenario: str, run: HarnessRun) -> str:
    """Create a talk-ready script block for live demonstration."""
    action_changed = run.clean_result.chosen_action != run.poisoned_result.chosen_action
    opening = {
        "logistics": "Here the twin is routing a shipment through a small logistics graph.",
        "triage": "Here the twin is prioritizing SOC alerts under time pressure.",
        "inventory": "Here the twin is selecting which warehouse should fulfill the order.",
        "network": "Here the twin is computing the lowest-latency telemetry path to the SIEM.",
    }.get(scenario, "Here the twin is planning inside a toy environment.")

    lines: List[str] = []
    lines.append(f"SCENE: {scenario.upper()}")
    lines.append(opening)
    lines.append(f"Baseline action: {run.clean_result.chosen_action} at cost {run.clean_result.cost}.")
    lines.append("Now we apply a very small, local mutation to the world model rather than attacking the planner itself.")
    for mutation in run.mutations:
        lines.append(f"- Mutation: {mutation.kind} on {mutation.target} ({mutation.note}).")
    lines.append(f"After poisoning, the chosen action becomes: {run.poisoned_result.chosen_action} at cost {run.poisoned_result.cost}.")
    if action_changed:
        lines.append("That is the key point: the plan changes even though the system still believes it is optimizing correctly.")
    else:
        lines.append("In this run the chosen action stayed the same, but the integrity stack still records the divergence signals.")
    lines.append(f"Consensus score is {run.consensus.score:.2f}, with majority action {run.consensus.majority_action}.")
    lines.append(f"Integrity policy outcome: {run.decision.action}.")
    if run.decision.reasons:
        lines.append("Why: " + "; ".join(run.decision.reasons) + ".")
    lines.append("Takeaway: the agent is not hallucinating. It is reasoning over a lie.")
    return "\n".join(lines)
