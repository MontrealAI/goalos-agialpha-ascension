# RELEASES

Audience: reviewers, developers, or operators as applicable.
Purpose: current Mainnet documentation for the configured pre-release.
Current status: Ethereum Mainnet deployed YES; configured YES; production activation NO; user-fund authorization NO.
Authoritative source: Mainnet receipts/readbacks, `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/`, and `qa/mainnet-release-state.json`.
Last reviewed: 2026-06-22.
Next review trigger: new release, authority change, verification change, incident, or Stage-C activation request.

## Current boundaries

Deployment: YES. Configuration: YES. Operator verification evidence: 48/48. Phase-B grants: 14/14. Wallet B / Ledger is permanent authority. Wallet A managed roles: 0. Production activation: NO. User-fund authorization: NO. External audit completion: NO.

## Read-only use

Use the generated registry and Etherscan links for discovery. Validate `chainId = 1`. Do not redeploy the canonical topology. Do not embed private keys, RPC secrets, mnemonics, browser profiles, or private operator logs.

## Stage C

Stage C remains separate and requires bounded canary, monitoring, reconciliation, pause/recovery drill, explicit Ledger approval, production-write enablement, and user-fund authorization.

## Governance terminology

For the 2026-06-21 canonical deployment use genesis authority assignment, permanent authority, and postdeployment role configuration. Legacy/future two-step ownership deployments are not required for the 2026-06-21 canonical deployment. `DEFAULT_ADMIN_ROLE = 0x00...00` is a role identifier, not a wallet.


## Release links

- GitHub release: https://github.com/MontrealAI/goalos-agialpha-ascension/releases/tag/v4.4.0-mainnet-2026-06-21
- Contract registry: `config/ethereum-mainnet.contracts.json` and `docs/ETHEREUM_MAINNET_CONTRACTS.md`
- Evidence archive: `release/mainnet-2026-06-21/` and `qa/mainnet-postdeploy/`
- Checksum asset: published release checksum asset when attached; repository checksum material remains under `release/mainnet-2026-06-21/`.
- Source archives: GitHub release source archives for tag `v4.4.0-mainnet-2026-06-21`.
- Security policy: `SECURITY.md` when present; otherwise repository security and limitations documentation.
- Stage-C runbook: `docs/PRODUCTION_ACTIVATION.md`

The contracts are publicly verified on Etherscan. Independent commit-to-bytecode reproducibility remains a distinct provenance result unless separately proven.
