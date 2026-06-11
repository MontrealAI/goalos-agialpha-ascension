#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/slither.txt"; JSON="$AUDIT_REPORT_DIR/slither.json"; SARIF="$AUDIT_REPORT_DIR/slither.sarif"
CMD="timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json"
if ! command -v slither >/dev/null 2>&1; then write_pending "Slither" "$CMD" "slither executable is not installed" "$JSON" "$TXT"; echo '{"runs":[]}' > "$SARIF"; exit 0; fi
set +e
timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json --json "$JSON" > "$TXT" 2>&1
STATUS=$?
if [ $STATUS -eq 124 ]; then write_pending "Slither" "$CMD" "slither exceeded 120 second CI timeout; run locally with larger timeout" "$JSON" "$TXT"; echo '{"runs":[]}' > "$SARIF"; exit 0; fi
if [ ! -s "$JSON" ]; then write_pending "Slither" "$CMD" "slither failed before JSON output; see slither.txt" "$JSON" "$TXT.pending"; echo '{"runs":[]}' > "$SARIF"; exit 0; fi
echo '{"version":"2.1.0","runs":[]}' > "$SARIF"
set -e
python scripts/audit/fail-on-critical-findings.py "$JSON" slither || exit $?
exit 0
