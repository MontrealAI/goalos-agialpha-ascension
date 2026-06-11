#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/mythril.txt"; JSON="$AUDIT_REPORT_DIR/mythril.json"
CMD="myth analyze contracts/registry/LaunchGateRegistry.sol --solv 0.8.24 -o json --execution-timeout 120"
MYTH=$(command -v myth || command -v mythril || true)
if [ -z "$MYTH" ]; then write_pending "Mythril" "$CMD" "myth/mythril executable is not installed or failed to install" "$JSON" "$TXT"; exit 0; fi
set +e
"$MYTH" analyze contracts/registry/LaunchGateRegistry.sol --solv 0.8.24 -o json --execution-timeout 120 > "$JSON" 2> "$TXT"
STATUS=$?
cat "$JSON" >> "$TXT"
exit $STATUS
