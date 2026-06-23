# Current Status

## Ethereum Mainnet release state

| Item | Current value |
| --- | --- |
| Deployment path | `DIRECT_OPERATOR_NO_CERTIFICATE` |
| Predeployment authorization | NOT_APPLICABLE — DIRECT_OPERATOR_NO_CERTIFICATE |
| Ethereum Mainnet deployment | PASS — YES |
| Mainnet configuration | PASS — YES |
| GoalOS contracts | PASS — 48 |
| Canonical registry | PASS — 49 entries |
| Operator verification evidence | PASS — 48/48 |
| Postdeployment operator evidence | PASS — VERIFIED_AND_CONFIGURED |
| Phase-B grants | PASS — 14/14 |
| Permanent authority | PASS — Wallet B / Ledger |
| Wallet A managed roles | PASS — 0 |
| Independent live revalidation | PENDING_EXTERNAL_INPUT |
| Production activation | NOT ACTIVATED |
| User-fund authorization | NO |

PENDING_EXTERNAL_INPUT is not a failure of the deployed release. It means the optional independent dual-provider revalidation was not executed in an environment containing protected read-only provider credentials.

Current source of truth: `qa/mainnet-release-state.json`, `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/verification-evidence.json`, `config/ethereum-mainnet.contracts.json`, and `release/mainnet-2026-06-21/`. Historical Stage-A predeployment records are preserved but do not override the current direct-operator postdeployment release state.

## Claim boundary

Not externally audited. No external-audit claim is made by this release. The external audit completion gate is not an active release-state gate. This repository does not claim production activation, user-fund authorization, legal approval, tax approval, guaranteed security, yield, revenue share, or price appreciation.
