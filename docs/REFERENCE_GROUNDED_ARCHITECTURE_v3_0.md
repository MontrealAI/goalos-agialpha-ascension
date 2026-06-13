> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Reference-Grounded Architecture v3.0

## GoalOS source doctrine

GoalOS AEP-001 defines the institutional law:

- Aim -> Act -> Prove -> Evolve
- Commit -> Execute -> Prove -> Evolve
- Do not put intelligence on-chain; put proof of intelligence on-chain
- No proof, no evolution; no eval, no propagation; no rollback, no release

The v3 implementation maps this to deployable contracts:

| AEP object | Contract |
|---|---|
| GoalOSCommit | AEPGoalOSCommitRegistry |
| RunCommitment | AEPRunCommitmentRegistry |
| ProofPacket / ProofRoot | AEPProofLedger |
| EvalAttestation | AEPEvalRegistry |
| Attestation | AEPAttestationRegistry |
| Proof-Carrying Artifact | AEPArtifactRegistry |
| SelectionCertificate | AEPSelectionGate |
| RolloutReceipt | AEPRolloutRouter |
| RollbackReceipt | AEPRollbackRegistry |
| Evidence Docket | AEPEvidenceDocketRegistry |

## AGI ALPHA source doctrine

AGI ALPHA defines the organizational substrate:

- agents
- jobs
- validators
- proof bundles
- alpha-Work Units
- AGI.Eth / ASI.Eth naming
- request -> escrow -> execute -> proof -> validate -> settle -> chronicle
- no ProofBundle, no settlement
- no replay, no settlement
- no authority, no autonomy

The v3 implementation maps this to:

| AGI ALPHA object | Contract |
|---|---|
| ProofBundle | AEPProofBundleRegistry |
| alpha-Work Unit | AlphaWorkUnitLedger |
| MandateEpoch | MandateEpochRegistry |
| AGI.Eth namespace | AGIEthNamespaceRegistry |
| legacy AGIJobManager reference | LegacyAGIJobManagerRegistry |
| proof job market | JobRegistry + ClaimBond + ProofSubmission + ReviewerBond |
| proof card | ProofCardRegistry |
| credential | ProofCredentialRegistry |
| reputation | ReputationRegistry |

## Blockchain boundary

On-chain:

- hashes
- attestations
- public-safe proof metadata
- commitments
- proof roots
- credentials
- reputation roots
- settlement references
- rollback receipts
- gate hashes

Off-chain:

- model inference
- private prompts
- private traces
- customer data
- enterprise documents
- evaluator workpapers
- confidential business logic

## Final architecture

```text
GoalOSCommit
-> RunCommitment
-> ProofBundle / ProofRoot
-> EvalAttestation
-> SelectionCertificate
-> RolloutReceipt
-> Evidence Docket
-> Credential / Reputation / Alpha-WU
-> MandateEpoch / Proof Graph
```
