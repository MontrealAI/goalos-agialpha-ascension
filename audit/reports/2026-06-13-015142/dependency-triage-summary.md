# npm audit summary

Raw status: npm audit returned findings; this is dependency risk input, not automatic mainnet authorization.

## Vulnerability counts
- info: 0
- low: 18
- moderate: 22
- high: 4
- critical: 0
- total: 44

## Policy
- Production dependency critical/high advisories affecting used deployed code paths are mainnet blockers until remediated or accepted.
- DevDependency advisories are CI/release blockers when they affect compiler, test, deployment, or artifact integrity, but are not automatically on-chain mainnet blockers.

