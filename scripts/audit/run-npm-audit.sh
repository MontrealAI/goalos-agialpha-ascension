#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/npm-audit.txt"; RAW="$AUDIT_REPORT_DIR/npm-audit.raw.json"; JSON="$AUDIT_REPORT_DIR/npm-audit.json"
set +e
npm audit --json > "$RAW" 2> "$TXT"
STATUS=$?
set -e
python - "$RAW" "$JSON" "$TXT" "$STATUS" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import load_triage, npm_findings, write_normalized
raw, out, txt = map(pathlib.Path, sys.argv[1:4]); status=int(sys.argv[4])
text=raw.read_text(errors='ignore') if raw.exists() else ''
try:
    data=json.loads(text) if text.strip() else {}
    triage, errors=load_triage()
    findings=npm_findings(data, triage)
    findings += [{"fingerprint":"triage-error-"+str(i),"id":"TRIAGE_ERROR","tool":"npm-audit","severity":"high","status":"unresolved","title":e,"packageOrContract":"audit/TRIAGE.json","installedVersion":"","fixedVersion":"","dependencyPath":"audit/TRIAGE.json","file":"audit/TRIAGE.json","line":None,"description":e,"evidence":[],"triageRef":""} for i,e in enumerate(errors)]
    state='COMPLETED_WITH_FINDINGS' if findings else 'COMPLETED'
except Exception as exc:
    findings=[{"fingerprint":"npm-audit-parse-error","id":"NPM_AUDIT_PARSE_ERROR","tool":"npm-audit","severity":"high","status":"unresolved","title":"npm audit output malformed","packageOrContract":"npm-audit","installedVersion":"","fixedVersion":"","dependencyPath":"","file":str(raw),"line":None,"description":str(exc),"evidence":[str(raw)],"triageRef":""}]
    state='MALFORMED'
obj=write_normalized(out,'npm-audit','npm audit --json',status,findings,[str(raw),str(txt)],state)
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']}, indent=2))
PY
