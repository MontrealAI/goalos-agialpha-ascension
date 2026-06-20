# Ownership handoff runbook

Use `npm run deploy:handoff -- --manifest <path>`. Operational completion is blocked until final Owner readback, pending Owner clearance, expected roles, deployer-role removal, and treasury/controller/operator configuration are evidenced.

Use `ownership:mainnet:accept-local-gated` for delayed Mainnet acceptance. Wait until pendingOwnerAcceptAfter before trying to accept delayed ownership.
