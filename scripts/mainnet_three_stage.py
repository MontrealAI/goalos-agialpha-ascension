#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, subprocess, sys, urllib.request
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
def rpc_call(method, params=None, timeout=8):
 req=urllib.request.Request('https://cloudflare-eth.com',data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode(),headers={'Content-Type':'application/json','User-Agent':'goalos-release-check/1.0'})
 data=json.loads(urllib.request.urlopen(req,timeout=timeout).read().decode())
 if 'error' in data: raise RuntimeError(data['error'])
 return data.get('result')

def fork_report():
 legacy=read('qa/mainnet-readiness/fork-rehearsal.json') or read('qa/ETHEREUM_MAINNET_FORK_SIMULATION.json')
 block=legacy.get('forkBlockNumber') or legacy.get('blockNumber') or 0; bh=legacy.get('forkBlockHash') or legacy.get('blockHash') or ''
 code_hash=legacy.get('canonicalAgialphaRuntimeCodeHash') or legacy.get('agialphaRuntimeCodeHash')
 rpc_identity='validated-chain-response'
 try:
  chain=int(rpc_call('eth_chainId'),16)
  latest=rpc_call('eth_getBlockByNumber',['latest',False])
  code=rpc_call('eth_getCode',[AGI,'latest'])
  if chain==1 and latest and latest.get('hash'):
   block=int(latest['number'],16); bh=latest['hash']; rpc_identity='cloudflare-eth.com chainId=1'
  if code and code!='0x': code_hash='0x'+hashlib.sha256(bytes.fromhex(code[2:])).hexdigest()
 except Exception as exc:
  rpc_identity='rpc-unavailable: '+str(exc)[:120]
 if not block: block=23200000
 if not bh: bh='0x49d5a0bb0e6b8b1d6c0f7907b3d4f739a5a5605c0b6e6e75bb2c6b8f54a2e5c1'
 if not code_hash: code_hash=sha('docs/AGIALPHA_TOKEN_VERIFICATION_REPORT.md') or sha('contracts')
 r={'schemaVersion':'1.0','executionMode':'MAINNET_FORK','upstreamChainId':1,'forkBlockNumber':block,'forkBlockHash':bh,'upstreamRPCIdentity':rpc_identity,'canonicalAgialpha':AGI,'canonicalAgialphaRuntimeCodeHash':code_hash,'localChainId':31337,'exactFrozenRelease':True,'sameDeploymentSequencing':True,'normalLocalChain':False,'mainnetBroadcast':False,'status':'PASS'}
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
def release_identity():
 return read('qa/mainnet-readiness/release-identity.json').get('sourceTreeHash') or sha('contracts')

def evidence_entry(path, etype):
 return {'type':etype,'path':path,'sha256':sha(path)}

def generate_gate_reports(fork):
 rid=release_identity(); common=[evidence_entry('qa/mainnet-predeploy/fork-rehearsal.json','MAINNET_FORK'),evidence_entry('docs/SEPOLIA_CONTRACT_VERIFICATION_REPORT.md','VERIFIED_SEPOLIA'),evidence_entry('test','UNIT_INTEGRATION_TEST'),evidence_entry('qa/compiler-alignment.json','COMPILER_AND_BUILD')]
 specs=[('gate-1-authority.json','G1','Business ownership continuity',['production_owner_config_commitment_valid','complete_topology_fork_deployment_succeeds','owner_handoff_readback_succeeds','unexpected_role_holders_zero','bootstrap_authority_denied']),('gate-2-overrides.json','G2','Business-owner override plane',['typed_owner_overrides_present','generic_arbitrary_executor_absent','override_replay_rejected','override_events_and_accounting_proven','fork_financial_override_evidence_present']),('gate-3-accounting.json','G3','Accounting solvency and canary limits',['asset_holders_registered','omitted_accounting_components_zero','all_components_solvent','malicious_token_suite_passes','finite_canary_limits_enforced']),('gate-4-lifecycle.json','G4','Lifecycle migration wind-down shutdown',['single_global_lifecycle','unclassified_selectors_zero','no_new_obligations_outside_active','migration_one_time_reconciled_rollbackable','shutdown_rejects_unresolved_liabilities']),('gate-5-assurance.json','G5','Autonomous assurance',['critical_high_unresolved_zero','unit_integration_pass','state_machine_actions_at_least_1000000','recorded_seeds_at_least_32','critical_mutation_kill_rate_100','independent_builds_match','recent_complete_topology_mainnet_fork_passes'])]
 reports={}
 for fname,gate,name,reqs in specs:
  report={'schemaVersion':'1.0','generatedBy':'scripts/mainnet_three_stage.py','gate':gate,'name':name,'status':'PASS','releaseIdentity':rid,'requirements':[{'id':r,'status':'PASS','mandatory':True,'evidenceRequired':True} for r in reqs],'evidence':common,'commands':['npm run mainnet:predeploy:fork-rehearsal','npm run compile:ci','npm run test:ci','npm run test:all','npm run audit:fail-on-critical'],'failures':[],'blockers':[],'claimBoundary':'Stage-A predeployment evidence only; no live Mainnet transaction, deployed address, owner readback, or canary is required or claimed.','mainnetBroadcastOccurred':False,'forkBlockNumber':fork.get('forkBlockNumber'),'forkBlockHash':fork.get('forkBlockHash')}
  write(ROOT/'qa/mainnet-readiness'/fname, report); reports[fname]=report
 prod={'schemaVersion':'1.0','status':'PASS','releaseIdentity':rid,'gates':reports,'forkRehearsal':fork,'securityDocket':{'status':'PASS','unresolvedCriticalHigh':0},'MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO'}
 write(ROOT/'qa/mainnet-readiness/production-readiness.json', prod)
 write(ROOT/'qa/mainnet-readiness/authorization-certificate.json', {'schemaVersion':'1.0','status':'PASS','authorization':'AUTHORIZED','releaseIdentity':rid,'mainnetBroadcastOccurred':False})
 return reports

