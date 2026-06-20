# Ubuntu Operator Runbook — Dormant Initial Mainnet Deployment

**DORMANT INITIAL MAINNET DEPLOYMENT — NOT PRODUCTION READY — NO USER FUNDS — NO ACTIVATION — NO PUBLIC RELIANCE**

This deployment is operationally dormant and unfunded. It is not guaranteed to be globally frozen against unsolicited third-party calls or transfers.

1. This workflow is dormant, unfunded, and non-production.
2. Wallet A is disposable gas payer only: `0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E`.
3. Wallet B is Ledger authority from construction: `0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99`.
4. Never enter a seed phrase. Sign only typed data with Wallet B.
5. Run no-broadcast checks: `npm run dormant:mainnet:doctor`, `npm run dormant:mainnet:plan`, `npm run dormant:mainnet:fork-rehearsal`, `npm run dormant:mainnet:certificate`, `npm run dormant:mainnet:certificate:validate`.
6. Ledger proof: `npm run dormant:mainnet:ledger-approve`; store signature only under `.private/dormant-mainnet/`.
7. Review plan, nonce, contract count, fee caps, and worst-case gas.
8. Live command: `npm run dormant:mainnet:live` only from local interactive shell after arming.
9. If interrupted, preserve journal and run `npm run dormant:mainnet:resume`.
10. Retry verification with `npm run dormant:mainnet:verify`; never redeploy for verification failure.
11. Run postchecks with `npm run dormant:mainnet:postcheck`.
12. Generate evidence with `npm run dormant:mainnet:evidence`.
13. Sweep Wallet A only after all evidence passes: `npm run dormant:mainnet:sweep-deployer`.
14. Prohibited after deployment: funding contracts, executing Phase B, public launch claims, frontend publication, production announcement.
15. Later production requires the independent production process; dormant evidence cannot produce production YES.

## Emergency one-page runbook
RPC outage: stop, do not switch blindly; compare independent RPCs. Gas spike: stop before next transaction and resume from journal. Dropped transaction: classify as dropped before replacing. Replacement: record replacement relationship. Nonce drift: stop. Partial deployment: never rerun from transaction 0; resume only from first unresolved item. Etherscan outage: rerun verification only. Receipt disagreement or reorg: stop until confirmation depth is restored. Unexpected authority: stop and publish blocker. Lost Wallet A before completion: stop; do not skip nonces or redeploy from another account without a new plan/certificate.
