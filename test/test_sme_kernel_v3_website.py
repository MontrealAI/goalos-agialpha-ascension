from __future__ import annotations
import ast, hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'scripts/website/build_sme_kernel_v3.py';SNAPSHOT=ROOT/'scripts/website/snapshot_sme_kernel_v3_site.py';VERIFY=ROOT/'scripts/website/verify_sme_kernel_v3.py';VISUAL=ROOT/'scripts/website/visual_check_sme_kernel_v3.py'
CONTENT=ROOT/'content/sme-kernel-v3.json';ENV_SCHEMA=ROOT/'schemas/sme-kernel-v3-envelope.schema.json';BUNDLE_SCHEMA=ROOT/'schemas/sme-kernel-v3-mission-bundle.schema.json'
PAGES=['sovereign-machine-economy-kernel-v3.html','sovereign-machine-economy-kernel-v3-protocol.html','sovereign-machine-economy-kernel-v3-chronicle.html','sovereign-machine-economy-kernel-v3-verifier.html','sovereign-machine-economy-kernel-v3-sdk.html']
SHARED=['index.html','routes.json','sitemap.xml','site-status.json']
COMPANIONS=[('meta-agentic-alpha-agi-manifest.json','goalos.meta_agentic_alpha_agi.website_manifest.v2'),('agi-alpha-node-v0-manifest.json','goalos.agi_alpha_node_v0.website_manifest.v2'),('agi-jobs-v0-v2-manifest.json','goalos.agi_jobs_v0_v2.website_manifest.v3'),('sovereign-machine-economy-manifest.json','goalos.sovereign_machine_economy.website_manifest.v2')]
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

