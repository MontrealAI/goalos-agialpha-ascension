# GoalOS AGIALPHA Ascension

GoalOS AGIALPHA Ascension v4.4 candidate.
Automated security/toolchain review: completed with blockers.
Ethereum Sepolia rehearsal: completed locally on chainId 11155111; public Sepolia replay pending unless real RPC/deployer evidence is supplied.
Dependency PRs: triaged, not blindly merged.
Not externally audited.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
Ethereum Mainnet not authorized.

Mainnet AGIALPHA token address: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. This repository must not deploy or mint a new AGIALPHA token on Ethereum Mainnet.

**GoalOS AGIALPHA Ascension** is a GoalOS-native reimplementation of **α‑AGI Ascension** using the existing Ethereum Mainnet `$AGIALPHA` token as the utility coordination asset for proof-settled AI workflow work.

```text
GoalOS decides what may evolve.
AGIALPHA coordinates proof-settled work.
Evidence Dockets make claims auditable.
```

## Current status

```text
Repository status: v4.4 candidate with automated/internal security gates.
Implementation package: gate-clean evidence-ready audit candidate.
Automated security/toolchain review: completed with blockers.
Ethereum Sepolia rehearsal: completed locally; public Sepolia replay pending unless real network evidence is supplied.
Not externally audited.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
```

Do **not** call this repository externally audited, mainnet authorized, legally approved, tax reviewed, production deployed, or guaranteed non-security.

## Existing AGIALPHA token

This repository uses the existing Ethereum Mainnet `$AGIALPHA` ERC-20 token:

```text
0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA
```

The implementation does **not** deploy or mint a new AGIALPHA token on Ethereum Mainnet.

## Source doctrine

1. **GoalOS / AEP-001**: `Aim → Act → Prove → Evolve`; do not put intelligence on-chain, put proof of intelligence on-chain.
2. **AGI ALPHA / α‑AGI Ascension**: `Request → Escrow → Execute → Proof → Validate → Settle → Chronicle`; settlement requires replayable ProofBundles, validator review, and claim boundaries.

## What this repository contains

```text
contracts/        Ethereum Solidity contracts and registries
scripts/          deployment, verification, readiness, audit, and evidence scripts
schemas/          Evidence Docket, ProofBundle, and mainnet gate schemas
test/             Hardhat tests
docs/             operator, architecture, claim-boundary, and gate docs
audit/            automated/internal security toolchain workspace
qa/               generated manifests and readiness reports
.github/          issue templates, workflows, and repository governance
```

## High-level loop

```text
Opportunity Discovery
→ Proof Seed
→ Sponsor Proof Mission
→ AGIALPHA Proof Job
→ Builder / Agent Claim
→ GoalOS Workflow Execution
→ ProofBundle / Evidence Docket
→ Reviewer Validation
→ Proof Card
→ Credential
→ Reputation
→ Selection Gate
→ Rollout / Rollback
→ Chronicle / Evolution Ledger
```

## Safe public language

Use:

```text
GoalOS improves workflows.
AGIALPHA coordinates proof work.
Evidence Dockets make claims auditable.
Proof Cards create trust.
Credentials create reputation.
Reputation unlocks better jobs.
Not externally audited.
Ethereum Mainnet not authorized.
```

Avoid claims about investment, yield, revenue-share, price-target, guaranteed resale value, guaranteed non-security, achieved AGI/ASI, autonomous enterprise without governance, mainnet authorization, production deployment, or external audit status.

## Quick start for engineers

```bash
npm install
cp .env.example .env
npm run compile
npm test
npm run test:all
npm run static-check
npm run readiness:v4.3
npm run assert:public-status
npm run evidence:docket:template
```

Ethereum Sepolia rehearsal:

```bash
npm run sepolia:rehearsal
npm run sepolia:evidence
```

Automated security/toolchain:

```bash
npm run audit:all
npm run audit:summarize
npm run audit:clearance-report
npm run audit:fail-on-critical
```

Ethereum Mainnet remains blocked unless all computed gates are real and founder deployment approval is explicit:

```bash
npm run preflight:ethereum-mainnet
npm run verify:agialpha-token
npm run mainnet:readiness-check
npm run mainnet:authorization-check
```

## Mainnet gate law

Ethereum Mainnet deployment is not authorized until all required gates are complete:

```text
compile/tests
Ethereum Sepolia rehearsal evidence
filled Evidence Docket
automated security/toolchain clearance
internal security review and findings remediation
legal/token counsel review if required by founder policy
tax/accounting review if required by founder policy
public-claims review
treasury/founder/admin ceremony
AGIALPHA token verification
AGIALPHA vault-funding approval, if funding is planned
formal founder deployment approval
```

Technical mainnet readiness is computed separately from deployment authorization. Deployment authorization remains NO until founder approval and every deployment gate is real.

## Security

Never commit private keys, `.env`, wallet seed phrases, RPC secrets, API keys, private buyer products, private Evidence Dockets, customer data, legal memos, tax memos, or paid buyer products.

See `SECURITY.md`.

## Production continuation repository

```text
Repository upload
→ GitHub security/rulesets
→ CI validation
→ compile/tests
→ Ethereum Sepolia rehearsal
→ filled Evidence Docket
→ automated security/toolchain clearance
→ internal security review
→ legal / tax / claims / treasury / founder gates as required
→ technical mainnet-readiness decision
→ founder deployment authorization decision
```

Current status remains:

```text
Not externally audited.
Ethereum Mainnet not authorized.
Ethereum Mainnet technical readiness: NO.
Ethereum Mainnet deployment authorization: NO.
Ethereum Mainnet authorization: NO.
```
