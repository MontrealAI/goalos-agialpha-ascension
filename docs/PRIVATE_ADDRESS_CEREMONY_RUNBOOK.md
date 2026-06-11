# Private Address Ceremony Runbook

Founder, treasury, admin, vault, security, community, and deployer addresses remain local-only.

```bash
python scripts/private/generate-address-ceremony-commitment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The private ceremony is written under `.private/address-ceremony-private.json`. Public GitHub receives only `qa/public-address-ceremony-evidence.json`, which contains a commitment hash and public-safety flags.
