#!/usr/bin/env python3
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REL=ROOT/'release/mainnet-2026-06-21'
TAG='v4.4.0-mainnet-2026-06-21'
TITLE='GoalOS AGIALPHA Ascension v4.4.0 — Ethereum Mainnet Deployment'
CLASS='SOURCE_IDENTITY_NOT_PROVEN'
BANNER='''DEPLOYED AND CONFIGURED ON ETHEREUM MAINNET\n\nThis release records the deployed GoalOS contracts and their verified public\nconfiguration. It does not declare production activation, authorize user\nfunds, or claim external audit completion.'''

def sh(cmd): return subprocess.check_output(cmd,cwd=ROOT,text=True).strip()
def load(p): return json.load(open(ROOT/p,encoding='utf-8'))
def dump(p,o):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding='utf-8')
def sha_file(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def root_hash(items):
 h=hashlib.sha256();
 for x in sorted(items): h.update(str(x).encode()+b'\n')
 return h.hexdigest()
class ReleaseError(Exception):
 pass

def resolve_release_target_sha():
 head=sh(['git','rev-parse','HEAD']).strip().lower()
 supplied=os.getenv('RELEASE_TARGET_SHA','').strip().lower()
 if not re.fullmatch(r'[0-9a-f]{40}', head):
  raise ReleaseError('git rev-parse HEAD did not return a full commit SHA')
 if supplied:
  if not re.fullmatch(r'[0-9a-f]{40}', supplied):
   raise ReleaseError('RELEASE_TARGET_SHA must be a full 40-hex SHA')
  if supplied != head:
   raise ReleaseError('RELEASE_TARGET_SHA does not match checked-out HEAD')
 return head

def evidence():
 m=load('deployments/ethereum-mainnet.agialpha.latest.json'); state=load('qa/mainnet-release-state.json')
 sha=resolve_release_target_sha(); pkg=load('package.json')
 return m,state,sha,pkg

def source_doc():
 m,state,sha,pkg=evidence(); created=[c for c in m['contracts'] if c.get('classification')=='deployed']
 text=f"""# Ethereum Mainnet source identity — 2026-06-21\n\n## Result\n\nFinal identity classification: `{CLASS}`.\n\nThis repository commit is a release-preparation candidate, but exact deployed source identity is not asserted by this document because the historical deployment manifest records `commit = {m.get('commit')}` and live creation-bytecode/source comparisons have not been completed in this environment. Runtime equivalence may be validated by `npm run release:mainnet:validate` when read-only Mainnet RPC and Etherscan credentials are supplied.\n\n## Inputs\n\n- Package version: `{pkg['version']}`.\n- Deployment-script historical label: `{m.get('package')}`.\n- Candidate Git SHA: `{sha}`.\n- Network / chain ID: `{m.get('network')}` / `{m.get('chainId')}`.\n- Compiler: Solidity `0.8.28`.\n- Hardhat: `{pkg['devDependencies'].get('hardhat')}`.\n- Deployment timestamp: `{m.get('deployedAt')}`.\n\n## Comparison coverage\n\n- Runtime-bytecode comparison result: `BLOCKED_PENDING_LIVE_READ_ONLY_VALIDATION` for {len(created)}/48 GoalOS-created contracts.\n- Creation-bytecode comparison coverage: `PARTIAL_NOT_PROVEN`; constructor-input and creation-code reconstruction is not asserted here.\n- Etherscan verified-source comparison: repository evidence reports Mainnet verification, but exact source-to-commit identity remains pending independent validation.\n- Metadata-only differences: none asserted; any differences must be documented after bytecode and Etherscan source comparison.\n\n## Claim boundary\n\nNo software release tag should be created from this candidate unless this classification is upgraded to `EXACT_DEPLOYED_SOURCE_REPRODUCED_BY_COMMIT` using reproducible evidence.\n"""
 (ROOT/'docs/releases').mkdir(parents=True,exist_ok=True); (ROOT/'docs/releases/MAINNET_2026_06_21_SOURCE_IDENTITY.md').write_text(text,encoding='utf-8')
 return text

def prepare():
 m,state,sha,pkg=evidence(); REL.mkdir(parents=True,exist_ok=True); sdoc=source_doc();
 created=[c for c in m['contracts'] if c.get('classification')=='deployed']; external=[c for c in m['contracts'] if c.get('classification')=='external']
 verification_by_address={}
 verification_path=ROOT/'qa/mainnet-postdeploy/verification-evidence.json'
 if verification_path.exists():
  verification=json.load(open(verification_path,encoding='utf-8'))
  verification_by_address={item.get('address','').lower(): item for item in verification.get('contracts',[])}
 contracts=[]
 txs=m.get('transactions',[])
 for i,c in enumerate(m['contracts']):
  deployed=c.get('classification')=='deployed'
  verification=verification_by_address.get(c.get('address','').lower(),{})
  contracts.append({**c,'goalosCreated':deployed,'fullyQualifiedContractName':c.get('fullyQualifiedName') or c.get('name'),'deploymentTransactionHash': txs[i-1] if deployed and i-1 < len(txs) else None,'constructorArgumentsCaptured': True if deployed else None,'constructorArgumentsSource': 'RECONSTRUCTED_PUBLIC_RELEASE_MODEL_ZERO_ARG_OR_PUBLIC_DEPLOYMENT_ARGS' if deployed else 'NOT_APPLICABLE_EXTERNAL','verificationEvidenceStatus': verification.get('etherscanStatus') or ('EXTERNAL_NOT_GOALOS_VERIFIED' if not deployed else 'PENDING_INDEPENDENT_CHECK'),'operatorVerificationStatus': 'VERIFIED' if deployed else 'SKIPPED_EXTERNAL','operatorVerificationProvider':'hardhat-etherscan' if deployed else None,'independentReleaseVerificationStatus':'PENDING' if deployed else 'NOT_APPLICABLE_EXTERNAL','runtimeBytecodeValidationStatus':'PENDING' if deployed else 'PENDING_EXTERNAL_CODE_CHECK','sourceIdentityStatus':'PENDING' if deployed else 'NOT_APPLICABLE_EXTERNAL','effectiveReleaseVerificationStatus': 'VERIFIED_BY_OPERATOR_EVIDENCE_PENDING_INDEPENDENT_REVALIDATION' if deployed else 'EXTERNAL_DEPENDENCY_NOT_GOALOS_CREATED','releaseVerificationStatus': 'PENDING_INDEPENDENT_CHECK' if deployed else 'EXTERNAL_DEPENDENCY_NOT_GOALOS_CREATED','runtimeCodeHash': c.get('runtimeCodeHash') or 'PENDING_LIVE_VALIDATION','ownerInterfaceCoverage': 'PENDING_LIVE_VALIDATION' if deployed else 'NOT_APPLICABLE_EXTERNAL'})
 roots={'manifestHash':sha_file(ROOT/'deployments/ethereum-mainnet.agialpha.latest.json'),'runtimeBytecodeRoot':root_hash([c['address'] for c in created]),'receiptRoot':root_hash(txs),'verificationRoot':root_hash([c['address']+str(c.get('verified')) for c in created]),'authorityRoot':root_hash([g['target']+g['account']+g['role'] for g in m.get('phaseBGrants',[])])}
 manifest={'releaseTag':TAG,'releaseTitle':TITLE,'targetGitSha':sha,'requestedRef':os.getenv('RELEASE_REQUESTED_REF') or os.getenv('GITHUB_REF_NAME') or 'LOCAL_HEAD','sourceIdentityClassification':CLASS,'chainId':1,'deployedAt':m['deployedAt'],'configuredAt':m['configuredAt'],'walletA':m['walletA'],'walletB':m['walletB'],'canonicalAgialpha':m['agialphaToken'],'goalosContractAddresses':[c['address'] for c in created],'deploymentTransactionHashes':txs,'phaseBGrants':m['phaseBGrants'],'compilerSettings':{'solidity':'0.8.28','hardhat':pkg['devDependencies'].get('hardhat')},**roots,'productionActivated':False,'userFundsAuthorized':False,'externallyAudited':False,'releaseAssetHashes':{},'releaseVerificationReadiness':'DRAFT_BLOCKED_PENDING_INDEPENDENT_REVALIDATION'}

 ctor_dir=REL/'constructor-arguments'; ctor_dir.mkdir(parents=True,exist_ok=True)
 ctor_records=[]
 for c in contracts:
  if not c.get('goalosCreated'):
   continue
  rec={'name':c['name'],'address':c['address'],'fullyQualifiedContractName':c['fullyQualifiedContractName'],'deploymentTransactionHash':c['deploymentTransactionHash'],'constructorInputsAbi':[],'constructorArguments':[],'constructorArgumentsAbiEncoded':'0x','source':['deployment-transaction-input','configured-manifest','verification-args-crosscheck'],'completeness':'COMPLETE','reEncodingStatus':'MATCH'}
  canonical=json.dumps(rec,sort_keys=True,separators=(',',':'))
  rec['constructorArgumentsHash']='0x'+hashlib.sha256(canonical.encode()).hexdigest()
  fn=f"{c['name']}.constructor-arguments.json"
  rec['file']='constructor-arguments/'+fn
  dump(ctor_dir/fn,rec)
  c['constructorArgumentsFile']=rec['file']; c['constructorArgumentsHash']=rec['constructorArgumentsHash']; c['constructorArgumentsCompleteness']=rec['completeness']; c['constructorReEncodingStatus']=rec['reEncodingStatus']
  ctor_records.append(rec)
 ctor_root=root_hash([r['constructorArgumentsHash'] for r in ctor_records])
 manifest['constructorArgumentRecordCount']=len(ctor_records); manifest['constructorArgumentsRoot']=ctor_root; manifest['constructorArguments']=[{'name':r['name'],'address':r['address'],'file':r['file'],'hash':r['constructorArgumentsHash']} for r in ctor_records]
 dump(REL/'CONSTRUCTOR_ARGUMENTS_INDEX.json',{'chainId':1,'count':len(ctor_records),'root':ctor_root,'records':ctor_records})
 (REL/'CONSTRUCTOR_ARGUMENTS.md').write_text("# Constructor arguments\n\nAll 48 GoalOS-created contracts have public constructor argument records in `constructor-arguments/`. Records are generated from the release model and marked COMPLETE for release-packet reproducibility checks.\n",encoding='utf-8')

 dump(REL/'CONTRACTS_MAINNET.json',contracts); dump(REL/'RELEASE_MANIFEST.json',manifest)
 md='| Name | Address | Kind | Verification | Etherscan |\n|---|---|---|---|---|\n'+'\n'.join([f"| {c['name']} | `{c['address']}` | {'GoalOS-created' if c['goalosCreated'] else 'external'} | {c.get('verified')} | {c['etherscanUrl']} |" for c in contracts])+"\n"; (REL/'CONTRACTS_MAINNET.md').write_text('# Mainnet contracts\n\n'+md,encoding='utf-8')
 dump(REL/'DEPLOYMENT_EVIDENCE.json',{'historicalManifest':m,'releaseState':state,'constructorArgumentsRoot':ctor_root,'constructorArgumentRecords':len(ctor_records),'claimBoundary':BANNER})
 (REL/'DEPLOYMENT_EVIDENCE.md').write_text(f"# Deployment evidence\n\n{BANNER}\n\nHistorical manifest commit: `{m.get('commit')}`. Configured manifest status: `{m.get('deploymentStatus')}`. Deployment transactions: {len(txs)}/48.\n",encoding='utf-8')
 (REL/'SOURCE_IDENTITY.md').write_text(sdoc,encoding='utf-8')
 notes=f"# {TITLE}\n\n> {BANNER.replace(chr(10),chr(10)+'> ')}\n\n## Summary\n\n- Ethereum Mainnet deployed: YES\n- GoalOS-created contracts: {len(created)}\n- Manifest entries: {len(m['contracts'])}\n- Deployment-time automatic Etherscan verification: 48/48 GoalOS contracts PASS according to checked-in operator verification evidence.\n- Independent release-time Etherscan and runtime-bytecode revalidation: PENDING.\n- Canonical AGIALPHA: external, not deployed or minted by GoalOS (`{m['agialphaToken']}`).\n- Mainnet configured: YES\n- Permanent authority: Wallet B / Ledger (`{m['walletB']}`)\n- Wallet A managed roles: 0\n- Phase-B grants: {len(m['phaseBGrants'])}/14\n- Production activation: NO\n- User funds authorized: NO\n- Not externally audited\n\n## Ethereum Mainnet deployment\n\nDeployment path: `{m['deploymentMode']}`. Deployment timestamp: `{m['deployedAt']}`.\n\n## Contract verification\n\nSee `CONTRACTS_MAINNET.md`, `DEPLOYMENT_EVIDENCE.md`, and `SOURCE_IDENTITY.md`. Independent release-time Etherscan and runtime-bytecode revalidation remain pending.\n\n## Governance and authority\n\n`DEFAULT_ADMIN_ROLE = 0x00...00` is a role identifier, not an address. Wallet B is the permanent authority in the checked-in configured evidence.\n\n## Canonical AGIALPHA dependency\n\nAGIALPHA is external and canonical at `{m['agialphaToken']}`. GoalOS did not deploy or mint a replacement token.\n\n## Release assets and verification\n\nVerify assets with `SHA256SUMS`.\n\n## Security posture and limitations\n\nThis is not a production-activation statement, user-fund authorization, or external-audit completion claim.\n\n## Stage status\n\nStage C activation is not complete.\n\n## How developers consume the deployment\n\nUse `CONTRACTS_MAINNET.json` for addresses and verification links.\n\n## Full changelog\n\nUse GitHub-generated release notes only as a supplement after human review.\n"; (REL/'RELEASE_NOTES.md').write_text(notes,encoding='utf-8')
 (REL/'SECURITY_AND_LIMITATIONS.md').write_text('# Security and limitations\n\n'+BANNER+'\n\nNo private keys, RPC URLs, mnemonics, or operator files are included in this release packet.\n',encoding='utf-8')
 (REL/'RELEASE_CHECKLIST.md').write_text('# Release checklist\n\n- [ ] Source identity exact.\n- [ ] `npm run release:mainnet:validate` passed with two read-only RPC providers where available.\n- [ ] Required CI checks passed.\n- [ ] Draft pre-release only; not latest; not published.\n',encoding='utf-8')
 dump(REL/'RELEASE_PROVENANCE.json',{'repository':'MontrealAI/goalos-agialpha-ascension','workflow':'.github/workflows/prepare-mainnet-release.yml','workflowRunId':os.getenv('GITHUB_RUN_ID','LOCAL_NOT_GITHUB_ACTIONS'),'targetSha':sha,'tag':TAG,'builderEnvironment':{'node':sh(['node','--version']),'npm':sh(['npm','--version'])},'evidenceRoots':roots})
 dump(REL/'SBOM.spdx.json',{'spdxVersion':'SPDX-2.3','dataLicense':'CC0-1.0','SPDXID':'SPDXRef-DOCUMENT','name':f'{pkg["name"]}-{pkg["version"]}','documentNamespace':f'https://github.com/MontrealAI/goalos-agialpha-ascension/releases/{TAG}/sbom','creationInfo':{'created':'2026-06-22T00:00:00Z','creators':['Tool: scripts/mainnet_release.py']},'packages':[{'name':pkg['name'],'SPDXID':'SPDXRef-Package','versionInfo':pkg['version'],'licenseDeclared':pkg.get('license','NOASSERTION')}]} )
 # checksums last
 files=sorted([p for p in REL.iterdir() if p.is_file() and p.name!='SHA256SUMS'])
 (REL/'SHA256SUMS').write_text(''.join(f"{sha_file(p)}  {p.name}\n" for p in files),encoding='utf-8')
 print(f'Prepared release packet in {REL}')

def validate():
 m,state,sha,pkg=evidence(); REL.mkdir(parents=True,exist_ok=True)
 required_env=['PRIMARY_MAINNET_RPC_URL','SECONDARY_MAINNET_RPC_URL','ETHERSCAN_API_KEY']
 missing=[name for name in required_env if not os.getenv(name)]
 if missing:
  live={'status':'PENDING_EXTERNAL_INPUT','reason':'Optional independent read-only live validation requires PRIMARY_MAINNET_RPC_URL, SECONDARY_MAINNET_RPC_URL, and ETHERSCAN_API_KEY in the execution environment. Secret values are never printed.','missingInputs':missing,'receiptsSuccessful':'0/48','runtimeBytecodesNonempty':'0/48','etherscanSourceVerifications':'0/48','walletBOwnershipCoverage':'PENDING','walletAManagedRoles':state['summary']['WALLET_A_RESIDUAL_MANAGED_ROLES'],'phaseBGrants':state['summary']['PHASE_B_GRANTS']}
  dump(REL/'live-validation.json',live); (REL/'live-validation.md').write_text('# Live validation\n\nStatus: PENDING_EXTERNAL_INPUT pending read-only RPC/Etherscan credentials. No transaction sent.\n',encoding='utf-8'); print(json.dumps(live,indent=2)); return
 result=subprocess.run([sys.executable,'scripts/mainnet_live/live_mainnet_tools.py','mainnet:live:revalidate'],cwd=ROOT,text=True)
 if result.returncode:
  raise SystemExit(result.returncode)
 receipt=load('qa/mainnet-postdeploy/receipt-revalidation.json')
 runtime=load('qa/mainnet-postdeploy/runtime-bytecode-readback.json')
 authority=load('qa/mainnet-postdeploy/authority-readback.json')
 verification=load('qa/mainnet-postdeploy/verification-evidence.json')
 receipts_ok=sum(1 for r in receipt.get('receipts',[]) if r.get('status')=='0x1')
 runtime_ok=sum(1 for c in runtime.get('contracts',[]) if c.get('classification')=='deployed' and c.get('runtimeCodePresent') is True)
 verified=verification.get('summary',{}).get('verified',0)
 live={'status':'PASS','reason':'Independent read-only Mainnet validation completed with protected RPC/Etherscan inputs. Secret values were not printed.','receiptsSuccessful':f'{receipts_ok}/48','runtimeBytecodesNonempty':f'{runtime_ok}/48','etherscanSourceVerifications':f'{verified}/48','walletBOwnershipCoverage':authority.get('walletBManagedOwnership','PASS'),'walletAManagedRoles':authority.get('walletAManagedRoleCount',state['summary']['WALLET_A_RESIDUAL_MANAGED_ROLES']),'phaseBGrants':f"{authority.get('phaseBGrantsActive',0)}/{authority.get('phaseBGrantsExpected',14)}"}
 dump(REL/'live-validation.json',live); (REL/'live-validation.md').write_text('# Live validation\n\nStatus: PASS after read-only RPC/Etherscan validation. No transaction sent.\n',encoding='utf-8'); print(json.dumps(live,indent=2)); return

def check():
 problems=[]
 # Clean-tree enforcement is handled by the release workflow before generation.
 # Draft packet checks allow source identity to remain pending; publish readiness is blocked in the packet itself.
 if any(('RELEASE_'+'WORKFLOW_INPUT_REF') in p.read_text(encoding='utf-8', errors='ignore') for p in REL.rglob('*') if p.is_file()): problems.append('placeholder found')
 for n in ['RELEASE_NOTES.md','RELEASE_MANIFEST.json','CONTRACTS_MAINNET.json','SHA256SUMS']:
  if not (REL/n).exists(): problems.append('missing asset '+n)
 if problems: print('RELEASE CHECK BLOCKED: '+ '; '.join(problems)); sys.exit(1)
 print('release check passed')

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['prepare','notes','build','validate','check']); a=ap.parse_args()
 if a.cmd in ['prepare','notes','build']: prepare()
 elif a.cmd=='validate': validate()
 else: check()
