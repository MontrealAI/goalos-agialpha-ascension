This deployment is dormant infrastructure only. It is not production-ready. It does not authorize user funds, Phase-B configuration, activation, settlement, a public frontend, production announcements, or public reliance.

# Dormant Initial Mainnet Recovery

Dormant Mainnet deployment is a one-attempt ceremony. The private journal at `.private/dormant-mainnet/deployment-journal.json` records each transaction immediately after submission and before receipt waiting. If any transaction hash or deployed address exists, the live deployment command refuses to start again.

Use:

- `npm run deploy:mainnet:dormant:status` to inspect whether a journaled attempt exists.
- `npm run deploy:mainnet:dormant:recover` for expert recovery guidance without deleting or overwriting the journal.
- `npm run verify:mainnet:dormant:auto` to retry verification only. Etherscan verification failure never justifies redeployment.
- `npm run deploy:mainnet:dormant:postcheck` after receipt-backed evidence exists.

Raw addresses may enter tracked public postdeployment evidence only after real chain-1 receipts, code, verification/already-verified status, canonical AGIALPHA validation, Wallet B authority readback, Wallet A zero authority, pending owner count zero, Phase-B queued/inactive status, checked initial balances zero, and activation=false all pass.
