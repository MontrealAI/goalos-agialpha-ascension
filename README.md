# GoalOS AGIALPHA Ascension

[![Repository Validation](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml)
[![Final Public Mainnet Authorization](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml)
[![Mainnet Authorization Gate](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml)
[![Solidity Audit Toolchain](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml)
[![License: No license granted](https://img.shields.io/badge/License-No%20license%20granted-lightgrey.svg)](LICENSE_DECISION.md)
[![Solidity 0.8.35](https://img.shields.io/badge/Solidity-0.8.35-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)
[![TypeScript 5.9.3](https://img.shields.io/badge/TypeScript-5.9.3-3178c6?logo=typescript&logoColor=white)](package.json)
[![Mainnet Authorized](https://img.shields.io/badge/Ethereum%20Mainnet%20Authorized-NO-critical)](qa/mainnet-authorization-certificate.json)
[![Mainnet Deployed](https://img.shields.io/badge/Ethereum%20Mainnet%20Deployed-NO-critical)](qa/mainnet-authorization-certificate.json)

GoalOS AGIALPHA Ascension v4.4.0 mainnet authorization candidate.
Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
Ethereum Mainnet deployed: NO.

This means the repository package is not currently authorized for manual gated Ethereum Mainnet deployment. Resolve the certificate blockers, regenerate the certificate, and rerun the public checks before any mainnet deployment attempt. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.

It does not claim external audit completion, legal approval, tax review, guaranteed security, guaranteed token classification, investment return, yield, price target, revenue share, or production deployment.

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.


## Executive overview

GoalOS AGIALPHA Ascension is the institutional, evidence-first package for proof-settled AI workflow coordination using the existing AGIALPHA token. The repository is designed for reviewers, operators, auditors, and governance stakeholders who need a clear source of truth, reproducible checks, and strict public-claims boundaries.

**Official source of truth:** `qa/mainnet-authorization-certificate.json`. Public README/status documents summarize that certificate; they do not override it.

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

The source of truth is `qa/mainnet-authorization-certificate.json`. README/status documents are generated from that certificate; manual edits cannot create YES.

- TECHNICALLY_MAINNET_READY: **NO**
- MAINNET_DEPLOYMENT_AUTHORIZED: **NO**
- ETHEREUM_MAINNET_AUTHORIZED: **NO**
- MAINNET_DEPLOYED: **NO**
- Canonical AGIALPHA token: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`
- Chain: Ethereum Mainnet (`chainId=1`)
- Final manual command: `npm run deploy:ethereum-mainnet:gated`

## Safety boundary

CI cannot deploy Ethereum Mainnet. Runtime RPC URL, deployer key, and runtime addresses are local broadcast inputs only and are not stored in GitHub. MockAGIALPHA is local/Sepolia-only and is forbidden on Ethereum Mainnet. No new AGIALPHA token is deployed on Ethereum Mainnet.

## Deployment and verification command center

Use `docs/DEPLOYMENT_START_HERE.md` as the operator-facing command path. Shortest safe paths:

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

## Ownership handoff

GoalOS deployments require ERC-173 ownership handoff before being considered operationally complete. See `docs/OWNERSHIP_HANDOFF_RUNBOOK.md` and use `npm run ownership:sepolia:doctor|plan|dry-run|transfer|verify|evidence` or `npm run ownership:mainnet:doctor|plan|fork-rehearsal|transfer-local-gated|verify|evidence`. Mainnet single-deployer permanent-address mode is blocked.
