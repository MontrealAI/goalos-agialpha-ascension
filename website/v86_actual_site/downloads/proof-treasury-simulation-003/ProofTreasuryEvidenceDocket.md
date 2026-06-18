# Proof Treasury Simulation 003 Evidence Docket

## Claim

$AGIALPHA can be modeled as a proof-conditioned economic control rail after proof exists. In this simulation, accepted proof must pass QA, claim-boundary, internal replay, and external replay before high-impact work can settle or receive capacity-scale allocation.

## Core law

```text
No proof -> no settlement.
No replay -> no settlement for high-impact work.
No external replay -> no capacity scale.
No governance -> no acceleration.
Proof first. Settlement second. $AGIALPHA only moves when proof changes state.
```

## Simulation status

- Total simulated $AGIALPHA budget: 10,000,000
- Simulated rewards released: 2,200,000
- Simulated locked pending replay: 2,600,000
- Simulated returned unsettled: 1,000,000
- Simulated work-object slashed: 210,000
- Simulated validator rewards: 120,000
- Simulated validator slashed: 154,000
- Alpha-Work Units recorded: 870.0
- Capacity auction pool: 800,000
- Capacity auction allocated: 800,000
- Token movement: false
- Mainnet broadcast: false

## Thermostat signals

```json
{
  "external_replay_pass_rate": 0.2857,
  "external_replay_fail_rate": 0.2857,
  "external_replay_pending_rate": 0.2857,
  "claim_boundary_fail_rate": 0.125,
  "qa_fail_rate": 0.125,
  "validator_false_verdict_rate": 0.2917,
  "proof_debt": 0.2381,
  "validator_pressure": "increase",
  "settlement_speed": "slow_until_external_replay",
  "capacity_scale_gate": "partial_external_replay_cleared",
  "next_epoch_policy": "increase_external_replay_grants_and_validator_bonds"
}
```

## Capacity auction

```json
{
  "AI-First Startup": 442070,
  "Enterprise Governance": 256894,
  "Regular-Person Utility": 101036
}
```

## Interpretation

Proof Treasury Simulation 001 showed that proof can gate simulated settlement. Proof Treasury Simulation 002 added replay-gated reinvestment. Proof Treasury Simulation 003 adds an external replay market, validator honesty scoring, and a replay-cleared capacity auction. The system does not reward generic output. It rewards proof-state transitions.

## Claim boundary

This docket does not claim achieved AGI, achieved ASI, achieved superintelligence, empirical SOTA, guaranteed ROI, token appreciation, production certification, external audit completion, real token movement, live Mainnet settlement, energy abundance, or Kardashev Type II achievement.
