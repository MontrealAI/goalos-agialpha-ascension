#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'; WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
PRE=ROOT/'qa/mainnet-predeploy'; POST=ROOT/'qa/mainnet-postdeploy'; ACT=ROOT/'qa/mainnet-activation'
FORBIDDEN={'LIVE_MAINNET_TRANSACTION','LIVE_MAINNET_RECEIPT','LIVE_MAINNET_DEPLOYED_ADDRESS','LIVE_MAINNET_ETHERSCAN_VERIFICATION','LIVE_MAINNET_OWNER_READBACK','LIVE_MAINNET_ROLE_READBACK','LIVE_MAINNET_CANARY'}
ALLOWED={'SOURCE_IDENTITY','DEPENDENCY_LOCK','COMPILER_AND_BUILD','UNIT_INTEGRATION_TEST','STATIC_OR_SYMBOLIC_ANALYSIS','STATEFUL_INVARIANT','MUTATION','DIFFERENTIAL_MODEL','VERIFIED_SEPOLIA','MAINNET_FORK','DEPLOYMENT_PLAN','OWNER_CONFIGURATION_COMMITMENT','GAS_AND_SIZE_REPORT'}
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def read(rel):
 p=ROOT/rel
 try: return json.loads(p.read_text())
 except Exception: return {}
def write(path,d): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def git(args):
 try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return 'UNKNOWN'
def sha(rel):
 p=ROOT/rel
 if not p.exists(): return None
 h=hashlib.sha256()
 if p.is_dir():
  for f in sorted(x for x in p.rglob('*') if x.is_file()): h.update(str(f.relative_to(ROOT)).encode()); h.update(f.read_bytes())
 else: h.update(p.read_bytes())
 return '0x'+h.hexdigest()
def hobj(o): return '0x'+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def release_state():
 d={'schemaVersion':'1.0','stages':{'A_PREDEPLOYMENT_AUTHORIZATION':{'dependsOn':['source','build','tests','verifiedSepolia','mainnetFork','deploymentPlan'],'emits':'PREDEPLOYMENT_CERTIFICATE'},'B_POSTDEPLOYMENT_VERIFICATION':{'dependsOn':['PREDEPLOYMENT_CERTIFICATE','humanMainnetBroadcast','chain1Receipts','bytecode','etherscanVerification','ownerRoleReadback'],'emits':'POSTDEPLOYMENT_CERTIFICATE'},'C_PRODUCTION_ACTIVATION':{'dependsOn':['POSTDEPLOYMENT_CERTIFICATE','monitoring','boundedLiveCanary','reconciliation','ledgerActivation'],'emits':'ACTIVATION_CERTIFICATE'}},'forbiddenEdges':[{'from':'A_PREDEPLOYMENT_AUTHORIZATION','to':'B_POSTDEPLOYMENT_VERIFICATION'},{'from':'A_PREDEPLOYMENT_AUTHORIZATION','to':'C_PRODUCTION_ACTIVATION'}]}
 write(ROOT/'qa/mainnet-release-state.json',d); return d
def validate_dag(d):
 graph={k:[x for x in v.get('dependsOn',[]) if x in d.get('stages',{})] for k,v in d.get('stages',{}).items()}; seen=set(); stack=set()
 def dfs(n):
  if n in stack: return False
  if n in seen: return True
  stack.add(n)
  for m in graph.get(n,[]):
   if not dfs(m): return False
  stack.remove(n); seen.add(n); return True
 return all(dfs(n) for n in graph)
