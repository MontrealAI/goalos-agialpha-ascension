# Protected Mainnet Readiness Runbook

This runbook is for Phase B only. Phase A never reads protected inputs.

1. Configure the GitHub environment `mainnet-readiness`.
2. Add only fork-rehearsal inputs: `MAINNET_FORK_RPC_URL`, `GOALOS_PRODUCTION_OWNER_KIND`, `GOALOS_PRODUCTION_OWNER_ADDRESS`, `GOALOS_PRODUCTION_OWNER_CONFIG_B64`, and `FORK_AGIALPHA_FUNDER`.
3. Do not add a Mainnet broadcaster private key to the workflow.
4. Run the manual workflow `.github/workflows/mainnet-readiness.yml` or locally run `npm run mainnet:fork-rehearsal:release && npm run mainnet:final-check` after `npm run codex:phase-a`.
5. Keep public status at `MAINNET_DEPLOYED = NO` and `MAINNET_VERIFIED = NO` until real chain-1 broadcast and verification evidence exists.
