# Start Here: Ethereum Mainnet

# Current Status

## Ethereum Mainnet release state

| Item | Current value |
| --- | --- |
| Ethereum Mainnet deployment | PASS — YES |
| Mainnet configuration | PASS — YES |
| GoalOS contracts | 48 |
| Canonical external AGIALPHA | 1 |
| Operator verification evidence | PASS — 48/48 |
| Postdeployment operator evidence | PASS — VERIFIED_AND_CONFIGURED |
| Phase-B grants | PASS — 14/14 |
| Permanent authority | PASS — Wallet B / Ledger |
| Wallet A managed roles | PASS — 0 |
| Predeployment authorization | NOT_APPLICABLE — DIRECT_OPERATOR_NO_CERTIFICATE |
| Independent live revalidation | PENDING_EXTERNAL_INPUT |
| Source-identity reproducibility | PENDING |
| Production activation | NOT_ACTIVATED |
| User-fund authorization | NO |

PENDING_EXTERNAL_INPUT is not a deployment failure. It means optional independent dual-provider validation was not run in an environment containing protected read-only credentials.

Current source of truth: `qa/mainnet-release-state.json`, `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/verification-evidence.json`, `config/ethereum-mainnet.contracts.json`, and `release/mainnet-2026-06-21/`. Historical Stage-A predeployment records are preserved but do not override the current direct-operator postdeployment release state.

## Claim boundary

No external-audit claim is made by this release. External-audit completion is not an active release-state gate. This repository does not claim production activation, user-fund authorization, legal approval, tax approval, guaranteed security, yield, revenue share, or price appreciation.


## Safe ordinary validation

```bash
npm run mainnet:release-state:all
```

The ordinary validation path is offline/public and must not receive deployer private keys, mnemonics, Ledger seeds, RPC URLs, Etherscan keys, or write/broadcast permissions.
