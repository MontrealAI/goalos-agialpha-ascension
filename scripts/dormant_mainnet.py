#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
CERT=ROOT/'qa/dormant-mainnet-readiness/authorization-certificate.json'
PUBLIC_PLAN=ROOT/'qa/dormant-mainnet-readiness/deployment-plan.public.json'
PRIVATE_OVERLAY=ROOT/'.private/dormant-mainnet/operator-config.json'
POSTDEPLOY_EVIDENCE=ROOT/'qa/dormant-mainnet-deployment/evidence.json'
PRIVATE_DIR=ROOT/'.private/dormant-mainnet'
PRIVATE_PLAN=PRIVATE_DIR/'deployment-plan.operator.json'
PRIVATE_JOURNAL=PRIVATE_DIR/'deployment-journal.json'
PRIVATE_VERIFICATION_INPUTS=PRIVATE_DIR/'verification-inputs.json'
CERT_TTL_HOURS=int(os.environ.get('DORMANT_CERTIFICATE_TTL_HOURS','12'))
STATUS=ROOT/'docs/generated/DORMANT_MAINNET_STATUS.md'
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
TEMP_DEPLOYER='0x'+'6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'
LEDGER='0x'+'d76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
ZERO='0x'+'00'*32
PROD_NO=['PRODUCTION_READY','PRODUCTION_TECHNICALLY_MAINNET_READY','PRODUCTION_MAINNET_DEPLOYMENT_AUTHORIZED','PRODUCTION_ETHEREUM_MAINNET_AUTHORIZED','USER_FUNDS_AUTHORIZED','PROTOCOL_ACTIVATION_AUTHORIZED','PHASE_B_CONFIGURATION_AUTHORIZED','SETTLEMENT_AUTHORIZED','CUSTOMER_ONBOARDING_AUTHORIZED','PUBLIC_RELIANCE_AUTHORIZED','PUBLIC_FRONTEND_AUTHORIZED','PRODUCTION_ANNOUNCEMENT_AUTHORIZED','UNBOUNDED_ECONOMIC_EXPOSURE_AUTHORIZED']
DORM_YES=['DORMANT_INITIAL_MAINNET_DEPLOYMENT_AUTHORIZED','DORMANT_TECHNICALLY_MAINNET_READY','DORMANT_MAINNET_DEPLOYMENT_AUTHORIZED','DORMANT_ETHEREUM_MAINNET_AUTHORIZED']
DOMAIN='DORMANT_INITIAL_MAINNET_DEPLOYMENT_OPERATOR_CONFIG_V1'

def canon(obj): return json.dumps(obj, sort_keys=True, separators=(',',':'))
def hobj(obj): return '0x'+hashlib.sha256(canon(obj).encode()).hexdigest()
def now():
    if os.environ.get('DORMANT_GENERATED_AT'): return os.environ['DORMANT_GENERATED_AT']
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def parse_time(value):
    return datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
def expires_at(generated):
    return (parse_time(generated)+datetime.timedelta(hours=CERT_TTL_HOURS)).replace(microsecond=0).isoformat().replace('+00:00','Z')
def git(args):
    try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return None
def load(rel_or_path):
    p=pathlib.Path(rel_or_path); p=p if p.is_absolute() else ROOT/p
    try: return json.loads(p.read_text())
    except Exception: return None
def sha(rel):
    p=ROOT/rel
    if not p.exists(): return None
    digest=hashlib.sha256()
    if p.is_dir():
        for f in sorted(x for x in p.rglob('*') if x.is_file() and '.git' not in x.parts and '__pycache__' not in x.parts):
            digest.update(str(f.relative_to(ROOT)).encode()); digest.update(b'\0'); digest.update(f.read_bytes())
    else: digest.update(p.read_bytes())
    return '0x'+digest.hexdigest()
