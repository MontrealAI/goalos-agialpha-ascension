#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, getpass, hashlib, json, os, pathlib, re, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
QA=ROOT/'qa/dormant-mainnet'; DEP=ROOT/'deployments/dormant-mainnet'; EVI=ROOT/'evidence/dormant-mainnet'; DOC=ROOT/'docs/dormant-mainnet'; PRIV=ROOT/'.private/dormant-mainnet'
CERT=QA/'dormant-initial-mainnet-certificate.json'; PLAN_PUB=QA/'deployment-plan.public.json'; PLAN_PRIV=PRIV/'deployment-plan.private.json'; POLICY=PRIV/'authority-policy.mainnet.json'
WALLET_A='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; WALLET_B='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'; AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
STATUS='AUTHORIZED_FOR_DORMANT_INITIAL_DEPLOYMENT_ONLY'; BANNER='DORMANT INITIAL MAINNET DEPLOYMENT — NOT PRODUCTION READY — NO USER FUNDS — NO ACTIVATION — NO PUBLIC RELIANCE'
DISCLAIMER='This deployment is operationally dormant and unfunded. It is not guaranteed to be globally frozen against unsolicited third-party calls or transfers.'
NO_FLAGS=['productionReady','productionDeploymentAuthorized','userFundsAuthorized','userDepositsAuthorized','protocolActivationAuthorized','phaseBConfigurationAuthorized','publicRelianceAuthorized','publicFrontendAuthorized','productionAnnouncementAuthorized','tokenFundingAuthorized','treasuryFundingAuthorized']
CONTRACTS=['CommercializationPerformanceVault','ProofRewardsVault','LiquidityVault','SecurityVault','CommunityVault','ProofSeedRegistry','LegacyAGIJobManagerRegistry','ReputationRegistry','ReferralRegistry','ProofCardRegistry','ProofCredentialRegistry','JobRegistry','JobClaimBondManager','PremiumAccessRegistry','ProofSubmissionRegistry','ReviewerBondRegistry','TreasuryRouter','ProtocolConfigRegistry','LaunchGateRegistry','DisputeRegistry','AppealRegistry','SponsorRegistry','BuilderProfileRegistry','CredentialRevocationRegistry','AEPAgentRegistry','AEPArtifactRegistry','AEPGoalOSCommitRegistry','AEPRunCommitmentRegistry','AEPProofLedger','AEPEvalRegistry','AEPAttestationRegistry','AEPSelectionGate','AEPRolloutRouter','AEPRollbackRegistry','AEPEvidenceDocketRegistry','AEPProofBundleRegistry','AlphaWorkUnitLedger','MandateEpochRegistry','AGIEthNamespaceRegistry','AEPConformanceRegistry','AEPClaimBoundaryRegistry','AEPReplayRegistry','AEPCommitRevealValidationRegistry','AEPEvaluatorStakingRegistry','AEPSlashingCourt','AEPRewardVault','AEPChronicleRegistry','AEPFalsificationRegistry']
PHASE_B=['JobRegistry<-ClaimBond','JobRegistry<-ProofSubmissions','ClaimBond<-ProofSubmissions','ProofSubmissions<-ReviewerBonds','ProofCards<-ProofSubmissions','Credentials<-ProofSubmissions','Credentials<-Revocations','Reputation<-ProofSubmissions','Referrals<-ProofSubmissions','ProofSeeds<-operationsAddress','LegacyRegistry<-operationsAddress','ProtocolConfig<-operationsAddress','LaunchGates<-operationsAddress','EvaluatorStaking<-SlashingCourt']
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'))
def shabytes(b): return '0x'+hashlib.sha256(b).hexdigest()
def sha_path(p):
 p=ROOT/p if not isinstance(p,pathlib.Path) or not p.is_absolute() else p
 if not p.exists(): return None
 if p.is_file(): return shabytes(p.read_bytes())
 h=hashlib.sha256()
 for f in sorted(x for x in p.rglob('*') if x.is_file() and '.git' not in x.parts and '.private' not in x.parts): h.update(str(f.relative_to(ROOT)).encode()+b'\0'+f.read_bytes())
 return '0x'+h.hexdigest()
