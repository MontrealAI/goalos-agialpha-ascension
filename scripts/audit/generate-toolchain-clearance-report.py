#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib, sys
report_dir = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else pathlib.Path('audit/reports/latest.txt').read_text().strip())
summary_path = report_dir / 'audit-summary.json'
summary = json.loads(summary_path.read_text()) if summary_path.exists() else {'tools': [], 'mainnet_blockers': ['missing audit summary']}
blockers = []
for tool in summary.get('tools', []):
    if tool.get('blocks_technical_mainnet_readiness'):
        blockers.extend(tool.get('blockers', []))
blockers.extend(summary.get('mainnet_blockers', []))
status = 'NOT_CLEARED' if blockers else 'CLEARED'
content = ['# Automated Security Toolchain Clearance Report','',f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",f"Clearance: **{status}**",'', '## Blockers']
content += [f"- {b}" for b in blockers] or ['- No blockers recorded in automated summary.']
content += ['', '## Boundary', '- This is automated/internal security-toolchain evidence, not an external audit.', '- Technical mainnet readiness remains separate from founder deployment authorization.']
text='\n'.join(content)+'\n'
(report_dir/'toolchain-clearance-report.md').write_text(text)
pathlib.Path('audit/TOOLCHAIN_CLEARANCE_REPORT.md').write_text(text)
sha=hashlib.sha256(text.encode()).hexdigest()
print(json.dumps({'status':status,'sha256':sha,'path':str(report_dir/'toolchain-clearance-report.md')},indent=2))
