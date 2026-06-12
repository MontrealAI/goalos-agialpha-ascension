#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib, sys
report_dir = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else pathlib.Path('audit/reports/latest.txt').read_text().strip())
summary_path = report_dir/'audit-summary.json'
summary = json.loads(summary_path.read_text()) if summary_path.exists() else {'tools': [], 'mainnet_blockers': ['missing audit summary'], 'critical_high_unresolved': 0, 'medium_unaccepted': 0, 'tier1_blocked_tools': []}
blockers = list(summary.get('mainnet_blockers', []))
if int(summary.get('critical_high_unresolved',0) or 0)>0 and 'unresolved critical/high findings present' not in blockers: blockers.append('unresolved critical/high findings present')
if summary.get('tier1_blocked_tools'): blockers.append('Tier 1 blocked tools: '+', '.join(summary['tier1_blocked_tools']))
status='NOT_CLEARED' if blockers else 'CLEARED'
content=['# Automated Security Toolchain Clearance Report','',f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",f"Clearance: **{status}**",'', '## Blockers']
content += [f'- {b}' for b in blockers] if blockers else ['- None.']
content += ['', '## Tier 1 mandatory tools']
for t in summary.get('tools',[]):
    if t.get('tier')=='1': content.append(f"- {t['tool']}: {t['status']} (critical/high: {t['critical_high_unresolved']})")
content += ['', '## Tier 2 unavailable tools', *[f"- {t}" for t in summary.get('tier2_environment_unavailable', [])], '', '## Boundary', '- This is automated/internal security-toolchain evidence, not an external audit.', '- Tier 1 tools are not marked passed when environment-blocked; Tier 2 unavailable tools are documented separately and not counted as passed.']
text='\n'.join(content)+'\n'
(report_dir/'toolchain-clearance-report.md').write_text(text); pathlib.Path('audit/TOOLCHAIN_CLEARANCE_REPORT.md').write_text(text)
qa={'redacted':True,'containsSecrets':False,'containsPrivateAddresses':False,'status':'PASSED' if status=='CLEARED' else 'NOT_CLEARED','automatedSecurityToolchain':'PASSED' if status=='CLEARED' else 'NOT_CLEARED','tier1Status':'PASSED' if status=='CLEARED' else 'BLOCKED','tier1BlockedTools':summary.get('tier1_blocked_tools',[]),'tier2UnavailableTools':summary.get('tier2_environment_unavailable',[]),'unresolvedCriticalHighFindings':int(summary.get('critical_high_unresolved',0) or 0),'unresolvedMediumFindings':int(summary.get('medium_unaccepted',0) or 0),'mainnetDeployed':'NO','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
pathlib.Path('qa/public-toolchain-clearance-evidence.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps({'status':status,'sha256':hashlib.sha256(text.encode()).hexdigest(),'path':str(report_dir/'toolchain-clearance-report.md')},indent=2))
if status!='CLEARED': sys.exit(1)
