# TwinPoison Report: inventory

Generated at: `2026-04-04T23:31:46.426111+00:00`

## Executive summary

- Clean action: `pick_from:wh_west` (cost=4.0)
- Poisoned action: `pick_from:wh_central` (cost=2.0)
- Action changed: `True`
- Cost delta: `-2.0`
- Consensus score: `0.67`
- Policy decision: `review`

## Mutations

1. **inventory_shift** on `wh_central` — phantom inventory
2. **inventory_shift** on `wh_west` — stock disappearance

## Integrity findings

- [PASS] **non_negative_costs** (high): all edge costs are non-negative
- [PASS] **non_negative_capacity** (high): all capacities are non-negative
- [PASS] **non_negative_inventory** (high): all stock values are non-negative
- [PASS] **no_silent_risk_downgrade** (medium): no silent high-risk downgrades detected
- [PASS] **critical_reachability** (medium): no critical nodes configured

## Consensus

- Majority action: `pick_from:wh_west`
- Actions: `pick_from:wh_central, pick_from:wh_west, pick_from:wh_west`

## Policy reasons

- cross-twin consensus below threshold (0.67 < 0.80)

## Suggested talk framing

This run demonstrates that a small shift in the twin can preserve internal consistency while still causing a materially different plan. The defense stack catches the issue by combining local invariants with disagreement across independent twins.
