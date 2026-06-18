# Proof Treasury Simulation 003

## External Replay Market & Capacity Auction

Proof Treasury Simulation 003 is a simulation-only proof of how $AGIALPHA can act as a proof-conditioned economic control rail after proof exists.

It extends the previous simulations:

```text
Simulation 001: proof gates settlement.
Simulation 002: replay gates reinvestment.
Simulation 003: external replay gates capacity scale.
```

## Core law

```text
No proof -> no settlement.
No replay -> no settlement for high-impact work.
No external replay -> no capacity scale.
No governance -> no acceleration.
Claim-boundary failure overrides all scores.
```

## Outputs

The workflow generates:

```text
TreasurySimulationManifest.json
AGIALPHABudgetLedger.csv
SettlementTable.csv
AlphaWorkUnitLedger.csv
ExternalReplayLedger.csv
ValidatorMarketLedger.csv
ValidatorSlashingLedger.csv
CapacityAuctionAllocations.csv
ProofDebtLedger.csv
ContractCallTrace.csv
ThermostatSignals.json
ReinvestmentDecision.json
NoTokenMovementCertificate.md
ClaimBoundaryReport.md
QAReport.md
ProofTreasuryEvidenceDocket.md
ChronicleEntry.md
run-state.json
index.html
```

## Why this matters

This simulation makes $AGIALPHA useful beyond payout accounting. It models $AGIALPHA as a capacity rail: proof can release simulated settlement, external replay can unlock capacity allocation, validator dishonesty can be penalized, and only replay-cleared work can influence the next mission budget.

## Contract-call surface simulated

```text
AGIALPHA.approve(ProofTreasuryVault,totalBudget)
ProofTreasuryVault.fundEpoch(epochId,totalBudget,policyRoot)
MandateEpochRegistry.openEpoch(mandateHash,epochPolicyHash,budgetRoot)
ExternalReplayMarket.openReplayRound(epochId,replayPolicyRoot)
JobRegistry.postJob(missionHash,reward,evidenceURI,deadline,riskClass)
JobClaimBondManager.claimJob(jobId,claimBond,proofBond)
ProofSubmissionRegistry.submitProof(jobId,proofBundleHash,docketURI,alphaWUEstimate)
ExternalReplayMarket.submitReplayAttestation(jobId,replayVerdict,replayHash)
JobRegistry.releaseReward(jobId,builder)
AlphaWorkUnitLedger.recordAlphaWorkUnits(jobId,alphaWU,proofRoot)
TreasuryRouter.allocateCapacity(epochId,capacityAuctionRoot)
AEPChronicleRegistry.recordEntry(epochId,chronicleHash)
```

These are protocol-level templates, not live on-chain calls. Exact deployed addresses, ABIs, role permissions, chain IDs, and production gates must be confirmed before Sepolia or Mainnet use.
