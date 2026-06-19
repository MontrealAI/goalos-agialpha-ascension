#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/solhint.txt"; JSON="$AUDIT_REPORT_DIR/solhint.json"
if [ ! -f .solhint.json ]; then
  echo ".solhint.json is missing" > "$TXT"
  python - "$JSON" "$TXT" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import write_normalized
out, txt = map(pathlib.Path, sys.argv[1:3])
f={'fingerprint':'solhint-config-missing','id':'SOLHINT_CONFIG_MISSING','tool':'solhint','severity':'high','status':'unresolved','title':'.solhint.json is missing','packageOrContract':'solhint','installedVersion':'','fixedVersion':'','dependencyPath':'','file':'.solhint.json','line':None,'description':'.solhint.json is missing','evidence':[str(txt)],'triageRef':''}
obj=write_normalized(out,'solhint','npx --yes solhint@6.2.3 "contracts/**/*.sol"',1,[f],[str(txt)],'FAILED')
print(json.dumps({k:obj[k] for k in ['tool','status','criticalHighUnresolved']},indent=2))
PY
  exit 1
fi
set +e
npx --yes solhint@6.2.3 "contracts/**/*.sol" > "$TXT" 2>&1
STATUS=$?
set -e
python - "$TXT" "$JSON" "$STATUS" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import stable_fingerprint, write_normalized
text_path,out=map(pathlib.Path,sys.argv[1:3]); status=int(sys.argv[3])
text=text_path.read_text(errors='ignore')
findings=[]
for line in text.splitlines():
    if ' error ' not in line.lower():
        continue
    parts=line.strip().split()
    file=parts[0] if parts else ''
    findings.append({'fingerprint':stable_fingerprint('solhint','SOLHINT_ERROR','contracts','',line),'id':'SOLHINT_ERROR','tool':'solhint','severity':'high','status':'unresolved','title':line.strip()[:200],'packageOrContract':'contracts','installedVersion':'','fixedVersion':'','dependencyPath':'','file':file,'line':None,'description':line.strip(),'evidence':[str(text_path)],'triageRef':''})
state='FAILED' if findings else 'COMPLETED'
obj=write_normalized(out,'solhint','npx --yes solhint@6.2.3 "contracts/**/*.sol"',status,findings,[str(text_path)],state)
obj['errors']=len(findings); obj['warnings']=text.lower().count(' warning ')
out.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
print(json.dumps({'tool':'solhint','status':obj['status'],'exitStatus':status,'errors':len(findings),'warnings':obj['warnings'],'criticalHighUnresolved':obj['criticalHighUnresolved']},indent=2))
if findings: sys.exit(1)
PY
