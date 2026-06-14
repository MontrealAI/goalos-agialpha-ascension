# Deployment and Verification Gap Report

This report was written after inspecting the existing Hardhat deployment and verification surface, including `package.json`, `hardhat.config.ts`, `scripts/config/*`, `scripts/deployment/`, the Sepolia/Mainnet deployment scripts, manifest scripts, `deployments/`, `qa/`, `docs/`, workflows, `README.md`, `.gitignore`, and `AGENTS.md`.

## 1. Existing deployment scripts

- `scripts/deploy-core.ts` is the shared deployment core used by network-specific wrappers.
- `scripts/deploy-ethereum-sepolia.ts` provides the Sepolia live deployment wrapper.
- `scripts/deploy-ethereum-mainnet-gated.ts` provides the strict Ethereum Mainnet local-only gated deployment wrapper.
- `scripts/preflight-ethereum-mainnet.ts` and related Mainnet authorization/readiness scripts provide no-broadcast readiness checks.
- `scripts/deployment/goalos-deploy-command-center.ts` already exists and is the unified command center to improve rather than replace.
- `scripts/private/*` already contains private/local operator helpers.

## 2. Existing verification scripts

- `scripts/verify-agialpha-token.ts` verifies the canonical AGIALPHA token boundary.
- `scripts/verify-deployment.ts` and `scripts/deployment/verify-deployment-friendly.ts` provide deployment verification UX.
- `scripts/verification/verify-contracts-from-manifest.ts` already exists as the autonomous manifest-based verification entrypoint.
- `scripts/verify-deployment-manifest.ts` validates deployment manifests.

## 3. Existing npm aliases

The repository already has many aliases for compile/test/readiness, Sepolia deployment, Mainnet preflight/gated deployment, manifest generation/verification, command-center operations, evidence validation, verification, bytecode checks, and claim-boundary checks. This PR preserves existing names and fills gaps only by wiring missing operator-grade behaviors to the existing command center and verification entrypoints.

## 4. Existing docs

The repository already contains extensive deployment, Mainnet authorization, Sepolia rehearsal, claim-boundary, audit, and operator documentation. The operator-facing docs that matter for this PR already exist and are improved in place: `docs/DEPLOYMENT_START_HERE.md`, `docs/CONTRACT_VERIFICATION_START_HERE.md`, `docs/SEPOLIA_DEPLOYMENT_GUIDE.md`, `docs/MAINNET_OPERATOR_RUNBOOK.md`, troubleshooting docs, FAQ, and claim-boundary docs.

## 5. Existing workflows

- Sepolia deployment automation already exists at `.github/workflows/deploy-ethereum-sepolia.yml`.
- Mainnet preflight/operator-packet automation already exists at `.github/workflows/mainnet-preflight-and-operator-packet.yml`.
- Autonomous verification workflows already exist for Sepolia and Mainnet.
- Existing Mainnet workflows are no-broadcast authorization/preflight style workflows; final Mainnet broadcast remains local-only.

## 6. Existing safety gates

- Hardhat network aliases include Sepolia/Mainnet chain IDs.
- Mainnet gated deployment blocks CI/GitHub Actions.
- Mainnet gated deployment requires chainId 1, canonical AGIALPHA, no mock token, no new AGIALPHA token, authorization evidence, typed confirmation, and exact allow value.
- Public status and repository-safety scripts guard claim boundaries and private operator data.
- Verification logic treats already-verified contracts as success and records failures instead of fabricating success.

## 7. Missing pieces

- The root `AGENTS.md` needed to be made concise and aligned with deployment/verification review priorities.
- This gap report was missing/empty.
- The verification engine needed explicit helper-module seams for Hardhat, Etherscan, Sourcify, status classification, constructor args, bytecode checks, and reporting.
- Operator command-center output needed stronger evidence-first status language and local-only Mainnet packet generation.

## 8. Duplicated pieces

- Several Mainnet wizard/private scripts overlap with the TypeScript command center. This PR does not create a second command center; the existing `goalos-deploy-command-center.ts` remains the consolidated operator entrypoint.
- Legacy Sepolia rehearsal docs and newer deployment guides overlap. This PR keeps the Start Here guides as the operator front door and leaves historical evidence docs intact.

## 9. Changes this PR will make

- Preserve and harden the existing command center rather than replacing it.
- Add/keep safe environment examples and `.gitignore` rules for local-only files.
- Preserve Mainnet local-only broadcast controls and Sepolia protected workflow dispatch.
- Add verification helper modules behind the existing manifest verifier.
- Ensure docs, evidence, verification reports, and tests remain claim-bounded and secret-redacted.

## 10. Changes this PR intentionally will not make

- It will not deploy Sepolia or Ethereum Mainnet.
- It will not mark Ethereum Mainnet deployed as YES.
- It will not mark contracts verified without explorer/source verification evidence or confirmed already-verified status.
- It will not add a GitHub Actions path that can broadcast Ethereum Mainnet transactions.
- It will not deploy or mint a new AGIALPHA token on Ethereum Mainnet.
- It will not migrate to Hardhat 3 or rewrite contracts.
