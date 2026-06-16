# GoalOS Deployment and Contract Verification Guide

## What this does
It helps an authorized operator verify deployed contracts and preserve claim-bounded verification evidence.

## What this does not do
It does not deploy Ethereum Mainnet, does not prove AGI/ASI/superintelligence, does not provide legal/tax/security approval, and does not claim production safety.

## What you need
- A deployment manifest in `deployments/`.
- `ETHERSCAN_API_KEY` for Etherscan verification.
- Optional read-only RPC for bytecode checks.
- For Ethereum Mainnet, local operator verification inputs or an unredacted private constructor-args source when constructor args are redacted from the public manifest.

## What must stay private
Private keys, mnemonics, RPC URLs, API keys, bearer tokens, signatures, `.env.*.local`, and `.private/` files.

## What is safe to share
Redacted manifests, generated evidence JSON, verification reports, transaction hashes, public addresses, and claim-bounded summaries.

## Copy-paste commands

Sepolia default operator path:
```bash
npm run verify:doctor -- --network ethereumSepolia
npm run deploy:sepolia:verify
npm run verify:contracts:status -- --network ethereumSepolia
```

Ethereum Mainnet guarded operator path:
```bash
npm run verify:doctor -- --network ethereumMainnet
npm run deploy:mainnet:verify
npm run verify:contracts:status -- --network ethereumMainnet
```

Manifest-only verifier path for unredacted manifests:
```bash
npm run verify:sepolia:all
```

Do not use `npm run verify:mainnet:all` as the default post-deployment Mainnet route when the public Mainnet manifest has redacted constructor args. Use `npm run deploy:mainnet:verify`, which routes through the Mainnet-aware wrapper and blocks unsafe verification attempts instead of fabricating evidence.

## How to know it worked
The command writes `qa/*contract-verification-evidence.json`, `qa/*verification-report.json`, or `docs/*CONTRACT_VERIFICATION_REPORT.md` with complete status or clear failure instructions.

## Generated files
Manual fallback commands are written to `qa/manual-verification-commands.sepolia.md` or `qa/manual-verification-commands.mainnet.md`; constructor args files are written under `verification-args/` or wrapper-specific temporary argument files.

## If it fails
Fix the blocked item, rerun the same wrapper command, or use generated manual fallback instructions. For Mainnet, do not replace a redacted-args failure with a verified claim unless source/bytecode verification evidence or confirmed already-verified status exists.

## Autonomous verification
The verifier reads the manifest, checks chainId and constructor args, runs Hardhat verification, treats already-verified as success, records failures, and never fabricates success.

## Claim boundary
This evidence reports deployment and verification mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.
