#!/usr/bin/env python3
"""Build GoalOS Sovereign Machine Economy Kernel v3 additively."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEATURE_ID='sme-kernel-v3'
RELEASE_TITLE='GoalOS AGIALPHA Ascension Sovereign Machine Economy Kernel v3 ⚙️✨'
PAGES=[
 'sovereign-machine-economy-kernel-v3.html',
 'sovereign-machine-economy-kernel-v3-protocol.html',
 'sovereign-machine-economy-kernel-v3-chronicle.html',
 'sovereign-machine-economy-kernel-v3-verifier.html',
 'sovereign-machine-economy-kernel-v3-sdk.html',
]
ASSETS=[
 'sme-kernel-v3.css','sme-kernel-v3.js','sme-kernel-v3-core.js','sme-kernel-v3-adapters.js','sme-kernel-v3-worker.js'
]
SHARED=['index.html','routes.json','sitemap.xml','site-status.json']
COMPANION_MANIFESTS=[
 ('meta-agentic-alpha-agi-manifest.json','goalos.meta_agentic_alpha_agi.website_manifest.v2'),
 ('agi-alpha-node-v0-manifest.json','goalos.agi_alpha_node_v0.website_manifest.v2'),
 ('agi-jobs-v0-v2-manifest.json','goalos.agi_jobs_v0_v2.website_manifest.v3'),
 ('sovereign-machine-economy-manifest.json','goalos.sovereign_machine_economy.website_manifest.v2'),
]
STYLE_START='<!-- GOALOS_SME_KERNEL_V3_STYLE_START -->';STYLE_END='<!-- GOALOS_SME_KERNEL_V3_STYLE_END -->'
NAV_START='<!-- GOALOS_SME_KERNEL_V3_NAV_START -->';NAV_END='<!-- GOALOS_SME_KERNEL_V3_NAV_END -->'
HOME_START='<!-- GOALOS_SME_KERNEL_V3_HOME_START -->';HOME_END='<!-- GOALOS_SME_KERNEL_V3_HOME_END -->'
SME_NAV_END='<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_END -->';SME_HOME_END='<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_END -->'
BASE_URL='https://montrealai.github.io/goalos-agialpha-ascension/'

def now()->datetime:
 epoch=os.environ.get('SOURCE_DATE_EPOCH');return datetime.fromtimestamp(int(epoch),tz=timezone.utc) if epoch else datetime.now(timezone.utc)
def iso(value:datetime)->str:return value.replace(microsecond=0).isoformat().replace('+00:00','Z')
def stable(value:Any)->str:return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha_bytes(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def sha_value(value:Any)->str:return sha_bytes(stable(value).encode())
def sha_file(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(value,dict):raise ValueError(f'Expected JSON object: {path}')
 return value
def dump(path:Path,value:Any)->None:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def esc(value:Any)->str:return html.escape(str(value),quote=True)

def validate_content(data:dict[str,Any])->None:
 expected={'schema_version':'3.0.0','release_id':'GOALOS-AGIALPHA-SME-KERNEL-V3-001','release_title':RELEASE_TITLE,'version':'3.0.0-executable-constitutional-kernel','status':'executable-browser-local-constitutional-kernel','doctrine':'Typed state. Signed handoffs. Durable memory. Human authority.'}
 errors=[f'{key} mismatch' for key,value in expected.items() if data.get(key)!=value]
 counts={'hero_metrics':6,'autonomy_chain':6,'roles':5,'states':17,'envelope_types':10,'adapter_contract':6,'adapters':3,'presets':6,'postures':3,'risks':3,'incidents':5,'review_actions':4,'invariants':10,'threat_controls':8,'claim_boundary':6}
 for key,count in counts.items():
  if not isinstance(data.get(key),list) or len(data[key])!=count:errors.append(f'{key} must contain {count}')
 if [x.get('id') for x in data.get('states',[])]!=['DRAFT','MISSION_COMMITTED','INSTITUTION_PROPOSED','INSTITUTION_CHARTERED','NODE_ADMITTED','EXECUTION_BOUNDED','WORK_EXECUTED','EVIDENCE_SEALED','MARKET_CONVENED','VALIDATION_COMMITTED','VALIDATION_REVEALED','CHALLENGE_WINDOW_OPEN','SETTLEMENT_INTENT_PREPARED','AWAITING_HUMAN_REVIEW','HUMAN_REVIEW_RECORDED','MEMORY_DISPOSITION_RECORDED','COMPLETE']:errors.append('state order mismatch')
 sec=data.get('security',{})
 for key in ['external_dependencies','api_keys','wallet_connection','network_reads','network_writes','live_model_calls','live_compute','live_token_movement','credential_issuance','automatic_memory_promotion']:
  if sec.get(key) is not False:errors.append(f'security.{key} must be false')
 if sec.get('signature_algorithm')!='Ed25519' or sec.get('worker_isolation') is not True or sec.get('human_review_required') is not True:errors.append('security contract mismatch')
 if errors:raise RuntimeError('; '.join(errors))

def replace_block(raw:str,start:str,end:str,replacement:str)->str:
 if start in raw or end in raw:
  if raw.count(start)!=1 or raw.count(end)!=1:raise RuntimeError(f'Invalid marker count for {start}')
  return re.sub(re.escape(start)+r'.*?'+re.escape(end),replacement,raw,count=1,flags=re.S)
 return raw

def homepage_blocks(data:dict[str,Any])->tuple[str,str,str]:
 style=f'{STYLE_START}<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 rx=%2718%27 fill=%27%23030506%27/%3E%3Ccircle cx=%2732%27 cy=%2732%27 r=%2718%27 fill=%27none%27 stroke=%27%238fffd2%27 stroke-width=%274%27/%3E%3Ccircle cx=%2732%27 cy=%2732%27 r=%277%27 fill=%27%23fff0bd%27/%3E%3C/svg%3E" data-goalos-sme-kernel-v3-icon><link rel="stylesheet" href="assets/sme-kernel-v3.css" data-goalos-sme-kernel-v3>{STYLE_END}'
 nav=f'{NAV_START}<a href="sovereign-machine-economy-kernel-v3.html">Kernel v3</a>{NAV_END}'
 home=f'''{HOME_START}<section class="kv3-home-gateway" id="sme-kernel-v3" data-goalos-feature="sme-kernel-v3"><div class="kv3-home-in"><div><small>GOALOS AGIALPHA ASCENSION · EXECUTABLE CONSTITUTIONAL FOUNDATION</small><h2>THE SOVEREIGN <span>KERNEL v3</span></h2><p><strong>Experience above. Protocol beneath. Proof throughout.</strong> Seventeen strict states, ten typed envelopes, five Ed25519 authorities, three replaceable engine adapters, an append-only mission chronicle, portable bundle verification and a signed Human Review Chamber.</p><div class="kv3-home-stats"><div class="kv3-home-stat"><strong>17</strong><span>constitutional states</span></div><div class="kv3-home-stat"><strong>10</strong><span>typed envelopes</span></div><div class="kv3-home-stat"><strong>5</strong><span>signing authorities</span></div><div class="kv3-home-stat"><strong>0</strong><span>external actions</span></div></div><div class="kv3-home-actions"><a href="sovereign-machine-economy-kernel-v3.html">Launch Kernel v3</a><a href="sovereign-machine-economy-kernel-v3-protocol.html">Inspect Protocol</a><a href="sovereign-machine-economy-kernel-v3-verifier.html">Verify Bundle</a><a href="sovereign-machine-economy.html">Return to Machine Economy Ω</a></div></div><div class="kv3-home-visual" aria-label="Sovereign Machine Economy Kernel v3"><div class="kv3-home-ring"></div><div class="kv3-home-ring r2"></div><div class="kv3-home-core"><span>KERNEL<br>v3</span></div><div class="kv3-home-node a"><b>MIND</b>Charter</div><div class="kv3-home-node b"><b>NODE</b>Execute</div><div class="kv3-home-node c"><b>MARKET</b>Coordinate</div><div class="kv3-home-node d"><b>PROOF</b>Verify</div><div class="kv3-home-node e"><b>HUMAN</b>Authorize</div></div></div></section>{HOME_END}'''
 return style,nav,home

def patch_homepage(path:Path,data:dict[str,Any])->None:
 raw=path.read_text(encoding='utf-8');style,nav,home=homepage_blocks(data)
 if STYLE_START in raw:raw=replace_block(raw,STYLE_START,STYLE_END,style)
 elif '</head>' in raw:raw=raw.replace('</head>',style+'\n</head>',1)
 else:raise RuntimeError('Homepage missing </head>')
 if NAV_START in raw:raw=replace_block(raw,NAV_START,NAV_END,nav)
 elif SME_NAV_END in raw:raw=raw.replace(SME_NAV_END,SME_NAV_END+'\n'+nav,1)
 elif '</nav>' in raw:raw=raw.replace('</nav>',nav+'\n</nav>',1)
 else:raise RuntimeError('Homepage missing navigation insertion point')
 if HOME_START in raw:raw=replace_block(raw,HOME_START,HOME_END,home)
 elif SME_HOME_END in raw:raw=raw.replace(SME_HOME_END,SME_HOME_END+'\n'+home,1)
 elif '</main>' in raw:raw=raw.replace('</main>',home+'\n</main>',1)
 elif '</body>' in raw:raw=raw.replace('</body>',home+'\n</body>',1)
 else:raise RuntimeError('Homepage missing content insertion point')
 path.write_text(raw,encoding='utf-8')

def render(template:str,data:dict[str,Any],page:str)->str:
 metrics=''.join(f'<div class="kv3-metric"><strong>{esc(x["value"])}</strong><span>{esc(x["label"])}</span></div>' for x in data['hero_metrics'])
 autonomy=''.join(f'<li data-phase="{esc(x["id"])}"><b>{esc(x["index"])}</b><div><strong>{esc(x["label"])} <span aria-hidden="true">{esc(x["icon"])}</span></strong><small>{esc(x["artifact"])}</small></div></li>' for x in data['autonomy_chain'])
 reviews=''.join(f'<button class="kv3-review-action" type="button" data-review-action="{esc(x["id"])}" disabled><strong>{esc(x["label"])}</strong><span>{esc(x["memory"])}</span></button>' for x in data['review_actions'])
 envelopes=''.join(f'<article class="kv3-envelope"><span>{esc(x["issuer"])}</span><h3>{esc(x["id"])}</h3><p>{esc(x["purpose"])}</p></article>' for x in data['envelope_types'])
 states=''.join(f'<article class="kv3-transition-node"><span>{i:02d} · {esc(x["plane"])}</span><strong>{esc(x["label"])}</strong></article>' for i,x in enumerate(data['states'],1))
 embedded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
 out=template.replace('@@DATA_JSON@@',embedded).replace('@@HERO_METRICS@@',metrics).replace('@@AUTONOMY_CHAIN@@',autonomy).replace('@@REVIEW_ACTIONS@@',reviews).replace('@@ENVELOPE_CARDS@@',envelopes).replace('@@STATE_CARDS@@',states)
 key={'sovereign-machine-economy-kernel-v3.html':'experience','sovereign-machine-economy-kernel-v3-protocol.html':'protocol','sovereign-machine-economy-kernel-v3-chronicle.html':'chronicle','sovereign-machine-economy-kernel-v3-verifier.html':'verifier','sovereign-machine-economy-kernel-v3-sdk.html':'sdk'}[page]
 out=out.replace(f'data-page="{key}"',f'data-page="{key}" aria-current="page"')
 if '@@' in out:raise RuntimeError(f'Unresolved template token in {page}')
 return out

def update_routes(path:Path,data:dict[str,Any])->None:
 payload=load(path) if path.exists() else {'version':'unknown','routes':[]};routes=payload.get('routes',[])
 if not isinstance(routes,list):raise RuntimeError('routes.json routes must be an array')
 payload['routes']=sorted(set(map(str,routes)).union(PAGES));payload['sme_kernel_v3']={'release_id':data['release_id'],'version':data['version'],'pages':PAGES,'states':17,'envelope_types':10,'signing_authorities':5,'adapters':3,'storage':'IndexedDB','signature':'Ed25519','worker_isolated':True,'external_actions':0};dump(path,payload)

def update_sitemap(path:Path)->None:
 raw=path.read_text(encoding='utf-8') if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>"
 for page in PAGES:
  url=BASE_URL+page
  if url not in raw:
   if '</urlset>' not in raw:raise RuntimeError('sitemap missing </urlset>')
   raw=raw.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>',1)
 path.write_text(raw,encoding='utf-8')

def update_status(path:Path,data:dict[str,Any],built_at:str)->None:
 site=path.parent;payload=load(path) if path.exists() else {};payload['root_html_pages']=len(list(site.glob('*.html')));payload['published_html_pages_including_resources']=len(list(site.rglob('*.html')));payload['sme_kernel_v3']={'release':data['release_id'],'version':data['version'],'status':data['status'],'pages':PAGES,'states':17,'typed_envelopes':10,'signing_authorities':5,'adapters':3,'signature_algorithm':'Ed25519','durable_store':'IndexedDB','worker_isolated':True,'human_review_required':True,'external_authority':'NONE_GRANTED','external_actions':0,'built_at':built_at};dump(path,payload)

def reconcile(site:Path,data:dict[str,Any],built_at:str)->list[str]:
 names=[]
 for filename,schema in COMPANION_MANIFESTS:
  path=site/filename
  if not path.is_file():raise RuntimeError(f'Required companion manifest missing: {filename}')
  payload=load(path)
  if payload.get('schema')!=schema:raise RuntimeError(f'Unrecognized companion manifest schema: {filename}')
  files=payload.get('files')
  if not isinstance(files,dict):raise RuntimeError(f'Companion manifest files missing: {filename}')
  for relative in SHARED:
   target=site/relative
   if target.is_file():files[relative]={'sha256':sha_file(target),'bytes':target.stat().st_size}
  # Companion manifests form an acyclic dependency chain: META → Node → Jobs → Machine Economy.
  # Refresh references to earlier manifests after their Kernel reconciliation has been written.
  for earlier_name,_ in COMPANION_MANIFESTS:
   if earlier_name==filename:break
   target=site/earlier_name
   if earlier_name in files and target.is_file():files[earlier_name]={'sha256':sha_file(target),'bytes':target.stat().st_size}
  integration=payload.setdefault('integration',{});history=integration.setdefault('reconciliations',[])
  if not isinstance(history,list):raise RuntimeError(f'Invalid reconciliation history: {filename}')
  history[:]=[x for x in history if not isinstance(x,dict) or x.get('release_id')!=data['release_id']]
  history.append({'release_id':data['release_id'],'version':data['version'],'built_at':built_at,'reason':'Kernel v3 extended declared shared website surfaces after the companion release','files':SHARED})
  dump(path,payload);names.append(filename)
 return names

def main()->int:
 root=Path(__file__).resolve().parents[2]
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--site',type=Path,default=root/'site');parser.add_argument('--root',type=Path,default=root);parser.add_argument('--content',type=Path,default=root/'content/sme-kernel-v3.json');parser.add_argument('--source',type=Path,default=root/'website/features/sme-kernel-v3');args=parser.parse_args()
 site=args.site.resolve();repo=args.root.resolve();content_path=args.content.resolve();source=args.source.resolve();built_at=iso(now())
 if not site.is_dir() or not (site/'index.html').is_file():raise RuntimeError(f'Built GoalOS site missing: {site}')
 for relative in ['sovereign-machine-economy.html','sovereign-machine-economy-manifest.json','agi-jobs-v0-v2.html','agi-alpha-node-v0.html','meta-agentic-alpha-agi.html']:
  if not (site/relative).is_file():raise RuntimeError(f'Build all constitutional engines before Kernel v3: {relative}')
 data=load(content_path);validate_content(data);before={p.relative_to(site).as_posix():sha_file(p) for p in site.rglob('*') if p.is_file()}
 template_dir=source/'templates';asset_dir=source/'assets';outputs=[]
 for page in PAGES:
  template=template_dir/page
  if not template.is_file():raise RuntimeError(f'Missing template: {template}')
  output=site/page;output.write_text(render(template.read_text(encoding='utf-8'),data,page),encoding='utf-8');outputs.append(output)
 out_assets=site/'assets';out_assets.mkdir(parents=True,exist_ok=True)
 for asset in ASSETS:
  src=asset_dir/asset
  if not src.is_file():raise RuntimeError(f'Missing asset: {src}')
  dest=out_assets/asset;shutil.copy2(src,dest);outputs.append(dest)
 data_out=site/'data/sme-kernel-v3.json';dump(data_out,data);outputs.append(data_out)
 patch_homepage(site/'index.html',data);update_routes(site/'routes.json',data);update_sitemap(site/'sitemap.xml');update_status(site/'site-status.json',data,built_at)
 companions=reconcile(site,data,built_at)
 download=site/'downloads/sme-kernel-v3';download.mkdir(parents=True,exist_ok=True)
 protocol={'schema':'goalos.sme.kernel.v3.protocol_manifest','protocol':'goalos.sme.kernel.v3','schemaVersion':'3.0.0','release_id':data['release_id'],'states':data['states'],'envelope_types':data['envelope_types'],'roles':data['roles'],'adapter_contract':data['adapter_contract'],'security':data['security'],'authority':'NONE_GRANTED','external_actions':0}
 protocol['protocol_root']=sha_value(protocol);dump(download/'sme-kernel-v3-protocol-manifest.json',protocol)
 template={'schema':'goalos.sme.kernel.v3.mission_template','protocol':'goalos.sme.kernel.v3','mission':data['presets'][0]['mission'],'preset':data['presets'][0]['id'],'posture':data['presets'][0]['posture'],'risk':data['presets'][0]['risk'],'incident':'none','authority':'NONE_GRANTED','note':'Run Kernel v3 in a compatible browser to create a signed portable mission bundle.'};dump(download/'sme-kernel-v3-mission-template.json',template)
 shutil.copy2(asset_dir/'sme-kernel-v3-core.js',download/'sme-kernel-v3-core.js');shutil.copy2(asset_dir/'sme-kernel-v3-adapters.js',download/'sme-kernel-v3-adapters.js')
 brief=f"""# GoalOS Sovereign Machine Economy Kernel v3 — Executive Review Brief

