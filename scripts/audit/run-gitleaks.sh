#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/gitleaks.txt"; JSON="$AUDIT_REPORT_DIR/gitleaks.json"
if ! command -v gitleaks >/dev/null 2>&1; then
  go install github.com/zricethezav/gitleaks/v8@latest >> "$TXT" 2>&1
  export PATH="$(go env GOPATH)/bin:$PATH"
fi
set +e
gitleaks detect --no-git --source . --config .gitleaks.toml --report-format json --report-path "$JSON.tmp" >> "$TXT" 2>&1
STATUS=$?
set -e
python - "$JSON.tmp" "$JSON" "$STATUS" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); findings=[]
if p.exists() and p.read_text().strip():
    try: findings=json.loads(p.read_text())
    except Exception: findings=[]
out={'tool':'gitleaks','status':'COMPLETED' if not findings else 'FAILED','findingCount':len(findings),'critical_high_unresolved':len(findings),'findings':findings}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['tool','status','findingCount','critical_high_unresolved']},indent=2))
if findings: sys.exit(1)
PY
