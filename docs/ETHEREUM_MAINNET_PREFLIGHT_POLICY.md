# Ethereum Mainnet Preflight Policy

The Ethereum Mainnet preflight is read-only and public-CI safe. If no runtime RPC is supplied, it must report `MAINNET_PREFLIGHT: PUBLIC_AUTHORIZATION_MODE_NO_RUNTIME_RPC` and rely on public AGIALPHA token verification, local deterministic rehearsal, mainnet-shaped simulation evidence, and gated deployment script guardrails.

When a runtime Ethereum Mainnet RPC is supplied locally, the preflight verifies chainId `1`, the canonical AGIALPHA token address `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`, token code, ERC-20 metadata where available, no MockAGIALPHA path, no new AGIALPHA deployment path, Ethereum-mainnet manifest shape, automated/internal launch gates, and the generated Mainnet Authorization Certificate.

The preflight does not broadcast transactions, does not require GitHub secrets, and does not make an external-audit, legal, tax, guaranteed-security, investment, yield, or deployment claim.
