# Dependency Threat Model

Dependency risk categories:

- **Production bytecode risk:** OpenZeppelin contracts, token primitives, access control, SafeERC20, ERC721, pausing, and reentrancy guards can alter deployed bytecode or security behavior.
- **Compiler/toolchain risk:** Hardhat, TypeScript, ts-node, TypeChain, and plugins can alter compilation, generated artifacts, tests, deployments, and CI.
- **Audit-tool risk:** Slither, Echidna, Mythril, Medusa, Foundry, Semgrep, and npm audit can fail open if missing or misconfigured; environment-blocked tools remain documented release blockers until run or accepted.
- **Supply-chain risk:** npm install scripts, transitive dependency advisories, compromised packages, and lockfile drift can affect reproducibility.

Controls:

- Major upgrades require isolated triage and migration reports.
- Production dependency upgrades require compile/test/audit review and deployed-bytecode impact assessment.
- DevDependency upgrades require CI/deploy/test compatibility review.
- `npm audit` findings are classified by production/dev relevance; devDependency advisories are not automatically on-chain mainnet blockers but may block release tooling.
- Mainnet cannot be authorized by dependency updates alone.
