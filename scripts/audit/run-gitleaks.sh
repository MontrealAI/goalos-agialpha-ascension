#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/gitleaks.txt"
JSON="$AUDIT_REPORT_DIR/gitleaks.json"
TMP="$AUDIT_REPORT_DIR/gitleaks.json.tmp"
SCAN_ROOT=""
: > "$TXT"

prepare_scan_source() {
  SCAN_ROOT="$(mktemp -d)"
  python - "$SCAN_ROOT" <<'PY'
import pathlib, shutil, subprocess, sys
root = pathlib.Path('.').resolve()
out = pathlib.Path(sys.argv[1]).resolve()
exclude_prefixes = (
    'audit/reports/',
    'artifacts/',
    'cache/',
    'coverage/',
    'direct-solc-output/',
    'node_modules/',
    'typechain-types/',
)
exclude_parts = {'.git', '.private', '__pycache__'}

def include(rel: str) -> bool:
    parts = pathlib.PurePosixPath(rel).parts
    if any(part in exclude_parts for part in parts):
        return False
    if rel.endswith('.pyc'):
        return False
    return not rel.startswith(exclude_prefixes)

try:
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=root, text=True, stderr=subprocess.DEVNULL).splitlines()
except Exception:
    tracked = [p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()]

for rel in tracked:
    if not include(rel):
        continue
    src = root / rel
    if not src.is_file():
        continue
    dst = out / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
PY
}

cleanup_scan_source() {
  if [ -n "${SCAN_ROOT:-}" ] && [ -d "$SCAN_ROOT" ]; then
    rm -rf "$SCAN_ROOT"
  fi
}
trap cleanup_scan_source EXIT

if ! command -v gitleaks >/dev/null 2>&1; then
  set +e
  go install github.com/zricethezav/gitleaks/v8@v8.24.2 >> "$TXT" 2>&1
  INSTALL_STATUS=$?
  set -e
  if [ "$INSTALL_STATUS" -ne 0 ] || ! command -v gitleaks >/dev/null 2>&1; then
    python - "$TXT" "$JSON" "$INSTALL_STATUS" <<'PY'
import json, pathlib, re, sys
from scripts.audit.audit_model import stable_fingerprint, write_normalized
text_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
install_status = int(sys.argv[3])
install_output = text_path.read_text(errors="ignore")
exclude_dirs = {".git", "node_modules", "artifacts", "cache", "direct-solc-output"}
exclude_prefixes = ("audit/reports/", ".private.example/", "artifacts/", "cache/", "coverage/", "direct-solc-output/", "node_modules/", "typechain-types/")
secret_name = re.compile(r"(?i)(private[_-]?key|deployer[_-]?key|mnemonic|seed[_-]?phrase|etherscan[_-]?api[_-]?key|rpc[_-]?url)")
assignment = re.compile(r"(?i)([A-Z0-9_]*(?:PRIVATE_KEY|DEPLOYER_KEY|MNEMONIC|SEED_PHRASE|ETHERSCAN_API_KEY|RPC_URL)[A-Z0-9_]*)\s*[:=]\s*['\"]?([^'\"\s#]+)")
placeholder = re.compile(r"(?i)^(|0x0+|0x?DO_NOT_COMMIT.*|DO_NOT_COMMIT.*|PRIVATE_LOCAL.*|TYPE_CONFIRMATION.*|first_env\(.*\)|<.*>|\$\{.*\}|.*\{token\}.*|your[-_].*|example|placeholder|redacted|changeme|dummy|localhost|http://127\.0\.0\.1.*|http://localhost.*)$")
findings = []
try:
    candidates = [pathlib.Path(line) for line in __import__('subprocess').check_output(['git', 'ls-files'], text=True, stderr=__import__('subprocess').DEVNULL).splitlines()]
except Exception:
    candidates = [p for p in pathlib.Path('.').rglob('*') if p.is_file()]
for path in candidates:
    rel = path.as_posix()
    if not path.is_file() or any(part in exclude_dirs for part in path.parts) or rel.startswith(exclude_prefixes):
        continue
    try:
        data = path.read_text(errors='ignore')
    except Exception:
        continue
    if re.search(r'(?m)^-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----$', data):
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
        if value.startswith('|') or '|' in value:
            continue
        # Documentation and scripts may mention variable names; only concrete runtime-looking values fail.
        if len(value) >= 24 and not value.startswith(('process.env', 'env.', 'secrets.', 'vars.')):
            findings.append({'file': rel, 'line': line_no, 'rule': 'secret-assignment', 'key': match.group(1)})
