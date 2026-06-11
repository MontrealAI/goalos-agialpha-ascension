#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
cat > "$AUDIT_REPORT_DIR/smtchecker.txt" <<TXT
solc SMTChecker: PENDING_ENVIRONMENT_BLOCKED
Command attempted: selected solc --model-checker-engine checks
Reason: SMTChecker needs a pinned solc binary and solver configuration for selected properties; Hardhat compile remains the active compiler gate.
Environment: $(uname -a)
Blocks technical mainnet readiness until configured/run or internally accepted.
TXT
cat > "$AUDIT_REPORT_DIR/smtchecker.json" <<JSON
{"tool":"solc-smtchecker","status":"PENDING_ENVIRONMENT_BLOCKED","blocks_mainnet":true}
JSON
