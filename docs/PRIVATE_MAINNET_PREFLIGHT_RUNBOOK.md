# Private Mainnet Read-Only Preflight Runbook

Run locally only. This is read-only preflight, not deployment.

```bash
python scripts/private/run-private-mainnet-preflight.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The script reads `MAINNET_RPC_URL` from `.private/mainnet-operator.env`, confirms chain id `1`, checks the fixed AGIALPHA token address, confirms mainnet scripts must not deploy `MockAGIALPHA` or a new AGIALPHA token, optionally records fork-simulation evidence, writes `.private/mainnet-preflight-private.json`, and emits `qa/public-mainnet-preflight-evidence.json`.

The public output contains the AGIALPHA token address, pass/fail fields, code/preflight/fork commitment hashes where available, and no RPC URL or private addresses.
