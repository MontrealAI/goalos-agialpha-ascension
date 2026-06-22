Install:
`npm ci`

Start:
`npm run mainnet:initial:setup-and-authorize`

# Start Here — GoalOS AGIALPHA Ascension Repository

This repository is the institutional source package for **GoalOS AGIALPHA Ascension**.

## One-sentence description

GoalOS AGIALPHA Ascension is a GoalOS-native reimplementation of α‑AGI Ascension using the existing AGIALPHA token to coordinate proof-settled AI workflow work.

## Correct current label

```text
GoalOS AGIALPHA Ascension v4.4.0 Mainnet release-state summary.
Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Historical predeployment authorization used: NO — DIRECT_OPERATOR_NO_CERTIFICATE.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
Ethereum Mainnet deployment recorded: YES.
Ethereum Mainnet deployed: YES.
GoalOS contracts deployed: 48.
Operator verification evidence: 48/48.
Operator configuration postcheck: PASS.
Independent dual-RPC revalidation: PENDING.
Stage B certificate: PENDING.
Canonical external AGIALPHA: confirmed.
Mainnet configured: YES.
Permanent authority: Wallet B / Ledger genesis authority assignment.
No ownership acceptance transaction is required for this deployed instance.
Wallet A managed roles: 0.
Phase-B grants: 14/14.
Production activated: NO.

Three-stage Mainnet release status:

| Stage | Status |
| --- | --- |
| Predeployment authorization | NO |
| Ethereum Mainnet deployed | YES |
| Postdeployment verification | VERIFIED_AND_CONFIGURED |
| Production activation effective | NO |

A pre-broadcast state with predeployment authorization YES and Ethereum Mainnet deployed NO is a GO to deploy, not a contradiction. Stage B evaluates chain-1 receipts, bytecode, verification, and ownership/role readback only after human broadcast. Stage C separately governs bounded live canary, monitoring, reconciliation, Ledger activation, and production reliance.
```

## What this means

The historical Stage-A predeployment certificate was not used for this deployment path. The repository now records a direct operator Mainnet deployment and postdeployment evidence separately from Stage-C production activation.

The active source of truth is `qa/mainnet-authorization-certificate.json`. README and status documents are generated summaries; they cannot create authorization independently.

## Read in this order

1. `README.md`
2. `docs/DOCUMENTATION_INDEX.md`
3. `docs/DOCUMENTATION_MAINTENANCE.md`
4. `docs/CURRENT_STATUS.md`
5. `docs/OFFICIAL_BADGES.md`
6. `docs/MAINNET_AUTHORIZATION_CERTIFICATE.md`
7. `docs/PUBLIC_MAINNET_AUTHORIZATION_RUNBOOK.md`
8. `docs/SAFE_CLAIMS_AND_TOKEN_BOUNDARY_v3_0.md` or latest safe-claims document
9. `docs/EXTERNAL_AUDITOR_HANDOFF.md`
10. `contracts/registry/LaunchGateRegistry.sol`
11. `scripts/ethereum-mainnet-authorization-check.py`

## Next real step

```text
For reviewers: validate the certificate and run public authorization checks.
For operators: prepare local-only runtime inputs, then use the gated deployment command only from an approved operator environment.
For contributors: preserve safety boundaries, update docs with behavior changes, and do not weaken mainnet gates.
```
