#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, stat, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
QA=ROOT/'qa/mainnet-predeploy/evidence'
AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'; WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'
REQ_TYPES={'G1_AUTHORITY','G2_OVERRIDES','G3_ACCOUNTING','G4_LIFECYCLE','G5_ASSURANCE','MAINNET_FORK','DEPLOYMENT_PLAN','SEPOLIA'}
GATE_REQUIREMENTS={
 'G1_AUTHORITY':{'fork_topology_deployed','wallet_b_final_authority','wallet_a_zero_permanent_authority','negative_authority_paths_revert'},
 'G2_OVERRIDES':{'typed_owner_resolvers_exercised','replay_duplicate_rejected','financial_override_events_reconciled','arbitrary_call_backdoors_absent'},
 'G3_ACCOUNTING':{'canonical_agialpha_used_on_fork','asset_holder_reconciliation','malicious_token_suite_executed','cap_breaches_revert'},
 'G4_LIFECYCLE':{'selector_classification_complete','phase_transitions_exercised','shutdown_blocks_unresolved_liabilities','terminal_shutdown_after_discharge'},
 'G5_ASSURANCE':{'invariants_executed_1000000_actions_32_seeds','secondary_stateful_engine_pass','differential_traces_match','critical_mutants_killed','independent_bytecode_builds_match','security_docket_complete'},
}
FALLBACK_DIRS=[ROOT/'.private/mainnet-predeploy',ROOT/'.private/mainnet-deployment',ROOT/'.private/mainnet-readiness',ROOT/'.private/evidence/mainnet-predeploy']
PATH_VARS={'GOALOS_RELEASE_IDENTITY_EVIDENCE':'RELEASE_IDENTITY','GOALOS_G1_EVIDENCE_PATH':'G1_AUTHORITY','GOALOS_G2_EVIDENCE_PATH':'G2_OVERRIDES','GOALOS_G3_EVIDENCE_PATH':'G3_ACCOUNTING','GOALOS_G4_EVIDENCE_PATH':'G4_LIFECYCLE','GOALOS_G5_EVIDENCE_PATH':'G5_ASSURANCE','GOALOS_MAINNET_FORK_EVIDENCE_PATH':'MAINNET_FORK','GOALOS_MAINNET_FORK_RAW_RECEIPTS_PATH':'MAINNET_FORK_LOCAL_RECEIPT','GOALOS_MAINNET_FORK_AUTHORITY_READBACK_PATH':'G1_AUTHORITY','GOALOS_MAINNET_FORK_OVERRIDE_EVIDENCE_PATH':'G2_OVERRIDES','GOALOS_MAINNET_FORK_ACCOUNTING_EVIDENCE_PATH':'G3_ACCOUNTING','GOALOS_MAINNET_FORK_LIFECYCLE_EVIDENCE_PATH':'G4_LIFECYCLE','GOALOS_DEPLOYMENT_PLAN_PRIVATE_PATH':'DEPLOYMENT_PLAN','GOALOS_DEPLOYMENT_PLAN_PUBLIC_PATH':'DEPLOYMENT_PLAN','GOALOS_DEPLOYMENT_PLAN_APPROVAL_PATH':'DEPLOYMENT_PLAN_APPROVAL','GOALOS_AUTHORITY_POLICY_PATH':'AUTHORITY_POLICY','GOALOS_OWNER_PROOF_PATH':'OWNER_PROOF','GOALOS_SEPOLIA_EVIDENCE_INDEX':'SEPOLIA','GOALOS_INVARIANT_EVIDENCE_PATH':'G5_ASSURANCE','GOALOS_MUTATION_EVIDENCE_PATH':'G5_ASSURANCE','GOALOS_REPRODUCIBLE_BUILD_EVIDENCE_PATH':'G5_ASSURANCE','GOALOS_SECURITY_DOCKET_PATH':'G5_ASSURANCE'}

def git(args):
 try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return 'UNKNOWN'
