> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# AGIALPHA Utility Mapping v3.0

AGIALPHA replaces JOBS in the same utility coordination role.

| JOBS utility | AGIALPHA implementation |
|---|---|
| Sponsor posting | JobRegistry posting fee and reward token path. |
| Builder job claiming | JobClaimBondManager claim bond. |
| Proof submission bonds | ProofSubmissionRegistry proof bond. |
| Reviewer bonds | ReviewerBondRegistry reviewer bond. |
| Credential minting | ProofSubmissionRegistry action fees + ProofCredentialRegistry. |
| Proof-card registry actions | ProofCardRegistry via approved submission. |
| Premium job access | PremiumAccessRegistry. |
| Referral attribution | ReferralRegistry. |
| Reputation-weighted opportunities | ReputationRegistry and PremiumAccessRegistry. |
| Commercialization performance | CommercializationPerformanceVault. |
| Proof-of-evolution commitments | AEPGoalOSCommitRegistry. |
| Proof bundles and alpha-WU | AEPProofBundleRegistry and AlphaWorkUnitLedger. |
| MandateEpoch work batching | MandateEpochRegistry. |

Boundary: AGIALPHA is used as a utility coordination asset, not as equity, yield, revenue share, or investment promise.