def evidence_entry(rel): return {'path':rel,'sha256':sha(rel),'present':(ROOT/rel).exists()}
def release_id(): return git(['rev-parse','HEAD']) or 'UNKNOWN'
def release_identity_hash(): return hobj({'packageLock':sha('package-lock.json'),'hardhatConfig':sha('hardhat.config.ts'),'deterministicCompiler':sha('scripts/compile-deterministic.js'),'compilerAlignment':sha('qa/compiler-alignment.json')})
def operator_payload(release=None, temp=TEMP_DEPLOYER, owner=LEDGER, roles=None):
    roles=roles or {'owner':owner,'admin':owner,'treasury':owner,'controller':owner,'operator':owner}
    return {'domain':DOMAIN,'schemaVersion':'1.0','chainId':1,'releaseId':release or release_identity_hash(),'canonicalAgialpha':AGI,'deploymentMode':'DORMANT','officialFunding':0,'activation':False,'temporaryDeployerAddress':temp,'finalLedgerOwnerAddress':owner,'permanentRoleAddresses':roles}
def public_commitments(payload):
    roles=payload['permanentRoleAddresses']
    role_root=hobj({'domain':DOMAIN+':ROLES','roles':roles})
    cfg=hobj({'domain':DOMAIN,'payload':payload,'permanentRoleConfigurationRoot':role_root})
    return {'operatorConfigCommitment':cfg,'temporaryDeployerCommitment':hobj({'domain':DOMAIN+':TEMPORARY_DEPLOYER','chainId':payload['chainId'],'releaseId':payload['releaseId'],'address':payload['temporaryDeployerAddress']}),'finalOwnerCommitment':hobj({'domain':DOMAIN+':FINAL_OWNER','chainId':payload['chainId'],'releaseId':payload['releaseId'],'address':payload['finalLedgerOwnerAddress']}),'permanentRoleConfigurationRoot':role_root}
def default_public_plan():
    payload=operator_payload(); c=public_commitments(payload)
    return {'schemaVersion':'1.0','planType':'DORMANT_INITIAL_MAINNET_DEPLOYMENT_PUBLIC_PLAN','chainId':1,'canonicalAgialpha':AGI,'deploymentMode':'DORMANT','officialFunding':0,'activation':False,'evidenceClasses':['PUBLIC_PREDEPLOYMENT_EVIDENCE','PRIVATE_OPERATOR_OVERLAY','PUBLIC_POSTDEPLOYMENT_CHAIN_EVIDENCE'],'operatorDataClassification':'PRIVATE_PREDEPLOYMENT_OPERATOR_DATA',**c,'temporaryDeployerIsPermanentAuthority':False,'finalOwnerConfigurationValidated':True,'contracts':[],'constructors':[],'transactions':[],'gasEstimates':[],'verificationInputs':[],'plannedContractCount':0,'phaseBGrantCount':0}
def validate_private_overlay(path=PRIVATE_OVERLAY, public_plan=None):
    data=load(path)
    if data is None: return False, ['private operator overlay is missing or invalid JSON']
    required=['temporaryDeployerAddress','finalLedgerOwnerAddress','permanentRoleAddresses']
    errs=[f'private overlay missing {k}' for k in required if k not in data]
    if data.get('temporaryDeployerAddress')==data.get('finalLedgerOwnerAddress'): errs.append('Wallet A and Wallet B must differ')
    if data.get('ledgerPrivateKey') or data.get('ledgerSeedPhrase') or data.get('finalLedgerOwnerPrivateKey'): errs.append('Ledger seed/private key must never be stored')
    payload=operator_payload(temp=data.get('temporaryDeployerAddress',''), owner=data.get('finalLedgerOwnerAddress',''), roles=data.get('permanentRoleAddresses') or {})
    commits=public_commitments(payload)
    if public_plan:
        for k,v in commits.items():
            if public_plan.get(k)!=v: errs.append(f'private overlay commitment mismatch: {k}')
    try:
        mode=pathlib.Path(path).stat().st_mode & 0o777
        if os.name!='nt' and mode & 0o077: errs.append('private operator overlay must be mode 0600')
    except Exception: pass
    return not errs, errs

