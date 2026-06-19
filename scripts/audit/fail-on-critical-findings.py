#!/usr/bin/env python3
from __future__ import annotations
import json, os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from scripts.audit.audit_model import current_report_dir

def emit(msg):
    print(msg)
    step=os.environ.get('GITHUB_STEP_SUMMARY')
    if step:
        with open(step,'a') as f: f.write(msg+'\n')

def main():
    path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else current_report_dir()/'audit-summary.json'
    if not path.exists():
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_MISSING','summaryPath':str(path)}, indent=2)); return 2
    try: data=json.loads(path.read_text())
    except Exception as exc:
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_MALFORMED','summaryPath':str(path),'error':str(exc)}, indent=2)); return 2
    required=['schemaVersion','decision','criticalHighUnresolved','unresolvedFindings','toolFailures','unavailableMandatoryTools']
    missing=[k for k in required if k not in data]
    if data.get('schemaVersion') != '2.0' or missing:
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_INVALID','summaryPath':str(path),'missing':missing}, indent=2)); return 2
    unresolved=data.get('unresolvedFindings')
    if not isinstance(unresolved,list):
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_INVALID','summaryPath':str(path),'reason':'unresolvedFindings is not a list'}, indent=2)); return 2
    derived=sum(1 for f in unresolved if str(f.get('severity','')).lower() in {'critical','high'} and f.get('status')=='unresolved')
    if int(data.get('criticalHighUnresolved',-1)) != derived:
        emit(json.dumps({'status':'BLOCKED_INTERNAL_INCONSISTENCY','summaryPath':str(path),'declared':data.get('criticalHighUnresolved'),'derived':derived}, indent=2)); return 2
    if data.get('toolFailures') or data.get('unavailableMandatoryTools') or data.get('triageErrors'):
        emit('BLOCKED: mandatory scanner/triage failure')
        emit(json.dumps({'summaryPath':str(path),'toolFailures':data.get('toolFailures',[]),'unavailableMandatoryTools':data.get('unavailableMandatoryTools',[]),'triageErrors':data.get('triageErrors',[])}, indent=2)); return 2
    if derived:
        emit(f'BLOCKED: {derived} unresolved critical/high finding(s)')
        for i,f in enumerate(unresolved,1):
            emit(f"{i}. {f.get('id')} | {f.get('packageOrContract')} | {f.get('severity')} | installed {f.get('installedVersion')} | path {f.get('dependencyPath')} | fixed {f.get('fixedVersion')}")
        emit(f'Summary: {path}'); return 1
    emit(json.dumps({'status':'PASS_NO_UNRESOLVED_CRITICAL_HIGH','summaryPath':str(path),'criticalHighUnresolved':0}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
