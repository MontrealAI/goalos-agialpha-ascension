import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "qa/mainnet-authorization-certificate.json"

class FiveGateCertificateTests(unittest.TestCase):
    def run_cmd(self, *args):
        return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_certificate_generation_is_fail_closed_on_blocked_gates(self):
        result = self.run_cmd("python", "scripts/generate-mainnet-authorization-certificate.py")
        self.assertEqual(result.returncode, 0, result.stdout)
        cert = json.loads(CERT.read_text())
        self.assertEqual(cert["authorization"], "NOT_AUTHORIZED")
        self.assertEqual(cert["technicallyMainnetReady"], "NO")
        self.assertEqual(cert["MAINNET_DEPLOYED"], "NO")
        self.assertEqual(cert["MAINNET_VERIFIED"], "NO")
        self.assertEqual(cert["LIVE_OWNER_HANDOFF_COMPLETE"], "NO")
        self.assertEqual(cert["LIVE_CANARY_COMPLETE"], "NO")
        self.assertTrue(cert["blockers"])
        self.assertEqual(set(cert["gates"]), {"G1", "G2", "G3", "G4", "G5"})
        self.assertTrue(all(status != "PASS" for status in cert["gates"].values()))

    def test_certificate_validator_accepts_blocked_certificate_but_rejects_stale_authorization(self):
        gen = self.run_cmd("python", "scripts/generate-mainnet-authorization-certificate.py")
        self.assertEqual(gen.returncode, 0, gen.stdout)
        ok = self.run_cmd("python", "scripts/validate-mainnet-authorization-certificate.py")
        self.assertEqual(ok.returncode, 0, ok.stdout)
        cert = json.loads(CERT.read_text())
        cert["authorization"] = "AUTHORIZED"
        CERT.write_text(json.dumps(cert, indent=2) + "\n")
        bad = self.run_cmd("python", "scripts/validate-mainnet-authorization-certificate.py")
        self.assertNotEqual(bad.returncode, 0, bad.stdout)
        self.assertIn("non-ready certificate cannot be AUTHORIZED", bad.stdout)
        self.run_cmd("python", "scripts/generate-mainnet-authorization-certificate.py")

if __name__ == "__main__":
    unittest.main()
