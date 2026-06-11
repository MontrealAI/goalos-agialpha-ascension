#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
if [ -f .solhint.json ]; then
  npx --yes solhint@latest "contracts/**/*.sol" > "$AUDIT_REPORT_DIR/solhint.txt" 2>&1 || true
else
  write_pending "solhint" "npx solhint contracts/**/*.sol" ".solhint.json is missing" "$AUDIT_REPORT_DIR/solhint.json" "$AUDIT_REPORT_DIR/solhint.txt"
fi
