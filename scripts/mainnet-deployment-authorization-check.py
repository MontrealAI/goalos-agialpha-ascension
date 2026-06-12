#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 a=argparse.ArgumentParser(); a.add_argument('--certificate',default='qa/mainnet-authorization-certificate.json'); ns=a.parse_args(); c=json.loads((ROOT/ns.certificate).read_text())
 blockers=[]
 if c.get('technicallyMainnetReady')!='YES': blockers.append('TECHNICALLY_MAINNET_READY is not YES.')
 if c.get('mainnetDeploymentAuthorized')!='YES' or c.get('MAINNET_DEPLOYMENT_AUTHORIZED')!='YES': blockers+=c.get('blockers') or ['Certificate deployment authorization is not YES.']
 if c.get('ciCanDeployMainnet') is not False: blockers.append('CI deployment must be disabled.')
 if c.get('privateOperatorAuthorizationPackageRequired') is not False: blockers.append('Private operator authorization package must not be required.')
 status='NO' if blockers else 'YES'
 out={'status':status,'MAINNET_DEPLOYMENT_AUTHORIZED':status,'mainnetDeploymentAuthorized':status,'commit':c.get('commit'),'chain':'ethereum','chainId':1,'agialphaToken':c.get('agialphaToken'),'mainnetDeployed':'NO','runtimeSecretsRequiredForBroadcast':True,'runtimeSecretsStoredInGitHub':False,'privateOperatorAuthorizationPackageRequired':False,'evidence':c.get('evidence',{}),'blockers':blockers,'generatedAt':now(),'generatedBy':'scripts/mainnet-deployment-authorization-check.py'}
 for f in ['docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json','docs/MAINNET_AUTHORIZATION_DECISION.json']: (ROOT/f).write_text(json.dumps(out,indent=2)+'\n')
 md=f"# Mainnet Deployment Authorization Decision\n\nEthereum Mainnet deployment authorization: **{status}**.\n\nMAINNET_DEPLOYMENT_AUTHORIZED: **{status}**\n\nMAINNET_DEPLOYED: **NO**\n\nPublic repository governance authorizes only manual, local, typed-confirmation gated deployment. Runtime RPC/key are not stored in GitHub.\n\n## Blockers\n"+("\n".join(f"- {b}" for b in blockers) if blockers else "- None.")+"\n"
 for f in ['docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md','docs/MAINNET_AUTHORIZATION_DECISION.md']: (ROOT/f).write_text(md)
 (ROOT/'qa/public-mainnet-deployment-authorization-evidence.json').write_text(json.dumps({'redacted':True,'containsSecrets':False,'containsPrivateAddresses':False,**out},indent=2)+'\n')
 print(json.dumps(out,indent=2)); sys.exit(0 if status=='YES' else 1)
if __name__=='__main__': main()
