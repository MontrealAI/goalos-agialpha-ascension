# Repo Doctor Report

Generated: 2026-06-12T17:51:42.191470+00:00

- Current branch: `codex/mainnet-authorization-certificate-v12`
- Current commit: `61eb3a6a92369014304cc058f94c10f5f0d0aa54`
- Package manager: npm via package-lock.json
- package-lock.json exists: True
- Active Hardhat version: 2.28.6 (Hardhat 2)
- Active Hardhat Toolbox version: 5.0.0
- Active OpenZeppelin Contracts version: 4.9.6
- Active TypeScript version: 5.9.3
- Active Node version in workflows: 20.x / v20.20.2 local runtime
- Solidity compiler baseline: local solc-js 0.8.35+commit.47b9dedd.Emscripten.clang aligned with hardhat 0.8.35
- Node: v20.20.2
- npm: 11.4.2

## Current status
- npmCi: PASSED; package-lock.json used
- compilerAlignment: PASSED
- compileCi: PASSED; deterministic local solc-js compile generated Hardhat artifacts without Hardhat compiler download
- testCi: PASSED
- testAll: PASSED
- staticCheck: PASSED
- slitherSecurityToolchain: PASSED; no unresolved critical/high findings
- toolchainClearance: PASSED
- tier1SecurityToolchain: PASSED
- tier1BlockedTools: []
- tier2UnavailableTools: ['echidna', 'mythril', 'medusa', 'foundry', 'halmos', 'smtchecker']
- localRehearsal: PASSED
- localEvidenceDocket: LOCAL_SIMULATION_ONLY generated
- evidenceDocket: PASSED; local public-safe Evidence Docket generated
- agialphaTokenVerification: PASSED
- mainnetAuthorizationStatus: TECHNICALLY_MAINNET_READY=YES; MAINNET_DEPLOYMENT_AUTHORIZED=YES; ETHEREUM_MAINNET_AUTHORIZED=YES; MAINNET_DEPLOYED=NO
- mainnetSimulation: PASSED
- technicallyMainnetReady: YES
- mainnetDeploymentAuthorized: YES
- ethereumMainnetAuthorized: YES
- mainnetDeployed: NO

## Blockers preventing TECHNICALLY_MAINNET_READY: YES
- None.

## Blockers preventing MAINNET_DEPLOYMENT_AUTHORIZED: YES
- None.

## Blockers preventing ETHEREUM_MAINNET_AUTHORIZED: YES
- None.

## Dependency Notes
- Final YES does not depend on private operator evidence.
- Final YES does not depend on external audit closure.
- Private runtime values remain local-only operational broadcast inputs.
