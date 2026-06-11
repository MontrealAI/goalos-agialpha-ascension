#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
if command -v shellcheck >/dev/null 2>&1; then
  find scripts -name '*.sh' -print0 | xargs -0 shellcheck > "$AUDIT_REPORT_DIR/shellcheck.txt" 2>&1 || true
else
  write_pending "shellcheck" "shellcheck scripts/**/*.sh" "shellcheck executable is not installed in this environment" "$AUDIT_REPORT_DIR/shellcheck.json" "$AUDIT_REPORT_DIR/shellcheck.txt"
fi
