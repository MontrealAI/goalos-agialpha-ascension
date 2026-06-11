# TypeScript 6 Migration Decision

Decision: **DEFER**.

Do not merge Dependabot PR #3 for `typescript` 5.9.3 → 6.0.3 into the Sepolia-readiness branch unless Hardhat config, ts-node scripts, generated typings, and tests all pass.

## Rationale

TypeScript major upgrades can change type checking and module behavior used by Hardhat, TypeChain, deployment scripts, and tests. The production-continuation branch remains on TypeScript 5.9.3 until a controlled TypeScript 6 branch proves compatibility.

## Required controlled branch

`codex/deps/typescript-6-controlled-migration`

## Merge gates

- `npx tsc --noEmit` passes if enabled for the project.
- `npm run compile`, `npm test`, `npm run test:all`, `npm run static-check`, and `npm run readiness:v4.3` pass.
- Deployment and Sepolia rehearsal scripts execute with the migrated TypeScript stack.
