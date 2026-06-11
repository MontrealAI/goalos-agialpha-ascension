# GoalOS AGIALPHA Ascension v4.2 — Evidence-Ready Audit Candidate

This is the closest safe package to a 10/10 **given the current state**.

It is designed for:

```text
engineering handoff
local compile/test
Sepolia rehearsal
Evidence Docket production
automated security/toolchain and internal security review
mainnet gate review
```

It is **not** mainnet authorized.

## Correct status

```text
Evidence-ready institutional audit candidate: yes.
Uses existing AGIALPHA on Ethereum mainnet: yes.
Sepolia rehearsal path: yes.
Mainnet deployment script: gated.
Not externally audited.
Automated security/toolchain review: pending.
Ethereum Mainnet not authorized.
Legally approved: no.
Tax reviewed: no.
Security reviewed: no.
Guaranteed non-security: no.
```

## Fast path

```bash
npm install
cp .env.example .env
npm run compile
npm test
npm run test:all
npm run static-check
npm run readiness:v4.2
npm run evidence:docket:template
npm run deploy:ethereum-sepolia
```

If the compiler download is blocked:

```bash
npm run direct-solc-compile
npm run generate-artifacts-from-solc
npm run test:no-compile
npm run readiness:v4.2
```

## What makes v4.2 stronger than v4.1

```text
Evidence Docket template generator
mainnet authorization checker
expanded readiness verifier
no-secret static scan
Sepolia proof-loop evidence checklist
automated security/toolchain clearance request
governance role ceremony checklist
public claims review checklist
mainnet NOT AUTHORIZED decision memo
CODEX / auditor remediation prompt
```

## 10/10 rule

The package becomes a true 10/10 only after evidence exists:

```text
compile passes
all tests pass
Sepolia deploys
proof-work loop completes
Evidence Docket is filled
automated security/toolchain clearance and internal security review are complete
legal/tax/security/claims gates are complete
founder approval is signed
```

Until then, use this line:

```text
v4.2 is evidence-ready. Mainnet is still no.
```