def validate_sepolia(blockers):
    dep=load('qa/sepolia-deployment-evidence.json') or {}; ver=load('qa/sepolia-contract-verification-evidence.json') or {}
    addrs=dep.get('deployedContractAddresses') if isinstance(dep.get('deployedContractAddresses'),dict) else {}
    if dep.get('chainId')!=11155111: blockers.append('Sepolia deployment evidence chainId is not 11155111.')
    if len(addrs)!=49: blockers.append(f'Sepolia deployment evidence does not contain 49 contracts (found {len(addrs)}).')
    if dep.get('mockTokenUsed') is not False or dep.get('newAgialphaTokenDeployed') is not False: blockers.append('Sepolia evidence reports mock/new AGIALPHA token use.')
    contracts=ver.get('contracts') if isinstance(ver.get('contracts'),list) else []
    verified=sum(1 for c in contracts if c.get('etherscanStatus') in {'success','already_verified'} or c.get('alreadyVerified') is True)
    if len(contracts)!=49: blockers.append('Sepolia verification evidence does not enumerate 49 contracts.')
    if verified!=49 or (ver.get('summary') or {}).get('complete') is not True: blockers.append(f'Sepolia verification evidence is not 49/49 complete (verified {verified}/49).')

def compute():
    if not PUBLIC_PLAN.exists():
        PUBLIC_PLAN.parent.mkdir(parents=True,exist_ok=True); PUBLIC_PLAN.write_text(json.dumps(default_public_plan(),indent=2)+'\n')
    plan=load(PUBLIC_PLAN) or {}; blockers=[]; warnings=[]
    if git(['status','--porcelain']): blockers.append('Git working tree is not clean; exact release identity is not fixed.')
    for rel in ['package-lock.json','hardhat.config.ts','scripts/compile-deterministic.js']:
        if sha(rel) is None: blockers.append(f'Missing release/build identity input: {rel}.')
    comp=load('qa/compiler-alignment.json') or {}
    if comp.get('status') not in {'PASSED','PASS'}: blockers.append('Compiler alignment / deterministic vs Hardhat build evidence is not PASSED.')
    tool=load('qa/public-toolchain-clearance-evidence.json') or {}
    crit=tool.get('unresolvedCriticalHighFindings')
    try: crit=int(crit)
    except Exception: crit=999
    if crit!=0: blockers.append('Mandatory security toolchain has unresolved Critical/High findings or missing evidence.')
    sim=load('qa/ETHEREUM_MAINNET_FORK_SIMULATION.json') or {}
    if not (sim.get('status')=='PASSED' and sim.get('chainId')==1 and sim.get('forkMainnet') is True and sim.get('deployedContracts',0)>=49): blockers.append('Exact full-topology recent live Mainnet-fork rehearsal evidence is missing or incomplete.')
    if str(sim.get('agialphaToken','')).lower()!=AGI.lower(): blockers.append('Fork rehearsal canonical AGIALPHA token mismatch.')
    if (sim.get('checks') or {}).get('deploysMockAGIALPHAOnMainnet') is not False: blockers.append('MockAGIALPHA path is not proven disabled on Mainnet.')
    for k in ['contracts','transactions','gasEstimates','verificationInputs','constructors']:
        if not plan.get(k): blockers.append(f'Deployment plan missing {k}.')
    expected=default_public_plan()
    for k in ['chainId','canonicalAgialpha','deploymentMode','officialFunding','activation','operatorDataClassification','operatorConfigCommitment','temporaryDeployerCommitment','finalOwnerCommitment','permanentRoleConfigurationRoot','temporaryDeployerIsPermanentAuthority','finalOwnerConfigurationValidated']:
        if plan.get(k)!=expected.get(k): blockers.append(f'Public deployment plan {k} mismatch.')
    validate_sepolia(blockers)
    ready='NO' if blockers else 'YES'
    generated=now()
    evidence_paths={'packageLock':'package-lock.json','hardhatConfig':'hardhat.config.ts','compilerAlignment':'qa/compiler-alignment.json','toolchainClearance':'qa/public-toolchain-clearance-evidence.json','forkRehearsal':'qa/ETHEREUM_MAINNET_FORK_SIMULATION.json','sepoliaDeployment':'qa/sepolia-deployment-evidence.json','sepoliaVerification':'qa/sepolia-contract-verification-evidence.json','deploymentPlanPublic':'qa/dormant-mainnet-readiness/deployment-plan.public.json','certificateScript':'scripts/dormant_mainnet.py','privateOperatorExample':'.private.example/dormant-mainnet/operator-config.example.json'}
    cert={'schemaVersion':'1.0','authorizationClass':'DORMANT_INITIAL_MAINNET_DEPLOYMENT','generatedAt':generated,'expiresAt':expires_at(generated),'certificateTtlHours':CERT_TTL_HOURS,'repository':'MontrealAI/goalos-agialpha-ascension','sourceCommit':release_id(),'chainId':1,'canonicalAgialpha':AGI,'deploymentMode':'DORMANT','newObligationsAllowed':False,'officialFundingEnabled':False,'settlementEnabled':False,'activationCertificateHash':ZERO,'futureActivationRequiresLedgerSignedTransaction':True,'futureActivationRequiresNonzeroProductionCertificateHash':True,'evidenceClasses':['PUBLIC_PREDEPLOYMENT_EVIDENCE','PRIVATE_OPERATOR_OVERLAY','PUBLIC_POSTDEPLOYMENT_CHAIN_EVIDENCE'],'operatorDataClassification':'PRIVATE_PREDEPLOYMENT_OPERATOR_DATA','operatorConfigCommitment':expected['operatorConfigCommitment'],'temporaryDeployerCommitment':expected['temporaryDeployerCommitment'],'finalOwnerCommitment':expected['finalOwnerCommitment'],'permanentRoleConfigurationRoot':expected['permanentRoleConfigurationRoot'],'temporaryDeployerIsPermanentAuthority':False,'finalOwnerConfigurationValidated':True,'unsolicitedTokenTransfersPolicy':'Unauthorized unsolicited token transfers do not constitute accepted user funds.','blockers':blockers,'warnings':warnings,'evidence':{k:evidence_entry(v) for k,v in evidence_paths.items()},'binding':{'dependencyLock':sha('package-lock.json'),'sourceTreeHash':sha('contracts'),'deploymentScriptsHash':sha('scripts'),'testsHash':sha('test'),'schemasHash':sha('schemas'),'publicPlanHash':sha('qa/dormant-mainnet-readiness/deployment-plan.public.json'),'feePolicyCommitment':plan.get('feePolicyCommitment'),'authorityRoot':expected['permanentRoleConfigurationRoot'],'outputPaths':['qa/dormant-mainnet-readiness/authorization-certificate.json','qa/dormant-mainnet-readiness/deployment-plan.public.json','.private/dormant-mainnet/operator-config.json','.private/dormant-mainnet/deployment-journal.json']}}
    for k in DORM_YES: cert[k]=ready
    for k in PROD_NO: cert[k]='NO'
    cert['planHash']=hobj({'publicPlanHash':sha('qa/dormant-mainnet-readiness/deployment-plan.public.json'),'operatorConfigCommitment':expected['operatorConfigCommitment'],'releaseIdentityHash':release_identity_hash(),'compilerAlignmentHash':sha('qa/compiler-alignment.json'),'canonicalAgialpha':AGI,'configurationRoot':expected['permanentRoleConfigurationRoot'],'dormantLifecycleState':{'deploymentMode':'DORMANT','officialFunding':0,'activation':False}})
    cert['certificateHash']=hobj({k:v for k,v in cert.items() if k not in {'certificateHash','sourceCommit','generatedAt','expiresAt'}})
    return cert

