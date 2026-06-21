# Start Here: Ethereum Mainnet

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

It does not claim external audit completion, legal approval, tax review, guaranteed security, guaranteed token classification, investment return, yield, price target, revenue share, or production deployment.

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.


## Command center

1. Check public repo status: `npm run mainnet:status`
2. Run local public checks: `npm run mainnet:local-checks`
3. Run automated/internal security toolchain: `npm run mainnet:security`
4. Run local deterministic rehearsal: `npm run mainnet:local-rehearsal`
5. Run public AGIALPHA token verification: `npm run verify:agialpha-token:public`
6. Generate Mainnet Authorization Certificate: `npm run mainnet:certificate`
7. Compute technical readiness: `npm run mainnet:readiness-check`
8. Compute deployment authorization: `npm run mainnet:deployment-authorization-check`
9. Compute Ethereum Mainnet authorization: `npm run mainnet:authorization-check`
10. Show final manual deployment command: `npm run mainnet:next`
11. Run final local gated deployment: `npm run deploy:ethereum-mainnet:gated`
12. Generate post-deployment report after real transaction evidence exists.
