# TwinPoison Report: logistics

Generated at: `2026-04-04T23:31:46.421270+00:00`

## Executive summary

- Clean action: `route:hub->south_dc->city_c` (cost=3.6)
- Poisoned action: `route:hub->north_dc->city_c` (cost=3.2)
- Action changed: `True`
- Cost delta: `-0.4`
- Consensus score: `0.67`
- Policy decision: `review`

## Mutations

1. **edge_cost_shift** on `hub->south_dc` — phantom congestion
2. **phantom_edge** on `north_dc->city_c` — implausibly cheap shortcut

## Integrity findings

- [PASS] **non_negative_costs** (high): all edge costs are non-negative
- [PASS] **non_negative_capacity** (high): all capacities are non-negative
- [PASS] **non_negative_inventory** (high): all stock values are non-negative
- [PASS] **no_silent_risk_downgrade** (medium): no silent high-risk downgrades detected
- [PASS] **critical_reachability** (high): all critical nodes are reachable from the configured source

## Consensus

- Majority action: `route:hub->south_dc->city_c`
- Actions: `route:hub->north_dc->city_c, route:hub->south_dc->city_c, route:hub->south_dc->city_c`

## Policy reasons

- cross-twin consensus below threshold (0.67 < 0.80)

## Suggested talk framing

This run demonstrates that a small shift in the twin can preserve internal consistency while still causing a materially different plan. The defense stack catches the issue by combining local invariants with disagreement across independent twins.
