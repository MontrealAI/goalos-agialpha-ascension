import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ProofGradientApexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.builder = cls.repo / "scripts/website/build_proof_gradient_apex.py"
        cls.verifier = cls.repo / "scripts/website/verify_proof_gradient_apex.py"
        cls.manifest = cls.repo / "data/mainnet/v4.4.0-mainnet-2026-06-21.json"
        cls.content = cls.repo / "content/proof-gradient-apex.json"

    def make_site(self, root: Path) -> Path:
        site = root / "site"
        (site / "assets").mkdir(parents=True)
        (site / "assets/goalos-v86-preserve.css").write_text("body{}", encoding="utf-8")
        (site / "assets/goalos-v86-dynamic-ai.js").write_text("", encoding="utf-8")
        index = """<!doctype html><html><head><link rel='stylesheet' href='assets/goalos-v86-preserve.css'><style id='goalos-v86-critical'>body{margin:0}</style></head><body><main><h1>GoalOS</h1><p>Canonical content remains untouched.</p></main><script defer src='assets/goalos-v86-dynamic-ai.js'></script></body></html>"""
        (site / "index.html").write_text(index, encoding="utf-8")
        for name in ["mission-os.html", "proof-cards.html", "proof-observatory.html", "ethereum-mainnet.html", "untouched.html"]:
            (site / name).write_text(f"<html><body>{name}</body></html>", encoding="utf-8")
        (site / "routes.json").write_text(json.dumps({"version": "test", "routes": ["index.html"]}), encoding="utf-8")
        (site / "sitemap.xml").write_text("<?xml version='1.0'?><urlset></urlset>", encoding="utf-8")
        (site / "site-status.json").write_text(json.dumps({"release": "test"}), encoding="utf-8")
        return site

    def run_builder(self, site: Path, manifest: Path | None = None):
        cmd = [sys.executable, str(self.builder), "--site", str(site), "--content", str(self.content), "--manifest", str(manifest or self.manifest)]
        return subprocess.run(cmd, cwd=self.repo, capture_output=True, text=True)

    def run_verifier(self, site: Path):
        cmd = [sys.executable, str(self.verifier), "--site", str(site), "--content", str(self.content), "--manifest", str(self.manifest)]
        return subprocess.run(cmd, cwd=self.repo, capture_output=True, text=True)

    def test_additive_idempotent_overlay_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.make_site(Path(tmp))
            untouched = site / "untouched.html"
            original_hash = hashlib.sha256(untouched.read_bytes()).hexdigest()
            first = self.run_builder(site)
            self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
            second = self.run_builder(site)
            self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
            self.assertEqual(hashlib.sha256(untouched.read_bytes()).hexdigest(), original_hash)
            home = (site / "index.html").read_text(encoding="utf-8")
            self.assertEqual(home.count("GOALOS_PROOF_GRADIENT_APEX_START"), 1)
            self.assertEqual(home.count("GOALOS_PROOF_GRADIENT_APEX_STYLE_START"), 1)
            self.assertTrue((site / "proof-gradient-challenge.html").exists())
            report = json.loads((site / "qa/proof-gradient-apex-build.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS")
            self.assertFalse(report["canonicalSourceModified"])
            self.assertEqual(report["removedGeneratedFiles"], [])
            self.assertEqual(report["unexpectedModifiedFiles"], [])
            verify = self.run_verifier(site)
            self.assertEqual(verify.returncode, 0, verify.stderr + verify.stdout)

    def test_wrong_chain_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site = self.make_site(root)
            bad = json.loads(self.manifest.read_text(encoding="utf-8"))
            bad["chainId"] = 11155111
            bad_path = root / "bad-manifest.json"
            bad_path.write_text(json.dumps(bad), encoding="utf-8")
            result = self.run_builder(site, bad_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("chainId 1", result.stderr + result.stdout)
            self.assertFalse((site / "proof-gradient-challenge.html").exists())

    def test_generated_downloads_contain_48_goalos_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.make_site(Path(tmp))
            result = self.run_builder(site)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            public_map = json.loads((site / "downloads/proof-gradient/proof-gradient-mainnet-map.json").read_text(encoding="utf-8"))
            self.assertEqual(public_map["chainId"], 1)
            self.assertEqual(public_map["goalosCreatedContractCount"], 48)
            self.assertEqual(sum(1 for item in public_map["contracts"] if item["goalosCreated"]), 48)
            self.assertEqual(len(public_map["proofRoute"]), 15)
            self.assertFalse(public_map.get("publicNetworkTransactionSent", False))


if __name__ == "__main__":
    unittest.main()
