# Institutional Handoff v2.0

## Decision

Use v2.0, not v1.0, for engineering/audit handoff.

## Why v2.0 is better

- Verifies the existing AGIALPHA token address on Ethereum mainnet.
- Does not deploy a new AGIALPHA token on mainnet.
- Adds deployment verification.
- Adds vault funding instructions.
- Adds gated vault funding script.
- Adds clearer treasury/funding separation.
- Fixes the direct solc artifact script mismatch.
- Adds chain-time-safe tests.

## Current status

Complete implementation package: yes.
Ethereum Sepolia rehearsal-ready after compile/tests pass: yes.
Ethereum Mainnet authorization: no.
