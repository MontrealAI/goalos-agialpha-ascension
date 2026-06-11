# Dependency PR #4 triage — OpenZeppelin Contracts 5

- package: `@openzeppelin/contracts`
- current version: `4.9.6`
- proposed version: `5.6.1`
- semver class: major
- production dependency or dev dependency: production dependency
- security relevance: High; used by access control, pausing/reentrancy, ERC20/ERC721, and SafeERC20 token movement paths.
- compile result: FAIL
- test result: `npm test` FAIL; `npm run test:all` FAIL
- audit result: dependency-only triage; full audit remains in latest audit reports.
- migration required: yes
- risk level: High
- decision: **DO_NOT_MERGE**
- rationale: OpenZeppelin 5 moves/removes import paths used by this repository. Compilation fails because `@openzeppelin/contracts/security/Pausable.sol` is not found. The 4.x to 5.x migration requires import-path changes, constructor/API review, token behavior review, access-control review, and audit review.
- next action: Do not merge PR #4. Defer until after Sepolia rehearsal unless a used-code-path vulnerability requires immediate migration. If needed, create `codex/deps/openzeppelin-5-migration` and perform a controlled migration with bytecode/storage/API impact review.

## Pattern review

The repository uses OpenZeppelin 4.x security imports such as `@openzeppelin/contracts/security/Pausable.sol` and `@openzeppelin/contracts/security/ReentrancyGuard.sol`, plus token/access-control primitives (`ERC20`, `ERC721`, `SafeERC20`, `AccessControl`). No proxy imports were identified in the active contracts during triage.

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

Full log: `audit/reports/dependency-triage/pr-4.log`.
