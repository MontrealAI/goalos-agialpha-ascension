# Mainnet Authorization Sprint Runbook

1. Preserve the deterministic dependency baseline and use `npm ci`.
2. Run baseline checks and update `qa/BASELINE_GREEN_REPORT.json` plus `qa/BASELINE_COMMAND_LOG.md`.
3. Run the automated/internal security toolchain and produce `audit/reports/<run>/` plus `audit/TOOLCHAIN_CLEARANCE_REPORT.md`.
4. Complete public Ethereum Sepolia rehearsal with receipts and independent RPC verification.
5. Run read-only Ethereum Mainnet AGIALPHA verification and preflight.
6. Run mainnet fork simulation without broadcasting.
7. Enable branch protection on `main`, or record explicit founder risk acceptance.
8. Complete address ceremony, founder approval, and policy signoffs/waivers.
9. Run:

```bash
npm run mainnet:readiness-check
npm run mainnet:deployment-authorization-check
npm run ethereum-mainnet:authorization-check
npm run mainnet:authorization-check
```

10. If and only if all three statuses are YES, the founder/deployer may manually run:

```bash
npm run deploy:ethereum-mainnet:gated
```

CI must never run the final Ethereum Mainnet deployment command automatically.
