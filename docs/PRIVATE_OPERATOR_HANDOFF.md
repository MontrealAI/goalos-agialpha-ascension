> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Private Operator Handoff

Private operators run the custody-sensitive evidence workflow locally. Do not paste private inputs into GitHub, GitHub Actions secrets, PR comments, public docs, logs, artifacts, or committed files.

## Private evidence kept locally

- `.private/mainnet-operator-input.json`
- `.private/mainnet-operator.env`
- `.private/sepolia-rehearsal-private.json`
- `.private/mainnet-preflight-private.json`
- `.private/address-ceremony-private.json`
- `.private/founder-approval-private.json`
- `.private/final-deploy-private.env`

## Public redacted evidence that may be committed

- `qa/public-sepolia-rehearsal-evidence.json`
- `qa/public-mainnet-preflight-evidence.json`
- `qa/public-founder-approval-evidence.json`
- `qa/public-address-ceremony-evidence.json`
- `qa/public-mainnet-technical-readiness-evidence.json`
- `qa/public-mainnet-deployment-authorization-evidence.json`
- `qa/public-ethereum-mainnet-authorization-evidence.json`

## Handoff sequence

1. Generate private templates: `python scripts/private/generate-private-operator-template.py`.
2. Copy example files inside `.private/` and fill real values locally.
3. Validate private inputs locally.
4. Run private Sepolia rehearsal and private mainnet read-only preflight.
5. Generate founder approval and address ceremony commitments.
6. Generate redacted public evidence files under `qa/`.
7. Commit only the redacted `qa/public-*.json` outputs.
8. Run the public checkers with `--with-redacted-private-evidence`.
9. If authorization is `YES`, deployment still requires local founder/deployer execution of the gated deployment command.

No raw private approvals, addresses, RPC URLs, keys, wallet metadata, or private ceremony details are required in GitHub.

The committed private-operator scripts validate that private input paths resolve under `.private/` before reading local inputs. They print only status lines and redacted commitment locations, not sensitive values.
