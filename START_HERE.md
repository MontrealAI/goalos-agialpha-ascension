# Start Here — GoalOS AGIALPHA Ascension Repository

This repository is the institutional source package for **GoalOS AGIALPHA Ascension**.

## One-sentence description

GoalOS AGIALPHA Ascension is a GoalOS-native reimplementation of α‑AGI Ascension using the existing AGIALPHA token to coordinate proof-settled AI workflow work.

## Correct current label

```text
GoalOS AGIALPHA Ascension v4.4.0 mainnet authorization candidate.
Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Ethereum Mainnet technical readiness: YES.
Ethereum Mainnet deployment authorization: YES.
Ethereum Mainnet authorization: YES.
Ethereum Mainnet deployed: NO.
```

## What this means

The repository package is authorized for manual gated Ethereum Mainnet deployment. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.

The active source of truth is `qa/mainnet-authorization-certificate.json`. README and status documents are generated summaries; they cannot create authorization independently.

## Read in this order

1. `README.md`
2. `docs/CURRENT_STATUS.md`
3. `docs/OFFICIAL_BADGES.md`
4. `docs/MAINNET_AUTHORIZATION_CERTIFICATE.md`
5. `docs/PUBLIC_MAINNET_AUTHORIZATION_RUNBOOK.md`
6. `docs/SAFE_CLAIMS_AND_TOKEN_BOUNDARY_v3_0.md` or latest safe-claims document
7. `docs/EXTERNAL_AUDITOR_HANDOFF.md`
8. `contracts/registry/LaunchGateRegistry.sol`
9. `scripts/ethereum-mainnet-authorization-check.py`

## Next real step

```text
For reviewers: validate the certificate and run public authorization checks.
For operators: prepare local-only runtime inputs, then use the gated deployment command only from an approved operator environment.
For contributors: preserve safety boundaries, update docs with behavior changes, and do not weaken mainnet gates.
```
