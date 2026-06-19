#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/slither.txt"; RAW="$AUDIT_REPORT_DIR/slither.raw.json"; JSON="$AUDIT_REPORT_DIR/slither.json"; SARIF="$AUDIT_REPORT_DIR/slither.sarif"
CMD="timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json"
if ! npm run compile:ci > "$AUDIT_REPORT_DIR/deterministic-compile.log" 2>&1; then
  python - "$JSON" "$TXT" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import write_normalized
out, txt = map(pathlib.Path, sys.argv[1:3])
f={"fingerprint":"slither-compile-failed","id":"SLITHER_COMPILE_FAILED","tool":"slither","severity":"high","status":"unresolved","title":"Deterministic compile failed before Slither","packageOrContract":"compile:ci","installedVersion":"","fixedVersion":"","dependencyPath":"","file":str(txt),"line":None,"description":"Deterministic compile failed; Slither clearance is impossible until compile passes","evidence":[str(txt)],"triageRef":""}
obj=write_normalized(out,'slither','npm run compile:ci',1,[f],[str(txt)],'FAILED')
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']},indent=2))
PY
  echo '{"runs":[]}' > "$SARIF"
  exit 1
fi
if ! command -v slither >/dev/null 2>&1; then
  python -m pip install --user slither-analyzer==0.10.4 > "$AUDIT_REPORT_DIR/slither-install.log" 2>&1 || true
  export PATH="$HOME/.local/bin:$PATH"
fi
if ! command -v slither >/dev/null 2>&1; then
  python - "$JSON" "$TXT" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import write_normalized
out, txt = map(pathlib.Path, sys.argv[1:3])
f={"fingerprint":"slither-unavailable","id":"SLITHER_UNAVAILABLE","tool":"slither","severity":"high","status":"unresolved","title":"Slither unavailable","packageOrContract":"slither","installedVersion":"","fixedVersion":"","dependencyPath":"","file":str(txt),"line":None,"description":"slither executable unavailable after pinned install attempt","evidence":[str(txt)],"triageRef":""}
obj=write_normalized(out,'slither','timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json',127,[f],[str(txt)],'UNAVAILABLE')
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']},indent=2))
PY
  echo '{"runs":[]}' > "$SARIF"
  exit 1
fi
set +e
timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json --json "$RAW" > "$TXT" 2>&1
SLITHER_STATUS=$?
set -e
python - "$RAW" "$JSON" "$TXT" "$SLITHER_STATUS" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import stable_fingerprint, write_normalized
raw,out,txt=map(pathlib.Path,sys.argv[1:4]); status=int(sys.argv[4])
findings=[]; state='COMPLETED'
if status == 124:
    state='TIMEOUT'; findings.append({'fingerprint':'slither-timeout','id':'SLITHER_TIMEOUT','tool':'slither','severity':'high','status':'unresolved','title':'Slither timed out','packageOrContract':'slither','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(txt),'line':None,'description':'slither exceeded 120 second CI timeout','evidence':[str(txt)],'triageRef':''})
elif not raw.exists() or not raw.read_text(errors='ignore').strip():
    state='FAILED'; findings.append({'fingerprint':'slither-no-json','id':'SLITHER_NO_JSON','tool':'slither','severity':'high','status':'unresolved','title':'Slither failed before JSON output','packageOrContract':'slither','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(txt),'line':None,'description':'slither did not produce JSON output','evidence':[str(txt)],'triageRef':''})
else:
    try:
        data=json.loads(raw.read_text())
        detectors=data.get('results',{}).get('detectors',[]) if isinstance(data,dict) else []
        for d in detectors:
            sev=str(d.get('impact') or '').lower()
            if sev not in {'high','critical'}: continue
            check=str(d.get('check') or d.get('title') or 'SLITHER_FINDING')
            loc=(d.get('elements') or [{}])[0].get('source_mapping',{}) if isinstance(d.get('elements'),list) else {}
            file=loc.get('filename_relative') or loc.get('filename_absolute') or ''
            line=(loc.get('lines') or [None])[0] if isinstance(loc.get('lines'),list) else None
            findings.append({'fingerprint':stable_fingerprint('slither',check,'contracts','',file,file,line),'id':check,'tool':'slither','severity':sev,'status':'unresolved','title':str(d.get('description') or check).split('\n')[0][:200],'packageOrContract':'contracts','installedVersion':'','fixedVersion':'','dependencyPath':'','file':file,'line':line,'description':str(d.get('description') or ''),'evidence':[str(raw)],'triageRef':''})
        if findings: state='COMPLETED_WITH_FINDINGS'
    except Exception as exc:
        state='MALFORMED'; findings.append({'fingerprint':'slither-malformed','id':'SLITHER_MALFORMED','tool':'slither','severity':'high','status':'unresolved','title':'Slither output malformed','packageOrContract':'slither','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(raw),'line':None,'description':str(exc),'evidence':[str(raw)],'triageRef':''})
obj=write_normalized(out,'slither','timeout 120 slither . --compile-force-framework hardhat --config-file configs/slither.config.json --json slither.raw.json',status,findings,[str(raw),str(txt)],state)
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']},indent=2))
sys.exit(1 if obj['criticalHighUnresolved'] or state in {'FAILED','UNAVAILABLE','TIMEOUT','MALFORMED'} else 0)
PY
set +e
for printer in human-summary contract-summary vars-and-auth; do
  timeout 15 slither . --print "$printer" --compile-force-framework hardhat --config-file configs/slither.config.json > "$AUDIT_REPORT_DIR/slither-$printer.txt" 2>&1 || true
done
set -e
echo '{"version":"2.1.0","runs":[]}' > "$SARIF"
