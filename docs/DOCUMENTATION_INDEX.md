# Documentation Index

This index is the routing page for reviewers, operators, auditors, and contributors. It is intentionally claim-bounded: generated status documents summarize certificate-backed evidence, but only `qa/mainnet-authorization-certificate.json` is the authorization source of truth.

## Current status and source of truth

- `README.md` — public overview, badges, current label, safety boundary, and canonical command summary.
- `START_HERE.md` — shortest repository entry point and recommended read order.
- `docs/CURRENT_STATUS.md` — generated current status summary.
- `docs/DOCUMENTATION_MAINTENANCE.md` — documentation source-of-truth order, update checklist, validation matrix, and PR documentation expectations.
- `qa/mainnet-authorization-certificate.json` — active certificate backing technical readiness, deployment authorization, Ethereum Mainnet authorization, and deployment status.
- `docs/MAINNET_AUTHORIZATION_CERTIFICATE.md` — human-readable certificate summary generated from the certificate JSON.

## Deployment and verification

- `docs/DEPLOYMENT_START_HERE.md` — shortest safe Sepolia and Ethereum Mainnet deployment and verification command paths.
- `docs/CONTRACT_VERIFICATION_START_HERE.md` — contract verification entry point; use wrapper commands for default Sepolia and Mainnet operator verification, not raw Mainnet manifest-only verification when constructor args are redacted.
- `docs/SEPOLIA_DEPLOYMENT_GUIDE.md` — Sepolia operator guide.
- `docs/MAINNET_OPERATOR_RUNBOOK.md` — Mainnet operator runbook.
- `docs/DEPLOYMENT_TROUBLESHOOTING.md` — deployment failure recovery and troubleshooting.
- `docs/DEPLOYMENT_FAQ.md` — deployment FAQ.

## Mainnet gates and claim boundaries

- `docs/PUBLIC_MAINNET_AUTHORIZATION_RUNBOOK.md` — public authorization gate sequence.
- `docs/MAINNET_AUTHORIZATION_MODEL.md` — authorization model and guardrails.
- `docs/ETHEREUM_MAINNET_GATES_v2_0.md` — Mainnet gate model.
- `docs/SAFE_CLAIMS_AND_TOKEN_BOUNDARY_v3_0.md` — safe public-claims and AGIALPHA token-boundary guidance.
- `docs/SAFE_CLAIMS.md` — public-safe wording reference.

## Audit and security review

- `audit/README.md` — audit documentation entry point.
- `audit/AUDIT_SCOPE.md` — audit scope.
- `audit/AUDIT_FINDINGS_REGISTER.md` — findings register.
- `audit/TOOLCHAIN_CLEARANCE_REPORT.md` — automated/internal toolchain clearance summary.
- `audit/AUTOMATED_SECURITY_TOOLCHAIN.md` — security toolchain description.
- `docs/EXTERNAL_AUDITOR_HANDOFF.md` — external auditor handoff package.

## Contributor and governance materials

- `CONTRIBUTING.md` — contribution process and repository expectations.
- `GOVERNANCE.md` — governance reference.
- `SECURITY.md` — vulnerability reporting and security posture.
- `CODE_OF_CONDUCT.md` — community conduct expectations.
- `LICENSE_DECISION.md` — license posture; no license is granted unless this file changes.

## Maintenance expectations

- Use `docs/DOCUMENTATION_MAINTENANCE.md` before changing README files, runbooks, public website copy, generated status docs, or claim-boundary materials.
- Regenerate certificate-derived public status docs with `npm run docs:status` after certificate changes.
- Run `npm run assert:public-status` after editing generated status docs or their generator.
- Run `npm run deployment:claim-boundary:check` after editing deployment, verification, or deployment-evidence docs.
- Do not mark Ethereum Mainnet deployed as `YES` without real `chainId=1` transaction evidence.
- Do not mark contracts verified as `YES` without source/bytecode verification evidence or confirmed already-verified status.
