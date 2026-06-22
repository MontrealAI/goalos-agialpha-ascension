# Documentation Maintenance

Audience: contributors and reviewers.
Purpose: define source-of-truth precedence and generated/editable documentation rules.
Current status: current.
Authoritative source: this policy plus repository evidence files.
Last reviewed: 2026-06-22.
Next review trigger: release evidence, generated-doc drift, status claim, or Stage-C change.

## Source-of-truth hierarchy

1. Mainnet receipts and on-chain readbacks.
2. `deployments/ethereum-mainnet.agialpha.latest.json`.
3. `qa/mainnet-postdeploy/verification-evidence.json` (or the current verification evidence path).
4. `qa/mainnet-postdeploy/` evidence.
5. `qa/mainnet-release-state.json`.
6. `release/mainnet-2026-06-21/`.
7. Generated public docs.

The historical Stage-A/predeployment certificate is historical evidence. It is not the current sole source of truth for the configured 2026-06-21 deployment.

## File classes

- Authoritative: deployment manifest, postdeploy evidence, release state, receipts/readbacks.
- Generated: `docs/ETHEREUM_MAINNET_CONTRACTS.md`, `config/ethereum-mainnet.contracts.json`, `app/config/ethereum-mainnet.contracts.generated.ts`, `website/data/ethereum-mainnet.contracts.json`.
- Historical: archived pre-mainnet and legacy authorization docs.
- Editable: explanatory docs that summarize evidence without creating new claims.
- Review-triggered: README, current status, website/app status, governance, runbooks, badges, release docs.

## Maintenance checklist

Before merging documentation changes that affect public status, deployment, verification, operator guidance, or generated artifacts:

1. Trace every YES/NO status to the highest available source in the hierarchy above; do not promote historical or seed-only evidence into current live claims.
2. Keep generated files generated: update the source inputs or generator first, then run the documented generator/check command instead of hand-editing generated output.
3. Preserve claim boundaries for Mainnet deployment, contract verification, production activation, user-fund authorization, external audit completion, and canonical AGIALPHA ownership.
4. Treat missing current-documentation links as release blockers; historical paper/provenance links may warn but must not be used as current operator guidance.
5. Record the exact commands run in the PR body, including failures and environment-limited warnings.

## Required checks

- `npm run docs:all` validates generated Mainnet docs, internal documentation links, stale current claims, and the Mainnet contract registry.
- `python scripts/check_docs_links.py` fails on unresolved current-documentation links and warns only for historical/provenance material.
- `python scripts/check_stale_claims.py` blocks known stale public-status phrases outside approved archive/provenance paths.

Run `npm run docs:all` before merging public-status documentation changes.
