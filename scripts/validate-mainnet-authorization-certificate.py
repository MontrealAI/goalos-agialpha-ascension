#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
CERT=ROOT/'qa/mainnet-authorization-certificate.json'
AGIALPHA='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
required_yes=['technicallyMainnetReady','mainnetDeploymentAuthorized','ethereumMainnetAuthorized']
errors=[]
try: d=json.loads(CERT.read_text())
except Exception as e: print(f'certificate missing/unreadable: {e}'); sys.exit(1)
if d.get('schemaVersion')!='1.0': errors.append('schemaVersion must be 1.0')
if d.get('chain')!='ethereum' or d.get('chainId')!=1: errors.append('chain must be ethereum chainId 1')
if str(d.get('agialphaToken','')).lower()!=AGIALPHA.lower(): errors.append('AGIALPHA token mismatch')
for k in required_yes:
    if d.get(k)!='YES': errors.append(f'{k} must be YES')
for k in ['externalAuditPlanned','externalAuditRequired','legalTaxReviewClaimed','runtimeSecretsStoredInGitHub','ciCanDeployMainnet']:
    if d.get(k) is not False: errors.append(f'{k} must be false')
if d.get('mainnetDeployed')!='NO': errors.append('mainnetDeployed must be NO')
if d.get('runtimeSecretsRequiredForBroadcast') is not True: errors.append('runtimeSecretsRequiredForBroadcast must be true')
if d.get('blockers'): errors.append('blockers must be empty for final YES')
if errors:
    print('Mainnet Authorization Certificate validation failed:')
    [print(f'- {e}') for e in errors]
    sys.exit(1)
print('Mainnet Authorization Certificate validation passed.')
