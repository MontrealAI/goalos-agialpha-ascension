import csv
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProofMission004Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.site = cls.tmp / "site"
        for command in [
            ["python3", "scripts/build_goalos_agialpha_ascension_website_v86.py", "--out", str(cls.site)],
            ["python3", "scripts/website/build_proof_gradient_sovereign.py", "--site", str(cls.site)],
            ["python3", "scripts/website/build_proof_mission_002.py", "--site", str(cls.site)],
            ["python3", "scripts/website/build_proof_mission_003.py", "--site", str(cls.site)],
            ["python3", "scripts/website/build_proof_mission_004.py", "--site", str(cls.site)],
        ]:
            subprocess.run(command, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_additive_idempotent_and_canonical_source_preserved(self):
        original = (ROOT / "website/v86_actual_site/index.html").read_bytes()
        first = (self.site / "index.html").read_bytes()
        subprocess.run(
            ["python3", "scripts/website/build_proof_mission_004.py", "--site", str(self.site)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        self.assertEqual(first, (self.site / "index.html").read_bytes())
        self.assertEqual(original, (ROOT / "website/v86_actual_site/index.html").read_bytes())

    def test_mission_contract_is_complete_and_claim_bounded(self):
        content = json.loads((ROOT / "content/proof-mission-004-sovereign-institution.json").read_text())
        self.assertEqual(content["sequence"], 4)
        self.assertEqual(content["status"], "PROTOCOL_PUBLISHED_AWAITING_ONE_COMPOSITION_PROVEN_CONSTELLATION")
        self.assertEqual(sum(item["share"] for item in content["settlement"]), 100)
        self.assertEqual(len(content["proofRoute"]), 34)
        self.assertEqual(len(content["validators"]), 5)
        self.assertEqual(content["missionBudget"]["missionEpochs"], 4)
        self.assertEqual(content["missionBudget"]["challengeWindowHours"], 336)
        page = (self.site / "proof-mission-004.html").read_text().lower()
        self.assertIn("no institutional result predeclared", page)
        self.assertIn("cannot begin scientifically until one constellation", page)
        self.assertIn("it does not establish", page)
        self.assertIn("achieved agi, asi, or superintelligence", page)

    def test_missions_one_to_three_are_preserved_and_hub_has_four(self):
        for page in ["proof-gradient-challenge.html", "proof-mission-002.html", "proof-mission-003.html"]:
            self.assertTrue((self.site / page).exists())
        hub = (self.site / "proof-missions.html").read_text()
        self.assertEqual(hub.count('class="pm-card'), 4)
        for href in [
            "proof-gradient-challenge.html",
            "proof-mission-002.html",
            "proof-mission-003.html",
            "proof-mission-004.html",
        ]:
            self.assertIn(href, hub)
        home = (self.site / "index.html").read_text()
        for marker in [
            "GOALOS_PROOF_GRADIENT_SOVEREIGN_START",
            "GOALOS_PROOF_MISSION_002_START",
            "GOALOS_PROOF_MISSION_003_START",
            "GOALOS_PROOF_MISSION_004_START",
        ]:
            self.assertEqual(home.count(f"<!-- {marker} -->"), 1)

    def test_mission_three_horizon_is_promoted_without_rewriting_other_content(self):
        page = (self.site / "proof-mission-003.html").read_text()
        self.assertIn("PUBLIC PROOF MISSION 004 · NOW PUBLISHED", page)
        self.assertIn("proof-mission-004.html", page)
        self.assertNotIn("MISSION 004 HORIZON", page)
        self.assertIn("the capability constellation", page.lower())

    def test_public_content_has_no_named_competitor_reference(self):
        text = "\n".join(
            (self.site / page).read_text().lower()
            for page in ["proof-mission-004.html", "proof-missions.html", "index.html"]
        )
        for term in ["recursive.com", "recursive org", "recursive-style", "competitor comparison", "named competitor"]:
            self.assertNotIn(term, text)

    def test_templates_are_not_evidence_and_route_matches_mainnet(self):
        directory = self.site / "downloads/proof-missions"
        templates = [
            "mission-004-institution-charter-template.json",
            "mission-004-epoch-ledger-template.json",
            "mission-004-treasury-policy-template.json",
            "mission-004-incident-recovery-template.json",
        ]
        for name in templates:
            self.assertEqual(json.loads((directory / name).read_text())["status"], "TEMPLATE_NOT_EVIDENCE")
        with (directory / "mission-004-proof-route.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 34)
        mainnet = json.loads((ROOT / "data/mainnet/v4.4.0-mainnet-2026-06-21.json").read_text())
        by_name = {entry["name"]: entry["address"].lower() for entry in mainnet["contracts"]}
        for row in rows:
            self.assertEqual(by_name[row["contract"]], row["address"].lower())

    def test_verifier_passes(self):
        result = subprocess.run(
            ["python3", "scripts/website/verify_proof_mission_004.py", "--site", str(self.site)],
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
