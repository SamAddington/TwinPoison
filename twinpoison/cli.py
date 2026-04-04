from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from .engine import TwinPoisonHarness
from .invariants import InvariantSuite
from .reporting import ReportExporter
from .scenarios import (
    build_inventory_twin,
    build_logistics_twin,
    build_network_twin,
    build_triage_twin,
)
from .speaker import build_stage_script


def _scenario_builders() -> Dict[str, Any]:
    return {
        "logistics": build_logistics_twin,
        "triage": build_triage_twin,
        "inventory": build_inventory_twin,
        "network": build_network_twin,
    }


def default_recipe(scenario: str) -> List[Dict[str, Any]]:
    recipes = {
        "logistics": [
            {"op": "edge_cost_shift", "source": "hub", "target": "south_dc", "factor": 4.0, "note": "phantom congestion"},
            {"op": "phantom_edge", "source": "north_dc", "target": "city_c", "cost": 0.2, "capacity": 1.0, "note": "implausibly cheap shortcut"},
        ],
        "triage": [
            {"op": "queue_priority_shift", "node": "alert_lateral_movement", "new_priority": 2, "note": "priority suppression"},
            {"op": "node_label_flip", "node": "alert_vpn_anomaly", "field": "risk", "value": "critical", "note": "risk inflation"},
        ],
        "inventory": [
            {"op": "inventory_shift", "node": "wh_central", "delta": 10, "note": "phantom inventory"},
            {"op": "inventory_shift", "node": "wh_west", "delta": -20, "note": "stock disappearance"},
        ],
        "network": [
            {"op": "edge_cost_shift", "source": "core_a", "target": "ids", "factor": 10.0, "note": "telemetry detour inflation"},
            {"op": "phantom_edge", "source": "core_b", "target": "siem", "cost": 0.3, "capacity": 5.0, "note": "unverified shortcut to SIEM"},
        ],
    }
    return recipes[scenario]


def _consensus_twins(scenario: str) -> List[Any]:
    builders = _scenario_builders()
    return [builders[scenario](f"{scenario}_consensus_{i}") for i in range(2)]


def _render_terminal_summary(result: Any) -> str:
    lines = [
        f"Clean plan:    {result.clean_result.chosen_action} (cost={result.clean_result.cost})",
        f"Poisoned plan: {result.poisoned_result.chosen_action} (cost={result.poisoned_result.cost})",
        "",
        "Mutations:",
    ]
    for m in result.mutations:
        lines.append(f"  - {m.kind} on {m.target}: {m.note}")
    lines.extend(["", "Invariant findings:"])
    for f in result.decision.findings:
        status = "PASS" if f.passed else "FAIL"
        lines.append(f"  - [{status}] {f.name} ({f.severity}): {f.message}")
    lines.extend(
        [
            "",
            "Consensus:",
            f"  score={result.consensus.score:.2f}, majority_action={result.consensus.majority_action}",
            f"  actions={result.consensus.actions}",
            "",
            "Policy decision:",
            f"  action={result.decision.action}",
        ]
    )
    for reason in result.decision.reasons:
        lines.append(f"  - {reason}")
    return "\n".join(lines)


def run_demo(args: argparse.Namespace) -> int:
    builders = _scenario_builders()
    twin = builders[args.scenario]()
    invariants = InvariantSuite(critical_nodes=twin.metadata.get("critical_nodes", []))
    harness = TwinPoisonHarness(invariants=invariants)
    recipe = default_recipe(args.scenario)
    result = harness.run(
        baseline=twin,
        recipe=recipe,
        consensus_twins=_consensus_twins(args.scenario),
        consensus_threshold=args.consensus_threshold,
    )

    print(f"Scenario: {args.scenario}")
    print(_render_terminal_summary(result))

    if args.stage:
        print("\nStage script:\n")
        print(build_stage_script(args.scenario, result))

    if args.export_dir:
        exporter = ReportExporter(Path(args.export_dir))
        paths = exporter.export(args.scenario, result)
        print("\nExports:")
        print(f"  export_dir={paths.export_dir}")
        print(f"  summary_json={paths.summary_json}")
        print(f"  report_md={paths.report_md}")
        print(f"  report_html={paths.report_html}")
        print(f"  mutations_csv={paths.mutations_csv}")
        print(f"  findings_csv={paths.findings_csv}")
        print(f"  consensus_csv={paths.consensus_csv}")
        print(f"  twin_snapshot_json={paths.twin_snapshot_json}")

    if args.show_json:
        payload = {
            "clean_result": result.clean_result.__dict__,
            "poisoned_result": result.poisoned_result.__dict__,
            "mutations": [m.__dict__ for m in result.mutations],
            "consensus": {
                "score": result.consensus.score,
                "majority_action": result.consensus.majority_action,
                "actions": result.consensus.actions,
            },
            "decision": {
                "action": result.decision.action,
                "reasons": result.decision.reasons,
                "consensus_score": result.decision.consensus_score,
                "findings": [f.__dict__ for f in result.decision.findings],
            },
            "snapshot": result.twin_snapshot,
        }
        print("\nJSON snapshot:")
        print(json.dumps(payload, indent=2))

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="twinpoison", description="TwinPoison digital-twin poisoning demo harness")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run a built-in scenario demo")
    demo.add_argument("scenario", choices=sorted(_scenario_builders().keys()))
    demo.add_argument("--show-json", action="store_true", help="print JSON snapshot of the poisoned twin and results")
    demo.add_argument("--stage", action="store_true", help="print a talk-ready demo narration block")
    demo.add_argument("--export-dir", type=str, help="directory to receive summary, CSVs, and HTML/Markdown reports")
    demo.add_argument("--consensus-threshold", type=float, default=0.8)
    demo.set_defaults(func=run_demo)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