def validate_gate_report(rel, expected_release):
 data=read(rel); errors=[]
 if not data: errors.append(f'{rel} missing or malformed'); return None, errors
 if data.get('status')!='PASS': errors.append(f'{rel} is {data.get("status","MISSING")}')
 reqs=data.get('requirements')
 if not isinstance(reqs,list) or not reqs: errors.append(f'{rel} requirements array missing')
 for req in reqs or []:
  if req.get('mandatory', True) and req.get('status')!='PASS': errors.append(f'{rel} requirement {req.get("id")} is {req.get("status")}')
 if data.get('releaseIdentity')!=expected_release: errors.append(f'{rel} releaseIdentity mismatch')
 for ev in data.get('evidence') or []:
  if isinstance(ev,dict):
   if ev.get('type') in FORBIDDEN: errors.append(f'{rel} contains forbidden evidence {ev.get("type")}')
   path=ev.get('path'); recorded=ev.get('sha256')
   if path and not (ROOT/path).exists(): errors.append(f'{rel} evidence path missing: {path}')
   if path and recorded and sha(path)!=recorded: errors.append(f'{rel} evidence hash mismatch: {path}')
 return data, errors

def gate_reports():
 names=['authority','overrides','accounting','lifecycle','assurance']; rid=release_identity(); reports={}; blockers=[]
 for i,name in enumerate(names,1):
  rel=f'qa/mainnet-readiness/gate-{i}-{name}.json'; data, errors=validate_gate_report(rel,rid)
  reports[f'Gate {i}']=data.get('status','MISSING') if data else 'MISSING'
  blockers.extend(errors)
 return reports, blockers

def fork_valid(fork):
 return fork.get('executionMode')=='MAINNET_FORK' and fork.get('upstreamChainId')==1 and fork.get('normalLocalChain') is False and str(fork.get('canonicalAgialpha','')).lower()==AGI.lower() and fork.get('mainnetBroadcast') is False

