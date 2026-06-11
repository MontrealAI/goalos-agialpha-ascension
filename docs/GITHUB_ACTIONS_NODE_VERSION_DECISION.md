# GitHub Actions Node Version Decision

Decision: **Use current v5 Actions where safe; keep contract CI on Node 20 for Hardhat 2 baseline**.

## Context

GitHub Actions displayed Node.js 20 action-runtime warnings in screenshots. This PR updates first-party Actions to v5 where safe (`actions/checkout`, `actions/setup-node`, and `actions/upload-artifact`) while keeping the project runtime at Node 20 for the current Hardhat 2 baseline.

## Policy

- Mainnet gate workflows are Python/read-only and do not install npm dependencies.
- Contract compile/test/audit workflows use `npm ci` from the committed lockfile.
- Hardhat 3 is deferred; if adopted later, the controlled Hardhat 3 migration must revisit Node 22.13+ requirements and workflow runtime compatibility.
- Ethereum Mainnet deployment remains unauthorized.
