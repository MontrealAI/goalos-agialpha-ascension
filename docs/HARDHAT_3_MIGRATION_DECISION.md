# Hardhat 3 Migration Decision

Decision: **DEFER / CONTROLLED_MIGRATION_REQUIRED**.

Do not merge Dependabot PR #1/#12 for `hardhat` 2.28.6 → 3.9.0 into the Sepolia-readiness branch.

## Rationale

The screenshots show `hardhat@3.9.0` conflicts with the current Hardhat-2-aligned toolbox and chai matcher stack (`@nomicfoundation/hardhat-toolbox@5.0.0`, `@nomicfoundation/hardhat-chai-matchers@2.1.2`). Hardhat 3 requires a coherent migration of Hardhat, toolbox/plugins, Node runtime, TypeScript configuration, test APIs, and deployment scripts.

## Required controlled branch

`codex/deps/hardhat-3-controlled-migration`

## Merge gates

- `npm ci` succeeds without `--legacy-peer-deps`.
- `npm run compile`, `npm test`, `npm run test:all`, `npm run static-check`, and `npm run readiness:v4.3` pass.
- Deployment scripts and Sepolia rehearsal path still work.
- Automated security/toolchain run produces no unresolved critical/high findings.
- Node version policy is updated for Hardhat 3 if required.
