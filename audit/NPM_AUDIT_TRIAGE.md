# npm Audit Triage

Status: **TRIAGED_ACCEPTED_DEV_ONLY**.

Production-impacting high/critical findings: **0**.
Untriaged high/critical findings: **0**.

`npm audit` findings are retained in `audit/reports/latest-npm-audit.json`. Current findings are dependency/tooling-path issues and are not deployed Solidity runtime code. Controlled upgrades may address them later; `npm audit fix --force` is prohibited unless compile/tests/security are reviewed.
