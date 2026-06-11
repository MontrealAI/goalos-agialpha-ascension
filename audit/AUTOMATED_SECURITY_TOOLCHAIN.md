# Automated Security Toolchain

This repository uses overlapping automated and internal security-review signals rather than a planned external audit gate. The active gate model requires automated security/toolchain clearance, internal security review, Sepolia rehearsal evidence, AGIALPHA token verification, and founder deployment approval.

Required tools include Hardhat compile/tests, Slither, Echidna, Foundry/Forge, Mythril, Medusa, Halmos where available, solc SMTChecker where configured, Semgrep, Solhint, npm audit, OSV Scanner, actionlint, shellcheck, and gitleaks.

Environment-blocked tools are recorded as technical mainnet-readiness blockers until they are run or explicitly accepted by internal security/founder review.
