import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProofMission002Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.site = cls.tmp / "site"
        subprocess.run(
            ["python3", "scripts/build_goalos_agialpha_ascension_website_v86.py", "--out", str(cls.site)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            ["python3", "scripts/website/build_proof_gradient_sovereign.py", "--site", str(cls.site)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            ["python3", "scripts/website/build_proof_mission_002.py", "--site", str(cls.site)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_additive_idempotent_and_source_preserved(self):
        original = (ROOT / "website/v86_actual_site/index.html").read_bytes()
        first = (self.site / "index.html").read_bytes()
        subprocess.run(
            ["python3", "scripts/website/build_proof_mission_002.py", "--site", str(self.site)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        second = (self.site / "index.html").read_bytes()
        self.assertEqual(first, second)
        self.assertEqual(original, (ROOT / "website/v86_actual_site/index.html").read_bytes())

    def test_mission_sequence_and_claim_boundary(self):
        content = json.loads((ROOT / "content/proof-mission-002-ascension-protocol.json").read_text())
        self.assertEqual(content["sequence"], 2)
        self.assertEqual(content["status"], "PROTOCOL_PUBLISHED_AWAITING_MISSION_001_ACCEPTED_CAPABILITY")
        self.assertEqual(sum(item["share"] for item in content["settlement"]), 100)
        self.assertEqual(len(content["proofRoute"]), 17)
        page = (self.site / "proof-mission-002.html").read_text().lower()
        self.assertIn("no result predeclared", page)
        self.assertIn("mission 001 produces an accepted capability", page)

    def test_public_content_has_no_named_competitor_reference(self):
        page = (self.site / "proof-mission-002.html").read_text().lower()
        hub = (self.site / "proof-missions.html").read_text().lower()
        home = (self.site / "index.html").read_text()
        overlay = home.split("<!-- GOALOS_PROOF_MISSION_002_START -->", 1)[1].split("<!-- GOALOS_PROOF_MISSION_002_END -->", 1)[0].lower()
        for term in ["recursive.com", "recursive org", "recursive-style", "competitor comparison", "named competitor"]:
            self.assertNotIn(term, page + "\n" + hub + "\n" + overlay)

    def test_mission_001_is_preserved_and_hub_links_both(self):
        self.assertTrue((self.site / "proof-gradient-challenge.html").exists())
        hub = (self.site / "proof-missions.html").read_text()
        self.assertIn("proof-gradient-challenge.html", hub)
        self.assertIn("proof-mission-002.html", hub)
        home = (self.site / "index.html").read_text()
        self.assertEqual(home.count("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->"), 1)
        self.assertEqual(home.count("<!-- GOALOS_PROOF_MISSION_002_START -->"), 1)

    def test_verifier_passes(self):
        result = subprocess.run(
            ["python3", "scripts/website/verify_proof_mission_002.py", "--site", str(self.site)],
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
