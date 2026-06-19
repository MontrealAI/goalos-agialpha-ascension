#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/semgrep.txt"; RAW="$AUDIT_REPORT_DIR/semgrep.raw.json"; JSON="$AUDIT_REPORT_DIR/semgrep.json"
CMD="semgrep scan --config configs/semgrep.yml --json --output semgrep.raw.json ."
: > "$TXT"
python -m pip install --user setuptools==80.9.0 semgrep==1.101.0 --quiet >> "$TXT" 2>&1 || true
export PATH="$HOME/.local/bin:$PATH"
set +e
timeout 180 semgrep scan --config configs/semgrep.yml --json --output "$RAW" . >> "$TXT" 2>&1
STATUS=$?
set -e
python - "$RAW" "$JSON" "$TXT" "$STATUS" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import stable_fingerprint, write_normalized
raw,out,txt=map(pathlib.Path,sys.argv[1:4]); status=int(sys.argv[4])
findings=[]; state='COMPLETED'
if status == 124:
    state='TIMEOUT'; findings.append({'fingerprint':'semgrep-timeout','id':'SEMGREP_TIMEOUT','tool':'semgrep','severity':'high','status':'unresolved','title':'Semgrep timed out','packageOrContract':'semgrep','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(txt),'line':None,'description':'semgrep exceeded 180 second timeout','evidence':[str(txt)],'triageRef':''})
elif not raw.exists() or not raw.read_text(errors='ignore').strip():
    state='FAILED'; findings.append({'fingerprint':'semgrep-no-json','id':'SEMGREP_NO_JSON','tool':'semgrep','severity':'high','status':'unresolved','title':'Semgrep failed before JSON output','packageOrContract':'semgrep','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(txt),'line':None,'description':'semgrep did not produce JSON output','evidence':[str(txt)],'triageRef':''})
else:
    try:
        data=json.loads(raw.read_text())
        for r in data.get('results',[]) if isinstance(data,dict) else []:
            sev_raw=str(r.get('extra',{}).get('severity','')).upper()
            if sev_raw not in {'ERROR','CRITICAL','HIGH'}: continue
            sev='critical' if sev_raw=='CRITICAL' else 'high'
            rid=str(r.get('check_id') or 'SEMGREP_FINDING')
            loc=r.get('start',{}) if isinstance(r,dict) else {}
            file=str(r.get('path') or '')
            line=loc.get('line')
            findings.append({'fingerprint':stable_fingerprint('semgrep',rid,'source','',file,file,line),'id':rid,'tool':'semgrep','severity':sev,'status':'unresolved','title':str(r.get('extra',{}).get('message') or rid)[:200],'packageOrContract':'source','installedVersion':'','fixedVersion':'','dependencyPath':'','file':file,'line':line,'description':str(r.get('extra',{}).get('message') or ''),'evidence':[str(raw)],'triageRef':''})
        if findings: state='COMPLETED_WITH_FINDINGS'
    except Exception as exc:
        state='MALFORMED'; findings.append({'fingerprint':'semgrep-malformed','id':'SEMGREP_MALFORMED','tool':'semgrep','severity':'high','status':'unresolved','title':'Semgrep output malformed','packageOrContract':'semgrep','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(raw),'line':None,'description':str(exc),'evidence':[str(raw)],'triageRef':''})
obj=write_normalized(out,'semgrep','semgrep scan --config configs/semgrep.yml --json --output semgrep.raw.json .',status,findings,[str(raw),str(txt)],state)
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']},indent=2))
sys.exit(1 if obj['criticalHighUnresolved'] or state in {'FAILED','TIMEOUT','MALFORMED'} else 0)
PY
