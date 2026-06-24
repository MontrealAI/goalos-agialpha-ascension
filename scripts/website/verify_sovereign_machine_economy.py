#!/usr/bin/env python3
"""Verify the generated GoalOS Sovereign Machine Economy and preservation boundary."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any

PAGES=["sovereign-machine-economy.html","sovereign-machine-economy-architecture.html","sovereign-machine-economy-chronicle.html","sovereign-machine-economy-atlas.html"]
SHARED=["index.html","routes.json","sitemap.xml","site-status.json"]
COMPANIONS={"meta-agentic-alpha-agi-manifest.json":"goalos.meta_agentic_alpha_agi.website_manifest.v2","agi-alpha-node-v0-manifest.json":"goalos.agi_alpha_node_v0.website_manifest.v2","agi-jobs-v0-v2-manifest.json":"goalos.agi_jobs_v0_v2.website_manifest.v3"}
NEW={*PAGES,"sovereign-machine-economy-manifest.json","assets/sovereign-machine-economy.css","assets/sovereign-machine-economy.js","data/sovereign-machine-economy.json","downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json","qa/sovereign-machine-economy-build.json"}
ALLOWED_CHANGED={*SHARED,*COMPANIONS}
MARKERS=["GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_START","GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_START","GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_START"]
HEX=re.compile(r"^[0-9a-f]{64}$")
def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def stable(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest(v:Any)->str:return hashlib.sha256(stable(v).encode()).hexdigest()
def load(path:Path)->Any:return json.loads(path.read_text(encoding='utf-8'))
def run(site:Path,root:Path,baseline:Path|None,schema:Path|None,output:Path)->dict[str,Any]:
 checks=[]
 def check(label:str,condition:bool,detail:Any="")->None:checks.append({'label':label,'status':'PASS' if condition else 'FAIL','detail':detail})
 check('site-exists',site.is_dir(),str(site))
 required=[*PAGES,'sovereign-machine-economy-manifest.json','assets/sovereign-machine-economy.css','assets/sovereign-machine-economy.js','data/sovereign-machine-economy.json','downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json','qa/sovereign-machine-economy-build.json']
 for rel in required:
  path=site/rel;check(f'required:{rel}',path.is_file() and path.stat().st_size>0,path.stat().st_size if path.is_file() else 0)
 if not all((site/x).is_file() for x in required):
  report={'schema':'goalos.sovereign_machine_economy.static_qa.v1','status':'FAIL','checks':checks};output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');return report
 data=load(site/'data/sovereign-machine-economy.json');docket=load(site/'downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json');manifest=load(site/'sovereign-machine-economy-manifest.json')
 check('release-id',data.get('release_id')=='GOALOS-SOVEREIGN-MACHINE-ECONOMY-001',data.get('release_id'))
 check('release-title',data.get('release_title')=='GoalOS AGIALPHA Ascension — Sovereign Machine Economy',data.get('release_title'))
 check('version',data.get('version')=='1.0.0-civilization',data.get('version'))
 expected={'hero_metrics':6,'presets':5,'postures':4,'risk_profiles':4,'incidents':5,'gates':18,'artifacts':36,'guardians':7,'handoff_rules':6,'claim_boundary':6}
 for key,count in expected.items():check(f'count:{key}',isinstance(data.get(key),list) and len(data[key])==count,len(data.get(key,[])) if isinstance(data.get(key),list) else type(data.get(key)).__name__)
 check('meta-agents',len(data.get('meta',{}).get('agents',[]))==9,len(data.get('meta',{}).get('agents',[])))
 check('node-peers',len(data.get('node',{}).get('peers',[]))==12,len(data.get('node',{}).get('peers',[])))
 check('jobs-institutions',len(data.get('jobs',{}).get('institutions',[]))==12,len(data.get('jobs',{}).get('institutions',[])))
 check('companions-three',len(data.get('companions',[]))==3,[x.get('layer') for x in data.get('companions',[])])
 check('security-authority',data.get('security',{}).get('external_authority')=='none',data.get('security'))
 for key in ['external_dependencies','api_keys','wallet_connection','network_reads','network_writes','local_storage','live_compute','live_token_movement','credential_issuance']:
  check(f'security-false:{key}',data.get('security',{}).get(key) is False,data.get('security',{}).get(key))
 check('docket-schema',docket.get('schema')=='goalos.sovereign_machine_economy.docket.v1',docket.get('schema'))
 check('schema-file-present',schema is None or schema.is_file(),str(schema) if schema else 'not supplied')
 if schema and schema.is_file():
  schema_data=load(schema)
  check('schema-id',str(schema_data.get('$id','')).endswith('sovereign-machine-economy-docket.schema.json'),schema_data.get('$id'))
  check('schema-docket-v1',schema_data.get('properties',{}).get('schema',{}).get('const')=='goalos.sovereign_machine_economy.docket.v1',schema_data.get('properties',{}).get('schema'))
  check('schema-requires-run-commitment','run_commitment' in schema_data.get('required',[]),schema_data.get('required'))
  check('schema-thirty-six-artifacts',schema_data.get('properties',{}).get('evidence',{}).get('properties',{}).get('artifacts',{}).get('maxItems')==36,'')
  check('schema-four-terminal-states',len(schema_data.get('properties',{}).get('authority',{}).get('properties',{}).get('terminal_state',{}).get('enum',[]))==4,'')
  try:
   from jsonschema import Draft202012Validator
   Draft202012Validator.check_schema(schema_data)
   errors=sorted(Draft202012Validator(schema_data).iter_errors(docket),key=lambda e:list(e.path))
   check('json-schema-validation',not errors,[{'path':list(e.path),'message':e.message} for e in errors[:10]])
  except ImportError as exc:
   check('json-schema-validator-installed',False,str(exc))
 chain=docket.get('evidence',{}).get('artifacts',[]);check('docket-36-artifacts',len(chain)==36,len(chain))
 previous='0'*64;valid_chain=True
 for index,item in enumerate(chain):
  if item.get('previous_commitment')!=previous:valid_chain=False;break
  expected_commit=digest({'previous':previous,'payload':item.get('payload')})
  if item.get('commitment')!=expected_commit:valid_chain=False;break
  previous=expected_commit
 check('docket-chain-valid',valid_chain,{'index':index if chain else None,'head':previous})
 check('docket-chain-head',docket.get('evidence',{}).get('chain_head')==previous,docket.get('evidence',{}).get('chain_head'))
 without=dict(docket);run_commitment=without.pop('run_commitment',None);check('docket-run-commitment',run_commitment==digest(without),run_commitment)
 authority=docket.get('authority',{})
 check('terminal-human-review',authority.get('terminal_state')=='HUMAN_SETTLEMENT_REVIEW',authority.get('terminal_state'))
 check('authority-none',authority.get('external_authority')=='NONE_GRANTED',authority.get('external_authority'))
 for key in ['external_actions','network_requests','wallet_connections','live_token_movements']:check(f'authority-zero:{key}',authority.get(key)==0,authority.get(key))
 check('three-handoffs',len(docket.get('handoffs',[]))==3,len(docket.get('handoffs',[])))
 check('handoff-hashes',all(HEX.match(str(x.get('commitment',''))) for x in docket.get('handoffs',[])),docket.get('handoffs'))
 homepage=(site/'index.html').read_text(encoding='utf-8')
 for marker in MARKERS:check(f'homepage-marker:{marker}',homepage.count(marker)==1,homepage.count(marker))
 check('homepage-gateway-once',homepage.count('id="sovereign-machine-economy"')==1,homepage.count('id="sovereign-machine-economy"'))
 check('homepage-nav-once',homepage.count('href="sovereign-machine-economy.html">Machine Economy</a>')==1,homepage.count('href="sovereign-machine-economy.html">Machine Economy</a>'))
 check('homepage-existing-feature-markers',all(marker in homepage for marker in ['GOALOS_META_AGENTIC_ALPHA_AGI_HOME_START','GOALOS_AGI_ALPHA_NODE_V0_HOME_START','GOALOS_AGI_JOBS_V0_V2_HOME_START']), '')
 routes=load(site/'routes.json');check('routes-pages',set(PAGES).issubset(set(routes.get('routes',[]))),routes.get('routes'))
 check('routes-record',routes.get('sovereign_machine_economy',{}).get('external_actions')==0,routes.get('sovereign_machine_economy'))
 sitemap=(site/'sitemap.xml').read_text(encoding='utf-8');check('sitemap-pages',all(page in sitemap for page in PAGES),'')
 status=load(site/'site-status.json');check('status-record',status.get('sovereign_machine_economy',{}).get('proof_artifacts')==36,status.get('sovereign_machine_economy'))
 css=(site/'assets/sovereign-machine-economy.css').read_text(encoding='utf-8');js=(site/'assets/sovereign-machine-economy.js').read_text(encoding='utf-8')
 check('css-responsive','@media(max-width:720px)' in css and '.sme-home-gateway' in css,'')
 check('js-crypto','crypto.subtle.digest("SHA-256"' in js,'')
 check('js-no-fetch',not re.search(r'\bfetch\s*\(',js),'')
 check('js-four-terminals',all(x in js for x in ['HUMAN_SETTLEMENT_REVIEW','HUMAN_REVIEW_REQUIRED','DISPUTE_OPEN','SAFE_HOLD']),'')
 for page in PAGES:
  text=(site/page).read_text(encoding='utf-8')
  check(f'page-title:{page}','Sovereign Machine Economy' in text or 'MACHINE ECONOMY' in text,'')
  check(f'page-local-assets:{page}','assets/sovereign-machine-economy.css' in text and 'assets/sovereign-machine-economy.js' in text,'')
  check(f'page-no-external-runtime:{page}',not re.search(r'<(?:script|link)[^>]+(?:src|href)=["\']https?://',text,re.I),'')
  check(f'page-data:{page}','id="sme-data"' in text,'')
 check('manifest-schema',manifest.get('schema')=='goalos.sovereign_machine_economy.website_manifest.v1',manifest.get('schema'))
 check('manifest-experience',manifest.get('experience',{}).get('constitutional_gates')==18 and manifest.get('experience',{}).get('proof_artifacts')==36,manifest.get('experience'))
 for rel,rec in manifest.get('files',{}).items():
  path=site/rel;check(f'manifest-file:{rel}',path.is_file() and sha(path)==rec.get('sha256') and path.stat().st_size==rec.get('bytes'),rec)
 for name,schema in COMPANIONS.items():
  m=load(site/name);check(f'companion-schema:{name}',m.get('schema')==schema,m.get('schema'))
  check(f'companion-reconciliation:{name}',any(isinstance(x,dict) and x.get('release_id')=='GOALOS-SOVEREIGN-MACHINE-ECONOMY-001' for x in m.get('integration',{}).get('reconciliations',[])),m.get('integration',{}).get('reconciliations',[]))
  for rel,rec in m.get('files',{}).items():
   path=site/rel;check(f'companion-file:{name}:{rel}',path.is_file() and sha(path)==rec.get('sha256') and path.stat().st_size==rec.get('bytes'),rec)
 preservation={}
 if baseline:
  snap=load(baseline);base=snap.get('files',{});current={str(p.relative_to(site)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in site.rglob('*') if p.is_file()}
  removed=sorted(set(base)-set(current));changed=sorted(x for x in set(base)&set(current) if base[x]['sha256']!=current[x]['sha256']);added=sorted(set(current)-set(base))
  unexpected_changed=sorted(set(changed)-ALLOWED_CHANGED);unexpected_added=sorted(x for x in added if x not in NEW and not x.startswith('qa/sovereign-machine-economy'))
  preservation={'removed':removed,'changed':changed,'added':added,'unexpected_changed':unexpected_changed,'unexpected_added':unexpected_added}
  check('preservation-no-removals',not removed,removed);check('preservation-only-declared-changes',not unexpected_changed,unexpected_changed);check('preservation-only-declared-additions',not unexpected_added,unexpected_added);check('preservation-baseline-count',len(base)==snap.get('file_count'),{'listed':len(base),'declared':snap.get('file_count')})
 else:check('preservation-baseline-optional',True,'No baseline supplied')
 failed=[x for x in checks if x['status']=='FAIL'];report={'schema':'goalos.sovereign_machine_economy.static_qa.v1','release_title':'GoalOS AGIALPHA Ascension — Sovereign Machine Economy','status':'PASS' if not failed else 'FAIL','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'preservation':preservation}
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return report
def main()->int:
 root=Path(__file__).resolve().parents[2];ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--site',type=Path,default=root/'site');ap.add_argument('--root',type=Path,default=root);ap.add_argument('--baseline',type=Path);ap.add_argument('--schema',type=Path,default=root/'schemas/sovereign-machine-economy-docket.schema.json');ap.add_argument('--output',type=Path);a=ap.parse_args();output=a.output or a.site/'qa/sovereign-machine-economy-static.json';report=run(a.site.resolve(),a.root.resolve(),a.baseline.resolve() if a.baseline else None,a.schema.resolve() if a.schema else None,output.resolve());print(json.dumps({'status':report['status'],'checks_total':report['checks_total'],'checks_passed':report['checks_passed'],'checks_failed':report['checks_failed'],'output':str(output)},indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
