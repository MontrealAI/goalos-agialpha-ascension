from __future__ import annotations
import json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content/proof-mission-008-open-future.json'
MAINNET=ROOT/'data/mainnet/v4.4.0-mainnet-2026-06-21.json'
BUILDERS=['build_proof_gradient_sovereign.py','build_proof_mission_002.py','build_proof_mission_003.py','build_proof_mission_004.py','build_proof_mission_005.py','build_proof_mission_006.py','build_proof_mission_007.py','build_proof_mission_008.py']

def load(path): return json.loads(Path(path).read_text())
def run(command):
 r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
 if r.returncode: raise AssertionError(r.stdout+'\n'+r.stderr)

class ProofMission008Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=Path(tempfile.mkdtemp(prefix='goalos-m8-test-')); cls.site=cls.tmp/'site'
  run([sys.executable,'scripts/build_goalos_agialpha_ascension_website_v86.py','--out',str(cls.site)])
  for builder in BUILDERS: run([sys.executable,'scripts/website/'+builder,'--site',str(cls.site)])
 @classmethod
 def tearDownClass(cls): shutil.rmtree(cls.tmp)
 def test_identity_status_and_horizon(self):
  c=load(CONTENT); self.assertEqual(c['missionId'],'GOALOS-PUBLIC-PROOF-MISSION-008'); self.assertEqual(c['sequence'],8); self.assertEqual(c['status'],'PROTOCOL_PUBLISHED_AWAITING_THREE_STEWARDSHIP_PROVEN_COVENANTS'); self.assertEqual(c['mission9']['status'],'HORIZON_ONLY_NOT_YET_AUTHORIZED')
 def test_constitution_budget_and_settlement(self):
  c=load(CONTENT); b=c['missionBudget']; self.assertEqual(len(c['constitution']),3); self.assertEqual(len(c['optionalityTrial']['gates']),9); self.assertEqual(b['validatorQuorum'],9); self.assertEqual(b['publicChallengeWindowHours'],2160); self.assertEqual(sum(x['share'] for x in c['settlement']),100)
 def test_proof_route_uses_all_goalos_contracts(self):
  c=load(CONTENT); m=load(MAINNET); names={x['name'] for x in m['contracts'] if x['name']!='AGIALPHA'}; route={x['contractName'] for x in c['proofRoute']}; self.assertEqual(len(c['proofRoute']),48); self.assertEqual(route,names); self.assertEqual(m['verification']['verified'],48); self.assertEqual(m['verification']['failed'],0); self.assertTrue(m['verification']['complete']); self.assertEqual(m['phaseBGrantCount'],14); self.assertEqual(m['postcheck']['status'],'PASSED')
 def test_no_named_competitor_or_predeclared_result(self):
  text=CONTENT.read_text().lower()
  for token in ('recursive.com','recursive org','recursive-style','named competitor'): self.assertNotIn(token,text)
  c=load(CONTENT); self.assertIn('AWAITING',c['status']); self.assertTrue(any('not evidence' in x.lower() for x in c['claimBoundaries'])); self.assertNotEqual(c['maturity']['designation'],c['status'])
 def test_build_generates_complete_experience(self):
  page=(self.site/'proof-mission-008.html').read_text(); hub=(self.site/'proof-missions.html').read_text(); self.assertIn('THE <span>OPEN FUTURE</span>',page); self.assertEqual(page.count('class="of-route route-item"'),48); self.assertIn('The Open Future',hub); self.assertTrue((self.site/'downloads/proof-missions/public-proof-mission-008.json').exists()); self.assertTrue((self.site/'downloads/proof-missions/mission-008-proof-route.csv').exists())
 def test_builder_records_preservation_and_promotion(self):
  r=load(self.site/'qa/proof-mission-008-build.json'); self.assertTrue(r['mission001To006Preserved']); self.assertTrue(r['mission007HorizonPromoted']); self.assertFalse(r['publicNetworkTransactionSent'])
 def test_homepage_has_one_marked_full_bleed_series_panel(self):
  h=(self.site/'index.html').read_text(); self.assertEqual(h.count('<!-- GOALOS_PROOF_MISSION_008_START -->'),1); self.assertEqual(h.count('<!-- GOALOS_PROOF_MISSION_008_END -->'),1); self.assertEqual(h.count('PUBLIC PROOF MISSION 008'),1)
  self.assertIn('data-proof-mission-series="sovereign"',h); self.assertIn('data-proof-mission="008"',h)
  self.assertEqual(h.count('class="of-home-stat"'),4); self.assertIn('href="proof-mission-008.html#mainnet"',h)
  self.assertIn('.of-home{margin:0!important;max-width:none!important;width:100%!important',h)
  self.assertNotIn('.of-home{margin:2rem auto;max-width:1180px',h)
 def test_templates_are_not_evidence(self):
  paths=list((self.site/'downloads/proof-missions').glob('mission-008-*-template.json')); self.assertEqual(len(paths),5)
  for p in paths: self.assertEqual(load(p)['status'],'TEMPLATE_NOT_EVIDENCE')
 def test_mission007_is_changed_only_by_horizon_promotion(self):
  m7=(self.site/'proof-mission-007.html').read_text(); self.assertIn('PUBLIC PROOF MISSION 008 · NOW PUBLISHED',m7); self.assertIn('<!-- GOALOS_PROOF_MISSION_008_PROMOTION_START -->',m7)
 def test_optionality_and_irreversibility_requirements_are_explicit(self):
  c=load(CONTENT); joined=' '.join(c['acceptance']).lower(); self.assertIn('strategic options',joined); self.assertIn('irreversibility',json.dumps(c).lower()); self.assertIn('abstains',joined); self.assertIn('dissolves',joined)
 def test_full_verifier_passes_without_network_or_broadcast(self):
  run([sys.executable,'scripts/website/verify_proof_mission_008.py','--site',str(self.site),'--repo','.']); r=load(self.site/'qa/proof-mission-008-verification.json'); self.assertEqual(r['status'],'PASS'); self.assertFalse(r['publicNetworkTransactionSent'])

if __name__=='__main__': unittest.main()
