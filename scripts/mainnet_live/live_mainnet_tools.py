#!/usr/bin/env python3
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WALLET_A='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'
WALLET_B='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
AGIALPHA='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
POSTDEPLOY_CLAIM_BOUNDARY='This evidence reports Ethereum Mainnet deployment, verification, and configuration mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, user-fund authorization, or production activation.'

PRIMARY_RPC_ENV_NAMES=['PRIMARY_MAINNET_RPC_URL','PRIVATE_MAINNET_RPC_URL','MAINNET_RPC_URL','ETHEREUM_MAINNET_RPC_URL']
SECONDARY_RPC_ENV_NAMES=['SECONDARY_MAINNET_RPC_URL','PRIVATE_SECONDARY_MAINNET_RPC_URL','MAINNET_SECONDARY_RPC_URL','ETHEREUM_MAINNET_SECONDARY_RPC_URL']

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

def first_env(names):
    for name in names:
        if os.environ.get(name):
            return name
    return None

def rpc_status():
    primary_name=first_env(PRIMARY_RPC_ENV_NAMES)
    secondary_name=first_env(SECONDARY_RPC_ENV_NAMES)
    primary=bool(primary_name)
    secondary=bool(secondary_name)
    if primary and secondary:
        comparison='PRIMARY_AND_SECONDARY_CONFIGURED_FOR_OPERATOR_CI'
    elif primary:
        comparison='MISSING_SECONDARY_MAINNET_RPC_URL'
    else:
        comparison='MISSING_PRIMARY_MAINNET_RPC_URL'
    return {
        'primaryMainnetRpcConfigured':primary,
        'secondaryMainnetRpcConfigured':secondary,
        'primaryMainnetRpcEnv':primary_name,
        'secondaryMainnetRpcEnv':secondary_name,
        'etherscanApiConfigured':bool(os.environ.get('ETHERSCAN_API_KEY')),
        'providerComparison':comparison,
        'acceptedPrimaryAliases':PRIMARY_RPC_ENV_NAMES,
        'acceptedSecondaryAliases':SECONDARY_RPC_ENV_NAMES,
    }

def stub(name,status='REQUIRES_LIVE_RPC_VALIDATION'):
    out={'tool':name,'status':status,'chainId':1,'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGIALPHA,'generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'claimBoundary':POSTDEPLOY_CLAIM_BOUNDARY,'transactionBoundary':'No Mainnet transaction is broadcast by this read-only tool; RPC URLs and API keys are never printed.'}
    out.update(rpc_status())
    return out

def validate_seed(args):
    p,d=load_manifest()
    cs=contracts(d)
    goalos=[x for x in cs if (x.get('classification') or x.get('type'))!='external']
    txs=d.get('transactions') or []
    phase=d.get('phaseBGrants') or []
    failures=[]
    if d.get('chainId')!=1: failures.append('chainId must be 1')
    if len(cs)!=49: failures.append(f'manifest entries must be 49, got {len(cs)}')
    if len(goalos)!=48: failures.append(f'GoalOS contracts must be 48, got {len(goalos)}')
    addrs=[(x.get('address') or x.get('contractAddress') or '').lower() for x in cs]
    if len(set(addrs))!=len(addrs): failures.append('duplicate contract address')
    if len(txs)!=48 or len(set(txs))!=48: failures.append('deployment transaction hashes must be 48 unique values')
    if len(phase)!=14: failures.append(f'Phase-B grants must be 14, got {len(phase)}')
    if d.get('agialphaToken','').lower()!=AGIALPHA.lower(): failures.append('canonical AGIALPHA mismatch')
    out=stub('mainnet:live:validate-seed','PASSED_NO_STAGE_B' if not failures else 'FAILED')
    out.update({'sourceManifest':str(p),'sourceManifestSha256':sha(p),'manifestEntries':len(cs),'goalosContracts':len(goalos),'deploymentTransactions':len(txs),'phaseBGrants':len(phase),'canEmitStageBPass':False,'failures':failures})
    write(Path('qa/mainnet-postdeploy/seed-validation.json'),out)
    print('seed validation',out['status'])
    if failures: raise SystemExit('; '.join(failures))

def revalidate_live(args):
    status=rpc_status()
    if not status['primaryMainnetRpcConfigured']:
        raise SystemExit('LIVE OPERATOR REVALIDATION PENDING: missing primary Mainnet RPC. Accepted aliases: '+','.join(PRIMARY_RPC_ENV_NAMES))
    if not status['secondaryMainnetRpcConfigured']:
        raise SystemExit('LIVE OPERATOR REVALIDATION PENDING: missing secondary Mainnet RPC. Accepted aliases: '+','.join(SECONDARY_RPC_ENV_NAMES))
    if not status['etherscanApiConfigured']:
        raise SystemExit('LIVE OPERATOR REVALIDATION PENDING: missing ETHERSCAN_API_KEY')
    # postdeploy_assurance.py performs read-only receipt/runtime/authority calls and certificate gating.
    for command in ['mainnet:revalidate','mainnet:verify','mainnet:authority-readback']:
        result=subprocess.run([sys.executable,str(ROOT/'scripts/mainnet_live/postdeploy_assurance.py'),command],cwd=ROOT)
        if result.returncode!=0:
            raise SystemExit(result.returncode)
    print('LIVE OPERATOR REVALIDATION: read-only evidence generated; run npm run mainnet:postdeploy:certificate after review')

