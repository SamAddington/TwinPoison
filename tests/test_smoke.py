from pathlib import Path

from twinpoison.engine import TwinPoisonHarness
from twinpoison.invariants import InvariantSuite
from twinpoison.reporting import ReportExporter
from twinpoison.scenarios import build_logistics_twin


def test_logistics_smoke() -> None:
    twin = build_logistics_twin()
    harness = TwinPoisonHarness(InvariantSuite(critical_nodes=twin.metadata.get("critical_nodes", [])))
    recipe = [
        {"op": "edge_cost_shift", "source": "hub", "target": "south_dc", "factor": 5.0},
        {"op": "phantom_edge", "source": "north_dc", "target": "city_c", "cost": 0.1},
    ]
    result = harness.run(twin, recipe, consensus_twins=[build_logistics_twin("alt")])
    assert result.clean_result.scenario == "logistics"
    assert result.poisoned_result.scenario == "logistics"
    assert result.mutations
    assert result.decision.action in {"allow", "review", "block"}


def test_report_export(tmp_path: Path) -> None:
    twin = build_logistics_twin()
    harness = TwinPoisonHarness(InvariantSuite(critical_nodes=twin.metadata.get("critical_nodes", [])))
    recipe = [
        {"op": "edge_cost_shift", "source": "hub", "target": "south_dc", "factor": 5.0},
        {"op": "phantom_edge", "source": "north_dc", "target": "city_c", "cost": 0.1},
    ]
    result = harness.run(twin, recipe, consensus_twins=[build_logistics_twin("alt")])
    bundle = ReportExporter(tmp_path).export("logistics", result)
    assert bundle.summary_json.exists()
    assert bundle.report_html.exists()
    assert bundle.mutations_csv.exists()
