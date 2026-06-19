#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/actionlint.txt"; JSON="$AUDIT_REPORT_DIR/actionlint.json"
: > "$TXT"
# Always install and run a fresh actionlint binary instead of relying on a
# potentially stale preinstalled runner binary. PR #44 hit a CI-only
# actionlint failure while local latest actionlint passed; pinning our own
# toolchain keeps the audit deterministic and makes failures reproducible.
if ! command -v go >/dev/null 2>&1; then
  echo "go is required to install actionlint for deterministic workflow auditing" | tee -a "$TXT"
  python - "$TXT" "$JSON" <<'PY'
import json,pathlib,sys
from scripts.audit.audit_model import write_normalized
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore')
out_path=pathlib.Path(sys.argv[2])
f={'fingerprint':'actionlint-go-unavailable','id':'ACTIONLINT_GO_UNAVAILABLE','tool':'actionlint','severity':'high','status':'unresolved','title':'go unavailable for actionlint','packageOrContract':'actionlint','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(sys.argv[1]),'line':None,'description':text[:4000],'evidence':[str(sys.argv[1])],'triageRef':''}
out=write_normalized(out_path,'actionlint','go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.7 && actionlint',127,[f],[str(sys.argv[1])],'FAILED')
print(json.dumps({k:out[k] for k in ['tool','status','exitStatus','criticalHighUnresolved']},indent=2))
PY
  exit 1
fi
write_result() {
  local status="$1"
  python - "$TXT" "$JSON" "$status" <<'PY'
import json,pathlib,sys
from scripts.audit.audit_model import write_normalized
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore'); status=int(sys.argv[3])
out_path=pathlib.Path(sys.argv[2])
findings=[]
if status:
    findings.append({'fingerprint':'actionlint-failed','id':'ACTIONLINT_FAILED','tool':'actionlint','severity':'high','status':'unresolved','title':'actionlint failed','packageOrContract':'github-actions','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(sys.argv[1]),'line':None,'description':text[-4000:],'evidence':[str(sys.argv[1])],'triageRef':''})
out=write_normalized(out_path,'actionlint','actionlint',status,findings,[str(sys.argv[1])],'FAILED' if status else 'COMPLETED')
print(json.dumps({k:out[k] for k in ['tool','status','exitStatus','criticalHighUnresolved']},indent=2))
if status:
    print('--- actionlint output ---')
    print(text[-4000:])
    sys.exit(1)
PY
}
set +e
go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.7 >> "$TXT" 2>&1
INSTALL_STATUS=$?
set -e
if [ "$INSTALL_STATUS" -ne 0 ]; then
  write_result "$INSTALL_STATUS"
fi
export PATH="$(go env GOPATH)/bin:$PATH"
set +e
actionlint > "$TXT.tmp" 2>&1
STATUS=$?
cat "$TXT.tmp" >> "$TXT" 2>/dev/null || true
set -e
write_result "$STATUS"
