# Token Integration Risk Review

AGIALPHA is treated as an existing utility coordination token. Ethereum Mainnet must use exactly `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`; this repository must not deploy or mint a new mainnet AGIALPHA. Sepolia/local rehearsals may use MockAGIALPHA. Vault funding is separate from deployment, and token-moving functions use checked transfer paths.
