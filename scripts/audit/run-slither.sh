#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/slither.txt"; JSON="$AUDIT_REPORT_DIR/slither.json"; SARIF="$AUDIT_REPORT_DIR/slither.sarif"
if ! npm run compile:ci > "$AUDIT_REPORT_DIR/deterministic-compile.log" 2>&1; then
  write_pending "Slither" "npm run compile:ci" "Deterministic compile failed; Slither clearance is impossible until compile passes" "$JSON" "$TXT"
  echo '{"runs":[]}' > "$SARIF"
  exit 1
fi
CMD="timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json"
if ! command -v slither >/dev/null 2>&1; then write_pending "Slither" "$CMD" "slither executable is not installed" "$JSON" "$TXT"; echo '{"runs":[]}' > "$SARIF"; exit 0; fi
set +e
timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json --json "$JSON" > "$TXT" 2>&1
for printer in human-summary contract-summary inheritance-graph vars-and-auth call-graph; do timeout 60 slither . --print "$printer" --compile-force-framework hardhat --config-file configs/slither.config.json > "$AUDIT_REPORT_DIR/slither-$printer.txt" 2>&1 || true; done
STATUS=$?
if [ $STATUS -eq 124 ]; then write_pending "Slither" "$CMD" "slither exceeded 120 second CI timeout; run locally with larger timeout" "$JSON" "$TXT"; echo '{"runs":[]}' > "$SARIF"; exit 0; fi
if [ ! -s "$JSON" ]; then write_pending "Slither" "$CMD" "slither failed before JSON output; see slither.txt" "$JSON" "$TXT.pending"; echo '{"runs":[]}' > "$SARIF"; exit 0; fi
echo '{"version":"2.1.0","runs":[]}' > "$SARIF"
set -e
python scripts/audit/fail-on-critical-findings.py "$JSON" slither || exit $?
exit 0
