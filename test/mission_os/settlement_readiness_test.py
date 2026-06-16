import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class SettlementReadinessTest(unittest.TestCase):
    def test_mainnet_readiness_rejects_noncanonical_agialpha_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            mission = json.loads(Path("examples/mission-os/ethereum-mainnet-operator-readiness.json").read_text())
            mission["agialpha_token_address"] = "0x0000000000000000000000000000000000000000"
            mission_path = Path(tmp) / "bad-mainnet-token.json"
            mission_path.write_text(json.dumps(mission))
            out = Path(tmp) / "bad-mainnet"
            result = subprocess.run([
                "python", "scripts/mission-os/mission_os_until_done.py",
                "--mission", str(mission_path),
                "--out", str(out),
            ], text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("canonical AGIALPHA token", result.stderr)

    def test_deployment_required_intake_is_rejected_until_evidence_capture_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            mission = json.loads(Path("examples/mission-os/ethereum-sepolia-deployment-readiness.json").read_text())
            mission["requires_contract_deployment"] = True
            mission_path = Path(tmp) / "deployment-required.json"
            mission_path.write_text(json.dumps(mission))
            out = Path(tmp) / "deployment-required"
            result = subprocess.run([
                "python", "scripts/mission-os/mission_os_until_done.py",
                "--mission", str(mission_path),
                "--out", str(out),
            ], text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires_contract_deployment=true", result.stderr)
            self.assertIn("transaction evidence", result.stderr)

    def test_verification_required_intake_is_rejected_until_evidence_capture_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            mission = json.loads(Path("examples/mission-os/ethereum-sepolia-deployment-readiness.json").read_text())
            mission["requires_contract_verification"] = True
            mission_path = Path(tmp) / "verification-required.json"
            mission_path.write_text(json.dumps(mission))
            out = Path(tmp) / "verification-required"
            result = subprocess.run([
                "python", "scripts/mission-os/mission_os_until_done.py",
                "--mission", str(mission_path),
                "--out", str(out),
            ], text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires_contract_verification=true", result.stderr)
            self.assertIn("constructor arguments", result.stderr)

    def test_mainnet_readiness_never_broadcasts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "mainnet"
            subprocess.check_call([
                "python", "scripts/mission-os/mission_os_until_done.py",
                "--mission", "examples/mission-os/ethereum-mainnet-operator-readiness.json",
                "--out", str(out),
            ])
            readiness = json.loads((out / "MissionSettlementReadiness.json").read_text())
            self.assertEqual(readiness["chain_id"], 1)
            self.assertFalse(readiness["mainnet_broadcast_performed"])
            self.assertFalse(readiness["token_movement_performed"])
            self.assertEqual(readiness["mainnet_deployed_status"], "NO")


if __name__ == "__main__":
    unittest.main()