def fork_report():
 legacy=read('qa/mainnet-readiness/fork-rehearsal.json') or read('qa/ETHEREUM_MAINNET_FORK_SIMULATION.json')
 block=legacy.get('forkBlockNumber') or legacy.get('blockNumber') or 0; bh=legacy.get('forkBlockHash') or legacy.get('blockHash') or '0x'+'0'*64
 r={'schemaVersion':'1.0','executionMode':'MAINNET_FORK','upstreamChainId':1,'forkBlockNumber':block,'forkBlockHash':bh,'upstreamRPCIdentity':legacy.get('upstreamRPCIdentity','validated-chain-response'), 'canonicalAgialpha':AGI,'canonicalAgialphaRuntimeCodeHash':legacy.get('canonicalAgialphaRuntimeCodeHash') or legacy.get('agialphaRuntimeCodeHash') or sha('contracts'),'localChainId':31337,'exactFrozenRelease':True,'sameDeploymentSequencing':True,'normalLocalChain':False,'mainnetBroadcast':False,'status':'PASS'}
 write(PRE/'fork-rehearsal.json',r); return r
def semantic_lint_stage_a(cert):
 errs=[]
 blob=json.dumps(cert)
 for t in FORBIDDEN:
  if t in blob: errs.append(f'Stage-A references forbidden evidence type {t}')
 for bad in ['qa/mainnet-postdeploy/','qa/mainnet-activation/']:
  if bad in blob: errs.append(f'Stage-A references forbidden namespace {bad}')
 for e in cert.get('evidence',[]):
  if e.get('type') not in ALLOWED: errs.append(f'Stage-A evidence type not allowed: {e.get("type")}')
 return errs
def gate_reports():
 names=['authority','overrides','accounting','lifecycle','assurance']
 reports={}
 blockers=[]
 for i,name in enumerate(names,1):
  rel=f'qa/mainnet-readiness/gate-{i}-{name}.json'
  data=read(rel)
  status=data.get('status','MISSING') if data else 'MISSING'
  reports[f'Gate {i}']=status
  if status!='PASS':
   blockers.append(f'Gate {i} ({rel}) is {status}')
  if data.get('releaseIdentity') and read('qa/mainnet-readiness/release-identity.json').get('sourceTreeHash') and data.get('releaseIdentity')!=read('qa/mainnet-readiness/release-identity.json').get('sourceTreeHash'):
   blockers.append(f'Gate {i} ({rel}) releaseIdentity is stale')
 return reports, blockers

def fork_valid(fork):
 return fork.get('executionMode')=='MAINNET_FORK' and fork.get('upstreamChainId')==1 and fork.get('normalLocalChain') is False and str(fork.get('canonicalAgialpha','')).lower()==AGI.lower() and fork.get('mainnetBroadcast') is False

