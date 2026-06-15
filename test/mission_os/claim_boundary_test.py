import subprocess
import tempfile
import unittest
from pathlib import Path


class ClaimBoundaryTest(unittest.TestCase):
    def test_claim_boundary_example_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            subprocess.check_call([
                "python", "scripts/mission-os/mission_os_until_done.py",
                "--mission", "examples/mission-os/ai-product-intelligence.json",
                "--out", str(out),
            ])
            subprocess.check_call(["python", "scripts/mission-os/claim_boundary_check.py", "--dir", str(out)])


if __name__ == "__main__":
    unittest.main()
