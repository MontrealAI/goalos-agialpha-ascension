#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/dormant-mainnet-readiness/authorization-certificate.json'
STATUS=ROOT/'docs/generated/DORMANT_MAINNET_STATUS.md'
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
DEP='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'
LEDGER='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
ZERO='0x'+'00'*32
PROD_NO=['PRODUCTION_TECHNICALLY_MAINNET_READY','PRODUCTION_MAINNET_DEPLOYMENT_AUTHORIZED','PRODUCTION_ETHEREUM_MAINNET_AUTHORIZED','USER_FUNDS_AUTHORIZED','PROTOCOL_ACTIVATION_AUTHORIZED','CUSTOMER_ONBOARDING_AUTHORIZED','PUBLIC_RELIANCE_AUTHORIZED','SETTLEMENT_AUTHORIZED','UNBOUNDED_ECONOMIC_EXPOSURE_AUTHORIZED']
DORM_YES=['DORMANT_TECHNICALLY_MAINNET_READY','DORMANT_MAINNET_DEPLOYMENT_AUTHORIZED','DORMANT_ETHEREUM_MAINNET_AUTHORIZED']

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(args):
    try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return None
def load(rel):
    p=ROOT/rel
    try: return json.loads(p.read_text())
    except Exception: return None
def sha(rel):
    p=ROOT/rel
    if not p.exists(): return None
    h=hashlib.sha256()
    if p.is_dir():
        for f in sorted(x for x in p.rglob('*') if x.is_file() and '.git' not in x.parts):
            h.update(str(f.relative_to(ROOT)).encode()); h.update(b'\0'); h.update(f.read_bytes())
    else: h.update(p.read_bytes())
    return '0x'+h.hexdigest()
def evidence_entry(rel): return {'path':rel,'sha256':sha(rel),'present':(ROOT/rel).exists()}

def validate_sepolia(blockers):
    dep=load('qa/sepolia-deployment-evidence.json') or {}; ver=load('qa/sepolia-contract-verification-evidence.json') or {}
    if dep.get('chainId')!=11155111: blockers.append('Sepolia deployment evidence chainId is not 11155111.')
    addrs=dep.get('deployedContractAddresses') if isinstance(dep.get('deployedContractAddresses'),dict) else {}
    if len(addrs)!=49: blockers.append(f'Sepolia deployment evidence does not contain 49 contracts (found {len(addrs)}).')
    if dep.get('mockTokenUsed') is not False or dep.get('newAgialphaTokenDeployed') is not False: blockers.append('Sepolia evidence reports mock/new AGIALPHA token use.')
    contracts=ver.get('contracts') if isinstance(ver.get('contracts'),list) else []
    summary=ver.get('summary') if isinstance(ver.get('summary'),dict) else {}
    verified=sum(1 for c in contracts if c.get('etherscanStatus') in {'success','already_verified'} or c.get('alreadyVerified') is True)
    if summary.get('totalContracts')!=49 or len(contracts)!=49: blockers.append('Sepolia verification evidence does not enumerate 49 contracts.')
    if verified!=49 or summary.get('complete') is not True: blockers.append(f'Sepolia verification evidence is not 49/49 complete (verified {verified}/49).')

