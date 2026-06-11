# Dependency Upgrade Policy

GoalOS AGIALPHA Ascension does not merge dependency updates blindly. Dependency changes are evaluated against compile, tests, repository safety checks, static checks, readiness checks, audit-tool compatibility, and mainnet authorization invariants.

## Classification

- Production dependencies that influence deployed bytecode, token behavior, access control, cryptography, or SafeERC20 handling are high-risk by default.
- DevDependencies that influence compiler, Hardhat, TypeChain, ts-node, test execution, CI, or deploy scripts are release-toolchain risks.
- Major upgrades require isolated migration branches unless a security advisory affecting a used code path requires immediate action.

## Required gates before merging dependency PRs

1. `npm ci` when `package-lock.json` exists.
2. `npm run repo:all`
3. `npm run repo:no-paid-products`
4. `npm run compile`
5. `npm test`
6. `npm run test:all`
7. `npm run static-check`
8. `npm run readiness:v4.3`
9. `npm run mainnet:authorization-check:public` returns expected private-evidence-pending NO without real gates.
10. Audit-tool impact reviewed and documented.

## Decision rules

- Do not use `--legacy-peer-deps` as a permanent fix.
- Do not merge Hardhat 3, Hardhat Toolbox 7, TypeScript 6, or OpenZeppelin 5 into the mainnet path without a dedicated migration branch, updated runbooks, and passing evidence.
- If install/compile/test/static/readiness fails: **DO_NOT_MERGE**.
- If a major upgrade touches deployed bytecode or security primitives: **DEFER** or **REPLACE_WITH_CONTROLLED_BRANCH** unless migration and audit are complete.
- If a devDependency upgrade changes compiler/test/deploy behavior: defer unless Hardhat, ts-node, TypeChain, deploy scripts, CI, and audit scripts are green.
- Mainnet remains blocked regardless of dependency status until all real launch gates are complete.
- Public CI must not require RPC URLs, private keys, private addresses, founder signatures, or API keys.
- Any dependency vulnerability waiver must be documented in the findings register and the toolchain clearance report.
