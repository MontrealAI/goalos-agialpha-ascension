# Official Badges

This document defines the official badge set for the GoalOS AGIALPHA Ascension repository.

## Badge principles

- **Official signals only:** badges must represent repository-owned workflows, package-declared versions, license posture, or certificate-backed status.
- **Automatically updated where possible:** GitHub Actions badges update dynamically from workflow runs.
- **Certificate-backed status:** authorization and deployment badges must mirror `qa/mainnet-authorization-certificate.json`.
- **No marketing inflation:** badges must not imply external audit completion, legal/tax approval, guaranteed security, yield, investment return, or live mainnet deployment.
- **Reviewer-first clarity:** every badge should help an operator, auditor, governance reviewer, or contributor understand current repository posture quickly.

## Active README badge set

| Badge | Source | Update model |
| --- | --- | --- |
| Repository Validation | `.github/workflows/repository-validation.yml` | Dynamic GitHub Actions badge |
| Final Public Mainnet Authorization | `.github/workflows/final-public-mainnet-authorization.yml` | Dynamic GitHub Actions badge |
| Mainnet Authorization Gate | `.github/workflows/mainnet-authorization-gate.yml` | Dynamic GitHub Actions badge |
| Solidity Audit Toolchain | `.github/workflows/solidity-audit-toolchain.yml` | Dynamic GitHub Actions badge |
| License: MIT | `NOTICE.md` and package metadata | Static repository metadata badge |
| Solidity version | `package.json` | Static package-declared version badge |
| Hardhat version | `package.json` | Static package-declared version badge |
| TypeScript version | `package.json` | Static package-declared version badge |
| Ethereum Mainnet authorization | `qa/mainnet-authorization-certificate.json` | Certificate-backed static status badge |
| Ethereum Mainnet deployed | `qa/mainnet-authorization-certificate.json` | Certificate-backed static status badge |

## Maintenance checklist

When status, tooling, or workflow names change:

1. Regenerate or validate the public authorization certificate.
2. Update README badges only after the underlying source changes.
3. Keep badge labels plain, corporate, and factual.
4. Run `npm run docs:status` if certificate-derived status documents need regeneration.
5. Run `npm run qa:manifest:verify` before release-oriented documentation changes are merged.

## Prohibited badges

Do not add badges that claim or imply:

- external audit completion unless a real external audit artifact exists;
- legal, tax, securities, or investment approval;
- guaranteed security or exploit immunity;
- live Ethereum Mainnet deployment while `MAINNET_DEPLOYED` is `NO`;
- new AGIALPHA token deployment, minting, yield, revenue share, or price appreciation.
