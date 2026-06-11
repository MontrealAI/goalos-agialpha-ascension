# Final Local Operator Runbook

This runbook is for the private operator. GitHub Actions must not execute the final deployment command.

## Prerequisites

- Private input and env files exist under `.private/`.
- Redacted public evidence has been generated and committed.
- Public checkers report `TECHNICALLY_MAINNET_READY: YES`, `MAINNET_DEPLOYMENT_AUTHORIZED: YES`, and `ETHEREUM_MAINNET_AUTHORIZED: YES`.
- Ethereum Mainnet AGIALPHA token address is exactly `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`.
- Founder/deployer accepts that the repository is not externally audited.

## Commands

```bash
python scripts/private/generate-private-operator-template.py
cp .private/mainnet-operator-input.example.json .private/mainnet-operator-input.json
cp .private/mainnet-operator.env.example .private/mainnet-operator.env
python scripts/private/validate-private-operator-inputs.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/run-private-sepolia-rehearsal.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/run-private-mainnet-preflight.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/verify-founder-approval-private.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/generate-address-ceremony-commitment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/private/generate-redacted-public-evidence.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
python scripts/mainnet-authorization-check.py --with-redacted-private-evidence
```

If the final public authorization JSON is `YES`, the private operator may run:

```bash
python scripts/private/run-final-local-mainnet-deployment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The final script requires local confirmation via the private env. No mainnet deployment occurred in this PR.
