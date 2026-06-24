#!/usr/bin/env python3
"""Verify SME Kernel v3, its executable protocol contract, and additive preservation boundary."""
from __future__ import annotations
import argparse, ast, hashlib, json, re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

RELEASE_TITLE='GoalOS AGIALPHA Ascension Sovereign Machine Economy Kernel v3 ⚙️✨'
PAGES=['sovereign-machine-economy-kernel-v3.html','sovereign-machine-economy-kernel-v3-protocol.html','sovereign-machine-economy-kernel-v3-chronicle.html','sovereign-machine-economy-kernel-v3-verifier.html','sovereign-machine-economy-kernel-v3-sdk.html']
ASSETS=['assets/sme-kernel-v3.css','assets/sme-kernel-v3.js','assets/sme-kernel-v3-core.js','assets/sme-kernel-v3-adapters.js','assets/sme-kernel-v3-worker.js']
DOWNLOADS=['downloads/sme-kernel-v3/sme-kernel-v3-protocol-manifest.json','downloads/sme-kernel-v3/sme-kernel-v3-mission-template.json','downloads/sme-kernel-v3/sme-kernel-v3-core.js','downloads/sme-kernel-v3/sme-kernel-v3-adapters.js','downloads/sme-kernel-v3/sme-kernel-v3-executive-brief.md']
COMPANIONS={'meta-agentic-alpha-agi-manifest.json':'goalos.meta_agentic_alpha_agi.website_manifest.v2','agi-alpha-node-v0-manifest.json':'goalos.agi_alpha_node_v0.website_manifest.v2','agi-jobs-v0-v2-manifest.json':'goalos.agi_jobs_v0_v2.website_manifest.v3','sovereign-machine-economy-manifest.json':'goalos.sovereign_machine_economy.website_manifest.v2'}
SHARED={'index.html','routes.json','sitemap.xml','site-status.json'}
NEW_OUTPUTS=set(PAGES+ASSETS+DOWNLOADS+['data/sme-kernel-v3.json','sme-kernel-v3-manifest.json','qa/sme-kernel-v3-build.json'])
ALLOWED_CHANGED=SHARED|set(COMPANIONS)

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def stable(value:Any)->str:return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha_value(value:Any)->str:return hashlib.sha256(stable(value).encode()).hexdigest()
def load(path:Path)->Any:return json.loads(path.read_text(encoding='utf-8'))
def local_targets(raw:str)->list[str]:return re.findall(r'(?:href|src)=["\']([^"\']+)["\']',raw,re.I)

