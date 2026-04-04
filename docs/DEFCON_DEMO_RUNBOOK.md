# TwinPoison DEF CON Demo Runbook

## Live flow

1. Start with the clean twin and explain the planner objective.
2. Show the baseline action and baseline cost.
3. Apply one or two local mutations to the digital twin.
4. Re-run the planner and highlight the changed action.
5. Show cross-twin disagreement and invariant findings.
6. End on the policy outcome: allow, review, or block.

## Suggested command sequence

```bash
python -m pip install -e .

twinpoison demo logistics --stage --export-dir exports
twinpoison demo triage --stage --export-dir exports
twinpoison demo inventory --stage --export-dir exports
twinpoison demo network --stage --export-dir exports
```

## Stage cues

- "We are not attacking the model weights."
- "We are not attacking the downstream tool."
- "We are poisoning the thing the planner thinks is reality."
- "The action still looks internally rational."
- "That is why integrity checks must sit outside the planner."

## Files worth showing on screen

- `report.html` for a clean audience-friendly artifact
- `summary.json` for reproducibility
- `mutations.csv` and `findings.csv` for research workflows
- `docs/figures/twinpoison_architecture.svg` for the architecture slide