def current_release_id(): return git(['rev-parse','HEAD'])
def sha_path(p:pathlib.Path):
 h=hashlib.sha256(); h.update(p.read_bytes()); return '0x'+h.hexdigest()
def hobj(o): return '0x'+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def is_hex_bytes(value, length):
 return isinstance(value,str) and value.startswith('0x') and len(value)==2+length*2 and all(c in '0123456789abcdefABCDEF' for c in value[2:])
def read(p):
 try: return json.loads(pathlib.Path(p).read_text())
 except Exception as e: return {'_parseError':str(e)}
def write(p,o): pathlib.Path(p).parent.mkdir(parents=True,exist_ok=True); pathlib.Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def resolve(p):
 q=pathlib.Path(p)
 return q if q.is_absolute() else ROOT/q
def is_tracked(p):
 try: return subprocess.call(['git','ls-files','--error-unmatch',str(p.relative_to(ROOT))],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)==0
 except Exception: return False

def infer_type(data):
 typ=data.get('type') or data.get('evidenceType') or data.get('protectedType')
 if typ in REQ_TYPES: return typ
 gate=data.get('gate')
 if gate in {'G1','G2','G3','G4','G5'}: return {'G1':'G1_AUTHORITY','G2':'G2_OVERRIDES','G3':'G3_ACCOUNTING','G4':'G4_LIFECYCLE','G5':'G5_ASSURANCE'}[gate]
 obs=data.get('observed',{}) if isinstance(data.get('observed'),dict) else {}
 if data.get('executionMode')=='MAINNET_FORK': return 'MAINNET_FORK'
 if data.get('network')=='sepolia' or data.get('chainId')==11155111 or data.get('verifiedContracts') is not None: return 'SEPOLIA'
 if data.get('orderedTransactions') and data.get('startingNonce') is not None: return 'DEPLOYMENT_PLAN'
 if obs.get('walletAZeroAuthority') is True or obs.get('walletBPermanentAuthority') is True: return 'G1_AUTHORITY'
 if 'typedOverrideCoverage' in obs: return 'G2_OVERRIDES'
 if 'omittedAccountingComponents' in obs: return 'G3_ACCOUNTING'
 if 'unclassifiedSelectors' in obs: return 'G4_LIFECYCLE'
 if 'invariantExecutedActions' in obs or 'mutationSurvived' in obs: return 'G5_ASSURANCE'
 return None

def discover():
 items=[]; root_env=os.environ.get('GOALOS_PROTECTED_EVIDENCE_ROOT')
 roots=[]
 if root_env:
  r=resolve(root_env); roots.append(('GOALOS_PROTECTED_EVIDENCE_ROOT',r))
 for d in FALLBACK_DIRS: roots.append((str(d.relative_to(ROOT)),d))
 idx_env=os.environ.get('GOALOS_PROTECTED_EVIDENCE_INDEX')
 if idx_env: items.append(('GOALOS_PROTECTED_EVIDENCE_INDEX',resolve(idx_env),'INDEX'))
 for name,typ in PATH_VARS.items():
  if os.environ.get(name): items.append((name,resolve(os.environ[name]),typ))
 for label,r in roots:
  idx=r/'protected-evidence-index.json'
  if idx.exists(): items.append((label+'/protected-evidence-index.json',idx,'INDEX'))
  if r.is_dir():
   for p in sorted(r.rglob('*.json')):
    if p.name=='protected-evidence-index.json': continue
    typ=infer_type(read(p))
    if typ in REQ_TYPES: items.append((label+'/'+str(p.relative_to(r)),p,typ))
 return roots,items

