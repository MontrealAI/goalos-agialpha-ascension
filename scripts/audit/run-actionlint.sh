#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/actionlint.txt"; JSON="$AUDIT_REPORT_DIR/actionlint.json"
if ! command -v actionlint >/dev/null 2>&1; then
  go install github.com/rhysd/actionlint/cmd/actionlint@latest >> "$TXT" 2>&1
  export PATH="$(go env GOPATH)/bin:$PATH"
fi
set +e
actionlint > "$TXT.tmp" 2>&1
STATUS=$?
cat "$TXT.tmp" >> "$TXT" 2>/dev/null || true
set -e
python - "$TXT" "$JSON" "$STATUS" <<'PY'
import json,pathlib,sys
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore'); status=int(sys.argv[3])
out={'tool':'actionlint','status':'COMPLETED' if status==0 else 'FAILED','exitStatus':status,'critical_high_unresolved':0 if status==0 else 1,'output':text[:4000]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['tool','status','exitStatus','critical_high_unresolved']},indent=2))
if status: sys.exit(1)
PY
