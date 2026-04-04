from __future__ import annotations

from pathlib import Path

from twinpoison.cli import default_recipe
from twinpoison.engine import TwinPoisonHarness
from twinpoison.invariants import InvariantSuite
from twinpoison.reporting import ReportExporter
from twinpoison.scenarios import (
    build_inventory_twin,
    build_logistics_twin,
    build_network_twin,
    build_triage_twin,
)
from twinpoison.speaker import build_stage_script


SCENARIOS = {
    "logistics": build_logistics_twin,
    "triage": build_triage_twin,
    "inventory": build_inventory_twin,
    "network": build_network_twin,
}


def main() -> int:
    out = Path("exports")
    for name, builder in SCENARIOS.items():
        twin = builder()
        harness = TwinPoisonHarness(InvariantSuite(critical_nodes=twin.metadata.get("critical_nodes", [])))
        result = harness.run(
            baseline=twin,
            recipe=default_recipe(name),
            consensus_twins=[builder(f"{name}_alt_0"), builder(f"{name}_alt_1")],
            consensus_threshold=0.8,
        )
        paths = ReportExporter(out).export(name, result)
        print("=" * 72)
        print(build_stage_script(name, result))
        print(f"\nArtifacts: {paths.export_dir}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
