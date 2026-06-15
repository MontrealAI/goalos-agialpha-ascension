import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class SettlementReadinessTest(unittest.TestCase):
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
