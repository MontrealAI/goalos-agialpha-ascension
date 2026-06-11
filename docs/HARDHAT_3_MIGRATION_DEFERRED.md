# Hardhat 3 Migration Deferred

Decision: CONTROLLED_MIGRATION_REQUIRED / DEFER.

Hardhat 3 requires a coherent Hardhat-3-compatible plugin stack and Node.js `v22.13.0+`. The current Hardhat 2 baseline is green and is retained for the mainnet authorization package unless a used-code-path security issue requires immediate migration.

A controlled migration branch should update Hardhat, toolbox, chai matchers, TypeScript/ts-node, deployment scripts, tests, CI Node version, and security tooling together.
