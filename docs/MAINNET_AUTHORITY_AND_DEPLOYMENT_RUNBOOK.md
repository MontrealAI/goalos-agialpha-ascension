# Mainnet authority and deployment runbook

The disposable MetaMask account is only the gas payer. It must never be the contract owner, default administrator, permanent operator, vault administrator, Safe owner, or treasury/economic destination. Use a Ledger-controlled Safe (`GOVERNANCE_OWNER_KIND=SAFE`) by default. A direct Ledger EOA is a single-key recovery risk and requires `ALLOW_SINGLE_LEDGER_EOA_GOVERNANCE=I_ACCEPT_SINGLE_KEY_AND_RECOVERY_RISK`.

Never enter a seed phrase or private key into this repository. Put private runtime data in `.private/authority-policy.mainnet.json`, validate it with `npm run authority:policy:validate -- --policy .private/authority-policy.mainnet.json`, and verify full addresses, not abbreviated prefixes.

Local sequence: `npm ci`, `npm run compile:ci`, `npm run ownership:test`, `npm run authority:inventory`, `npm run deploy:mainnet:fork-rehearsal`. Mainnet live commands remain local-gated and must not run in CI. Stop on wrong chain, nonce drift, stale git/artifact hashes, Safe mismatch, missing audit approval, fee cap excess, failed receipt, codehash mismatch, unexpected owner/role member, no-setter treasury mismatch, or secret leakage.

After deployment, the final owner prepares/executess Phase-B grants. The deployer is decommissioned only after ownership, role, Safe, bytecode, and economic-destination evidence passes at a confirmed block. Removing an account from MetaMask does not invalidate its private key; safety comes from zero on-chain authority and sweeping residual ETH only after the decommission check passes.
