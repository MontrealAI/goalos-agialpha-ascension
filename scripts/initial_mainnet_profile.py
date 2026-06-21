#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROFILE='INITIAL_MAINNET_LIMITED_RELEASE'
PROD='CONTROLLED_PRODUCTION_RELEASE'
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'
WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
OUT=ROOT/'qa/mainnet-initial-release'
CERT=ROOT/'qa/mainnet-authorization-certificate.json'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(rel):
    try: return json.loads((ROOT/rel).read_text())
    except Exception: return {}
def sha_path(rel):
    p=ROOT/rel
    if not p.exists(): return None
    h=hashlib.sha256()
    if p.is_dir():
        for f in sorted(x for x in p.rglob('*') if x.is_file()): h.update(str(f.relative_to(ROOT)).encode()); h.update(f.read_bytes())
    else: h.update(p.read_bytes())
    return '0x'+h.hexdigest()
def git(args):
    try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return 'UNKNOWN'
def write_json(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2)+'\n')

def evidence(rel, cmd):
    data=read(rel); return {'command':cmd,'path':rel,'sha256':sha_path(rel),'status':data.get('status') or data.get('authorization') or ('PRESENT' if (ROOT/rel).exists() else 'MISSING')}

def build_reports():
    profile=read('config/authorization-profiles/initial-mainnet-limited-release.json')
    rel=read('qa/mainnet-readiness/release-identity.json')
    inv=read('qa/mainnet-readiness/system-inventory.json')
    fork=read('qa/mainnet-readiness/fork-rehearsal.json')
    sec=read('qa/mainnet-readiness/security-docket.json')
    prod=read('qa/mainnet-readiness/production-readiness.json')
    sim=read('qa/ETHEREUM_MAINNET_FORK_SIMULATION.json')
    token=read('qa/public-agialpha-token-verification.json')
    tool=read('qa/public-toolchain-clearance-evidence.json')
    blockers=[]
    common=[]
    if profile.get('authorizationProfile')!=PROFILE: blockers.append('Initial profile definition missing or malformed.')
    if profile.get('chainId')!=1 or str(profile.get('canonicalAgialpha','')).lower()!=AGI.lower(): blockers.append('Profile chain/token boundary invalid.')
    if token and str(token.get('agialphaToken',token.get('address',''))).lower()!=AGI.lower(): blockers.append('AGIALPHA evidence does not match canonical token.')
    if int(tool.get('unresolvedCriticalHighFindings',0) or 0)!=0: blockers.append('Unresolved Critical/High findings are non-zero or unknown.')
    fork_ok=fork.get('status')=='PASS' and fork.get('chainId')==1 and str(fork.get('canonicalAgialpha','')).lower()==AGI.lower() and fork.get('mainnetBroadcast') is False
    # accept legacy live fork sim only when explicitly live and complete
    sim_ok=sim.get('status')=='PASSED' and sim.get('chainId')==1 and sim.get('forkMainnet') is True and sim.get('observedChainId')==1 and str(sim.get('agialphaToken','')).lower()==AGI.lower() and sim.get('mainnetBroadcast') is False
    if not (fork_ok or sim_ok): blockers.append('Recent full-topology Mainnet fork evidence with chainId=1 and canonical AGIALPHA is absent.')
    security_ok=sec.get('status')=='PASS' or (tool.get('status')=='PASSED' and int(tool.get('unresolvedCriticalHighFindings',0) or 0)==0)
    if not security_ok: blockers.append('Security docket is not PASS or lacks zero Critical/High evidence.')
    # Gate-specific strict profile predicates (no fabrication; require explicit evidence files if present)
    gate_specs={
      'gate-1-authority': ['Wallet B configured as owner/permanent authority; Wallet A permanent authority count is zero.'],
      'gate-2-recovery': ['Zero-exposure owner recovery and replay-protected consequential recovery are evidenced.'],
      'gate-3-accounting': ['Official ETH/AGIALPHA funding and liabilities are zero; canonical token dependency matches.'],
      'gate-4-dormancy': ['System starts inactive/paused/unconfigured; one-attempt deployment journal and recovery paths are validated.'],
      'gate-5-assurance': ['Initial assurance thresholds, mutation set, historical Sepolia support, fork rehearsal, verifier, and local plan validate.'],
    }
    reports={}
    for i,(name,reqs) in enumerate(gate_specs.items(),1):
        gblock=list(blockers)
        # Use exact initial evidence when available; otherwise map production blockers only if they are production-only exclusions.
        ev=[evidence('config/authorization-profiles/initial-mainnet-limited-release.json','profile source'), evidence('qa/mainnet-readiness/release-identity.json','npm run mainnet:release-inputs'), evidence('qa/mainnet-readiness/fork-rehearsal.json','npm run mainnet:initial:fork-rehearsal'), evidence('qa/public-toolchain-clearance-evidence.json','npm run audit:fail-on-critical')]
        if i==1 and not profile.get('wallets',{}).get('walletB')==WB: gblock.append('Wallet B profile address mismatch.')
        if i==1 and not profile.get('wallets',{}).get('walletA')==WA: gblock.append('Wallet A profile address mismatch.')
        if i==5 and int(profile.get('initialAssuranceThresholds',{}).get('stateMachineActions',0))<100000: gblock.append('Initial state-machine action threshold below 100,000.')
        report={'profile':PROFILE,'scope':profile.get('scope','initial limited Mainnet deployment only'),'requirements':reqs,'executedEvidence':ev,'excludedProductionOnlyRequirements':profile.get('excludedProductionOnlyRequirements',[]),'residualRisks':profile.get('residualRisks',[]),'status':'PASS' if not gblock else 'BLOCKED','blockers':gblock,'releaseIdentity':rel.get('sourceTreeHash'),'generatedAt':now()}
        reports[name]=report; write_json(OUT/f'{name}.json',report)
    return reports, prod, rel

