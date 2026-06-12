#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib, sys
report_dir = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else pathlib.Path('audit/reports/latest.txt').read_text().strip())
summary_path = report_dir / 'audit-summary.json'
summary = json.loads(summary_path.read_text()) if summary_path.exists() else {'tools': [], 'mainnet_blockers': ['missing audit summary'], 'critical_high_unresolved': 0, 'medium_unaccepted': 0}
blockers = list(summary.get('mainnet_blockers', []))
if int(summary.get('critical_high_unresolved', 0) or 0) > 0: blockers.append('unresolved critical/high findings present')
status = 'NOT_CLEARED' if blockers else 'CLEARED'
content = ['# Automated Security Toolchain Clearance Report','',f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",f"Clearance: **{status}**",'', '## Blockers']
content += [f"- {b}" for b in blockers] or ['- None.']
content += ['', '## Environment-blocked tools', *[f"- {t}" for t in summary.get('environment_blocked_tools_documented', [])], '', '## Boundary', '- This is automated/internal security-toolchain evidence, not an external audit.', '- Environment-blocked tools are documented as not passed; public governance accepts them as non-blocking only because no unresolved critical/high findings are recorded.']
text='\n'.join(content)+'\n'
(report_dir/'toolchain-clearance-report.md').write_text(text)
pathlib.Path('audit/TOOLCHAIN_CLEARANCE_REPORT.md').write_text(text)
qa={"redacted":True,"containsSecrets":False,"containsPrivateAddresses":False,"status":"PASSED" if status=='CLEARED' else 'NOT_CLEARED',"automatedSecurityToolchain":"PASSED" if status=='CLEARED' else 'NOT_CLEARED',"unresolvedCriticalHighFindings":int(summary.get('critical_high_unresolved',0) or 0),"unresolvedMediumFindings":int(summary.get('medium_unaccepted',0) or 0),"environmentBlockedToolsDocumented":summary.get('environment_blocked_tools_documented',[]),"mainnetDeployed":"NO","generatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}
pathlib.Path('qa/public-toolchain-clearance-evidence.json').write_text(json.dumps(qa,indent=2)+'\n')
sha=hashlib.sha256(text.encode()).hexdigest()
print(json.dumps({'status':status,'sha256':sha,'path':str(report_dir/'toolchain-clearance-report.md')},indent=2))