def import_cmd(args):
    p,d=load_manifest(); hist=ROOT/'deployments/history/ethereum-mainnet.agialpha.deployed-2026-06-21.json'; hist.parent.mkdir(exist_ok=True,parents=True); hist.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); (hist.with_suffix('.sha256')).write_text(sha(hist)+'  '+hist.name+'\n')
    d.update({'deploymentStatus':'CONFIGURED','deploymentMode':'DIRECT_OPERATOR_NO_CERTIFICATE','mainnetDeployed':True,'mainnetVerified':True,'mainnetConfigured':True,'productionActivated':False,'chainId':1})
    out=ROOT/'deployments/ethereum-mainnet.agialpha.latest.json'; out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); (out.with_suffix('.sha256')).write_text(sha(out)+'  '+out.name+'\n')
    print('imported',p)

def producer(args):
    p,d=load_manifest(); raw=args.command.split('mainnet:live:')[-1] if 'mainnet:live:' in args.command else args.command.split(':')[-1]
    aliases={'import-seed':'import','doctor':'doctor','verification':'etherscan-check','authority':'authority-check','roles':'roles','non-role-authority':'non-role-authority','phase-b':'phase-b','fork':'fork','fork:gate2':'fork-gate2','fork:gate3':'fork-gate3','fork:gate4':'fork-gate4','fork:gates':'fork-gates'}
    name=aliases.get(raw,raw)
    mp={'doctor':'live-doctor.json','receipts':'deployment-receipts.json','bytecode':'runtime-bytecode-report.json','etherscan-check':'etherscan-v2-independent-check.json','authority-check':'authority-readback.json','roles':'role-holder-readback.json','non-role-authority':'non-role-authority-readback.json','phase-b':'phase-b-grants-readback.json','reconcile':'configuration-reconciliation.json','certificate':'deployment-verification-certificate.json','status':'latest-live-status.json','monitor':'latest-live-status.json','decommission-check':'wallet-a-decommission-readiness.json','fork':'live-fork-plan.json','fork-gate2':'live-fork-gate2.json','fork-gate3':'live-fork-gate3.json','fork-gate4':'live-fork-gate4.json','fork-gates':'live-fork-gates.json'}
    out=stub(args.command)
    out['sourceManifest']=str(p); out['sourceManifestSha256']=sha(p); out['contractCount']=len([x for x in contracts(d) if (x.get('classification') or x.get('type'))!='external'])
    if name == 'certificate':
        out.update({'status':'BLOCKED_UNTIL_READ_ONLY_LIVE_EVIDENCE_PASSES','deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','predeploymentCertificateUsed':False,'productionActivated':False})
    if name.startswith('fork'):
        out.update({'status':'NOT_RUN_REQUIRES_READ_ONLY_MAINNET_FORK','livePublicTransactions':'FORBIDDEN','productionActivated':False})
    write(Path('qa/mainnet-postdeploy')/mp[name],out); print('wrote',mp[name])

def contracts_gen(args):
    p,d=load_manifest(); rows=[]
    for x in contracts(d):
        addr=x.get('address') or x.get('contractAddress')
        if not addr: continue
        rows.append({'name':x.get('name','UNKNOWN'),'address':addr,'chainId':1,'category':x.get('category','GoalOS'),'fullyQualifiedSourceName':x.get('fullyQualifiedSourceName') or x.get('sourceName') or 'UNKNOWN','etherscanUrl':f'https://etherscan.io/address/{addr}','verified':x.get('verified','REQUIRES_INDEPENDENT_CHECK'),'classification':x.get('classification','deployed'),'owner':x.get('owner')})
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
    for c in ['doctor','receipts','bytecode','etherscan-check','authority-check','roles','non-role-authority','phase-b','reconcile','certificate','status']:
        args.command='mainnet:live:'+c; producer(args)
    status=rpc_status()
    missing=[]
    if not status['primaryMainnetRpcConfigured']:
        missing.append('PRIMARY_MAINNET_RPC_URL')
    if not status['secondaryMainnetRpcConfigured']:
        missing.append('SECONDARY_MAINNET_RPC_URL')
    if not status['etherscanApiConfigured']:
        missing.append('ETHERSCAN_API_KEY')
    if missing:
        raise SystemExit('mainnet:live:all fail-closed: generated PENDING artifacts only; live read-only validation blocked by missing '+', '.join(missing))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command'); args=ap.parse_args()
    if args.command in ('mainnet:live:import','mainnet:live:import-seed'): import_cmd(args)
    elif args.command=='mainnet:live:validate-seed': validate_seed(args)
    elif args.command=='mainnet:live:revalidate': revalidate_live(args)
    elif args.command=='mainnet:live:all': all_cmd(args)
    elif args.command=='mainnet:contracts:generate': contracts_gen(args)
    elif args.command=='mainnet:contracts:check': contracts_check(args)
    elif args.command in ['mainnet:wallet-a:decommission-check']: args.command='mainnet:live:decommission-check'; producer(args)
    else: producer(args)
if __name__=='__main__': main()
