#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/semgrep.txt"; JSON="$AUDIT_REPORT_DIR/semgrep.json"
CMD="semgrep --config configs/semgrep.yml --json --output $JSON ."
if command -v semgrep >/dev/null 2>&1; then
  timeout 120 semgrep --config configs/semgrep.yml --json --output "$JSON" . > "$TXT" 2>&1 || true
elif command -v npx >/dev/null 2>&1; then
  timeout 120 npx --yes semgrep@latest --config configs/semgrep.yml --json --output "$JSON" . > "$TXT" 2>&1 || true
else
  write_pending "Semgrep" "$CMD" "semgrep/npx executable is not installed" "$JSON" "$TXT"; exit 0
fi
if [ ! -s "$JSON" ]; then
  write_pending "Semgrep" "$CMD" "semgrep did not produce JSON output; see semgrep.txt" "$JSON" "$TXT.pending"
fi
exit 0
