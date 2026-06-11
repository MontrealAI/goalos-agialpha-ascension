#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/medusa.txt"; JSON="$AUDIT_REPORT_DIR/medusa.json"
CMD="medusa fuzz --config configs/medusa.json"
if ! command -v medusa >/dev/null 2>&1; then write_pending "Medusa" "$CMD" "medusa executable is not installed; run locally with Trail of Bits Medusa Docker/release" "$JSON" "$TXT"; exit 0; fi
medusa fuzz --config configs/medusa.json > "$TXT" 2>&1; cp "$TXT" "$JSON" || true