critical = len(findings)
state = 'FAILED' if findings else 'COMPLETED'
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
normalized=[]
for i, finding in enumerate(findings):
    file = str(finding.get('file') or finding.get('File') or finding.get('path') or finding.get('Path') or text_path)
    line = finding.get('line') or finding.get('StartLine')
    normalized.append({'fingerprint':stable_fingerprint('gitleaks', str(finding.get('rule') or finding.get('RuleID') or 'GITLEAKS_FINDING'), 'secrets', '', file, file, line), 'id':str(finding.get('rule') or finding.get('RuleID') or 'GITLEAKS_FINDING'), 'tool':'gitleaks', 'severity':'high', 'status':'unresolved', 'title':'Potential secret detected', 'packageOrContract':'secrets', 'installedVersion':'', 'fixedVersion':'', 'dependencyPath':'', 'file':file, 'line':line, 'description':str(finding)[:1000], 'evidence':[str(text_path)], 'triageRef':''})
obj = write_normalized(out_path, 'gitleaks', 'internal fallback secret scan', install_status, normalized, [str(text_path)], state)
obj['mode'] = 'internal-fallback-secret-scan'
obj['findingCount'] = len(findings)
obj['note'] = 'gitleaks unavailable; deterministic internal secret scanner executed as CI fallback'
out_path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
summary = {k: obj[k] for k in ['tool', 'status', 'findingCount', 'criticalHighUnresolved']}
if findings:
    summary['findingFiles'] = sorted({str(f.get('file') or f.get('File') or f.get('path') or f.get('Path') or 'unknown') for f in findings})[:20]
print(json.dumps(summary, indent=2))
sys.exit(1 if critical else 0)
PY
    exit $?
  fi
  export PATH="$(go env GOPATH)/bin:$PATH"
fi

prepare_scan_source
set +e
gitleaks detect --no-git --source "$SCAN_ROOT" --config .gitleaks.toml --report-format json --report-path "$TMP" >> "$TXT" 2>&1
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
summary = {k: out[k] for k in ["tool", "status", "findingCount", "critical_high_unresolved"]}
if findings:
    summary["findingFiles"] = sorted({str((f.get("File") or f.get("file") or f.get("Path") or f.get("path") or "unknown")) for f in findings})[:20]
print(json.dumps(summary, indent=2))
if critical:
    sys.exit(1)
PY
python - "$JSON" "$TXT" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import stable_fingerprint, write_normalized
path=pathlib.Path(sys.argv[1]); txt=pathlib.Path(sys.argv[2])
try: legacy=json.loads(path.read_text())
except Exception as exc:
    legacy={'tool':'gitleaks','status':'MALFORMED','critical_high_unresolved':1,'findings':[{'error':str(exc)}]}
raw_findings=legacy.get('findings',[]) if isinstance(legacy.get('findings',[]),list) else []
critical=int(legacy.get('critical_high_unresolved', len(raw_findings)) or 0)
findings=[]
for i,f in enumerate(raw_findings or [{}]*critical):
    file=str(f.get('File') or f.get('file') or f.get('Path') or f.get('path') or txt)
    line=f.get('StartLine') or f.get('line')
    findings.append({'fingerprint':stable_fingerprint('gitleaks',str(f.get('RuleID') or f.get('rule') or 'GITLEAKS_FINDING'),'secrets','',file,file,line),'id':str(f.get('RuleID') or f.get('rule') or 'GITLEAKS_FINDING'),'tool':'gitleaks','severity':'high','status':'unresolved','title':'Potential secret detected','packageOrContract':'secrets','installedVersion':'','fixedVersion':'','dependencyPath':'','file':file,'line':line,'description':str(f)[:1000],'evidence':[str(txt)],'triageRef':''})
state='FAILED' if findings else ('FAILED_SCANNER_ERROR' if 'ERROR' in str(legacy.get('status','')) else 'COMPLETED')
obj=write_normalized(path,'gitleaks','gitleaks detect --no-git',int(legacy.get('scannerExitStatus',legacy.get('installExitStatus',0)) or 0),findings,[str(txt)],state)
obj['findingCount']=len(raw_findings)
path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
PY
