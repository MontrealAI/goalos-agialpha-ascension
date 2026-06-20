import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FiveGateFailClosedTest(unittest.TestCase):
    def run_cmd(self, *cmd):
        return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_production_readiness_generates_blocked_five_gate_dossier(self):
        result = self.run_cmd('python', 'scripts/mainnet_operational_readiness.py', '--validate')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        dossier = json.loads((ROOT / 'qa/mainnet-readiness/production-readiness.json').read_text())
        self.assertEqual(dossier['status'], 'BLOCKED')
        self.assertEqual(dossier['MAINNET_DEPLOYED'], 'NO')
        self.assertEqual(dossier['MAINNET_VERIFIED'], 'NO')
        for name in [
            'gate-1-authority.json',
            'gate-2-overrides.json',
            'gate-3-accounting.json',
            'gate-4-lifecycle.json',
            'gate-5-assurance.json',
        ]:
            gate = json.loads((ROOT / 'qa/mainnet-readiness' / name).read_text())
            self.assertEqual(gate['status'], 'BLOCKED')
            self.assertTrue(gate['blockers'])

    def test_certificate_cannot_authorize_without_five_gate_pass(self):
        self.run_cmd('python', 'scripts/mainnet_operational_readiness.py')
        result = self.run_cmd('python', 'scripts/generate-mainnet-authorization-certificate.py')
        self.assertEqual(result.returncode, 0, result.stdout)
        cert = json.loads((ROOT / 'qa/mainnet-authorization-certificate.json').read_text())
        self.assertEqual(cert['TECHNICALLY_MAINNET_READY'], 'NO')
        self.assertEqual(cert['ETHEREUM_MAINNET_AUTHORIZED'], 'NO')
        self.assertIn('Five-gate production-readiness dossier is not PASS.', cert['blockers'])
        self.assertEqual(cert['MAINNET_DEPLOYED'], 'NO')

    def test_phase_a_helper_does_not_report_release_pass_without_evidence(self):
        result = self.run_cmd('python', 'scripts/phase_a_assurance.py', 'differential')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        report = json.loads((ROOT / 'qa/pr-readiness/differential-report.json').read_text())
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertTrue(report['blockers'])


if __name__ == '__main__':
    unittest.main()
