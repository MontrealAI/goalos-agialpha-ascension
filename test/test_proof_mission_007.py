from __future__ import annotations
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content/proof-mission-007-civilizational-covenant.json'
MAINNET = ROOT / 'data/mainnet/v4.4.0-mainnet-2026-06-21.json'
BUILDERS = [
    'build_proof_gradient_sovereign.py', 'build_proof_mission_002.py',
    'build_proof_mission_003.py', 'build_proof_mission_004.py',
    'build_proof_mission_005.py', 'build_proof_mission_006.py',
    'build_proof_mission_007.py',
]

def load(path):
    return json.loads(Path(path).read_text())

def run(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stdout + '\n' + result.stderr)

class ProofMission007Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='goalos-m7-test-'))
        cls.site = cls.tmp / 'site'
        run([sys.executable, 'scripts/build_goalos_agialpha_ascension_website_v86.py', '--out', str(cls.site)])
        for builder in BUILDERS:
            run([sys.executable, 'scripts/website/' + builder, '--site', str(cls.site)])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_identity_status_and_horizon(self):
        content = load(CONTENT)
        self.assertEqual(content['missionId'], 'GOALOS-PUBLIC-PROOF-MISSION-007')
        self.assertEqual(content['sequence'], 7)
        self.assertEqual(content['status'], 'PROTOCOL_PUBLISHED_AWAITING_THREE_CONTINUITY_PROVEN_COMMONWEALTHS')
        self.assertEqual(content['mission8']['status'], 'HORIZON_ONLY_NOT_YET_AUTHORIZED')

    def test_constitution_budget_and_settlement(self):
        content = load(CONTENT)
        budget = content['missionBudget']
        self.assertEqual(len(content['constitution']), 3)
        self.assertEqual(len(content['stewardshipTrial']['covenants']), 8)
        self.assertEqual(budget['validatorQuorum'], 8)
        self.assertEqual(budget['publicChallengeWindowHours'], 1440)
        self.assertEqual(sum(item['share'] for item in content['settlement']), 100)

    def test_proof_route_uses_all_goalos_contracts(self):
        content = load(CONTENT)
        mainnet = load(MAINNET)
        names = {item['name'] for item in mainnet['contracts'] if item['name'] != 'AGIALPHA'}
        route = {item['contractName'] for item in content['proofRoute']}
        self.assertEqual(len(content['proofRoute']), 48)
        self.assertEqual(route, names)
        self.assertEqual(mainnet['verification']['verified'], 48)
        self.assertEqual(mainnet['verification']['failed'], 0)
        self.assertTrue(mainnet['verification']['complete'])
        self.assertEqual(mainnet['phaseBGrantCount'], 14)
        self.assertEqual(mainnet['postcheck']['status'], 'PASSED')

    def test_no_named_competitor_or_predeclared_result(self):
        text = CONTENT.read_text().lower()
        for token in ('recursive.com', 'recursive org', 'recursive-style', 'named competitor'):
            self.assertNotIn(token, text)
        content = load(CONTENT)
        self.assertIn('AWAITING', content['status'])
        self.assertTrue(any('not evidence' in item.lower() for item in content['claimBoundaries']))
        self.assertNotEqual(content.get('maturity', {}).get('designation'), content['status'])

    def test_build_generates_complete_experience(self):
        page = (self.site / 'proof-mission-007.html').read_text()
        hub = (self.site / 'proof-missions.html').read_text()
        self.assertIn('THE <span>CIVILIZATIONAL COVENANT</span>', page)
        self.assertEqual(page.count('class="cv-route route-item"'), 48)
        self.assertIn('The Civilizational Covenant', hub)
        self.assertTrue((self.site / 'downloads/proof-missions/public-proof-mission-007.json').exists())
        self.assertTrue((self.site / 'downloads/proof-missions/mission-007-proof-route.csv').exists())

    def test_builder_records_preservation_and_promotion(self):
        report = load(self.site / 'qa/proof-mission-007-build.json')
        self.assertTrue(report['mission001To005Preserved'])
        self.assertTrue(report['mission006HorizonPromoted'])
        self.assertFalse(report['publicNetworkTransactionSent'])

    def test_homepage_has_one_marked_panel(self):
        home = (self.site / 'index.html').read_text()
        self.assertEqual(home.count('<!-- GOALOS_PROOF_MISSION_007_START -->'), 1)
        self.assertEqual(home.count('<!-- GOALOS_PROOF_MISSION_007_END -->'), 1)
        self.assertEqual(home.count('PUBLIC PROOF MISSION 007'), 1)

    def test_templates_are_not_evidence(self):
        for path in (self.site / 'downloads/proof-missions').glob('mission-007-*-template.json'):
            self.assertEqual(load(path)['status'], 'TEMPLATE_NOT_EVIDENCE')

    def test_mission006_is_changed_only_by_horizon_promotion(self):
        mission6 = (self.site / 'proof-mission-006.html').read_text()
        self.assertIn('PUBLIC PROOF MISSION 007 · NOW PUBLISHED', mission6)
        self.assertIn('<!-- GOALOS_PROOF_MISSION_007_PROMOTION_START -->', mission6)

    def test_full_verifier_passes_without_network_or_broadcast(self):
        run([sys.executable, 'scripts/website/verify_proof_mission_007.py', '--site', str(self.site), '--repo', '.'])
        report = load(self.site / 'qa/proof-mission-007-verification.json')
        self.assertEqual(report['status'], 'PASS')
        self.assertFalse(report['publicNetworkTransactionSent'])

if __name__ == '__main__':
    unittest.main()
