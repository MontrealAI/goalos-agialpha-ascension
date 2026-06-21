#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, subprocess, sys, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'; WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
PRE=ROOT/'qa/mainnet-predeploy'; POST=ROOT/'qa/mainnet-postdeploy'; ACT=ROOT/'qa/mainnet-activation'
GATES=PRE/'gates'
GATE_SPECS={
 'G1':('gate-1','Authority',['fork_topology_deployed','wallet_b_final_authority','wallet_a_zero_permanent_authority','negative_authority_paths_revert']),
 'G2':('gate-2','Overrides',['typed_owner_resolvers_exercised','replay_duplicate_rejected','financial_override_events_reconciled','arbitrary_call_backdoors_absent']),
 'G3':('gate-3','Accounting',['canonical_agialpha_used_on_fork','asset_holder_reconciliation','malicious_token_suite_executed','cap_breaches_revert']),
 'G4':('gate-4','Lifecycle',['selector_classification_complete','phase_transitions_exercised','shutdown_blocks_unresolved_liabilities','terminal_shutdown_after_discharge']),
 'G5':('gate-5','Assurance',['invariants_executed_1000000_actions_32_seeds','secondary_stateful_engine_pass','differential_traces_match','critical_mutants_killed','independent_bytecode_builds_match','security_docket_complete']),
}
OK_STATUS='PASS'
FORBIDDEN={'LIVE_MAINNET_TRANSACTION','LIVE_MAINNET_RECEIPT','LIVE_MAINNET_DEPLOYED_ADDRESS','LIVE_MAINNET_ETHERSCAN_VERIFICATION','LIVE_MAINNET_OWNER_READBACK','LIVE_MAINNET_ROLE_READBACK','LIVE_MAINNET_CANARY'}

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def read(rel):
 p=ROOT/rel if not isinstance(rel,pathlib.Path) else rel
 try: return json.loads(p.read_text())
 except Exception: return {}
def write(path,d): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def git(args):
 try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return 'UNKNOWN'
def sha(rel):
 p=ROOT/rel if not isinstance(rel,pathlib.Path) else rel
 if not p.exists(): return None
 h=hashlib.sha256()
 if p.is_dir():
  for f in sorted(x for x in p.rglob('*') if x.is_file() and '.git' not in x.parts): h.update(str(f.relative_to(ROOT)).encode()); h.update(f.read_bytes())
 else: h.update(p.read_bytes())
 return '0x'+h.hexdigest()
def hobj(o): return '0x'+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def release_identity():
 return {'releaseId':git(['rev-parse','HEAD']),'finalGitSha':git(['rev-parse','HEAD']),'sourceTreeHash':sha('contracts'),'lockfileHash':sha('package-lock.json'),'hardhatConfigurationHash':sha('hardhat.config.ts'),'deploymentScriptsHash':sha('scripts/deployment') or sha('scripts')}

def release_state():
 d={'schemaVersion':'1.0','stages':{'A_PREDEPLOYMENT_AUTHORIZATION':{'dependsOn':['exactRelease','ordinaryCi','verifiedSepolia','pinnedMainnetFork','deploymentPlan'],'forbiddenEvidence':sorted(FORBIDDEN),'emits':'GO_TO_DEPLOY_MAINNET'},'B_POSTDEPLOYMENT_VERIFICATION':{'dependsOn':['GO_TO_DEPLOY_MAINNET','chain1Receipts','bytecode','etherscanVerification','ownerRoleReadback'],'emits':'MAINNET_DEPLOYMENT_VERIFIED'},'C_PRODUCTION_ACTIVATION':{'dependsOn':['MAINNET_DEPLOYMENT_VERIFIED','monitoring','boundedLiveCanary','accountingReconciliation','ledgerActivation'],'emits':'PRODUCTION_ACTIVATION_EFFECTIVE'}}}
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

def rpc_call(url,method,params=None,timeout=20):
 req=urllib.request.Request(url,data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode(),headers={'Content-Type':'application/json'})
 data=json.loads(urllib.request.urlopen(req,timeout=timeout).read().decode())
 if 'error' in data: raise RuntimeError(data['error'])
 return data.get('result')

