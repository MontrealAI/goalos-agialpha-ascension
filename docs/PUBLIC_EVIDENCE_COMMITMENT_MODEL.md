# Public Evidence Commitment Model

Public redacted evidence files must contain:

- `redacted: true`
- `containsSecrets: false`
- `containsPrivateAddresses: false`
- chain target and AGIALPHA token address
- commit SHA
- pass/fail fields
- SHA-256 commitments to private evidence files
- blockers, if any
- generated timestamp

They must not contain raw RPC URLs, private keys, private addresses, raw founder signatures, wallet metadata, private operator notes, or private evidence appendices.
