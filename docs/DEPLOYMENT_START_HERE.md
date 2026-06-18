# Deployment Start Here

## 1. What you are about to do
Use the Deployment Command Center to check readiness, deploy to Sepolia, verify contracts, create evidence, and prepare a strictly local Ethereum Mainnet deployment package.

## 2. What you need
Node/npm, a funded deployer wallet, a private RPC URL, and optionally `ETHERSCAN_API_KEY` for verification.

## 3. What not to do
Do not commit secrets. Do not put Mainnet keys in GitHub Actions. Do not claim Mainnet deployed until real chainId=1 transaction hashes and addresses pass post-deployment verification.

## 4. Copy-paste commands

Sepolia:
```bash
cp .env.sepolia.example .env.sepolia.local
npm run deploy:sepolia:doctor
npm run deploy:sepolia:dry-run
npm run deploy:sepolia:live
npm run deploy:sepolia:verify
npm run deploy:sepolia:evidence
```

Ethereum Mainnet:
```bash
npm run deploy:mainnet:doctor
npm run deploy:mainnet:preflight
npm run deploy:mainnet:fork-rehearsal
npm run deploy:mainnet:prepare-local
source .private/mainnet-operator.env
npm run deploy:mainnet:live-local-gated
npm run deploy:mainnet:verify
npm run deploy:mainnet:evidence
```

> **Warning:** Sepolia may be deployed through protected GitHub Actions. Ethereum Mainnet final broadcast is local-only and must not be deployed by CI. Mainnet contract verification may run from GitHub Actions only after deployment, using a manifest and no deployer key.

## 5. How to know it worked
The command center prints PASS/WARN/FAIL, the detected chain ID, deployer address, balance, manifest path, evidence path, and allowed next step.

## 6. What to do if it fails
Read the printed “Next action” line. It names the missing env var, wrong network, missing evidence, or blocked Mainnet gate.

## 7. What the generated files mean
`deployments/*.latest.json` is the manifest. `qa/*deployment-evidence.json` is the evidence docket. `docs/*DEPLOYMENT_REPORT.md` is the public-safe human report.

## 8. What you can safely share
Public addresses, transaction hashes, manifest hashes, verification reports, and public evidence dockets.

## 9. What must remain private
Private keys, RPC URLs, mnemonics, seeds, signatures, and `.private/*` filled operator files.

## 10. Final claim boundary
This evidence reports deployment mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.


## Partial deployment recovery
If a deployment fails after some contracts broadcast, stop and preserve terminal output. Do not claim success. Inspect any partial manifest, then choose one recovery path: resume from the partial manifest if supported, abandon and redeploy with a clean manifest, or inspect manually with an engineer. A deployment is complete only after all required contracts, transaction hashes, and post-checks pass.


## Ownership handoff

GoalOS deployments require ERC-173 ownership handoff before being considered operationally complete. See `docs/OWNERSHIP_HANDOFF_RUNBOOK.md` and use `npm run ownership:sepolia:doctor|plan|dry-run|transfer|verify|evidence` or `npm run ownership:mainnet:doctor|plan|fork-rehearsal|transfer-local-gated|verify|evidence`. Mainnet single-deployer permanent-address mode is blocked.
