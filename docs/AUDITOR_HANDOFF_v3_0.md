> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Auditor Handoff v3.0

## Audit scope

Audit the complete v3.0 package with special attention to:

- use of existing AGIALPHA token
- no new AGIALPHA deployment on mainnet
- mainnet gate enforcement
- AGIALPHA fee/bond flows
- rejected proof refund flows
- expired claimed job reclaim flows
- reviewer cooldown/challenge windows
- AEP proof-of-evolution registries
- MandateEpoch batching and roots
- alpha-Work Unit accounting
- Evidence Docket public/private boundary
- admin/operator roles
- vault funding separation
- pause controls

## Priority contracts

- AEPGoalOSCommitRegistry
- AEPRunCommitmentRegistry
- AEPProofLedger
- AEPEvalRegistry
- AEPSelectionGate
- AEPRolloutRouter
- AEPRollbackRegistry
- AEPEvidenceDocketRegistry
- AEPProofBundleRegistry
- AlphaWorkUnitLedger
- MandateEpochRegistry
- ProofSubmissionRegistry
- JobRegistry
- ReviewerBondRegistry
- CommercializationPerformanceVault

## Required output

- findings
- remediation status
- residual risks
- mainnet recommendation
- deployment checklist
- role/governance checklist
