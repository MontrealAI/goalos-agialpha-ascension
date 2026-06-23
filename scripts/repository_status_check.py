from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
required=['README.md','START_HERE.md','GITHUB_REPOSITORY_SETTINGS.md','CREATE_REPOSITORY_WEB_UI_GUIDE.md','LICENSE_DECISION.md','SECURITY.md','CONTRIBUTING.md','GOVERNANCE.md','docs/REPOSITORY_STATUS.md','docs/SAFE_CLAIMS.md']
missing=[p for p in required if not (ROOT/p).exists()]
if missing:
 print('Missing required files:'); [print('-',p) for p in missing]; sys.exit(1)
readme=(ROOT/'README.md').read_text(encoding='utf-8')
state=json.loads((ROOT/'qa/mainnet-release-state.json').read_text())
must=['Not externally audited','Ethereum Mainnet deployment | PASS — YES','Mainnet configuration | PASS — YES','Operator verification evidence | PASS — 48/48','Wallet A managed roles | PASS — 0','Independent live revalidation | PENDING_EXTERNAL_INPUT','AGIALPHA','0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA']
for item in must:
 if item.lower() not in readme.lower(): print(f'README missing required status phrase: {item}'); sys.exit(1)
if state['summary']['ETHEREUM_MAINNET_DEPLOYED']!='YES' or state['summary']['MAINNET_CONFIGURED']!='YES':
 print('release-state deployment/configuration mismatch'); sys.exit(1)
print('Repository status check passed.')