def doctor():
 roots,items=discover(); rows=[]
 for label,path in roots:
  rows.append({'name':label,'kind':'directory','status':'PRESENT' if path.is_dir() else 'MISSING','trackedByGit':is_tracked(path) if path.exists() else False})
 for label,path,typ in items:
  exists=path.exists(); st=path.stat() if exists else None
  rows.append({'name':label,'type':typ,'status':'PRESENT' if exists else 'MISSING','fileType':'file' if exists and path.is_file() else None,'bytes':st.st_size if st else None,'permissions':oct(stat.S_IMODE(st.st_mode)) if st else None,'sha256Prefix':sha_path(path)[:18] if exists and path.is_file() else None,'trackedByGit':is_tracked(path) if exists else False,'schemaResult':'UNKNOWN' if not exists or not path.is_file() else ('PASS' if not read(path).get('_parseError') else 'FAIL'),'releaseIdResult':'UNKNOWN' if not exists or not path.is_file() else ('PASS' if (read(path).get('releaseId') or read(path).get('gitCommit') or current_release_id())==current_release_id() else 'MISMATCH')})
 ok=any(r.get('type')=='INDEX' and r['status']=='PRESENT' for r in rows) or any(r.get('type') in REQ_TYPES and r['status']=='PRESENT' for r in rows)
 out={'schemaVersion':'1.0','status':'PRESENT' if ok else 'MISSING','releaseId':current_release_id(),'items':rows}
 print(json.dumps(out,indent=2)); return 0 if ok else 2

def load_or_create_index(write_index=False):
 roots,items=discover(); idx_items=[x for x in items if x[2]=='INDEX' and x[1].exists()]
 if idx_items:
  path=idx_items[0][1]; idx=read(path); return path,idx
 entries=[]; base=None
 for label,path,typ in items:
  if typ in REQ_TYPES and path.exists():
   base=base or path.parent
   entries.append({'type':typ,'path':str(path),'sha256':sha_path(path),'schemaVersion':read(path).get('schemaVersion'),'releaseId':read(path).get('releaseId') or read(path).get('gitCommit'),'publicDisclosure':'COMMITMENT_ONLY'})
 # De-duplicate by required type, preferring explicit environment paths before recursive fallback files.
 seen=set(); dedup=[]
 for e in entries:
  if e['type'] not in seen:
   dedup.append(e); seen.add(e['type'])
 entries=dedup
 if not entries: return None,{'_errors':['No protected evidence index or explicit evidence paths found']}
 base=base or next((r for _,r in roots if r.exists()),None)
 idx={'schemaVersion':'1.0','releaseId':current_release_id(),'gitCommit':current_release_id(),'chainId':1,'walletA':WA,'walletB':WB,'canonicalAgialpha':AGI,'entries':entries}
 idx['indexSha256']=hobj({k:v for k,v in idx.items() if k!='indexSha256'})
 path=(base or ROOT/'.private/mainnet-predeploy')/'protected-evidence-index.json'
 if write_index: write(path,idx)
 return path,idx

