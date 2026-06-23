#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'qa/mainnet-release-state.json').read_text())
docs=['README.md','START_HERE.md','docs/CURRENT_STATUS.md','docs/START_HERE_MAINNET.md']
required=[
 'Deployment path | `DIRECT_OPERATOR_NO_CERTIFICATE`',
 'Predeployment authorization | NOT_APPLICABLE',
 'Ethereum Mainnet deployment | PASS — YES',
 'Mainnet configuration | PASS — YES',
 'GoalOS contracts | PASS — 48',
 'Canonical registry | PASS — 49 entries',
 'Operator verification evidence | PASS — 48/48',
 'Postdeployment operator evidence | PASS — VERIFIED_AND_CONFIGURED',
 'Phase-B grants | PASS — 14/14',
 'Permanent authority | PASS — Wallet B / Ledger',
 'Wallet A managed roles | PASS — 0',
 'Independent live revalidation | PENDING_EXTERNAL_INPUT',
 'Production activation | NOT ACTIVATED',
 'User-fund authorization | NO',
]
errors=[]
if state['predeploymentAuthorization']['status']!='NOT_USED_DIRECT_OPERATOR_PATH': errors.append('release state predeployment authorization mismatch')
if state['deployment']['status']!='DEPLOYED' or state['summary']['ETHEREUM_MAINNET_DEPLOYED']!='YES': errors.append('release state deployment mismatch')
if state['postdeployment']['status']!='VERIFIED_AND_CONFIGURED': errors.append('release state postdeployment mismatch')
if state['summary']['WALLET_A_RESIDUAL_MANAGED_ROLES']!=0: errors.append('Wallet A managed roles must equal zero')
combined=''
for rel in docs:
    text=(ROOT/rel).read_text(encoding='utf-8',errors='ignore')
    combined+=text+'\n'
    for phrase in required:
        if phrase not in text: errors.append(f'{rel}: missing {phrase}')
for forbidden in ['External audit completion | NO','Ethereum Mainnet technical readiness: NO','Ethereum Mainnet deployment authorization: NO','Ethereum Mainnet authorization: NO','Stage-B/live postdeployment check | BLOCKED']:
    if forbidden in combined and 'not externally audited' not in forbidden.lower(): errors.append(f'active docs contain stale phrase: {forbidden}')
if 'No external-audit claim is made by this release.' not in combined: errors.append('missing neutral external-audit disclosure')
if errors:
    print('Public status assertion failed:'); print('\n'.join('- '+e for e in errors)); sys.exit(1)
print('Public status assertion passed: current direct-operator postdeployment status is lifecycle-aware and bounded.')
