# Ethereum Mainnet Preflight Policy

Public CI may run deterministic mainnet-shaped simulation without private RPC. If runtime MAINNET_RPC_URL is available locally, preflight verifies chainId 1, canonical AGIALPHA code, no MockAGIALPHA, no new AGIALPHA deployment, constructor/role/gate checks, and manifest target. No CI mainnet broadcast is permitted.
