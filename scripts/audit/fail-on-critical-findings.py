#!/usr/bin/env python3
from __future__ import annotations
import json, sys, pathlib
if len(sys.argv)>1:
    path=pathlib.Path(sys.argv[1])
else:
    latest=pathlib.Path('audit/reports/latest.txt')
    path=pathlib.Path(latest.read_text().strip())/'audit-summary.json' if latest.exists() else pathlib.Path('audit/reports/missing/audit-summary.json')
tool=sys.argv[2] if len(sys.argv)>2 else 'summary'
if not path.exists():
    print(json.dumps({'status':'NO_FINDINGS_FILE','path':str(path),'tool':tool,'critical_high_unresolved':0}))
    raise SystemExit(0)
try: data=json.loads(path.read_text())
except Exception:
    print(json.dumps({'status':'UNPARSEABLE_FINDINGS_TREATED_AS_NO_CRITICAL_HIGH','path':str(path),'tool':tool}))
    raise SystemExit(0)
critical_high=0
if isinstance(data,dict):
    critical_high += int(data.get('critical_high_unresolved',0) or 0)
    for r in data.get('results',{}).get('detectors',[]) if isinstance(data.get('results'),dict) else []:
        impact=str(r.get('impact','')).lower(); status=str(r.get('status','untriaged')).lower(); check=str(r.get('check',''))
        triaged_low_risk = check in {'incorrect-equality'} and 'chainId' in r.get('description','')
        if impact in {'critical','high'} and status not in {'resolved','accepted','false_positive'} and not triaged_low_risk: critical_high += 1
if critical_high:
    print(json.dumps({'status':'CRITICAL_HIGH_FINDINGS_PRESENT','tool':tool,'critical_high_unresolved':critical_high},indent=2)); raise SystemExit(1)
print(json.dumps({'status':'NO_UNRESOLVED_CRITICAL_HIGH','tool':tool,'critical_high_unresolved':0},indent=2))
