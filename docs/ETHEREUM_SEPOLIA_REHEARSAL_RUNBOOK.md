# Ethereum Sepolia Rehearsal Runbook

1. Set Sepolia RPC and private key in the operator environment only; never commit secrets.
2. Optionally set a Sepolia AGIALPHA token address. If absent, the script deploys `MockAGIALPHA` on Sepolia/local rehearsal only.
3. Run `npm run compile`.
4. Run `npm run sepolia:rehearsal`.
5. Run `npm run sepolia:evidence`.
6. Review `deployments/ethereum-sepolia.agialpha.latest.json` and `evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json`.
7. Confirm `allCoreGatesPassed()` remains false unless all other real gates exist.
