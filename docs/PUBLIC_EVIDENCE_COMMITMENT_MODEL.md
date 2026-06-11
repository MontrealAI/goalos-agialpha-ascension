# Public Evidence Commitment Model

Public evidence files are redacted commitments. They make private evidence auditable without exposing private operational data.

## Required public fields

Each mainnet authorization evidence file includes:

- `redacted: true`;
- `containsSecrets: false`;
- `containsPrivateAddresses: false`;
- `chain: ethereum`;
- `chainId: 1`;
- `agialphaToken: 0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`;
- `commit`;
- `generatedAt`;
- pass/fail decision fields;
- `toolchainClearanceHash`;
- `sepoliaEvidenceDocketHash`;
- `sepoliaReceiptVerificationHash`;
- `mainnetPreflightHash`;
- `addressCeremonyCommitmentHash`;
- `founderApprovalCommitmentHash`;
- `policyDecisionCommitmentHash`;
- `blockers`.

## Public-safety prohibitions

Public redacted evidence must not include raw RPC URLs, private keys, seed phrases, founder signatures unless explicitly published by the founder, raw founder/treasury/admin/deployer/vault/security/community addresses, private evidence bodies, wallet files, private operator notes, or private deployment ceremony details.

Hashes are commitments, not public disclosure of the committed material.
