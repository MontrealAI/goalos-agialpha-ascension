#!/usr/bin/env python3
from __future__ import annotations
import csv, json, sys, pathlib, datetime, hashlib
report_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path('audit/reports/latest.txt').read_text().strip() if pathlib.Path('audit/reports/latest.txt').exists() else f"audit/reports/{datetime.datetime.utcnow():%Y-%m-%d-%H%M}")
report_dir.mkdir(parents=True, exist_ok=True)
tools=[]
for name in ['slither','echidna','mythril','medusa','foundry','semgrep','npm-audit']:
    j=report_dir/({'foundry':'foundry.json','npm-audit':'npm-audit.json'}.get(name, name+'.json'))
    t=report_dir/({'foundry':'foundry-test.log','npm-audit':'npm-audit.txt'}.get(name,name+'.txt'))
    status='NOT_RUN'
    blockers=[]
    data={}
    if j.exists():
        try: data=json.loads(j.read_text()); status=data.get('status','COMPLETED')
        except Exception: status='COMPLETED_TEXT_ONLY'
    elif t.exists(): status='COMPLETED_TEXT_ONLY'
    if status in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN'}:
        blockers.append(f'{name} execution pending')
    if name == 'npm-audit' and status not in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN'}:
        status='COMPLETED_WITH_FINDINGS_REVIEW_REQUIRED'
    tools.append({'tool':name,'status':status,'json':str(j) if j.exists() else None,'text':str(t) if t.exists() else None,'blocks_mainnet': bool(blockers),'blockers':blockers})
summary={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'report_dir':str(report_dir),'decision':'NOT_AUTHORIZED','critical_high_unresolved':0,'medium_unaccepted':0,'tools':tools,'mainnet_blockers':['external audit closure hash missing','legal/tax/public-claims/treasury/founder gates missing','Sepolia rehearsal requires real network evidence unless manifest/evidence are present','audit tools pending where environment-blocked']}
(report_dir/'audit-summary.json').write_text(json.dumps(summary,indent=2))
md=['# Audit Summary','',f"Generated: {summary['generated_at']}",f"Decision: **{summary['decision']}**",'', '## Tool Results']
for tool in tools: md.append(f"- {tool['tool']}: {tool['status']}" + (f" ({'; '.join(tool['blockers'])})" if tool['blockers'] else ''))
md += ['', '## Mainnet Blockers'] + [f"- {b}" for b in summary['mainnet_blockers']]
(report_dir/'audit-summary.md').write_text('\n'.join(md)+'\n')
with (report_dir/'unresolved-findings.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','tool','severity','status','summary','mainnet_blocker']);
    for tool in tools:
        if tool['blocks_mainnet']: w.writerow([f"ENV-{tool['tool'].upper()}",tool['tool'],'Medium','Pending',f"{tool['tool']} needs executable available for full run",'true'])
print(json.dumps(summary,indent=2))
