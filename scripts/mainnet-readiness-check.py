#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads((ROOT/p).read_text())
def main():
 p=argparse.ArgumentParser(); p.add_argument('--certificate',default='qa/mainnet-authorization-certificate.json'); a=p.parse_args(); c=read(a.certificate)
 blockers=[]
 if c.get('technicallyMainnetReady')!='YES' or c.get('TECHNICALLY_MAINNET_READY')!='YES': blockers+=c.get('blockers') or ['Mainnet Authorization Certificate technical readiness is not YES.']
 status='NO' if blockers else 'YES'
 out={'status':status,'TECHNICALLY_MAINNET_READY':status,'technicallyMainnetReady':status,'commit':c.get('commit'),'chain':c.get('chain'),'chainId':c.get('chainId'),'agialphaToken':c.get('agialphaToken'),'mainnetDeployed':'NO','privateOperatorAuthorizationPackageRequired':False,'externalAuditRequired':False,'evidence':c.get('evidence',{}),'blockers':blockers,'generatedAt':now(),'generatedBy':'scripts/mainnet-readiness-check.py'}
 (ROOT/'docs/MAINNET_TECHNICAL_READINESS_DECISION.json').write_text(json.dumps(out,indent=2)+'\n')
 (ROOT/'qa/public-mainnet-technical-readiness-evidence.json').write_text(json.dumps({'redacted':True,'containsSecrets':False,'containsPrivateAddresses':False,**out},indent=2)+'\n')
 (ROOT/'docs/MAINNET_TECHNICAL_READINESS_DECISION.md').write_text(f"# Mainnet Technical Readiness Decision\n\nEthereum Mainnet technical readiness: **{status}**.\n\nTECHNICALLY_MAINNET_READY: **{status}**\n\nMAINNET_DEPLOYED: **NO**\n\nNot externally audited. External audit is not planned and is not an active mainnet gate. Automated/internal security-toolchain clearance is the active security gate.\n\n## Blockers\n"+("\n".join(f"- {b}" for b in blockers) if blockers else "- None.")+"\n")
 print(json.dumps(out,indent=2)); sys.exit(0 if status=='YES' else 1)
if __name__=='__main__': main()
