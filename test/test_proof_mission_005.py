import csv,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProofMission005Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=Path(tempfile.mkdtemp()); cls.site=cls.tmp/'site'
  cmds=[['python3','scripts/build_goalos_agialpha_ascension_website_v86.py','--out',str(cls.site)],['python3','scripts/website/build_proof_gradient_sovereign.py','--site',str(cls.site)],['python3','scripts/website/build_proof_mission_002.py','--site',str(cls.site)],['python3','scripts/website/build_proof_mission_003.py','--site',str(cls.site)],['python3','scripts/website/build_proof_mission_004.py','--site',str(cls.site)],['python3','scripts/website/build_proof_mission_005.py','--site',str(cls.site)]]
  for c in cmds: subprocess.run(c,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 @classmethod
 def tearDownClass(cls): shutil.rmtree(cls.tmp)
 def test_additive_idempotent_and_canonical_source_preserved(self):
  original=(ROOT/'website/v86_actual_site/index.html').read_bytes(); first=(self.site/'index.html').read_bytes()
  subprocess.run(['python3','scripts/website/build_proof_mission_005.py','--site',str(self.site)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  self.assertEqual(first,(self.site/'index.html').read_bytes()); self.assertEqual(original,(ROOT/'website/v86_actual_site/index.html').read_bytes())
 def test_mission_contract_is_complete_and_claim_bounded(self):
  c=json.loads((ROOT/'content/proof-mission-005-interinstitutional-accord.json').read_text())
  self.assertEqual(c['sequence'],5); self.assertEqual(c['status'],'PROTOCOL_PUBLISHED_AWAITING_THREE_INSTITUTION_PROVEN_MEMBERS'); self.assertEqual(sum(x['share'] for x in c['settlement']),100); self.assertEqual(len(c['proofRoute']),40); self.assertEqual(len(c['validators']),6); self.assertEqual(c['missionBudget']['challengeWindowHours'],504)
  p=(self.site/'proof-mission-005.html').read_text().lower(); self.assertIn('no federation result predeclared',p); self.assertIn('cannot begin scientifically until at least three institutions',p); self.assertIn('does not establish successful federation',p)
 def test_missions_one_to_four_preserved_and_hub_has_five(self):
  for p in ['proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-mission-004.html','proof-mission-005.html']: self.assertTrue((self.site/p).exists())
  h=(self.site/'proof-missions.html').read_text(); self.assertEqual(h.count('class="pm-card'),5)
  for x in ['proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-mission-004.html','proof-mission-005.html']: self.assertIn(x,h)
 def test_mission_four_horizon_promoted(self):
  p=(self.site/'proof-mission-004.html').read_text(); self.assertIn('PUBLIC PROOF MISSION 005 · NOW PUBLISHED',p); self.assertIn('proof-mission-005.html',p); self.assertNotIn('MISSION 005 HORIZON',p); self.assertIn('The Sovereign Institution',p)
 def test_homepage_contains_exactly_one_panel_per_mission(self):
  h=(self.site/'index.html').read_text()
  for m in ['GOALOS_PROOF_GRADIENT_SOVEREIGN_START','GOALOS_PROOF_MISSION_002_START','GOALOS_PROOF_MISSION_003_START','GOALOS_PROOF_MISSION_004_START','GOALOS_PROOF_MISSION_005_START']: self.assertEqual(h.count(f'<!-- {m} -->'),1)
 def test_public_content_has_no_named_competitor_or_private_material(self):
  t='\n'.join((self.site/p).read_text().lower() for p in ['proof-mission-005.html','proof-missions.html','index.html','proof-mission-004.html'])
  for x in ['recursive.com','recursive org','recursive-style','competitor comparison','named competitor','private_mainnet_deployer_private_key','mainnet_rpc_url=','etherscan_api_key=']: self.assertNotIn(x,t)
 def test_templates_and_route(self):
  d=self.site/'downloads/proof-missions'
  for n in ['mission-005-commonwealth-treaty-template.json','mission-005-reciprocal-obligation-ledger-template.json','mission-005-dispute-appeal-template.json','mission-005-member-exit-template.json']: self.assertEqual(json.loads((d/n).read_text())['status'],'TEMPLATE_NOT_EVIDENCE')
  with (d/'mission-005-proof-route.csv').open(encoding='utf-8') as handle: rows=list(csv.DictReader(handle))
  self.assertEqual(len(rows),40)
  m=json.loads((ROOT/'data/mainnet/v4.4.0-mainnet-2026-06-21.json').read_text()); by={x['name']:x['address'].lower() for x in m['contracts']}
  for r in rows: self.assertEqual(by[r['contract']],r['address'].lower())
 def test_verifier_passes(self):
  r=subprocess.run(['python3','scripts/website/verify_proof_mission_005.py','--site',str(self.site)],cwd=ROOT); self.assertEqual(r.returncode,0)
if __name__=='__main__': unittest.main()
