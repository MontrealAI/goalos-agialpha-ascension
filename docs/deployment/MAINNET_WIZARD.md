# GoalOS Mainnet deployment wizard

Install: `npm ci`
Start:   `npm run deploy`

The wizard guides Compile → Tests/security → Doctor → Plan/cost → Fork rehearsal → Final confirmation → Deploy → Verify automatically → Initiate ownership transfer → Wait exact delay → Connect Ledger → Accept ownership one transaction at a time → Remove temporary authority → Sweep remaining free deployer assets → Final readback → Generate report.

Mainnet broadcast is local-only. CI and Codex runs must not broadcast Ethereum Mainnet transactions. Operational completion is blocked until live chain-1 verification, Ledger acceptance, role cleanup, temporary-wallet sweep, monitoring, and bounded canary evidence are complete.
