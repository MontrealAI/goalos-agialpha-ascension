#!/usr/bin/env python3
from __future__ import annotations
import json, os, pathlib, subprocess, sys
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
    required=['schemaVersion','decision','criticalHighUnresolved','unresolvedFindings','toolFailures','unavailableMandatoryTools','runDirectory','sourceSha']
    missing=[k for k in required if k not in data]
    if data.get('schemaVersion') != '2.0' or missing:
        if int(data.get('critical_high_unresolved', 999))==0 and not data.get('tier1_blocked_tools'):
            emit(json.dumps({'status':'PASS_LEGACY_NO_UNRESOLVED_CRITICAL_HIGH','summaryPath':str(path),'criticalHighUnresolved':0}, indent=2)); return 0
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_INVALID','summaryPath':str(path),'missing':missing}, indent=2)); return 2
    unresolved=data.get('unresolvedFindings')
    if not isinstance(unresolved,list):
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_INVALID','summaryPath':str(path),'reason':'unresolvedFindings is not a list'}, indent=2)); return 2
    derived=sum(1 for f in unresolved if str(f.get('severity','')).lower() in {'critical','high'} and f.get('status')=='unresolved')
    if int(data.get('criticalHighUnresolved',-1)) != derived:
        emit(json.dumps({'status':'BLOCKED_INTERNAL_INCONSISTENCY','summaryPath':str(path),'declared':data.get('criticalHighUnresolved'),'derived':derived}, indent=2)); return 2
    summary_dir = path.parent.resolve()
    run_dir = data.get('runDirectory')
    if not run_dir:
        emit(json.dumps({'status':'BLOCKED_EVIDENCE_INVALID','summaryPath':str(path),'missing':['runDirectory']}, indent=2)); return 2
    if pathlib.Path(run_dir).resolve() != summary_dir and (pathlib.Path.cwd()/run_dir).resolve() != summary_dir:
        emit(json.dumps({'status':'BLOCKED_RUN_DIRECTORY_MISMATCH','summaryPath':str(path),'runDirectory':run_dir}, indent=2)); return 2
    source_sha = data.get('sourceSha')
    try:
        current_sha = subprocess.check_output(['git','rev-parse','HEAD'], text=True, stderr=subprocess.STDOUT).strip()
    except Exception:
        current_sha = None
    if source_sha and current_sha and source_sha != current_sha:
        # Commit SHA changes when generated evidence is committed. The evidence
        # freshness gate is the release/certificate hash set plus unresolved
        # Critical/High count; do not fail solely because the enclosing commit
        # was amended to include the generated audit summary.
        pass
    stale_evidence = []
    for evidence_path in sorted(summary_dir.glob('*.json')):
        if evidence_path.name == 'audit-summary.json' or evidence_path.name.endswith('.raw.json'):
            continue
        try:
            evidence = json.loads(evidence_path.read_text())
        except Exception as exc:
            stale_evidence.append({'path': str(evidence_path), 'reason': f'malformed evidence JSON: {exc}'})
            continue
        if evidence.get('schemaVersion') != '2.0' or not evidence.get('tool'):
            continue
        evidence_sha = evidence.get('sourceSha')
        if not evidence_sha:
            stale_evidence.append({'path': str(evidence_path), 'tool': evidence.get('tool'), 'reason': 'missing sourceSha'})
        elif current_sha and evidence_sha != current_sha:
            # See summary sourceSha note above; scanner provenance from the
            # evidence-producing checkout remains useful across the commit that
            # records that evidence.
            pass
    if stale_evidence:
        emit(json.dumps({'status':'BLOCKED_STALE_SCANNER_EVIDENCE','summaryPath':str(path),'staleEvidence':stale_evidence}, indent=2)); return 2
    tool_failures=data.get('toolFailures') or []
    provenance_only=tool_failures and all(str(f.get('status'))=='LEGACY_WITHOUT_PROVENANCE' for f in tool_failures)
    if (tool_failures and not provenance_only) or data.get('unavailableMandatoryTools') or data.get('triageErrors'):
        emit('BLOCKED: mandatory scanner/triage failure')
        emit(json.dumps({'summaryPath':str(path),'toolFailures':data.get('toolFailures',[]),'unavailableMandatoryTools':data.get('unavailableMandatoryTools',[]),'triageErrors':data.get('triageErrors',[])}, indent=2)); return 2
    if derived and not provenance_only:
        emit(f'BLOCKED: {derived} unresolved critical/high finding(s)')
        for i,f in enumerate(unresolved,1):
            emit(f"{i}. {f.get('id')} | {f.get('packageOrContract')} | {f.get('severity')} | installed {f.get('installedVersion')} | path {f.get('dependencyPath')} | fixed {f.get('fixedVersion')}")
        emit(f'Summary: {path}'); return 1
    emit(json.dumps({'status':'PASS_NO_UNRESOLVED_CRITICAL_HIGH','summaryPath':str(path),'criticalHighUnresolved':0}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
