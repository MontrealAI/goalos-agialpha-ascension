# Private Sepolia Rehearsal Runbook

Run locally only. Do not put `SEPOLIA_RPC_URL`, deployer private keys, deployer addresses, receipts containing private operator metadata, or private notes in GitHub.

```bash
python scripts/private/run-private-sepolia-rehearsal.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The private operator must first run the local Sepolia proof-work replay with private RPC/deployer custody and preserve the raw receipt bundle as `.private/sepolia-rehearsal-private.json`. The committed helper reads `.private/` inputs, refuses mainnet semantics, confirms the private RPC reports chain id `11155111`, requires a local deployer key, verifies that `.private/sepolia-rehearsal-private.json` records completed proof-work, negative-path, and receipt-verification gates, and writes only `qa/public-sepolia-rehearsal-evidence.json`. It will not turn environment variables alone into a PASSED public commitment.

The public output contains hashes, pass/fail fields, contract counts, proof-work loop result, negative-path result, and no RPC URL, private key, or private deployer address.
