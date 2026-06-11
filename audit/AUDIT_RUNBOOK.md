# Audit Runbook

1. Run `npm install`.
2. Run `npm run compile && npm test && npm run test:all`.
3. Run `npm run audit:all`.
4. Review `audit/reports/latest.txt` and the timestamped report directory.
5. Review Semgrep and npm audit outputs separately from Solidity findings.
6. Triage all critical/high findings before Sepolia evidence is considered complete.
7. Do not authorize mainnet while medium findings lack qualified acceptance or any required gate is missing.
