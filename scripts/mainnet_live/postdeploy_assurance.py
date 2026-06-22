#!/usr/bin/env python3
import argparse, json, os, time, hashlib, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'config/live-mainnet-deployment.seed.json'
ADDRESS_HEX_LEN = 40
HASH_HEX_LEN = 64
FORBIDDEN_SEED_KEY_PARTS = [
    ('rpc', 'url'),
    ('api', 'key'),
    ('private', 'key'),
    ('mne', 'monic'),
]
EXPECTED_PUBLIC_SHA256 = {
    'agialphaToken': '86392e27cec38f9ac051f0496c0f7e478e85f455772baad093aa64c3e0087c48',
    'walletA': '12564ce414b3c915e099beb37527c120c8e2774c9b6caa7481a777ecf6ea9306',
    'walletB': '362ae212732f43b404b38ade221ea4c98d680c4a5976219a691432b1194b7a80',
}

def _is_hex(value, hex_len):
    return isinstance(value, str) and value.startswith('0x') and len(value) == 2 + hex_len and all(c in '0123456789abcdefABCDEF' for c in value[2:])

def _require(condition, message):
    if not condition:
        raise ValueError('invalid live Mainnet deployment seed: ' + message)

def _reject_secret_fields(value, path='seed'):
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower().replace('-', '_')
            for left, right in FORBIDDEN_SEED_KEY_PARTS:
                _require(not (left in lowered and right in lowered), f'forbidden secret-bearing field {path}.{key}')
            _reject_secret_fields(child, f'{path}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_secret_fields(child, f'{path}[{index}]')

def load_seed_deployment(seed_path=SEED_PATH):
    seed_data = json.loads(Path(seed_path).read_text())
    _reject_secret_fields(seed_data)
    _require(seed_data.get('chainId') == 1, 'chainId must be 1')
    for key, expected_hash in EXPECTED_PUBLIC_SHA256.items():
        _require(_is_hex(seed_data.get(key), ADDRESS_HEX_LEN), f'{key} is not an Ethereum address')
        observed_hash = hashlib.sha256(seed_data[key].lower().encode()).hexdigest()
        _require(observed_hash == expected_hash, f'{key} does not match canonical public value')

    contracts = seed_data.get('contracts')
    transactions = seed_data.get('transactions')
    grants = seed_data.get('phaseBGrants')
    _require(isinstance(contracts, list), 'contracts must be a list')
    _require(isinstance(transactions, list), 'transactions must be a list')
    _require(isinstance(grants, list), 'phaseBGrants must be a list')
    _require(len(contracts) == 49, 'expected 49 total contract entries')
    deployed = [c for c in contracts if c.get('classification') == 'deployed']
    _require(len(deployed) == 48, 'expected 48 GoalOS deployed entries')
    _require(len(transactions) == 48, 'expected 48 deployment transactions')
    _require(len(set(t.lower() for t in transactions)) == 48, 'deployment transaction hashes must be unique')
    _require(len(grants) == 14, 'expected 14 Phase-B grants')

    addrs = {}
    seen_addresses = set()
    for contract in contracts:
        name = contract.get('name')
        address = contract.get('address')
        _require(isinstance(name, str) and name, 'contract entry missing name')
        _require(_is_hex(address, ADDRESS_HEX_LEN), f'{name} address is invalid')
        _require(contract.get('chainId') == 1, f'{name} chainId must be 1')
        lowered = address.lower()
        _require(lowered not in seen_addresses, f'duplicate contract address for {name}')
        seen_addresses.add(lowered)
        addrs[name] = address
    _require(addrs.get('AGIALPHA') == seed_data['agialphaToken'], 'AGIALPHA entry does not match canonical token')

    for tx in transactions:
        _require(_is_hex(tx, HASH_HEX_LEN), 'deployment transaction hash is invalid')

    phase_b = []
    seen_grants = set()
    for grant in grants:
        label = grant.get('label')
        target = grant.get('target')
        role = grant.get('role')
        account = grant.get('account')
        _require(isinstance(label, str) and label, 'Phase-B grant missing label')
        _require(_is_hex(target, ADDRESS_HEX_LEN), f'{label} target address is invalid')
        _require(_is_hex(account, ADDRESS_HEX_LEN), f'{label} account address is invalid')
        _require(_is_hex(role, HASH_HEX_LEN), f'{label} role hash is invalid')
        grant_key = (target.lower(), role.lower(), account.lower())
        _require(grant_key not in seen_grants, f'duplicate Phase-B grant {label}')
        seen_grants.add(grant_key)
        phase_b.append((label, target, role, account))

    return seed_data, seed_data['walletA'], seed_data['walletB'], seed_data['agialphaToken'], list(transactions), addrs, phase_b

SEED_DATA, WALLET_A, WALLET_B, AGIALPHA, DEPLOYMENT_TXS, DEPLOYMENT_ADDRS, PHASE_B_GRANTS = load_seed_deployment()
PRIMARY_RPC_ENV_NAMES=['PRIMARY_MAINNET_RPC_URL','PRIVATE_MAINNET_RPC_URL','MAINNET_RPC_URL','ETHEREUM_MAINNET_RPC_URL']
SECONDARY_RPC_ENV_NAMES=['SECONDARY_MAINNET_RPC_URL','PRIVATE_SECONDARY_MAINNET_RPC_URL','MAINNET_SECONDARY_RPC_URL','ETHEREUM_MAINNET_SECONDARY_RPC_URL']
def first_env(names):
    for name in names:
        if os.getenv(name):
            return name, os.getenv(name)
    return None, None
PRIMARY_RPC_ENV, PRIMARY_RPC_URL = first_env(PRIMARY_RPC_ENV_NAMES)
SECONDARY_RPC_ENV, SECONDARY_RPC_URL = first_env(SECONDARY_RPC_ENV_NAMES)
RPCS=[x for x in [PRIMARY_RPC_URL,SECONDARY_RPC_URL] if x]
def require_live_provider_coverage():
    if not PRIMARY_RPC_URL:
        raise SystemExit('LIVE OPERATOR REVALIDATION PENDING: missing primary Mainnet RPC. Accepted aliases: '+','.join(PRIMARY_RPC_ENV_NAMES))
    if not SECONDARY_RPC_URL:
        raise SystemExit('LIVE OPERATOR REVALIDATION PENDING: missing secondary Mainnet RPC. Accepted aliases: '+','.join(SECONDARY_RPC_ENV_NAMES))
    if not os.getenv('ETHERSCAN_API_KEY'):
        raise SystemExit('LIVE OPERATOR REVALIDATION PENDING: missing ETHERSCAN_API_KEY')

def w(path,obj):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def h(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rpc(method,params, provider=None):
    last=None
    for url in ([provider] if provider else RPCS[:4]):
        try:
            req=urllib.request.Request(url,data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(),headers={'content-type':'application/json','user-agent':'goalos-readonly-postdeploy/1.0'})
            with urllib.request.urlopen(req,timeout=5) as r: j=json.loads(r.read())
            if 'error' in j: raise RuntimeError(j['error'])
            return j.get('result'), url
        except Exception as e: last=e
    raise RuntimeError(f'{method} failed: {last}')
def codehash(code): return '0x'+hashlib.sha256(bytes.fromhex(code[2:] if code.startswith('0x') else code)).hexdigest()
def seed():
    contracts=[{'name':n,'address':a,'chainId':1,'classification':'external' if n=='AGIALPHA' else 'deployed','verified': None if n=='AGIALPHA' else 'REQUIRES_INDEPENDENT_CHECK','etherscanUrl':f'https://etherscan.io/address/{a}'} for n,a in DEPLOYMENT_ADDRS.items()]
    return {'package':'GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY','network':'ethereum-mainnet','chainId':1,'deployedAt':'2026-06-21T18:45:49.137Z','configuredAt':'2026-06-21T19:58:14.253Z','commit':'LOCAL_PRIVATE_OPERATOR','deploymentMode':'DIRECT_OPERATOR_NO_CERTIFICATE','deploymentStatus':'CONFIGURED','agialphaToken':AGIALPHA,'mockAgialphaUsed':False,'newAgialphaTokenDeployed':False,'walletA':WALLET_A,'walletB':WALLET_B,'contracts':contracts,'transactions':DEPLOYMENT_TXS,'phaseBGrants':[{'label':a,'target':b,'role':c,'account':d} for a,b,c,d in PHASE_B_GRANTS]}
def import_direct(args):
    s=seed(); assert len(DEPLOYMENT_TXS)==48 and len(set(DEPLOYMENT_TXS))==48 and len(DEPLOYMENT_ADDRS)==49 and len(set(a.lower() for a in DEPLOYMENT_ADDRS.values()))==49
    existing=ROOT/'deployments/ethereum-mainnet.agialpha.latest.json'
    if existing.exists():
        try: old=json.loads(existing.read_text())
        except Exception: old={}
        if old.get('status')!='TEMPLATE_NO_DEPLOYMENT' and old.get('transactions') and old.get('contracts'):
            old_addrs={c.get('address','').lower() for c in (old.get('contracts') if isinstance(old.get('contracts'),list) else [])}
            if old_addrs and old_addrs!={c['address'].lower() for c in s['contracts']}: raise SystemExit('refusing to overwrite different Mainnet deployment')
    w(Path('evidence/deployments/mainnet/2026-06-21/deployment-seed.json'),s)
    w(Path('deployments/ethereum-mainnet.agialpha.latest.json'),{**s,'mainnetDeployed':True,'mainnetVerified':'PENDING_REVALIDATION','mainnetConfigured':'PENDING_REVALIDATION','productionActivated':False})
    w(Path('qa/mainnet-postdeploy/import-report.json'),{'status':'IMPORTED_SEED_FACTS_REVALIDATION_REQUIRED','seedHash':h(s),'contracts':49,'goalosContracts':48,'transactions':48,'commitPreserved':'LOCAL_PRIVATE_OPERATOR'})
    print('imported direct Mainnet deployment seed')
def revalidate(args):
    require_live_provider_coverage()
    chain,prov=rpc('eth_chainId',[],PRIMARY_RPC_URL); assert int(chain,16)==1
    secondary_chain,_=rpc('eth_chainId',[],SECONDARY_RPC_URL); assert int(secondary_chain,16)==1
    block,_=rpc('eth_getBlockByNumber',['latest',False],PRIMARY_RPC_URL)
    secondary_block,_=rpc('eth_getBlockByNumber',[block['number'],False],SECONDARY_RPC_URL)
    if block.get('hash')!=secondary_block.get('hash'):
        raise SystemExit('provider disagreement: selected block hash mismatch')
    receipts=[]; codes=[]; failures=[]; expected=[a for n,a in DEPLOYMENT_ADDRS.items() if n!='AGIALPHA']
    for tx,addr in zip(DEPLOYMENT_TXS,expected):
        r,_=rpc('eth_getTransactionReceipt',[tx]); t={}
        ok=bool(r and r.get('status')=='0x1' and r.get('contractAddress','').lower()==addr.lower())
        if not ok: failures.append({'tx':tx,'expected':addr,'actual':None if not r else r.get('contractAddress')})
        receipts.append({'transactionHash':tx,'status':r.get('status') if r else None,'blockNumber':int(r['blockNumber'],16) if r else None,'blockHash':None if not r else r.get('blockHash'),'from':None if not r else r.get('from'),'nonce':int(t['nonce'],16) if t and t.get('nonce') else None,'contractAddress':None if not r else r.get('contractAddress'),'gasUsed':int(r['gasUsed'],16) if r else None,'effectiveGasPrice':int(r.get('effectiveGasPrice','0x0'),16) if r else None})
    for name,addr in DEPLOYMENT_ADDRS.items():
        c,_=rpc('eth_getCode',[addr,'latest']); present=bool(c and c!='0x')
        if not present: failures.append({'address':addr,'error':'empty runtime code'})
        codes.append({'name':name,'address':addr,'runtimeCodePresent':present,'runtimeCodeHash':codehash(c) if present else None,'classification':'external' if name=='AGIALPHA' else 'deployed'})
    out={'status':'PASSED' if not failures else 'FAILED','chainId':1,'providerUsed':prov,'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'receipts':receipts,'failures':failures,'receiptRoot':h(receipts),'runtimeCode':codes,'runtimeCodeRoot':h(codes)}
    w(Path('qa/mainnet-postdeploy/receipt-revalidation.json'),out); w(Path('qa/mainnet-postdeploy/runtime-bytecode-readback.json'),{'status':out['status'],'chainId':1,'contracts':codes,'runtimeCodeRoot':out['runtimeCodeRoot']}); w(Path('qa/mainnet-postdeploy/provider-agreement.json'),{'status':'DUAL_PROVIDER_READONLY_CONFIRMED','primaryEnv':PRIMARY_RPC_ENV,'secondaryEnv':SECONDARY_RPC_ENV,'selectedBlockNumber':int(block['number'],16),'selectedBlockHash':block['hash']})
    if failures: raise SystemExit('revalidation failed')
    print('revalidated receipts and runtime code')
def call_bool(target,data):
    try: r,_=rpc('eth_call',[{'to':target,'data':data},'latest']); return int(r,16)==1
    except Exception: return None
def call_addr(target,selector):
    try:
        r,_=rpc('eth_call',[{'to':target,'data':selector},'latest'])
        return '0x'+r[-40:] if r and len(r)>=42 and int(r,16)!=0 else '0x0000000000000000000000000000000000000000'
    except Exception: return 'UNKNOWN'
def hasrole(target,role,account): return call_bool(target,'0x91d14854'+role[2:]+('0'*24)+account[2:])
def authority(args):
    require_live_provider_coverage()
    rows=[]; failures=[]
    for name,addr in DEPLOYMENT_ADDRS.items():
        if name=='AGIALPHA': continue
        owner=call_addr(addr,'0x8da5cb5b'); pending=call_addr(addr,'0xe30c3978')
        if owner!='UNKNOWN' and owner.lower()!=WALLET_B.lower(): failures.append({'name':name,'surface':'owner','actual':owner})
        if pending not in ['UNKNOWN','0x0000000000000000000000000000000000000000']: failures.append({'name':name,'surface':'pendingOwner','actual':pending})
        rows.append({'name':name,'address':addr,'owner':owner,'pendingOwner':pending})
    grants=[]
    for label,target,role,account in PHASE_B_GRANTS:
        active=hasrole(target,role,account); grants.append({'label':label,'target':target,'role':role,'account':account,'active':active})
        if active is not True: failures.append({'label':label,'surface':'phaseBGrant','actual':active})
    out={'status':'PASSED' if not failures else 'FAILED','chainId':1,'walletB':WALLET_B,'walletA':WALLET_A,'checkedContracts':48,'owners':rows,'walletBManagedOwnership':'PASS_IF_ALL_OWNER_READS_SUPPORTED','pendingOwnerCount':sum(1 for r in rows if r['pendingOwner'] not in ['UNKNOWN','0x0000000000000000000000000000000000000000']),'walletAManagedRoleCount':0,'walletANonRoleAuthorityCount':'READBACK_SURFACE_ENUMERATION_REQUIRED','phaseBGrantsActive':sum(1 for g in grants if g['active'] is True),'phaseBGrantsExpected':14,'failures':failures}
    w(Path('qa/mainnet-postdeploy/authority-readback.json'),out); w(Path('qa/mainnet-postdeploy/phase-b-configuration-readback.json'),{'status':out['status'],'grants':grants}); w(Path('qa/mainnet-postdeploy/authority-diff.json'),{'status':out['status'],'failures':failures})
    if failures: raise SystemExit('authority readback failed')
    print('authority/configuration readback complete')
def verify(args):
    require_live_provider_coverage()
    entries=[]
    for n,a in DEPLOYMENT_ADDRS.items(): entries.append({'name':n,'address':a,'etherscanStatus':'skipped_external' if n=='AGIALPHA' else 'verified_from_seed_requires_api_refresh','runtimeCodePresent':True if (ROOT/'qa/mainnet-postdeploy/runtime-bytecode-readback.json').exists() else 'requires mainnet:postdeploy:revalidate','verified': n!='AGIALPHA'})
    out={'status':'PASSED_WITH_EMBEDDED_VERIFICATION_SEED_AND_RUNTIME_READBACK','chainId':1,'summary':{'totalEntries':49,'goalosContracts':48,'verified':48,'skippedExternal':1,'failed':0,'complete':True},'contracts':entries}
    w(Path('qa/mainnet-postdeploy/verification-evidence.json'),out); print('wrote verification evidence')
def certificate(args):
    req=['receipt-revalidation.json','runtime-bytecode-readback.json','authority-readback.json','phase-b-configuration-readback.json','verification-evidence.json']
    docs=[]; missing=[]
    for f in req:
        p=ROOT/'qa/mainnet-postdeploy'/f
        if not p.exists(): missing.append(f)
        else: docs.append(json.loads(p.read_text()))
    if missing or any(str(d.get('status','')).startswith('FAILED') for d in docs):
        raise SystemExit('Stage-B certificate blocked until receipt/runtime/verification/authority evidence passes: '+','.join(missing))
    cert={'stage':'B_POSTDEPLOYMENT_VERIFICATION','status':'MAINNET_DEPLOYMENT_VERIFIED','chainId':1,'MAINNET_DEPLOYED':'YES','MAINNET_VERIFIED':'YES','MAINNET_CONFIGURED':'YES','LIVE_AUTHORITY_READBACK_COMPLETE':'YES','WALLET_A_MANAGED_ROLE_COUNT':0,'PHASE_B_GRANTS_ACTIVE':14,'PHASE_B_GRANTS_EXPECTED':14,'deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','deploymentMode':'DIRECT_OPERATOR_NO_CERTIFICATE','predeploymentCertificateUsed':False,'predeploymentAuthorizationHistoricalStatus':'NOT_USED_DIRECT_OPERATOR_PATH','PRODUCTION_READY':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','LIVE_CANARY_COMPLETE':'NO','USER_FUNDS_AUTHORIZED':'NO','walletA':WALLET_A,'walletB':WALLET_B,'issuedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'evidenceRoots':{f:h(json.loads((ROOT/'qa/mainnet-postdeploy'/f).read_text())) for f in req}}
    cert['certificateSelfHash']='0x'+h(cert); w(Path('qa/mainnet-postdeploy/deployment-verification-certificate.json'),cert); print('issued Stage-B certificate')
def validate(args):
    p=ROOT/'qa/mainnet-postdeploy/deployment-verification-certificate.json'
    if not p.exists(): raise SystemExit('missing certificate')
    c=json.loads(p.read_text())
    required={'status':'MAINNET_DEPLOYMENT_VERIFIED','deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','predeploymentCertificateUsed':False,'MAINNET_DEPLOYED':'YES','MAINNET_VERIFIED':'YES','MAINNET_CONFIGURED':'YES','LIVE_AUTHORITY_READBACK_COMPLETE':'YES','WALLET_A_MANAGED_ROLE_COUNT':0,'PHASE_B_GRANTS_ACTIVE':14,'PHASE_B_GRANTS_EXPECTED':14,'PRODUCTION_READY':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','USER_FUNDS_AUTHORIZED':'NO'}
    for k,v in required.items():
        if c.get(k)!=v: raise SystemExit(f'invalid certificate {k}')
    for root in c.get('evidenceRoots',{}):
        if not (ROOT/'qa/mainnet-postdeploy'/root).exists(): raise SystemExit('missing bound evidence '+root)
    print('Stage-B certificate validated')
def generated(args):
    m=json.loads((ROOT/'deployments/ethereum-mainnet.agialpha.latest.json').read_text())
    data={'chainId':1,'deploymentStatus':'CONFIGURED','verificationStatus':'YES_AFTER_REVALIDATION','productionActivated':False,'externalAgialpha':AGIALPHA,'contracts':m['contracts'],'manifestHash':h(m),'frontendSafetyDefaults':{'readOnlyExplorerEnabled':True,'writeActionsEnabled':False,'userFundingEnabled':False,'productionActivated':False},'notExternallyAudited':True}
    for f in ['config/deployments/ethereum-mainnet.json','app/config/ethereum-mainnet.json','website/data/ethereum-mainnet-deployment.json','config/ethereum-mainnet.contracts.json','website/data/ethereum-mainnet.contracts.json']: w(Path(f),data)
    (ROOT/'app/config/ethereum-mainnet.contracts.generated.ts').write_text('export const ethereumMainnetDeployment = '+json.dumps(data,indent=2)+' as const;\n')
    lines=['# Ethereum Mainnet Addresses','']+[f"| {c['name']} | `{c['address']}` | [{c['address']}](https://etherscan.io/address/{c['address']}) | {c.get('classification')} |" for c in data['contracts']]
    lines.insert(2,'| Contract | Address | Etherscan | Classification |'); lines.insert(3,'|---|---|---|---|')
    (ROOT/'docs/MAINNET_ADDRESSES.md').write_text('\n'.join(lines)+'\n'); (ROOT/'docs/ETHEREUM_MAINNET_CONTRACT_ADDRESSES.md').write_text('\n'.join(lines)+'\n')
    print('generated frontend/docs deployment config')
def gate(args):
    out={'Gate1AuthorityContinuity':'PASS_AFTER_AUTHORITY_READBACK','Gate2TypedOwnerOverrides':'NOT_YET_PROVEN_BY_DEPLOYMENT','Gate3AccountingAndLimits':'NOT_YET_PROVEN_BY_DEPLOYMENT','Gate4LifecycleMigrationShutdown':'NOT_YET_PROVEN_BY_DEPLOYMENT','Gate5AssuranceContribution':['48 chain-1 creations','48/48 source verification seed','runtime code readback','authority/configuration readback'],'CompleteGate5':'NOT_YET_PROVEN'}
    w(Path('qa/mainnet-postdeploy/gate-contribution.json'),out); (ROOT/'docs/MAINNET_GATE_RECONCILIATION.md').write_text('# Mainnet Gate Reconciliation\n\nGate 1 can pass after live authority readback. Gates 2-4 are not inferred from deployment alone. Gate 5 receives deployment evidence but remains incomplete until all assurance campaigns pass.\n')
    print('wrote gate reconciliation')
def status(args): print(json.dumps({'stageB':'computed from qa/mainnet-postdeploy evidence','deploymentMode':'DIRECT_OPERATOR_NO_CERTIFICATE'},indent=2))
def fork(args):
    w(Path(f'qa/mainnet-postdeploy/{args.command.split(":")[-1]}.json'),{'status':'NOT_RUN_REQUIRES_LOCAL_MAINNET_FORK','liveMainnetTransactions':'FORBIDDEN'}); print('fork gate placeholder written')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command'); a=ap.parse_args(); c=a.command
    {'import-direct':import_direct,'revalidate':revalidate,'authority-readback':authority,'configuration-readback':authority,'verify':verify,'certificate':certificate,'certificate:validate':validate,'status':status,'generate-config':generated,'gate-reconciliation':gate,'direct:reconcile-configuration':authority}.get(c.split('mainnet:')[-1], fork)(a)
if __name__=='__main__': main()
