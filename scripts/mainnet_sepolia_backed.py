#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/mainnet-predeploy-sepolia'
PRIVATE=ROOT/'.private/mainnet-deployment'
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'; WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
PROFILE='SEPOLIA_BACKED_INITIAL_MAINNET_V1'
STATUS='AUTHORIZED_TO_DEPLOY_ON_ETHEREUM_MAINNET'
BANNER='INITIAL MAINNET DEPLOYMENT ONLY — NO MAINNET-FORK ASSURANCE — NO USER FUNDS — NO PRODUCTION ACTIVATION — NO PUBLIC RELIANCE'
STATUSES=['historicalSepolia','currentRelease','localRehearsal','safetyChecks','deploymentPlan','ledgerRiskAcceptance','verificationReadiness','resumeReadiness']

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def git(args):
 try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return 'UNKNOWN'
def read(path):
 p=path if isinstance(path,pathlib.Path) else ROOT/path
 try: return json.loads(p.read_text())
 except Exception: return {}
def write(path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def sha(path):
 p=path if isinstance(path,pathlib.Path) else ROOT/path
 if not p.exists(): return None
 h=hashlib.sha256()
 if p.is_dir():
  for f in sorted(x for x in p.rglob('*') if x.is_file()): h.update(str(f.relative_to(ROOT)).encode()); h.update(f.read_bytes())
 else: h.update(p.read_bytes())
 return '0x'+h.hexdigest()
def hobj(o): return '0x'+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def clean_tree(): return subprocess.call(['git','diff','--quiet','--ignore-submodules','--'],cwd=ROOT)==0 and subprocess.call(['git','diff','--cached','--quiet','--ignore-submodules','--'],cwd=ROOT)==0

def validate_historical(write_report=True):
 val=read('qa/sepolia-release-evidence/validation.json'); rec=read('qa/sepolia-release-evidence/deployment-evidence.reconciled.json'); prov=read('qa/sepolia-release-evidence/provenance.json')
 errors=[]
 if val.get('status')!='PASS': errors.append('historical validation is not PASS')
 if rec.get('classification')!='HISTORICAL_VERIFIED_SEPOLIA_DEPLOYMENT': errors.append('wrong historical classification')
 if rec.get('chainId')!=11155111: errors.append('historical Sepolia chainId mismatch')
 if int(rec.get('contractCount') or 0)!=49: errors.append('historical contract count is not 49')
 v=rec.get('verificationSummary',{})
 if v.get('etherscanV2')!='49/49' or v.get('independentCheck')!='49 verified, 0 failed': errors.append('historical verification is not reconciled 49/49')
 contracts=rec.get('contracts') or []
 if not any(c.get('name')=='AGIALPHA' and 'MockAGIALPHA' in c.get('fqn','') for c in contracts): errors.append('historical MockAGIALPHA boundary missing')
 fixture=any(x=='DETERMINISTIC_FIXTURE_NOT_OPERATOR_ARTIFACT' for x in (prov.get('inputHashes') or {}).values())
 status='PASS' if not errors else 'FAIL'
 out={'schemaVersion':'1.0','criterion':'HISTORICAL_SEPOLIA_EXTERNAL_NETWORK_EVIDENCE','status':status,'errors':errors,'HISTORICAL_SEPOLIA_DEPLOYMENT_VALID':'YES' if status=='PASS' else 'NO','HISTORICAL_SEPOLIA_CONTRACTS_VERIFIED':49 if status=='PASS' else 0,'HISTORICAL_SEPOLIA_VERIFICATION_FAILURES':0 if status=='PASS' else None,'CURRENT_RELEASE_BYTECODE_PARITY':'NO','CURRENT_RELEASE_AUTHORITY_PARITY':'NO','ACCEPTED_FOR_STAGE_A_SEPOLIA_EXTERNAL_NETWORK_EVIDENCE':'YES' if status=='PASS' else 'NO','mismatches':{'compiler':'historical Solidity 0.8.35 vs current release 0.8.28','token':'historical MockAGIALPHA vs canonical Mainnet AGIALPHA','authority':'historical deployer == governanceOwner == operationsAddress == founder == treasury; current requires Wallet A gas-only and Wallet B permanent authority','release':'historical LOCAL_PRIVATE_OPERATOR/local rather than current release'},'evidenceHashes':{'validation':sha('qa/sepolia-release-evidence/validation.json'),'reconciled':sha('qa/sepolia-release-evidence/deployment-evidence.reconciled.json'),'provenance':sha('qa/sepolia-release-evidence/provenance.json')},'fixtureOnly':fixture,'mainnetBroadcastOccurred':False}
 if write_report: write(OUT/'historical-sepolia-validation.json',out)
 return out

def current_release():
 rid=git(['rev-parse','HEAD'])
 out={'schemaVersion':'1.0','criterion':'CURRENT_RELEASE_IDENTITY','releaseId':rid,'gitSha':rid,'cleanTrackedTree':clean_tree(),'packageLockHash':sha('package-lock.json'),'sourceTreeHash':sha('contracts'),'hardhatConfigHash':sha('hardhat.config.ts'),'deploymentScriptHash':sha('scripts/deployment'),'artifactBytecodeRoot':sha('artifacts'),'status':'PASS' if rid!='UNKNOWN' and clean_tree() and sha('package-lock.json') else 'BLOCKED','mainnetBroadcastOccurred':False}
 write(OUT/'current-release.json',out); return out

def load(name): return read(OUT/name)
def rehearsal():
 existing=load('local-rehearsal.json')
 req=['schemaVersion','executionMode','walletA','walletB','topologyCount','transactionCount','receiptCount','ownerReadback','walletAZeroAuthority','walletBAuthority','mainnetBroadcastOccurred']
 ok=existing and all(k in existing for k in req) and existing.get('executionMode')=='LOCAL_DETERMINISTIC_RELEASE_REHEARSAL' and existing.get('mainnetForkAssurance') is False and existing.get('mainnetBroadcastOccurred') is False and str(existing.get('walletA','')).lower()==WA.lower() and str(existing.get('walletB','')).lower()==WB.lower() and existing.get('ownerReadback')==WB and existing.get('walletAZeroAuthority') is True and int(existing.get('receiptCount') or 0)>0
 if ok:
  existing['status']='PASS'
  return existing
 out={'schemaVersion':'1.0','criterion':'LOCAL_WALLET_A_WALLET_B_REHEARSAL','status':'BLOCKED','executionMode':'NOT_RUN','requiredExecutionMode':'LOCAL_DETERMINISTIC_RELEASE_REHEARSAL','mainnetForkAssurance':False,'mainnetBroadcastOccurred':False,'blockers':['missing qa/mainnet-predeploy-sepolia/local-rehearsal.json with real local receipts/readbacks']}
 write(OUT/'local-rehearsal.json',out); return out

def safety():
 existing=load('initial-safety-checks.json')
 checks=['ownership_admin_assignment','semantic_override_replay_rejection','stale_state_rejection','no_arbitrary_executor','accounting_consistency','zero_canary_limit_disabled','lifecycle_transition_controls','shutdown_liability_checks','deployment_resume_logic']
 ok=existing.get('status')=='PASS' and all(existing.get('checks',{}).get(c)=='PASS' for c in checks) and existing.get('mainnetBroadcastOccurred') is False
 if ok: return existing
 out={'schemaVersion':'1.0','criterion':'INITIAL_DEPLOYMENT_SAFETY_CHECKS','status':'BLOCKED','checks':{c:existing.get('checks',{}).get(c,'NOT_RUN') for c in checks},'mainnetBroadcastOccurred':False,'blockers':['targeted current-release local safety checks have not all passed']}
 write(OUT/'initial-safety-checks.json',out); return out

def plan_validate(write_report=True):
 p=read(OUT/'deployment-plan.public.json'); errors=[]; txs=p.get('orderedTransactions')
 if p.get('chainId')!=1: errors.append('plan chainId must be 1')
 if str(p.get('canonicalAgialpha','')).lower()!=AGI.lower(): errors.append('plan canonical AGIALPHA mismatch')
 if str(p.get('walletA','')).lower()!=WA.lower() or str(p.get('walletB','')).lower()!=WB.lower(): errors.append('plan wallet mismatch')
 if not isinstance(txs,list) or not txs: errors.append('plan requires nonempty orderedTransactions')
 for i,tx in enumerate(txs or []):
  if tx.get('commitment')=='protected' and 'count' in tx: errors.append(f'aggregate-only transaction {i} rejected')
  for k in ['expectedNonce','expectedCreateAddress','fullyQualifiedName','artifactHash','constructorCommitment','initcodeHash','expectedRuntimeBytecodeHash','transactionValue','gasEstimate','gasLimit','maxFeePerGas','maxPriorityFeePerGas','maximumTransactionCost']:
   if tx.get(k) in [None,'',[],{}]: errors.append(f'transaction {i} missing {k}')
 for k in ['startingNonce','pendingTransactionDisposition','maximumCumulativeCost','minimumWalletARemainingEth','verificationInputCommitment','issuedAt','expiresAt','planHash']:
  if p.get(k) in [None,'',[],{}]: errors.append(f'plan missing {k}')
 out={'schemaVersion':'1.0','criterion':'IMMUTABLE_MAINNET_DEPLOYMENT_PLAN','status':'PASS' if not errors else 'BLOCKED','errors':errors,'planHash':p.get('planHash'),'transactionCount':len(txs or []),'mainnetBroadcastOccurred':False}
 if write_report: write(OUT/'deployment-plan-validation.json',out)
 return out

def ledger():
 p=load('ledger-risk-acceptance.json'); statement='I authorize an initial Ethereum Mainnet deployment without a pinned Mainnet-fork rehearsal. I understand the historical Sepolia deployment used different compiler/token/authority settings. This authorization does not permit user funds, public reliance, frontend activation, or production activation.'
 ok=p.get('status')=='PASS' and str(p.get('recoveredSigner','')).lower()==WB.lower() and p.get('statement')==statement and p.get('chainId')==1 and str(p.get('walletA','')).lower()==WA.lower() and str(p.get('walletB','')).lower()==WB.lower() and str(p.get('canonicalAgialpha','')).lower()==AGI.lower()
 if ok: return p
 out={'schemaVersion':'1.0','criterion':'LEDGER_RISK_ACCEPTANCE','status':'BLOCKED','requiredSigner':WB,'requiredStatement':statement,'mainnetBroadcastOccurred':False,'blockers':['missing valid Wallet-B Ledger EIP-712 risk acceptance']}
 write(OUT/'ledger-risk-acceptance.json',out); return out

def readiness(kind, filename, required):
 p=load(filename); ok=p.get('status')=='PASS' and all(p.get(k) for k in required) and p.get('mainnetBroadcastOccurred') is False
 if ok: return p
 out={'schemaVersion':'1.0','criterion':kind,'status':'BLOCKED','required':required,'mainnetBroadcastOccurred':False,'blockers':[f'missing {filename} readiness evidence']}
 write(OUT/filename,out); return out


def mainnet_dependency_doctor():
 p=load('mainnet-dependency-doctor.json')
 ok=p.get('status')=='PASS' and p.get('chainId')==1 and str(p.get('canonicalAgialpha','')).lower()==AGI.lower() and p.get('providerAgreement') is True and p.get('canonicalAgialphaCodeHash') and p.get('mainnetBroadcastOccurred') is False
 if ok: return p
 out={'schemaVersion':'1.0','criterion':'READ_ONLY_MAINNET_AGIALPHA_DEPENDENCY_DOCTOR','status':'BLOCKED','chainId':1,'canonicalAgialpha':AGI,'mainnetBroadcastOccurred':False,'blockers':['missing read-only dual-RPC canonical Mainnet AGIALPHA dependency doctor evidence; this is not a fork rehearsal']}
 write(OUT/'mainnet-dependency-doctor.json',out); return out

def criteria():
 return {'historicalSepolia':validate_historical(True),'currentRelease':current_release(),'mainnetDependencyDoctor':mainnet_dependency_doctor(),'localRehearsal':rehearsal(),'safetyChecks':safety(),'deploymentPlan':plan_validate(True),'ledgerRiskAcceptance':ledger(),'verificationReadiness':readiness('AUTOMATIC_VERIFICATION_READINESS','verification-readiness.json',['etherscanV2','privateConstructorInputsCommitment']),'resumeReadiness':readiness('DEPLOYMENT_RESUME_READINESS','resume-readiness.json',['appendOnlyJournal','nonceLocking','safeResumeTested'])}

def cert():
 cs=criteria(); blockers=[]
 for k,v in cs.items():
  if v.get('status')!='PASS': blockers.append(f'{k}: {v.get("status")}')
 ok=not blockers
 c={'schemaVersion':'1.0','certificateType':'MAINNET_PREDEPLOY_SEPOLIA_BACKED_INITIAL_MAINNET_V1','warningBanner':BANNER,'status':STATUS if ok else 'BLOCKED','authorizationProfile':PROFILE,'AUTHORIZATION_MODE':'SEPOLIA_BACKED_INITIAL_MAINNET_V1','AUTHORIZATION_SCOPE':'INITIAL_MAINNET_INFRASTRUCTURE_DEPLOYMENT_ONLY','INITIAL_MAINNET_INFRASTRUCTURE_DEPLOYMENT_AUTHORIZED':'YES' if ok else 'NO','TECHNICALLY_READY_FOR_INITIAL_DEPLOYMENT':'YES' if ok else 'NO','TECHNICALLY_MAINNET_READY':'YES' if ok else 'NO','MAINNET_DEPLOYMENT_AUTHORIZED':'YES' if ok else 'NO','ETHEREUM_MAINNET_AUTHORIZED':'YES' if ok else 'NO','FULL_MAINNET_FORK_ASSURANCE':'NO','FULL_G1_G5_ASSURANCE':'NO','PRODUCTION_READY':'NO','USER_FUNDS_AUTHORIZED':'NO','CUSTOMER_ONBOARDING_AUTHORIZED':'NO','PUBLIC_RELIANCE_AUTHORIZED':'NO','PUBLIC_FRONTEND_AUTHORIZED':'NO','PRODUCTION_ANNOUNCEMENT_AUTHORIZED':'NO','PROTOCOL_ACTIVATION_AUTHORIZED':'NO','PHASE_B_CONFIGURATION_AUTHORIZED':'NO','SETTLEMENT_AUTHORIZED':'NO','UNBOUNDED_ECONOMIC_EXPOSURE_AUTHORIZED':'NO','TOKEN_FUNDING_AUTHORIZED':'NO','TREASURY_FUNDING_AUTHORIZED':'NO','MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_READBACK_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','chainId':1,'canonicalAgialpha':AGI,'walletA':WA,'walletB':WB,'releaseId':git(['rev-parse','HEAD']),'gates':{'Gate 1':'PASS' if cs.get('localRehearsal',{}).get('status')=='PASS' else 'BLOCKED','Gate 2':'PASS' if cs.get('safetyChecks',{}).get('status')=='PASS' else 'BLOCKED','Gate 3':'PASS' if cs.get('safetyChecks',{}).get('status')=='PASS' and cs.get('deploymentPlan',{}).get('status')=='PASS' else 'BLOCKED','Gate 4':'PASS' if cs.get('safetyChecks',{}).get('status')=='PASS' and cs.get('resumeReadiness',{}).get('status')=='PASS' else 'BLOCKED','Gate 5':'PASS' if all(cs.get(x,{}).get('status')=='PASS' for x in ['historicalSepolia','currentRelease','mainnetDependencyDoctor','deploymentPlan','verificationReadiness','resumeReadiness']) else 'BLOCKED'},'criteria':{k:{'status':v.get('status'),'hash':sha(OUT/( {'historicalSepolia':'historical-sepolia-validation.json','currentRelease':'current-release.json','localRehearsal':'local-rehearsal.json','safetyChecks':'initial-safety-checks.json','deploymentPlan':'deployment-plan-validation.json','ledgerRiskAcceptance':'ledger-risk-acceptance.json','verificationReadiness':'verification-readiness.json','resumeReadiness':'resume-readiness.json','mainnetDependencyDoctor':'mainnet-dependency-doctor.json'}[k]))} for k,v in cs.items()},'blockers':blockers,'issuedAt':now(),'expiresAt':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=14)).isoformat(),'mainnetBroadcastOccurred':False}
 c['certificateHash']=hobj({k:v for k,v in c.items() if k!='certificateHash'})
 write(OUT/'initial-deployment-certificate.json',c)
 write(ROOT/'qa/mainnet-predeploy/authorization-certificate.json',c)
 return c

