# Private Founder Approval Runbook

Founder approval is local-custody evidence. GitHub does not require the founder address, raw approval signature, or private approval artifact.

Generate the message locally:

```bash
python scripts/private/generate-founder-approval-message.py --input .private/mainnet-operator-input.json
```

Verify or attest locally:

```bash
python scripts/private/verify-founder-approval-private.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

Public output records only `founderApprovalCommitmentHash`, `founderApprovalVerified`, `founderApprovalHeldPrivately`, `containsFounderAddress: false`, `containsSignature: false`, and the verification mode. If the founder declines local signature verification, the mode is `private-custody-attestation`; that is not represented as public signature verification.
