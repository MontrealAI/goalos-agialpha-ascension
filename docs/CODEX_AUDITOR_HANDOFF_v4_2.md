> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# CODEX / Auditor Handoff v4.2

Act as a senior Solidity security engineer and release engineer.

## Task

Bring GoalOS AGIALPHA Ascension v4.2 from evidence-ready audit candidate to Sepolia evidence package.

## Commands

```bash
npm install
cp .env.example .env
npm run compile
npm test
npm run test:all
npm run static-check
npm run readiness:v4.2
npm run evidence:docket:template
npm run deploy:ethereum-sepolia
```

If compiler download fails:

```bash
npm run direct-solc-compile
npm run generate-artifacts-from-solc
npm run test:no-compile
```

## Deliverables

- compile log
- test log
- static QA log
- deployment JSON
- deployed addresses
- transaction hashes
- completed Evidence Docket
- audit closure notes
- residual-risk register

## Restrictions

Do not deploy Ethereum mainnet.
Do not weaken mainnet gates.
Do not add investment, yield or revenue-share mechanics.
Do not put private intelligence or private workflow evidence on-chain.
