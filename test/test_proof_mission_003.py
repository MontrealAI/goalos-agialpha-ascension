import csv,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class ProofMission003Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=Path(tempfile.mkdtemp()); cls.site=cls.tmp/'site'
        for cmd in [
            ['python3','scripts/build_goalos_agialpha_ascension_website_v86.py','--out',str(cls.site)],
            ['python3','scripts/website/build_proof_gradient_sovereign.py','--site',str(cls.site)],
            ['python3','scripts/website/build_proof_mission_002.py','--site',str(cls.site)],
            ['python3','scripts/website/build_proof_mission_003.py','--site',str(cls.site)],
        ]: subprocess.run(cmd,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    @classmethod
    def tearDownClass(cls): shutil.rmtree(cls.tmp)
    def test_additive_idempotent_and_canonical_source_preserved(self):
        original=(ROOT/'website/v86_actual_site/index.html').read_bytes(); first=(self.site/'index.html').read_bytes()
        subprocess.run(['python3','scripts/website/build_proof_mission_003.py','--site',str(self.site)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        self.assertEqual(first,(self.site/'index.html').read_bytes()); self.assertEqual(original,(ROOT/'website/v86_actual_site/index.html').read_bytes())
    def test_mission_contract_is_complete_and_claim_bounded(self):
        c=json.loads((ROOT/'content/proof-mission-003-capability-constellation.json').read_text())
        self.assertEqual(c['sequence'],3); self.assertEqual(c['status'],'PROTOCOL_PUBLISHED_AWAITING_THREE_TRANSFER_PROVEN_CAPABILITIES')
        self.assertEqual(sum(x['share'] for x in c['settlement']),100); self.assertEqual(len(c['proofRoute']),24); self.assertEqual(len(c['validators']),4)
        page=(self.site/'proof-mission-003.html').read_text().lower(); self.assertIn('no result predeclared',page); self.assertIn('cannot begin scientifically until at least three capabilities',page)
    def test_missions_one_and_two_are_preserved(self):
        self.assertTrue((self.site/'proof-gradient-challenge.html').exists()); self.assertTrue((self.site/'proof-mission-002.html').exists())
        hub=(self.site/'proof-missions.html').read_text(); self.assertEqual(hub.count('class="pm-card'),3)
        for href in ['proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html']: self.assertIn(href,hub)
        home=(self.site/'index.html').read_text()
        for marker in ['GOALOS_PROOF_GRADIENT_SOVEREIGN_START','GOALOS_PROOF_MISSION_002_START','GOALOS_PROOF_MISSION_003_START']: self.assertEqual(home.count(f'<!-- {marker} -->'),1)
    def test_public_content_has_no_named_competitor_reference(self):
        text='\n'.join((self.site/p).read_text().lower() for p in ['proof-mission-003.html','proof-missions.html','index.html'])
        for term in ['recursive.com','recursive org','recursive-style','competitor comparison','named competitor']: self.assertNotIn(term,text)
    def test_templates_are_not_evidence_and_route_matches_mainnet(self):
        d=self.site/'downloads/proof-missions'
        for name in ['mission-003-constellation-manifest-template.json','mission-003-interface-covenant-template.json','mission-003-fault-domain-register-template.json']:
            self.assertEqual(json.loads((d/name).read_text())['status'],'TEMPLATE_NOT_EVIDENCE')
        with (d/'mission-003-proof-route.csv').open(encoding='utf-8') as handle:
            rows=list(csv.DictReader(handle))
        self.assertEqual(len(rows),24)
        mainnet=json.loads((ROOT/'data/mainnet/v4.4.0-mainnet-2026-06-21.json').read_text()); by={x['name']:x['address'].lower() for x in mainnet['contracts']}
        for row in rows: self.assertEqual(by[row['contract']],row['address'].lower())
    def test_verifier_passes(self):
        r=subprocess.run(['python3','scripts/website/verify_proof_mission_003.py','--site',str(self.site)],cwd=ROOT)
        self.assertEqual(r.returncode,0)

if __name__=='__main__': unittest.main()
