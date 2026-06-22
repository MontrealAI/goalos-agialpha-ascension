# GoalOS AGIALPHA Ascension

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)
[![Ethereum Mainnet Deployed YES](https://img.shields.io/badge/Ethereum%20Mainnet%20Deployed-YES-success)](qa/mainnet-release-state.json)
[![Contracts Verified 48/48](https://img.shields.io/badge/Contracts%20Verified-48%2F48-success)](qa/mainnet-postdeploy/verification-evidence.json)
[![Mainnet Configured YES](https://img.shields.io/badge/Mainnet%20Configured-YES-success)](qa/mainnet-release-state.json)
[![Production Activation NO](https://img.shields.io/badge/Production%20Activation-NO-critical)](qa/mainnet-release-state.json)

## Mission statement

GoalOS AGIALPHA Ascension is an evidence-first Ethereum/Hardhat repository for proof-settled AI workflow coordination using the existing canonical AGIALPHA token. The repository is organized for reviewers, operators, developers, and auditors who need clear public status, reproducible checks, and bounded claims.

## Current Mainnet status

| Item | Current value |
| --- | --- |
| Ethereum Mainnet deployment | YES |
| Mainnet configuration | YES |
| GoalOS contracts | 48 |
| Etherscan verification | 48/48 |
| Phase-B grants | 14/14 |
| Final postdeployment check | PASSED |
| Permanent authority | Wallet B / Ledger |
| Wallet A managed roles | 0 |
| Production activation | NO |
| User-fund authorization | NO |
| External audit completion | NO |

Not externally audited.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
Ethereum Mainnet deployed: YES.
Production activated: NO.

Lifecycle boundaries remain separate: deployment and configuration are complete for the pre-release, while independent dual-RPC revalidation, any Stage-B certificate, production activation, user-fund authorization, live canary completion, and external audit completion must retain the status recorded in their evidence files.

## Published release

Published pre-release: [`v4.4.0-mainnet-2026-06-21`](https://github.com/MontrealAI/goalos-agialpha-ascension/releases/tag/v4.4.0-mainnet-2026-06-21). Full tag SHA resolved from Git: `51bacf4fe58e4eb425240e74eef7e8461832767f`.

Release type: Pre-release. Release date: 2026-06-22. Deployment date: 2026-06-21. Package version: 4.4.0.

## Canonical AGIALPHA

Canonical AGIALPHA on Ethereum Mainnet is `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. It is external to GoalOS: `external = true`, `deployedByGoalOS = false`, and `mintedByGoalOS = false`.

## Governance and authority

The canonical 2026-06-21 deployment used `DIRECT_OPERATOR_NO_CERTIFICATE`, genesis authority assignment, and postdeployment role configuration. Wallet A deployer is documented in `qa/mainnet-release-state.json`; Wallet B permanent Ledger authority is documented in `qa/mainnet-release-state.json`. Wallet A has zero managed roles. No ERC-173 acceptance transaction is required for this deployed instance.

Historical predeployment certificate: not used. Deployment path: `DIRECT_OPERATOR_NO_CERTIFICATE`.

## Audience navigation

- Executive/reviewer: [`docs/CURRENT_STATUS.md`](docs/CURRENT_STATUS.md), [`docs/ETHEREUM_MAINNET.md`](docs/ETHEREUM_MAINNET.md), [`docs/SECURITY_AND_LIMITATIONS.md`](docs/SECURITY_AND_LIMITATIONS.md), [`docs/MAINNET_LIVE_GATE_IMPACT.md`](docs/MAINNET_LIVE_GATE_IMPACT.md).
- Developer: [`docs/DEVELOPER_QUICKSTART_MAINNET.md`](docs/DEVELOPER_QUICKSTART_MAINNET.md), [`docs/CONTRACT_INTERACTION_REFERENCE.md`](docs/CONTRACT_INTERACTION_REFERENCE.md), [`docs/ETHEREUM_MAINNET_CONTRACTS.md`](docs/ETHEREUM_MAINNET_CONTRACTS.md).
- Operator: [`docs/OPERATIONS_RUNBOOK_MAINNET.md`](docs/OPERATIONS_RUNBOOK_MAINNET.md), [`docs/MONITORING_AND_ALERTING.md`](docs/MONITORING_AND_ALERTING.md), [`docs/INCIDENT_RESPONSE_MAINNET.md`](docs/INCIDENT_RESPONSE_MAINNET.md), [`docs/WALLET_A_DECOMMISSION_REPORT.md`](docs/WALLET_A_DECOMMISSION_REPORT.md), [`docs/PRODUCTION_ACTIVATION.md`](docs/PRODUCTION_ACTIVATION.md).
- Contributor: [`START_HERE.md`](START_HERE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/DOCUMENTATION_MAINTENANCE.md`](docs/DOCUMENTATION_MAINTENANCE.md).

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.

## Developer quick start

```bash
npm ci
npm run mainnet:contracts:check
npm run docs:mainnet:check
```

Use the generated registry in [`config/ethereum-mainnet.contracts.json`](config/ethereum-mainnet.contracts.json) or [`app/config/ethereum-mainnet.contracts.generated.ts`](app/config/ethereum-mainnet.contracts.generated.ts). Validate `chainId === 1`, load ABIs from repository artifacts, and use read-only calls until Stage C explicitly enables production writes.

## Read-only operator commands

```bash
npm run mainnet:contracts:check
npm run mainnet:postdeploy:status
npm run docs:all
```

These commands are for status, registry, documentation, and read-only evidence review. Do not redeploy the canonical topology. Canonical redeployment commands must fail closed and must never run from CI with signing material.

## Security/claim boundary

This repository does not claim production activation, user-fund authorization, live canary completion, external audit completion, legal or tax approval, token classification, guaranteed security, investment return, AGI/ASI, yield, revenue share, or price appreciation. Do not commit secrets, `.private/` data, raw operator logs, private constructor inputs, private keys, mnemonics, RPC URLs, API keys, Ledger secrets, browser profiles, caches, or coverage artifacts.

## Architecture overview

The configured Mainnet topology contains 49 registry entries: 48 GoalOS-created contracts and one external canonical AGIALPHA token. Public contract discovery is centralized in the generated registry and the canonical Mainnet hub rather than duplicated across unrelated documents.

## Documentation index

Start with [`docs/DOCUMENTATION_INDEX.md`](docs/DOCUMENTATION_INDEX.md). The source-of-truth hierarchy is: Mainnet receipts/readbacks; `deployments/ethereum-mainnet.agialpha.latest.json`; `qa/mainnet-postdeploy/verification-evidence.json`; `qa/mainnet-postdeploy/`; `qa/mainnet-release-state.json`; `release/mainnet-2026-06-21/`; generated public docs.

## Citation and license

Use [`CITATION.cff`](CITATION.cff) for citation metadata. This repository is licensed under the MIT License; see [`LICENSE`](LICENSE).
