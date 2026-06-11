# GoalOS AGIALPHA Ascension v4.3 — Gate-Clean Evidence-Ready Audit Candidate

v4.3 is the corrected package to hand to engineers and auditors.

## What v4.3 fixes

- Replaces stale `BASE_SEPOLIA_REHEARSAL` launch gate with `ETHEREUM_SEPOLIA_REHEARSAL`.
- Adds `AGIALPHA_TOKEN_VERIFICATION` as a launch gate.
- Adds `EXTERNAL_AUDIT_CLOSURE` as a launch gate.
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
Audited: no.
Mainnet authorized: no.
```

## Mainnet remains blocked

Mainnet is not authorized until compile/tests, Ethereum Sepolia rehearsal, Evidence Docket, external audit closure, legal, tax, public-claims, treasury, AGIALPHA token verification, and founder approval gates are complete.