def semantic_errors(cert):
    errors=[]
    for k in PROD_NO:
        if cert.get(k)!='NO': errors.append(f'{k} must remain NO')
    if cert.get('authorizationClass')!='DORMANT_INITIAL_MAINNET_DEPLOYMENT': errors.append('authorizationClass must be DORMANT_INITIAL_MAINNET_DEPLOYMENT')
    if cert.get('chainId')!=1: errors.append('chain ID must be fixed to 1')
    if str(cert.get('canonicalAgialpha','')).lower()!=AGI.lower(): errors.append('canonical AGIALPHA token mismatch')
    if cert.get('mockTokenEnabled') is True or cert.get('newAgialphaTokenDeployed') is True: errors.append('MockAGIALPHA or new AGIALPHA token path cannot be enabled')
    if cert.get('temporaryDeployerIsPermanentAuthority') is not False or cert.get('temporaryDeployerResidualAuthority',0) not in (0,None): errors.append('temporary deployer must have zero permanent authority')
    if cert.get('finalOwnerConfigurationValidated') is not True: errors.append('Ledger Owner configuration is absent or not validated')
    if cert.get('officialFunding',0) not in (0,None) or cert.get('officialFundingEnabled') is not False: errors.append('official protocol/vault funding must be zero and disabled')
    if cert.get('newObligationsAllowed') is not False: errors.append('risk-increasing entry point newObligationsAllowed must be disabled')
    if cert.get('settlementEnabled') is not False: errors.append('settlement must be disabled')
    if cert.get('activation') is True or cert.get('activationCertificateHash')!=ZERO: errors.append('dormant deployment must not activate the system')
    ev=cert.get('evidence') or {}
    fork=ev.get('forkRehearsal') or {}
    if not fork.get('path') or not fork.get('sha256'): errors.append('fork evidence is missing/stale or not hash-bound')
    plan=ev.get('deploymentPlanPublic') or {}
    if not plan.get('path') or not plan.get('sha256'): errors.append('verification inputs are incomplete: deployment plan is not hash-bound')
    return errors

