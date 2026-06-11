# v4.3 Gate-Clean Delta

v4.2 moved the package closer to 10/10 by adding the evidence-production layer.

v4.3 fixes the remaining gate-hygiene issue found during inspection.

## Problem found in v4.2

`LaunchGateRegistry` still used:

```text
BASE_SEPOLIA_REHEARSAL
```

But this package is Ethereum Mainnet / Ethereum Sepolia only.

## Fix

v4.3 replaces it with:

```text
ETHEREUM_SEPOLIA_REHEARSAL
```

and adds:

```text
AGIALPHA_TOKEN_VERIFICATION
AUTOMATED_SECURITY_TOOLCHAIN
INTERNAL_SECURITY_REVIEW
FOUNDER_APPROVAL
```

## Mainnet preflight additions

v4.3 requires:

```text
TREASURY_REVIEW_HASH
AGIALPHA_TOKEN_VERIFICATION_HASH
```

## Result

v4.4 supersedes the historical external-audit gate with automated security/toolchain and internal security-review gates while preserving Ethereum AGIALPHA launch discipline.
