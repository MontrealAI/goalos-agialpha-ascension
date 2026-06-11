# Ethereum Mainnet Deployment Runbook

## Install and test

```bash
npm install
npm run compile
npm test
npm run test:agialpha
npm run static-check
```

## Ethereum Sepolia rehearsal

```bash
npm run deploy:ethereum-sepolia
```

Run the full proof-work loop on Sepolia.

## Mainnet preflight

```bash
npm run preflight:ethereum-mainnet
```

## Mainnet deployment

Only after gates:

```bash
npm run deploy:ethereum-mainnet:gated
```

## Do not deploy mainnet unless

- automated security/toolchain clearance and internal security review are complete
- Sepolia rehearsal evidence is complete
- legal/token counsel review is complete
- tax/accounting review is complete
- public claims review is complete
- treasury/founder/admin address ceremony is complete
- formal founder approval is complete
