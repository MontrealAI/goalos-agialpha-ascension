# Mainnet Stage-A Completion Plan

This plan preserves the Stage-A/Stage-B/Stage-C claim boundary. Stage A may authorize predeployment only from release-bound Sepolia evidence, genuine pinned Mainnet-fork evidence, real Gate 1-5 producers, and a complete immutable deployment plan.

## Current status

- No Mainnet or Sepolia broadcast is authorized by this document.
- Missing protected inputs remain external if the approved protected evidence roots and RPC variables are absent.
- Aggregate gate packages and shallow self-declared PASS files must fail closed.

## Completion loop

1. Freeze a clean release commit and record compiler, artifact, source, package-lock, Hardhat, deployment-script, authority-policy, and evidence schema hashes.
2. Discover protected evidence through the approved environment variables and fallback roots.
3. Validate each evidence artifact independently, including requirement-specific evidence paths, evidence hashes, raw commitments, producer IDs, tool versions, execution timestamps, release binding, and fork/plan bindings.
4. Generate the nonce-bound deployment plan with one sanitized public entry per transaction and private constructor inputs in a mode-0600 private plan.
5. Pin a genuine Mainnet fork using two independent RPC providers, verify canonical AGIALPHA code through both, deploy the exact topology with Wallet A impersonated only as sender and Wallet B as permanent authority, and preserve raw fork receipts/readbacks.
6. Execute Gate 1 authority, Gate 2 override, Gate 3 accounting/limits, Gate 4 lifecycle, and Gate 5 assurance producers.
7. Generate sanitized public commitments, derive gate statuses from requirement evidence, generate the Stage-A certificate, and independently validate all hashes and bindings.
8. Keep Stage B and Stage C blocked until real chain-1 deployment/verification and production activation evidence exists.

## External inputs that cannot be fabricated

- `MAINNET_FORK_RPC_URL` and `SECONDARY_MAINNET_RPC_URL` (or compatible legacy secondary variable).
- Protected release-bound Gate evidence, raw fork receipts/readbacks, Sepolia evidence or operator authorization to broadcast a fresh Sepolia rehearsal, Ledger owner proof, and private deployment-plan constructor inputs.