**Release:** `{data['release_id']}`  
**Version:** `{data['version']}`  
**Protocol:** `goalos.sme.kernel.v3`  
**Build:** `{built_at}`

Kernel v3 supplies the executable foundation beneath the Sovereign Machine Economy: a seventeen-state constitutional state machine, ten typed protocol envelopes, five persistent local Ed25519 role identities, three replaceable engine adapters, an isolated Web Worker runtime, an append-only IndexedDB event chronicle, portable mission bundles, strict independent verification, and signed human review certificates.

No external authority is granted. Factual correctness is not certified. No wallet, network request, model call, token movement, settlement execution, credential issuance, production activation, or automatic memory promotion occurs.
"""
 (download/'sme-kernel-v3-executive-brief.md').write_text(brief,encoding='utf-8')
 outputs.extend([download/'sme-kernel-v3-protocol-manifest.json',download/'sme-kernel-v3-mission-template.json',download/'sme-kernel-v3-core.js',download/'sme-kernel-v3-adapters.js',download/'sme-kernel-v3-executive-brief.md'])
 outputs.extend(site/x for x in SHARED);outputs.extend(site/x for x in companions)
 files={p.relative_to(site).as_posix():{'sha256':sha_file(p),'bytes':p.stat().st_size} for p in outputs}
 manifest={'schema':'goalos.sme.kernel.v3.website_manifest.v1','release_id':data['release_id'],'release_title':data['release_title'],'version':data['version'],'built_at':built_at,'protocol':'goalos.sme.kernel.v3','experience':{'states':17,'envelopes':10,'authorities':5,'adapters':3,'signature':'Ed25519','storage':'IndexedDB','worker_isolated':True,'external_actions':0},'integration':{'mode':'additive-post-sovereign-machine-economy','canonical_v86_source_modified':False,'homepage_markers':[STYLE_START,NAV_START,HOME_START],'allowed_existing_changes':[ *SHARED,*companions]},'files':files}
 manifest_path=site/'sme-kernel-v3-manifest.json';dump(manifest_path,manifest)
 after={p.relative_to(site).as_posix():sha_file(p) for p in site.rglob('*') if p.is_file()};removed=sorted(set(before)-set(after));changed=sorted(name for name in set(before)&set(after) if before[name]!=after[name]);added=sorted(set(after)-set(before));allowed=set(SHARED)|set(companions)
 unexpected=sorted(set(changed)-allowed)
 report={'schema':'goalos.sme.kernel.v3.build_report.v1','status':'PASS' if not removed and not unexpected else 'FAIL','release_title':data['release_title'],'version':data['version'],'built_at':built_at,'pages':PAGES,'files_written':sorted([*files,manifest_path.relative_to(site).as_posix()]),'files_removed':removed,'declared_existing_files_allowed_to_change':sorted(allowed),'unexpected_existing_file_changes':unexpected,'declared_generated_outputs':sorted(set(PAGES+[f"assets/{x}" for x in ASSETS]+['data/sme-kernel-v3.json','sme-kernel-v3-manifest.json','qa/sme-kernel-v3-build.json']+[f"downloads/sme-kernel-v3/{x}" for x in ['sme-kernel-v3-protocol-manifest.json','sme-kernel-v3-mission-template.json','sme-kernel-v3-core.js','sme-kernel-v3-adapters.js','sme-kernel-v3-executive-brief.md']])), 'companion_manifests_reconciled':companions,'external_actions':0}
 report_path=site/'qa/sme-kernel-v3-build.json';dump(report_path,report)
 if report['status']!='PASS':raise RuntimeError(f'Kernel v3 preservation failed: {report}')
 print(json.dumps({'status':'PASS','release':data['release_id'],'pages':PAGES,'files_added':len(added),'existing_files_changed':changed,'report':str(report_path)},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
