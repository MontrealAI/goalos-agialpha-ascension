# Dependabot Label Fix

`gh` was not available in this execution environment, so labels could not be created directly from the container.

Repository maintainers should create these labels in GitHub before Dependabot applies them to PRs:

| Label | Color | Description |
|---|---|---|
| `dependencies` | `0366d6` | Dependency updates |
| `security` | `d73a4a` | Security and audit-sensitive work |
| `priority-critical` | `b60205` | Blocks the next production gate |
| `priority-high` | `d93f0b` | High-priority production continuation work |
| `mainnet-blocked` | `b60205` | Ethereum Mainnet is not authorized |
| `sepolia` | `5319e7` | Ethereum Sepolia rehearsal |
| `evidence-docket` | `0e8a16` | Evidence Docket work |
| `audit` | `1d76db` | Audit, findings, and security review |
| `ci` | `5319e7` | Continuous integration |
| `docs` | `0075ca` | Documentation |
| `claims` | `fbca04` | Public claims review |
| `treasury` | `0052cc` | Treasury/admin ceremony |
| `legal` | `fef2c0` | Legal/token counsel review |
| `tax` | `c2e0c6` | Tax/accounting review |

Equivalent `gh` commands:

```bash
gh label create dependencies --color 0366d6 --description "Dependency updates" || true
gh label create security --color d73a4a --description "Security and audit-sensitive work" || true
gh label create priority-critical --color b60205 --description "Blocks the next production gate" || true
gh label create priority-high --color d93f0b --description "High-priority production continuation work" || true
gh label create mainnet-blocked --color b60205 --description "Ethereum Mainnet is not authorized" || true
gh label create sepolia --color 5319e7 --description "Ethereum Sepolia rehearsal" || true
gh label create evidence-docket --color 0e8a16 --description "Evidence Docket work" || true
gh label create audit --color 1d76db --description "Audit, findings, and security review" || true
gh label create ci --color 5319e7 --description "Continuous integration" || true
gh label create docs --color 0075ca --description "Documentation" || true
gh label create claims --color fbca04 --description "Public claims review" || true
gh label create treasury --color 0052cc --description "Treasury/admin ceremony" || true
gh label create legal --color fef2c0 --description "Legal/token counsel review" || true
gh label create tax --color c2e0c6 --description "Tax/accounting review" || true
gh label list
```
