# Dependabot Triage Report

Dependabot PRs were triaged in isolated temporary workspaces and were **not merged blindly**.

| PR | Package | Upgrade | Risk | Decision | Rationale |
|---:|---|---|---|---|---|
| #1/#12 | `hardhat` | `2.28.6` → `3.9.0` | High | **CONTROLLED_MIGRATION_REQUIRED** | Hardhat 3 conflicts with the current Hardhat-2 toolbox/chai-matchers stack; defer to controlled migration. |
| #2 | `@nomicfoundation/hardhat-toolbox` | `5.0.0` → `7.0.0` | High | **DO_NOT_MERGE** | Compile/tests fail; major Hardhat tooling migration required. |
| #3 | `typescript` | `5.9.3` → `6.0.3` | Medium/High | **DO_NOT_MERGE** | `npx tsc --noEmit` and tests fail under TypeScript 6. |
| #4 | `@openzeppelin/contracts` | `4.9.6` → `5.6.1` | High | **DO_NOT_MERGE** | Compile fails due OpenZeppelin 5 import-path changes; controlled migration/audit required. |

Detailed records:

- `audit/reports/dependency-triage/pr-1-12-hardhat.md`
- `audit/reports/dependency-triage/pr-1-hardhat.md`
- `audit/reports/dependency-triage/pr-12-hardhat.md`
- `audit/reports/dependency-triage/pr-2-hardhat-toolbox.md`
- `audit/reports/dependency-triage/pr-3-typescript.md`
- `audit/reports/dependency-triage/pr-4-openzeppelin.md`
- `audit/reports/dependency-triage/openzeppelin-pattern-scan.md`

Missing Dependabot labels are documented in `docs/DEPENDABOT_LABEL_FIX.md` because `gh` is unavailable in this container.

## Mainnet impact

Dependency PRs do not authorize mainnet. Ethereum Mainnet remains `NOT_AUTHORIZED` until all real gates, automated/internal security clearance, and founder deployment approval are complete.
