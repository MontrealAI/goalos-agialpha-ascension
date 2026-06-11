# Ethereum Mainnet Deployment Runbook v3.0

## Current status

This package can deploy the contracts, but mainnet remains gated.

## Local / CI

```bash
npm install
cp .env.example .env
npm run compile
npm test
npm run test:agialpha
npm run test:aep
npm run static-check
```

## Ethereum Sepolia rehearsal

```bash
npm run deploy:ethereum-sepolia
```

Then run:

1. Create Proof Seed.
2. Create GoalOSCommit.
3. Commit Run.
4. Post Proof Job.
5. Builder claims.
6. Builder submits proof.
7. Reviewer validates.
8. Append ProofRoot.
9. Register ProofBundle.
10. Record EvalAttestation.
11. Issue SelectionCertificate.
12. Record Evidence Docket.
13. Issue credential / reputation / alpha-WU.
14. Record rollout or rollback.

## Mainnet preflight

```bash
npm run preflight:ethereum-mainnet
npm run verify:agialpha-token
```

## Mainnet deploy

Only after gates:

```bash
npm run deploy:ethereum-mainnet:gated
npm run verify:deployment
```

## Mainnet gates

- automated security/toolchain clearance
- internal security review
- Ethereum Sepolia evidence docket
- legal/token counsel memo
- tax/accounting memo
- public claims review
- promoter disclosure policy
- treasury/founder/admin address ceremony
- AGIALPHA vault-funding approval, if funding vaults
- formal founder approval

## Post-deployment

- save manifest
- verify contracts on Etherscan
- verify AGIALPHA token address
- verify all contract code
- verify roles
- verify pause controls
- verify Evidence Docket public/private boundaries
- fund vaults only after treasury approval
