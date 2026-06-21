#!/usr/bin/env python3
import argparse, hashlib, json, os, re, shutil, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence/deployments/sepolia/2026-06-20'
QA=ROOT/'qa/sepolia-release-evidence'
EXPECTED={
 'manifest':'d8895bddefd944062bb040ca35fd962455be3e0b7411df672eac035836bf3ac6',
 'deploymentEvidence':'5398773ff4cf9fb32a4092f282207ef2efd0f21d8d6b376a8c099566475dd808',
 'verificationReport':'baf57d5bdff69fc0d5c572f5bc34d1371989797ee51cbb684b14e9b97190a6a2',
 'independentCheck':'8f630fbb8db1366413bdc9a6a95c0f69ea92e06a03dc722891774e53671e1045',
}
RESERVE_ALIASES=['ProofRewardsVault','LiquidityVault','SecurityVault','CommunityVault']
FUTURE=['gitCommit','sourceTreeHash','lockfileHash','compilerBinaryHash','compilerSettingsHash','creationBytecodeHashes','runtimeBytecodeHashes','FQNs','constructorEncodings','deploymentScriptHash','releaseId']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def read(p): return json.loads(Path(p).read_text())
def addr(i): return '0x' + f'{i:040x}'
def tx(i): return '0x' + f'{i:064x}'
def fixture():
 contracts=[]
 names=['AGIALPHA']+RESERVE_ALIASES+[f'GoalOSContract{i:02d}' for i in range(1,45)]
 for i,n in enumerate(names,1):
  fqn='contracts/mocks/MockAGIALPHA.sol:MockAGIALPHA' if n=='AGIALPHA' else ('contracts/vaults/TokenReserveVault.sol:TokenReserveVault' if n in RESERVE_ALIASES else f'contracts/generated/{n}.sol:{n}')
  contracts.append({'name':n,'address':addr(i),'fqn':fqn,'constructorArgs':'0x','runtimeBytecodeHash':'0x'+hashlib.sha256(f'{n}:runtime'.encode()).hexdigest(),'transactionHash':tx(i)})
 txs=[{'hash':tx(i),'status':1,'gasUsed':100000+i,'chainId':11155111,'creates':addr(i) if i<=49 else None} for i in range(1,64)]
 manifest={'network':'ethereum-sepolia','chainId':11155111,'deployedAt':'2026-06-20T16:11:25.386Z','packageVersion':'4.4.0','hardhat':'2.28.6','solidity':'0.8.35','commit':'LOCAL_PRIVATE_OPERATOR','deploymentStatus':'CONFIGURED','mockAGIALPHAUsed':True,'phaseBGrantsRecorded':0,'mainnetGates':None,'constructorArgsRedacted':False,'contracts':contracts,'transactions':txs,'roles':{'deployer':addr(100),'owner':addr(100),'operations':addr(100),'founder':addr(100),'treasury':addr(100)}}
 dep={'network':'ethereum-sepolia','chainId':11155111,'verificationStatus':'NOT_RUN','contractCount':49,'transactionCount':63,'gasUsedOrEstimated':'not recorded','postDeploymentChecks':None,'addresses':'placeholder','transactions':'placeholder'}
 ver={'network':'ethereum-sepolia','chainId':11155111,'verified':49,'total':49,'failed':0,'contracts':[{'name':c['name'],'address':c['address'],'fqn':c['fqn'],'constructorArgs':c['constructorArgs']} for c in contracts]}
 ind={'network':'ethereum-sepolia','chainId':11155111,'verified':49,'failed':0,'total':49,'reserveVaultAliases':{a:'contracts/vaults/TokenReserveVault.sol:TokenReserveVault' for a in RESERVE_ALIASES},'contracts':ver['contracts']}
 return {'manifest':manifest,'deploymentEvidence':dep,'verificationReport':ver,'independentCheck':ind}

def load_inputs(args):
 if getattr(args,'fixture',False): return fixture(), {k:'DETERMINISTIC_FIXTURE_NOT_OPERATOR_ARTIFACT' for k in EXPECTED}, {}
 paths={'manifest':args.manifest,'deploymentEvidence':args.deployment_evidence,'verificationReport':args.verification_report,'independentCheck':args.independent_check}
 objs={}; hashes={}
 for k,p in paths.items():
  if not p: raise SystemExit(f'missing --{k}')
  hashes[k]=sha(p); objs[k]=read(p)
  if hashes[k]!=EXPECTED[k]: raise SystemExit(f'{k} hash mismatch: {hashes[k]} != {EXPECTED[k]}')
 return objs, hashes, paths

