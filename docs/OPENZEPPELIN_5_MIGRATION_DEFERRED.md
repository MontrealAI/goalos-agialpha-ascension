# OpenZeppelin 5 Migration Deferred

Decision: CONTROLLED_MIGRATION_REQUIRED / DEFER.

OpenZeppelin 5 changes import paths such as:

- `@openzeppelin/contracts/security/Pausable.sol` → `@openzeppelin/contracts/utils/Pausable.sol`
- `@openzeppelin/contracts/security/ReentrancyGuard.sol` → `@openzeppelin/contracts/utils/ReentrancyGuard.sol`

Import replacement alone is not sufficient. A controlled migration must review Ownable constructor behavior, AccessControl behavior, SafeERC20 behavior, ERC20 assumptions, Pausable/ReentrancyGuard behavior, proxy/initializer assumptions, and all tests/fuzz/invariants.

The current OpenZeppelin 4.9.6 baseline remains in place for deterministic authorization evidence unless vulnerability triage identifies a used-code-path blocker.
