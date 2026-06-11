# Remediation Log

| Date | Finding | Severity | Action | Status | Reviewer |
|---|---|---:|---|---|---|
| 2026-06-11 | Audit toolchain and evidence gates added | Info | Added scripts/configs/docs/CI and mainnet decision generation | Complete | Codex |
| 2026-06-11 | Slither arbitrary-send-erc20 on TreasuryRouter.routeFrom | High | Restricted `from` to `msg.sender` and added nonzero token/amount/reason checks | Complete | Codex |
