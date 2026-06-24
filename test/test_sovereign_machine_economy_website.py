from __future__ import annotations
import ast, hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'scripts/website/build_sovereign_machine_economy.py'
SNAPSHOT=ROOT/'scripts/website/snapshot_sovereign_machine_economy_site.py'
VERIFY=ROOT/'scripts/website/verify_sovereign_machine_economy.py'
VISUAL=ROOT/'scripts/website/visual_check_sovereign_machine_economy.py'
CONTENT=ROOT/'content/sovereign-machine-economy.json'
SCHEMA=ROOT/'schemas/sovereign-machine-economy-docket.schema.json'
PAGES=['sovereign-machine-economy.html','sovereign-machine-economy-observatory.html','sovereign-machine-economy-architecture.html','sovereign-machine-economy-ledger.html','sovereign-machine-economy-memory.html','sovereign-machine-economy-passport.html']
DEPENDENCY_PAGES=['meta-agentic-alpha-agi.html','meta-agentic-alpha-agi-architecture.html','agi-alpha-node-v0.html','agi-alpha-node-v0-architecture.html','agi-alpha-node-v0-proof-ledger.html','agi-jobs-v0-v2.html','agi-jobs-v0-v2-market.html','agi-jobs-v0-v2-proof.html','agi-jobs-v0-v2-settlement.html','agi-jobs-v0-v2-architecture.html']
SHARED=['index.html','routes.json','sitemap.xml','site-status.json']

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(value:object)->str:return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))

class SovereignMachineEconomyWebsiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls)->None:
  cls.temp=tempfile.TemporaryDirectory();cls.site=Path(cls.temp.name)/'site';cls.site.mkdir()
  (cls.site/'index.html').write_text("<!doctype html><html><head><title>GoalOS</title></head><body><nav><a href='index.html'>Home</a><!-- GOALOS_AGI_JOBS_V0_V2_NAV_END --></nav><main><section id='existing'>Preserved</section><!-- GOALOS_AGI_JOBS_V0_V2_HOME_END --></main></body></html>",encoding='utf-8')
  (cls.site/'routes.json').write_text(json.dumps({'version':'test','routes':['index.html']})+'\n',encoding='utf-8')
  (cls.site/'sitemap.xml').write_text("<?xml version='1.0'?><urlset></urlset>\n",encoding='utf-8')
  (cls.site/'site-status.json').write_text(json.dumps({'status':'fixture'})+'\n',encoding='utf-8')
  for page in DEPENDENCY_PAGES:(cls.site/page).write_text('<!doctype html><html><body>'+('dependency '+page+' ')*80+'</body></html>',encoding='utf-8')
  manifests=[('meta-agentic-alpha-agi-manifest.json','goalos.meta_agentic_alpha_agi.website_manifest.v2'),('agi-alpha-node-v0-manifest.json','goalos.agi_alpha_node_v0.website_manifest.v2'),('agi-jobs-v0-v2-manifest.json','goalos.agi_jobs_v0_v2.website_manifest.v3')]
  for filename,schema in manifests:
   files={name:{'sha256':sha(cls.site/name),'bytes':(cls.site/name).stat().st_size} for name in SHARED}
   for earlier,_ in manifests:
    if earlier==filename:break
    if (cls.site/earlier).exists():files[earlier]={'sha256':sha(cls.site/earlier),'bytes':(cls.site/earlier).stat().st_size}
   (cls.site/filename).write_text(json.dumps({'schema':schema,'files':files,'integration':{'reconciliations':[]}},indent=2)+'\n',encoding='utf-8')
  cls.baseline=Path(cls.temp.name)/'baseline.json'
  subprocess.run([sys.executable,str(SNAPSHOT),'--site',str(cls.site),'--output',str(cls.baseline)],cwd=ROOT,check=True,capture_output=True,text=True)
  env=dict(os.environ,SOURCE_DATE_EPOCH='1782432000')
  subprocess.run([sys.executable,str(BUILD),'--site',str(cls.site),'--root',str(ROOT)],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
 @classmethod
 def tearDownClass(cls)->None:cls.temp.cleanup()
 def test_01_release_contract_is_exact(self)->None:
  data=json.loads(CONTENT.read_text(encoding='utf-8'));self.assertEqual(data['release_title'],'GoalOS AGIALPHA Ascension Sovereign Machine Economy 👁️⚡️✨');self.assertEqual(data['version'],'2.0.0-constitutional-civilization-engine');self.assertEqual(data['status'],'interactive-constitutional-machine-economy-civilization-engine');self.assertEqual(data['doctrine'],'Minds are formed. Nodes execute. Markets coordinate. Proof earns permission. Humans authorize.')
 def test_02_constitutional_depth_is_complete(self)->None:
  data=json.loads(CONTENT.read_text(encoding='utf-8'));expected={'source_releases':3,'hero_metrics':6,'thesis':7,'mission_presets':8,'postures':4,'risk_profiles':4,'incidents':8,'gates':21,'handoffs':15,'artifact_classes':48,'governance_principles':10,'threats':10,'memory_rules':9,'review_actions':4,'universes':3,'constitutional_rights':8,'claim_boundary':10}
  for key,count in expected.items():self.assertEqual(len(data[key]),count,key)
  self.assertEqual([x['id'] for x in data['gates']],[f'G{i:02d}' for i in range(1,22)]);self.assertEqual([x['id'] for x in data['handoffs']],[f'H{i:02d}' for i in range(1,16)])
 def test_03_security_is_default_deny(self)->None:
  security=json.loads(CONTENT.read_text(encoding='utf-8'))['security']
  for key in ['external_dependencies','api_keys','wallet_connection','network_reads','network_writes','live_model_calls','live_compute','live_token_movement','credential_issuance','local_storage']:self.assertIs(security[key],False,key)
  self.assertTrue(security['human_review_required']);self.assertEqual(security['external_authority'],'none')
 def test_04_build_outputs_six_public_surfaces(self)->None:
  for page in PAGES:self.assertGreater((self.site/page).stat().st_size,2000,page)
  for relative in ['assets/sovereign-machine-economy.css','assets/sovereign-machine-economy.js','data/sovereign-machine-economy.json','downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json','downloads/sovereign-machine-economy/sovereign-machine-economy-executive-brief.md','sovereign-machine-economy-manifest.json','qa/sovereign-machine-economy-build.json']:self.assertTrue((self.site/relative).is_file(),relative)
 def test_05_homepage_and_discovery_are_additive(self)->None:
  homepage=(self.site/'index.html').read_text(encoding='utf-8');self.assertIn("<section id='existing'>Preserved</section>",homepage)
  for marker in ['GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_START','GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_START','GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_START']:self.assertEqual(homepage.count(marker),1,marker)
  self.assertEqual(homepage.count('href="sovereign-machine-economy.html">Machine Economy Ω</a>'),1);self.assertEqual(homepage.count('id="sovereign-machine-economy"'),1);self.assertIn('21 proof gates',homepage);self.assertIn('48 evidence artifacts',homepage)
  routes=json.loads((self.site/'routes.json').read_text());self.assertTrue(set(PAGES).issubset(routes['routes']));self.assertEqual(routes['sovereign_machine_economy']['constitutional_gates'],21);self.assertEqual(routes['sovereign_machine_economy']['handoffs'],15);self.assertEqual(routes['sovereign_machine_economy']['artifacts'],48)
  full_status=json.loads((self.site/'site-status.json').read_text());status=full_status['sovereign_machine_economy'];self.assertEqual(status['counterfactual_universes'],3);self.assertEqual(status['human_review_actions'],4);self.assertEqual(full_status['root_html_pages'],len(list(self.site.glob('*.html'))));self.assertEqual(full_status['published_html_pages_including_resources'],len(list(self.site.rglob('*.html'))))
 def test_06_sample_docket_has_fifteen_valid_handoffs(self)->None:
  d=json.loads((self.site/'downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json').read_text());previous='0'*64;self.assertEqual(len(d['handoffs']),15)
  for i,item in enumerate(d['handoffs'],1):
   self.assertEqual(item['id'],f'H{i:02d}');self.assertEqual(item['previous_commitment'],previous);payload={'id':item['id'],'from':item['from'],'to':item['to'],'name':item['name'],'mission':d['mission']['mission'],'institution':d['institution']['id'],'node':d['node']['id'],'market':d['market']['id'],'previous':previous};previous=hashlib.sha256(stable(payload).encode()).hexdigest();self.assertEqual(item['commitment'],previous)
 def test_07_sample_docket_has_valid_forty_eight_link_chain(self)->None:
  d=json.loads((self.site/'downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json').read_text());previous='0'*64;self.assertEqual(len(d['evidence']['artifacts']),48);self.assertEqual([x['plane'] for x in d['evidence']['artifacts']].count('MIND'),16);self.assertEqual([x['plane'] for x in d['evidence']['artifacts']].count('NODE'),16);self.assertEqual([x['plane'] for x in d['evidence']['artifacts']].count('MARKET'),16)
  for i,item in enumerate(d['evidence']['artifacts'],1):
   self.assertEqual(item['id'],f'A{i:02d}');self.assertEqual(item['previous_commitment'],previous);artifact_hash=hashlib.sha256(stable(item['payload']).encode()).hexdigest();self.assertEqual(item['artifact_hash'],artifact_hash);previous=hashlib.sha256(stable({'previous':previous,'payload':item['payload'],'artifact_hash':artifact_hash}).encode()).hexdigest();self.assertEqual(item['commitment'],previous)
  self.assertEqual(d['evidence']['chain_head'],previous)
 def test_08_counterfactual_observatory_preserves_constitutional_invariants(self)->None:
  d=json.loads((self.site/'downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json').read_text());self.assertEqual([x['id'] for x in d['counterfactuals']],['prudential','balanced','frontier']);self.assertTrue(all(x['terminal_state']=='HUMAN_SETTLEMENT_REVIEW' and x['authority']=='NONE_GRANTED' and x['external_actions']==0 for x in d['counterfactuals']));self.assertEqual(len({x['commitment'] for x in d['counterfactuals']}),3)
 def test_09_human_authority_dissent_and_memory_are_preserved(self)->None:
  d=json.loads((self.site/'downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json').read_text());self.assertEqual(d['market']['parliament']['dissent'],1);dissent=[x for x in d['market']['parliament']['opinions'] if x['verdict']=='DISSENT'];self.assertEqual(len(dissent),1);self.assertEqual(d['review']['status'],'PENDING_HUMAN_REVIEW');self.assertEqual(len(d['review']['available_actions']),4);self.assertFalse(d['review']['authority_granted']);self.assertFalse(d['review']['settlement_authorized']);self.assertFalse(d['review']['memory_promoted']);self.assertEqual(d['authority']['external_authority'],'NONE_GRANTED');self.assertEqual(d['authority']['automatic_memory_promotion'],'NOT_AUTHORIZED');self.assertEqual(d['memory']['status'],'HUMAN_PROMOTION_REQUIRED');self.assertTrue(d['memory']['failure_memory_preserved'])
 def test_10_observatory_passport_and_review_chamber_are_public(self)->None:
  experience=(self.site/'sovereign-machine-economy.html').read_text();observatory=(self.site/'sovereign-machine-economy-observatory.html').read_text();passport=(self.site/'sovereign-machine-economy-passport.html').read_text();self.assertIn('sme-review-chamber',experience);self.assertIn('sme-universe-preview',experience);self.assertIn('sme-run-universes',observatory);self.assertIn('sme-comparison-table',observatory);self.assertIn('sme-passport-file',passport);self.assertIn('sme-passport-glyph',passport)
 def test_11_manifest_hashes_every_declared_output(self)->None:
  manifest=json.loads((self.site/'sovereign-machine-economy-manifest.json').read_text());self.assertEqual(manifest['schema'],'goalos.sovereign_machine_economy.website_manifest.v2')
  for relative,record in manifest['files'].items():self.assertEqual(record['sha256'],sha(self.site/relative),relative);self.assertEqual(record['bytes'],(self.site/relative).stat().st_size,relative)
 def test_12_static_verifier_and_preservation_pass(self)->None:
  out=Path(self.temp.name)/'static.json';result=subprocess.run([sys.executable,str(VERIFY),'--site',str(self.site),'--root',str(ROOT),'--content',str(CONTENT),'--schema',str(SCHEMA),'--baseline',str(self.baseline),'--output',str(out)],cwd=ROOT,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr);report=json.loads(out.read_text());self.assertEqual(report['status'],'PASS');self.assertFalse(report['preservation']['removed']);self.assertFalse(report['preservation']['unexpected_changed']);self.assertFalse(report['preservation']['unexpected_added'])
 def test_13_second_build_is_byte_identical(self)->None:
  before={p.relative_to(self.site).as_posix():sha(p) for p in self.site.rglob('*') if p.is_file() and not p.as_posix().endswith('sovereign-machine-economy-static.json')};env=dict(os.environ,SOURCE_DATE_EPOCH='1782432000');subprocess.run([sys.executable,str(BUILD),'--site',str(self.site),'--root',str(ROOT)],cwd=ROOT,env=env,check=True,capture_output=True,text=True);after={p.relative_to(self.site).as_posix():sha(p) for p in self.site.rglob('*') if p.is_file() and not p.as_posix().endswith('sovereign-machine-economy-static.json')};self.assertEqual(before,after)
 def test_14_python311_and_javascript_preflights_pass(self)->None:
  for path in [BUILD,SNAPSHOT,VERIFY,VISUAL,Path(__file__)]:ast.parse(path.read_text(encoding='utf-8'),filename=str(path),feature_version=(3,11))
  result=subprocess.run(['node','--check',str(ROOT/'website/features/sovereign-machine-economy/assets/sovereign-machine-economy.js')],cwd=ROOT,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
 def test_15_runtime_has_no_network_or_storage_apis(self)->None:
  js=(ROOT/'website/features/sovereign-machine-economy/assets/sovereign-machine-economy.js').read_text();self.assertNotIn('fetch(',js);self.assertNotIn('XMLHttpRequest',js);self.assertNotIn('WebSocket(',js);self.assertNotIn('localStorage',js);self.assertNotIn('sessionStorage',js);self.assertIn('window.__SME_STATE__',js);self.assertIn('function sha256',js);self.assertIn('runUniverses',js);self.assertIn('applyReviewAction',js);self.assertIn('renderPassport',js)
 def test_16_all_three_exact_release_titles_are_public(self)->None:
  homepage=(self.site/'index.html').read_text(encoding='utf-8');experience=(self.site/PAGES[0]).read_text(encoding='utf-8')
  for title in ['META-AGENTIC α‑AGI','AGI Alpha Node v0','AGI Jobs v0 (v2)']:self.assertTrue(title in homepage or title in experience,title)

if __name__=='__main__':unittest.main()
