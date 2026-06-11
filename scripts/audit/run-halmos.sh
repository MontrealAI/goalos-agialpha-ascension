#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
if command -v halmos >/dev/null 2>&1; then
  halmos > "$AUDIT_REPORT_DIR/halmos.txt" 2>&1 || true
else
  write_pending "halmos" "halmos" "halmos executable is not installed in this environment" "$AUDIT_REPORT_DIR/halmos.json" "$AUDIT_REPORT_DIR/halmos.txt"
fi
