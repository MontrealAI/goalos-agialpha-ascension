#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/echidna.txt"; JSON="$AUDIT_REPORT_DIR/echidna.json"
CMD="echidna . --config configs/echidna.yaml"
if ! command -v echidna >/dev/null 2>&1; then write_pending "Echidna" "$CMD" "echidna executable is not installed; install via crytic/echidna Docker or release binary" "$JSON" "$TXT"; exit 0; fi
echidna . --config configs/echidna.yaml > "$TXT" 2>&1; cp "$TXT" "$JSON" || true
