#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/osv-scanner.txt"; RAW="$AUDIT_REPORT_DIR/osv-scanner.raw.json"; JSON="$AUDIT_REPORT_DIR/osv-scanner.json"
: > "$TXT"
if ! command -v osv-scanner >/dev/null 2>&1; then
  if command -v go >/dev/null 2>&1; then
    timeout 180 go install github.com/google/osv-scanner/v2/cmd/osv-scanner@v2.2.3 >> "$TXT" 2>&1 || true
    export PATH="$(go env GOPATH)/bin:$PATH"
  fi
fi
if command -v osv-scanner >/dev/null 2>&1; then
  set +e
  osv-scanner --format json --lockfile package-lock.json > "$RAW" 2>> "$TXT"
  STATUS=$?
  set -e
else
  echo '{}' > "$RAW"; STATUS=127
fi
python - "$RAW" "$JSON" "$TXT" "$STATUS" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import load_triage, stable_fingerprint, apply_triage, write_normalized
raw,out,txt=map(pathlib.Path,sys.argv[1:4]); status=int(sys.argv[4])
findings=[]; state='COMPLETED'
if status==127:
    findings.append({"fingerprint":"osv-unavailable","id":"OSV_UNAVAILABLE","tool":"osv-scanner","severity":"high","status":"unresolved","title":"osv-scanner unavailable","packageOrContract":"osv-scanner","installedVersion":"","fixedVersion":"","dependencyPath":"","file":"package-lock.json","line":None,"description":"Mandatory OSV scanner was unavailable","evidence":[str(txt)],"triageRef":""}); state='UNAVAILABLE'
else:
    try: data=json.loads(raw.read_text() or '{}')
    except Exception as exc:
        data={}; findings.append({"fingerprint":"osv-malformed","id":"OSV_MALFORMED","tool":"osv-scanner","severity":"high","status":"unresolved","title":"osv output malformed","packageOrContract":"osv-scanner","installedVersion":"","fixedVersion":"","dependencyPath":"","file":str(raw),"line":None,"description":str(exc),"evidence":[str(raw)],"triageRef":""}); state='MALFORMED'
    triage,errors=load_triage()
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('vulnerabilities'),list):
                for vuln in v['vulnerabilities']:
                    pkg=v.get('package',{}).get('name') or vuln.get('package',{}).get('name') or ''
                    ver=v.get('package',{}).get('version') or vuln.get('package',{}).get('version') or ''
                    sev='high'
                    adv=vuln.get('id') or vuln.get('aliases',[None])[0] or 'OSV'
                    f={"fingerprint":stable_fingerprint('osv-scanner',adv,pkg,ver,pkg),"id":adv,"tool":"osv-scanner","severity":sev,"status":"unresolved","title":vuln.get('summary') or adv,"packageOrContract":pkg,"installedVersion":ver,"fixedVersion":"","dependencyPath":pkg,"file":"package-lock.json","line":None,"description":vuln.get('details','')[:500],"evidence":vuln.get('aliases',[]),"triageRef":""}
                    findings.append(apply_triage(f,triage))
            for c in v.values(): walk(c)
        elif isinstance(v,list):
            for c in v: walk(c)
    walk(data)
    if errors:
        findings += [{"fingerprint":"osv-triage-error-"+str(i),"id":"TRIAGE_ERROR","tool":"osv-scanner","severity":"high","status":"unresolved","title":e,"packageOrContract":"audit/TRIAGE.json","installedVersion":"","fixedVersion":"","dependencyPath":"audit/TRIAGE.json","file":"audit/TRIAGE.json","line":None,"description":e,"evidence":[],"triageRef":""} for i,e in enumerate(errors)]
    if findings and state=='COMPLETED': state='COMPLETED_WITH_FINDINGS'
obj=write_normalized(out,'osv-scanner','osv-scanner --format json --lockfile package-lock.json',status,findings,[str(raw),str(txt)],state)
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']},indent=2))
PY
