# OSV Audit Triage

Status: **TRIAGED_ACCEPTED_DEV_TOOLING_ONLY**

The OSV scanner must run for Tier 1 clearance. If the scanner is unavailable or exits with an execution/configuration error, the OSV gate is blocked.

The accepted OSV IDs in `audit/OSV_AUDIT_TRIAGE.json` are transitive npm development/tooling findings. They are not Solidity source, are not linked into deployed bytecode, are not served by a repository web service, and are not Ethereum Mainnet runtime dependencies. Any new OSV ID not listed in the JSON triage remains a Tier 1 blocker until fixed or explicitly triaged.