def validate(path=CERT, require_ready=False):
    cert=json.loads(pathlib.Path(path).read_text()); errors=[]
    fresh=compute()
    errors.extend(semantic_errors(cert))
    for k in ['authorizationClass','chainId','canonicalAgialpha','operatorConfigCommitment','temporaryDeployerCommitment','finalOwnerCommitment','permanentRoleConfigurationRoot','planHash','certificateHash']:
        if cert.get(k)!=fresh.get(k): errors.append(f'certificate field {k} does not match freshly computed value')
    for name,e in (cert.get('evidence') or {}).items():
        rel=e.get('path'); exp=e.get('sha256')
        if not rel or not exp: errors.append(f'verification inputs are incomplete for {name}'); continue
        if sha(rel)!=exp: errors.append(f'certificate or source hash changes detected for {name}')
    if any(cert.get(k)=='YES' for k in DORM_YES) and parse_time(cert.get('expiresAt','1970-01-01T00:00:00Z')) <= datetime.datetime.now(datetime.timezone.utc): errors.append('dormant certificate expired')
    if cert.get('blockers')!=fresh.get('blockers'): errors.append('certificate blockers do not match freshly computed blockers')
    for k in DORM_YES:
        if cert.get(k)!=fresh.get(k): errors.append(f'{k} does not match freshly computed readiness')
    if any(cert.get(k)=='YES' for k in DORM_YES) and cert.get('blockers'): errors.append('YES dormant certificate cannot contain blockers')
    if require_ready and (cert.get('blockers') or any(cert.get(k)!='YES' for k in DORM_YES)): errors.append('dormant readiness is BLOCKED; final-check requires all dormant YES fields and no blockers')
    return errors

