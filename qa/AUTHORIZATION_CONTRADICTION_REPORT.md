# Authorization Contradiction Report

Active source of truth: `qa/mainnet-authorization-certificate.json`.

## Summary
- HISTORICAL_DOC_OK_WITH_BANNER: 22
- OLD_AUDIT_REPORT_OK_AS_ARCHIVED: 10
- SCRIPT_BACKWARD_COMPATIBILITY_OK: 8
- STALE_QA_ARTIFACT_MOVE_TO_HISTORICAL: 2

## Final public states
- TECHNICALLY_MAINNET_READY: YES
- MAINNET_DEPLOYMENT_AUTHORIZED: YES
- ETHEREUM_MAINNET_AUTHORIZED: YES
- MAINNET_DEPLOYED: NO

## Classification notes
- Active docs were updated to certificate-backed public YES.
- Historical docs are bannered where retained.
- Script compatibility flags are deprecated/no-op and acceptable.
- Old audit reports are archived historical evidence, not active gates.
- Stale QA artifacts were regenerated or moved under `qa/historical/`.
