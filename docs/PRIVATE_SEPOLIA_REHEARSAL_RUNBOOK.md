# Private Sepolia Rehearsal Runbook

Run locally only:

```bash
python scripts/private/run-private-sepolia-rehearsal.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The script loads private RPC/deployer inputs locally, refuses mainnet, records a private evidence file under `.private/`, and writes only `qa/public-sepolia-rehearsal-evidence.json` as a redacted public commitment.
