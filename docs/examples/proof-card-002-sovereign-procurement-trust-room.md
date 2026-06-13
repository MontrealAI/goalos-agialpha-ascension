# Proof Card 002 - Sovereign Procurement Trust Room

**Status:** public-safe illustrative use case. Not a live customer result until an Evidence Docket is filled with real transaction hashes and reviewer attestations.

## One-line story

A sponsor needs to trust an AI workflow vendor; GoalOS converts the procurement, security, compliance, and implementation evidence into a proof-backed Trust Room, coordinated with AGIALPHA and improved through RSI.

## Why this matters

A government, hospital network, bank, infrastructure company, or enterprise buyer must evaluate AI workflow adoption across security, privacy, procurement, vendor risk, finance, operations, and governance. The process is slow, fragmented, and difficult to trust.

GoalOS decomposes the procurement obstacle into bounded proof missions. Builders create evidence artifacts. Reviewers validate them. AGIALPHA coordinates mission posting, bonds, review, credentialing, and reputation. The approved artifacts become a reusable Trust Room that improves future procurement cycles.

## How AGIALPHA is used

AGIALPHA coordinates the proof-work network around the mission:

- sponsor reward escrow;
- builder claim bond;
- proof submission bond;
- reviewer bond;
- proof-card registry action;
- credential action;
- reward settlement;
- reputation-linked future routing.

## Smart-contract flow

| Step | Contract / registry | Purpose |
|---|---|---|
| 1 | `AEPGoalOSCommitRegistry` | Creates the signed institutional commitment: objective, constraints, success metrics, risk class, allowed evidence, and rollback expectation. |
| 2 | `AEPRunCommitmentRegistry` | Commits the run plan: work packages, builders, reviewers, artifacts, tools, deadlines, and evidence roots. |
| 3 | `JobRegistry` | Posts the proof mission with AGIALPHA reward and public-safe mission metadata. |
| 4 | `JobClaimBondManager` | Builder claims the mission with an AGIALPHA bond. |
| 5 | `ProofSubmissionRegistry` | Builder submits proof hashes, public-safe proof note, evidence docket root, and proof-card candidate. |
| 6 | `ReviewerBondRegistry` | Reviewer bonds AGIALPHA and validates or rejects the proof under a rubric. |
| 7 | `ProofCardRegistry` | Registers the approved public Proof Card hash and URI. |
| 8 | `ProofCredentialRegistry` | Issues a non-transferable credential to the builder and optionally reviewer. |
| 9 | `ReputationRegistry` | Updates reputation based on approved proof, review quality, and challenge history. |
| 10 | `AEPEvidenceDocketRegistry` | Registers the Evidence Docket root and public/private proof boundary. |
| 11 | `AEPSelectionGate` | Issues a Selection Certificate for artifacts that may influence future work. |
| 12 | `AEPChronicleRegistry` | Records the accepted artifacts, credentials, reputation, and upgrade lineage. |


## RSI: proof-backed upgrade rights

An improvement is not allowed to shape future work merely because it exists. It must pass evidence, evaluation, reviewer validation, scope control, challenge window, rollout readiness, monitoring, and rollback readiness.

| RSI phase | Meaning |
|---|---|
| Observe | Procurement cycles repeatedly stall on the same evidence gaps: security questionnaire, privacy proof, support workflow, claim boundary, rollback plan. |
| Improve | Builders create reusable artifacts: Trust Room index, evidence checklist, answer library, security claim map, RFP response templates, review rubric. |
| Prove | Reviewer validates before/after evidence, checks public claims, confirms private evidence boundaries, and signs an attestation. |
| Select | Selection Gate promotes only artifacts that are evidence-backed, scope-limited, reversible, and useful for future runs. |
| Propagate | Future procurement missions route through the accepted artifacts, reducing duplicated work and improving consistency. |
| Rollback | If evidence becomes stale, challenged, or unsafe, the artifact is paused, replaced, or rolled back with a visible receipt. |


## Public claim boundary

This Proof Card is a high-value usage example and demand engine for the first live Evidence Docket; it is not a live customer result or deployment authorization. It is a high-value usage example and demand engine for the first live Evidence Docket.
