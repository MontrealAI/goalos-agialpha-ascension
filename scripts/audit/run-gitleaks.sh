#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-git --source . --config .gitleaks.toml --report-format json --report-path "$AUDIT_REPORT_DIR/gitleaks.json" > "$AUDIT_REPORT_DIR/gitleaks.txt" 2>&1 || true
else
  write_pending "gitleaks" "gitleaks detect --no-git --source ." "gitleaks executable is not installed in this environment" "$AUDIT_REPORT_DIR/gitleaks.json" "$AUDIT_REPORT_DIR/gitleaks.txt"
fi
