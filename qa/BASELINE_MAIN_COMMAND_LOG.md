# Baseline Main Command Log

`main` is not available as a local branch in this execution environment; the baseline was established on the current repository foundation branch before dependency upgrades were merged. No Dependabot PR was merged.

| Command | Result |
|---|---|
| `npm install` | PASS with npm audit warnings |
| `npm run repo:all` | PASS |
| `npm run repo:no-paid-products` | PASS |
| `npm run compile` | PASS |
| `npm test` | PASS |
| `npm run test:all` | PASS |
| `npm run static-check` | PASS |
| `npm run readiness:v4.3` | PASS |
| `npm run evidence:docket:template` | PASS |
| `npm run mainnet:authorization-check` | PASS_EXPECTED_NOT_AUTHORIZED |

Mainnet remains blocked because real gates are absent.
