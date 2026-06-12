# Runtime Address Policy

The public repository authorizes the deployment package. The actual deployer provides runtime addresses at deployment time. Runtime addresses are validated by deployment scripts but not committed to GitHub.

Allowed modes: `SINGLE_DEPLOYER_INITIAL_ADMIN_MODE=true` with high-visibility warning and post-deployment transfer runbook; `RUNTIME_ADDRESS_PROMPT_MODE`; and `MULTISIG_RUNTIME_MODE` (recommended). Public authorization YES does not require public private addresses.