def validate_entry(entry, idx):
 errs=[]; typ=entry.get('type'); p=resolve(entry.get('path',''))
 if typ not in REQ_TYPES and typ not in {'SEPOLIA','OWNER_PROOF','AUTHORITY_POLICY','DEPLOYMENT_PLAN_APPROVAL','RELEASE_IDENTITY','MAINNET_FORK_LOCAL_RECEIPT'}: errs.append(f'unknown entry type {typ}')
 if not p.exists(): return [f'{typ}: missing file {entry.get("path")}'], None
 actual=sha_path(p)
 if entry.get('sha256')!=actual: errs.append(f'{typ}: sha256 mismatch {entry.get("sha256")} != {actual}')
 data=read(p)
 if data.get('fixtureOnly') or data.get('notReleaseEvidence'): errs.append(f'{typ}: fixture evidence rejected')
 if typ in REQ_TYPES and data.get('mainnetBroadcastOccurred') is not False: errs.append(f'{typ}: mainnetBroadcastOccurred must be false')
 rid=data.get('releaseId') or data.get('gitCommit') or entry.get('releaseId')
 if rid not in {idx.get('releaseId'), idx.get('gitCommit'), current_release_id()}: errs.append(f'{typ}: releaseId mismatch')
 if typ.startswith('G'):
  if data.get('generatedBy') in {None,'','fixture-tool','manual','unknown'}: errs.append(f'{typ}: generatedBy is not an allowlisted producer')
  if not isinstance(data.get('toolVersions'),dict) or not data.get('toolVersions'): errs.append(f'{typ}: missing toolVersions')
  if not data.get('executedAt') and not data.get('finishedAt'): errs.append(f'{typ}: missing execution timestamp')
  if data.get('releaseId') in {None,'','UNKNOWN'}: errs.append(f'{typ}: invalid releaseId')
  if data.get('status')!='PASS': errs.append(f'{typ}: status is not PASS')
  reqs=data.get('requirements') or data.get('requirementResults') or []
  if not reqs: errs.append(f'{typ}: missing requirements')
  expected=GATE_REQUIREMENTS.get(typ,set())
  seen=set()
  for r in reqs:
   rid=r.get('id')
   seen.add(rid)
   if rid not in expected: errs.append(f'{typ}: unknown requirement {rid}')
   if r.get('releaseId') not in {data.get('releaseId'), idx.get('releaseId'), idx.get('gitCommit')}: errs.append(f'{typ}: requirement {rid} releaseId mismatch')
   if r.get('status')!='PASS': errs.append(f'{typ}: requirement {rid} not PASS')
   if not r.get('evidence') or not r.get('evidenceHashes') or not r.get('rawEvidenceCommitments'): errs.append(f'{typ}: requirement {rid} lacks independent evidence, hashes, or raw commitments')
   if r.get('generatedBy') in {None,'','fixture-tool','manual','unknown'}: errs.append(f'{typ}: requirement {rid} missing real producer')
   if not isinstance(r.get('toolVersions'),dict) or not r.get('toolVersions'): errs.append(f'{typ}: requirement {rid} missing toolVersions')
   if not r.get('executedAt') and not r.get('finishedAt'): errs.append(f'{typ}: requirement {rid} missing execution timestamp')
   if r.get('failures') not in ([],None) or r.get('blockers') not in ([],None): errs.append(f'{typ}: requirement {rid} has failures/blockers')
  missing=expected-seen
  for rid in sorted(missing): errs.append(f'{typ}: missing requirement {rid}')
  obs=data.get('observed',{})
  if typ=='G1_AUTHORITY' and (obs.get('walletAZeroAuthority') is not True or obs.get('walletBPermanentAuthority') is not True): errs.append(f'{typ}: authority predicates missing')
  if typ=='G5_ASSURANCE':
   if int(obs.get('invariantExecutedActions',0))<1000000: errs.append(f'{typ}: invariant actions below threshold')
   if int(obs.get('deterministicSeedCount',0))<32: errs.append(f'{typ}: fewer than 32 seeds')
   if int(obs.get('mutationSurvived',0))!=0: errs.append(f'{typ}: surviving mutants present')
 if typ=='MAINNET_FORK':
  for k in ['executionMode','upstreamChainId','localChainId','forkBlockNumber','forkBlockHash','forkBlockTimestamp','primaryProviderCommitment','secondaryProviderCommitment','canonicalAgialpha','upstreamCanonicalAgialphaCodeHash','localForkCanonicalAgialphaCodeHash','deploymentPlanHash','deployedTopologyCount','transactionReceiptCount','runtimeBytecodeRoot']:
   if data.get(k) in [None,'',[],{}]: errs.append(f'{typ}: missing {k}')
  for k in ['forkBlockHash','upstreamCanonicalAgialphaCodeHash','localForkCanonicalAgialphaCodeHash','runtimeBytecodeRoot']:
   if data.get(k) and not is_hex_bytes(data.get(k),32): errs.append(f'{typ}: {k} must be bytes32')
  if data.get('providerAgreement') is not True: errs.append(f'{typ}: providerAgreement must be true')
  if data.get('executionMode')!='MAINNET_FORK' or data.get('upstreamChainId')!=1: errs.append(f'{typ}: not a valid Mainnet fork')
  if str(data.get('canonicalAgialpha','')).lower()!=AGI.lower(): errs.append(f'{typ}: wrong canonical AGIALPHA')
  if int(data.get('transactionReceiptCount') or 0)<=0: errs.append(f'{typ}: empty receipt list')
 if typ=='DEPLOYMENT_PLAN':
  for k in ['chainId','canonicalAgialpha','walletA','walletB','startingNonce','orderedTransactions','maximumCumulativeCost','planHash','expiresAt']:
   if data.get(k) in [None,'',[],{}]: errs.append(f'{typ}: missing {k}')
  for i,tx in enumerate(data.get('orderedTransactions') or []):
   if tx.get('commitment')=='protected' and 'count' in tx: errs.append(f'{typ}: aggregate-only transaction {i} rejected')
   for k in ['expectedNonce','expectedCreateAddress','fullyQualifiedName','artifactHash','constructorCommitment','initcodeHash','expectedRuntimeBytecodeHash','transactionValue','gasLimit','maxFeePerGas','maxPriorityFeePerGas','maximumTransactionCost']:
    if tx.get(k) in [None,'',[],{}]: errs.append(f'{typ}: transaction {i} missing {k}')
  if data.get('chainId')!=1: errs.append(f'{typ}: wrong chainId')
  if str(data.get('walletA','')).lower()!=WA.lower() or str(data.get('walletB','')).lower()!=WB.lower(): errs.append(f'{typ}: wrong wallet')
  if str(data.get('canonicalAgialpha','')).lower()!=AGI.lower(): errs.append(f'{typ}: wrong token')
 if typ=='SEPOLIA':
  if data.get('status')!='PASS': errs.append(f'{typ}: status is not PASS')
  if data.get('chainId') not in {11155111, '11155111'}: errs.append(f'{typ}: wrong chainId')
  total=int(data.get('totalContracts') or data.get('total') or 0)
  verified=int(data.get('verifiedContracts') or data.get('verified') or 0)
  failed=int(data.get('failedContracts') or data.get('failed') or 0)
  if total <= 0 or verified != total or failed != 0: errs.append(f'{typ}: Sepolia verification counts are not complete')
 return errs,data

