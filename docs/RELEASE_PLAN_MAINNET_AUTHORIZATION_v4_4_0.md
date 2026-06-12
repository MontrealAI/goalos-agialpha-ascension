# Release Plan: Mainnet Authorization v4.4.0

Release tag: `mainnet-authorization-v4.4.0`.

Release title: **GoalOS AGIALPHA Ascension v4.4.0 — Certificate-Backed Manual Ethereum Mainnet Authorization**.

## Scope

This release aligns package metadata, generated public status docs, certificate validation, QA manifests, workflow naming, branch-protection hardening guidance, and public release documentation for certificate-backed manual Ethereum Mainnet authorization.

## Authorization state

- Ethereum Mainnet technical readiness: **YES**.
- Ethereum Mainnet deployment authorization: **YES**.
- Ethereum Mainnet authorization: **YES**.
- Ethereum Mainnet deployed: **NO**.
- Final manual deployment command: `npm run deploy:ethereum-mainnet:gated`.

## Required before actual broadcast

- Optional but recommended branch-protection hardening.
- Local runtime RPC URL and deployer key outside GitHub.
- Valid runtime addresses at execution time.
- Post-deployment verification before any status can change to deployed.