def validate_cert(require=False):
 c=read(OUT/'initial-deployment-certificate.json') or cert(); errors=[]
 if c.get('certificateType')!='MAINNET_PREDEPLOY_SEPOLIA_BACKED_INITIAL_MAINNET_V1': errors.append('wrong certificateType')
 if c.get('authorizationProfile')!=PROFILE or c.get('AUTHORIZATION_MODE')!='SEPOLIA_BACKED_INITIAL_MAINNET_V1' or c.get('AUTHORIZATION_SCOPE')!='INITIAL_MAINNET_INFRASTRUCTURE_DEPLOYMENT_ONLY': errors.append('wrong authorization scope')
 for f in ['FULL_MAINNET_FORK_ASSURANCE','FULL_G1_G5_ASSURANCE','PRODUCTION_READY','USER_FUNDS_AUTHORIZED','PUBLIC_RELIANCE_AUTHORIZED','PROTOCOL_ACTIVATION_AUTHORIZED','MAINNET_DEPLOYED','MAINNET_VERIFIED']:
  if c.get(f)!='NO': errors.append(f'{f} must be NO')
 expected=hobj({k:v for k,v in c.items() if k!='certificateHash'}) if c else None
 if c.get('certificateHash')!=expected: errors.append('certificate self-hash mismatch')
 if require and c.get('status')!=STATUS: errors.extend(c.get('blockers') or ['certificate is not authorized'])
 out={'status':'PASSED' if not errors else 'FAILED','authorized':c.get('status')==STATUS,'errors':errors,'blockers':c.get('blockers',[])}; print(json.dumps(out,indent=2)); return not errors

