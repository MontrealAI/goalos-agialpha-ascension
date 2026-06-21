# Sepolia Deployment Evidence Docket

This docket defines how the June 20, 2026 Ethereum Sepolia deployment is imported, validated, reconciled, and preserved as public release evidence without converting it into an Ethereum Mainnet claim.

## Import command

```bash
npm run evidence:sepolia:import -- \
  --manifest /path/ethereum-sepolia.agialpha.latest.json \
  --deployment-evidence /path/sepolia-deployment-evidence.json \
  --verification-report /path/sepolia-verification-report.json \
  --independent-check /path/sepolia-etherscan-v2-independent-check.json
```

Codex Cloud did not receive the four operator-supplied JSON files. The repository therefore includes deterministic fixture support for tests and development, but fixture output is marked `DETERMINISTIC_FIXTURE_NOT_OPERATOR_ARTIFACT` and is not final operator evidence.

## What the deployment proves when imported and independently read back

The known Sepolia evidence supports these bounded facts after the importer verifies the exact four SHA-256 input hashes and the online verifier confirms Sepolia receipts/code:

- Network identity is Ethereum Sepolia (`chainId == 11155111`).
- The deployment is dated `2026-06-20T16:11:25.386Z`.
- The package version was `4.4.0`, Hardhat was `2.28.6`, and the manifest reports Solidity `0.8.35`.
- The topology contains 49 contract addresses: Sepolia `MockAGIALPHA` plus 48 GoalOS contracts.
- The manifest records 63 transactions.
- Etherscan V2 verification reports 49/49 verified contracts.
- The independent Etherscan V2 check reports 49 verified and 0 failed.
- The four named reserve-vault aliases resolve to the `TokenReserveVault` artifact.

## What it does not prove

This historical deployment is classified as `HISTORICAL_VERIFIED_SEPOLIA_DEPLOYMENT`, not as current production authorization. It does not prove:

- Ethereum Mainnet deployment.
- Canonical Mainnet AGIALPHA usage.
- Current-release bytecode parity.
- Mainnet-fork behavior.
- Ledger/Safe handoff or disposable deployer separation.
- Typed Owner override scenario execution.
- Accounting reconciliation, canary limits, lifecycle rehearsal, migration, rollback, or shutdown correctness.
- Full security assurance or invariant-campaign completion.

## Reconciliation

The historical deployment-evidence file is stale because it says `verificationStatus: NOT_RUN`. The repository-owned reconciler does not hand-edit that input. Instead, it emits `qa/sepolia-release-evidence/deployment-evidence.reconciled.json` with field provenance and a reconciled status derived from validated input files and, when credentials are available, Sepolia readback.

## Future manifest requirements

Future release-candidate manifests must include: `gitCommit`, `sourceTreeHash`, `lockfileHash`, `compilerBinaryHash`, `compilerSettingsHash`, creation/runtime bytecode hashes, FQNs, constructor encodings, deployment script hash, and `releaseId`.
