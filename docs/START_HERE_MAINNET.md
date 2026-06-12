# Start Here: Ethereum Mainnet Authorization Package

This repository is a public, no-secrets GoalOS AGIALPHA Ascension v4.4 candidate. Public CI does not require RPC URLs, deployer private keys, founder signatures, treasury/admin addresses, or Etherscan keys.

1. Run `npm ci`.
2. Run `npm run mainnet:status`.
3. Run `npm run mainnet:local-checks`.
4. Run `npm run mainnet:security`.
5. Run `npm run mainnet:local-rehearsal`.
6. Private operator prepares `.private/` with `npm run mainnet:prepare-private`.
7. Private operator runs Sepolia rehearsal and Ethereum mainnet read-only preflight locally.
8. Private operator commits only redacted `qa/public-*.json` evidence commitments.
9. Run `npm run mainnet:final-check`.
10. If and only if all decisions are YES, founder/deployer may run `npm run deploy:ethereum-mainnet:gated:local` locally.

No Ethereum Mainnet deployment is performed by CI or by this documentation.
