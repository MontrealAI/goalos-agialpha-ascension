# Dependency PR #1/#12 triage — Hardhat 3

- package: `hardhat`
- current version: `2.28.6`
- proposed version: `3.9.0`
- semver class: major
- direct or transitive dependency: direct devDependency
- production or dev dependency: devDependency
- security relevance: High; controls compiler, tests, deployment scripts, plugins, and generated artifacts.
- compile result: NOT_RUN_ON_BASELINE_PR; screenshot indicates install fails before compile.
- test result: NOT_RUN_ON_BASELINE_PR; install failure blocks tests.
- static-check result: NOT_RUN_ON_BASELINE_PR; install failure blocks npm workflow.
- migration required: yes
- risk level: High
- decision: **CONTROLLED_MIGRATION_REQUIRED**
- rationale: `hardhat@3.9.0` conflicts with the current Hardhat-2-aligned `@nomicfoundation/hardhat-toolbox@5.0.0` and `@nomicfoundation/hardhat-chai-matchers@2.1.2` stack. This is a coherent stack migration, not a safe isolated bump.
- next action: Defer PR #1/#12. Create `codex/deps/hardhat-3-controlled-migration` and migrate Hardhat, plugins, Node policy, tests, TypeScript, deployment scripts, and audit tooling together.