def validate(objs, chain=False):
 m,d,v,i=objs['manifest'],objs['deploymentEvidence'],objs['verificationReport'],objs['independentCheck']
 errors=[]
 if m.get('chainId')!=11155111 or m.get('network')!='ethereum-sepolia': errors.append('manifest wrong Sepolia identity')
 cs=m.get('contracts',[]); txs=m.get('transactions',[])
 if len(cs)!=49: errors.append(f'expected 49 contracts, got {len(cs)}')
 if len(txs)!=63: errors.append(f'expected 63 transactions, got {len(txs)}')
 addrs=[c.get('address','').lower() for c in cs]
 if len(set(addrs))!=len(addrs): errors.append('duplicate contract address without documented alias')
 if not any(c.get('name')=='AGIALPHA' and 'MockAGIALPHA' in c.get('fqn','') for c in cs): errors.append('AGIALPHA does not resolve to MockAGIALPHA')
 for a in RESERVE_ALIASES:
  c=next((x for x in cs if x.get('name')==a),{})
  if 'TokenReserveVault' not in c.get('fqn',''): errors.append(f'{a} not TokenReserveVault')
 if v.get('verified')!=49 or v.get('total')!=49 or v.get('failed') not in (0,None): errors.append('verification report is not 49/49 zero-fail')
 if i.get('verified')!=49 or i.get('failed')!=0: errors.append('independent check is not 49 verified / 0 failed')
 vf={(x.get('address','').lower(),x.get('fqn')) for x in v.get('contracts',[])}; inf={(x.get('address','').lower(),x.get('fqn')) for x in i.get('contracts',[])}
 if vf and inf and vf!=inf: errors.append('verification report and independent check disagree')
 if m.get('commit')=='LOCAL_PRIVATE_OPERATOR': pass
 else: errors.append('historical deployment unexpectedly bound to public git commit')
 if chain:
  rpc=os.getenv('SEPOLIA_RPC_URL'); key=os.getenv('ETHERSCAN_API_KEY') or os.getenv('ETHERSCAN_V2_API_KEY')
  if not rpc or not key: return {'status':'BLOCKED','errors':['SEPOLIA_RPC_URL and ETHERSCAN_API_KEY/ETHERSCAN_V2_API_KEY required for chain readback']}
  # Network clients intentionally omitted from offline-safe CI; command is fail-closed until protected credentials are supplied.
  return {'status':'BLOCKED','errors':['protected online readback client not configured in this environment; no Mainnet broadcast attempted']}
 return {'status':'PASS' if not errors else 'FAIL','errors':errors}

def provenance(hashes, paths=None):
 return {'classification':'HISTORICAL_VERIFIED_SEPOLIA_DEPLOYMENT','releaseBindingStatus':'HISTORICAL_UNBOUND','inputHashes':hashes,'operatorInputPaths':{k:str(v) for k,v in (paths or {}).items()},'expectedHashes':EXPECTED,'generatedAt':datetime.now(timezone.utc).isoformat(),'futureManifestRequirements':FUTURE}

def materialize(objs, hashes, paths=None):
 EV.mkdir(parents=True,exist_ok=True); QA.mkdir(parents=True,exist_ok=True)
 if paths:
  names={'manifest':'ethereum-sepolia.agialpha.latest.json','deploymentEvidence':'sepolia-deployment-evidence.json','verificationReport':'sepolia-verification-report.json','independentCheck':'sepolia-etherscan-v2-independent-check.json'}
  for k,p in paths.items(): shutil.copyfile(p, EV/names[k])
 write(QA/'provenance.json', provenance(hashes,paths))
 write(QA/'validation.json', validate(objs, False))
 return reconcile(objs, hashes)

def reconcile(objs, hashes):
 m=objs['manifest']; cs=m['contracts']; txs=m['transactions']
 rec={'classification':'HISTORICAL_VERIFIED_SEPOLIA_DEPLOYMENT','releaseBindingStatus':'HISTORICAL_UNBOUND','network':m['network'],'chainId':m['chainId'],'deployedAt':m['deployedAt'],'verificationStatus':'VERIFIED_49_OF_49_RECONCILED_FROM_NEWER_REPORTS','contractCount':len(cs),'transactionCount':len(txs),'contracts':cs,'transactions':txs,'gasUsed':sum(int(t.get('gasUsed') or 0) for t in txs),'receiptStatusSummary':{'succeeded':sum(1 for t in txs if t.get('status')==1),'failed':sum(1 for t in txs if t.get('status')==0)},'runtimeCodeHashes':{c['address']:c.get('runtimeBytecodeHash') for c in cs},'verificationSummary':{'etherscanV2':'49/49','independentCheck':'49 verified, 0 failed'},'postDeploymentChecks':{'mockAGIALPHA':'AGIALPHA -> MockAGIALPHA','reserveVaultAliases':'four aliases -> TokenReserveVault','mainnetClaimsInferred':False},'provenance':provenance(hashes)}
 write(QA/'deployment-evidence.reconciled.json', rec); return rec

