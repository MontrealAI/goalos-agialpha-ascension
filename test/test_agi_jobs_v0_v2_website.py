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
    "agi-jobs-v0-v2-proof.html",
    "agi-jobs-v0-v2-settlement.html",
    "agi-jobs-v0-v2-architecture.html",
]
SHARED = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class AGIJobsV0V2WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.temp.name) / "site"
        cls.site.mkdir()
        (cls.site / "index.html").write_text(
            "<!doctype html><html><head><title>GoalOS</title></head><body><nav><a href='index.html'>Home</a></nav><main><section id='existing'>Preserved</section></main></body></html>",
            encoding="utf-8",
        )
        (cls.site / "routes.json").write_text(json.dumps({"version": "test", "routes": ["index.html"]}) + "\n", encoding="utf-8")
        (cls.site / "sitemap.xml").write_text("<?xml version='1.0'?><urlset></urlset>\n", encoding="utf-8")
        (cls.site / "site-status.json").write_text(json.dumps({"status": "fixture"}) + "\n", encoding="utf-8")

        meta_manifest = {
            "schema": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
            "files": {name: {"sha256": sha(cls.site / name), "bytes": (cls.site / name).stat().st_size} for name in SHARED},
            "integration": {"reconciliations": []},
        }
        (cls.site / "meta-agentic-alpha-agi-manifest.json").write_text(json.dumps(meta_manifest, indent=2) + "\n", encoding="utf-8")
        node_files = {name: {"sha256": sha(cls.site / name), "bytes": (cls.site / name).stat().st_size} for name in SHARED}
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
        subprocess.run(
            [sys.executable, str(SNAPSHOT), "--site", str(cls.site), "--output", str(cls.baseline)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        env = dict(os.environ, SOURCE_DATE_EPOCH="1782259200")
        subprocess.run(
            [sys.executable, str(BUILD), "--site", str(cls.site), "--root", str(ROOT)],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_01_release_contract_and_lineage_are_exact(self) -> None:
        data = json.loads((self.site / "data" / "agi-jobs-v0-v2.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "3.0.0")
        self.assertEqual(data["release_id"], "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002")
        self.assertEqual(data["release_title"], "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨")
        self.assertEqual(data["edition"], "Sovereign Work Civilization")
        self.assertEqual(data["version"], "3.0.0-sovereign-work-civilization")
        self.assertEqual(data["origin"]["snapshot_zip_sha256"], "085905a710b3021db79b21263495a9025cdff9fd829d2c5c8dba881426e15239")
        self.assertEqual(data["origin"]["snapshot_tree_root"], "71663cf756cad1347f71a70e1f9cf6071101ab3f494def62e13d268a9066f6fd")
        self.assertEqual(data["origin"]["selected_lineage_root"], "c5ef16a1f3b5dd096f243aa34d2e97d123c85b391e0389fcd2d2627f3025e8d4")

    def test_02_constitutional_depth_is_complete(self) -> None:
        data = json.loads(CONTENT.read_text(encoding="utf-8"))
        expected = {
            "hero_metrics": 5,
            "thesis": 7,
            "job_classes": 7,
            "presets": 8,
            "postures": 5,
            "risk_profiles": 4,
            "incidents": 7,
            "lifecycle": 16,
            "institutions": 12,
            "validators": 9,
            "guardians": 6,
            "modules": 16,
            "council_roles": 5,
            "work_packages": 8,
            "job_archetypes": 16,
            "artifacts": 24,
            "architecture_translation": 16,
            "governance_principles": 10,
            "threats": 10,
            "claim_boundary": 10,
            "lineage_fingerprints": 32,
        }
        for key, count in expected.items():
            self.assertEqual(len(data[key]), count, key)
        self.assertEqual([item["validator_seats"] for item in data["risk_profiles"]], [3, 5, 7, 9])
        self.assertEqual(sum(item["pct"] for item in data["settlement_policy"]["allocations"]), 100)

    def test_03_security_and_authority_are_default_deny(self) -> None:
        data = json.loads(CONTENT.read_text(encoding="utf-8"))
        security = data["security"]
        for key in [
            "external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes",
            "local_storage", "live_ens_resolution", "live_compute", "live_token_movement", "credential_issuance",
        ]:
            self.assertIs(security[key], False, key)
        self.assertTrue(security["human_review_required"])
        self.assertEqual(security["external_authority"], "none")
        self.assertFalse(data["settlement_policy"]["live_token_movement"])
        self.assertFalse(data["settlement_policy"]["wallet_connection"])
        self.assertEqual(data["settlement_policy"]["settlement_authority"], "NONE_GRANTED")

    def test_04_build_outputs_all_five_public_surfaces(self) -> None:
        for page in PAGES:
            self.assertGreater((self.site / page).stat().st_size, 5000, page)
        required = [
            "assets/agi-jobs-v0-v2.css",
            "assets/agi-jobs-v0-v2.js",
            "data/agi-jobs-v0-v2.json",
            "downloads/agi-jobs-v0-v2/sample-agi-jobs-evidence-docket.json",
            "agi-jobs-v0-v2-manifest.json",
            "qa/agi-jobs-v0-v2-build.json",
        ]
        for relative in required:
            self.assertTrue((self.site / relative).is_file(), relative)

    def test_05_homepage_routes_sitemap_and_status_are_additive(self) -> None:
        homepage = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn("<section id='existing'>Preserved</section>", homepage)
        for marker in ["GOALOS_AGI_JOBS_V0_V2_STYLE_START", "GOALOS_AGI_JOBS_V0_V2_NAV_START", "GOALOS_AGI_JOBS_V0_V2_HOME_START"]:
            self.assertEqual(homepage.count(marker), 1, marker)
        self.assertEqual(homepage.count('href="agi-jobs-v0-v2.html">AGI Jobs</a>'), 1)
        routes = json.loads((self.site / "routes.json").read_text(encoding="utf-8"))
        self.assertTrue(set(PAGES).issubset(set(routes["routes"])))
        self.assertEqual(routes["agi_jobs_v0_v2"]["edition"], "Sovereign Work Civilization")
        sitemap = (self.site / "sitemap.xml").read_text(encoding="utf-8")
        self.assertTrue(all(page in sitemap for page in PAGES))
        status = json.loads((self.site / "site-status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["agi_jobs_v0_v2"]["constitutional_gates"], 16)
        self.assertEqual(status["agi_jobs_v0_v2"]["public_surfaces"], 5)

    def test_06_sample_docket_has_valid_twenty_four_link_chain(self) -> None:
        docket = json.loads((self.site / "downloads" / "agi-jobs-v0-v2" / "sample-agi-jobs-evidence-docket.json").read_text(encoding="utf-8"))
        chain = docket["evidence"]["artifacts"]
        self.assertEqual(len(chain), 24)
        previous = "0" * 64
        for expected_id, item in enumerate(chain, 1):
            self.assertEqual(item["id"], f"A{expected_id:02d}")
            self.assertEqual(item["previous_commitment"], previous)
            commitment = hashlib.sha256(stable({"previous": previous, "payload": item["payload"]}).encode("utf-8")).hexdigest()
            self.assertEqual(item["commitment"], commitment)
            previous = commitment
        self.assertEqual(docket["evidence"]["artifact_count"], 24)
        self.assertEqual(docket["evidence"]["chain_head"], previous)
        without_commitment = dict(docket)
        run_commitment = without_commitment.pop("run_commitment")
        self.assertEqual(run_commitment, hashlib.sha256(stable(without_commitment).encode("utf-8")).hexdigest())

    def test_07_sample_docket_preserves_parliament_dissent_and_human_authority(self) -> None:
        docket = json.loads((self.site / "downloads" / "agi-jobs-v0-v2" / "sample-agi-jobs-evidence-docket.json").read_text(encoding="utf-8"))
        self.assertEqual(docket["parliament"]["seats"], 9)
        self.assertEqual(docket["parliament"]["threshold"], 7)
        self.assertEqual(docket["parliament"]["pass"], 8)
        self.assertEqual(docket["parliament"]["dissent"], 1)
        self.assertEqual(len(docket["guardians"]), 6)
        self.assertEqual(docket["authority"]["terminal_state"], "HUMAN_SETTLEMENT_REVIEW")
        self.assertEqual(docket["authority"]["external_authority"], "NONE_GRANTED")
        self.assertEqual(docket["authority"]["external_actions"], 0)
        self.assertEqual(docket["authority"]["network_requests"], 0)
        self.assertEqual(docket["authority"]["wallet_connections"], 0)
        self.assertEqual(docket["authority"]["live_token_movements"], 0)
        self.assertFalse(docket["settlement"]["live_token_movement"])

    def test_08_schema_declares_v3_chain_and_four_terminal_states(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema"]["const"], "goalos.agi_jobs_v0_v2.evidence_docket.v3")
        self.assertIn("run_commitment", schema["required"])
        artifacts = schema["properties"]["evidence"]["properties"]["artifacts"]
        self.assertEqual(artifacts["minItems"], 24)
        self.assertEqual(artifacts["maxItems"], 24)
        terminals = schema["properties"]["authority"]["properties"]["terminal_state"]["enum"]
        self.assertEqual(set(terminals), {"HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "DISPUTE_OPEN", "SAFE_HOLD"})

    def test_09_manifest_hashes_every_declared_output(self) -> None:
        manifest = json.loads((self.site / "agi-jobs-v0-v2-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "goalos.agi_jobs_v0_v2.website_manifest.v3")
        self.assertEqual(manifest["experience"]["constitutional_gates"], 16)
        self.assertEqual(manifest["experience"]["agent_guilds"], 12)
        self.assertEqual(manifest["experience"]["validator_seats"], 9)
        self.assertEqual(manifest["experience"]["evidence_artifacts"], 24)
        self.assertEqual(manifest["experience"]["public_surfaces"], 5)
        for relative, record in manifest["files"].items():
            path = self.site / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha(path), record["sha256"], relative)
            self.assertEqual(path.stat().st_size, record["bytes"], relative)

    def test_10_companion_manifests_reconcile_without_losing_integrity(self) -> None:
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
        result = subprocess.run(
            [sys.executable, str(VERIFY), "--site", str(self.site), "--root", str(ROOT), "--baseline", str(self.baseline), "--schema", str(SCHEMA), "--output", str(output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["preservation"]["removed"], [])
        self.assertEqual(report["preservation"]["unexpected_changed"], [])
        self.assertEqual(report["preservation"]["unexpected_added"], [])

    def test_12_second_build_is_idempotent(self) -> None:
        tracked = [
            *PAGES,
            "assets/agi-jobs-v0-v2.css",
            "assets/agi-jobs-v0-v2.js",
            "data/agi-jobs-v0-v2.json",
            "downloads/agi-jobs-v0-v2/sample-agi-jobs-evidence-docket.json",
            "agi-jobs-v0-v2-manifest.json",
            "meta-agentic-alpha-agi-manifest.json",
            "agi-alpha-node-v0-manifest.json",
            *SHARED,
        ]
        before = {item: sha(self.site / item) for item in tracked}
        env = dict(os.environ, SOURCE_DATE_EPOCH="1782259200")
        subprocess.run([sys.executable, str(BUILD), "--site", str(self.site), "--root", str(ROOT)], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
        after = {item: sha(self.site / item) for item in tracked}
        self.assertEqual(before, after)

    def test_13_javascript_and_python311_preflight_are_clean(self) -> None:
        javascript = ROOT / "website" / "features" / "agi-jobs-v0-v2" / "assets" / "agi-jobs-v0-v2.js"
        result = subprocess.run(["node", "--check", str(javascript)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = javascript.read_text(encoding="utf-8")
        for forbidden in ["fetch(", "XMLHttpRequest", "WebSocket(", "localStorage", "sessionStorage", "ethereum.request"]:
            self.assertNotIn(forbidden, text)
        for required in ["window.__AGI_JOBS_STATE__", "sha256", "pareto", "HUMAN_SETTLEMENT_REVIEW", "DISPUTE_OPEN", "SAFE_HOLD"]:
            self.assertIn(required, text)

        scripts = [BUILD, SNAPSHOT, VERIFY, VISUAL]
        for script in scripts:
            source = script.read_text(encoding="utf-8")
            ast.parse(source, filename=str(script), feature_version=(3, 11))
        compile_result = subprocess.run([sys.executable, "-m", "py_compile", *map(str, scripts)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(compile_result.returncode, 0, compile_result.stdout + compile_result.stderr)


if __name__ == "__main__":
    unittest.main()
