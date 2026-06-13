# Proof Card 001 - Buyer Rescue Workflow

A buyer cannot access a GoalOS product download. A first support reply is helpful but incomplete. GoalOS turns the situation into a workflow improvement mission.

The workflow improves from v1.0 to v1.1. AGIALPHA coordinates the proof mission between sponsor, builder, and reviewer. The reviewer validates evidence. A Proof Card explains the improvement without exposing private buyer data.

## AGIALPHA + smart-contract flow

| Step | Artifact | Contract / Registry action | Meaning |
|---|---|---|---|
| 1 | GoalOSCommit | `AEPGoalOSCommitRegistry.createCommit` | Sponsor records mission aim, success criteria, constraints, authority, data boundary, rollback obligation, and claim boundary. |
| 2 | RunCommitment | `AEPRunCommitmentRegistry.commitRun` | Operator records plan graph, tool permissions, context root, policy root, budget, and latency limits. |
| 3 | Sponsor mission | `JobRegistry.postJob` | Sponsor posts the support-workflow proof mission and escrows an AGIALPHA reward. |
| 4 | Builder claim | `JobClaimBondManager.claimJob` | Builder claims the mission with an AGIALPHA claim bond. |
| 5 | Proof submission | `ProofSubmissionRegistry.submitProof` | Builder submits proof hash, proof URI, proof-card hash, and proof bond. |
| 6 | Reviewer bond | `ReviewerBondRegistry.bondAsReviewer` | Reviewer bonds AGIALPHA before validating evidence. |
| 7 | Review decision | `ReviewerBondRegistry.reviewSubmission + ProofSubmissionRegistry.approveSubmission` | Reviewer validates the before/after workflow, scorecard, claim boundary, and proof note. |
| 8 | Proof Card | `ProofCardRegistry.registerProofCard` | Public-safe Proof Card is registered for the approved workflow improvement. |
| 9 | Credential | `ProofCredentialRegistry.issueCredential` | Builder receives a non-transferable proof-work credential. |
| 10 | Reputation | `ReputationRegistry.recordApprovedProof` | Builder and reviewer reputation update after approved proof. |
| 11 | Evidence Docket | `AEPEvidenceDocketRegistry.registerEvidenceDocket` | Evidence Docket anchors claims, costs, risks, public/private boundary, and proof artifacts. |
| 12 | Selection + Chronicle | `AEPSelectionGate.issueSelectionCertificate + AEPChronicleRegistry.recordEntry` | If the improvement passes the gate, it can influence future work and is recorded in institutional memory. |

AGIALPHA token used: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`.

## RSI loop

RSI means proof-backed upgrade rights. An improvement may shape future work only after it survives evidence, evaluation, reviewer validation, scope control, challenge window, rollout, monitoring, and rollback readiness.

## Claim boundary

Illustrative usage example only. A live Evidence Docket is required before claiming verified production impact.