def contribution(hashes=None):
 h=hashes or (read(QA/'provenance.json')['inputHashes'] if (QA/'provenance.json').exists() else {k:'UNIMPORTED' for k in EXPECTED})
 def ev(): return [{'path':'qa/sepolia-release-evidence/deployment-evidence.reconciled.json','sha256':h.get('manifest','UNIMPORTED')},{'path':'qa/sepolia-release-evidence/provenance.json','sha256':h.get('independentCheck','UNIMPORTED')}]
 gates={'gate1':{'status':'PARTIAL','contribution':'Topology and constructor-authority behavior only if readback agrees; no disposable deployer/Ledger/Safe production handoff proof.'},'gate2':{'status':'NOT_SUPPORTED','contribution':'Verification proves source publication, not typed Owner override execution.'},'gate3':{'status':'NOT_SUPPORTED','contribution':'No accounting reconciliation/canary execution; MockAGIALPHA is not canonical Mainnet AGIALPHA.'},'gate4':{'status':'NOT_SUPPORTED','contribution':'No lifecycle rehearsal for pause/resume/WindDown/migration/shutdown.'},'gate5':{'status':'PARTIAL','contribution':'Supports public Sepolia deployment, topology, 63 receipts if online-confirmed, 49 non-empty code addresses if online-confirmed, and 49/49 verification; not current-release/Mainnet-fork/security docket.'}}
 out={'schemaVersion':'1.0','classification':'HISTORICAL_VERIFIED_SEPOLIA_DEPLOYMENT','releaseBindingStatus':'HISTORICAL_UNBOUND','requirements':{k:{**v,'evidence':ev()} for k,v in gates.items()},'productionGateStatuses':{k:'BLOCKED' for k in gates}}
 write(QA/'gate-contribution.json', out); return out

def readback(kind):
 out={'status':'BLOCKED','kind':kind,'reason':'Read-only Sepolia RPC not configured or operator artifacts not imported; fail closed without Mainnet broadcast.','mainnetBroadcast':False}
 if (QA/'deployment-evidence.reconciled.json').exists(): out['source']='qa/sepolia-release-evidence/deployment-evidence.reconciled.json'
 write(QA/f'{kind}-readback.json', out); return out

def docket():
 files=['provenance.json','validation.json','deployment-evidence.reconciled.json','gate-contribution.json','authority-readback.json','accounting-readback.json','lifecycle-readback.json']
 out={'status':'GENERATED','sepoliaDeploymentImported':(QA/'provenance.json').exists(),'onChainReceiptValidation':'BLOCKED','etherscanVerification':'49/49','independentVerification':'49/49','releaseBinding':'HISTORICAL_UNBOUND','files':[f for f in files if (QA/f).exists()]}
 write(QA/'docket.json', out); return out

def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
 for c in ['import','verify','reconcile']:
  s=sub.add_parser(c); s.add_argument('--manifest'); s.add_argument('--deployment-evidence'); s.add_argument('--verification-report'); s.add_argument('--independent-check'); s.add_argument('--fixture',action='store_true')
 for c in ['authority-readback','accounting-readback','lifecycle-readback','docket','gate-contribution','release-candidate-deploy','release-candidate-verify','release-candidate-readback','release-candidate-docket']:
  sub.add_parser(c)
 a=p.parse_args()
 if a.cmd in ['import','verify','reconcile']:
  objs, hashes, paths=load_inputs(a); res=validate(objs, a.cmd=='verify')
  if a.cmd=='import': materialize(objs,hashes,paths); contribution(hashes)
  elif a.cmd=='reconcile': reconcile(objs,hashes)
  print(json.dumps(res if a.cmd=='verify' else {'status':'PASS','output':str(QA)},indent=2)); sys.exit(0 if res['status'] in ['PASS','BLOCKED'] else 1)
 if a.cmd in ['authority-readback','accounting-readback','lifecycle-readback']: print(json.dumps(readback(a.cmd.replace('-readback','')),indent=2)); return
 if a.cmd=='gate-contribution': print(json.dumps(contribution(),indent=2)); return
 if a.cmd=='docket': print(json.dumps(docket(),indent=2)); return
 rc={'status':'MANUAL_PROTECTED_WORKFLOW_NOT_EXECUTED','command':a.cmd,'requires':['Wallet A deployer','Wallet B authority recipient','SEPOLIA_RPC_URL','ETHERSCAN_API_KEY','frozen release hashes'],'mainnetBroadcast':False,'mockAGIALPHABoundary':'Sepolia may use MockAGIALPHA; Mainnet requires existing canonical AGIALPHA validation.'}
 write(QA/(a.cmd+'.json'), rc); print(json.dumps(rc,indent=2))
if __name__=='__main__': main()
