# Private Founder Approval Runbook

Founder approval may remain in private custody. The public repository stores only a founder approval commitment hash and mode.

If a signature is verified locally, public output may say `founderApprovalVerified: true` without publishing the signer address or signature. If local signature verification is not used, public output must say `founderApprovalVerificationMode: private-custody-attestation`.
