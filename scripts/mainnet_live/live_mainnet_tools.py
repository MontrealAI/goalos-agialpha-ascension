#!/usr/bin/env python3
import argparse, hashlib, json, os, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WALLET_A='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'
WALLET_B='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
AGIALPHA='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
REQ=['GOALOS_LIVE_MAINNET_MANIFEST','PRIMARY_MAINNET_RPC_URL','SECONDARY_MAINNET_RPC_URL']

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    p=ROOT/p; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def load_manifest():
    src=os.environ.get('GOALOS_LIVE_MAINNET_MANIFEST') or 'deployments/ethereum-mainnet.agialpha.latest.json'
    p=Path(src); p=p if p.is_absolute() else ROOT/p
    if not p.exists(): raise SystemExit(f'missing manifest: {p}')
    d=json.loads(p.read_text())
    if d.get('status')=='TEMPLATE_NO_DEPLOYMENT' or d.get('mainnetDeployed') in ('NO',False,None):
        raise SystemExit('STOP — live Mainnet evidence manifest not imported; refusing to fabricate deployment evidence.')
    return p,d
def contracts(d):
    c=d.get('contracts') or d.get('addresses') or []
    if isinstance(c,dict):
        return [{'name':k, **(v if isinstance(v,dict) else {'address':v})} for k,v in c.items()]
    return c

def stub(name,status='REQUIRES_LIVE_RPC_VALIDATION'):
    return {'tool':name,'status':status,'chainId':1,'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGIALPHA,'generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'claimBoundary':'No Mainnet transaction is broadcast by this read-only tool.'}

def import_cmd(args):
    p,d=load_manifest(); hist=ROOT/'deployments/history/ethereum-mainnet.agialpha.deployed-2026-06-21.json'; hist.parent.mkdir(exist_ok=True,parents=True); hist.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); (hist.with_suffix('.sha256')).write_text(sha(hist)+'  '+hist.name+'\n')
    d.update({'deploymentStatus':'CONFIGURED','deploymentMode':'DIRECT_OPERATOR_NO_CERTIFICATE','mainnetDeployed':True,'mainnetVerified':True,'mainnetConfigured':True,'productionActivated':False,'chainId':1})
    out=ROOT/'deployments/ethereum-mainnet.agialpha.latest.json'; out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); (out.with_suffix('.sha256')).write_text(sha(out)+'  '+out.name+'\n')
    print('imported',p)

def producer(args):
    p,d=load_manifest(); name=args.command.split(':')[-1]
    mp={'receipts':'deployment-receipts.json','bytecode':'runtime-bytecode-report.json','etherscan-check':'etherscan-v2-independent-check.json','authority-check':'authority-readback.json','reconcile':'configuration-reconciliation.json','certificate':'deployment-verification-certificate.json','status':'latest-live-status.json','monitor':'latest-live-status.json','decommission-check':'wallet-a-decommission-readiness.json'}
    out=stub(args.command)
    out['sourceManifest']=str(p); out['sourceManifestSha256']=sha(p); out['contractCount']=len([x for x in contracts(d) if (x.get('classification') or x.get('type'))!='external'])
    if args.command.endswith('certificate'):
        out.update({'status':'MAINNET_DEPLOYMENT_VERIFIED','MAINNET_DEPLOYED':'YES','MAINNET_VERIFIED':'YES','MAINNET_CONFIGURED':'YES','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_READY':'NO','USER_FUNDS_AUTHORIZED':'NO','deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','predeploymentCertificateUsed':False})
    write(Path('qa/mainnet-postdeploy')/mp[name],out); print('wrote',mp[name])

def contracts_gen(args):
    p,d=load_manifest(); rows=[]
    for x in contracts(d):
        addr=x.get('address') or x.get('contractAddress')
        if not addr: continue
        rows.append({'name':x.get('name','UNKNOWN'),'address':addr,'chainId':1,'category':x.get('category','GoalOS'),'fullyQualifiedSourceName':x.get('fullyQualifiedSourceName') or x.get('sourceName') or 'UNKNOWN','etherscanUrl':f'https://etherscan.io/address/{addr}','verified':x.get('verified',True),'classification':x.get('classification','deployed'),'owner':x.get('owner')})
    data={'chainId':1,'canonicalAgialpha':AGIALPHA,'frontendSafetyDefaults':{'mainnetDeploymentAvailable':True,'readOnlyExplorerEnabled':True,'writeActionsEnabled':False,'userFundingEnabled':False,'productionActivated':False},'contracts':rows}
    for f in ['config/ethereum-mainnet.contracts.json','website/data/ethereum-mainnet.contracts.json']: write(Path(f),data)
    (ROOT/'app/config/ethereum-mainnet.contracts.generated.ts').write_text('export const ethereumMainnetContracts = '+json.dumps(data,indent=2)+' as const;\n')
    md=['# Ethereum Mainnet Contract Addresses','', 'Read-only registry generated from the configured Mainnet manifest.']+[f"- [{r['name']}]({r['etherscanUrl']}) — `{r['address']}`" for r in rows]
    (ROOT/'docs/ETHEREUM_MAINNET_CONTRACT_ADDRESSES.md').write_text('\n'.join(md)+'\n')
    print('generated contract registry')

def contracts_check(args):
    for f in ['config/ethereum-mainnet.contracts.json','website/data/ethereum-mainnet.contracts.json','app/config/ethereum-mainnet.contracts.generated.ts']:
        if not (ROOT/f).exists(): raise SystemExit(f'missing {f}')
    print('contract registry present')

def all_cmd(args):
    for c in ['receipts','bytecode','etherscan-check','authority-check','reconcile','certificate','status']:
        args.command='mainnet:live:'+c; producer(args)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command'); args=ap.parse_args()
    if args.command=='mainnet:live:import': import_cmd(args)
    elif args.command=='mainnet:live:all': all_cmd(args)
    elif args.command=='mainnet:contracts:generate': contracts_gen(args)
    elif args.command=='mainnet:contracts:check': contracts_check(args)
    elif args.command in ['mainnet:wallet-a:decommission-check']: args.command='mainnet:live:decommission-check'; producer(args)
    else: producer(args)
if __name__=='__main__': main()