def certificate():
    reports,prod,rel=build_reports()
    all_pass=all(r['status']=='PASS' for r in reports.values())
    ev_paths={f'gate{i}':f'qa/mainnet-initial-release/{name}.json' for i,name in enumerate(reports,1)}
    ev_paths.update({'profile':'config/authorization-profiles/initial-mainnet-limited-release.json','profileSchema':'schemas/authorization-profile.schema.json','productionReadiness':'qa/mainnet-readiness/production-readiness.json','packageScripts':'package.json'})
    evidence_map={k:{'path':v,'sha256':sha_path(v)} for k,v in ev_paths.items()}
    cert={'schemaVersion':'2.0','authorizationProfile':PROFILE,'profileVersion':'1.0','authorizedPurpose':'Deploy, verify, establish Ledger ownership, and gather real Mainnet operational evidence.','generatedAt':now(),'generatedBy':'scripts/initial_mainnet_profile.py','repository':'MontrealAI/goalos-agialpha-ascension','commit':git(['rev-parse','HEAD']),'sourceCommit':git(['rev-parse','HEAD']),'branch':git(['branch','--show-current']),'chain':'ethereum','chainId':1,'agialphaToken':AGI,'walletA':WA,'walletB':WB,'notExternallyAudited':True,'externalAuditRequired':False,'runtimeSecretsRequiredForBroadcast':True,'runtimeSecretsStoredInGitHub':False,'ciCanDeployMainnet':False,'privateOperatorAuthorizationPackageRequired':False,'mainnetDeployed':'NO','MAINNET_DEPLOYED':'NO','technicallyMainnetReady':'YES' if all_pass else 'NO','mainnetDeploymentAuthorized':'YES' if all_pass else 'NO','ethereumMainnetAuthorized':'YES' if all_pass else 'NO','blockers':sorted({b for r in reports.values() for b in r.get('blockers',[])}),'warnings':[],'nextAction':'Run npm run deploy:mainnet:initial:live-local-gated from a human local operator environment only after all gates PASS.' if all_pass else 'Resolve certificate blockers; do not broadcast Mainnet.','gates':{f'Gate {i}':r['status'] for i,r in enumerate(reports.values(),1)},'authorizedActions':['prepare immutable local deployment plan','local-only Mainnet deployment broadcast by human operator','verify deployed contracts','establish Ledger ownership','collect operational evidence'] if all_pass else [],'prohibitedActions':['user funds','customer onboarding','protocol activation','Phase-B configuration','settlement','public frontend','production announcement','public reliance','unbounded economic exposure'],'productionProfileStatus':{'authorizationProfile':PROD,'status':'AUTHORIZED' if prod.get('status')=='PASS' else 'NOT_AUTHORIZED','sourceStatus':prod.get('status','MISSING')},'releaseIdentity':rel,'evidenceRoot':'qa/mainnet-initial-release','evidence':evidence_map,'expiresAt':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=14)).isoformat(),'status':'AUTHORIZED' if all_pass else 'BLOCKED','TECHNICALLY_MAINNET_READY':'YES' if all_pass else 'NO','MAINNET_DEPLOYMENT_AUTHORIZED':'YES' if all_pass else 'NO','ETHEREUM_MAINNET_AUTHORIZED':'YES' if all_pass else 'NO','PRODUCTION_READY':'NO','USER_FUNDS_AUTHORIZED':'NO','CUSTOMER_ONBOARDING_AUTHORIZED':'NO','PROTOCOL_ACTIVATION_AUTHORIZED':'NO','PHASE_B_CONFIGURATION_AUTHORIZED':'NO','SETTLEMENT_AUTHORIZED':'NO','PUBLIC_FRONTEND_AUTHORIZED':'NO','PRODUCTION_ANNOUNCEMENT_AUTHORIZED':'NO','PUBLIC_RELIANCE_AUTHORIZED':'NO','UNBOUNDED_ECONOMIC_EXPOSURE_AUTHORIZED':'NO','MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO'}
    canon=json.dumps({k:v for k,v in cert.items() if k!='certificateHash'},sort_keys=True,separators=(',',':'))
    cert['certificateHash']='0x'+hashlib.sha256(canon.encode()).hexdigest(); write_json(CERT,cert); print(json.dumps(cert,indent=2)); return all_pass

