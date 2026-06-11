# AGIALPHA Token Integration

## Mainnet token

AGIALPHA is already deployed at:

```text
0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA
```

The deployment script refuses Ethereum mainnet deployment if `AGIALPHA_TOKEN_ADDRESS` does not exactly match this address.

## No token deployment on mainnet

This package does not deploy a new AGIALPHA token on Ethereum mainnet.

For Sepolia rehearsal only, a `MockAGIALPHA` token can be deployed if no AGIALPHA address is supplied.

## Utility

AGIALPHA is used for:

- Proof Seed fees
- Sponsor posting
- Builder claim bonds
- Proof submission bonds
- Reviewer bonds
- Credential/proof-card action fees
- Premium access conditions
- Referral attribution
- Commercialization performance vaults


## v3.0 AEP additions

AGIALPHA also coordinates GoalOS AEP-001 commitments and MandateEpoch proof-work accounting through AEPGoalOSCommitRegistry, MandateEpochRegistry, AEPProofBundleRegistry, and AlphaWorkUnitLedger.
