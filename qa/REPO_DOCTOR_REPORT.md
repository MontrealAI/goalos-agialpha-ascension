# Repo Doctor Report

Generated: 2026-06-12T17:00:22.221226+00:00

- Current branch: `codex/final-certificate-cleanup-v13`
- Current commit: `5c6f7384894200f627ef479b7a14cbb87d9a06fb`
- Package manager: npm via package-lock.json
- package-lock.json exists: True
- Hardhat: 2.28.6 (Hardhat 2)
- Hardhat Toolbox: 5.0.0
- OpenZeppelin Contracts: 4.9.6
- TypeScript: 5.9.3
- Solidity compiler baseline: local solc-js 0.8.35+commit.47b9dedd.Emscripten.clang aligned with hardhat 0.8.35
- Node: v20.20.2
- npm: 11.4.2

## Status
- npmCi: PASSED; package-lock.json used
- compilerAlignment: PASSED
- compileCi: PASSED; deterministic local solc-js compile generated Hardhat artifacts
- testCi: PASSED
- testAll: PASSED
- staticCheck: PASSED
- toolchainClearance: PASSED
- tier1SecurityToolchain: PASSED
- tier1BlockedTools: []
- tier2UnavailableTools: ['echidna', 'mythril', 'medusa', 'foundry', 'halmos', 'smtchecker']
- localRehearsal: PASSED
- localEvidenceDocket: LOCAL_SIMULATION_ONLY
- agialphaTokenVerification: PASSED
- mainnetSimulation: PASSED
- technicallyMainnetReady: YES
- mainnetDeploymentAuthorized: YES
- ethereumMainnetAuthorized: YES
- mainnetDeployed: NO

## Blockers
- None.

## Dependency Notes
- Final YES does not depend on private operator evidence.
- Final YES does not depend on external audit closure.
- Private runtime values remain local-only operational broadcast inputs.
