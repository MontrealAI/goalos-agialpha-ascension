# Private Inputs Required But Not Committed

The following are local-only inputs and must not be placed in GitHub, workflow secrets, PR comments, logs, artifacts, or public docs:

- Sepolia/Mainnet RPC URLs
- deployer private keys
- Etherscan API keys
- founder approval signatures/artifacts
- founder, treasury, deployer, admin, vault, security, and community addresses
- private ceremony details, wallet metadata, operator notes, and private evidence appendices

Use `python scripts/private/generate-private-operator-template.py` to create local placeholder templates under `.private/`.
