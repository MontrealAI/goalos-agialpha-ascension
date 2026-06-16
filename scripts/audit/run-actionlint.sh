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
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore')
out={'tool':'actionlint','status':'FAILED','exitStatus':127,'critical_high_unresolved':1,'output':text[:4000]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['tool','status','exitStatus','critical_high_unresolved']},indent=2))
PY
  exit 1
fi
write_result() {
  local status="$1"
  python - "$TXT" "$JSON" "$status" <<'PY'
import json,pathlib,sys
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore'); status=int(sys.argv[3])
out={'tool':'actionlint','status':'COMPLETED' if status==0 else 'FAILED','exitStatus':status,'critical_high_unresolved':0 if status==0 else 1,'output':text[:4000]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['tool','status','exitStatus','critical_high_unresolved']},indent=2))
if status:
    print('--- actionlint output ---')
    print(text[-4000:])
    sys.exit(1)
PY
}
set +e
go install github.com/rhysd/actionlint/cmd/actionlint@latest >> "$TXT" 2>&1
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
