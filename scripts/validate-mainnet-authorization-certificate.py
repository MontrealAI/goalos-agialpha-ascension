#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
p=argparse.ArgumentParser(); p.add_argument('--certificate',default='qa/mainnet-authorization-certificate.json'); a=p.parse_args()
cert=json.loads((ROOT/a.certificate).read_text())
errors=[]
for k in ['schemaVersion','generatedAt','repository','commit','chain','chainId','agialphaToken','technicallyMainnetReady','mainnetDeploymentAuthorized','ethereumMainnetAuthorized','evidence','blockers']:
    if k not in cert: errors.append(f'missing {k}')
if cert.get('chain')!='ethereum' or cert.get('chainId')!=1: errors.append('certificate must target Ethereum Mainnet chainId 1')
if str(cert.get('agialphaToken','')).lower()!=AGI.lower(): errors.append('wrong AGIALPHA token')
if cert.get('mainnetDeployed')!='NO': errors.append('mainnetDeployed must be NO without transaction evidence')
if cert.get('ciCanDeployMainnet') is not False: errors.append('ciCanDeployMainnet must be false')
if cert.get('privateOperatorAuthorizationPackageRequired') is not False: errors.append('private operator package must not be required')
if cert.get('runtimeSecretsStoredInGitHub') is not False: errors.append('runtime secrets must not be stored in GitHub')
if cert.get('notExternallyAudited') is not True or cert.get('externalAuditRequired') is not False: errors.append('external-audit fields invalid')
if cert.get('technicallyMainnetReady')=='YES' and cert.get('blockers'): errors.append('YES certificate cannot have blockers')
print(json.dumps({'status':'PASSED' if not errors else 'FAILED','errors':errors},indent=2))
if errors: sys.exit(1)