def compute():
    blockers=[]; warnings=[]
    head=git(['rev-parse','HEAD']) or 'UNKNOWN'
    dirty=git(['status','--porcelain'])
    if dirty: blockers.append('Git working tree is not clean; exact release identity is not fixed.')
    for rel in ['package-lock.json','hardhat.config.ts','scripts/compile-deterministic.js']:
        if sha(rel) is None: blockers.append(f'Missing release/build identity input: {rel}.')
    comp=load('qa/compiler-alignment.json') or {}
    if comp.get('status') not in {'PASSED','PASS'}: blockers.append('Compiler alignment / deterministic vs Hardhat build evidence is not PASSED.')
    tool=load('qa/public-toolchain-clearance-evidence.json') or {}
    if int(tool.get('unresolvedCriticalHighFindings',999) or 999)!=0: blockers.append('Mandatory security toolchain has unresolved Critical/High findings or missing evidence.')
    sim=load('qa/ETHEREUM_MAINNET_FORK_SIMULATION.json') or {}
    if not (sim.get('status')=='PASSED' and sim.get('chainId')==1 and sim.get('forkMainnet') is True and sim.get('deployedContracts',0)>=49): blockers.append('Exact full-topology recent live Mainnet-fork rehearsal evidence is missing or incomplete.')
    if str(sim.get('agialphaToken','')).lower()!=AGI.lower(): blockers.append('Fork rehearsal canonical AGIALPHA token mismatch.')
    if (sim.get('checks') or {}).get('deploysMockAGIALPHAOnMainnet') is not False: blockers.append('MockAGIALPHA path is not proven disabled on Mainnet.')
    plan=load('qa/dormant-mainnet-readiness/deployment-plan.json') or {}
    if not plan: blockers.append('Dormant Mainnet deployment plan is missing.')
    else:
        for k in ['contracts','transactions','gasEstimates','verificationInputs','constructors']:
            if not plan.get(k): blockers.append(f'Deployment plan missing {k}.')
        if plan.get('chainId')!=1: blockers.append('Deployment plan chainId is not 1.')
        if str(plan.get('canonicalAgialpha','')).lower()!=AGI.lower(): blockers.append('Deployment plan canonical AGIALPHA mismatch.')
        if str(plan.get('temporaryDeployer','')).lower()!=DEP.lower(): blockers.append('Deployment plan temporary deployer mismatch.')
        if str(plan.get('ledgerOwner','')).lower()!=LEDGER.lower(): blockers.append('Deployment plan Ledger Owner missing or mismatch.')
        if plan.get('mockTokenEnabled') is not False: blockers.append('Deployment plan permits mock token.')
        if plan.get('temporaryDeployerPermanentAuthority') not in (0,'0',False): blockers.append('Temporary deployer has permanent authority in plan.')
        if plan.get('officialFundingTotal') not in (0,'0','0x0',False): blockers.append('Official vault/protocol funding is nonzero.')
        if plan.get('riskIncreasingEntryPointsDisabled') is not True: blockers.append('Risk-increasing entry points are not proven disabled.')
        if plan.get('ledgerPrivateKeyRequested') is not False: blockers.append('Plan requests or stores Ledger private key/seed.')
        if plan.get('ciBroadcastPossible') is not False: blockers.append('CI Mainnet broadcast is possible.')
    validate_sepolia(blockers)
    ready='NO' if blockers else 'YES'
    cert={'schemaVersion':'1.0','authorizationClass':'DORMANT_INITIAL_MAINNET_DEPLOYMENT','generatedAt':now(),'repository':'MontrealAI/goalos-agialpha-ascension','sourceCommit':head,'chainId':1,'canonicalAgialpha':AGI,'temporaryDeployer':DEP,'ledgerOwner':LEDGER,'deploymentMode':'DORMANT','newObligationsAllowed':False,'officialFundingEnabled':False,'settlementEnabled':False,'activationCertificateHash':ZERO,'futureActivationRequiresLedgerSignedTransaction':True,'futureActivationRequiresNonzeroProductionCertificateHash':True,'unsolicitedTokenTransfersPolicy':'Unauthorized unsolicited token transfers do not constitute accepted user funds.', 'blockers':blockers,'warnings':warnings,'evidence':{k:evidence_entry(v) for k,v in {'packageLock':'package-lock.json','hardhatConfig':'hardhat.config.ts','compilerAlignment':'qa/compiler-alignment.json','toolchainClearance':'qa/public-toolchain-clearance-evidence.json','forkRehearsal':'qa/ETHEREUM_MAINNET_FORK_SIMULATION.json','sepoliaDeployment':'qa/sepolia-deployment-evidence.json','sepoliaVerification':'qa/sepolia-contract-verification-evidence.json','deploymentPlan':'qa/dormant-mainnet-readiness/deployment-plan.json','certificateScript':'scripts/dormant_mainnet.py'}.items()}}
    for k in DORM_YES: cert[k]=ready
    for k in PROD_NO: cert[k]='NO'
    canonical=json.dumps({k:v for k,v in cert.items() if k!='certificateHash'},sort_keys=True,separators=(',',':'))
    cert['certificateHash']='0x'+hashlib.sha256(canonical.encode()).hexdigest()
    return cert

