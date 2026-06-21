Install:
`npm ci`

Start:
`npm run mainnet:initial:setup-and-authorize`

# GoalOS AGIALPHA Ascension

[![Repository Validation](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml)
[![Final Public Mainnet Authorization](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml)
[![Mainnet Authorization Gate](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml)
[![Solidity Audit Toolchain](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)
[![TypeScript 5.9.3](https://img.shields.io/badge/TypeScript-5.9.3-3178c6?logo=typescript&logoColor=white)](package.json)
[![Mainnet Authorized](https://img.shields.io/badge/Ethereum%20Mainnet%20Authorized-NO-critical)](qa/mainnet-authorization-certificate.json)
[![Mainnet Deployed](https://img.shields.io/badge/Ethereum%20Mainnet%20Deployed-YES-success)](qa/mainnet-release-state.json)

GoalOS AGIALPHA Ascension v4.4.0 Mainnet release-state summary.
Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Historical predeployment authorization used: NO — DIRECT_OPERATOR_NO_CERTIFICATE.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
Ethereum Mainnet deployed: YES.
GoalOS contracts deployed: 48.
GoalOS contracts Etherscan-verified: 48/48 after independent read-only validation.
Canonical external AGIALPHA: confirmed.
Mainnet configured: YES.
Permanent authority: Wallet B / Ledger genesis authority assignment.
Wallet A managed roles: 0.
Phase-B grants: 14/14.
Production activated: NO.

Three-stage Mainnet release status:

| Stage | Status |
| --- | --- |
| Predeployment authorization | NO |
| Ethereum Mainnet deployed | YES |
| Postdeployment verification | VERIFIED_AND_CONFIGURED |
| Production activation effective | NO |

A pre-broadcast state with predeployment authorization YES and Ethereum Mainnet deployed NO is a GO to deploy, not a contradiction. Stage B evaluates chain-1 receipts, bytecode, verification, and ownership/role readback only after human broadcast. Stage C separately governs bounded live canary, monitoring, reconciliation, Ledger activation, and production reliance.

The historical Stage-A predeployment certificate was not used for this deployment path. The repository now records a direct operator Mainnet deployment and postdeployment evidence separately from Stage-C production activation.

Runtime RPC URL and deployer key outside GitHub remain mandatory for any local-only operator action; CI must not receive signing keys.

It does not claim external audit completion, legal approval, tax review, guaranteed security, guaranteed token classification, investment return, yield, price target, revenue share, or production deployment.

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.


## Executive overview

GoalOS AGIALPHA Ascension is the institutional, evidence-first package for proof-settled AI workflow coordination using the existing AGIALPHA token. The repository is designed for reviewers, operators, auditors, and governance stakeholders who need a clear source of truth, reproducible checks, and strict public-claims boundaries.

**Official source of truth:** Stage-A authorization remains `qa/mainnet-authorization-certificate.json`; Stage-B deployment state is `qa/mainnet-release-state.json`. Public README/status documents summarize those records; they do not override them.

## Quick start for institutional reviewers

1. Read this README for current status, safety boundaries, and canonical commands.
2. Use `docs/DOCUMENTATION_INDEX.md` to choose the right reviewer, operator, auditor, or contributor path.
3. Use `docs/DOCUMENTATION_MAINTENANCE.md` before editing public docs, runbooks, or claim-boundary materials.
4. Confirm the certificate in `qa/mainnet-authorization-certificate.json`.
5. Run `npm run mainnet:public-authorize` to validate the public authorization gates.
6. Run `npm run mainnet:local-checks` before any operator handoff or release review.
7. Use `npm run deploy:ethereum-mainnet:gated` only from a local operator environment with runtime RPC URL and deployer key supplied outside GitHub.

## Documentation maintenance

Documentation is evidence-first. Before editing README files, runbooks, public website copy, generated status docs, or claim-boundary materials, use `docs/DOCUMENTATION_MAINTENANCE.md` for the source-of-truth order, update checklist, required validation commands, and PR documentation expectations. Public docs must summarize certificate-backed evidence and must not create deployment, verification, audit, legal, tax, token-classification, investment, yield, or production claims without evidence.

## Official badge policy

Badges at the top of this README are intentionally limited to official, auditable repository signals: GitHub Actions workflow status, package-declared tool versions, license, authorization state, and deployment state. Workflow badges update automatically from GitHub Actions. Static status badges mirror `qa/mainnet-authorization-certificate.json` and must be updated only when the certificate changes. See `docs/OFFICIAL_BADGES.md` for maintenance rules.

## Core doctrine

- GoalOS decides what may evolve.
- AGIALPHA coordinates proof-settled work.
- Evidence Dockets make claims auditable.
- Do not put intelligence on-chain; put proof of intelligence on-chain.
- No proof, no evolution. No eval, no propagation. No rollback, no release.

## Ethereum Mainnet authorization

The Stage-A source of truth is `qa/mainnet-authorization-certificate.json`; the Stage-B deployment source of truth is `qa/mainnet-release-state.json`. README/status documents are generated summaries; manual edits cannot create YES.

- TECHNICALLY_MAINNET_READY: **NO**
- MAINNET_DEPLOYMENT_AUTHORIZED: **NO**
- ETHEREUM_MAINNET_AUTHORIZED: **NO**
- MAINNET_DEPLOYED: **YES**
- Canonical AGIALPHA token: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`
- Chain: Ethereum Mainnet (`chainId=1`)
- Final manual command: `npm run deploy:ethereum-mainnet:gated`

## Safety boundary

CI cannot deploy Ethereum Mainnet. Runtime RPC URL, deployer key, and runtime addresses are local broadcast inputs only and are not stored in GitHub. MockAGIALPHA is local/Sepolia-only and is forbidden on Ethereum Mainnet. No new AGIALPHA token is deployed on Ethereum Mainnet.

## Deployment and verification command center

Use `docs/DEPLOYMENT_START_HERE.md` as the operator-facing command path. Shortest safe paths:

This evidence reports deployment mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.

**Sepolia**
```bash
npm run deploy:sepolia:doctor
npm run deploy:sepolia:dry-run
npm run deploy:sepolia:live
npm run deploy:sepolia:verify
npm run deploy:sepolia:evidence
```

**Ethereum Mainnet**
```bash
npm run deploy:mainnet:doctor
npm run deploy:mainnet:preflight
npm run deploy:mainnet:fork-rehearsal
npm run deploy:mainnet:prepare-local
npm run deploy:mainnet:live-local-gated
npm run deploy:mainnet:verify
npm run deploy:mainnet:evidence
```

> Sepolia may be deployed through protected GitHub Actions. Ethereum Mainnet final broadcast is local-only and must not be deployed by CI. Mainnet contract verification may run from GitHub Actions only after deployment, using a manifest and no deployer key.

## Sovereign RSI v6.3 research paper

The Sovereign RSI v6.3 publication folder is `docs/papers/sovereign-rsi/v6.3/`. Paper assets may be pending upload if they are not present in the tree; do not fabricate missing PDF/DOCX/source files.

Core thesis: GoalOS sets sovereign aims. AGIALPHA coordinates proof-settled work. AEP-001 defines valid evidence. The Proof Gradient decides what may evolve. The intelligence stays private. The proof becomes verifiable.

RSI means proof-backed upgrade rights. An artifact may influence future work only after evidence, evaluation, reviewer validation, scope control, challenge window, canary rollout, monitoring, rollback readiness, and chronicle memory.

Claim boundary: this paper does not claim achieved AGI, ASI, superintelligence, autonomous sovereignty, guaranteed ROI, safety certification, legal approval, tax approval, security approval, energy abundance, or Kardashev Type II achievement.

## Genesis authority assignment and ownership handoff

The 2026-06-21 direct Mainnet deployment records Wallet B / Ledger as the permanent authority through genesis authority assignment where applicable. Future GoalOS deployments require ERC-173 ownership handoff before being considered operationally complete. See `docs/OWNERSHIP_HANDOFF_RUNBOOK.md` and use `npm run ownership:sepolia:doctor|plan|dry-run|transfer|verify|evidence` or `npm run ownership:mainnet:doctor|plan|fork-rehearsal|transfer-local-gated|accept-local-gated|verify|evidence`. Mainnet single-deployer permanent-address mode is blocked. For delayed acceptance, run `ownership:mainnet:accept-local-gated` only after the contract readback says: Wait until pendingOwnerAcceptAfter.
