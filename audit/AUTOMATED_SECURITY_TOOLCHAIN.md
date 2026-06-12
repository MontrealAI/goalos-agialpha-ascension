# Automated/Internal Security Toolchain

Tier 1 mandatory tools: npm ci, deterministic compile, Hardhat tests, test:all, static-check, repo checks, public-status check, no-private-operator-data check, no-paid-products check, Slither, Solhint, Semgrep, secret scanning, actionlint, shellcheck, npm audit/OSV triage, local rehearsal, invariant tests, deployment guardrails, findings register, and clearance report.

Tier 2 best-available tools: Foundry, Echidna, Medusa, Mythril, Halmos, solc SMTChecker, SBOM, live mainnet fork simulation. Environment-unavailable Tier 2 tools are documented and do not block if Tier 1 passes and public governance accepts the status.
