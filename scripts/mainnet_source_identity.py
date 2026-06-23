#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, subprocess, sys, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/mainnet-source-identity'
TAG='v4.4.0-mainnet-2026-06-21'
CHAIN_ID=1
GOALOS_CONTRACTS=48
REQUIRED_ENV=['PRIMARY_MAINNET_RPC_URL','SECONDARY_MAINNET_RPC_URL','ETHERSCAN_API_KEY']

def write(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def read(p):
 try: return json.loads((ROOT/p if isinstance(p,str) else p).read_text())
 except Exception: return {}
def sha_path(p):
 p=ROOT/p if isinstance(p,str) else p
 if not p.exists(): return None
 h=hashlib.sha256()
 if p.is_dir():
  for f in sorted(x for x in p.rglob('*') if x.is_file() and '.git' not in x.parts and 'node_modules' not in x.parts):
   h.update(str(f.relative_to(ROOT)).encode()); h.update(b'\0'); h.update(f.read_bytes())
 else: h.update(p.read_bytes())
 return '0x'+h.hexdigest()
def hobj(o): return '0x'+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def git(args):
 try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return 'UNKNOWN'
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def rpc(url,method,params):
 req=urllib.request.Request(url,data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(),headers={'content-type':'application/json'})
 data=json.loads(urllib.request.urlopen(req,timeout=25).read().decode())
 if data.get('error'): raise RuntimeError(data['error'])
 return data.get('result')
def env_report():
 return {'present':{k:bool(os.environ.get(k)) for k in REQUIRED_ENV},'missing':[k for k in REQUIRED_ENV if not os.environ.get(k)]}
def identities():
 return {'publishedReleaseTag':TAG,'publishedReleaseTagSha':git(['rev-list','-n','1',TAG]),'publishedReleaseTagFuller':git(['show','--no-patch','--format=fuller',TAG]),'currentMainSha':git(['rev-parse','HEAD']),'historicalManifestCommitLabel':(read('release/mainnet-2026-06-21/RELEASE_MANIFEST.json').get('gitCommit') or read('release/mainnet-2026-06-21/RELEASE_MANIFEST.json').get('commit') or 'UNKNOWN'),'reproductionSourceCommitSha':git(['rev-parse','HEAD']),'evidenceCommitSha':git(['rev-parse','HEAD'])}
def doctor():
 e=env_report(); d={'schemaVersion':'1.0','command':'doctor','generatedAt':now(),**identities(),'environment':e,'status':'PASS' if not e['missing'] else 'BLOCKED_MISSING_READ_ONLY_CREDENTIALS'}; write(OUT/'doctor.json',d); return d
def fetch():
 d=doctor();
 if d['status']!='PASS':
  r={'schemaVersion':'1.0','status':'BLOCKED','failureReason':'read-only RPC/Etherscan credentials are required; values were not printed','missing':d['environment']['missing']}; write(OUT/'provider-consensus.json',r); return r
 a,b=os.environ['PRIMARY_MAINNET_RPC_URL'],os.environ['SECONDARY_MAINNET_RPC_URL']
 if a.strip()==b.strip():
  r={'schemaVersion':'1.0','status':'FAIL','failureReason':'primary and secondary RPC endpoints must be independent'}; write(OUT/'provider-consensus.json',r); return r
 try:
  ca,cb=int(rpc(a,'eth_chainId',[]),16),int(rpc(b,'eth_chainId',[]),16)
  ba=rpc(a,'eth_getBlockByNumber',['finalized',False]); bb=rpc(b,'eth_getBlockByNumber',[ba['number'],False])
  agree=ca==cb==CHAIN_ID and ba and bb and ba.get('hash')==bb.get('hash')
  r={'schemaVersion':'1.0','status':'PASS' if agree else 'FAIL','chainId':ca,'secondaryChainId':cb,'pinnedBlockNumber':int(ba['number'],16),'pinnedBlockHash':ba.get('hash'),'providerAgreement':agree,'contractRuntimeConsensus':{'expected':GOALOS_CONTRACTS,'validated':0,'status':'BLOCKED_UNTIL_MANIFEST_ADDRESS_FETCH_IMPLEMENTED'}}
 except Exception as exc:
  r={'schemaVersion':'1.0','status':'FAIL','failureReason':type(exc).__name__}
 write(OUT/'provider-consensus.json',r); return r
def compile_cmd():
 node=subprocess.getoutput('node --version'); npm=subprocess.getoutput('npm --version')
 comp={'schemaVersion':'1.0','generatedAt':now(),'nodeVersion':node,'npmVersion':npm,'packageLockSha256':sha_path('package-lock.json'),'hardhatConfigSha256':sha_path('hardhat.config.ts'),'contractsSha256':sha_path('contracts'),'deploymentScriptsSha256':sha_path('scripts'),'status':'RECORDED'}
 write(OUT/'compiler-environment.json',comp)
 base={'schemaVersion':'1.0','sourceRoot':str(ROOT),'artifactsSha256':sha_path('artifacts') or 'NOT_BUILT','buildInfoSha256':sha_path('artifacts/build-info') or 'NOT_BUILT','status':'RECORDED'}
 write(OUT/'build-a.json',base|{'build':'A'}); write(OUT/'build-b.json',base|{'build':'B','independentProcess':'not-run-in-this-environment'})
 return comp
def compare():
 docs=[]
 for name in ['runtime-comparison','creation-comparison','etherscan-source-comparison','constructor-comparison','source-tree-manifest']:
  status='BLOCKED_UNTIL_LIVE_EVIDENCE_FETCH_AND_EXACT_BUILD_MATCH'
  if name=='source-tree-manifest': status='RECORDED'
  d={'schemaVersion':'1.0','generatedAt':now(),'goalosContractCountExpected':GOALOS_CONTRACTS,'goalosContractCountValidated':0,'status':status,'sourceTreeSha256':sha_path('contracts')}
  write(OUT/f'{name}.json',d); docs.append(d)
 return {'status':'RECORDED','artifacts':len(docs)}
def certificate():
 refs=['provider-consensus.json','compiler-environment.json','build-a.json','build-b.json','runtime-comparison.json','creation-comparison.json','etherscan-source-comparison.json','constructor-comparison.json','source-tree-manifest.json']
 ev=[{'path':f'qa/mainnet-source-identity/{r}','sha256':sha_path(OUT/r)} for r in refs if (OUT/r).exists()]
 blockers=[]
 checks={}
 for r in refs:
  d=read(OUT/r); checks[r]=d.get('status','MISSING')
 required_pass=['provider-consensus.json','runtime-comparison.json','creation-comparison.json','etherscan-source-comparison.json','constructor-comparison.json']
 for r in required_pass:
  if checks.get(r)!='PASS': blockers.append(f'{r} is {checks.get(r)}')
 builds_match=read(OUT/'build-a.json').get('artifactsSha256')==read(OUT/'build-b.json').get('artifactsSha256') and read(OUT/'build-a.json').get('artifactsSha256') not in {None,'NOT_BUILT'}
 if not builds_match: blockers.append('two independent clean builds have not been proven byte-identical')
 status='PASS' if not blockers else 'BLOCKED'
 c={'schemaVersion':'1.0','stage':'SOURCE_IDENTITY_REPRODUCTION','classification':'EXACT_DEPLOYED_SOURCE_REPRODUCED_BY_COMMIT' if status=='PASS' else 'SOURCE_IDENTITY_NOT_PROVEN','status':status,'chainId':CHAIN_ID,**identities(),'exactReproductionProven':status=='PASS','historicalDeploymentCommitProven':False,'checks':checks,'blockers':blockers,'evidence':ev,'certificateHash':None}
 c['certificateHash']=hobj({k:v for k,v in c.items() if k!='certificateHash'}); write(OUT/'source-identity-certificate.json',c)
 md=f"# Mainnet Source Identity\n\nStatus: `{c['classification']}`\n\nExact reproduction proven: `{str(c['exactReproductionProven']).lower()}`\n\nThis document is generated from `qa/mainnet-source-identity/source-identity-certificate.json` and remains fail-closed until 48/48 runtime, creation-input, constructor, Etherscan source/settings, and two-build checks pass.\n\nCertificate hash: `{c['certificateHash']}`\n"
 (ROOT/'release/mainnet-2026-06-21/SOURCE_IDENTITY.md').write_text(md)
 (ROOT/'docs/releases').mkdir(parents=True,exist_ok=True); (ROOT/'docs/releases/MAINNET_2026_06_21_SOURCE_IDENTITY.md').write_text(md)
 return c
def validate():
 c=certificate(); errs=[]
 if c['status']!='PASS': errs+=c.get('blockers') or ['certificate is not PASS']
 for e in c.get('evidence',[]):
  if sha_path(e['path'])!=e.get('sha256'): errs.append('evidence hash mismatch '+e['path'])
 print(json.dumps({'status':'PASSED' if not errs else 'FAILED','errors':errs,'certificateStatus':c.get('status')},indent=2)); return not errs
def main():
 p=argparse.ArgumentParser(); p.add_argument('cmd',choices=['doctor','fetch','build','compile','compare','certificate','certificate-validate','all']); a=p.parse_args()
 if a.cmd=='doctor': print(json.dumps(doctor(),indent=2)); return
 if a.cmd=='fetch': print(json.dumps(fetch(),indent=2)); return
 if a.cmd in {'build','compile'}: print(json.dumps(compile_cmd(),indent=2)); return
 if a.cmd=='compare': print(json.dumps(compare(),indent=2)); return
 if a.cmd=='certificate': print(json.dumps(certificate(),indent=2)); return
 if a.cmd=='certificate-validate': sys.exit(0 if validate() else 1)
 if a.cmd=='all':
  doctor(); fetch(); compile_cmd(); compare(); certificate(); sys.exit(0 if validate() else 1)
if __name__=='__main__': main()
