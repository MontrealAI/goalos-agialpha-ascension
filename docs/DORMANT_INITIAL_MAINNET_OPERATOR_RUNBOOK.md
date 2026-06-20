This deployment is dormant infrastructure only. It is not production-ready. It does not authorize user funds, Phase-B configuration, activation, settlement, a public frontend, production announcements, or public reliance.

# Dormant Initial Mainnet Operator Runbook

1. Copy placeholder examples from `.private.example/dormant-mainnet/` into `.private/dormant-mainnet/` and set file mode `0600` where supported.
2. Populate actual Wallet A, Wallet B, RPC/API, fee ceiling, and balance data only in ignored local files. Never store the Ledger seed/private key.
3. Run `npm run mainnet:dormant:doctor`. It is no-broadcast and checks chain ID 1, canonical AGIALPHA, Wallet A key/address, Wallet B permanent authority, Etherscan V2 readiness, fee ceilings, deployer balance, no previous journal, and production-certificate separation.
4. Run `npm run mainnet:dormant:prepare`. It performs deterministic/Hardhat compilation, tests, static QA, security checks, doctor, certificate generation, and certificate validation.
5. Immediately before live broadcast, type dormant-only confirmations including the network and plan-hash suffix. Do not use `ALLOW_MAINNET_DEPLOYMENT`.
6. On Ubuntu, operators may wrap the live ceremony with `systemd-inhibit`; the core command remains cross-platform and warns when sleep inhibition is unavailable.

Fee ceilings (`MAINNET_MAX_FEE_PER_GAS_GWEI`, `MAINNET_MAX_PRIORITY_FEE_PER_GAS_GWEI`) and minimum deployer balance (`MIN_DORMANT_MAINNET_DEPLOYER_BALANCE_ETH`) are explicit local values. Fee ceilings must be rechecked before every transaction.

Use `npm run deploy:mainnet:dormant:live-local-gated` only locally. CI and this Codex task must never broadcast Mainnet.
