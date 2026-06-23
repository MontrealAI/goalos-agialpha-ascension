# Mainnet activation nontechnical runbook

This package stops at the physical Wallet-B Ledger boundary. Codex, CI, and cloud runners must not send Mainnet transactions.

## Ubuntu or macOS

1. Use a trusted local computer with the repository checked out.
2. Copy `.private/mainnet-activation/operator.env.example` to a private local operator file and fill only read-only RPC/Etherscan values and the public Ledger account address.
3. Connect the physical Ledger for Wallet B: `0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99`.
4. Run the exact command printed by `npm run mainnet:activation:prepare-local`.
5. Review every displayed action and plan hash before approving anything on the Ledger.
6. Type `ACTIVATE_CONTROLLED_PRODUCTION_CANARY_V1` only if the displayed plan hash matches.

Never type, paste, export, photograph, or store a Ledger recovery phrase or raw private key.
