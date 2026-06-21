# Sepolia-backed initial Mainnet profile

Active limited-launch profile: `SEPOLIA_BACKED_INITIAL_MAINNET_V1`.

This profile accepts the historical Ethereum Sepolia deployment as sufficient public-chain evidence for an initial Mainnet infrastructure deployment only. It does **not** claim full production readiness, full Mainnet-fork assurance, user-funds authorization, public reliance, frontend activation, settlement, or protocol activation.

Accepted historical Sepolia facts:

- chain ID `11155111`;
- 49 deployed/verified entries;
- 49 Etherscan V2 verified and 0 failed;
- 63 recorded deployment/configuration transactions;
- Solidity `0.8.35`;
- `MockAGIALPHA` was used;
- one historical address served as deployer, Owner, operations, founder, and treasury.

Known limitations that must remain visible:

- historical Sepolia bytecode is not current-release bytecode parity;
- historical Sepolia `MockAGIALPHA` is not canonical Mainnet AGIALPHA;
- historical Sepolia authority model is not the Wallet-A/Wallet-B Mainnet authority model;
- Stage B chain-1 receipt, bytecode, verification, and authority readback remains mandatory immediately after broadcast.

Required public status language:

```text
Stage-A profile: SEPOLIA_BACKED_INITIAL_MAINNET_V1
Initial Mainnet infrastructure deployment authorized: profile-dependent
Production ready: NO
User funds/activation/settlement/frontend/public reliance: NO
Mainnet deployed: NO
```

Human deployment command after independent operator review:

```bash
npm run deploy:mainnet:live-local-gated
```

Required Stage-B verification command immediately afterward:

```bash
npm run mainnet:postdeploy:verify
```
