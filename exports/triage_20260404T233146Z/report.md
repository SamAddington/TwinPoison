# TwinPoison Report: triage

Generated at: `2026-04-04T23:31:46.423874+00:00`

## Executive summary

- Clean action: `triage_first:alert_lateral_movement` (cost=6.0)
- Poisoned action: `triage_first:alert_email_bec` (cost=27.0)
- Action changed: `True`
- Cost delta: `21.0`
- Consensus score: `0.67`
- Policy decision: `review`

## Mutations

1. **queue_priority_shift** on `alert_lateral_movement` — priority suppression
2. **node_label_flip** on `alert_vpn_anomaly` — risk inflation

## Integrity findings

- [PASS] **non_negative_costs** (high): all edge costs are non-negative
- [PASS] **non_negative_capacity** (high): all capacities are non-negative
- [PASS] **non_negative_inventory** (high): all stock values are non-negative
- [PASS] **no_silent_risk_downgrade** (medium): no silent high-risk downgrades detected
- [PASS] **critical_reachability** (medium): no critical nodes configured

## Consensus

- Majority action: `triage_first:alert_lateral_movement`
- Actions: `triage_first:alert_email_bec, triage_first:alert_lateral_movement, triage_first:alert_lateral_movement`

## Policy reasons

- cross-twin consensus below threshold (0.67 < 0.80)

## Suggested talk framing

This run demonstrates that a small shift in the twin can preserve internal consistency while still causing a materially different plan. The defense stack catches the issue by combining local invariants with disagreement across independent twins.
