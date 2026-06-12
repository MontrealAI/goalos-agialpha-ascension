# Final Local Mainnet Deployment Runbook

1. Run public checks: `npm run mainnet:local-checks`.
2. Run automated/internal security toolchain: `npm run mainnet:security`.
3. Run local deterministic rehearsal: `npm run mainnet:local-rehearsal`.
4. Generate certificate: `npm run mainnet:certificate`.
5. Compute readiness: `npm run mainnet:readiness-check`.
6. Compute deployment authorization: `npm run mainnet:deployment-authorization-check`.
7. Compute Ethereum authorization: `npm run mainnet:authorization-check`.
8. Prepare runtime RPC/key locally outside GitHub.
9. Run final deployment: `npm run deploy:ethereum-mainnet:gated`.
10. Run post-deployment verification and publish only transaction/contract evidence.

Emergency pause/rollback follows `docs/FINAL_ROLLBACK_AND_INCIDENT_PLAN.md`.
