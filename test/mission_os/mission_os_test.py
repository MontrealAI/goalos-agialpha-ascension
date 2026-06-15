import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class MissionOSTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "mission"
        p = subprocess.run([
            "python", "scripts/mission-os/mission_os_until_done.py",
            "--mission", "examples/mission-os/ai-product-intelligence.json",
            "--out", str(cls.out),
            "--max-cycles", "2",
        ], cwd=ROOT, text=True, capture_output=True)
        cls.generator_result = p

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_cmd(self, args, cwd=ROOT):
        return subprocess.run(args, cwd=cwd, text=True, capture_output=True)

    def test_until_done_generates_required_artifacts(self):
        self.assertEqual(self.generator_result.returncode, 0, self.generator_result.stderr)
        state = json.loads((self.out / "run-state.json").read_text())
        self.assertTrue(state["done"])
        for name in ["EvidenceDocket.md", "DecisionState.json", "ActionGraph.md", "ClaimBoundaryReport.md", "QAReport.md", "artifact-manifest.json", "index.html"]:
            self.assertTrue((self.out / name).exists(), name)

    def test_done_checker_passes_complete_mission(self):
        self.assertEqual(self.generator_result.returncode, 0, self.generator_result.stderr)
        p = self.run_cmd(["python", "scripts/mission-os/done_check.py", str(self.out)])
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_claim_boundary_blocks_unsafe_claim(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "mission"
            out.mkdir(parents=True)
            (out / "bad.md").write_text("This claims achieved AGI and guaranteed ROI.")
            p = self.run_cmd(["python", "scripts/mission-os/claim_boundary_check.py", str(out)])
            self.assertNotEqual(p.returncode, 0)

    def test_workflow_does_not_auto_merge_or_mainnet_broadcast(self):
        workflow = (ROOT / ".github/workflows/goalos-mission-os-until-done.yml").read_text().lower()
        self.assertNotIn("deploy:ethereum-mainnet", workflow)
        self.assertNotIn("allow_mainnet_deployment", workflow)
        active_lines = [line for line in workflow.splitlines() if "does not" not in line and "never " not in line]
        self.assertNotIn("mainnet", "\n".join(active_lines))
        self.assertNotIn("token movement", "\n".join(active_lines))
        self.assertNotIn("auto-merge: true", workflow)

if __name__ == "__main__":
    unittest.main()
