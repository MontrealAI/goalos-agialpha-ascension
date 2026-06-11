# Codex Run Log

- Branch: `codex/sepolia-rehearsal-audit-toolchain-mainnet-decision`
- Starting commit: `cc359b8755640e09aebc79b7bf75e2296dcbe8bc`
- Node: `v20.20.2`
- npm: `11.4.2`
- Hardhat: `2.28.6`
- Solidity compiler: Hardhat configured `0.8.24`; `npx solcjs --version` returned `0.8.35+commit.47b9dedd.Emscripten.clang`
- Slither: `0.11.5`
- Foundry/Forge: not installed in container
- Echidna: not installed in container
- Mythril: install attempted; blocked by Python 3.12 dependency build incompatibility (`numpy==1.19.0` / distutils)
- Medusa: not installed in container
- Latest audit report directory: `audit/reports/2026-06-11-1528`
- Deployment manifest: `deployments/ethereum-sepolia.agialpha.latest.json`
- Evidence docket: `evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json`
- Mainnet remains blocked: yes, `NOT_AUTHORIZED`

## Commands and results

| Command | Result | Artifact / note |
|---|---|---|
| `npm install` | Passed with npm audit warnings | 44 vulnerabilities reported by npm audit metadata |
| `npm run repo:all` | Passed | repository safety/status/production/no-paid checks passed |
| `npm run repo:no-paid-products` | Passed | no paid/private product issue detected |
| `npm run static-check` | Passed | Static QA passed |
| `npm run readiness:v4.3` | Passed | readiness reported gate-clean evidence-ready audit candidate; mainnet not authorized |
| `npm run evidence:docket:template` | Passed | `evidence/SEPOLIA_EVIDENCE_DOCKET_TEMPLATE_v4_2.json` |
| `npm run mainnet:authorization-check` | Passed, expected `NOT_AUTHORIZED` | `docs/MAINNET_AUTHORIZATION_DECISION.md/json` |
| `npm run compile` | Passed | Hardhat compile succeeded |
| `npm test` | Passed | 8 tests passing |
| `npm run test:all` | Passed | 8 tests passing |
| `npm run sepolia:rehearsal` | Passed in local Hardhat JSON-RPC chainId `11155111` mode | `deployments/ethereum-sepolia.agialpha.latest.json` |
| `npm run sepolia:evidence` | Passed | `evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json` |
| `npm run audit:slither` | Passed after remediation | `audit/reports/2026-06-11-1528/slither.json`, `.txt`, `.sarif` |
| `npm run audit:echidna` | Environment-blocked/pending | executable not installed; pending recorded in audit reports |
| `npm run audit:mythril` | Environment-blocked/pending | executable not installed; install attempt failed on Python 3.12 dependency build |
| `npm run audit:medusa` | Environment-blocked/pending | executable not installed; pending recorded in audit reports |
| `npm run audit:foundry` | Environment-blocked/pending | `forge` not installed; pending recorded in audit reports |
| `npm run audit:all` | Passed with documented pending tools | `audit/reports/2026-06-11-1528/audit-summary.json` |
| `npm run audit:summarize` | Passed | audit summary generated |
| `npm run audit:fail-on-critical` | Passed | no unresolved critical/high findings in summary |
| `npm run verify:agialpha-token` | Warning / pending RPC | no `ETHEREUM_MAINNET_RPC_URL`; read-only verification not performed |
| `npm run preflight:ethereum-mainnet` | Passed, expected `NOT_AUTHORIZED` | missing real gate env vars and RPC |

## Sepolia/public-network note

The rehearsal was executed against a local Hardhat JSON-RPC node configured with chainId `11155111` because no public Sepolia RPC or funded Sepolia deployer secret was present. Public Ethereum Sepolia replay remains a mainnet blocker.