def existing_fork_valid_for_reuse(r):
 return r.get('schemaVersion')=='1.0' and r.get('executionMode')=='MAINNET_FORK' and r.get('upstreamChainId')==1 and r.get('localChainId')==31337 and r.get('forkBlockNumber') and r.get('forkBlockHash') and r.get('canonicalAgialphaCodeHash') and r.get('releaseIdentity')==release_identity() and r.get('mainnetBroadcastOccurred') is False and r.get('status') in {'PASS','NOT_RUN'}

def fork_report():
 existing=read(PRE/'fork-rehearsal.json')
 if existing_fork_valid_for_reuse(existing): return existing
 url=os.environ.get('MAINNET_FORK_RPC_URL')
 if not url:
  r={'schemaVersion':'1.0','executionMode':'NOT_RUN','status':'NOT_RUN','failureReason':'MAINNET_FORK_RPC_URL is required; public RPC reads and fallback block/hash constants are not evidence.','mainnetBroadcastOccurred':False}
  write(PRE/'fork-rehearsal.json',r); return r
 chain=int(rpc_call(url,'eth_chainId'),16)
 if chain!=1: raise SystemExit('MAINNET_FORK_RPC_URL must report chainId 1')
 latest=rpc_call(url,'eth_getBlockByNumber',['latest',False]); block=int(latest['number'],16); bh=latest['hash']
 code=rpc_call(url,'eth_getCode',[AGI,hex(block)])
 if not code or code=='0x': raise SystemExit('canonical AGIALPHA code missing at pinned block')
 r={'schemaVersion':'1.0','executionMode':'MAINNET_FORK','upstreamChainId':1,'localChainId':31337,'forkBlockNumber':block,'forkBlockHash':bh,'rpcIdentityCommitment':hobj({'urlHostRedacted':True,'chainId':1,'block':block,'hash':bh}),'canonicalAgialphaAddress':AGI,'canonicalAgialphaCodeHash':'0x'+hashlib.sha256(bytes.fromhex(code[2:])).hexdigest(),'releaseIdentity':release_identity(),'deployedTopologyCount':0,'scenarioResults':[],'mainnetBroadcastOccurred':False,'status':'NOT_RUN','failureReason':'RPC and block pin succeeded, but fork deployment/campaign execution evidence has not been produced by this wrapper.'}
 write(PRE/'fork-rehearsal.json',r); return r

def evidence_ref(path): return {'path':str(path.relative_to(ROOT)) if isinstance(path,pathlib.Path) else path,'sha256':sha(path)}

def validate_evidence_artifact(ev, gate, requirement_id, expected_release):
 errs=[]
 if ev.get('schemaVersion') not in {'1.0','1.1'}: errs.append('missing supported schemaVersion')
 if ev.get('stage')!='A_PREDEPLOYMENT_AUTHORIZATION': errs.append('wrong stage')
 if ev.get('gate')!=gate: errs.append('wrong gate')
 if ev.get('requirementId')!=requirement_id: errs.append('wrong requirementId')
 if ev.get('releaseIdentity')!=expected_release: errs.append('releaseIdentity mismatch')
 if ev.get('evidenceClass')!='PROTECTED_EXECUTION': errs.append('evidenceClass must be PROTECTED_EXECUTION')
 cmd=ev.get('command')
 if not isinstance(cmd,dict) or not cmd.get('argv') or cmd.get('exitCode')!=0: errs.append('passing evidence requires command argv and exitCode 0')
 if not isinstance(ev.get('observed'),dict) or not ev.get('observed'): errs.append('passing evidence requires observed predicates')
 if gate in {'G1','G2','G3','G4'}:
  if ev.get('executionMode')!='MAINNET_FORK': errs.append('gate requires MAINNET_FORK execution')
  if ev.get('upstreamChainId')!=1 or ev.get('localChainId')!=31337: errs.append('invalid fork chain ids')
  if not ev.get('forkBlockNumber') or not ev.get('forkBlockHash'): errs.append('missing pinned fork block/hash')
 if ev.get('mainnetBroadcastOccurred') is not False: errs.append('Stage-A evidence must not broadcast Mainnet')
 return errs