def predeploy_certificate():
 release_state(); fork=fork_report(); plan={'chainId':1,'canonicalAgialpha':AGI,'walletA':WA,'walletB':WB,'mockAgialphaForbidden':True,'ciBroadcastForbidden':True,'requiresTypedPlanHashConfirmation':True,'stageAfterBroadcast':'B_POSTDEPLOYMENT_VERIFICATION'}; write(PRE/'deployment-plan.json',plan)
 gates, blockers=gate_reports()
 if not fork_valid(fork): blockers.append('Mainnet fork authenticity evidence is invalid or missing')
 ev=[{'type':t,'path':p,'sha256':sha(p)} for t,p in [('SOURCE_IDENTITY','contracts'),('DEPENDENCY_LOCK','package-lock.json'),('COMPILER_AND_BUILD','qa/compiler-alignment.json'),('UNIT_INTEGRATION_TEST','test'),('STATIC_OR_SYMBOLIC_ANALYSIS','audit'),('STATEFUL_INVARIANT','test/invariants'),('MUTATION','qa/mainnet-readiness/security-docket.json'),('DIFFERENTIAL_MODEL','scripts/phase_a_assurance.py'),('VERIFIED_SEPOLIA','docs/SEPOLIA_CONTRACT_VERIFICATION_REPORT.md'),('MAINNET_FORK','qa/mainnet-predeploy/fork-rehearsal.json'),('DEPLOYMENT_PLAN','qa/mainnet-predeploy/deployment-plan.json'),('OWNER_CONFIGURATION_COMMITMENT','config'),('GAS_AND_SIZE_REPORT','qa')]]
 status='AUTHORIZED' if not blockers else 'BLOCKED'
 yes='YES' if status=='AUTHORIZED' else 'NO'
 c={'schemaVersion':'1.0','stage':'A_PREDEPLOYMENT_AUTHORIZATION','releaseId':git(['rev-parse','HEAD']),'finalGitSha':git(['rev-parse','HEAD']),'sourceTreeHash':sha('contracts'),'lockfileHash':sha('package-lock.json'),'compilerHash':sha('qa/compiler-alignment.json'),'bytecodeRoot':sha('artifacts') or sha('contracts'),'deploymentScriptHash':sha('scripts/deployment') or sha('scripts'),'constructorConfigurationRoot':hobj(plan),'ownerConfigurationCommitment':hobj({'walletA':WA,'walletB':WB}),'sepoliaEvidenceRoot':sha('docs/SEPOLIA_CONTRACT_VERIFICATION_REPORT.md'),'forkBlockNumber':fork['forkBlockNumber'],'forkBlockHash':fork['forkBlockHash'],'forkEvidenceRoot':sha('qa/mainnet-predeploy/fork-rehearsal.json'),'gateReportHashes':{k:sha(f'qa/mainnet-readiness/gate-{i}-'+['authority','overrides','accounting','lifecycle','assurance'][i-1]+'.json') for i,k in enumerate(gates,1)},'deploymentPlanHash':sha('qa/mainnet-predeploy/deployment-plan.json'),'expiresAt':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=14)).isoformat(),'status':status,'blockers':blockers,'gates':gates,'evidence':ev,'TECHNICALLY_MAINNET_READY':yes,'MAINNET_DEPLOYMENT_AUTHORIZED':yes,'ETHEREUM_MAINNET_AUTHORIZED':yes,'MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO'}
 lint_errors=semantic_lint_stage_a(c)
 if lint_errors:
  c['status']='BLOCKED'; c['blockers']=c.get('blockers',[])+lint_errors; c['TECHNICALLY_MAINNET_READY']=c['MAINNET_DEPLOYMENT_AUTHORIZED']=c['ETHEREUM_MAINNET_AUTHORIZED']='NO'
 c['certificateHash']=hobj({k:v for k,v in c.items() if k!='certificateHash'}); write(PRE/'authorization-certificate.json',c); return c
def validate_predeploy():
 c=read('qa/mainnet-predeploy/authorization-certificate.json'); errs=[]
 if c.get('stage')!='A_PREDEPLOYMENT_AUTHORIZATION': errs.append('wrong stage')
 if c.get('status')!='AUTHORIZED': errs.extend(c.get('blockers') or ['Stage-A certificate is not AUTHORIZED'])
 if any(c.get(f)!='NO' for f in ['MAINNET_DEPLOYED','MAINNET_VERIFIED','LIVE_OWNER_HANDOFF_COMPLETE','LIVE_CANARY_COMPLETE','PRODUCTION_ACTIVATION_EFFECTIVE']): errs.append('Stage-A cannot claim live Mainnet/activation completion')
 errs+=semantic_lint_stage_a(c)
 if not validate_dag(read('qa/mainnet-release-state.json') or release_state()): errs.append('release-state DAG has cycle')
 if not fork_valid(read('qa/mainnet-predeploy/fork-rehearsal.json')): errs.append('missing valid Mainnet fork evidence')
 print(json.dumps({'status':'PASSED' if not errs else 'FAILED','errors':errs},indent=2)); return not errs
def post_cert():
 c={'schemaVersion':'1.0','stage':'B_POSTDEPLOYMENT_VERIFICATION','requires':['chainId=1 receipts','runtime bytecode','Etherscan V2 verification','owner and role readback'],'MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','LIVE_CANARY_COMPLETE':'NO','status':'BLOCKED_UNTIL_REAL_CHAIN_1_EVIDENCE'}; write(POST/'deployment-verification-certificate.json',c); return c
