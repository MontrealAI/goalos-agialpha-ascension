# GoalOS Mission OS Operator Runbook

## Run the default mission

```bash
npm install
npm run mission-os:run
npm run mission-os:claim-boundary -- --dir evidence/mission-os/ai-product-intelligence-001
npm run mission-os:done-check -- --dir evidence/mission-os/ai-product-intelligence-001
npm run mission-os:qa
```

## Review outputs
1. Open `EvidenceDocket.md`.
2. Open `ClaimsMatrix.csv`.
3. Open `SourceProvenance.csv`.
4. Open `RiskLedger.csv`.
5. Open `DecisionState.json`.
6. Open `ActionGraph.md`.
7. Confirm `ClaimBoundaryReport.md` and `QAReport.md` pass.

## Safety reminder
Mission OS does not auto-merge, broadcast Mainnet transactions, request deployer keys, request Mainnet RPC secrets, or move tokens.
