# GoalOS Deployment and Contract Verification Guide

## What this does
It helps an authorized operator verify deployed contracts from a deployment manifest without a deployer private key.

## What this does not do
It does not deploy Ethereum Mainnet, does not prove AGI/ASI/superintelligence, does not provide legal/tax/security approval, and does not claim production safety.

## What you need
- A deployment manifest in `deployments/`.
- `ETHERSCAN_API_KEY` for Etherscan verification.
- Optional read-only RPC for bytecode checks.

## What must stay private
Private keys, mnemonics, RPC URLs, API keys, bearer tokens, signatures, `.env.*.local`, and `.private/` files.

## What is safe to share
Redacted manifests, generated evidence JSON, verification reports, transaction hashes, public addresses, and claim-bounded summaries.

## Copy-paste commands
```bash
npm run verify:doctor
npm run verify:sepolia:all
npm run verify:mainnet:all
npm run verify:contracts:status
```

## How to know it worked
The command writes `qa/*contract-verification-evidence.json` and `docs/*CONTRACT_VERIFICATION_REPORT.md` with complete status or clear failure instructions.

## Generated files
Manual fallback commands are written to `qa/manual-verification-commands.sepolia.md` or `qa/manual-verification-commands.mainnet.md`; constructor args files are written under `verification-args/`.

## If it fails
Fix the blocked item, rerun `npm run verify:contracts:retry-failed`, or use the generated manual command.

## Autonomous verification
The verifier reads the manifest, checks chainId and constructor args, runs Hardhat verification, treats already-verified as success, records failures, and never fabricates success.

## Claim boundary
This evidence reports deployment and verification mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.