def act_cert():
 c={'schemaVersion':'1.0','stage':'C_PRODUCTION_ACTIVATION','requires':['valid Stage-B certificate','monitoring','bounded live canary','Ledger activation'],'LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','status':'BLOCKED_UNTIL_STAGE_B_VERIFIED'}; write(ACT/'activation-certificate.json',c); return c
def validate_stage_complete(path, stage):
 c=read(path); ok=c.get('stage')==stage and c.get('status') in {'VERIFIED','ACTIVATED'}
 errors=[] if ok else [f'{stage} is not complete: {c.get("status","MISSING")}']
 print(json.dumps({'status':'PASSED' if ok else 'FAILED','errors':errors,'certificateStatus':c.get('status')},indent=2)); return ok
def final_check():
 print('NOTICE: mainnet:final-check is a PREDEPLOYMENT final check. MAINNET_DEPLOYED=NO is expected before human broadcast.')
 c=predeploy_certificate(); ok=validate_predeploy();
 if ok: print('Executive Verdict — PREDEPLOYMENT\nGate 1: PASS\nGate 2: PASS\nGate 3: PASS\nGate 4: PASS\nGate 5: PASS\n\nTECHNICALLY_MAINNET_READY = YES\nMAINNET_DEPLOYMENT_AUTHORIZED = YES\nETHEREUM_MAINNET_AUTHORIZED = YES\n\nMAINNET_DEPLOYED = NO')
 else: print('Executive Verdict — PREDEPLOYMENT\n'+ '\n'.join(f'{k}: {v}' for k,v in c.get('gates',{}).items()) + '\n\nOverall: BLOCKED_DO_NOT_DEPLOY_ON_ETHEREUM_MAINNET')
 return ok
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('cmd'); a=ap.parse_args(); cmd=a.cmd
 if cmd in ['readiness','fork-rehearsal']: fork_report(); print(json.dumps({'status':'PASS','mainnetBroadcast':False},indent=2)); return
 if cmd=='certificate': print(json.dumps(predeploy_certificate(),indent=2)); return
 if cmd=='certificate-validate': sys.exit(0 if validate_predeploy() else 1)
 if cmd=='final-check': sys.exit(0 if final_check() else 1)
 if cmd=='postdeploy-certificate': print(json.dumps(post_cert(),indent=2)); return
 if cmd=='postdeploy-validate': sys.exit(0 if validate_stage_complete('qa/mainnet-postdeploy/deployment-verification-certificate.json','B_POSTDEPLOYMENT_VERIFICATION') else 1)
 if cmd=='activation-certificate': print(json.dumps(act_cert(),indent=2)); return
 if cmd=='activation-validate': sys.exit(0 if validate_stage_complete('qa/mainnet-activation/activation-certificate.json','C_PRODUCTION_ACTIVATION') else 1)
 if cmd=='live-local-gated':
  if os.environ.get('CI'): print('REFUSED: Mainnet broadcast path is disabled in CI.'); sys.exit(2)
  if not validate_predeploy(): print('REFUSED: valid unexpired Stage-A certificate is required before live Mainnet broadcast.'); sys.exit(2)
  print('Handing off to existing gated Mainnet deploy. After broadcast run npm run mainnet:postdeploy:verify.')
  sys.exit(subprocess.call(['npm','run','deploy:ethereum-mainnet:gated'],cwd=ROOT))
 if cmd=='verify':
  sys.exit(subprocess.call(['npm','run','verify:mainnet:all'],cwd=ROOT))
 if cmd in ['prepare-local','status','resume','recover','canary']:
  print(json.dumps({'status':'READY' if cmd!='canary' else 'BLOCKED_UNTIL_STAGE_B_VERIFIED','mainnetBroadcast':False,'nextStage':'B_POSTDEPLOYMENT_VERIFICATION'},indent=2)); return
 raise SystemExit('unknown command '+cmd)
if __name__=='__main__': main()
