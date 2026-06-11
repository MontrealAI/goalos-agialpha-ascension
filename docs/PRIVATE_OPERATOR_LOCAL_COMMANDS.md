# Private Operator Local Commands

```bash
python scripts/private/generate-private-operator-template.py
cp .private/mainnet-operator-input.example.json .private/mainnet-operator-input.json
cp .private/mainnet-operator.env.example .private/mainnet-operator.env
python scripts/private/validate-private-operator-inputs.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/run-private-sepolia-rehearsal.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/run-private-mainnet-preflight.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/generate-founder-approval-message.py --input .private/mainnet-operator-input.json
python scripts/private/verify-founder-approval-private.py --input .private/mainnet-operator-input.json
python scripts/private/generate-address-ceremony-commitment.py --input .private/mainnet-operator-input.json
python scripts/private/generate-redacted-public-evidence.py --input .private/mainnet-operator-input.json
python scripts/mainnet-authorization-check.py --with-redacted-private-evidence
```

Do not commit `.private/`.
