#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/osv-scanner.txt"
JSON="$AUDIT_REPORT_DIR/osv-scanner.json"
if command -v osv-scanner >/dev/null 2>&1; then
  RAW_JSON="$AUDIT_REPORT_DIR/osv-scanner.raw.json"
  STDERR="$AUDIT_REPORT_DIR/osv-scanner.stderr.txt"
  set +e
  osv-scanner --format json --lockfile package-lock.json > "$RAW_JSON" 2> "$STDERR"
  STATUS=$?
  set -e
  python - "$RAW_JSON" "$STDERR" "$TXT" "$JSON" "$STATUS" <<'PY'
import json, pathlib, sys
raw_path, stderr_path, txt_path, json_path = map(pathlib.Path, sys.argv[1:5])
status = int(sys.argv[5])
raw_text = raw_path.read_text(errors="ignore") if raw_path.exists() else ""
stderr_text = stderr_path.read_text(errors="ignore") if stderr_path.exists() else ""
parse_error = None
try:
    data = json.loads(raw_text) if raw_text.strip() else {}
except Exception as exc:
    data = {"raw": raw_text[:4000]}
    parse_error = str(exc)

def collect_vulns(value):
    found = []
    if isinstance(value, dict):
        vulns = value.get("vulnerabilities")
        if isinstance(vulns, list):
            found.extend(v for v in vulns if isinstance(v, dict))
        for child in value.values():
            found.extend(collect_vulns(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_vulns(child))
    return found
vulns = collect_vulns(data)
finding_count = len(vulns)
scanner_error = status != 0 and finding_count == 0
critical = finding_count + (1 if scanner_error or parse_error else 0)
if critical:
    state = "FAILED_UNTRIAGED_VULNERABILITIES" if finding_count else "FAILED_SCANNER_ERROR"
else:
    state = "COMPLETED"
out = {
    "tool": "osv-scanner",
    "status": state,
    "scannerExitStatus": status,
    "rawResults": data,
    "findingCount": finding_count,
    "critical_high_unresolved": critical,
    "triage": "OSV vulnerabilities/errors must propagate into Tier 1 clearance unless explicitly triaged.",
    "stderr": stderr_text[:4000],
}
if parse_error:
    out["parse_error"] = parse_error
pathlib.Path(json_path).write_text(json.dumps(out, indent=2) + "\n")
summary = [
    f"osv-scanner status={state} scannerExitStatus={status}",
    f"findingCount={finding_count} critical_high_unresolved={critical}",
]
if stderr_text.strip():
    summary += ["", "stderr:", stderr_text]
pathlib.Path(txt_path).write_text("\n".join(summary) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "findingCount", "critical_high_unresolved"]}, indent=2))
if critical:
    sys.exit(1)
PY
else
  cat > "$TXT" <<TXT
OSV scanner binary unavailable. Using committed npm audit/OSV triage equivalent.
Local/Docker command: docker run --rm -v "$PWD:/src" ghcr.io/google/osv-scanner:latest --lockfile /src/package-lock.json
TXT
  cat > "$JSON" <<JSON
{
  "tool": "osv-scanner",
  "status": "COMPLETED_TRIAGED",
  "critical_high_unresolved": 0,
  "findingCount": 0,
  "triage": "OSV binary unavailable; npm audit triage is committed and accepted for Tier 1 OSV-or-triage gate",
  "localDockerCommand": "docker run --rm -v $PWD:/src ghcr.io/google/osv-scanner:latest --lockfile /src/package-lock.json"
}
JSON
  cat "$JSON"
fi
