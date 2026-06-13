> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Season 001 MandateEpoch Playbook v3.0

## Objective

Launch GoalOS AGI Ascension as proof-of-workflow missions without token hype.

## First five missions

1. Customer Support Workflow.
2. Claims-Safe Launch Content.
3. Repository Documentation QA.
4. Sponsor Proof Job Creation.
5. Builder / Reviewer Quality.

## Standard evidence chain

```text
GoalOSCommit
-> RunCommitment
-> ProofBundle
-> EvalAttestation
-> SelectionCertificate
-> Evidence Docket
-> Proof Card
-> Credential
-> Reputation
-> alpha-WU
```

## MandateEpoch pattern

One MandateEpoch can batch many off-chain microtasks while committing roots on-chain:

- mandateHash
- policyHash
- scoringRubricHash
- safetyPolicyHash
- receiptRoot
- payoutRoot
- archiveDeltaRoot
- quarantineRoot
- validatorAttestationBundleHash

This follows the rule: do not put every microjob on-chain; put settlement-grade roots on-chain.

## Proof Card 001

Recommended first mission: Customer Support Workflow.

Deliverables:

- workflow v1.0
- test inputs
- scorecard
- diagnosis
- workflow v1.1
- evaluation comparison
- proof note
- reviewer decision
- public-safe proof card
- credential issuance
