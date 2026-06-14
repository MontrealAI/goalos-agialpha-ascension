# AGENTS.md

## Repository expectations

- This is an evidence-first, claim-bounded Ethereum/Hardhat repository.
- Do not fabricate deployment or verification evidence.
- Do not weaken Mainnet gates.
- Do not add CI Mainnet broadcast.
- Do not commit secrets.
- Preserve canonical AGIALPHA token boundary.
- Preserve Sepolia/Mainnet chainId guards.
- Preserve public/private proof boundary.
- Prefer wrappers around existing scripts instead of duplicating systems.
- Add tests for every safety-critical deployment or verification behavior.
- Generated docs must preserve claim boundaries.
- Ethereum Mainnet deployed = YES requires real chainId=1 transaction evidence.
- Contract verified = YES requires source/bytecode verification evidence or confirmed already-verified status.
- PRs must include commands run, tests passed/failed, generated artifacts, and claim-boundary impact.

## Review guidelines

When reviewing deployment or verification changes, treat these as P0/P1:

- Any path that can broadcast Ethereum Mainnet transactions from CI.
- Any secret leakage.
- Any weakened Mainnet gate.
- Any MockAGIALPHA or new AGIALPHA token path on Mainnet.
- Any Mainnet deployed YES without chainId=1 transaction evidence.
- Any verified YES without verification evidence.
- Any missing constructor-argument capture for verifiable contracts.
- Any manifest missing data needed for verification.
- Any misleading claim boundary.
- Any missing test for a safety-critical gate.
