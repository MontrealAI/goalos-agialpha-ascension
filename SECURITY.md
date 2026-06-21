# Security Policy

## Current security status

```text
Audit-candidate package: yes
Externally audited: no
Mainnet authorized: no
```

## Reporting security issues

For now, report issues privately to the repository owner / maintainers. Do not create public issues containing exploitable details, private keys, RPC secrets, API keys, or customer data.

## Never commit

```text
.env
private keys
seed phrases
wallet backups
RPC credentials
API keys
secret JSON files
customer data
private Evidence Dockets
paid buyer products
legal/tax memos
unredacted audit findings
```

## Security scope

In scope:

```text
Solidity contract issues
deployment script issues
mainnet gate bypasses
role/permission bugs
secret exposure risks
unsafe public claims
Evidence Docket integrity issues
ProofBundle/replay integrity issues
```

Out of scope for public disclosure:

```text
attacks against third-party systems
external target scanning
social engineering
malware
private key recovery attempts
```

## Safe disclosure rule

If in doubt, disclose privately and redact sensitive details.

## Deployment security

Never commit `.private/` files, private keys, RPC URLs, API tokens, Safe signer lists, signatures, or private operator configuration. Mainnet broadcast is local-only and cannot run from CI.

## Three-stage Mainnet release model

| Stage | Status |
| --- | --- |
| Predeployment authorization | YES |
| Ethereum Mainnet deployed | NO |
| Postdeployment verification | NO |
| Production activation effective | NO |

This pre-broadcast state is a GO to deploy and is not contradictory: Stage A authorizes a human local chain-1 broadcast without requiring an already-existing Mainnet transaction, deployed address, receipt, Etherscan page, live ownership readback, or live canary. Stage B evaluates real chain-1 receipts, bytecode, verification, and ownership/role readback only after the human deployment ceremony. Stage C separately governs bounded live canary, monitoring, reconciliation, Ledger activation, and production reliance.

Not externally audited.
<!-- SEPOLIA_BACKED_INITIAL_MAINNET_V1_STATUS -->
Stage-A profile: `SEPOLIA_BACKED_INITIAL_MAINNET_V1`. Initial Mainnet infrastructure deployment is profile-gated; production ready: **NO**; user funds/activation/settlement/frontend/public reliance: **NO**; Mainnet deployed: **NO**; Not externally audited remains applicable.