def validate(write_report=True):
 path,idx=load_or_create_index(False); errs=[]; data_by_type={}
 if idx.get('_errors'): errs+=idx['_errors']
 if idx.get('schemaVersion')!='1.0': errs.append('INDEX: schemaVersion must be 1.0')
 if idx.get('chainId')!=1: errs.append('INDEX: chainId must be 1')
 if str(idx.get('walletA','')).lower()!=WA.lower(): errs.append('INDEX: walletA mismatch')
 if str(idx.get('walletB','')).lower()!=WB.lower(): errs.append('INDEX: walletB mismatch')
 if str(idx.get('canonicalAgialpha','')).lower()!=AGI.lower(): errs.append('INDEX: canonicalAgialpha mismatch')
 if idx.get('gitCommit') not in {current_release_id(), None}: errs.append('INDEX: gitCommit mismatch')
 types=set()
 for e in idx.get('entries') or []:
  e_errs,d=validate_entry(e,idx); errs+=e_errs; types.add(e.get('type'))
  if d is not None: data_by_type[e.get('type')]=d
 missing=REQ_TYPES-types
 for m in sorted(missing): errs.append(f'INDEX: missing required entry {m}')
 status='PASS' if not errs else 'FAIL'
 summary={}
 fork=data_by_type.get('MAINNET_FORK') or {}; plan=data_by_type.get('DEPLOYMENT_PLAN') or {}; g5=data_by_type.get('G5_ASSURANCE') or {}
 sepolia=data_by_type.get('SEPOLIA') or {}
 if fork: summary['fork']={k:fork.get(k) for k in ['forkBlockNumber','forkBlockHash','forkBlockTimestamp','deployedTopologyCount','transactionReceiptCount','deploymentPlanHash','runtimeBytecodeRoot']}
 if plan: summary['plan']={k:plan.get(k) for k in ['planHash','startingNonce','expiresAt','maximumCumulativeCost']}; summary['plan']['transactionCount']=len(plan.get('orderedTransactions') or [])
 if g5: summary['assurance']=g5.get('observed',{})
 if sepolia: summary['sepolia']={k:sepolia.get(k) for k in ['chainId','totalContracts','verifiedContracts','failedContracts']}
 report={'schemaVersion':'1.0','status':status,'releaseId':idx.get('releaseId'),'gitCommit':idx.get('gitCommit'),'indexPath':str(path) if path else None,'indexSha256':sha_path(path) if path and path.exists() else idx.get('indexSha256'),'errors':errs,'entryTypes':sorted(types),'summary':summary,'mainnetBroadcastOccurred':False}
 if write_report: write(QA/'protected-evidence-validation.json',report)
 print(json.dumps(report,indent=2)); return 0 if status=='PASS' else 2

