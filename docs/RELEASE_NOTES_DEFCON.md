# TwinPoison DEF CON Demo Release Notes

## Release focus

This package is shaped as a conference-ready, simulation-only artifact for demonstrating world-model poisoning in a safe, reproducible way.

## New in v0.2.0

- Added a stage-oriented CLI flow with `--stage`
- Added export bundles with JSON, CSV, Markdown, and HTML outputs
- Added `examples/defcon_showcase.py` for a four-scenario sequence
- Added `docs/DEFCON_DEMO_RUNBOOK.md` with suggested stage flow
- Added architecture figures in SVG and PNG formats
- Added regression tests for artifact export

## Recommended live-demo path

1. Run one scenario from the CLI with `--stage --export-dir exports`
2. Open the generated `report.html`
3. Show `summary.json` and `mutations.csv` briefly for reproducibility
4. Use the architecture figure to explain where integrity checks sit relative to the planner

## Safety posture

TwinPoison remains a toy-simulation research artifact. It is intended for defensive research, teaching, and conference demonstration, not for operating against real environments.
