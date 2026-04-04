from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Dict, List

from .engine import HarnessRun


@dataclass
class ExportBundlePaths:
    export_dir: Path
    summary_json: Path
    mutations_csv: Path
    findings_csv: Path
    consensus_csv: Path
    twin_snapshot_json: Path
    report_md: Path
    report_html: Path


class ReportExporter:
    """Export a harness run into portable artifacts for demos, papers, and CI."""

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, scenario: str, run: HarnessRun) -> ExportBundlePaths:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        export_dir = self.output_dir / f"{scenario}_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)

        paths = ExportBundlePaths(
            export_dir=export_dir,
            summary_json=export_dir / "summary.json",
            mutations_csv=export_dir / "mutations.csv",
            findings_csv=export_dir / "findings.csv",
            consensus_csv=export_dir / "consensus.csv",
            twin_snapshot_json=export_dir / "twin_snapshot.json",
            report_md=export_dir / "report.md",
            report_html=export_dir / "report.html",
        )

        payload = self._summary_payload(scenario, run)
        paths.summary_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        paths.twin_snapshot_json.write_text(json.dumps(run.twin_snapshot, indent=2), encoding="utf-8")
        self._write_mutations_csv(paths.mutations_csv, run)
        self._write_findings_csv(paths.findings_csv, run)
        self._write_consensus_csv(paths.consensus_csv, run)
        paths.report_md.write_text(self._render_markdown_report(payload), encoding="utf-8")
        paths.report_html.write_text(self._render_html_report(payload), encoding="utf-8")
        return paths

    def _summary_payload(self, scenario: str, run: HarnessRun) -> Dict[str, Any]:
        return {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "scenario": scenario,
            "summary": {
                "clean_action": run.clean_result.chosen_action,
                "clean_cost": run.clean_result.cost,
                "poisoned_action": run.poisoned_result.chosen_action,
                "poisoned_cost": run.poisoned_result.cost,
                "action_changed": run.clean_result.chosen_action != run.poisoned_result.chosen_action,
                "cost_delta": round(run.poisoned_result.cost - run.clean_result.cost, 3),
                "consensus_score": run.consensus.score,
                "majority_action": run.consensus.majority_action,
                "policy_decision": run.decision.action,
            },
            "clean_result": asdict(run.clean_result),
            "poisoned_result": asdict(run.poisoned_result),
            "mutations": [asdict(m) for m in run.mutations],
            "consensus": {
                "score": run.consensus.score,
                "majority_action": run.consensus.majority_action,
                "actions": run.consensus.actions,
                "results": [asdict(result) for result in run.consensus.results],
            },
            "decision": {
                "action": run.decision.action,
                "reasons": list(run.decision.reasons),
                "consensus_score": run.decision.consensus_score,
                "findings": [asdict(f) for f in run.decision.findings],
            },
        }

    def _write_mutations_csv(self, path: Path, run: HarnessRun) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["kind", "target", "note", "before", "after"])
            writer.writeheader()
            for mutation in run.mutations:
                writer.writerow(
                    {
                        "kind": mutation.kind,
                        "target": mutation.target,
                        "note": mutation.note,
                        "before": json.dumps(mutation.before, sort_keys=True),
                        "after": json.dumps(mutation.after, sort_keys=True),
                    }
                )

    def _write_findings_csv(self, path: Path, run: HarnessRun) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["name", "passed", "severity", "message"])
            writer.writeheader()
            for finding in run.decision.findings:
                writer.writerow(asdict(finding))

    def _write_consensus_csv(self, path: Path, run: HarnessRun) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["twin_index", "scenario", "chosen_action", "cost", "details"])
            writer.writeheader()
            for index, result in enumerate(run.consensus.results):
                writer.writerow(
                    {
                        "twin_index": index,
                        "scenario": result.scenario,
                        "chosen_action": result.chosen_action,
                        "cost": result.cost,
                        "details": json.dumps(result.details, sort_keys=True),
                    }
                )

    def _render_markdown_report(self, payload: Dict[str, Any]) -> str:
        summary = payload["summary"]
        decision = payload["decision"]
        mutations = payload["mutations"]
        consensus = payload["consensus"]
        lines: List[str] = []
        lines.append(f"# TwinPoison Report: {payload['scenario']}")
        lines.append("")
        lines.append(f"Generated at: `{payload['generated_at_utc']}`")
        lines.append("")
        lines.append("## Executive summary")
        lines.append("")
        lines.append(f"- Clean action: `{summary['clean_action']}` (cost={summary['clean_cost']})")
        lines.append(f"- Poisoned action: `{summary['poisoned_action']}` (cost={summary['poisoned_cost']})")
        lines.append(f"- Action changed: `{summary['action_changed']}`")
        lines.append(f"- Cost delta: `{summary['cost_delta']}`")
        lines.append(f"- Consensus score: `{summary['consensus_score']:.2f}`")
        lines.append(f"- Policy decision: `{summary['policy_decision']}`")
        lines.append("")
        lines.append("## Mutations")
        lines.append("")
        for idx, mutation in enumerate(mutations, start=1):
            lines.append(f"{idx}. **{mutation['kind']}** on `{mutation['target']}` — {mutation['note']}")
        lines.append("")
        lines.append("## Integrity findings")
        lines.append("")
        for finding in decision["findings"]:
            status = "PASS" if finding["passed"] else "FAIL"
            lines.append(f"- [{status}] **{finding['name']}** ({finding['severity']}): {finding['message']}")
        lines.append("")
        lines.append("## Consensus")
        lines.append("")
        lines.append(f"- Majority action: `{consensus['majority_action']}`")
        lines.append(f"- Actions: `{', '.join(consensus['actions'])}`")
        lines.append("")
        lines.append("## Policy reasons")
        lines.append("")
        for reason in decision["reasons"]:
            lines.append(f"- {reason}")
        lines.append("")
        lines.append("## Suggested talk framing")
        lines.append("")
        lines.append(
            "This run demonstrates that a small shift in the twin can preserve internal consistency while still causing a materially different plan. The defense stack catches the issue by combining local invariants with disagreement across independent twins."
        )
        lines.append("")
        return "\n".join(lines)

    def _render_html_report(self, payload: Dict[str, Any]) -> str:
        summary = payload["summary"]
        findings_html = "".join(
            f"<tr><td>{escape(item['name'])}</td><td>{'PASS' if item['passed'] else 'FAIL'}</td><td>{escape(item['severity'])}</td><td>{escape(item['message'])}</td></tr>"
            for item in payload["decision"]["findings"]
        )
        mutations_html = "".join(
            f"<tr><td>{escape(item['kind'])}</td><td>{escape(item['target'])}</td><td>{escape(item['note'])}</td></tr>"
            for item in payload["mutations"]
        )
        reasons_html = "".join(f"<li>{escape(reason)}</li>" for reason in payload["decision"]["reasons"])
        actions_html = "".join(
            f"<li>Twin {idx}: <code>{escape(result['chosen_action'])}</code> (cost={result['cost']})</li>"
            for idx, result in enumerate(payload["consensus"]["results"])
        )
        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>TwinPoison Report - {escape(payload['scenario'])}</title>
  <style>
    body {{ font-family: Arial, Helvetica, sans-serif; margin: 2rem; color: #111827; }}
    h1, h2 {{ margin-bottom: 0.4rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: 1rem; margin: 1.2rem 0 1.4rem; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 14px; padding: 1rem; background: #f9fafb; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 1.5rem; }}
    th, td {{ border: 1px solid #d1d5db; padding: 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 6px; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  </style>
</head>
<body>
  <h1>TwinPoison Report: {escape(payload['scenario'])}</h1>
  <p class=\"mono\">Generated at: {escape(payload['generated_at_utc'])}</p>
  <div class=\"grid\">
    <div class=\"card\"><strong>Clean action</strong><br><code>{escape(summary['clean_action'])}</code><br>cost={summary['clean_cost']}</div>
    <div class=\"card\"><strong>Poisoned action</strong><br><code>{escape(summary['poisoned_action'])}</code><br>cost={summary['poisoned_cost']}</div>
    <div class=\"card\"><strong>Policy decision</strong><br><code>{escape(summary['policy_decision'])}</code><br>consensus={summary['consensus_score']:.2f}</div>
  </div>
  <h2>Mutations</h2>
  <table>
    <thead><tr><th>Kind</th><th>Target</th><th>Note</th></tr></thead>
    <tbody>{mutations_html}</tbody>
  </table>
  <h2>Integrity findings</h2>
  <table>
    <thead><tr><th>Name</th><th>Status</th><th>Severity</th><th>Message</th></tr></thead>
    <tbody>{findings_html}</tbody>
  </table>
  <h2>Consensus actions</h2>
  <ul>{actions_html}</ul>
  <h2>Policy reasons</h2>
  <ul>{reasons_html}</ul>
  <h2>Why this matters</h2>
  <p>This export is designed for live demos, CI artifacts, and paper appendices. It preserves both the mutation trace and the integrity-policy outcome in a format that is easy to inspect, archive, and compare across runs.</p>
</body>
</html>
"""
