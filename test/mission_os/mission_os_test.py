import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class MissionOSRunTest(unittest.TestCase):
    def test_mission_os_run_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            result = subprocess.run(
                [
                    "python",
                    "scripts/mission-os/mission_os_until_done.py",
                    "--mission",
                    "examples/mission-os/ai-product-intelligence.json",
                    "--out",
                    str(out),
                    "--max-cycles",
                    "2",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            state = json.loads((out / "run-state.json").read_text())
            self.assertTrue(state["done"])
            self.assertTrue((out / "MissionSettlementReadiness.json").exists())


if __name__ == "__main__":
    unittest.main()
