#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
if command -v actionlint >/dev/null 2>&1; then
  actionlint > "$AUDIT_REPORT_DIR/actionlint.txt" 2>&1 || true
else
  write_pending "actionlint" "actionlint" "actionlint executable is not installed in this environment" "$AUDIT_REPORT_DIR/actionlint.json" "$AUDIT_REPORT_DIR/actionlint.txt"
fi
