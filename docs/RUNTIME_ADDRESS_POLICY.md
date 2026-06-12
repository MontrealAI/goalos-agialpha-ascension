# Runtime Address Policy

Public authorization YES does not require public founder/admin/treasury/security/community addresses. Actual deployment requires one runtime mode.

## SINGLE_DEPLOYER_INITIAL_ADMIN_MODE

The deployer becomes initial owner/admin/treasury/pause guardian, emits a warning, and must follow post-deployment transfer runbook. Requires `SINGLE_DEPLOYER_INITIAL_ADMIN_MODE=true`.

## RUNTIME_ADDRESS_PROMPT_MODE

The deploy script prompts locally for runtime addresses. Values are validated and are not stored in GitHub.

## MULTISIG_RUNTIME_MODE

Recommended production mode. The deploy script prompts locally for multisig addresses. No addresses are required before public authorization.