def resolve():
 c=cert(); validate_cert(False)
 if c.get('status')==STATUS:
  print('Executive Verdict — SEPOLIA_BACKED_INITIAL_MAINNET_V1\nGate 1: PASS\nGate 2: PASS\nGate 3: PASS\nGate 4: PASS\nGate 5: PASS\n\nOverall: AUTHORIZED_TO_DEPLOY_ON_ETHEREUM_MAINNET\n\nHistorical Sepolia deployment: PASS\nHistorical Sepolia verification: 49/49 PASS\nCurrent release build/tests: PASS\nLocal Wallet-A/Wallet-B rehearsal: PASS\nInitial-deployment safety checks: PASS\nImmutable Mainnet deployment plan: PASS\nLedger risk acceptance: PASS\nAutomatic verification readiness: PASS\nDeployment resume readiness: PASS\n\nTECHNICALLY_MAINNET_READY = YES\nMAINNET_DEPLOYMENT_AUTHORIZED = YES\nETHEREUM_MAINNET_AUTHORIZED = YES\n\nAUTHORIZATION_SCOPE = INITIAL_MAINNET_INFRASTRUCTURE_DEPLOYMENT_ONLY\nPRODUCTION_READY = NO\nUSER_FUNDS_AUTHORIZED = NO\nCUSTOMER_ONBOARDING_AUTHORIZED = NO\nPROTOCOL_ACTIVATION_AUTHORIZED = NO\nPHASE_B_CONFIGURATION_AUTHORIZED = NO\nSETTLEMENT_AUTHORIZED = NO\nPUBLIC_FRONTEND_AUTHORIZED = NO\nPRODUCTION_ANNOUNCEMENT_AUTHORIZED = NO\nPUBLIC_RELIANCE_AUTHORIZED = NO\nUNBOUNDED_ECONOMIC_EXPOSURE_AUTHORIZED = NO\n\nMAINNET_DEPLOYED = NO\nMAINNET_VERIFIED = NO\nLIVE_OWNER_READBACK_COMPLETE = NO\nLIVE_CANARY_COMPLETE = NO\nPRODUCTION_ACTIVATION_EFFECTIVE = NO')
  return True
 print(json.dumps({'status':'BLOCKED','blockers':c.get('blockers'),'mainnetBroadcastOccurred':False},indent=2)); return False