def requirement_status(req):
 if req.get('mandatory',True) and req.get('status')=='PASS' and req.get('evidence'):
  for ev in req['evidence']:
   if not ev.get('path') or sha(ev['path'])!=ev.get('sha256'): return 'FAIL','evidence missing or hash mismatch'
 return req.get('status','NOT_RUN'), req.get('failureReason')
def evaluate_report(report):
 statuses=[requirement_status(r)[0] for r in report.get('requirements',[])]
 if not statuses: return 'NOT_RUN'
 if any(s=='FAIL' for s in statuses): return 'FAIL'
 if any(s!='PASS' for s in statuses): return 'NOT_RUN'
 return 'PASS'

def generate_gate_report(gate):
 subdir,name,reqs=GATE_SPECS[gate]; base=GATES/subdir; rid=release_identity(); existing=read(base/'report.json')
 requirements=[]
 for rid_req in reqs:
  ev_path=base/f'{rid_req}.json'
  ev={}
  if ev_path.exists():
   ev=read(ev_path); raw_status=ev.get('status','NOT_RUN'); validation_errors=validate_evidence_artifact(ev,gate,rid_req,rid) if raw_status=='PASS' else []
   if raw_status=='PASS' and validation_errors:
    st='FAIL'; fail='; '.join(validation_errors)
   else:
    st=raw_status if raw_status in {'PASS','FAIL','NOT_RUN'} else 'FAIL'; fail=ev.get('failureReason')
   evidence=[evidence_ref(ev_path)] if st in {'PASS','FAIL'} else []
  else: st='NOT_RUN'; fail='mandatory evidence artifact has not executed'; evidence=[]
  requirements.append({'id':rid_req,'mandatory':True,'status':st,'command':ev.get('command') if ev_path.exists() else f'npm run release:{gate.lower()}','evidence':evidence,'observed':ev.get('observed',{}) if ev_path.exists() else {},'failureReason':fail})
 report={'schemaVersion':'1.0','stage':'A_PREDEPLOYMENT_AUTHORIZATION','gate':gate,'name':name,'releaseIdentity':rid,'requirements':requirements,'status':'NOT_RUN'}
 report['status']=evaluate_report(report)
 write(base/'report.json',report); write(ROOT/'qa/mainnet-readiness'/f'{subdir}-{name.lower()}.json',report)
 return report

def generate_gate_reports(fork=None): return {g:generate_gate_report(g) for g in GATE_SPECS}
def gate_reports():
 reps=generate_gate_reports(); return {f'Gate {i}':reps[f'G{i}']['status'] for i in range(1,6)}, [f'{g} {r["status"]}' for g,r in reps.items() if r['status']!='PASS']
def fork_valid(fork):
 return fork.get('executionMode')=='MAINNET_FORK' and fork.get('upstreamChainId')==1 and fork.get('localChainId')==31337 and fork.get('forkBlockHash') and fork.get('canonicalAgialphaCodeHash') and fork.get('mainnetBroadcastOccurred') is False and fork.get('status')=='PASS'
def semantic_lint_stage_a(cert):
 blob=json.dumps(cert); errs=[]
 for t in FORBIDDEN:
  if t in blob: errs.append(f'Stage-A references forbidden evidence type {t}')
 for bad in ['qa/mainnet-postdeploy/','qa/mainnet-activation/']:
  if bad in blob: errs.append(f'Stage-A references forbidden namespace {bad}')
 return errs

def plan_complete(p):
 return p.get('schemaVersion')=='1.0' and p.get('stage')=='A_PREDEPLOYMENT_AUTHORIZATION' and p.get('releaseIdentity')==release_identity() and p.get('chainId')==1 and p.get('canonicalAgialpha')==AGI and p.get('status')=='PASS' and isinstance(p.get('orderedTransactions'),list) and len(p.get('orderedTransactions'))>0 and p.get('startingNonce') is not None and p.get('planHash')

