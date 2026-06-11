# START HERE — GoalOS AGIALPHA Ascension v4.1

Use this version for audit and engineering handoff.

## What v4.1 is

An institutional audit-candidate implementation of GoalOS AGIALPHA Ascension using the existing AGIALPHA ERC-20 token on Ethereum mainnet.

## What v4.1 fixes

The package keeps the v4.0 AEP-001 institutional controls and improves Sepolia rehearsal safety. On Sepolia, leave `AGIALPHA_TOKEN_ADDRESS` blank to deploy `MockAGIALPHA` automatically. Ethereum mainnet still requires the exact deployed AGIALPHA token address.

## First commands

```bash
npm install
cp .env.example .env
npm run compile
npm test
npm run test:all
npm run static-check
```

## Rehearsal

```bash
npm run deploy:ethereum-sepolia
```

## Mainnet

Mainnet remains blocked until audit, legal, tax, security, treasury, public-claims, Sepolia evidence, and founder approval gates are complete.
