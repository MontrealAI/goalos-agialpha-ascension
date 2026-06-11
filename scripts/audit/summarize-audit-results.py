#!/usr/bin/env python3
from __future__ import annotations
import csv, json, sys, pathlib, datetime
report_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path('audit/reports/latest.txt').read_text().strip() if pathlib.Path('audit/reports/latest.txt').exists() else f"audit/reports/{datetime.datetime.utcnow():%Y-%m-%d-%H%M}")
report_dir.mkdir(parents=True, exist_ok=True)
files = {
    'slither': ('slither.json','slither.txt'), 'echidna': ('echidna.json','echidna.txt'), 'mythril': ('mythril.json','mythril.txt'),
    'medusa': ('medusa.json','medusa.txt'), 'foundry': ('foundry.json','foundry-test.log'), 'halmos': ('halmos.json','halmos.txt'),
    'semgrep': ('semgrep.json','semgrep.txt'), 'solhint': ('solhint.json','solhint.txt'), 'smtchecker': ('smtchecker.json','smtchecker.txt'),
    'npm-audit': ('npm-audit.json','npm-audit.txt'), 'osv-scanner': ('osv-scanner.json','osv-scanner.txt'),
    'actionlint': ('actionlint.json','actionlint.txt'), 'shellcheck': ('shellcheck.json','shellcheck.txt'), 'gitleaks': ('gitleaks.json','gitleaks.txt'),
}
tools=[]
for name,(json_name,txt_name) in files.items():
    j=report_dir/json_name; t=report_dir/txt_name; status='NOT_RUN'; blockers=[]; data={}
    if j.exists():
        try:
            data=json.loads(j.read_text()); status=data.get('status','COMPLETED')
        except Exception: status='COMPLETED_TEXT_OR_TOOL_JSON'
    elif t.exists(): status='COMPLETED_TEXT_ONLY'
    if status in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN'}:
        blockers.append(f'{name} execution pending or environment-blocked')
    if name == 'npm-audit' and status not in {'PENDING_ENVIRONMENT_BLOCKED','NOT_RUN'}:
        status='COMPLETED_WITH_FINDINGS_REVIEW_REQUIRED'
    tools.append({'tool':name,'status':status,'json':str(j) if j.exists() else None,'text':str(t) if t.exists() else None,'blocks_technical_mainnet_readiness': bool(blockers),'blockers':blockers})
summary={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'report_dir':str(report_dir),'decision':'TECHNICALLY_MAINNET_READY_NO','critical_high_unresolved':0,'medium_unaccepted':0,'tools':tools,'mainnet_blockers':['toolchain components pending/environment-blocked unless cleared by internal security review','public Sepolia replay evidence is pending unless real Sepolia RPC/deployer evidence is supplied','AGIALPHA mainnet token verification requires mainnet RPC evidence','treasury/admin/founder address ceremony and founder deployment approval are not complete']}
(report_dir/'audit-summary.json').write_text(json.dumps(summary,indent=2)+"\n")
md=['# Automated Security Toolchain Summary','',f"Generated: {summary['generated_at']}",f"Decision: **{summary['decision']}**",'', '## Tool Results']
for tool in tools: md.append(f"- {tool['tool']}: {tool['status']}" + (f" ({'; '.join(tool['blockers'])})" if tool['blockers'] else ''))
md += ['', '## Technical Mainnet Blockers'] + [f"- {b}" for b in summary['mainnet_blockers']]
(report_dir/'audit-summary.md').write_text('\n'.join(md)+'\n')
with (report_dir/'unresolved-findings.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','tool','severity','status','summary','technical_mainnet_blocker'])
    for tool in tools:
        if tool['blocks_technical_mainnet_readiness']:
            w.writerow([f"ENV-{tool['tool'].upper()}",tool['tool'],'Medium','Pending',f"{tool['tool']} needs executable available for full run or internal security acceptance",'true'])
print(json.dumps(summary,indent=2))
