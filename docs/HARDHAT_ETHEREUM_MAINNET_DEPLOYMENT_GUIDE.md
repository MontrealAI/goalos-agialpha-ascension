# Hardhat Ethereum Mainnet Deployment Guide

Public CI can load Hardhat config without RPC/private keys. Final deployment is manual/local only:

```bash
MAINNET_TARGET=ethereum AGIALPHA_TOKEN_ADDRESS=0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA npm run deploy:ethereum-mainnet:gated
```

The script requires chainId 1, exact AGIALPHA token, no MockAGIALPHA, no new AGIALPHA token, certificate YES, toolchain/rehearsal/token evidence, non-CI execution, runtime RPC/key, and typed confirmation `DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET`.
