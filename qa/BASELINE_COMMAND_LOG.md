# Baseline Command Log

Branch: `codex/stabilize-ci-deps-toolchain-sepolia-readiness`

| Command | Result | Notes |
|---|---|---|
| `npm install` | PASS_WITH_AUDIT_WARNINGS | 44 npm audit findings remain for dependency review; no legacy peer deps used. |
| `npm ci` | PASS_WITH_AUDIT_WARNINGS | Lockfile install succeeded on the baseline stack. |
| `npm ls hardhat @nomicfoundation/hardhat-toolbox @nomicfoundation/hardhat-chai-matchers @openzeppelin/contracts typescript` | PASS | Hardhat 2.28.6, toolbox 5.0.0, chai matchers 2.1.2, OpenZeppelin 4.9.6, TypeScript 5.9.3. |
| `npm run repo:all` | PASS | Repository safety/status/production/no-paid-products checks passed. |
| `npm run repo:no-paid-products` | PASS | Paid/private product check passed. |
| `npm run compile` | PASS | 78 Solidity files compiled. |
| `npm test` | PASS | 8 passing tests. |
| `npm run test:all` | PASS | 8 passing tests. |
| `npm run static-check` | PASS | Static QA passed. |
| `npm run readiness:v4.3` | PASS | Gate-clean evidence-ready candidate; mainnet not authorized. |
| `npm run assert:public-status` | PASS | Public status bounded and not externally audited. |
| `npm run evidence:docket:template` | PASS | Template regenerated. |
| `python scripts/mainnet-authorization-check.py` | PASS_EXPECTED_NOT_AUTHORIZED | Mainnet authorization remains NO. |
| `npm run audit:fail-on-critical` | PASS | No unresolved critical/high findings in summary. |
| `npm run mainnet:readiness-check` | PASS_EXPECTED_NOT_READY | Technical readiness remains NO. |
| `npm run mainnet:authorization-check` | PASS_EXPECTED_NOT_AUTHORIZED | Deployment authorization remains NO. |

Ethereum Mainnet was not deployed.
