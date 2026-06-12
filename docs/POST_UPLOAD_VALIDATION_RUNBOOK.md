> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Post-Upload Validation Runbook

After uploading all batches, confirm:

## File presence

- [ ] `README.md`
- [ ] `GITHUB_COMMAND_CENTER.html`
- [ ] `.github/workflows/agialpha-audit-candidate-ci.yml`
- [ ] `.github/workflows/mainnet-gate-watch.yml`
- [ ] `contracts/registry/LaunchGateRegistry.sol`
- [ ] `scripts/mainnet-authorization-check.py`
- [ ] `scripts/repository_production_readiness_check.py`
- [ ] `docs/PRODUCTION_CONTINUATION_PLAN.md`
- [ ] `docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md`
- [ ] `schemas/agialpha-mainnet-gate-v4.3.schema.json`

## Status text

- [ ] README says Not externally audited.
- [ ] README says Ethereum Mainnet not authorized.
- [ ] README identifies the existing AGIALPHA token.
- [ ] README does not say guaranteed non-security.
- [ ] README does not say mainnet ready.

## First checks

```bash
npm run repo:all
npm run static-check
npm run readiness:v4.3
npm run mainnet:authorization-check
```

Expected mainnet result:

```text
NOT_AUTHORIZED
```
