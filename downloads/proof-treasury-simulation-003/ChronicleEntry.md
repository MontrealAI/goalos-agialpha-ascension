# Chronicle Entry — Proof Treasury Simulation 003

Proof Treasury Simulation 003 advanced the proof treasury from replay-gated reinvestment to external replay market and replay-cleared capacity allocation.

What worked:
- Externally replay-passed work received simulated settlement and alpha-Work Units.
- External replay pending or failed work did not receive capacity-scale allocation.
- Claim-boundary failure overrode all value scores.
- Validator false or unsafe approvals produced simulated slashing and trust penalties.
- Capacity auction allocated only to replay-cleared eligible domains.

Reusable capability:
- External Replay Market ledger.
- Validator honesty / slashing simulation.
- Replay-cleared capacity auction.
- ProofDebtLedger for repair routing.
- No-token-movement certificate.

Next mission:
Proof Treasury Simulation 004: delayed-outcome gauntlet and multi-epoch capacity compounding, where previous capacity allocations must improve future proof production under equal-budget controls.