def hobj(o): return shabytes(canon(o).encode())
def run(args):
 try: return subprocess.check_output(args,cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return ''
def load(p):
 p=ROOT/p if isinstance(p,str) else p
 return json.loads(p.read_text()) if p.exists() else None
def atomic_private(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.',text=True); os.write(fd,(json.dumps(obj,indent=2)+'\n').encode()); os.fsync(fd); os.close(fd); os.chmod(tmp,0o600); os.replace(tmp,path)
def write_json(path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2)+'\n')
def release():
 pkg=load('package.json') or {}; lock=load('package-lock.json') or {}; hh=(ROOT/'hardhat.config.ts').read_text()
 return {'gitCommit':run(['git','rev-parse','HEAD']),'gitDirty':bool(run(['git','status','--porcelain'])),'packageVersion':pkg.get('version'),'packageEngines':pkg.get('engines',{}),'packageLockSha256':sha_path('package-lock.json'),'nodeVersion':run(['node','--version']),'npmVersion':run(['npm','--version']),'hardhatVersion':run(['npx','hardhat','--version']),'solidityVersion':re.search(r'version:\s*"([^"]+)"',hh).group(1),'optimizer':{'enabled':'enabled: true' in hh,'runs':200},'evmTarget':'compiler default (not explicitly set)'}
def fqn(name):
 matches=list((ROOT/'contracts').rglob(name+'.sol'))
 return f"{matches[0].relative_to(ROOT)}:{name}" if matches else name
def constructor_args(name):
 if name in ['CommercializationPerformanceVault']: return ['COMMERCIALIZATION_PERFORMANCE_ADMIN',AGI]
 if name in ['ProofRewardsVault','LiquidityVault','SecurityVault','CommunityVault']: return [name.upper()+'_ADMIN',AGI,'purpose string']
 if name in ['ProofSeedRegistry','JobRegistry','AEPGoalOSCommitRegistry','MandateEpochRegistry','AEPEvaluatorStakingRegistry']: return [WALLET_B,AGI,WALLET_B]
 if name=='JobClaimBondManager': return [WALLET_B,AGI,'JobRegistry',WALLET_B]
 if name=='PremiumAccessRegistry': return [WALLET_B,AGI,'ReputationRegistry']
 if name=='ProofSubmissionRegistry': return [WALLET_B,AGI,'JobRegistry','JobClaimBondManager','ProofCardRegistry','ProofCredentialRegistry','ReputationRegistry',WALLET_B]
 if name=='ReviewerBondRegistry': return [WALLET_B,AGI,'ProofSubmissionRegistry',WALLET_B]
 if name=='TreasuryRouter': return [WALLET_B,WALLET_B]
 if name in ['LegacyAGIJobManagerRegistry']: return [WALLET_B,'0xb3aaeb69b630f0299791679c063d68d6687481d1']
 if name in ['DisputeRegistry']: return [WALLET_B,'ReputationRegistry']
 if name in ['CredentialRevocationRegistry']: return [WALLET_B,'ProofCredentialRegistry']
 if name in ['AEPSlashingCourt']: return [WALLET_B,'AEPEvaluatorStakingRegistry']
 if name in ['AEPRewardVault']: return [WALLET_B,AGI]
 return [WALLET_B]
def inventories():
 rel=release(); instances=[]; auth=[]
 for i,n in enumerate(CONTRACTS):
  args=constructor_args(n); instances.append({'index':i,'contractName':n,'fullyQualifiedName':fqn(n),'constructorArgs':args,'walletAAppearsInConstructor':any(str(a).lower()==WALLET_A.lower() for a in args),'value':'0','phase':'A_DORMANT_DEPLOYMENT'})
  auth.append({'contractName':n,'expectedOwner':WALLET_B,'expectedPendingOwner':None,'managedRoles':{'DEFAULT_ADMIN_ROLE':[WALLET_B]},'nonRoleAuthorityValues':[a for a in args if isinstance(a,str) and a.startswith('0x')],'economicDestinations':[a for a in args if str(a).lower()==WALLET_B.lower() or str(a).lower()==AGI.lower()],'walletAProhibitedEverywhere':True,'unknownAuthoritySurfaceFailsGate':True})
 write_json(QA/'deployment-instance-inventory.json',{'banner':BANNER,'release':rel,'chainId':1,'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGI,'instances':instances,'phaseBPlannedForbidden':PHASE_B})
 write_json(QA/'authority-surface-inventory.json',{'banner':BANNER,'disclaimer':DISCLAIMER,'release':rel,'surfaces':auth,'publicStateChangingFunctionsDocumented':'see docs/DORMANT_MAINNET_AUTHORITY_AND_DORMANCY_MODEL.md','productionAuthorizationPreserved':['qa/mainnet-authorization-certificate.json','npm run mainnet:certificate','npm run mainnet:certificate:validate','npm run deploy:ethereum-mainnet:gated']})
 return instances,auth
def plan():
 instances,_=inventories(); start=int(os.environ.get('DORMANT_MAINNET_STARTING_NONCE','0')); maxfee=os.environ.get('DORMANT_MAINNET_MAX_FEE_GWEI'); prio=os.environ.get('DORMANT_MAINNET_MAX_PRIORITY_FEE_GWEI')
 txs=[]
 for i,inst in enumerate(instances):
  txs.append({'index':i,'kind':'deployment','configuration':False,'phaseB':False,'expectedNonce':start+i,'contractName':inst['contractName'],'fullyQualifiedName':inst['fullyQualifiedName'],'expectedCreateAddress':'DERIVED_AT_RUNTIME_FROM_WALLET_A_AND_NONCE','constructorArgsCommitment':hobj(inst['constructorArgs']),'initcodeHash':'REQUIRES_COMPILE_ARTIFACT','expectedRuntimeBytecodeHash':'REQUIRES_COMPILE_ARTIFACT','gasEstimate':'REQUIRES_RPC_ESTIMATE','gasLimit':'estimate_plus_margin','value':'0','maxFeePerGasGwei':maxfee,'maxPriorityFeePerGasGwei':prio})
 phase=[{'kind':'phaseB-configuration','label':x,'planned':True,'forbiddenInDormantMode':True,'executed':False} for x in PHASE_B]
 obj={'schemaVersion':1,'banner':BANNER,'disclaimer':DISCLAIMER,'deploymentStatus':'DORMANT_UNCONFIGURED','phaseBExecuted':False,'phaseBConfigurationAuthorized':False,'chainId':1,'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGI,'startingNonce':start,'transactions':txs,'phaseBPlan':phase,'feePolicy':{'maxFeeGwei':maxfee,'maxPriorityFeeGwei':prio,'maxTotalCostEth':os.environ.get('DORMANT_MAINNET_MAX_TOTAL_COST_ETH'),'minRemainingEth':os.environ.get('DORMANT_MAINNET_MIN_REMAINING_ETH')},'truthBoundary':{k:False for k in NO_FLAGS}|{'dormantInitialMainnetDeploymentAuthorized':True}}
 write_json(PLAN_PUB,obj); atomic_private(PLAN_PRIV,{**obj,'privateConstructorArgs':{x['contractName']:x['constructorArgs'] for x in instances}}); return obj
def policy():
 p={'schemaVersion':1,'chainId':1,'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGI,'instances':[]}
 for n in CONTRACTS: p['instances'].append({'contractName':n,'expectedOwner':WALLET_B,'expectedPendingOwner':None,'expectedRoleHolders':{'DEFAULT_ADMIN_ROLE':[WALLET_B]},'expectedNonRoleAuthorityValues':constructor_args(n),'expectedImmutableEconomicDestinations':[WALLET_B,AGI],'expectedEthBalance':'0','expectedAgialphaBalance':'0','expectedDormancyState':'DORMANT_UNCONFIGURED','expectedRuntimeArtifact':fqn(n),'expectedRuntimeBytecodeHash':'REQUIRES_COMPILE_ARTIFACT'})
 atomic_private(POLICY,p); return p
def blockers():
 b=[]; rel=release()
 if rel['gitDirty']: b.append('Git working tree is dirty; certificate cannot authorize live deployment.')
 for e in ['DORMANT_MAINNET_MAX_FEE_GWEI','DORMANT_MAINNET_MAX_PRIORITY_FEE_GWEI','DORMANT_MAINNET_MAX_TOTAL_COST_ETH','DORMANT_MAINNET_MIN_REMAINING_ETH']: 
  if not os.environ.get(e): b.append(f'Missing fee/funding limit {e}.')
 for p in [PLAN_PUB,POLICY,QA/'mainnet-fork-rehearsal.json',PRIV/'ledger-approval.json']:
  if not p.exists(): b.append(f'Missing required evidence: {p.relative_to(ROOT)}')
 la=load(PRIV/'ledger-approval.json')
 if la and (la.get('recoveredAddress','').lower()!=WALLET_B.lower() or la.get('valid') is not True): b.append('Ledger approval is invalid or does not recover Wallet B.')
 if la and la.get('expiresAt') and la['expiresAt'] <= datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'): b.append('Ledger approval expired.')
 return b
def certificate():
 p=plan() if not PLAN_PUB.exists() else load(PLAN_PUB); pol=policy() if not POLICY.exists() else load(POLICY); rel=release(); b=blockers(); exp=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=12)).replace(microsecond=0).isoformat().replace('+00:00','Z')
 c={'schemaVersion':1,'status':STATUS if not b else 'BLOCKED_DORMANT_INITIAL_DEPLOYMENT','chainId':1,'dormantInitialMainnetDeploymentAuthorized':not b, **{k:False for k in NO_FLAGS}, 'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGI,'gitCommit':rel['gitCommit'],'packageLockSha256':rel['packageLockSha256'],'artifactBundleSha256':sha_path('artifacts') or 'MISSING_ARTIFACTS','deploymentPlanSha256':sha_path(PLAN_PUB),'authorityPolicySha256':sha_path(POLICY),'forkRehearsalSha256':sha_path(QA/'mainnet-fork-rehearsal.json'),'ledgerApprovalSha256':sha_path(PRIV/'ledger-approval.json'),'startingNonce':p.get('startingNonce',0),'expiresAt':exp,'blockers':b,'warnings':['Operational dormancy is not global freeze.'], 'banner':BANNER,'disclaimer':DISCLAIMER}
 write_json(CERT,c); return c
def validate_cert():
 c=load(CERT); errs=[]
 if not c: return ['certificate missing']
 fresh=certificate()
 for k in ['gitCommit','packageLockSha256','deploymentPlanSha256','authorityPolicySha256','forkRehearsalSha256','ledgerApprovalSha256','startingNonce','walletA','walletB','canonicalAgialpha','chainId']:
  if c.get(k)!=fresh.get(k): errs.append(f'{k} mismatch')
 for k in NO_FLAGS:
  if c.get(k) is not False: errs.append(f'{k} must be false')
 if c.get('status')==STATUS and c.get('blockers'): errs.append('authorized status cannot contain blockers')
 if c.get('expiresAt','') <= datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'): errs.append('certificate expired')
 return errs
def reports(kind):
 base={'schemaVersion':1,'banner':BANNER,'disclaimer':DISCLAIMER,'chainId':1,'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGI,'deploymentStatus':'DORMANT_UNCONFIGURED','phaseBExecuted':False,'phaseBConfigurationAuthorized':False,'noMainnetTransactionBroadcastByThisCommand':True}
 paths=[QA/'verification-report.json',QA/'postdeployment-authority-report.json',QA/'dormancy-report.json',QA/'multi-rpc-report.json',QA/'runtime-bytecode-report.json']
 for p in paths: write_json(p,{**base,'status':'PENDING_LIVE_EVIDENCE','checks':[],'blockers':['No live dormant Mainnet deployment evidence has been provided.']})
 manifest={**base,'contracts':{},'publicConstructorArgsCommitment':sha_path(PLAN_PUB)}; write_json(DEP/'ethereum-mainnet.dormant.latest.json',manifest); (DEP/'ethereum-mainnet.dormant.latest.sha256').write_text(sha_path(DEP/'ethereum-mainnet.dormant.latest.json')+'\n')
 idx={'banner':BANNER,'commit':release()['gitCommit'],'planSha256':sha_path(PLAN_PUB),'certificateSha256':sha_path(CERT),'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha_path(p)} for p in [CERT,PLAN_PUB,*paths,DEP/'ethereum-mainnet.dormant.latest.json']]}; write_json(QA/'evidence-index.json',idx)
def docs():
 (ROOT/'docs').mkdir(exist_ok=True); DOC.mkdir(parents=True,exist_ok=True)
 (ROOT/'docs/DORMANT_MAINNET_AUTHORITY_AND_DORMANCY_MODEL.md').write_text(f"# Dormant Mainnet Authority and Dormancy Model\n\n**{BANNER}**\n\n{DISCLAIMER}\n\nWallet A `{WALLET_A}` is only the transaction signer/gas payer/historical creator. Wallet B `{WALLET_B}` is the intended owner/admin from construction. Phase B grants are planned but forbidden and inactive. Unknown authority surfaces fail the gate. Production authorization remains separate in `qa/mainnet-authorization-certificate.json`.\n\nContracts inventoried: {len(CONTRACTS)}. Phase-B planned-forbidden grants: {len(PHASE_B)}.\n")
 (DOC/'DORMANT_INITIAL_MAINNET_DEPLOYMENT_REPORT.md').write_text(f"# Dormant Initial Mainnet Deployment Report\n\n**{BANNER}**\n\n{DISCLAIMER}\n\nStatus: dormant-only evidence namespace. This report is not production authorization and does not authorize user funds, deposits, activation, public reliance, public frontend, funding, treasury funding, or production announcement.\n")
 (DOC/'UBUNTU_OPERATOR_RUNBOOK.md').write_text(f"# Ubuntu Operator Runbook — Dormant Initial Mainnet Deployment\n\n**{BANNER}**\n\n{DISCLAIMER}\n\n1. This workflow is dormant, unfunded, and non-production.\n2. Wallet A is disposable gas payer only: `{WALLET_A}`.\n3. Wallet B is Ledger authority from construction: `{WALLET_B}`.\n4. Never enter a seed phrase. Sign only typed data with Wallet B.\n5. Run no-broadcast checks: `npm run dormant:mainnet:doctor`, `npm run dormant:mainnet:plan`, `npm run dormant:mainnet:fork-rehearsal`, `npm run dormant:mainnet:certificate`, `npm run dormant:mainnet:certificate:validate`.\n6. Ledger proof: `npm run dormant:mainnet:ledger-approve`; store signature only under `.private/dormant-mainnet/`.\n7. Review plan, nonce, contract count, fee caps, and worst-case gas.\n8. Live command: `npm run dormant:mainnet:live` only from local interactive shell after arming.\n9. If interrupted, preserve journal and run `npm run dormant:mainnet:resume`.\n10. Retry verification with `npm run dormant:mainnet:verify`; never redeploy for verification failure.\n11. Run postchecks with `npm run dormant:mainnet:postcheck`.\n12. Generate evidence with `npm run dormant:mainnet:evidence`.\n13. Sweep Wallet A only after all evidence passes: `npm run dormant:mainnet:sweep-deployer`.\n14. Prohibited after deployment: funding contracts, executing Phase B, public launch claims, frontend publication, production announcement.\n15. Later production requires the independent production process; dormant evidence cannot produce production YES.\n\n## Emergency one-page runbook\nRPC outage: stop, do not switch blindly; compare independent RPCs. Gas spike: stop before next transaction and resume from journal. Dropped transaction: classify as dropped before replacing. Replacement: record replacement relationship. Nonce drift: stop. Partial deployment: never rerun from transaction 0; resume only from first unresolved item. Etherscan outage: rerun verification only. Receipt disagreement or reorg: stop until confirmation depth is restored. Unexpected authority: stop and publish blocker. Lost Wallet A before completion: stop; do not skip nonces or redeploy from another account without a new plan/certificate.\n")
def ledger_approve():
 p=load(PLAN_PUB) or plan(); msg={'domain':{'name':'GoalOS Dormant Initial Mainnet Deployment','version':'1','chainId':1},'message':{'gitCommit':release()['gitCommit'],'deploymentPlanSha256':sha_path(PLAN_PUB),'authorityPolicySha256':sha_path(POLICY),'walletA':WALLET_A,'walletB':WALLET_B,'canonicalAgialpha':AGI,'status':STATUS,'noScopeFlags':NO_FLAGS,'statement':'This is not production authorization. No user funds, no activation, no public reliance.','expiresAt':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=12)).replace(microsecond=0).isoformat().replace('+00:00','Z')}}
 sig=os.environ.get('DORMANT_LEDGER_SIGNATURE',''); rec=os.environ.get('DORMANT_LEDGER_RECOVERED_ADDRESS','')
 atomic_private(PRIV/'ledger-approval.json',{'typedData':msg,'signature':sig,'recoveredAddress':rec,'valid':bool(sig) and rec.lower()==WALLET_B.lower(),'expiresAt':msg['message']['expiresAt']}); print(json.dumps({'status':'RECORDED' if sig else 'SIGNATURE_REQUIRED','typedData':msg,'privateOutput':'.private/dormant-mainnet/ledger-approval.json'},indent=2))
def arm():
 c=load(CERT) or certificate(); phrase='AUTHORIZE DORMANT INITIAL MAINNET DEPLOYMENT ONLY — NO USER FUNDS'; print(json.dumps({'walletA':WALLET_A,'walletB':WALLET_B,'chainId':1,'contractCount':len(CONTRACTS),'transactionCount':len(CONTRACTS),'feeCaps':(load(PLAN_PUB) or {}).get('feePolicy'),'planHash':sha_path(PLAN_PUB),'certificateExpiry':c.get('expiresAt'),'NOFlags':NO_FLAGS,'requiredPhrase':phrase},indent=2)); typed=sys.stdin.readline().strip();
 if typed!=phrase: sys.exit('Arming phrase mismatch; no token written.')
 atomic_private(PRIV/'arming-token.json',{'planHash':sha_path(PLAN_PUB),'certificateSha256':sha_path(CERT),'expiresAt':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=15)).replace(microsecond=0).isoformat().replace('+00:00','Z')}); print('ARMED_DORMANT_ONLY')
def live_like(cmd):
 if os.environ.get('CI','').lower() in ['1','true','yes'] or os.environ.get('GITHUB_ACTIONS')=='true': sys.exit('Refusing dormant Mainnet broadcast in CI.')
 if cmd=='live': sys.exit('Dormant live executor is fail-closed in repository automation: requires local signer integration, valid certificate, ledger approval, arming token, clean git, exact nonce, fee caps, and second typed confirmation. No transaction was sent.')
 if cmd=='resume': sys.exit('No resumable live executor ran in this environment; preserve journal if present. No transaction was sent.')
 if cmd=='sweep-deployer': sys.exit('Sweep blocked until receipts, runtime code, verification, authority, dormancy, and evidence reports pass. No transaction was sent.')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('cmd'); args=ap.parse_args();
 if args.cmd in ['doctor','status']:
  inventories(); docs(); print(json.dumps({'status':'PASSED_NO_BROADCAST','release':release(),'contractCount':len(CONTRACTS),'productionAuthorizationPreserved':True},indent=2)); return
 if args.cmd=='plan': policy(); print(json.dumps(plan(),indent=2)); return
 if args.cmd=='fork-rehearsal': write_json(QA/'mainnet-fork-rehearsal.json',{'banner':BANNER,'status':'BLOCKED_REQUIRES_PINNED_MAINNET_FORK_RPC','chainId':1,'forkMainnetRequired':True,'localChainId1IsInsufficient':True,'noBroadcast':True}); sys.exit(1)
 if args.cmd=='ledger-approve': policy(); plan(); ledger_approve(); return
 if args.cmd=='certificate': print(json.dumps(certificate(),indent=2)); return
 if args.cmd=='certificate-validate': errs=validate_cert(); print(json.dumps({'status':'PASSED' if not errs else 'FAILED','errors':errs},indent=2)); sys.exit(1 if errs else 0)
 if args.cmd=='arm': arm(); return
 if args.cmd in ['live','resume','sweep-deployer']: live_like(args.cmd)
 if args.cmd in ['verify','verify-status','postcheck','evidence']: reports(args.cmd); docs(); print(json.dumps({'status':'PENDING_LIVE_EVIDENCE_NO_BROADCAST','outputNamespace':'qa/dormant-mainnet'},indent=2)); return
 sys.exit('unknown command')
if __name__=='__main__': main()
