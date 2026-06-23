# Ethereum Mainnet Documentation Hub

Status: DEPLOYED_AND_CONFIGURED_PRE_RELEASE
Release: v4.4.0-mainnet-2026-06-21
Last evidence date: 2026-06-21
Production activation: NO

## Executive status

| Item | Value |
| --- | --- |
| Network | Ethereum Mainnet |
| Chain ID | 1 |
| Deployment | YES |
| Configuration | YES |
| GoalOS-created contracts | 48 |
| Manifest entries | 49 including external AGIALPHA |
| Deployment transactions | 48 |
| Operator verification evidence | 48/48 GoalOS contracts; current evidence status `verified_from_seed_requires_api_refresh` |
| Runtime bytecode/live RPC validation | REQUIRES_LIVE_RPC_VALIDATION |
| Verification failures | 0 |
| Phase-B grants | 14/14 active |
| Postdeployment operator evidence | PASS — VERIFIED_AND_CONFIGURED |
| Independent live revalidation | PENDING_EXTERNAL_INPUT |
| Production activation | NO |
| User-fund authorization | NO |


## Published release

GitHub pre-release: [`v4.4.0-mainnet-2026-06-21`](https://github.com/MontrealAI/goalos-agialpha-ascension/releases/tag/v4.4.0-mainnet-2026-06-21). Full tag SHA resolved from Git: `51bacf4fe58e4eb425240e74eef7e8461832767f`.

## Chain and token boundary

Canonical AGIALPHA is `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. It is external, not deployed by GoalOS, and not minted by GoalOS.

## Contract registry

Use the generated registry: [Ethereum Mainnet Contracts](ETHEREUM_MAINNET_CONTRACTS.md), `config/ethereum-mainnet.contracts.json`, `app/config/ethereum-mainnet.contracts.generated.ts`, and `website/data/ethereum-mainnet.contracts.json`.

## Timeline

- 2026-06-21: Direct operator deployment and configuration evidence recorded.
- 2026-06-22: Published GitHub pre-release documented.

## Governance and authority

The deployment used genesis authority assignment and postdeployment role configuration. Wallet B / Ledger is permanent authority. Wallet A has zero managed roles. No ownership acceptance transaction is required for this deployment.

## Verification methodology

Verification status is backed by deployment receipts, operator Etherscan verification evidence, runtime bytecode/readback evidence under `qa/mainnet-postdeploy/`, and release state summaries. Current registry generation preserves evidence qualifiers such as `verified_from_seed_requires_api_refresh` and `requires mainnet:postdeploy:revalidate`; independent dual-RPC revalidation and any Stage-B certificate retain the exact status in their evidence files.

## Release evidence and checksums

Release evidence is under `release/mainnet-2026-06-21/` and `qa/mainnet-postdeploy/`. Checksums and archives linked by the published release remain the release source; this PR does not move or overwrite them.

## Provenance boundary

Operator verification evidence records 48/48 GoalOS contracts with the current evidence qualifiers preserved. Independent live Etherscan/API revalidation, commit-to-bytecode reproducibility, and live-RPC bytecode validation remain distinct provenance results unless separately proven.

## Read-only developer use

Developers should import the generated registry, validate `chainId === 1`, load ABIs from repository artifacts, and use read-only provider calls. Writes remain disabled until Stage C.

## Monitoring and incident response

See [Monitoring and Alerting](MONITORING_AND_ALERTING.md) and [Incident Response](INCIDENT_RESPONSE_MAINNET.md).

## Stage-C boundary

Stage C is not complete. It requires bounded canary, monitoring, reconciliation, pause/recovery drill, explicit Ledger approval, production-write enablement, and user-fund authorization.
