from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UnifiedProofGradientSovereignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="goalos-proof-gradient-"))
        cls.site = cls.tmp / "site"
        cls._run("scripts/build_goalos_agialpha_ascension_website_v86.py", "--out", str(cls.site))
        cls._run(
            "scripts/add_goalos_ethereum_mainnet_pages_v87.py",
            "--site", str(cls.site),
            "--registry", "config/ethereum-mainnet.contracts.json",
            "--release-contracts", "release/mainnet-2026-06-21/CONTRACTS_MAINNET.json",
            "--release-manifest", "release/mainnet-2026-06-21/RELEASE_MANIFEST.json",
            "--deployment-evidence", "release/mainnet-2026-06-21/DEPLOYMENT_EVIDENCE.json",
        )
        cls._run(
            "scripts/website/build_proof_gradient_sovereign.py",
            "--site", str(cls.site),
            "--content", "content/proof-gradient-sovereign.json",
            "--mainnet", "data/mainnet/v4.4.0-mainnet-2026-06-21.json",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp)

    @classmethod
    def _run(cls, script: str, *args: str) -> None:
        subprocess.run(
            ["python3", script, *args],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_unified_build_is_additive_and_idempotent(self) -> None:
        canonical_before = (ROOT / "website/v86_actual_site/index.html").read_bytes()
        first_home = (self.site / "index.html").read_bytes()
        first_mainnet = (self.site / "ethereum-mainnet.html").read_bytes()
        first_proof = (self.site / "proof-gradient-challenge.html").read_bytes()

        self._run(
            "scripts/add_goalos_ethereum_mainnet_pages_v87.py",
            "--site", str(self.site),
            "--registry", "config/ethereum-mainnet.contracts.json",
            "--release-contracts", "release/mainnet-2026-06-21/CONTRACTS_MAINNET.json",
            "--release-manifest", "release/mainnet-2026-06-21/RELEASE_MANIFEST.json",
            "--deployment-evidence", "release/mainnet-2026-06-21/DEPLOYMENT_EVIDENCE.json",
        )
        self._run(
            "scripts/website/build_proof_gradient_sovereign.py",
            "--site", str(self.site),
            "--content", "content/proof-gradient-sovereign.json",
            "--mainnet", "data/mainnet/v4.4.0-mainnet-2026-06-21.json",
        )

        self.assertEqual(first_home, (self.site / "index.html").read_bytes())
        self.assertEqual(first_mainnet, (self.site / "ethereum-mainnet.html").read_bytes())
        self.assertEqual(first_proof, (self.site / "proof-gradient-challenge.html").read_bytes())
        self.assertEqual(canonical_before, (ROOT / "website/v86_actual_site/index.html").read_bytes())

    def test_homepage_contains_both_non_overlapping_features(self) -> None:
        home = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertEqual(home.count("<!-- GOALOS_MAINNET_V87_START -->"), 1)
        self.assertEqual(home.count("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->"), 1)
        self.assertIn("ethereum-mainnet.html", home)
        self.assertIn("proof-gradient-challenge.html", home)

    def test_public_content_has_no_competitor_reference(self) -> None:
        page = (self.site / "proof-gradient-challenge.html").read_text(encoding="utf-8").lower()
        home = (self.site / "index.html").read_text(encoding="utf-8")
        overlay = home.split("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->", 1)[1].split("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->", 1)[0].lower()
        for term in ("third-party competitor", "competitor comparison", " versus ", " vs. "):
            self.assertNotIn(term, page + "\n" + overlay)

    def test_mainnet_evidence_and_contract_count(self) -> None:
        mainnet_map = json.loads((self.site / "downloads/proof-gradient/proof-gradient-mainnet-map.json").read_text(encoding="utf-8"))
        self.assertEqual(mainnet_map["verification"]["verified"], 48)
        self.assertEqual(mainnet_map["verification"]["failed"], 0)
        self.assertEqual(len([item for item in mainnet_map["contracts"] if item["goalosCreated"]]), 48)
        self.assertEqual(mainnet_map["postcheck"]["status"], "PASSED")
        self.assertEqual(mainnet_map["postcheck"]["checkedContracts"], 48)

    def test_all_static_verifiers_pass(self) -> None:
        commands = (
            ["python3", "scripts/verify_goalos_ethereum_mainnet_pages_v87.py", "--site", str(self.site), "--registry", "config/ethereum-mainnet.contracts.json"],
            ["python3", "scripts/website/verify_proof_gradient_sovereign.py", "--site", str(self.site)],
            ["python3", "scripts/website/verify_unified_public_site.py", "--site", str(self.site)],
        )
        for command in commands:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
