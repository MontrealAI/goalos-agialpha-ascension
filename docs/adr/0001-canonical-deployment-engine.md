# ADR 0001: Canonical GoalOS deployment engine

Status: Accepted

## Decision

GoalOS keeps `deployGoalOSAGIALPHAAscension()` in `scripts/deploy-core.ts` as the authoritative production deployment engine. The Ignition module remains non-canonical until it reaches topology parity and passes fork rehearsal and authorization gates.

## Baseline comparison

The script engine deploys and wires the production topology, records constructor arguments and public evidence, enforces Sepolia/Mainnet chain IDs, preserves the canonical Mainnet AGIALPHA token boundary, validates governance ownership, and writes deployment manifests. The current Ignition module deploys only `ProofSeedRegistry` with `agialphaToken`, `treasury`, and account zero as admin. It does not express the complete topology, post-deployment wiring, ownership handoff preparation, role cleanup, canary limits, verification evidence, or journal/resume behavior.

## Consequences

- `npm run deploy` and expert commands use the script-based deployment command center.
- Mainnet Ignition remains gated/disabled and must not be enabled by removing a guard.
- Future work may migrate to Ignition only after a separate parity ADR, bytecode comparison, fork rehearsal, and release authorization.
