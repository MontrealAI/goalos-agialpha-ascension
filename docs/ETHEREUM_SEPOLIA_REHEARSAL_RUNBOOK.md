# Ethereum Sepolia Rehearsal Runbook

1. Set Sepolia broadcast RPC and private key in the operator environment only; never commit secrets.
2. Set `ETHEREUM_SEPOLIA_PUBLIC_VERIFICATION_RPC_URL` to an independent public Sepolia RPC so the evidence generator can verify every rehearsal transaction receipt outside the broadcast endpoint. Without this verification RPC, public Sepolia readiness remains pending.
3. Optionally set a Sepolia AGIALPHA token address. If absent, the script deploys `MockAGIALPHA` on Sepolia/local rehearsal only.
4. Run `npm run compile`.
5. Run `npm run sepolia:rehearsal`.
6. Run `npm run sepolia:evidence`.
7. Review `deployments/ethereum-sepolia.agialpha.latest.json` and `evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json`.
8. Confirm `allCoreGatesPassed()` remains false unless all other real gates exist.
