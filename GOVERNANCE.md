# Governance

The canonical 2026-06-21 Ethereum Mainnet deployment uses genesis authority assignment, permanent authority, and postdeployment role configuration. Wallet B / Ledger is permanent authority. Wallet A has zero managed roles. No ERC-173 acceptance transaction or ownership handoff remains required for this deployment.

Legacy/future two-step ownership deployments — not required for the 2026-06-21 canonical deployment — may retain delayed-acceptance runbooks for future patterns. `DEFAULT_ADMIN_ROLE = 0x00...00` is a role identifier, not a wallet.