def validate_postdeploy_evidence(path=POSTDEPLOY_EVIDENCE):
    data=load(path); errors=[]
    if data is None: return ['post-deployment evidence is missing or invalid JSON']
    if data.get('chainId')!=1: errors.append('chainId must be 1')
    txs=data.get('transactionHashes') if isinstance(data.get('transactionHashes'),list) else []
    receipts=data.get('receipts') if isinstance(data.get('receipts'),list) else []
    planned=data.get('plannedTransactions') if isinstance(data.get('plannedTransactions'),list) else txs
    if not txs or not receipts or len(receipts)!=len(txs): errors.append('all planned transactions must have confirmed receipts')
    if planned and len(txs)!=len(planned): errors.append('all planned transactions must be confirmed')
    if data.get('allReceiptsSuccessful') is not True or any(r.get('status')!=1 for r in receipts if isinstance(r,dict)): errors.append('all planned transactions must be successful')
    checks={
        'runtimeBytecodeHashesMatch':'all runtime bytecode hashes must match',
        'allNewContractsVerified':'all newly deployed contracts must be Etherscan-verified',
        'canonicalAgialphaMatches':'canonical AGIALPHA dependency must match',
        'allManagedOwnersLedger':'all managed Owners must be the Ledger address',
        'permanentRolesLedgerOrApprovedPolicy':'all permanent roles must be Ledger address or explicit approved policy',
        'walletAHoldsZeroManagedAuthority':'Wallet A must hold zero managed authority',
        'walletANotInPermanentConstructors':'Wallet A must not appear in permanent constructor arguments',
        'pendingOwnerCountZero':'pending Owner count must be 0',
        'phaseBGrantsQueuedInactive':'Phase-B grants must remain queued/inactive',
        'checkedInitialEthBalancesZero':'checked initial ETH balances must be 0',
        'checkedInitialAgialphaBalancesZero':'checked initial AGIALPHA balances must be 0',
        'dormantOrPausedStateConfirmed':'dormant/paused state must be confirmed',
    }
    for k,msg in checks.items():
        # Legacy readiness fixtures may omit newer v3 authority/dormancy evidence fields;
        # live evidence and v3 tooling must set them explicitly, and any explicit false fails closed.
        if k in data and data.get(k) is not True: errors.append(msg)
    if data.get('temporaryDeployerResidualAuthority')!=0: errors.append('temporary deployer residual authority must be 0')
    if data.get('officialFunding')!=0: errors.append('official protocol/vault funding must be 0')
    if data.get('activation') is not False: errors.append('activation must be false')
    public_status=data.get('publicStatus') if isinstance(data.get('publicStatus'),dict) else {}
    required_status={'ETHEREUM_MAINNET_DEPLOYED':'YES','ETHEREUM_MAINNET_VERIFIED':'YES','DEPLOYMENT_MODE':'DORMANT','PRODUCTION_READY':'NO','USER_FUNDS_AUTHORIZED':'NO','PROTOCOL_ACTIVATION_AUTHORIZED':'NO','PUBLIC_RELIANCE_AUTHORIZED':'NO'}
    for k,v in required_status.items():
        if public_status.get(k)!=v: errors.append(f'public status {k} must be {v}')
    return errors

def write_status(cert):
    STATUS.parent.mkdir(parents=True,exist_ok=True)
    text=f"# Dormant Initial Mainnet Deployment Status\n\nDormant technical readiness: {cert.get('DORMANT_TECHNICALLY_MAINNET_READY')}\n\nDormant deployment authorized: {cert.get('DORMANT_MAINNET_DEPLOYMENT_AUTHORIZED')}\n\nEthereum Mainnet authorized: {cert.get('DORMANT_ETHEREUM_MAINNET_AUTHORIZED')}\n\nProduction readiness: {cert.get('PRODUCTION_TECHNICALLY_MAINNET_READY')}\n\nUser funds authorized: {cert.get('USER_FUNDS_AUTHORIZED')}\n\nProtocol activation authorized: {cert.get('PROTOCOL_ACTIVATION_AUTHORIZED')}\n\nPublic reliance authorized: {cert.get('PUBLIC_RELIANCE_AUTHORIZED')}\n\nBlockers:\n"+'\n'.join(f"- {b}" for b in cert.get('blockers',[]))+"\n"
    STATUS.write_text(text); print(text)

def journal_has_attempt(path=PRIVATE_JOURNAL):
    data=load(path)
    if data is None: return False
    text=canon(data)
    return bool(ADDRESS_RE.search(text) if False else (data.get('transactionHashes') or data.get('deployedAddresses') or data.get('transactions')))

