# Runtime Address Policy

Public authorization YES does not require public founder/admin/treasury/security/community addresses. Actual deployment requires one runtime mode.

## SINGLE_DEPLOYER_INITIAL_ADMIN_MODE

The deployer becomes initial owner/admin/treasury/pause guardian, emits a warning, and must follow post-deployment transfer runbook. Requires `SINGLE_DEPLOYER_INITIAL_ADMIN_MODE=true`.

## RUNTIME_ADDRESS_PROMPT_MODE

The deploy script prompts locally for runtime addresses. Values are validated and are not stored in GitHub.

## MULTISIG_RUNTIME_MODE

Recommended production mode. The deploy script prompts locally for multisig addresses. No addresses are required before public authorization.


## Ownership handoff

GoalOS deployments require ERC-173 ownership handoff before being considered operationally complete. See `docs/OWNERSHIP_HANDOFF_RUNBOOK.md` and use `npm run ownership:sepolia:doctor|plan|dry-run|transfer|verify|evidence` or `npm run ownership:mainnet:doctor|plan|fork-rehearsal|transfer-local-gated|verify|evidence`. Mainnet single-deployer permanent-address mode is blocked.
