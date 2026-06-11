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
EXTERNAL_AUDIT_CLOSURE
FOUNDER_APPROVAL
```

## Mainnet preflight additions

v4.3 requires:

```text
TREASURY_REVIEW_HASH
AGIALPHA_TOKEN_VERIFICATION_HASH
```

## Result

v4.3 is cleaner for an external auditor because every active launch gate now matches the Ethereum AGIALPHA deployment path.