class SMEKernelV3WebsiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls)->None:
  cls.temp=tempfile.TemporaryDirectory();cls.site=Path(cls.temp.name)/'site';cls.site.mkdir()
  index="<!doctype html><html><head><link rel='stylesheet' href='assets/goalos-v86-preserve.css'></head><body><nav><a href='index.html'>Home</a><!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_END --></nav><main><section id='preserved'>Preserved</section><!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_END --></main></body></html>"
  (cls.site/'index.html').write_text(index,encoding='utf-8');(cls.site/'routes.json').write_text(json.dumps({'version':'test','routes':['index.html']})+'\n');(cls.site/'sitemap.xml').write_text("<?xml version='1.0'?><urlset></urlset>\n");(cls.site/'site-status.json').write_text(json.dumps({'status':'fixture'})+'\n')
  (cls.site/'assets').mkdir();(cls.site/'assets/goalos-v86-preserve.css').write_text('body{margin:0}\n')
  for page in ['meta-agentic-alpha-agi.html','agi-alpha-node-v0.html','agi-jobs-v0-v2.html','sovereign-machine-economy.html']:(cls.site/page).write_text('<!doctype html><html><body>'+page*80+'</body></html>')
  for filename,schema in COMPANIONS:
   files={name:{'sha256':sha(cls.site/name),'bytes':(cls.site/name).stat().st_size} for name in SHARED}
   (cls.site/filename).write_text(json.dumps({'schema':schema,'files':files,'integration':{'reconciliations':[]}},indent=2)+'\n')
  cls.baseline=Path(cls.temp.name)/'baseline.json';subprocess.run([sys.executable,str(SNAPSHOT),'--site',str(cls.site),'--output',str(cls.baseline)],cwd=ROOT,check=True,capture_output=True,text=True)
  env=dict(os.environ,SOURCE_DATE_EPOCH='1782259200');subprocess.run([sys.executable,str(BUILD),'--site',str(cls.site),'--root',str(ROOT)],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
 @classmethod
 def tearDownClass(cls)->None:cls.temp.cleanup()
 def test_01_release_contract(self):
  data=json.loads(CONTENT.read_text());self.assertEqual(data['release_title'],'GoalOS AGIALPHA Ascension Sovereign Machine Economy Kernel v3 ⚙️✨');self.assertEqual(data['version'],'3.0.0-executable-constitutional-kernel');self.assertEqual(data['status'],'executable-browser-local-constitutional-kernel')
 def test_02_constitutional_depth(self):
  d=json.loads(CONTENT.read_text());expected={'hero_metrics':6,'roles':5,'states':17,'envelope_types':10,'adapter_contract':6,'adapters':3,'presets':6,'postures':3,'risks':3,'incidents':5,'review_actions':4,'invariants':10,'threat_controls':8,'claim_boundary':6}
  for key,count in expected.items():self.assertEqual(len(d[key]),count,key)
 def test_03_security_default_deny(self):
  s=json.loads(CONTENT.read_text())['security'];
  for key in ['external_dependencies','api_keys','wallet_connection','network_reads','network_writes','live_model_calls','live_compute','live_token_movement','credential_issuance','automatic_memory_promotion']:self.assertIs(s[key],False,key)
  self.assertEqual(s['signature_algorithm'],'Ed25519');self.assertTrue(s['worker_isolation']);self.assertTrue(s['human_review_required'])
 def test_04_all_public_surfaces_exist(self):
  for page in PAGES:self.assertGreater((self.site/page).stat().st_size,5500,page)
  for relative in ['assets/sme-kernel-v3.css','assets/sme-kernel-v3.js','assets/sme-kernel-v3-core.js','assets/sme-kernel-v3-adapters.js','assets/sme-kernel-v3-worker.js','data/sme-kernel-v3.json','sme-kernel-v3-manifest.json']:self.assertTrue((self.site/relative).is_file(),relative)
 def test_05_homepage_additive(self):
  raw=(self.site/'index.html').read_text();self.assertIn("<section id='preserved'>Preserved</section>",raw);self.assertEqual(raw.count('GOALOS_SME_KERNEL_V3_HOME_START'),1);self.assertEqual(raw.count('GOALOS_SME_KERNEL_V3_NAV_START'),1);self.assertEqual(raw.count('GOALOS_SME_KERNEL_V3_STYLE_START'),1);self.assertEqual(raw.count('data-goalos-sme-kernel-v3-icon'),1);self.assertIn('Kernel v3',raw)
 def test_06_routes_status_and_sitemap(self):
  routes=json.loads((self.site/'routes.json').read_text());self.assertTrue(set(PAGES).issubset(routes['routes']));self.assertEqual(routes['sme_kernel_v3']['states'],17);self.assertEqual(routes['sme_kernel_v3']['signature'],'Ed25519');status=json.loads((self.site/'site-status.json').read_text())['sme_kernel_v3'];self.assertEqual(status['typed_envelopes'],10);self.assertTrue(status['worker_isolated']);sitemap=(self.site/'sitemap.xml').read_text();self.assertTrue(all(page in sitemap for page in PAGES))
 def test_07_protocol_manifest_root(self):
  p=json.loads((self.site/'downloads/sme-kernel-v3/sme-kernel-v3-protocol-manifest.json').read_text());root=p.pop('protocol_root');self.assertEqual(root,hashlib.sha256(json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest())
 def test_08_manifest_hashes_outputs(self):
  m=json.loads((self.site/'sme-kernel-v3-manifest.json').read_text());self.assertEqual(m['schema'],'goalos.sme.kernel.v3.website_manifest.v1')
  for relative,record in m['files'].items():self.assertEqual(record['sha256'],sha(self.site/relative),relative);self.assertEqual(record['bytes'],(self.site/relative).stat().st_size,relative)
 def test_09_companion_manifests_reconciled(self):
  release='GOALOS-AGIALPHA-SME-KERNEL-V3-001'
  for filename,schema in COMPANIONS:
   m=json.loads((self.site/filename).read_text());self.assertEqual(m['schema'],schema);self.assertTrue(any(x.get('release_id')==release for x in m['integration']['reconciliations']))
   for relative in SHARED:self.assertEqual(m['files'][relative]['sha256'],sha(self.site/relative))
 def test_10_static_verifier_and_preservation(self):
  out=Path(self.temp.name)/'static.json';result=subprocess.run([sys.executable,str(VERIFY),'--site',str(self.site),'--root',str(ROOT),'--content',str(CONTENT),'--envelope-schema',str(ENV_SCHEMA),'--bundle-schema',str(BUNDLE_SCHEMA),'--baseline',str(self.baseline),'--output',str(out)],cwd=ROOT,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr);report=json.loads(out.read_text());self.assertEqual(report['status'],'PASS');self.assertFalse(report['preservation']['removed']);self.assertFalse(report['preservation']['unexpected_changed']);self.assertFalse(report['preservation']['unexpected_added'])
 def test_11_core_ed25519_roundtrip(self):
  script="""global.window=global;global.crypto=require('crypto').webcrypto;require('./website/features/sme-kernel-v3/assets/sme-kernel-v3-core.js');(async()=>{const c=SMEKernelCore;const id=await c.generateIdentity('META_ARCHITECT');const u=await c.createUnsignedEnvelope({envelopeType:'InstitutionProposal',missionId:'mission-1234567890abcdef',issuer:'META_ARCHITECT',logicalTime:1,previousCommitment:'0'.repeat(64),payload:{proof:'bounded'},authorityScope:'TEST'});const e=await c.signEnvelope(u,id);const v=await c.verifyEnvelope(e);if(!v.ok)process.exit(2);e.payload.proof='tampered';const bad=await c.verifyEnvelope(e);if(bad.ok)process.exit(3);console.log('PASS')})().catch(e=>{console.error(e);process.exit(1)});"""
  result=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn('PASS',result.stdout)
 def test_12_adapter_contract(self):
  raw=(ROOT/'website/features/sme-kernel-v3/assets/sme-kernel-v3-adapters.js').read_text()
  for name in ['initialize','propose','execute','evaluate','produceEvidence','verifyEvidence','MetaAgenticAdapter','AlphaNodeAdapter','AGIJobsAdapter']:self.assertIn(name,raw)
 def test_13_worker_isolated_durable_and_no_network(self):
  raw=(ROOT/'website/features/sme-kernel-v3/assets/sme-kernel-v3-worker.js').read_text();self.assertIn('indexedDB.open',raw);self.assertIn('importScripts',raw);self.assertIn('applyHumanReview',raw);self.assertIn('exportMission',raw)
  for token in ['fetch(','XMLHttpRequest','WebSocket(','localStorage','sessionStorage']:self.assertNotIn(token,raw)
 def test_14_second_build_is_idempotent(self):
  before={p.relative_to(self.site).as_posix():sha(p) for p in self.site.rglob('*') if p.is_file() and p.name!='sme-kernel-v3-static.json'};env=dict(os.environ,SOURCE_DATE_EPOCH='1782259200');subprocess.run([sys.executable,str(BUILD),'--site',str(self.site),'--root',str(ROOT)],cwd=ROOT,env=env,check=True,capture_output=True,text=True);after={p.relative_to(self.site).as_posix():sha(p) for p in self.site.rglob('*') if p.is_file() and p.name!='sme-kernel-v3-static.json'};self.assertEqual(before,after)
 def test_15_python311_and_javascript_preflight(self):
  for path in [BUILD,SNAPSHOT,VERIFY,VISUAL,Path(__file__)]:
   if path.exists():ast.parse(path.read_text(),filename=str(path),feature_version=(3,11))
  for name in ['sme-kernel-v3-core.js','sme-kernel-v3-adapters.js','sme-kernel-v3-worker.js','sme-kernel-v3.js']:
   result=subprocess.run(['node','--check',str(ROOT/'website/features/sme-kernel-v3/assets'/name)],cwd=ROOT,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
 def test_16_schemas_are_valid(self):
  import jsonschema
  jsonschema.Draft202012Validator.check_schema(json.loads(ENV_SCHEMA.read_text()));jsonschema.Draft202012Validator.check_schema(json.loads(BUNDLE_SCHEMA.read_text()))

if __name__=='__main__':unittest.main()
