# GoalOS AGIALPHA Ascension v4.3 — Gate-Clean Evidence-Ready Audit Candidate

v4.3 is the corrected package to hand to engineers and internal security/toolchain reviewers.

## What v4.3 fixes

- Replaces stale `BASE_SEPOLIA_REHEARSAL` launch gate with `ETHEREUM_SEPOLIA_REHEARSAL`.
- Adds `AGIALPHA_TOKEN_VERIFICATION` as a launch gate.
- Historical note: v4.3 previously referenced `EXTERNAL_AUDIT_CLOSURE`; v4.4 replaces that requirement with `AUTOMATED_SECURITY_TOOLCHAIN` and `INTERNAL_SECURITY_REVIEW`.
- Adds `FOUNDER_APPROVAL` as a launch gate.
- Requires `TREASURY_REVIEW_HASH` in mainnet gate checks.
- Requires `AGIALPHA_TOKEN_VERIFICATION_HASH` in mainnet gate checks.
- Updates deployment package labels to v4.3.
- Keeps v4.2 Evidence Docket generation, readiness verification, and mainnet authorization blocking.

## Correct status

```text
Evidence-ready institutional audit candidate: yes.
Gate-clean Ethereum launch hygiene: yes.
Uses existing AGIALPHA on Ethereum mainnet: yes.
Deploys new AGIALPHA token: no.
Mints AGIALPHA: no.
Not externally audited.
Automated security/toolchain review: pending.
Ethereum Mainnet not authorized.
```

## Mainnet remains blocked

Mainnet is not authorized until compile/tests, Ethereum Sepolia rehearsal, Evidence Docket, automated security/toolchain clearance, internal security review, legal, tax, public-claims, treasury, AGIALPHA token verification, and founder approval gates are complete.
