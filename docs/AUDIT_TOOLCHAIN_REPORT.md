# Audit Toolchain Report

The audit toolchain is implemented with Slither, Echidna, Mythril, Medusa, Foundry/Forge, Semgrep, and npm audit entrypoints. Timestamped outputs are written under `audit/reports/YYYY-MM-DD-HHMM/`.

Latest expected artifact set includes: Hardhat test logs, Foundry log or pending record, Slither JSON/SARIF/text, Echidna JSON/text, Medusa JSON/text, Mythril JSON/text, Semgrep JSON/text, npm audit JSON/text, gas/coverage placeholders where plugins are absent, audit summary, unresolved findings, dependency triage summary, and checksums.

Environment-blocked tools are documented as pending and remain mainnet blockers until executed in an equipped environment or accepted by qualified reviewers. npm audit findings are separated from deployed-bytecode findings: production dependency critical/high advisories affecting used code paths are blockers, while devDependency advisories are release-tooling risks that must be triaged.
