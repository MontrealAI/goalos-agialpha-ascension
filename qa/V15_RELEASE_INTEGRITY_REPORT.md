# V15 Release Integrity Report

## Summary
- Certificate hash: `0x1f133895a142dd3446b8bc7dbc249e40fb0707eb4bb7bf09a197d42412e75818`
- package.json version: `4.4.0`
- README/status version: `v4.4.0`
- Versions match: `True`
- Certificate validation in git checkout mode: `PASSED`.
- Certificate validation in source-archive/no-git mode: `PASSED` (`SOURCE_ARCHIVE_NO_GIT`).
- QA manifest freshness: `PASSED` (active latest manifest: `qa/MANIFEST.json`).
- assert_public_status.py passes: `True`
- no_private_operator_data_check.py passes without noisy fatal git output: `True`
- Paper folder exists: `True`
- Release docs exist: `True`
- Branch protection/rulesets: `PUBLIC_RISK_ACCEPTED`; pre-deployment hardening recommended.

## Final public states
- TECHNICALLY_MAINNET_READY: YES
- MAINNET_DEPLOYMENT_AUTHORIZED: YES
- ETHEREUM_MAINNET_AUTHORIZED: YES
- MAINNET_DEPLOYED: NO

## Workflow naming

- `.github/workflows/final-public-mainnet-authorization.yml`: `Final Public Mainnet Authorization` (ok).
- `.github/workflows/repository-validation.yml`: `Repository Validation` (ok).
- `.github/workflows/solidity-audit-toolchain.yml`: `Solidity Audit Toolchain` (ok).
- `.github/workflows/agialpha-audit-candidate-ci.yml`: `GoalOS AGIALPHA Audit-Candidate CI` (ok).
- `.github/workflows/mainnet-authorization-gate.yml`: `Mainnet Authorization Gate` (ok).
- `.github/workflows/mainnet-gate-watch.yml`: `Mainnet Gate Watch` (ok).
- `.github/workflows/ethereum-sepolia-rehearsal.yml`: `Ethereum Sepolia Rehearsal` (ok).
- `.github/workflows/sepolia-rehearsal.yml`: `Local/Sepolia Rehearsal` (ok).

## Active stale docs/artifacts
None remain as active contradictions to certificate-backed public YES.

## Historical stale docs/artifacts
Historical pre-certificate material is retained only when bannered, archived, or classified as script backward compatibility / old audit output. See `qa/AUTHORIZATION_CONTRADICTION_REPORT.json`.
