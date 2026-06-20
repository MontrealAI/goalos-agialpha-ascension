# Dormant Initial Mainnet Deployment Runbook

This deployment is dormant infrastructure only. It is not production-ready. It does not authorize user funds, customer onboarding, protocol activation, settlement, or public reliance.

## Purpose

`DORMANT_INITIAL_MAINNET_DEPLOYMENT` is a separate authorization class for deployment mechanics, source verification, ownership readback, and operational learning on Ethereum Mainnet. It does not replace or weaken the production five-gate authorization.

## Required commands

Run these from the repository root. Do not broadcast Mainnet from CI.

```bash
npm run dormant-mainnet:build
npm run dormant-mainnet:fork-rehearsal
npm run dormant-mainnet:certificate
npm run dormant-mainnet:certificate:validate
npm run dormant-mainnet:status
npm run deploy:mainnet:dormant:prepare
npm run deploy:mainnet:dormant:live-local-gated
npm run deploy:mainnet:verify
npm run dormant-mainnet:postdeploy-verify
npm run dormant-mainnet:final-check
```

`deploy:mainnet:dormant:live-local-gated` refuses to run in CI and requires `DORMANT_MAINNET_TYPED_PLAN_HASH` to exactly equal the generated deployment-plan hash.

## Claim boundary

Generated public status is derived from `qa/dormant-mainnet-readiness/authorization-certificate.json`, not manual README edits. Unsolicited token transfers cannot be universally prevented; they are unauthorized and do not constitute accepted user funds.
