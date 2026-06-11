#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/foundry-test.log"; JSON="$AUDIT_REPORT_DIR/foundry.json"
CMD="forge build && forge test && forge test -vvv"
if ! command -v forge >/dev/null 2>&1; then write_pending "Foundry" "$CMD" "forge executable is not installed; install Foundry with foundryup" "$JSON" "$TXT"; exit 0; fi
forge build > "$TXT" 2>&1 && forge test >> "$TXT" 2>&1 && forge test -vvv >> "$TXT" 2>&1
