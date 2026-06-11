# TypeScript 6 Migration Deferred

Decision: CONTROLLED_MIGRATION_REQUIRED / DEFER.

TypeScript 6 must not be merged unless `npx tsc --noEmit`, `npm run compile`, `npm test`, `npm run test:all`, and `npm run static-check` all pass. The current TypeScript 5.9.3 baseline remains in place for mainnet authorization evidence.
