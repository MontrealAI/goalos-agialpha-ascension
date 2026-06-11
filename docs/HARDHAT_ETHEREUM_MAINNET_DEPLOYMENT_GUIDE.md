# Hardhat Ethereum Mainnet Deployment Guide

This repository uses Hardhat 2 with custom scripts for Ethereum Mainnet. Public CI can load `hardhat.config.ts` without RPC URLs or private keys.

Networks:

- `ethereumSepolia`: chainId `11155111`, private RPC/key loaded locally only.
- `ethereumMainnet`: chainId `1`, private RPC/key loaded locally only.
- `hardhat` and `localhost`: public-safe local use.

Final deployment is blocked unless the canonical AGIALPHA token equals `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`, the token has code on chainId 1, redacted authorization is YES, private authorization is YES, all commitment hashes are nonzero, and the local operator types `DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET`.
