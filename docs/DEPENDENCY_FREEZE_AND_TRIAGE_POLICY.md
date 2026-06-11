# Dependency Freeze and Triage Policy

Status: **BASELINE_FREEZE_FOR_SEPOLIA_READINESS**.

This repository stays on the current green Hardhat 2 dependency stack until major migrations are completed on controlled branches with compile, test, toolchain, and Sepolia evidence.

## Frozen baseline

| Package | Baseline | Policy |
|---|---:|---|
| `hardhat` | `2.28.6` | Keep Hardhat 2 for production-continuation and Sepolia readiness. |
| `@nomicfoundation/hardhat-toolbox` | `5.0.0` | Keep Hardhat-2-compatible toolbox. |
| `@nomicfoundation/hardhat-chai-matchers` | `2.1.2` | Keep transitive Hardhat-2-compatible matcher stack. |
| `@openzeppelin/contracts` | `4.9.6` | Defer OpenZeppelin 5 until a controlled migration passes. |
| `typescript` | `5.9.3` | Defer TypeScript 6 until Hardhat/scripts/tests pass. |

## Rules

- Use `npm ci` in CI when `package-lock.json` exists.
- Do not use `--legacy-peer-deps` as a permanent fix.
- Do not merge major Dependabot PRs blindly.
- Major upgrades require controlled branches, migration notes, compile/test evidence, automated security/toolchain evidence, and Sepolia rehearsal verification.
- Ethereum Mainnet remains not authorized regardless of dependency status.

## Controlled migration issues to open

1. Controlled Hardhat 3 migration.
2. Controlled OpenZeppelin 5 migration.
3. Controlled TypeScript 6 migration.