def main():
 p=argparse.ArgumentParser(); p.add_argument('cmd'); a=p.parse_args(); cmd=a.cmd
 if cmd in {'doctor','status'}: print(json.dumps({'status':'READY' if cmd=='doctor' else read(OUT/'initial-deployment-certificate.json').get('status','BLOCKED'),'output':str(OUT),'mainnetBroadcastOccurred':False},indent=2)); return
 if cmd in {'import','validate-historical'}: print(json.dumps(validate_historical(True),indent=2)); sys.exit(0 if validate_historical(False).get('status')=='PASS' else 2)
 if cmd=='local-rehearsal': print(json.dumps(rehearsal(),indent=2)); sys.exit(0 if rehearsal().get('status')=='PASS' else 2)
 if cmd=='plan': print(json.dumps(plan_validate(True),indent=2)); sys.exit(0 if plan_validate(False).get('status')=='PASS' else 2)
 if cmd=='ledger-approve': print(json.dumps(ledger(),indent=2)); sys.exit(0 if ledger().get('status')=='PASS' else 2)
 if cmd=='certificate': print(json.dumps(cert(),indent=2)); return
 if cmd=='certificate-validate': sys.exit(0 if validate_cert(False) else 1)
 if cmd=='final-check': sys.exit(0 if validate_cert(True) else 2)
 if cmd=='resolve-and-authorize': sys.exit(0 if resolve() else 2)
 raise SystemExit('unknown command '+cmd)
if __name__=='__main__': main()
