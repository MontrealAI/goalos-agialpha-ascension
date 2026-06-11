# Mainnet Authorization With Redacted Evidence

Public-only checks run without secrets and return `NO` with `PRIVATE_OPERATOR_EVIDENCE_PENDING` until redacted evidence commitments are present.

With valid redacted private evidence:

```bash
python scripts/mainnet-readiness-check.py --with-redacted-private-evidence
python scripts/mainnet-deployment-authorization-check.py --with-redacted-private-evidence
python scripts/ethereum-mainnet-authorization-check.py --with-redacted-private-evidence
```

The checkers can return YES only if the redacted evidence is public-safe and records YES/PASSED for the required private operator workflows.
