# Private Sepolia Rehearsal Runbook

Run locally only. Do not put `SEPOLIA_RPC_URL`, deployer private keys, deployer addresses, receipts containing private operator metadata, or private notes in GitHub.

```bash
python scripts/private/run-private-sepolia-rehearsal.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The script reads `.private/` inputs, refuses mainnet semantics, targets chain id `11155111`, uses `MockAGIALPHA` unless a private Sepolia token is supplied locally, records private receipt/evidence material in `.private/sepolia-rehearsal-private.json`, and writes only `qa/public-sepolia-rehearsal-evidence.json`.

The public output contains hashes, pass/fail fields, contract counts, proof-work loop result, negative-path result, and no RPC URL, private key, or private deployer address.