def validate(path):
    cert=json.loads(path.read_text()); errors=[]
    if cert.get('authorizationClass')!='DORMANT_INITIAL_MAINNET_DEPLOYMENT': errors.append('wrong authorizationClass')
    if cert.get('chainId')!=1: errors.append('chain ID/token is wrong')
    if str(cert.get('canonicalAgialpha','')).lower()!=AGI.lower(): errors.append('chain ID/token is wrong')
    for k in PROD_NO:
        if cert.get(k)!='NO': errors.append(f'{k} must remain NO')
    for k in ['USER_FUNDS_AUTHORIZED','PROTOCOL_ACTIVATION_AUTHORIZED','PUBLIC_RELIANCE_AUTHORIZED']:
        if cert.get(k)!='NO': errors.append(f'{k} must be NO')
    if cert.get('activationCertificateHash')!=ZERO: errors.append('activationCertificateHash must be zero for dormant deployment')
    if cert.get('newObligationsAllowed') is not False or cert.get('officialFundingEnabled') is not False or cert.get('settlementEnabled') is not False: errors.append('dormant observable state is not disabled')
    if cert.get('temporaryDeployerPermanentAuthority') not in (None,0,'0',False): errors.append('temporary deployer has permanent authority')
    if cert.get('ledgerOwner')!=LEDGER: errors.append('Ledger Owner is absent')
    if cert.get('officialFundingTotal') not in (None,0,'0','0x0',False): errors.append('funding is nonzero')
    if cert.get('riskIncreasingEntryPointsDisabled') is False: errors.append('a risk-increasing entry point is not disabled')
    if cert.get('mockTokenEnabled') is True: errors.append('mock token is enabled')
    ev=cert.get('evidence') or {}
    for name, e in ev.items():
        rel=e.get('path'); exp=e.get('sha256')
        if not rel or not exp: errors.append(f'verification inputs are incomplete for {name}'); continue
        if sha(rel)!=exp: errors.append(f'certificate or source hash changes detected for {name}')
    if any(cert.get(k)=='YES' for k in DORM_YES) and cert.get('blockers'): errors.append('YES dormant certificate cannot contain blockers')
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['certificate','validate','status','prepare','postdeploy','final-check','live-local-gated']); ap.add_argument('--certificate',default=str(OUT)); args=ap.parse_args()
    if args.cmd=='certificate':
        OUT.parent.mkdir(parents=True,exist_ok=True); c=compute(); OUT.write_text(json.dumps(c,indent=2)+'\n'); print(json.dumps(c,indent=2)); return
    if args.cmd in ['validate','final-check']:
        errs=validate(pathlib.Path(args.certificate)); print(json.dumps({'status':'PASSED' if not errs else 'FAILED','errors':errs},indent=2)); sys.exit(1 if errs else 0)
    if args.cmd=='status':
        c=json.loads(pathlib.Path(args.certificate).read_text()) if pathlib.Path(args.certificate).exists() else compute(); STATUS.parent.mkdir(parents=True,exist_ok=True); text=f"# Dormant Initial Mainnet Deployment Status\n\nDormant technical readiness: {c.get('DORMANT_TECHNICALLY_MAINNET_READY')}\n\nDormant deployment authorized: {c.get('DORMANT_MAINNET_DEPLOYMENT_AUTHORIZED')}\n\nEthereum Mainnet authorized: {c.get('DORMANT_ETHEREUM_MAINNET_AUTHORIZED')}\n\nProduction readiness: {c.get('PRODUCTION_TECHNICALLY_MAINNET_READY')}\n\nUser funds authorized: {c.get('USER_FUNDS_AUTHORIZED')}\n\nProtocol activation authorized: {c.get('PROTOCOL_ACTIVATION_AUTHORIZED')}\n\nPublic reliance authorized: {c.get('PUBLIC_RELIANCE_AUTHORIZED')}\n\nBlockers:\n"+'\n'.join(f"- {b}" for b in c.get('blockers',[]))+"\n"; STATUS.write_text(text); print(text); return
    if args.cmd=='prepare': print('Prepared dormant Mainnet plan template path: qa/dormant-mainnet-readiness/deployment-plan.json'); return
    if args.cmd=='postdeploy': print(json.dumps({'status':'BLOCKED','reason':'No local human Ethereum Mainnet broadcast evidence supplied; not deployed and not verified.'},indent=2)); sys.exit(1)
    if args.cmd=='live-local-gated':
        if os.environ.get('CI','').lower() in {'1','true','yes'}: sys.exit('Refusing dormant Mainnet broadcast in CI.')
        c=json.loads(OUT.read_text()); plan_hash=(c.get('evidence',{}).get('deploymentPlan') or {}).get('sha256')
        if os.environ.get('DORMANT_MAINNET_TYPED_PLAN_HASH')!=plan_hash: sys.exit('Typed plan-hash confirmation missing or mismatched.')
        sys.exit('Broadcast wrapper is gated; operator must wire private local broadcaster after reviewing typed plan hash. No broadcast performed by repository automation.')
if __name__=='__main__': main()
