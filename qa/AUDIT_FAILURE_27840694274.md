# Audit Failure 27840694274

Workflow: GoalOS AGIALPHA Audit-Candidate CI
Branch: `codex/implement-business-operational-gates-for-goalos`
Failing SHA: `0ea4fed44f84ba8f4a8aa85cc1797bb0f3acc6de`

## Findings

| Advisory | Package | Installed | Severity | Scanner | Remediation |
|---|---:|---:|---|---|---|
| GHSA-r5fr-rjxr-66jc | lodash | 4.17.21 | high | npm audit | Finding-specific temporary acceptance with expiry and reachability controls in audit/TRIAGE.json. |
| GHSA-5c6j-r48x-rmvq | serialize-javascript | 6.0.2 | high | npm audit | package override to serialize-javascript 7.0.6. |
| GHSA-ph9p-34f9-6g65 | tmp | 0.0.33 | high | npm audit | package override to tmp 0.2.7. |
| GHSA-vrm6-8vpv-qv8q / GHSA-v9p9-hfj2-hcw8 / GHSA-vxpw-j846-p89q | undici | 5.29.0 | high | npm audit | package override to undici 6.27.0. |

## Pipeline defects
- fail-on-critical-findings.py accepted missing and malformed evidence as success
- audit summary exposed only aggregate critical_high_unresolved count for direct wrapper counts
- scanner wrappers used unpinned @latest installs and stale current-run/latest pointers
- normalized finding details were not required before gate evaluation
