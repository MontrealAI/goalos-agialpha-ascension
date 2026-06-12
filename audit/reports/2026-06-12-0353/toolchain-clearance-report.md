# Automated Security Toolchain Clearance Report

Generated: 2026-06-12T03:53:52.386261+00:00
Clearance: **NOT_CLEARED**

## Blockers
- Tier 1 tool slither did not pass (raw status: PENDING_ENVIRONMENT_BLOCKED)
- Tier 1 blocked tools: slither

## Tier 1 mandatory tools
- slither: TIER1_BLOCKED (critical/high: 0)
- semgrep: COMPLETED (critical/high: 0)
- solhint: COMPLETED (critical/high: 0)
- npm-audit: COMPLETED_FINDINGS_REVIEWED_NO_CRITICAL_HIGH_BLOCKER (critical/high: 0)
- osv-scanner: COMPLETED_TRIAGED (critical/high: 0)
- actionlint: COMPLETED (critical/high: 0)
- shellcheck: COMPLETED (critical/high: 0)
- gitleaks: COMPLETED (critical/high: 0)

## Tier 2 unavailable tools
- echidna
- mythril
- medusa
- foundry
- halmos
- smtchecker

## Boundary
- This is automated/internal security-toolchain evidence, not an external audit.
- Tier 1 tools are not marked passed when environment-blocked; Tier 2 unavailable tools are documented separately and not counted as passed.
