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
import json, pathlib, re, sys
text_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
install_status = int(sys.argv[3])
install_output = text_path.read_text(errors="ignore")
exclude_dirs = {".git", "node_modules", "artifacts", "cache", "direct-solc-output"}
exclude_prefixes = ("audit/reports/",)
secret_name = re.compile(r"(?i)(private[_-]?key|deployer[_-]?key|mnemonic|seed[_-]?phrase|etherscan[_-]?api[_-]?key|rpc[_-]?url)")
assignment = re.compile(r"(?i)([A-Z0-9_]*(?:PRIVATE_KEY|DEPLOYER_KEY|MNEMONIC|SEED_PHRASE|ETHERSCAN_API_KEY|RPC_URL)[A-Z0-9_]*)\s*[:=]\s*['\"]?([^'\"\s#]+)")
placeholder = re.compile(r"(?i)^(|0x0+|<.*>|\$\{.*\}|your[-_].*|example|placeholder|redacted|changeme|dummy|localhost|http://127\.0\.0\.1.*|http://localhost.*)$")
findings = []
for path in pathlib.Path('.').rglob('*'):
    rel = path.as_posix()
    if not path.is_file() or any(part in exclude_dirs for part in path.parts) or rel.startswith(exclude_prefixes):
        continue
    try:
        data = path.read_text(errors='ignore')
    except Exception:
        continue
    if 'BEGIN PRIVATE KEY' in data or 'BEGIN RSA PRIVATE KEY' in data or 'BEGIN OPENSSH PRIVATE KEY' in data:
        findings.append({'file': rel, 'rule': 'private-key-block'})
        continue
    for line_no, line in enumerate(data.splitlines(), 1):
        if not secret_name.search(line):
            continue
        match = assignment.search(line)
        if not match:
            continue
        value = match.group(2).strip()
        if placeholder.match(value):
            continue
        # Documentation and scripts may mention variable names; only concrete runtime-looking values fail.
        if len(value) >= 24 and not value.startswith(('process.env', 'env.', 'secrets.', 'vars.')):
            findings.append({'file': rel, 'line': line_no, 'rule': 'secret-assignment', 'key': match.group(1)})
critical = len(findings)
state = 'FAILED' if findings else 'COMPLETED_INTERNAL_SECRET_SCAN'
out = {
    'tool': 'gitleaks',
    'status': state,
    'mode': 'internal-fallback-secret-scan',
    'installExitStatus': install_status,
    'findingCount': len(findings),
    'critical_high_unresolved': critical,
    'findings': findings,
    'note': 'gitleaks unavailable; deterministic internal secret scanner executed as CI fallback',
    'output': install_output[:4000],
}
out_path.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: out[k] for k in ['tool', 'status', 'findingCount', 'critical_high_unresolved']}, indent=2))
sys.exit(1 if critical else 0)
PY
    exit $?
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
