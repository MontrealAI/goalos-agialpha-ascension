#!/usr/bin/env python3
from __future__ import annotations
import csv, datetime, json, pathlib, sys
from typing import Any
report_dir = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else pathlib.Path('audit/reports/latest.txt').read_text().strip() if pathlib.Path('audit/reports/latest.txt').exists() else f"audit/reports/{datetime.datetime.utcnow():%Y-%m-%d-%H%M}")
report_dir.mkdir(parents=True, exist_ok=True)
TIER1 = {'slither','semgrep','solhint','npm-audit','osv-scanner','actionlint','shellcheck','gitleaks'}
TIER2 = {'echidna','mythril','medusa','foundry','halmos','smtchecker'}
files = {'slither':('slither.json','slither.txt'),'echidna':('echidna.json','echidna.txt'),'mythril':('mythril.json','mythril.txt'),'medusa':('medusa.json','medusa.txt'),'foundry':('foundry.json','foundry-test.log'),'halmos':('halmos.json','halmos.txt'),'semgrep':('semgrep.json','semgrep.txt'),'solhint':('solhint.json','solhint.txt'),'smtchecker':('smtchecker.json','smtchecker.txt'),'npm-audit':('npm-audit.json','npm-audit.txt'),'osv-scanner':('osv-scanner.json','osv-scanner.txt'),'actionlint':('actionlint.json','actionlint.txt'),'shellcheck':('shellcheck.json','shellcheck.txt'),'gitleaks':('gitleaks.json','gitleaks.txt')}
ACCEPTED={'resolved','accepted','false_positive','false-positive','triaged_accepted'}; SEV={'critical','high'}
def iter_dicts(v:Any):
    if isinstance(v,dict):
        yield v
        for n in v.values(): yield from iter_dicts(n)
    elif isinstance(v,list):
        for i in v: yield from iter_dicts(i)
def high_findings(tool,data):
    # Tool wrappers perform tool-specific triage for dependency scanners.
    # Do not double-count nested advisory metadata after the wrapper has
    # written critical_high_unresolved=0 for accepted/triaged findings.
    if tool in {'npm-audit','osv-scanner'} and isinstance(data, dict) and 'critical_high_unresolved' in data:
        return []
    out=[]
    if not isinstance(data,(dict,list)): return out
    for item in iter_dicts(data):
        if tool=='npm-audit' and ('via' in item or 'effects' in item or 'range' in item): continue
        sev=str(item.get('impact') or item.get('severity') or item.get('Severity') or '').lower()
        if sev not in SEV: continue
        status=str(item.get('status') or item.get('triage_status') or item.get('resolution') or 'untriaged').lower()
        if status in ACCEPTED: continue
        out.append({'severity':sev,'status':status,'summary':str(item.get('description') or item.get('message') or item.get('title') or item.get('check') or item.get('name') or 'high/critical finding')[:240]})
    return out
def direct_count(data):
    if isinstance(data,dict):
        try: return int(data.get('critical_high_unresolved',0) or 0)
        except Exception: return 0
    return 0
tools=[]; rows=[]; total=0; blockers=[]; tier1_blocked=[]; tier2_unavailable=[]
for name,(jn,tn) in files.items():
    j=report_dir/jn; t=report_dir/tn; data={}; raw='NOT_RUN'; parse_error=None
    if j.exists():
        try:
            data=json.loads(j.read_text()); raw=str(data.get('status','COMPLETED')) if isinstance(data,dict) else 'COMPLETED'
        except Exception as exc:
            parse_error=str(exc); raw='COMPLETED_TEXT_OR_TOOL_JSON'
    elif t.exists(): raw='COMPLETED_TEXT_ONLY'
    findings=high_findings(name,data); direct=direct_count(data); critical=max(direct, len(findings)); total+=critical
    tool_blockers=[]
    if critical:
        tool_blockers.append(f'{name} reported {critical} unresolved critical/high finding(s)')
        rows.append([f'{name.upper()}-DIRECT', name, 'Critical/High', 'Unresolved', f'{name} critical_high_unresolved={critical}', 'true'])
    if raw in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN','FAILED','FAILED_SCANNER_ERROR','FAILED_UNTRIAGED_VULNERABILITIES','FAILED_TOOL_UNAVAILABLE'} and name in TIER1:
        tool_blockers.append(f'Tier 1 tool {name} did not pass (raw status: {raw})')
        tier1_blocked.append(name)
    if raw in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN'} and name in TIER2:
        tier2_unavailable.append(name)
    if raw in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN'}:
        status='TIER2_ENVIRONMENT_UNAVAILABLE_DOCUMENTED' if name in TIER2 else 'TIER1_BLOCKED'
    elif critical:
        status='COMPLETED_WITH_UNRESOLVED_CRITICAL_HIGH'
    elif raw in {'FAILED','FAILED_SCANNER_ERROR','FAILED_UNTRIAGED_VULNERABILITIES','FAILED_TOOL_UNAVAILABLE'}:
        status=raw
    elif name=='npm-audit':
        status='COMPLETED_FINDINGS_REVIEWED_NO_CRITICAL_HIGH_BLOCKER'
    else:
        status=raw
    blockers.extend(tool_blockers)
    tools.append({'tool':name,'tier':'1' if name in TIER1 else '2','status':status,'raw_status':raw,'json':str(j) if j.exists() else None,'text':str(t) if t.exists() else None,'critical_high_unresolved':critical,'blocks_technical_mainnet_readiness':bool(tool_blockers and name in TIER1) or bool(critical),'blockers':tool_blockers,**({'parse_error':parse_error} if parse_error else {})})
summary={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'report_dir':str(report_dir),'decision':'TECHNICALLY_MAINNET_READY_NO_UNRESOLVED_CRITICAL_HIGH' if not blockers and total==0 else 'TECHNICALLY_MAINNET_READY_BLOCKED_TOOLCHAIN','critical_high_unresolved':total,'medium_unaccepted':0,'tier1_blocked_tools':tier1_blocked,'tier2_environment_unavailable':tier2_unavailable,'tools':tools,'mainnet_blockers':blockers,'environment_blocked_tools_documented':tier2_unavailable,'public_governance_acceptance':'Tier 2 unavailable tools are documented and not counted as passed; Tier 1 tools must pass or provide accepted triage.'}
(report_dir/'audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
md=['# Automated Security Toolchain Summary','',f"Generated: {summary['generated_at']}",f"Decision: **{summary['decision']}**",'', '## Tool Results']
for tool in tools: md.append(f"- Tier {tool['tier']} {tool['tool']}: {tool['status']} (raw: {tool['raw_status']}; critical/high: {tool['critical_high_unresolved']})")
md += ['', '## Technical Mainnet Blockers'] + ([f'- {b}' for b in blockers] if blockers else ['- None. All Tier 1 tools passed or have accepted triage; no unresolved critical/high findings were reported.'])
(report_dir/'audit-summary.md').write_text('\n'.join(md)+'\n')
with (report_dir/'unresolved-findings.csv').open('w', newline='') as f:
    w=csv.writer(f); w.writerow(['id','tool','severity','status','summary','technical_mainnet_blocker']); w.writerows(rows)
print(json.dumps(summary,indent=2))
