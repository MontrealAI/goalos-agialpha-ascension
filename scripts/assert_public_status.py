#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.release.current_mainnet_state import normalize, StateError
try:
    state=normalize()
except StateError as exc:
    print(f'Public status assertion failed: {exc}'); sys.exit(1)
docs=['README.md','START_HERE.md','docs/CURRENT_STATUS.md','docs/START_HERE_MAINNET.md','docs/ETHEREUM_MAINNET.md']
required=[
 'Ethereum Mainnet deployment | PASS — YES',
 'Mainnet configuration | PASS — YES',
 'GoalOS contracts | 48',
 'Canonical external AGIALPHA | 1',
 'Operator verification evidence | PASS — 48/48',
 'Postdeployment operator evidence | PASS — VERIFIED_AND_CONFIGURED',
 'Phase-B grants | PASS — 14/14',
 'Permanent authority | PASS — Wallet B / Ledger',
 'Wallet A managed roles | PASS — 0',
 'Predeployment authorization | NOT_APPLICABLE — DIRECT_OPERATOR_NO_CERTIFICATE',
 'Independent live revalidation | PENDING_EXTERNAL_INPUT',
 'Source-identity reproducibility | PENDING',
 'Production activation | NOT_ACTIVATED',
 'User-fund authorization | NO',
]
forbidden=['External audit completion | NO','Ethereum Mainnet technical readiness: NO','Ethereum Mainnet deployment authorization: NO','Ethereum Mainnet authorization: NO','Stage-B/live postdeployment check | BLOCKED','external audit completion required']
errors=[]
combined=''
for rel in docs:
    path=ROOT/rel
    if not path.exists(): errors.append(f'{rel}: missing'); continue
    text=path.read_text(encoding='utf-8',errors='ignore')
    combined += text + '\n'
    for phrase in required:
        if phrase not in text: errors.append(f'{rel}: missing {phrase}')
for phrase in forbidden:
    if phrase in combined: errors.append(f'active docs contain stale phrase: {phrase}')
if 'No external-audit claim is made by this release.' not in combined:
    errors.append('missing neutral external-audit disclosure')
if 'externally audited' in combined.lower() and 'not externally audited' not in combined.lower():
    errors.append('active docs claim external audit')
if state['overallApplicableResult']!='PASS': errors.append('canonical release state is not PASS')
if errors:
    print('Public status assertion failed:'); print('\n'.join('- '+e for e in errors)); sys.exit(1)
print('Public status assertion passed: current direct-operator postdeployment status is lifecycle-aware and bounded.')
