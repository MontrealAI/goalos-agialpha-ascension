# Ownership Handoff Runbook

## Current 2026-06-21 Ethereum Mainnet deployment

The configured GoalOS Ethereum Mainnet deployment uses **genesis authority assignment**: Wallet B / Ledger (`0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99`) is the permanent authority where ownership is exposed from construction. Wallet A managed roles: 0.

No ownership acceptance transaction is required for this deployed instance.

Production activated: NO. User funds are not authorized.

## Legacy compatibility only

`ownership:mainnet:accept-local-gated` remains a legacy compatibility command for future or historical two-step ownership-transfer flows that have a pending owner and an approved acceptance plan.

Legacy compatibility only — not required for the 2026-06-21 GoalOS deployment.

Do not run ownership acceptance from CI. Do not run ownership acceptance unless a separate live readback proves a pending owner and the reviewed plan explicitly requires acceptance.
