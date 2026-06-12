> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Mainnet Authorization With Redacted Evidence

The public authorization system has two modes.

## Public-only mode

```bash
python scripts/mainnet-authorization-check.py --public-only
```

This mode requires no secrets. If redacted private evidence is missing, it returns:

- `TECHNICALLY_MAINNET_READY: NO`;
- `MAINNET_DEPLOYMENT_AUTHORIZED: NO`;
- `ETHEREUM_MAINNET_AUTHORIZED: NO`;
- blocker `PRIVATE_OPERATOR_EVIDENCE_PENDING`.

This is an expected public CI state and should not break routine CI.

## Redacted-private-evidence mode

```bash
python scripts/mainnet-readiness-check.py --with-redacted-private-evidence
python scripts/mainnet-deployment-authorization-check.py --with-redacted-private-evidence
python scripts/ethereum-mainnet-authorization-check.py --with-redacted-private-evidence
```

This mode reads only public redacted evidence under `qa/`. It validates public-safety flags, hashes, chain target, token address, private Sepolia commitment, mainnet preflight commitment, founder approval commitment or private-custody attestation, address ceremony commitment, and policy decision commitment.

YES is computed from evidence; it is not created by editing README text.
