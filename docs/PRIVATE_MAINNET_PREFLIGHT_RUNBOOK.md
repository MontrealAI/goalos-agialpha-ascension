# Private Mainnet Preflight Runbook

Run locally only:

```bash
python scripts/private/run-private-mainnet-preflight.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The script keeps RPC details private, verifies Ethereum Mainnet/AGIALPHA locally, and writes only redacted public commitment evidence.