def run(site:Path,root:Path,content_path:Path,envelope_schema:Path,bundle_schema:Path,baseline:Path|None,output:Path)->dict[str,Any]:
 checks=[];preservation={}
 def check(label:str,condition:bool,detail:Any='')->None:checks.append({'label':label,'status':'PASS' if condition else 'FAIL','detail':detail})
 required=[*PAGES,*ASSETS,*DOWNLOADS,'data/sme-kernel-v3.json','sme-kernel-v3-manifest.json','qa/sme-kernel-v3-build.json',*sorted(SHARED),*COMPANIONS]
 check('site-exists',site.is_dir(),str(site))
 for relative in required:
  path=site/relative;check(f'required:{relative}',path.is_file() and path.stat().st_size>0,path.stat().st_size if path.is_file() else 0)
 if not all((site/r).is_file() for r in required):
  report={'schema':'goalos.sme.kernel.v3.static_qa.v1','status':'FAIL','checks_total':len(checks),'checks_passed':sum(x['status']=='PASS' for x in checks),'checks_failed':sum(x['status']=='FAIL' for x in checks),'checks':checks,'preservation':preservation};output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return report
 content=load(content_path);data=load(site/'data/sme-kernel-v3.json');manifest=load(site/'sme-kernel-v3-manifest.json');build=load(site/'qa/sme-kernel-v3-build.json');protocol=load(site/'downloads/sme-kernel-v3/sme-kernel-v3-protocol-manifest.json');mission_template=load(site/'downloads/sme-kernel-v3/sme-kernel-v3-mission-template.json')
 expected={'schema_version':'3.0.0','release_id':'GOALOS-AGIALPHA-SME-KERNEL-V3-001','release_title':RELEASE_TITLE,'version':'3.0.0-executable-constitutional-kernel','status':'executable-browser-local-constitutional-kernel','doctrine':'Typed state. Signed handoffs. Durable memory. Human authority.'}
 for key,value in expected.items():check(f'content:{key}',content.get(key)==value,content.get(key));check(f'data:{key}',data.get(key)==value,data.get(key))
 counts={'hero_metrics':6,'roles':5,'states':17,'envelope_types':10,'adapter_contract':6,'adapters':3,'presets':6,'postures':3,'risks':3,'incidents':5,'review_actions':4,'invariants':10,'threat_controls':8,'claim_boundary':6}
 for key,count in counts.items():check(f'content-count:{key}',len(content.get(key,[]))==count,len(content.get(key,[])));check(f'data-count:{key}',len(data.get(key,[]))==count,len(data.get(key,[])))
 check('state-order',[x.get('id') for x in data['states']]==['DRAFT','MISSION_COMMITTED','INSTITUTION_PROPOSED','INSTITUTION_CHARTERED','NODE_ADMITTED','EXECUTION_BOUNDED','WORK_EXECUTED','EVIDENCE_SEALED','MARKET_CONVENED','VALIDATION_COMMITTED','VALIDATION_REVEALED','CHALLENGE_WINDOW_OPEN','SETTLEMENT_INTENT_PREPARED','AWAITING_HUMAN_REVIEW','HUMAN_REVIEW_RECORDED','MEMORY_DISPOSITION_RECORDED','COMPLETE'],[x.get('id') for x in data['states']])
 check('role-uniqueness',len({x['id'] for x in data['roles']})==5,[x['id'] for x in data['roles']]);check('envelope-uniqueness',len({x['id'] for x in data['envelope_types']})==10,[x['id'] for x in data['envelope_types']])
 security=data.get('security',{})
 for key in ['external_dependencies','api_keys','wallet_connection','network_reads','network_writes','live_model_calls','live_compute','live_token_movement','credential_issuance','automatic_memory_promotion']:check(f'security-deny:{key}',security.get(key) is False,security.get(key))
 check('security-ed25519',security.get('signature_algorithm')=='Ed25519',security.get('signature_algorithm'));check('security-worker',security.get('worker_isolation') is True,security.get('worker_isolation'));check('security-human',security.get('human_review_required') is True,security.get('human_review_required'));check('security-authority',security.get('external_authority')=='none',security.get('external_authority'))
 page_contract={
  PAGES[0]:['THE','KERNEL','kv3-mission-form','kv3-state-rail','kv3-event-list','kv3-review-chamber','kv3-export-bundle'],
  PAGES[1]:['TYPED','HANDOFFS','Envelope registry','Canonical envelope','kv3-transition-map','kv3-identity-grid'],
  PAGES[2]:['THE','CHRONICLE','kv3-mission-list','kv3-chronicle-table','Evidence maturity'],
  PAGES[3]:['TRUST','REPLAYED','kv3-bundle-file','kv3-tamper-bundle','kv3-verifier-result'],
  PAGES[4]:['THE','KERNEL SDK','Adapter contract','kv3-adapter-grid','sme-kernel-v3-core.js']
 }
 for page,needles in page_contract.items():
  path=site/page;raw=path.read_text(encoding='utf-8');check(f'page-size:{page}',path.stat().st_size>5500,path.stat().st_size);check(f'page-doctype:{page}',raw.lstrip().lower().startswith('<!doctype html>'),raw[:30]);check(f'page-csp:{page}',"connect-src 'none'" in raw and "worker-src 'self'" in raw,'CSP');check(f'page-data:{page}','id="kv3-data"' in raw,'kv3-data');check(f'page-css:{page}','assets/sme-kernel-v3.css' in raw,'css');check(f'page-js:{page}','assets/sme-kernel-v3.js' in raw,'js');check(f'page-no-external:{page}',not re.search(r'(?:src|href)=["\'](?:https?:)?//',raw,re.I),'external scan')
  for needle in needles:check(f'page-contract:{page}:{sha_value(needle)[:10]}',needle in raw,needle)
  for target in local_targets(raw):
   clean=unquote(target.split('#',1)[0].split('?',1)[0])
   if not clean or clean.startswith(('#','data:','mailto:','tel:','javascript:')) or clean.startswith(('http://','https://','//')):continue
   check(f'local-target:{page}:{clean}',(site/clean).exists(),clean)
 homepage=(site/'index.html').read_text(encoding='utf-8')
 for marker in ['GOALOS_SME_KERNEL_V3_STYLE_START','GOALOS_SME_KERNEL_V3_STYLE_END','GOALOS_SME_KERNEL_V3_NAV_START','GOALOS_SME_KERNEL_V3_NAV_END','GOALOS_SME_KERNEL_V3_HOME_START','GOALOS_SME_KERNEL_V3_HOME_END']:check(f'homepage-marker:{marker}',homepage.count(marker)==1,homepage.count(marker))
 check('homepage-nav',homepage.count('href="sovereign-machine-economy-kernel-v3.html">Kernel v3</a>')==1,homepage.count('href="sovereign-machine-economy-kernel-v3.html">Kernel v3</a>'));check('homepage-gateway',homepage.count('id="sme-kernel-v3"')==1,homepage.count('id="sme-kernel-v3"'));check('homepage-data-favicon',homepage.count('data-goalos-sme-kernel-v3-icon')==1 and 'data:image/svg+xml' in homepage,homepage.count('data-goalos-sme-kernel-v3-icon'));check('homepage-after-omega',homepage.index('GOALOS_SME_KERNEL_V3_HOME_START')>homepage.index('GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_END'),'order')
 routes=load(site/'routes.json');route=routes.get('sme_kernel_v3',{});check('routes-pages',set(PAGES).issubset(set(routes.get('routes',[]))),routes.get('routes',[]));
 for key,value in {'states':17,'envelope_types':10,'signing_authorities':5,'adapters':3,'signature':'Ed25519','storage':'IndexedDB','worker_isolated':True,'external_actions':0}.items():check(f'routes:{key}',route.get(key)==value,route.get(key))
 sitemap=(site/'sitemap.xml').read_text(encoding='utf-8')
 for page in PAGES:check(f'sitemap:{page}',page in sitemap,page)
 status=load(site/'site-status.json').get('sme_kernel_v3',{})
 for key,value in {'states':17,'typed_envelopes':10,'signing_authorities':5,'adapters':3,'signature_algorithm':'Ed25519','durable_store':'IndexedDB','worker_isolated':True,'human_review_required':True,'external_authority':'NONE_GRANTED','external_actions':0}.items():check(f'status:{key}',status.get(key)==value,status.get(key))
 check('protocol-schema',protocol.get('schema')=='goalos.sme.kernel.v3.protocol_manifest',protocol.get('schema'));check('protocol-root',protocol.get('protocol_root')==sha_value({k:v for k,v in protocol.items() if k!='protocol_root'}),protocol.get('protocol_root'));check('protocol-states',len(protocol.get('states',[]))==17,len(protocol.get('states',[])));check('protocol-envelopes',len(protocol.get('envelope_types',[]))==10,len(protocol.get('envelope_types',[])));check('mission-template',mission_template.get('schema')=='goalos.sme.kernel.v3.mission_template' and mission_template.get('authority')=='NONE_GRANTED',mission_template)
 try:
  import jsonschema
  jsonschema.Draft202012Validator.check_schema(load(envelope_schema));jsonschema.Draft202012Validator.check_schema(load(bundle_schema));check('json-schemas',True,'Draft 2020-12')
 except Exception as exc:check('json-schemas',False,str(exc))
 core=(site/'assets/sme-kernel-v3-core.js').read_text(encoding='utf-8');adapters=(site/'assets/sme-kernel-v3-adapters.js').read_text(encoding='utf-8');worker=(site/'assets/sme-kernel-v3-worker.js').read_text(encoding='utf-8');app=(site/'assets/sme-kernel-v3.js').read_text(encoding='utf-8');css=(site/'assets/sme-kernel-v3.css').read_text(encoding='utf-8')
 for needle in ['Ed25519','verifyBundle','signEnvelope','createEvent','IndexedDB' if False else 'STATE_CONTRACT','HUMAN_REVIEW_RECORDED','MEMORY_DISPOSITION_RECORDED']:check(f'core:{needle}',needle in core,needle)
 check('core-seventeen-states',all(f"'{state}'" in core for state in [x['id'] for x in data['states']]),'states');check('core-no-network',not re.search(r'\b(fetch|XMLHttpRequest|WebSocket)\s*\(',core),'network')
 for method in ['initialize','propose','execute','evaluate','produceEvidence','verifyEvidence']:check(f'adapter-contract:{method}',method in adapters,method)
 for adapter in ['MetaAgenticAdapter','AlphaNodeAdapter','AGIJobsAdapter']:check(f'adapter:{adapter}',adapter in adapters,adapter)
 for needle in ['importScripts','indexedDB.open','getOrCreateIdentity','runMission','applyHumanReview','exportMission','VERIFY_BUNDLE','Ed25519']:check(f'worker:{needle}',needle in worker,needle)
 check('worker-no-network',not re.search(r'\b(fetch|XMLHttpRequest|WebSocket)\s*\(',worker),'network');check('worker-no-local-storage','localStorage' not in worker and 'sessionStorage' not in worker,'storage');check('worker-five-identities','Core.ROLE_IDS' in worker,'roles')
 for needle in ['new Worker','RUN_MISSION','APPLY_REVIEW','EXPORT_MISSION','VERIFY_BUNDLE','IndexedDB','APPEND ONLY']:check(f'app:{needle}',needle in app,needle)
 check('app-no-network',not re.search(r'\b(fetch|XMLHttpRequest|WebSocket)\s*\(',app),'network');check('css-scoped','.kv3-body' in css and '.kv3-home-gateway' in css,'scoped');check('css-responsive','@media(max-width:760px)' in css or '@media (max-width:760px)' in css,'responsive');check('css-reduced-motion','prefers-reduced-motion' in css,'motion')
 check('manifest-schema',manifest.get('schema')=='goalos.sme.kernel.v3.website_manifest.v1',manifest.get('schema'));check('manifest-release',manifest.get('release_id')==data.get('release_id'),manifest.get('release_id'));files=manifest.get('files',{})
 for relative,record in files.items():
  target=site/relative;check(f'manifest-exists:{relative}',target.is_file(),relative)
  if target.is_file():check(f'manifest-hash:{relative}',record.get('sha256')==sha(target),record.get('sha256'));check(f'manifest-bytes:{relative}',record.get('bytes')==target.stat().st_size,record.get('bytes'))
 check('manifest-coverage',(NEW_OUTPUTS-{'sme-kernel-v3-manifest.json','qa/sme-kernel-v3-build.json'})<=set(files),sorted((NEW_OUTPUTS-{'sme-kernel-v3-manifest.json','qa/sme-kernel-v3-build.json'})-set(files)));check('build-pass',build.get('status')=='PASS',build.get('status'));check('build-no-removals',build.get('files_removed')==[],build.get('files_removed'));check('build-no-unexpected',build.get('unexpected_existing_file_changes')==[],build.get('unexpected_existing_file_changes'))
 for filename,schema in COMPANIONS.items():
  companion=load(site/filename);check(f'companion-schema:{filename}',companion.get('schema')==schema,companion.get('schema'));cfiles=companion.get('files',{})
  for relative in SHARED:check(f'companion-shared:{filename}:{relative}',cfiles.get(relative,{}).get('sha256')==sha(site/relative),cfiles.get(relative,{}).get('sha256'))
  history=companion.get('integration',{}).get('reconciliations',[]);check(f'companion-history:{filename}',any(isinstance(x,dict) and x.get('release_id')==data.get('release_id') for x in history),history[-2:] if isinstance(history,list) else history)
 forbidden=['PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY','SEED_PHRASE','MNEMONIC','MAINNET_RPC_URL=','ETHERSCAN_API_KEY=']
 feature_text='\n'.join((site/r).read_text(encoding='utf-8',errors='ignore') for r in [*PAGES,*ASSETS,'data/sme-kernel-v3.json'])
 for index,phrase in enumerate(forbidden,1):check(f'public-secret-token:{index}',phrase not in feature_text,hashlib.sha256(phrase.encode()).hexdigest()[:12])
 for phrase in ['production authorized','user funds authorized','guaranteed return','guaranteed roi']:check(f'claim-scan:{sha_value(phrase)[:10]}',phrase not in feature_text.lower(),sha_value(phrase)[:12])
 for path in [root/'scripts/website/build_sme_kernel_v3.py',root/'scripts/website/snapshot_sme_kernel_v3_site.py',root/'scripts/website/verify_sme_kernel_v3.py',root/'scripts/website/visual_check_sme_kernel_v3.py',root/'test/test_sme_kernel_v3_website.py']:
  if path.is_file():
   try:ast.parse(path.read_text(encoding='utf-8'),filename=str(path),feature_version=(3,11));check(f'python311:{path.name}',True,'PASS')
   except SyntaxError as exc:check(f'python311:{path.name}',False,str(exc))
 if baseline:
  snap=load(baseline);before=snap.get('files',{});current={p.relative_to(site).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in site.rglob('*') if p.is_file()};removed=sorted(set(before)-set(current));changed=sorted(name for name in set(before)&set(current) if before[name].get('sha256')!=current[name].get('sha256'));added=sorted(set(current)-set(before));unexpected_changed=sorted(set(changed)-ALLOWED_CHANGED);allowed_add=NEW_OUTPUTS|{output.relative_to(site).as_posix()} if output.is_relative_to(site) else NEW_OUTPUTS;unexpected_added=sorted(set(added)-allowed_add);preservation={'baseline_count':len(before),'current_count':len(current),'removed':removed,'changed':changed,'added':added,'unexpected_changed':unexpected_changed,'unexpected_added':unexpected_added,'allowed_changed':sorted(ALLOWED_CHANGED)};check('preservation-count',len(before)==snap.get('file_count'),{'listed':len(before),'declared':snap.get('file_count')});check('preservation-no-removals',not removed,removed);check('preservation-no-unexpected-changes',not unexpected_changed,unexpected_changed);check('preservation-only-declared-additions',not unexpected_added,unexpected_added)
 else:check('preservation-baseline-optional',True,'No baseline supplied')
 failed=[x for x in checks if x['status']=='FAIL'];report={'schema':'goalos.sme.kernel.v3.static_qa.v1','release_title':RELEASE_TITLE,'status':'PASS' if not failed else 'FAIL','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'preservation':preservation};output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return report

def main()->int:
 root=Path(__file__).resolve().parents[2];parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--site',type=Path,default=root/'site');parser.add_argument('--root',type=Path,default=root);parser.add_argument('--content',type=Path,default=root/'content/sme-kernel-v3.json');parser.add_argument('--envelope-schema',type=Path,default=root/'schemas/sme-kernel-v3-envelope.schema.json');parser.add_argument('--bundle-schema',type=Path,default=root/'schemas/sme-kernel-v3-mission-bundle.schema.json');parser.add_argument('--baseline',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args();output=args.output or args.site/'qa/sme-kernel-v3-static.json';report=run(args.site.resolve(),args.root.resolve(),args.content.resolve(),args.envelope_schema.resolve(),args.bundle_schema.resolve(),args.baseline.resolve() if args.baseline else None,output.resolve());print(json.dumps({'status':report['status'],'checks_total':report['checks_total'],'checks_passed':report['checks_passed'],'checks_failed':report['checks_failed'],'output':str(output)},indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
