# Dependency PR #2 triage — Hardhat Toolbox 7

- package: `@nomicfoundation/hardhat-toolbox`
- current version: `5.0.0`
- proposed version: `7.0.0`
- semver class: major
- production dependency or dev dependency: devDependency
- security relevance: High; controls compiler/test/deploy tooling and can affect generated artifacts.
- compile result: FAIL
- test result: `npm test` FAIL; `npm run test:all` FAIL
- audit result: dependency-only triage; full audit remains in latest audit reports.
- migration required: yes
- risk level: High
- decision: **DO_NOT_MERGE**
- rationale: `npm run compile`, `npm test`, and `npm run test:all` fail after the upgrade. Hardhat reports that the installed latest toolbox does not work with Hardhat 2 nor 3 and recommends the `hh2` tag for Hardhat 2.
- next action: Do not merge PR #2. If this upgrade is required, create a dedicated Hardhat 3 migration branch and update Hardhat, plugins, config, TypeChain, deployment scripts, CI, and audit tooling deliberately.

## Hardhat stack assessment

The current repository is Hardhat 2 aligned: `hardhat.config.ts` uses the Hardhat 2 config style and `package.json` pins `hardhat` in the 2.x line. The current stack is green before the Toolbox 7 upgrade, so this major tooling migration should be deferred until after Sepolia rehearsal evidence is accepted or handled in a dedicated migration branch.

## Command results

| Command | Result |
|---|---|
| `npm install` | PASS |
| `npm run repo:all` | PASS |
| `npm run repo:no-paid-products` | PASS |
| `npm run compile` | FAIL |
| `npm test` | FAIL |
| `npm run test:all` | FAIL |
| `npm run static-check` | PASS |
| `npm run readiness:v4.3` | PASS |
| `npm run mainnet:authorization-check` | PASS_EXPECTED_NOT_AUTHORIZED |
| `npm run deploy:ethereum-sepolia -- --dry-run` | FAIL |

Full log: `audit/reports/dependency-triage/pr-2.log`.
