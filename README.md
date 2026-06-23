# GoalOS AGIALPHA Ascension

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)

GoalOS AGIALPHA Ascension is an evidence-first Ethereum/Hardhat repository for proof-settled AI workflow coordination using the existing canonical AGIALPHA token.

## Current Mainnet status

Ethereum Mainnet deployed: YES.
Mainnet configured: YES.

| Item | Current value |
| --- | --- |
| Ethereum Mainnet deployment | PASS — YES |
| Mainnet configuration | PASS — YES |
| GoalOS contracts | 48 |
| Canonical external AGIALPHA | 1 |
| Operator verification evidence | PASS — 48/48 |
| Postdeployment operator evidence | PASS — VERIFIED_AND_CONFIGURED |
| Phase-B grants | PASS — 14/14 |
| Permanent authority | PASS — Wallet B / Ledger |
| Wallet A managed roles | PASS — 0 |
| Predeployment authorization | NOT_APPLICABLE — DIRECT_OPERATOR_NO_CERTIFICATE |
| Independent live revalidation | PENDING_EXTERNAL_INPUT |
| Source-identity reproducibility | PENDING |
| Production activation | NOT_ACTIVATED |
| User-fund authorization | NO |

PENDING_EXTERNAL_INPUT is not a deployment failure. It means optional independent dual-provider validation was not run in an environment containing protected read-only credentials.

Current source of truth: `qa/mainnet-release-state.json`, `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/verification-evidence.json`, `config/ethereum-mainnet.contracts.json`, and `release/mainnet-2026-06-21/`. Historical Stage-A predeployment records are preserved but do not override the current direct-operator postdeployment release state.

## Canonical AGIALPHA

Canonical AGIALPHA on Ethereum Mainnet is `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. It is external to GoalOS: `external = true`, `deployedByGoalOS = false`, and `mintedByGoalOS = false`.

## Published release

Published pre-release: `v4.4.0-mainnet-2026-06-21`. This change does not modify the published tag or release assets.

## Security and claim boundary

No external-audit claim is made by this release. External-audit completion is not an active release-state gate. This repository does not claim production activation, user-fund authorization, legal approval, tax approval, guaranteed security, yield, revenue share, or price appreciation.

## Developer quick start

```bash
npm ci
npm run mainnet:release-state:all
```
