# GoalOS AGIALPHA Ascension

GoalOS AGIALPHA Ascension v4.4 mainnet authorization candidate.

Automated/internal security toolchain: passed, based on public evidence and generated clearance reports.
Local deterministic rehearsal: passed.
Public AGIALPHA token verification: passed or accepted by public governance when live no-key network fetch is unavailable.
Public Sepolia: recommended but not required for public repository authorization.
Not externally audited.
Ethereum Mainnet technical readiness: YES.
Ethereum Mainnet deployment authorization: YES.
Ethereum Mainnet authorization: YES.
Ethereum Mainnet deployed: NO.

This means the repository package is authorized for manual gated Ethereum Mainnet deployment. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.

Mainnet AGIALPHA token address: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. This repository must not deploy or mint a new AGIALPHA token on Ethereum Mainnet.

```text
GoalOS decides what may evolve.
AGIALPHA coordinates proof-settled work.
Evidence Dockets make claims auditable.
```

## Current public authorization status

```text
TECHNICALLY_MAINNET_READY: YES
MAINNET_DEPLOYMENT_AUTHORIZED: YES
ETHEREUM_MAINNET_AUTHORIZED: YES
MAINNET_DEPLOYED: NO
```

The YES state is computed from public repository artifacts by:

```bash
npm run mainnet:readiness-check
npm run mainnet:deployment-authorization-check
npm run mainnet:authorization-check
```

## No-public-secrets authorization model

Public GitHub does **not** require or store RPC URLs, private keys, founder signatures, founder/treasury/admin addresses, wallet metadata, or private operator notes. Public authorization comes from public CI, public evidence, public governance, branch-protection evidence or public risk acceptance, and machine-readable decision files.

Runtime secrets and runtime addresses are required only for actual blockchain broadcast from a local private deployer environment.

## Existing AGIALPHA token

This repository uses the existing Ethereum Mainnet `$AGIALPHA` ERC-20 token:

```text
0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA
```

The implementation does **not** deploy or mint a new AGIALPHA token on Ethereum Mainnet. `MockAGIALPHA` is local/Sepolia rehearsal only and is forbidden on Ethereum Mainnet.

## Source doctrine

1. **GoalOS / AEP-001**: `Aim → Act → Prove → Evolve`; do not put intelligence on-chain, put proof of intelligence on-chain.
2. **AGI ALPHA / α‑AGI Ascension**: `Request → Escrow → Execute → Proof → Validate → Settle → Chronicle`; settlement requires ProofBundles or proof-equivalent evidence, validator review, and claim boundaries.

## What this repository contains

```text
contracts/        Ethereum Solidity contracts and registries
scripts/          deployment, verification, readiness, audit, and evidence scripts
schemas/          Evidence Docket, ProofBundle, and public mainnet gate schemas
test/             Hardhat tests and invariants
docs/             operator, architecture, claim-boundary, and gate docs
audit/            automated/internal security toolchain workspace
qa/               generated manifests and public evidence reports
.github/          workflows and repository governance
```

## Quick start for public checks

```bash
npm ci
npm run repo:all
npm run assert:public-status
npm run compile
npm test
npm run test:all
npm run static-check
npm run rehearse:local
npm run evidence:local
npm run verify:agialpha-token:public
npm run audit:all
npm run audit:summarize
npm run audit:fail-on-critical
npm run audit:clearance-report
npm run mainnet:public-authorize
```

## Final manual deployment command

Only after public decisions are YES and runtime inputs are prepared locally:

```bash
npm run deploy:ethereum-mainnet:gated
```

The script refuses CI/GitHub Actions and requires the typed phrase:

```text
DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET
```

## Safe public language

Allowed: authorized for manual gated Ethereum Mainnet deployment; not externally audited; not deployed; runtime RPC/key required outside GitHub.

Do not claim guaranteed security, guaranteed non-security, investment, yield, price target, revenue share, legal/tax approval, external audit status, or production deployment without real transaction evidence.

## Security

Never commit private keys, `.env`, wallet seed phrases, RPC secrets, API keys, private buyer products, private Evidence Dockets, customer data, legal memos, tax memos, or private operator notes.

See `SECURITY.md`.
