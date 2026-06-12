# Branch Protection Next Action

Main branch protection/ruleset enforcement is public-risk accepted for v4.4.0 authorization. Before actual Ethereum Mainnet deployment, the repository owner should enable operational hardening:

- PR required before merge.
- Required status checks.
- No force push.
- No deletion.
- Conversation resolution.
- CODEOWNER review for sensitive paths.

This is operational hardening. It does not mean CI can deploy Ethereum Mainnet, and it does not change the Ethereum Mainnet deployed status.

Current public authorization remains certificate-backed manual, local, gated deployment authorization only. Ethereum Mainnet deployed remains **NO** until real chainId 1 transaction evidence exists.
