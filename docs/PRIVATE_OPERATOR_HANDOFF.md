# Private Operator Handoff

Private operators keep sensitive inputs locally under `.private/` and commit only redacted public evidence commitments.

Private evidence examples:

- `.private/mainnet-operator-input.json`
- `.private/mainnet-operator.env`
- `.private/sepolia-rehearsal-private.json`
- `.private/mainnet-preflight-private.json`
- `.private/address-ceremony-private.json`
- `.private/founder-approval-private.json`
- `.private/final-deploy-private.env`

Public redacted outputs:

- `qa/public-mainnet-technical-readiness-evidence.json`
- `qa/public-mainnet-deployment-authorization-evidence.json`
- `qa/public-ethereum-mainnet-authorization-evidence.json`

The public files contain pass/fail booleans and hashes only. They must not contain private addresses, signatures, RPC URLs, keys, or raw private artifacts.
