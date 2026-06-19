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
                # Legacy scanner output has no sourceSha/run provenance, so it cannot be restamped as current evidence.
                status=str(data.get('status','LEGACY_WITHOUT_PROVENANCE'))
                count=int(data.get('critical_high_unresolved',0) or 0) if isinstance(data,dict) else 0
                findings=[]
                for i in range(max(count, 1)):
                    findings.append({'fingerprint':f'{tool}-legacy-provenance-{i}','id':f'{tool.upper()}-LEGACY_WITHOUT_PROVENANCE','tool':tool,'severity':'high','status':'unresolved','title':f'{tool} legacy output lacks sourceSha provenance','packageOrContract':tool,'installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(path),'line':None,'description':'Legacy wrapper output cannot prove it was generated for the current source SHA; rerun a schemaVersion 2.0 wrapper.','evidence':[str(path)],'triageRef':''})
                normalized.append(write_normalized(path, tool, data.get('command','legacy wrapper'), int(data.get('exitStatus',2) or 2), findings, [str(path)], 'LEGACY_WITHOUT_PROVENANCE'))
        except Exception as exc:
            normalized.append(write_normalized(path, tool, 'parse existing scanner output', 2, [{'fingerprint':f'{tool}-malformed','id':'MALFORMED_SCANNER_OUTPUT','tool':tool,'severity':'high','status':'unresolved','title':f'{tool} output malformed','packageOrContract':tool,'installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(path),'line':None,'description':str(exc),'evidence':[str(path)],'triageRef':''}], [str(path)], 'MALFORMED'))
    else:
        normalized.append(write_normalized(path, tool, 'not run', 2, [], [], 'UNAVAILABLE'))
_, triage_errors = load_triage()
summary=write_summary(report_dir, normalized, triage_errors)
print(json.dumps(summary, indent=2, sort_keys=True))
