# Dependency Baseline for Mainnet Authorization

The mainnet authorization branch prioritizes deterministic evidence over latest-package churn.

Pinned baseline:

- `hardhat`: `2.28.6`
- `@nomicfoundation/hardhat-toolbox`: `5.0.0`
- `@nomicfoundation/hardhat-chai-matchers`: `2.1.2` via toolbox
- `@openzeppelin/contracts`: `4.9.6`
- `typescript`: `5.9.3`

CI must use `npm ci` when `package-lock.json` exists. `--legacy-peer-deps` is not an acceptable permanent fix because it can hide a broken peer dependency graph.

## Active deployment model

Hardhat 2 is the active production deployment path. Hardhat Ignition is not mandatory for final Ethereum Mainnet deployment; custom scripts are used for explicit private-local authorization gates, canonical AGIALPHA address checks, typed confirmation, and public-safe manifest generation.
