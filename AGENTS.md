# AGENTS.md

This is an evidence-first, claim-bounded Ethereum/Hardhat repository.

- Do not fabricate deployment evidence, contract addresses, transaction hashes, verification status, or reports.
- Do not weaken Ethereum Mainnet gates or claim boundaries.
- Do not add CI/GitHub Actions paths that can broadcast Ethereum Mainnet transactions.
- Do not commit secrets, private operator files, RPC URLs, keys, mnemonics, signatures, or filled `.env` files.
- Prefer safe wrappers around existing deployment scripts instead of replacing deployment core logic.
- Add tests for safety-critical deployment behavior.
- Any generated deployment doc/report must preserve the claim boundary.
- Ethereum Mainnet deployed = YES requires real chainId=1 transaction evidence and post-deployment verification.
- PRs must list commands run, tests passed/failed, and claim-boundary impact.
- Do not fabricate verification evidence.
- Preserve official AGIALPHA token boundary.
- Preserve public/private proof boundary.
- Contract verified = YES requires block-explorer/source verification evidence or already-verified confirmation.
- PRs must include commands run, tests passed/failed, generated artifacts, and claim-boundary impact.
