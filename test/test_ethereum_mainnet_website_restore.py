from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSION_BUILDERS = [
    "build_proof_gradient_sovereign.py",
    "build_proof_mission_002.py",
    "build_proof_mission_003.py",
    "build_proof_mission_004.py",
    "build_proof_mission_005.py",
    "build_proof_mission_006.py",
    "build_proof_mission_007.py",
    "build_proof_mission_008.py",
]
MISSION_PAGES = [
    "proof-gradient-challenge.html",
    "proof-mission-002.html",
    "proof-mission-003.html",
    "proof-mission-004.html",
    "proof-mission-005.html",
    "proof-mission-006.html",
    "proof-mission-007.html",
    "proof-mission-008.html",
]
MISSION_MARKERS = [
    "GOALOS_PROOF_GRADIENT_SOVEREIGN_START",
    "GOALOS_PROOF_MISSION_002_START",
    "GOALOS_PROOF_MISSION_003_START",
    "GOALOS_PROOF_MISSION_004_START",
    "GOALOS_PROOF_MISSION_005_START",
    "GOALOS_PROOF_MISSION_006_START",
    "GOALOS_PROOF_MISSION_007_START",
    "GOALOS_PROOF_MISSION_008_START",
]


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stdout + "\n" + result.stderr)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EthereumMainnetWebsiteRestoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = Path(tempfile.mkdtemp(prefix="goalos-mainnet-site-restore-"))
        cls.site = cls.temp / "site"
        run([sys.executable, "scripts/build_goalos_agialpha_ascension_website_v86.py", "--out", str(cls.site)])
        for builder in MISSION_BUILDERS:
            run([sys.executable, f"scripts/website/{builder}", "--site", str(cls.site)])
        cls.before = {name: sha(cls.site / name) for name in MISSION_PAGES}
        run(
            [
                sys.executable,
                "scripts/add_goalos_ethereum_mainnet_pages_v87.py",
                "--site",
                str(cls.site),
                "--registry",
                "config/ethereum-mainnet.contracts.json",
                "--release-contracts",
                "release/mainnet-2026-06-21/CONTRACTS_MAINNET.json",
                "--release-manifest",
                "release/mainnet-2026-06-21/RELEASE_MANIFEST.json",
                "--deployment-evidence",
                "release/mainnet-2026-06-21/DEPLOYMENT_EVIDENCE.json",
            ]
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temp)

    def test_mainnet_page_and_home_feature_are_restored(self) -> None:
        self.assertTrue((self.site / "ethereum-mainnet.html").is_file())
        home = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertEqual(home.count("<!-- GOALOS_MAINNET_V87_START -->"), 1)
        self.assertEqual(home.count("<!-- GOALOS_MAINNET_V87_END -->"), 1)
        self.assertIn("href='ethereum-mainnet.html'", home)

    def test_all_eight_proof_missions_are_preserved_byte_for_byte(self) -> None:
        for name in MISSION_PAGES:
            self.assertEqual(sha(self.site / name), self.before[name], name)

    def test_all_eight_homepage_markers_remain_once(self) -> None:
        home = (self.site / "index.html").read_text(encoding="utf-8")
        for marker in MISSION_MARKERS:
            self.assertEqual(home.count(f"<!-- {marker} -->"), 1, marker)

    def test_sitemap_and_site_status_include_mainnet_record(self) -> None:
        sitemap = (self.site / "sitemap.xml").read_text(encoding="utf-8")
        status = json.loads((self.site / "site-status.json").read_text(encoding="utf-8"))
        self.assertIn("ethereum-mainnet.html", sitemap)
        self.assertEqual(status["ethereum_mainnet_page"], "ethereum-mainnet.html")
        self.assertEqual(status["goalos_mainnet_contracts"], 48)
        self.assertEqual(status["operator_etherscan_verification"], "48/48")
        self.assertFalse(status["production_activated"])

    def test_static_mainnet_verifier_passes(self) -> None:
        run(
            [
                sys.executable,
                "scripts/verify_goalos_ethereum_mainnet_pages_v87.py",
                "--site",
                str(self.site),
                "--registry",
                "config/ethereum-mainnet.contracts.json",
            ]
        )
        report = json.loads(
            (self.site / "qa/mainnet-page-static-verify-v87.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["checks"]["proof_mission_pages_preserved"], 8)
        self.assertEqual(report["checks"]["proof_mission_markers_preserved"], 8)


if __name__ == "__main__":
    unittest.main()
