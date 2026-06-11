#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
AUDIT_REPORT_DIR="${AUDIT_REPORT_DIR:-audit/reports/$(date -u +%Y-%m-%d-%H%M)}"
mkdir -p "$AUDIT_REPORT_DIR"
echo "$AUDIT_REPORT_DIR" > audit/reports/latest.txt
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
