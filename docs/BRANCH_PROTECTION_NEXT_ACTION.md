# Branch Protection Next Action

Main branch protection/ruleset enforcement is **public-risk accepted** for the v4.4.0 authorization package. The public repository remains certificate-backed and authorized for manual, local, gated Ethereum Mainnet deployment, but branch protection should be hardened before any actual broadcast.

Before actual Ethereum Mainnet deployment, the repository owner should enable:

- PR required before merge.
- Required status checks.
- No force push.
- No deletion.
- Conversation resolution.
- CODEOWNER review for sensitive paths.

This is operational hardening. It does not mean CI can deploy mainnet, does not store runtime RPC/key material in GitHub, and does not change `MAINNET_DEPLOYED: NO`.
