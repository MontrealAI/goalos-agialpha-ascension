# Private Inputs Required But Not Committed

The following inputs may be required for private operations but must remain local-only and gitignored:

- Sepolia RPC URL and deployer private key;
- Ethereum Mainnet RPC URL;
- optional Etherscan API key;
- founder approval signature and message;
- founder, deployer, treasury, admin, vault, security, and community addresses;
- address ceremony details;
- wallet metadata;
- private evidence appendices;
- final deployment environment and operator notes.

Use `.private/` for local custody. Public GitHub stores only hashes and redacted commitments generated from those local artifacts.