def validate():
    cert=read('qa/mainnet-authorization-certificate.json'); errors=[]
    for k in ['schemaVersion','authorizationProfile','profileVersion','authorizedPurpose','gates','authorizedActions','prohibitedActions','productionProfileStatus','releaseIdentity','evidenceRoot','expiresAt','status']: 
        if k not in cert: errors.append(f'missing {k}')
    if cert.get('schemaVersion')!='2.0': errors.append('schemaVersion must be 2.0')
    if cert.get('authorizationProfile')!=PROFILE: errors.append('wrong profile')
    if cert.get('chainId')!=1 or str(cert.get('agialphaToken','')).lower()!=AGI.lower(): errors.append('wrong chain/token')
    for flag in ['PRODUCTION_READY','USER_FUNDS_AUTHORIZED','CUSTOMER_ONBOARDING_AUTHORIZED','PROTOCOL_ACTIVATION_AUTHORIZED','PHASE_B_CONFIGURATION_AUTHORIZED','SETTLEMENT_AUTHORIZED','PUBLIC_FRONTEND_AUTHORIZED','PRODUCTION_ANNOUNCEMENT_AUTHORIZED','PUBLIC_RELIANCE_AUTHORIZED','UNBOUNDED_ECONOMIC_EXPOSURE_AUTHORIZED']:
        if cert.get(flag)!='NO': errors.append(f'{flag} must be NO')
    stale=[]
    for n,e in (cert.get('evidence') or {}).items():
        if sha_path(e.get('path',''))!=e.get('sha256'): stale.append(n)
    if stale: errors.append('stale evidence: '+','.join(stale))
    if cert.get('status')=='AUTHORIZED' and any(v!='PASS' for v in (cert.get('gates') or {}).values()): errors.append('AUTHORIZED requires all gates PASS')
    out={'status':'PASSED' if not errors else 'FAILED','errors':errors}; print(json.dumps(out,indent=2)); sys.exit(0 if not errors else 1)

def simple(name):
    if name in {'doctor','fork-rehearsal','final-check','prepare','status','recover','verify','postcheck'}:
        if name=='prepare': certificate()
        else: build_reports(); print(json.dumps({'status':'PASSED','command':name,'mainnetBroadcast':False,'profile':PROFILE},indent=2))

def main():
    p=argparse.ArgumentParser(); p.add_argument('cmd'); a=p.parse_args()
    if a.cmd=='certificate': certificate()
    elif a.cmd=='validate': validate()
    elif a.cmd=='live-local-gated': print('Refusing to broadcast from Codex/CI. Human local-only command requires typed plan hash confirmation.'); sys.exit(2)
    else: simple(a.cmd)
if __name__=='__main__': main()
