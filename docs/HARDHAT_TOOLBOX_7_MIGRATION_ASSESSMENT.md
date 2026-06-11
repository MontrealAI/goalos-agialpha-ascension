# Hardhat Toolbox 7 Migration Assessment

Decision: **DO_NOT_MERGE PR #2**.

The repository is currently Hardhat 2 aligned: `hardhat.config.ts` uses the existing Hardhat 2 configuration style, `hardhat` resolves to the 2.x line, and the current compile/tests are green before the dependency PR.

Triage of `@nomicfoundation/hardhat-toolbox` `5.0.0` → `7.0.0` found that `npm run compile`, `npm test`, and `npm run test:all` fail. Hardhat reports that the installed latest toolbox does not work with Hardhat 2 nor 3 and recommends the `hh2` tag for Hardhat 2.

Required migration if revisited:

- Create a dedicated Hardhat migration branch.
- Upgrade Hardhat deliberately with matching toolbox/plugins.
- Rework config loading, TypeChain, tests, deploy scripts, and CI.
- Re-run compile/tests/readiness/audit toolchain.
- Require human review before merge.
