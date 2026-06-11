# GoalOS AGIALPHA Ascension

GoalOS AGIALPHA Ascension v4.3+
Ethereum Sepolia rehearsal: completed / pending, based on evidence.
Audit toolchain: implemented and run / pending, based on evidence.
Dependency PRs: triaged, not blindly merged.
External audit: not closed unless real audit closure exists.
Ethereum Mainnet: NOT_AUTHORIZED unless all gates pass.
Not audited.
This repository is not mainnet authorized.

Mainnet AGIALPHA token address: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. This repository must not deploy or mint a new AGIALPHA token on Ethereum Mainnet.

# GoalOS AGIALPHA Ascension

**GoalOS AGIALPHA Ascension** is a GoalOS-native reimplementation of **α‑AGI Ascension** using the existing Ethereum Mainnet `$AGIALPHA` token as the utility coordination asset for proof-settled AI workflow work.

```text
GoalOS decides what may evolve.
AGIALPHA coordinates proof-settled work.
Evidence Dockets make claims auditable.
```

## Current status

```text
Repository status: initial institutional repository candidate.
Implementation package: v4.3 gate-clean evidence-ready audit candidate.
Ethereum Sepolia rehearsal: next.
Ethereum Mainnet authorization: no.
External audit closure: not complete.
Legal / tax / public-claims review: not complete.
```

Do **not** call this repository audited, mainnet authorized, legally approved, tax reviewed, production deployed, or guaranteed non-security.

## Existing AGIALPHA token

This repository uses the existing Ethereum Mainnet `$AGIALPHA` ERC-20 token:

```text
0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA
```

The implementation does **not** deploy or mint a new AGIALPHA token on Ethereum Mainnet.

## Source doctrine

GoalOS AGIALPHA Ascension combines two reference doctrines:

1. **GoalOS / AEP-001**  
   A proof-of-evolution constitution: `Aim → Act → Prove → Evolve`.  
   The public/private boundary is: do not put intelligence on-chain; put proof of intelligence on-chain.

2. **AGI ALPHA / α‑AGI Ascension**  
   A proof-settled organizational substrate: `Request → Escrow → Execute → Proof → Validate → Settle → Chronicle`.  
   Settlement requires replayable ProofBundles, validator review, and claim boundaries.

## What this repository contains

```text
contracts/        Ethereum Solidity contracts and registries
scripts/          deployment, verification, readiness, and evidence scripts
schemas/          Evidence Docket, ProofBundle, and mainnet gate schemas
test/             Hardhat tests
docs/             operator, auditor, architecture, claim-boundary, and gate docs
audit/            audit handoff templates and gate matrices
qa/               generated manifests and readiness reports
.github/          issue templates, workflows, and repository governance
```

## Core implementation layers

```text
AGIALPHA proof-work coordination
AEP-001 proof-of-evolution registries
Evidence Docket 6.1
Settlement-grade ProofBundle schema
Reviewer / evaluator / slashing controls
Launch gates and mainnet authorization checks
Legacy AGIJobManager continuity registry
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
```

Avoid:

```text
investment
yield
revenue share
price target
guaranteed resale value
guaranteed non-security
achieved AGI / ASI
autonomous enterprise without governance
mainnet authorized
audited
```

## Quick start for engineers

```bash
npm install
cp .env.example .env
npm run compile
npm test
npm run test:all
npm run static-check
npm run readiness:v4.3
npm run evidence:docket:template
```

Ethereum Sepolia rehearsal:

```bash
npm run deploy:ethereum-sepolia
```

Ethereum Mainnet remains blocked unless all gates are real:

```bash
npm run preflight:ethereum-mainnet
npm run verify:agialpha-token
npm run deploy:ethereum-mainnet:gated
npm run verify:deployment
```

## Mainnet gate law

Ethereum Mainnet deployment is not authorized until all required gates are complete:

```text
compile/tests
Ethereum Sepolia rehearsal
filled Evidence Docket
external audit closure
legal/token counsel review
tax/accounting review
public-claims review
treasury/founder/admin ceremony
AGIALPHA token verification
AGIALPHA vault-funding approval, if funding is planned
formal founder approval
```

## Recommended first use cases

```text
1. Customer Support Proof Room
2. Claims-Safe Launch Content
3. Repository + Website Documentation QA
4. Commercialization Proof-of-Value
5. Builder / Reviewer Credentialing
```

## License / rights

This repository contains a strategic implementation candidate. Do not assume open-source licensing until the founder and counsel approve the final license posture. See `LICENSE_DECISION.md`.

## Security

Never commit private keys, `.env`, wallet seed phrases, RPC secrets, API keys, private buyer products, private Evidence Dockets, customer data, legal memos, tax memos, or unpaid product ZIPs.

See `SECURITY.md`.

## Production continuation repository

This GitHub repository is intended to become the production-continuation source of truth for GoalOS AGIALPHA Ascension.

```text
Repository upload
→ GitHub security/rulesets
→ CI validation
→ compile/tests
→ Ethereum Sepolia rehearsal
→ filled Evidence Docket
→ external audit closure
→ legal / tax / claims / treasury / founder gates
→ mainnet decision
```

Current status remains:

```text
Not audited.
Not mainnet authorized.
```