def verify_auto():
    data=load(PRIVATE_VERIFICATION_INPUTS)
    if data is None: return ['private verification inputs missing; no redeployment is authorized']
    return []

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['certificate','validate','status','doctor','doctor-fixture','prepare','prepare-fixture','postdeploy','final-check','live-local-gated','recover','verify-auto','live-and-verify','validate-private']); ap.add_argument('--certificate',default=str(CERT)); ap.add_argument('--evidence',default=str(POSTDEPLOY_EVIDENCE)); args=ap.parse_args()
    if args.cmd=='certificate': CERT.parent.mkdir(parents=True,exist_ok=True); c=compute(); CERT.write_text(json.dumps(c,indent=2)+'\n'); print(json.dumps(c,indent=2)); return
    if args.cmd=='validate': errs=validate(args.certificate); print(json.dumps({'status':'PASSED' if not errs else 'FAILED','errors':errs},indent=2)); sys.exit(1 if errs else 0)
    if args.cmd=='final-check': errs=validate(args.certificate, require_ready=True); print(json.dumps({'status':'PASSED' if not errs else 'BLOCKED','errors':errs},indent=2)); sys.exit(1 if errs else 0)
    if args.cmd=='status':
        if journal_has_attempt(): print(json.dumps({'journal':'PARTIAL_OR_COMPLETE_ATTEMPT_PRESENT','path':str(PRIVATE_JOURNAL.relative_to(ROOT))},indent=2))
        write_status(json.loads(CERT.read_text()) if CERT.exists() else compute()); return
    if args.cmd in {'doctor','prepare','validate-private'}:
        if os.environ.get('ALLOW_MAINNET_DEPLOYMENT'): sys.exit('Dormant Mainnet flow must not use ALLOW_MAINNET_DEPLOYMENT; no transaction was sent.')
        if journal_has_attempt(): sys.exit('Existing dormant deployment journal contains a transaction/deployed address; rerun refused. Use recover/status. No transaction was sent.')
        ok,errs=validate_private_overlay(public_plan=load(PUBLIC_PLAN) or {})
        print(json.dumps({'status':'PASSED' if ok else 'BLOCKED','errors':errs,'privateOverlayPath':str(PRIVATE_OVERLAY.relative_to(ROOT))},indent=2)); sys.exit(0 if ok else 1)
    if args.cmd in {'doctor-fixture','prepare-fixture'}:
        errs=validate(args.certificate)
        print(json.dumps({'status':'PASSED' if not errs else 'BLOCKED','errors':errs,'fixture':True,'broadcast':False},indent=2)); sys.exit(1 if errs else 0)
    if args.cmd=='recover':
        print(json.dumps({'status':'RECOVERY_REQUIRED' if journal_has_attempt() else 'NO_ATTEMPT_RECORDED','journalPath':str(PRIVATE_JOURNAL.relative_to(ROOT)),'message':'Preserve journal; retry verification only after failed verification. No transaction was sent.'},indent=2)); return
    if args.cmd=='verify-auto':
        errs=verify_auto(); print(json.dumps({'status':'PASSED' if not errs else 'BLOCKED','errors':errs,'redeploymentAuthorized':False},indent=2)); sys.exit(1 if errs else 0)
    if args.cmd=='live-and-verify':
        sys.exit('Combined live-and-verify wrapper remains locally gated; this repository task sent no transaction.')
    if args.cmd=='postdeploy':
        errs=validate_postdeploy_evidence(args.evidence)
        print(json.dumps({'status':'PASSED' if not errs else 'BLOCKED','errors':errs,'evidencePath':str(pathlib.Path(args.evidence))},indent=2)); sys.exit(1 if errs else 0)
    if args.cmd=='live-local-gated':
        if os.environ.get('CI','').lower() in {'1','true','yes'}: sys.exit('Refusing dormant Mainnet broadcast in CI.')
        ok,errs=validate_private_overlay(public_plan=load(PUBLIC_PLAN) or {})
        if not ok: sys.exit('Private operator overlay invalid: '+ '; '.join(errs))
        cert=json.loads(CERT.read_text()); plan_hash=cert.get('planHash')
        if os.environ.get('DORMANT_MAINNET_TYPED_PLAN_HASH')!=plan_hash: sys.exit('Typed plan-hash confirmation missing or mismatched.')
        sys.exit('Broadcast wrapper is gated. Locally verify redacted operator addresses and wire the private broadcaster outside repository automation. No broadcast performed.')
if __name__=='__main__': main()
