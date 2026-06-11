# Dependency PR #3 triage — TypeScript 6

- package: `typescript`
- current version: `5.9.3`
- proposed version: `6.0.3`
- semver class: major
- production dependency or dev dependency: devDependency
- security relevance: Medium/High; affects Hardhat config loading, ts-node execution, TypeChain typings, and TypeScript tests/scripts.
- compile result: PASS
- test result: `npm test` FAIL; `npm run test:all` FAIL
- audit result: dependency-only triage; full audit remains in latest audit reports.
- migration required: yes
- risk level: Medium/High
- decision: **DO_NOT_MERGE**
- rationale: `npx tsc --noEmit` fails with TypeScript 6 configuration/type errors, and Hardhat tests fail under the upgraded TypeScript stack. The failures include `TS5011` rootDir/common source directory issues and generated contract objects being typed as `BaseContract` without expected methods.
- next action: Do not merge PR #3. Create `codex/deps/typescript-6-migration` if TypeScript 6 is required, then update `tsconfig`, TypeChain generation assumptions, test typings, and scripts in isolation.

## Command results

| Command | Result |
|---|---|
| `npm install` | PASS |
| `npm run repo:all` | PASS |
| `npm run repo:no-paid-products` | PASS |
| `npm run compile` | PASS |
| `npx tsc --noEmit` | FAIL |
| `npm test` | FAIL |
| `npm run test:all` | FAIL |
| `npm run static-check` | PASS |
| `npm run readiness:v4.3` | PASS |
| `npm run mainnet:authorization-check` | PASS_EXPECTED_NOT_AUTHORIZED |

Full log: `audit/reports/dependency-triage/pr-3.log`.
