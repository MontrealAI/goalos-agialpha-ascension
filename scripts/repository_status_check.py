#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.release.current_mainnet_state import normalize, StateError
required=['README.md','START_HERE.md','GITHUB_REPOSITORY_SETTINGS.md','CREATE_REPOSITORY_WEB_UI_GUIDE.md','LICENSE_DECISION.md','SECURITY.md','CONTRIBUTING.md','GOVERNANCE.md','docs/REPOSITORY_STATUS.md','docs/SAFE_CLAIMS.md']
missing=[p for p in required if not (ROOT/p).exists()]
if missing:
 print('Missing required files:'); [print('-',p) for p in missing]; sys.exit(1)
try: state=normalize()
except StateError as exc: print(f'Repository status check failed: {exc}'); sys.exit(1)
readme=(ROOT/'README.md').read_text(encoding='utf-8')
for item in ['Ethereum Mainnet deployment | PASS — YES','Mainnet configuration | PASS — YES','Operator verification evidence | PASS — 48/48','Wallet A managed roles | PASS — 0','Independent live revalidation | PENDING_EXTERNAL_INPUT','Source-identity reproducibility | PENDING','AGIALPHA','0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA']:
 if item.lower() not in readme.lower(): print(f'README missing required status phrase: {item}'); sys.exit(1)
if state['overallApplicableResult']!='PASS': print('release-state adapter did not PASS'); sys.exit(1)
print('Repository status check passed.')
