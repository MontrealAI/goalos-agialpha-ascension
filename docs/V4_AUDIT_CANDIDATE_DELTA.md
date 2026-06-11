# v4.0 Audit-Candidate Delta

## Why v4.0 exists

v3.0 was strong architecturally, but the reference documents imply additional contract surfaces for a truly institutional release candidate:

- conformance levels;
- claim boundaries;
- replay evidence;
- commit-reveal validation;
- evaluator staking;
- slashing court;
- reward vault;
- chronicle;
- falsification reporting.

v4.0 implements those surfaces.

## AEP-001 alignment

GoalOS AEP-001 says:

- Do not put intelligence on-chain; put proof of intelligence on-chain.
- Aim -> Act -> Prove -> Evolve.
- No proof, no evolution. No eval, no propagation. No rollback, no release.
- Evidence Dockets are proof rooms, not marketing pages.
- The AEP contract suite should coordinate registries, attestations, evaluation, selection, economics, rollout, rollback, reward, and slashing.

## AGI ALPHA alignment

AGI ALPHA says:

- Request -> Escrow -> Execute -> Proof -> Validate -> Settle -> Chronicle.
- No ProofBundle, no settlement.
- No replay, no settlement.
- alpha-Work Units are settlement-grade metrology for verified work.
- AGIALPHA is a utility token for staking, settlement and coordination, not equity/profit/yield.

v4.0 is built around those invariants.