def plan_public():
 existing=read(PRE/'deployment-plan.public.json')
 if plan_complete(existing): return existing
 p={'schemaVersion':'1.0','stage':'A_PREDEPLOYMENT_AUTHORIZATION','releaseIdentity':release_identity(),'chainId':1,'canonicalAgialpha':AGI,'walletA':WA,'walletB':WB,'orderedTransactions':[],'postDeploymentConfiguration':[],'requiresTypedPlanHashConfirmation':True,'mainnetBroadcastOccurred':False,'status':'INCOMPLETE','failureReason':'Complete deployment transaction sequence has not been generated.'}
 p['planHash']=hobj({k:v for k,v in p.items() if k!='planHash'}); write(PRE/'deployment-plan.public.json',p); return p

def predeploy_certificate():
 release_state(); fork=fork_report(); reps=generate_gate_reports(fork); plan=plan_public(); gates={f'Gate {i}':reps[f'G{i}']['status'] for i in range(1,6)}
 blockers=[f'{g} is {r["status"]}' for g,r in reps.items() if r['status']!='PASS']
 if not fork_valid(fork): blockers.append('Pinned Mainnet fork rehearsal with deployed topology and scenario PASS is missing.')
 if plan.get('status')!='PASS': blockers.append('Complete immutable deployment plan is missing or incomplete.')
 status='AUTHORIZED' if not blockers else 'BLOCKED'; yes='YES' if status=='AUTHORIZED' else 'NO'
 c={'schemaVersion':'1.0','stage':'A_PREDEPLOYMENT_AUTHORIZATION',**release_identity(),'forkBlockNumber':fork.get('forkBlockNumber'),'forkBlockHash':fork.get('forkBlockHash'),'forkEvidenceRoot':sha('qa/mainnet-predeploy/fork-rehearsal.json'),'deploymentPlanHash':plan.get('planHash'),'gateReportHashes':{g:sha(GATES/GATE_SPECS[g][0]/'report.json') for g in GATE_SPECS},'status':status,'blockers':blockers,'gates':gates,'TECHNICALLY_MAINNET_READY':yes,'MAINNET_DEPLOYMENT_AUTHORIZED':yes,'ETHEREUM_MAINNET_AUTHORIZED':yes,'MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','evidence':[evidence_ref('qa/mainnet-predeploy/fork-rehearsal.json'),evidence_ref('qa/mainnet-predeploy/deployment-plan.public.json')],'mainnetBroadcastOccurred':False}
 c['blockers']+=semantic_lint_stage_a(c); c['certificateHash']=hobj({k:v for k,v in c.items() if k!='certificateHash'}); write(PRE/'authorization-certificate.json',c)
 legacy={'schemaVersion':'3.1','status':c['status'],'generatedBy':'scripts/mainnet_three_stage.py','agialphaToken':AGI,'TECHNICALLY_MAINNET_READY':yes,'technicallyMainnetReady':yes,'MAINNET_DEPLOYMENT_AUTHORIZED':yes,'mainnetDeploymentAuthorized':yes,'ETHEREUM_MAINNET_AUTHORIZED':yes,'ethereumMainnetAuthorized':yes,'MAINNET_DEPLOYED':'NO','mainnetDeployed':'NO','MAINNET_VERIFIED':'NO','mainnetVerified':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','blockers':c['blockers'],'gates':gates,'certificateHash':c['certificateHash'],'deploymentPlanHash':c['deploymentPlanHash'],'notExternallyAudited':True,'privateOperatorAuthorizationPackageRequired':False,'runtimeSecretsStoredInGitHub':False,'ciCanDeployMainnet':False,'mainnetBroadcastOccurred':False,'nextAction':'Resolve Stage-A blockers; do not broadcast Mainnet.' if c['status']!='AUTHORIZED' else 'Run npm run deploy:mainnet:live-local-gated from a human local operator environment.'}
 write(ROOT/'qa/mainnet-authorization-certificate.json',legacy); return c

def validate_predeploy(require_authorized=False):
 c=predeploy_certificate(); errs=[]
 if c.get('schemaVersion')!='1.0' or c.get('stage')!='A_PREDEPLOYMENT_AUTHORIZATION': errs.append('wrong or legacy Stage-A certificate schema')
 if require_authorized and c.get('status')!='AUTHORIZED': errs.extend(c.get('blockers') or ['Stage-A certificate is not AUTHORIZED'])
 if any(c.get(f)!='NO' for f in ['MAINNET_DEPLOYED','MAINNET_VERIFIED','LIVE_OWNER_HANDOFF_COMPLETE','LIVE_CANARY_COMPLETE','PRODUCTION_ACTIVATION_EFFECTIVE']): errs.append('Stage-A cannot claim live Mainnet/activation completion')
 errs+=semantic_lint_stage_a(c)
 if not validate_dag(read('qa/mainnet-release-state.json') or release_state()): errs.append('release-state DAG has cycle')
 print(json.dumps({'status':'PASSED' if not errs else 'FAILED','authorized':c.get('status')=='AUTHORIZED','errors':errs,'blockers':c.get('blockers',[])},indent=2)); return not errs

def post_cert():
 path=POST/'deployment-verification-certificate.json'; existing=read(path)
 if existing.get('stage')=='B_POSTDEPLOYMENT_VERIFICATION' and existing.get('status') in {'MAINNET_DEPLOYMENT_VERIFIED','VERIFIED'}:
  return existing
 c={'schemaVersion':'1.0','stage':'B_POSTDEPLOYMENT_VERIFICATION','requires':['chainId=1 receipts','runtime bytecode','Etherscan V2 verification','owner and role readback'],'status':'BLOCKED_UNTIL_REAL_CHAIN_1_EVIDENCE','MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO'}; write(path,c); return c
def act_cert():
 path=ACT/'activation-certificate.json'; existing=read(path)
 if existing.get('stage')=='C_PRODUCTION_ACTIVATION' and existing.get('status') in {'PRODUCTION_ACTIVATION_EFFECTIVE','ACTIVATED'}:
  return existing
 c={'schemaVersion':'1.0','stage':'C_PRODUCTION_ACTIVATION','requires':['valid Stage-B certificate','monitoring','bounded live canary','Ledger activation'],'status':'BLOCKED_UNTIL_STAGE_B_VERIFIED','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO'}; write(path,c); return c
def validate_stage_b_certificate(c):
 errs=[]
 if c.get('schemaVersion')!='1.0' or c.get('stage')!='B_POSTDEPLOYMENT_VERIFICATION': errs.append('wrong Stage-B schema')
 if c.get('status') not in {'MAINNET_DEPLOYMENT_VERIFIED','VERIFIED'}: errs.append(f'Stage-B is not complete: {c.get("status","MISSING")}')
 if c.get('chainId')!=1: errs.append('Stage-B requires chainId=1')
 for key in ['receipts','deployedAddresses','runtimeBytecode','etherscanVerification','ownerRoleReadback','evidence']:
  if not c.get(key): errs.append(f'Missing Stage-B evidence field: {key}')
 for ev in c.get('evidence') or []:
  if isinstance(ev,dict) and ev.get('path') and ev.get('sha256') and sha(ev['path'])!=ev.get('sha256'): errs.append(f'Stage-B evidence hash mismatch: {ev.get("path")}')
 return errs
def validate_stage_c_certificate(c):
 errs=[]
 if c.get('schemaVersion')!='1.0' or c.get('stage')!='C_PRODUCTION_ACTIVATION': errs.append('wrong Stage-C schema')
 if c.get('status') not in {'PRODUCTION_ACTIVATION_EFFECTIVE','ACTIVATED'}: errs.append(f'Stage-C is not complete: {c.get("status","MISSING")}')
 for key in ['stageBReference','monitoring','boundedLiveCanary','accountingReconciliation','ledgerActivation','evidence']:
  if not c.get(key): errs.append(f'Missing Stage-C evidence field: {key}')
 return errs
def validate_stage_complete(path, stage, statuses):
 c=read(path)
 errors=validate_stage_b_certificate(c) if stage=='B_POSTDEPLOYMENT_VERIFICATION' else validate_stage_c_certificate(c)
 print(json.dumps({'status':'PASSED' if not errors else 'FAILED','errors':errors,'certificateStatus':c.get('status')},indent=2)); return not errors
def final_check(): c=predeploy_certificate(); validate_predeploy(require_authorized=True); return c.get('status')=='AUTHORIZED'


def fixture_report(name):
 d={'schemaVersion':'1.0','fixtureOnly':True,'notReleaseEvidence':True,'name':name,'status':OK_STATUS,'mainnetBroadcastOccurred':False,'releaseIdentity':release_identity()}
 out=ROOT/'qa/fixtures/mainnet-predeploy'/f'{name}.json'; write(out,d); return d

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('cmd'); a=ap.parse_args(); cmd=a.cmd
 if cmd=='fixture-generate': print(json.dumps(fixture_report('predeploy-structure'),indent=2)); return
 if cmd=='fixture-validate': print(json.dumps({'status':OK_STATUS,'fixtureOnly':True,'notReleaseEvidence':True},indent=2)); return
 if cmd=='postdeploy-fixture-test': print(json.dumps({'status':OK_STATUS,'fixtureOnly':True,'notReleaseEvidence':True,'stage':'B_POSTDEPLOYMENT_VERIFICATION'},indent=2)); return
 if cmd=='activation-fixture-test': print(json.dumps({'status':OK_STATUS,'fixtureOnly':True,'notReleaseEvidence':True,'stage':'C_PRODUCTION_ACTIVATION'},indent=2)); return
 if cmd=='readiness': print(json.dumps({'status':'INVENTORY_GENERATED','inventoryOnly':True},indent=2)); return
 if cmd=='fork-rehearsal': print(json.dumps(fork_report(),indent=2)); return
 if cmd=='evaluate-gates': print(json.dumps({'gates':gate_reports()[0],'blockers':gate_reports()[1]},indent=2)); sys.exit(0 if not gate_reports()[1] else 2)
 if cmd in {'certificate','certificate-generate'}: print(json.dumps(predeploy_certificate(),indent=2)); return
 if cmd=='certificate-validate': sys.exit(0 if validate_predeploy(False) else 1)
 if cmd=='final-check': sys.exit(0 if final_check() else 1)
 if cmd=='plan': print(json.dumps(plan_public(),indent=2)); return
 if cmd=='prepare-local': sys.exit(0 if validate_predeploy(True) else 2)
 if cmd=='live-local-gated':
  if os.environ.get('CI'): print('REFUSED: Mainnet broadcast path is disabled in CI.'); sys.exit(2)
  if not validate_predeploy(True): print('REFUSED: valid Stage-A certificate is required before live Mainnet broadcast.'); sys.exit(2)
  sys.exit(subprocess.call(['npm','run','deploy:ethereum-mainnet:gated'],cwd=ROOT))
 if cmd=='postdeploy-certificate': print(json.dumps(post_cert(),indent=2)); sys.exit(2)
 if cmd=='activation-certificate': print(json.dumps(act_cert(),indent=2)); sys.exit(2)
 if cmd=='postdeploy-validate': sys.exit(0 if validate_stage_complete('qa/mainnet-postdeploy/deployment-verification-certificate.json','B_POSTDEPLOYMENT_VERIFICATION',{'MAINNET_DEPLOYMENT_VERIFIED','VERIFIED'}) else 1)
 if cmd=='activation-validate': sys.exit(0 if validate_stage_complete('qa/mainnet-activation/activation-certificate.json','C_PRODUCTION_ACTIVATION',{'PRODUCTION_ACTIVATION_EFFECTIVE','ACTIVATED'}) else 1)
 if cmd=='status': print(json.dumps({'status':read(PRE/'authorization-certificate.json').get('status','BLOCKED'),'mainnetBroadcastOccurred':False},indent=2)); return
 if cmd in ['verify','resume','recover','canary']: print(json.dumps({'status':'BLOCKED','reason':'Stage-specific live evidence command is not satisfied by predeployment artifacts.'},indent=2)); sys.exit(2)
 raise SystemExit('unknown command '+cmd)
if __name__=='__main__': main()
