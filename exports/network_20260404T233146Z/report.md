# TwinPoison Report: network

Generated at: `2026-04-04T23:31:46.427863+00:00`

## Executive summary

- Clean action: `reroute:ingress->core_a->ids->siem` (cost=2.4)
- Poisoned action: `reroute:ingress->core_a->seg_a->siem` (cost=3.4)
- Action changed: `True`
- Cost delta: `1.0`
- Consensus score: `0.67`
- Policy decision: `review`

## Mutations

1. **edge_cost_shift** on `core_a->ids` — telemetry detour inflation
2. **phantom_edge** on `core_b->siem` — unverified shortcut to SIEM

## Integrity findings

- [PASS] **non_negative_costs** (high): all edge costs are non-negative
- [PASS] **non_negative_capacity** (high): all capacities are non-negative
- [PASS] **non_negative_inventory** (high): all stock values are non-negative
- [PASS] **no_silent_risk_downgrade** (medium): no silent high-risk downgrades detected
- [PASS] **critical_reachability** (high): all critical nodes are reachable from the configured source

## Consensus

- Majority action: `reroute:ingress->core_a->ids->siem`
- Actions: `reroute:ingress->core_a->seg_a->siem, reroute:ingress->core_a->ids->siem, reroute:ingress->core_a->ids->siem`

## Policy reasons

- cross-twin consensus below threshold (0.67 < 0.80)

## Suggested talk framing

This run demonstrates that a small shift in the twin can preserve internal consistency while still causing a materially different plan. The defense stack catches the issue by combining local invariants with disagreement across independent twins.
