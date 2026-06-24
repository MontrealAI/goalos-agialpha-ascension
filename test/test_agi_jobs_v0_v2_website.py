from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "website" / "build_agi_jobs_v0_v2.py"
SNAPSHOT = ROOT / "scripts" / "website" / "snapshot_agi_jobs_v0_v2_site.py"
VERIFY = ROOT / "scripts" / "website" / "verify_agi_jobs_v0_v2.py"
VISUAL = ROOT / "scripts" / "website" / "visual_check_agi_jobs_v0_v2.py"
CONTENT = ROOT / "content" / "agi-jobs-v0-v2.json"
SCHEMA = ROOT / "schemas" / "agi-jobs-v0-v2-evidence-docket.schema.json"
PAGES = [
    "agi-jobs-v0-v2.html",
    "agi-jobs-v0-v2-market.html",
    "agi-jobs-v0-v2-settlement.html",
    "agi-jobs-v0-v2-memory.html",
    "agi-jobs-v0-v2-architecture.html",
]
DOWNLOADS = [
    "downloads/agi-jobs-v0-v2/sample-agi-jobs-evidence-docket.json",
    "downloads/agi-jobs-v0-v2/agi-jobs-v0-v2-economic-memory.json",
    "downloads/agi-jobs-v0-v2/agi-jobs-v0-v2-executive-review-brief.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AGIJobsV0V2WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.temp.name) / "site"
        cls.site.mkdir()
        (cls.site / "index.html").write_text("<!doctype html><html><head><title>GoalOS</title></head><body><nav><a href='index.html'>Home</a></nav><main><section id='existing'>Preserved</section></main></body></html>", encoding="utf-8")
        (cls.site / "routes.json").write_text(json.dumps({"version": "test", "routes": ["index.html"]}) + "\n", encoding="utf-8")
        (cls.site / "sitemap.xml").write_text("<?xml version='1.0'?><urlset></urlset>\n", encoding="utf-8")
        (cls.site / "site-status.json").write_text(json.dumps({"status": "fixture"}) + "\n", encoding="utf-8")
        shared = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
        meta_manifest = {
            "schema": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
            "files": {name: {"sha256": sha(cls.site / name), "bytes": (cls.site / name).stat().st_size} for name in shared},
            "integration": {"reconciliations": []},
        }
        (cls.site / "meta-agentic-alpha-agi-manifest.json").write_text(json.dumps(meta_manifest, indent=2) + "\n", encoding="utf-8")
        node_files = {name: {"sha256": sha(cls.site / name), "bytes": (cls.site / name).stat().st_size} for name in shared}
        node_files["meta-agentic-alpha-agi-manifest.json"] = {
            "sha256": sha(cls.site / "meta-agentic-alpha-agi-manifest.json"),
            "bytes": (cls.site / "meta-agentic-alpha-agi-manifest.json").stat().st_size,
        }
        node_manifest = {
            "schema": "goalos.agi_alpha_node_v0.website_manifest.v2",
            "files": node_files,
            "integration": {"reconciliations": []},
        }
        (cls.site / "agi-alpha-node-v0-manifest.json").write_text(json.dumps(node_manifest, indent=2) + "\n", encoding="utf-8")
        cls.baseline = Path(cls.temp.name) / "baseline.json"
        subprocess.run([sys.executable, str(SNAPSHOT), "--site", str(cls.site), "--output", str(cls.baseline)], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.env = dict(os.environ, SOURCE_DATE_EPOCH="1782259200")
        subprocess.run([sys.executable, str(BUILD), "--site", str(cls.site), "--root", str(ROOT)], cwd=ROOT, env=cls.env, check=True, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_01_release_contract_is_exact(self) -> None:
        data = json.loads((self.site / "data" / "agi-jobs-v0-v2.json").read_text(encoding="utf-8"))
        self.assertEqual(data["release_title"], "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨")
        self.assertEqual(data["release_id"], "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002")
        self.assertEqual(data["version"], "3.0.0-sovereign-labor-civilization")
        self.assertEqual(data["lineage_root"], "ef43db8a6632192f9347083bf42f2c1cdbb6eb662f634408fde5139ea516d2a0")

    def test_02_constitutional_depth_is_complete(self) -> None:
        data = json.loads(CONTENT.read_text(encoding="utf-8"))
        expected = {
            "lifecycle": 14, "institutions": 12, "validators": 7, "guardians": 5, "modules": 14,
            "job_archetypes": 16, "artifacts": 24, "memory_rules": 8, "economic_invariants": 8,
            "lineage_fingerprints": 32,
        }
        for key, count in expected.items():
            self.assertEqual(len(data[key]), count, key)

    def test_03_security_is_default_deny(self) -> None:
        security = json.loads(CONTENT.read_text(encoding="utf-8"))["security"]
        for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "local_storage", "live_ens_resolution", "live_compute", "live_token_movement"]:
            self.assertIs(security[key], False, key)
        self.assertTrue(security["human_review_required"])
        self.assertEqual(security["external_authority"], "none")

    def test_04_build_outputs_all_five_public_surfaces(self) -> None:
        for page in PAGES:
            self.assertGreater((self.site / page).stat().st_size, 4000, page)
        for path in ["assets/agi-jobs-v0-v2.css", "assets/agi-jobs-v0-v2.js", "data/agi-jobs-v0-v2.json", *DOWNLOADS, "agi-jobs-v0-v2-manifest.json"]:
            self.assertTrue((self.site / path).is_file(), path)

    def test_05_homepage_integration_is_additive_and_discoverable(self) -> None:
        text = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn("<section id='existing'>Preserved</section>", text)
        self.assertEqual(text.count("GOALOS_AGI_JOBS_V0_V2_HOME_START"), 1)
        self.assertEqual(text.count("GOALOS_AGI_JOBS_V0_V2_NAV_START"), 1)
        self.assertEqual(text.count('href="agi-jobs-v0-v2.html">AGI Jobs</a>'), 1)
        for page in PAGES:
            self.assertIn(f'href="{page}"', text)

    def test_06_sample_docket_has_valid_twenty_four_link_chain(self) -> None:
        docket = json.loads((self.site / DOWNLOADS[0]).read_text(encoding="utf-8"))
        chain = docket["proof_chronicle"]["artifacts"]
        self.assertEqual(len(chain), 24)
        previous = "0" * 64
        for index, item in enumerate(chain, 1):
            payload_hash = hashlib.sha256(json.dumps(item["payload"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            commitment = hashlib.sha256(f"{previous}:{payload_hash}:{item['name']}".encode()).hexdigest()
            self.assertEqual(item["index"], index)
            self.assertEqual(item["previous_commitment"], previous)
            self.assertEqual(item["artifact_hash"], payload_hash)
            self.assertEqual(item["commitment"], commitment)
            previous = commitment
        self.assertEqual(docket["proof_chronicle"]["chain_head"], previous)

    def test_07_sample_docket_models_a_full_labor_constitution(self) -> None:
        docket = json.loads((self.site / DOWNLOADS[0]).read_text(encoding="utf-8"))
        self.assertEqual(len(docket["market"]["ranked"]), 12)
        self.assertEqual(len(docket["market"]["coalition"]["specialists"]), 2)
        self.assertEqual(len(docket["work_graph"]), 8)
        self.assertEqual(len(docket["validator_parliament"]["votes"]), 7)
        self.assertEqual(len(docket["guardian_chamber"]["seats"]), 5)
        self.assertEqual(len(docket["settlement"]["allocations"]), 6)
        self.assertGreaterEqual(len(docket["settlement"]["contributions"]), 4)

    def test_08_human_authority_and_memory_boundaries_hold(self) -> None:
        docket = json.loads((self.site / DOWNLOADS[0]).read_text(encoding="utf-8"))
        self.assertEqual(docket["terminal"]["state"], "HUMAN_SETTLEMENT_REVIEW")
        self.assertEqual(docket["terminal"]["authority"], "NONE_GRANTED")
        self.assertEqual(docket["terminal"]["external_actions"], 0)
        self.assertFalse(docket["settlement"]["live_token_movement"])
        self.assertEqual(docket["validator_parliament"]["dissent"], 1)
        self.assertEqual(docket["memory_candidate"]["status"], "HUMAN_APPROVAL_PENDING")
        self.assertTrue(docket["memory_candidate"]["revocable"])

    def test_09_manifest_hashes_every_declared_output(self) -> None:
        manifest = json.loads((self.site / "agi-jobs-v0-v2-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "goalos.agi_jobs_v0_v2.website_manifest.v3")
        for relative, record in manifest["files"].items():
            path = self.site / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha(path), record["sha256"], relative)
            self.assertEqual(path.stat().st_size, record["bytes"], relative)

    def test_10_companion_manifests_remain_internally_verifiable(self) -> None:
        for manifest_name in ["meta-agentic-alpha-agi-manifest.json", "agi-alpha-node-v0-manifest.json"]:
            manifest = json.loads((self.site / manifest_name).read_text(encoding="utf-8"))
            self.assertTrue(any(item.get("release_id") == "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002" for item in manifest["integration"]["reconciliations"]))
            for relative, record in manifest["files"].items():
                path = self.site / relative
                self.assertTrue(path.is_file(), f"{manifest_name}:{relative}")
                self.assertEqual(sha(path), record["sha256"], f"{manifest_name}:{relative}")
                self.assertEqual(path.stat().st_size, record["bytes"], f"{manifest_name}:{relative}")

    def test_11_static_verifier_and_preservation_audit_pass(self) -> None:
        output = self.site / "qa" / "unit-static.json"
        result = subprocess.run([sys.executable, str(VERIFY), "--site", str(self.site), "--root", str(ROOT), "--baseline", str(self.baseline), "--schema", str(SCHEMA), "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["preservation"]["removed"], [])
        self.assertEqual(report["preservation"]["unexpected_changed"], [])
        self.assertEqual(report["preservation"]["unexpected_added"], [])

    def test_12_second_build_is_idempotent(self) -> None:
        tracked = [*PAGES, "assets/agi-jobs-v0-v2.css", "assets/agi-jobs-v0-v2.js", "data/agi-jobs-v0-v2.json", *DOWNLOADS, "agi-jobs-v0-v2-manifest.json", "meta-agentic-alpha-agi-manifest.json", "agi-alpha-node-v0-manifest.json", "index.html", "routes.json", "sitemap.xml", "site-status.json"]
        before = {item: sha(self.site / item) for item in tracked}
        subprocess.run([sys.executable, str(BUILD), "--site", str(self.site), "--root", str(ROOT)], cwd=ROOT, env=self.env, check=True, capture_output=True, text=True)
        after = {item: sha(self.site / item) for item in tracked}
        self.assertEqual(before, after)

    def test_13_javascript_is_syntax_valid_deterministic_and_network_free(self) -> None:
        script = ROOT / "website" / "features" / "agi-jobs-v0-v2" / "assets" / "agi-jobs-v0-v2.js"
        result = subprocess.run(["node", "--check", str(script)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = script.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\bfetch\s*\(")
        self.assertNotIn("XMLHttpRequest", text)
        self.assertNotIn("WebSocket(", text)
        self.assertIn("window.__AGI_JOBS_STATE__", text)
        self.assertIn("sha256Fallback", text)

    def test_14_python311_preflight_is_clean(self) -> None:
        scripts = [BUILD, SNAPSHOT, VERIFY, VISUAL]
        for script in scripts:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script), feature_version=(3, 11))
        result = subprocess.run([sys.executable, "-m", "py_compile", *map(str, scripts)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
