# Branch Protection and Ruleset Requirements

Ethereum Mainnet authorization must not be treated as complete until the repository has either the protections below enabled on `main` or a founder-held risk-acceptance commitment hash recorded in redacted public evidence.

## Required protections

- Pull request required before merge.
- Required status checks for repository validation, audit-candidate CI, Solidity audit toolchain, and mainnet authorization gate.
- No force pushes.
- No branch deletion.
- Conversation resolution required before merge.
- CODEOWNER review for sensitive paths where possible.
- Bypass restricted to owner/admin only.

## Sensitive paths

- `contracts/**`
- `scripts/**`
- `schemas/**`
- `.github/**`
- `.env.example`
- `package.json`
- `hardhat.config.ts`
- `docs/*MAINNET*`
- `docs/*DEPLOYMENT*`
- `docs/*AUTHORIZATION*`
- `audit/**`
- `security/**`

## Manual setup

If the GitHub CLI is authenticated with repository administration rights, configure the equivalent branch ruleset from repository settings or with `gh api`. Do not store a GitHub token in this repository.

Until protection evidence or an explicit founder-held risk-acceptance commitment exists, public authorization checkers must keep `MAINNET_DEPLOYMENT_AUTHORIZED=NO`.
