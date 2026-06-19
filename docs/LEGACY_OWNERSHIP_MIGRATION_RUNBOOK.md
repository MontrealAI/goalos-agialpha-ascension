# Legacy ownership migration runbook

This path is for Sepolia rehearsals or pre-existing deployments where a disposable account is already owner/admin. It is not the fresh Mainnet architecture.

Run `npm run ownership:sepolia:legacy-plan`, inspect every managed manifest entry and expected owner, initiate transfers with `npm run ownership:sepolia:legacy-initiate`, wait the configured delay, prepare Safe or Ledger acceptance with `npm run ownership:sepolia:legacy-accept-prepare`, then run `npm run ownership:sepolia:legacy-verify` and `npm run ownership:sepolia:legacy-evidence`.

Partial migration is expected to be visible and is not success. Pause protocol operations where safe, do not start new deployments while ownership is split, preserve contract-to-contract roles, and stop on unexpected owner, pending owner, role member, codehash, manifest hash, or chain disagreement.
