# Hardhat Ethereum Mainnet Deployment Baseline

- CI Node version: Node.js 20 via GitHub Actions setup-node.
- Package manager: npm with committed `package-lock.json`; CI must use `npm ci`.
- Hardhat: 2.28.6.
- Hardhat Toolbox: 5.0.0.
- OpenZeppelin Contracts: 4.9.6.
- TypeScript: 5.9.3.
- Active production path: Hardhat 2.
- Hardhat 3 / Toolbox 7 / OpenZeppelin 5: deferred to a separate controlled migration branch.
- Hardhat Ignition: optional only; final mainnet path uses custom typed-confirmation gated scripts because the current suite needs private local evidence gates and redacted manifests.
- Custom scripts: yes, under `scripts/` and `scripts/private/`.

The chosen path preserves the stable working dependency baseline while adding Ethereum Mainnet and Sepolia network aliases that do not require secrets during config load. Private RPC URLs and deployer keys are loaded only by local operator scripts or explicit deployment/preflight commands.