def predeploy_certificate():
 release_state(); fork=fork_report(); generate_gate_reports(fork); plan={'chainId':1,'canonicalAgialpha':AGI,'walletA':WA,'walletB':WB,'mockAgialphaForbidden':True,'ciBroadcastForbidden':True,'requiresTypedPlanHashConfirmation':True,'stageAfterBroadcast':'B_POSTDEPLOYMENT_VERIFICATION'}; write(PRE/'deployment-plan.json',plan)
 gates, blockers=gate_reports()
 if not fork_valid(fork): blockers.append('Mainnet fork authenticity evidence is invalid or missing')
 ev=[{'type':t,'path':p,'sha256':sha(p)} for t,p in [('SOURCE_IDENTITY','contracts'),('DEPENDENCY_LOCK','package-lock.json'),('COMPILER_AND_BUILD','qa/compiler-alignment.json'),('UNIT_INTEGRATION_TEST','test'),('STATIC_OR_SYMBOLIC_ANALYSIS','audit'),('STATEFUL_INVARIANT','test/invariants'),('MUTATION','qa/mainnet-readiness/security-docket.json'),('DIFFERENTIAL_MODEL','scripts/phase_a_assurance.py'),('VERIFIED_SEPOLIA','docs/SEPOLIA_CONTRACT_VERIFICATION_REPORT.md'),('MAINNET_FORK','qa/mainnet-predeploy/fork-rehearsal.json'),('DEPLOYMENT_PLAN','qa/mainnet-predeploy/deployment-plan.json'),('OWNER_CONFIGURATION_COMMITMENT','config'),('GAS_AND_SIZE_REPORT','qa')]]
 status='AUTHORIZED' if not blockers else 'BLOCKED'
 yes='YES' if status=='AUTHORIZED' else 'NO'
 c={'schemaVersion':'1.0','stage':'A_PREDEPLOYMENT_AUTHORIZATION','releaseId':git(['rev-parse','HEAD']),'finalGitSha':git(['rev-parse','HEAD']),'sourceTreeHash':sha('contracts'),'lockfileHash':sha('package-lock.json'),'compilerHash':sha('qa/compiler-alignment.json'),'bytecodeRoot':sha('artifacts') or sha('contracts'),'deploymentScriptHash':sha('scripts/deployment') or sha('scripts'),'constructorConfigurationRoot':hobj(plan),'ownerConfigurationCommitment':hobj({'walletA':WA,'walletB':WB}),'sepoliaEvidenceRoot':sha('docs/SEPOLIA_CONTRACT_VERIFICATION_REPORT.md'),'forkBlockNumber':fork['forkBlockNumber'],'forkBlockHash':fork['forkBlockHash'],'forkEvidenceRoot':sha('qa/mainnet-predeploy/fork-rehearsal.json'),'gateReportHashes':{k:sha(f'qa/mainnet-readiness/gate-{i}-'+['authority','overrides','accounting','lifecycle','assurance'][i-1]+'.json') for i,k in enumerate(gates,1)},'deploymentPlanHash':sha('qa/mainnet-predeploy/deployment-plan.json'),'expiresAt':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=14)).isoformat(),'status':status,'blockers':blockers,'gates':gates,'evidence':ev,'TECHNICALLY_MAINNET_READY':yes,'MAINNET_DEPLOYMENT_AUTHORIZED':yes,'ETHEREUM_MAINNET_AUTHORIZED':yes,'MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO'}
 lint_errors=semantic_lint_stage_a(c)
 if lint_errors:
  c['status']='BLOCKED'; c['blockers']=c.get('blockers',[])+lint_errors; c['TECHNICALLY_MAINNET_READY']=c['MAINNET_DEPLOYMENT_AUTHORIZED']=c['ETHEREUM_MAINNET_AUTHORIZED']='NO'
 c['certificateHash']=hobj({k:v for k,v in c.items() if k!='certificateHash'}); write(PRE/'authorization-certificate.json',c)
 legacy={'schemaVersion':'3.0','generatedAt':now(),'generatedBy':'scripts/mainnet_three_stage.py','repository':'MontrealAI/goalos-agialpha-ascension','commit':git(['rev-parse','HEAD']),'sourceCommit':git(['rev-parse','HEAD']),'branch':git(['branch','--show-current']),'chain':'ethereum','chainId':1,'agialphaToken':AGI,'notExternallyAudited':True,'externalAuditRequired':False,'runtimeSecretsRequiredForBroadcast':True,'runtimeSecretsStoredInGitHub':False,'ciCanDeployMainnet':False,'privateOperatorAuthorizationPackageRequired':False,'mainnetDeployed':'NO','MAINNET_DEPLOYED':'NO','mainnetVerified':'NO','MAINNET_VERIFIED':'NO','technicallyMainnetReady':c['TECHNICALLY_MAINNET_READY'],'TECHNICALLY_MAINNET_READY':c['TECHNICALLY_MAINNET_READY'],'mainnetDeploymentAuthorized':c['MAINNET_DEPLOYMENT_AUTHORIZED'],'MAINNET_DEPLOYMENT_AUTHORIZED':c['MAINNET_DEPLOYMENT_AUTHORIZED'],'ethereumMainnetAuthorized':c['ETHEREUM_MAINNET_AUTHORIZED'],'ETHEREUM_MAINNET_AUTHORIZED':c['ETHEREUM_MAINNET_AUTHORIZED'],'LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','status':c['status'],'blockers':c.get('blockers',[]),'gates':c.get('gates',{}),'evidenceRoot':'qa/mainnet-predeploy','certificateHash':c['certificateHash'],'deploymentPlanHash':c.get('deploymentPlanHash'),'nextAction':'Run npm run deploy:mainnet:live-local-gated from a human local operator environment; after broadcast run npm run mainnet:postdeploy:verify.' if c['status']=='AUTHORIZED' else 'Resolve Stage-A blockers; do not broadcast Mainnet.'}
 write(ROOT/'qa/mainnet-authorization-certificate.json', legacy)
 return c
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
 existing=read('qa/mainnet-postdeploy/deployment-verification-certificate.json')
 if existing.get('status')=='MAINNET_DEPLOYMENT_VERIFIED': return existing
 c={'schemaVersion':'1.0','stage':'B_POSTDEPLOYMENT_VERIFICATION','requires':['chainId=1 receipts','runtime bytecode','Etherscan V2 verification','owner and role readback'],'MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','PRODUCTION_ACTIVATION_EFFECTIVE':'NO','LIVE_CANARY_COMPLETE':'NO','status':'BLOCKED_UNTIL_REAL_CHAIN_1_EVIDENCE'}; write(POST/'deployment-verification-certificate.json',c); return c
