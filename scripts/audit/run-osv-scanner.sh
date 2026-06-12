#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/osv-scanner.txt"
JSON="$AUDIT_REPORT_DIR/osv-scanner.json"
: > "$TXT"

if ! command -v osv-scanner >/dev/null 2>&1; then
  if command -v go >/dev/null 2>&1; then
    set +e
    go install github.com/google/osv-scanner/cmd/osv-scanner@latest >> "$TXT" 2>&1
    INSTALL_STATUS=$?
    set -e
    export PATH="$(go env GOPATH)/bin:$PATH"
  else
    INSTALL_STATUS=127
  fi
  if [ "${INSTALL_STATUS:-0}" -ne 0 ] || ! command -v osv-scanner >/dev/null 2>&1; then
    python - "$TXT" "$JSON" "${INSTALL_STATUS:-127}" <<'PY'
import json, pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text(errors="ignore")
status = int(sys.argv[3])
out = {
    "tool": "osv-scanner",
    "status": "FAILED_TOOL_UNAVAILABLE",
    "installExitStatus": status,
    "findingCount": 0,
    "critical_high_unresolved": 1,
    "error": "osv-scanner was not available and automatic installation failed",
    "localDockerCommand": "docker run --rm -v $PWD:/src ghcr.io/google/osv-scanner:latest --lockfile /src/package-lock.json",
    "output": text[:4000],
}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "findingCount", "critical_high_unresolved"]}, indent=2))
sys.exit(1)
PY
  fi
fi

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
triage_path = pathlib.Path("audit/OSV_AUDIT_TRIAGE.json")
accepted_ids = set()
triage_status = "MISSING"
if triage_path.exists():
    try:
        triage_data = json.loads(triage_path.read_text())
        triage_status = str(triage_data.get("status", "UNKNOWN"))
        if triage_status in {"TRIAGED_ACCEPTED_DEV_TOOLING_ONLY", "TRIAGED_ACCEPTED_DEV_ONLY"}:
            accepted_ids = set(map(str, triage_data.get("acceptedIds", [])))
    except Exception as exc:
        triage_status = f"PARSE_ERROR: {exc}"

def vuln_id(v):
    return str(v.get("id") or v.get("ghsa_id") or v.get("cve") or "UNKNOWN")
untriaged = [v for v in vulns if vuln_id(v) not in accepted_ids]
accepted = [v for v in vulns if vuln_id(v) in accepted_ids]
critical = len(untriaged) + (1 if scanner_error or parse_error else 0)
if scanner_error or parse_error:
    state = "FAILED_SCANNER_ERROR"
elif untriaged:
    state = "FAILED_UNTRIAGED_VULNERABILITIES"
elif findings := finding_count:
    state = "COMPLETED_TRIAGED"
else:
    state = "COMPLETED"
out = {
    "tool": "osv-scanner",
    "status": state,
    "scannerExitStatus": status,
    "rawResults": data,
    "findingCount": finding_count,
    "acceptedFindingCount": len(accepted),
    "untriagedFindingCount": len(untriaged),
    "untriagedIds": sorted({vuln_id(v) for v in untriaged}),
    "critical_high_unresolved": critical,
    "triage": "OSV scanner executed; listed dev/tooling findings are accepted only via audit/OSV_AUDIT_TRIAGE.json. Missing scanner, scanner errors, or unlisted IDs block Tier 1 clearance.",
    "triageStatus": triage_status,
    "triagePath": str(triage_path),
    "stderr": stderr_text[:4000],
}
if parse_error:
    out["parse_error"] = parse_error
pathlib.Path(json_path).write_text(json.dumps(out, indent=2) + "\n")
summary = [
    f"osv-scanner status={state} scannerExitStatus={status}",
    f"findingCount={finding_count} accepted={len(accepted)} untriaged={len(untriaged)} critical_high_unresolved={critical}",
]
if stderr_text.strip():
    summary += ["", "stderr:", stderr_text]
pathlib.Path(txt_path).write_text("\n".join(summary) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "findingCount", "critical_high_unresolved"]}, indent=2))
if critical:
    sys.exit(1)
PY
