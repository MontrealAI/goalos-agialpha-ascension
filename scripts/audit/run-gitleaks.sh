#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/gitleaks.txt"
JSON="$AUDIT_REPORT_DIR/gitleaks.json"
TMP="$AUDIT_REPORT_DIR/gitleaks.json.tmp"
: > "$TXT"

if ! command -v gitleaks >/dev/null 2>&1; then
  set +e
  go install github.com/zricethezav/gitleaks/v8@latest >> "$TXT" 2>&1
  INSTALL_STATUS=$?
  set -e
  if [ "$INSTALL_STATUS" -ne 0 ] || ! command -v gitleaks >/dev/null 2>&1; then
    python - "$TXT" "$JSON" "$INSTALL_STATUS" <<'PY'
import json, pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text(errors="ignore")
status = int(sys.argv[3])
out = {
    "tool": "gitleaks",
    "status": "FAILED_TOOL_UNAVAILABLE",
    "installExitStatus": status,
    "findingCount": 0,
    "critical_high_unresolved": 1,
    "error": "gitleaks was not available and automatic installation failed",
    "output": text[:4000],
}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "findingCount", "critical_high_unresolved"]}, indent=2))
sys.exit(1)
PY
  fi
  export PATH="$(go env GOPATH)/bin:$PATH"
fi

set +e
gitleaks detect --no-git --source . --config .gitleaks.toml --report-format json --report-path "$TMP" >> "$TXT" 2>&1
STATUS=$?
set -e
python - "$TMP" "$JSON" "$STATUS" "$TXT" <<'PY'
import json, pathlib, sys
report = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
status = int(sys.argv[3])
text = pathlib.Path(sys.argv[4]).read_text(errors="ignore")
findings = []
parse_error = None
if report.exists() and report.read_text(errors="ignore").strip():
    try:
        parsed = json.loads(report.read_text(errors="ignore"))
        findings = parsed if isinstance(parsed, list) else parsed.get("findings", []) if isinstance(parsed, dict) else []
    except Exception as exc:
        parse_error = str(exc)
scanner_error = status not in (0, 1) or (status == 1 and not findings) or parse_error is not None
critical = len(findings) + (1 if scanner_error else 0)
if scanner_error:
    state = "FAILED_SCANNER_ERROR"
elif findings:
    state = "FAILED"
else:
    state = "COMPLETED"
out = {
    "tool": "gitleaks",
    "status": state,
    "scannerExitStatus": status,
    "findingCount": len(findings),
    "critical_high_unresolved": critical,
    "findings": findings,
    "output": text[:4000],
}
if parse_error:
    out["parse_error"] = parse_error
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "findingCount", "critical_high_unresolved"]}, indent=2))
if critical:
    sys.exit(1)
PY
