#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from scripts.audit.audit_model import current_report_dir, write_summary, load_triage, write_normalized
report_dir = pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else current_report_dir()
report_dir.mkdir(parents=True, exist_ok=True)
expected = ['slither','semgrep','solhint','npm-audit','osv-scanner','actionlint','shellcheck','gitleaks']
normalized=[]
for tool in expected:
    path = report_dir / f'{tool}.json'
    if path.exists():
        try:
            data=json.loads(path.read_text())
            if data.get('schemaVersion') == '2.0':
                normalized.append(data)
            else:
                # Legacy wrapper output: convert status/count without inventing pass.
                status=str(data.get('status','COMPLETED'))
                count=int(data.get('critical_high_unresolved',0) or 0) if isinstance(data,dict) else 0
                findings=[]
                for i in range(count):
                    findings.append({'fingerprint':f'{tool}-legacy-{i}','id':f'{tool.upper()}-LEGACY-{i+1}','tool':tool,'severity':'high','status':'unresolved','title':f'{tool} legacy unresolved critical/high finding','packageOrContract':tool,'installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(path),'line':None,'description':'Legacy wrapper exposed only aggregate count.','evidence':[str(path)],'triageRef':''})
                normalized.append(write_normalized(path, tool, data.get('command','legacy wrapper'), int(data.get('exitStatus',0) or 0), findings, [str(path)], 'COMPLETED_WITH_FINDINGS' if findings else status))
        except Exception as exc:
            normalized.append(write_normalized(path, tool, 'parse existing scanner output', 2, [{'fingerprint':f'{tool}-malformed','id':'MALFORMED_SCANNER_OUTPUT','tool':tool,'severity':'high','status':'unresolved','title':f'{tool} output malformed','packageOrContract':tool,'installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(path),'line':None,'description':str(exc),'evidence':[str(path)],'triageRef':''}], [str(path)], 'MALFORMED'))
    else:
        normalized.append(write_normalized(path, tool, 'not run', 2, [], [], 'UNAVAILABLE'))
_, triage_errors = load_triage()
summary=write_summary(report_dir, normalized, triage_errors)
print(json.dumps(summary, indent=2, sort_keys=True))
