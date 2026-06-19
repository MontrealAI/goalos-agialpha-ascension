#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
AUDIT_REPORTS_ROOT="${AUDIT_REPORTS_ROOT:-audit/reports}"
AUDIT_RUN_FILE="${AUDIT_RUN_FILE:-$AUDIT_REPORTS_ROOT/current-run.txt}"
mkdir -p "$AUDIT_REPORTS_ROOT"

if [ "${RESET_AUDIT_REPORT_DIR:-}" = "true" ]; then
  rm -f "$AUDIT_RUN_FILE"
fi

if [ -n "${AUDIT_REPORT_DIR:-}" ]; then
  :
elif [ -f "$AUDIT_RUN_FILE" ] && [ -s "$AUDIT_RUN_FILE" ]; then
  AUDIT_REPORT_DIR="$(cat "$AUDIT_RUN_FILE")"
else
  AUDIT_REPORT_DIR="$AUDIT_REPORTS_ROOT/$(date -u +%Y-%m-%d-%H%M%S)"
  echo "$AUDIT_REPORT_DIR" > "$AUDIT_RUN_FILE"
fi

export AUDIT_REPORT_DIR
mkdir -p "$AUDIT_REPORT_DIR"
echo "$AUDIT_REPORT_DIR" > "$AUDIT_REPORTS_ROOT/latest.txt"
write_pending() {
  local tool="$1" cmd="$2" reason="$3" json="$4" txt="$5"
  cat > "$json" <<JSON
{"tool":"$tool","status":"PENDING_ENVIRONMENT_BLOCKED","command":"$cmd","reason":"$reason","blocks_mainnet":true,"generated_at":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
JSON
  cat > "$txt" <<TXT
$tool: PENDING_ENVIRONMENT_BLOCKED
Command attempted: $cmd
Reason: $reason
Environment: $(uname -a)
Blocks mainnet: true until run/triaged by qualified reviewer.
TXT
}
