#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
if command -v osv-scanner >/dev/null 2>&1; then
  osv-scanner --format json --lockfile package-lock.json > "$AUDIT_REPORT_DIR/osv-scanner.json" 2> "$AUDIT_REPORT_DIR/osv-scanner.txt" || true
else
  write_pending "osv-scanner" "osv-scanner --lockfile package-lock.json" "osv-scanner executable is not installed in this environment" "$AUDIT_REPORT_DIR/osv-scanner.json" "$AUDIT_REPORT_DIR/osv-scanner.txt"
fi