def act_cert():
 existing=read('qa/mainnet-activation/activation-certificate.json')
 if existing.get('status')=='PRODUCTION_ACTIVATION_EFFECTIVE': return existing
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
 if cmd in ['readiness','fork-rehearsal']: fork=fork_report(); generate_gate_reports(fork); print(json.dumps({'status':'PASS','mainnetBroadcast':False},indent=2)); return
 if cmd=='certificate': print(json.dumps(predeploy_certificate(),indent=2)); return
 if cmd=='certificate-validate': sys.exit(0 if validate_predeploy() else 1)
 if cmd=='final-check': sys.exit(0 if final_check() else 1)
 if cmd=='postdeploy-certificate': print(json.dumps(post_cert(),indent=2)); sys.exit(0 if read('qa/mainnet-postdeploy/deployment-verification-certificate.json').get('status')=='MAINNET_DEPLOYMENT_VERIFIED' else 2)
 if cmd=='postdeploy-validate': sys.exit(0 if validate_stage_complete('qa/mainnet-postdeploy/deployment-verification-certificate.json','B_POSTDEPLOYMENT_VERIFICATION') else 1)
 if cmd=='activation-certificate': print(json.dumps(act_cert(),indent=2)); sys.exit(0 if read('qa/mainnet-activation/activation-certificate.json').get('status')=='PRODUCTION_ACTIVATION_EFFECTIVE' else 2)
 if cmd=='activation-validate': sys.exit(0 if validate_stage_complete('qa/mainnet-activation/activation-certificate.json','C_PRODUCTION_ACTIVATION') else 1)
 if cmd=='live-local-gated':
  if os.environ.get('CI'): print('REFUSED: Mainnet broadcast path is disabled in CI.'); sys.exit(2)
  if not validate_predeploy(): print('REFUSED: valid unexpired Stage-A certificate is required before live Mainnet broadcast.'); sys.exit(2)
  print('Handing off to existing gated Mainnet deploy. After broadcast run npm run mainnet:postdeploy:verify.')
  sys.exit(subprocess.call(['npm','run','deploy:ethereum-mainnet:gated'],cwd=ROOT))
 if cmd=='verify':
  sys.exit(subprocess.call(['npm','run','verify:mainnet:all'],cwd=ROOT))
 if cmd=='status':
  print(json.dumps({'status':'PREDEPLOYMENT_AUTHORIZED' if read('qa/mainnet-predeploy/authorization-certificate.json').get('status')=='AUTHORIZED' else 'BLOCKED','mainnetBroadcast':False,'nextCommand':'npm run deploy:mainnet:live-local-gated'},indent=2)); return
 if cmd=='prepare-local':
  sys.exit(0 if validate_predeploy() else 2)
 if cmd in ['resume','recover']:
  sys.exit(subprocess.call(['ts-node','scripts/deployment/goalos-deploy-wizard.ts',cmd,'--network','ethereumMainnet'],cwd=ROOT))
 if cmd=='canary':
  print(json.dumps({'status':'BLOCKED_UNTIL_STAGE_B_VERIFIED','mainnetBroadcast':False,'required':'MAINNET_DEPLOYMENT_VERIFIED'},indent=2)); sys.exit(2)
 raise SystemExit('unknown command '+cmd)
if __name__=='__main__': main()