def index_cmd():
 path,idx=load_or_create_index(True); out={'schemaVersion':'1.0','status':'PASS' if path and not idx.get('_errors') else 'FAIL','indexPath':str(path) if path else None,'indexSha256':sha_path(path) if path and path.exists() else None,'errors':idx.get('_errors',[])}
 print(json.dumps(out,indent=2)); return 0 if out['status']=='PASS' else 2

def import_cmd():
 rc=validate(True)
 report=read(QA/'protected-evidence-validation.json')
 path,idx=load_or_create_index(False)
 commitments=[]
 for e in idx.get('entries') or []:
  p=resolve(e.get('path',''))
  if p.exists(): commitments.append({'type':e.get('type'),'sha256':sha_path(p),'schemaVersion':read(p).get('schemaVersion'),'releaseId':read(p).get('releaseId') or e.get('releaseId'),'publicDisclosure':e.get('publicDisclosure','COMMITMENT_ONLY')})
 out={'schemaVersion':'1.0','status':report.get('status'),'releaseId':idx.get('releaseId'),'gitCommit':idx.get('gitCommit'),'indexSha256':report.get('indexSha256'),'commitments':commitments,'mainnetBroadcastOccurred':False}
 write(QA/'protected-evidence-commitments.json',out)
 # Write public sanitized package summaries with commitments only.
 name_map={'G1_AUTHORITY':'gate-1-authority.public.json','G2_OVERRIDES':'gate-2-overrides.public.json','G3_ACCOUNTING':'gate-3-accounting.public.json','G4_LIFECYCLE':'gate-4-lifecycle.public.json','G5_ASSURANCE':'gate-5-assurance.public.json','MAINNET_FORK':'mainnet-fork.public.json','SEPOLIA':'sepolia.public.json'}
 for c in commitments:
  if c['type'] in name_map: write(QA/name_map[c['type']],{'schemaVersion':'1.0','status':report.get('status'),'evidenceType':c['type'],'protectedFileHash':c['sha256'],'releaseId':c.get('releaseId'),'schemaVersionOfEvidence':c.get('schemaVersion'),'producerMetadata':{'source':'validated protected evidence'},'safeSummary':{'rawProtectedEvidence':'not disclosed','disclosure':c.get('publicDisclosure')},'validationResult':report.get('status'),'commitment':c,'mainnetBroadcastOccurred':False})
 print(json.dumps(out,indent=2)); return rc

def status_cmd():
 rep=read(QA/'protected-evidence-validation.json')
 if not rep: return validate(True)
 print(json.dumps(rep,indent=2)); return 0 if rep.get('status')=='PASS' else 2

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['doctor','index','validate','import','status']); a=ap.parse_args()
 return {'doctor':doctor,'index':index_cmd,'validate':validate,'import':import_cmd,'status':status_cmd}[a.cmd]()
if __name__=='__main__': raise SystemExit(main())
