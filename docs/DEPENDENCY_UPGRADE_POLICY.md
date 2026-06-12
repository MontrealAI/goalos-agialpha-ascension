# Dependency Upgrade Policy

Do not mix Hardhat 3 with the Hardhat 2 toolbox stack. Do not migrate OpenZeppelin 4 to 5 without controlled compile/test/security validation. Do not run `npm audit fix --force` unless reviewed and proven safe. High/critical production-impacting findings must be fixed or triaged as not reachable; dev-only findings require rationale.
