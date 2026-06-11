# OpenZeppelin 5 Migration Decision

Decision: **DEFER / CONTROLLED_MIGRATION_REQUIRED**.

Do not merge Dependabot PR #4 for `@openzeppelin/contracts` 4.9.6 → 5.6.1 into the Sepolia-readiness branch.

## Rationale

The screenshot compile failure is expected for an unplanned OpenZeppelin 5 upgrade: `@openzeppelin/contracts/security/Pausable.sol` is no longer available at the OpenZeppelin 4 import path. OpenZeppelin 5 moves `Pausable` and `ReentrancyGuard` to `utils/` and can require constructor, Ownable, ERC token, and semantic review.

## Required controlled branch

`codex/deps/openzeppelin-5-controlled-migration`

## Required checks

- Replace imports deliberately, including `security/Pausable.sol` → `utils/Pausable.sol` and `security/ReentrancyGuard.sol` → `utils/ReentrancyGuard.sol` where applicable.
- Review Ownable, AccessControl, ERC20/ERC721/ERC1155, SafeERC20, and proxy/initializer usage.
- Run full compile/tests, invariants/fuzzing, Slither/static analysis, and Sepolia rehearsal.
- Do not merge with unresolved critical/high findings.
