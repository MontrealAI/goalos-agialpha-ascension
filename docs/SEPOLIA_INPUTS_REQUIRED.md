# Sepolia Inputs Required

Public Ethereum Sepolia rehearsal cannot be upgraded from local-only evidence to public evidence until these inputs are supplied securely:

- `SEPOLIA_RPC_URL`
- `SEPOLIA_RPC_URL_SECONDARY` when available
- `SEPOLIA_DEPLOYER_PRIVATE_KEY`
- `ETHERSCAN_API_KEY` if source verification is used

No secrets may be committed. Until public receipts and independent verification exist, `TECHNICALLY_MAINNET_READY` must remain NO.
