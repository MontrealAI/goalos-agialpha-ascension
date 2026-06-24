from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "website" / "build_sovereign_machine_economy.py"
SNAPSHOT = ROOT / "scripts" / "website" / "snapshot_sovereign_machine_economy_site.py"
VERIFY = ROOT / "scripts" / "website" / "verify_sovereign_machine_economy.py"
VISUAL = ROOT / "scripts" / "website" / "visual_check_sovereign_machine_economy.py"
CONTENT = ROOT / "content" / "sovereign-machine-economy.json"
SCHEMA = ROOT / "schemas" / "sovereign-machine-economy-docket.schema.json"
PAGES = [
    "sovereign-machine-economy.html",
    "sovereign-machine-economy-architecture.html",
    "sovereign-machine-economy-chronicle.html",
    "sovereign-machine-economy-atlas.html",
]
SHARED = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
COMPANIONS = [
    ("meta-agentic-alpha-agi-manifest.json", "goalos.meta_agentic_alpha_agi.website_manifest.v2", "goalos-meta-agentic-alpha-agi-ascension-002", "2.0.0-ascension-alpha"),
    ("agi-alpha-node-v0-manifest.json", "goalos.agi_alpha_node_v0.website_manifest.v2", "goalos-agialpha-ascension-agi-alpha-node-v0-omega", "3.0.0-sovereign-citadel"),
    ("agi-jobs-v0-v2-manifest.json", "goalos.agi_jobs_v0_v2.website_manifest.v3", "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002", "3.0.0-sovereign-work-civilization"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class SovereignMachineEconomyWebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.temp.name) / "site"
        cls.site.mkdir()
        homepage = """<!doctype html><html><head><title>GoalOS</title></head><body><nav><a href='index.html'>Home</a><!-- GOALOS_AGI_JOBS_V0_V2_NAV_END --></nav><main><section id='existing'>Preserved</section><!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_START --><section>Meta</section><!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END --><!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_START --><section>Node</section><!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_END --><!-- GOALOS_AGI_JOBS_V0_V2_HOME_START --><section>Jobs</section><!-- GOALOS_AGI_JOBS_V0_V2_HOME_END --></main></body></html>"""
        (cls.site / "index.html").write_text(homepage, encoding="utf-8")
        (cls.site / "routes.json").write_text(json.dumps({"version": "test", "routes": ["index.html"]}) + "\n", encoding="utf-8")
        (cls.site / "sitemap.xml").write_text("<?xml version='1.0'?><urlset></urlset>\n", encoding="utf-8")
        (cls.site / "site-status.json").write_text(json.dumps({"status": "fixture"}) + "\n", encoding="utf-8")
        for page in ["meta-agentic-alpha-agi.html", "agi-alpha-node-v0.html", "agi-jobs-v0-v2.html"]:
            (cls.site / page).write_text(f"<!doctype html><title>{page}</title>\n", encoding="utf-8")

        prior: list[str] = []
        for filename, schema, release_id, version in COMPANIONS:
            files = {name: {"sha256": sha(cls.site / name), "bytes": (cls.site / name).stat().st_size} for name in SHARED}
            for dependency in prior:
                files[dependency] = {"sha256": sha(cls.site / dependency), "bytes": (cls.site / dependency).stat().st_size}
            manifest = {
                "schema": schema,
                "release_id": release_id,
                "release_title": release_id,
                "version": version,
                "files": files,
                "integration": {"reconciliations": []},
            }
            (cls.site / filename).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            prior.append(filename)

        cls.baseline = Path(cls.temp.name) / "baseline.json"
        subprocess.run([sys.executable, str(SNAPSHOT), "--site", str(cls.site), "--output", str(cls.baseline)], cwd=ROOT, check=True, capture_output=True, text=True)
        env = dict(os.environ, SOURCE_DATE_EPOCH="1782320400")
        subprocess.run([sys.executable, str(BUILD), "--site", str(cls.site), "--root", str(ROOT)], cwd=ROOT, env=env, check=True, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_01_release_identity_and_constellation_are_exact(self) -> None:
        data = json.loads((self.site / "data" / "sovereign-machine-economy.json").read_text(encoding="utf-8"))
        self.assertEqual(data["release_id"], "GOALOS-SOVEREIGN-MACHINE-ECONOMY-001")
        self.assertEqual(data["release_title"], "GoalOS AGIALPHA Ascension — Sovereign Machine Economy")
        self.assertEqual(data["version"], "1.0.0-civilization")
        self.assertIn("META-AGENTIC α‑AGI", data["constellation_title"])
        self.assertIn("AGI Alpha Node v0", data["constellation_title"])
        self.assertIn("AGI Jobs v0 (v2)", data["constellation_title"])

    def test_02_constitutional_depth_is_complete(self) -> None:
        data = json.loads(CONTENT.read_text(encoding="utf-8"))
        expected = {"hero_metrics": 6, "presets": 5, "postures": 4, "risk_profiles": 4, "incidents": 5, "gates": 18, "artifacts": 36, "guardians": 7, "handoff_rules": 6, "claim_boundary": 6}
        for key, count in expected.items():
            self.assertEqual(len(data[key]), count, key)
        self.assertEqual(Counter(item["layer"] for item in data["artifacts"]), {"META": 12, "NODE": 12, "JOBS": 12})
        self.assertEqual([item["terminal"] for item in data["incidents"]], ["HUMAN_SETTLEMENT_REVIEW", "SAFE_HOLD", "SAFE_HOLD", "DISPUTE_OPEN", "HUMAN_REVIEW_REQUIRED"])

    def test_03_security_and_authority_are_default_deny(self) -> None:
        data = json.loads(CONTENT.read_text(encoding="utf-8"))
        for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "local_storage", "live_compute", "live_token_movement", "credential_issuance"]:
            self.assertIs(data["security"][key], False, key)
        self.assertEqual(data["security"]["external_authority"], "none")
        self.assertTrue(data["security"]["human_review_required"])

    def test_04_build_outputs_four_public_surfaces_and_evidence(self) -> None:
        for page in PAGES:
            self.assertGreater((self.site / page).stat().st_size, 5000, page)
        for relative in ["assets/sovereign-machine-economy.css", "assets/sovereign-machine-economy.js", "data/sovereign-machine-economy.json", "downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json", "sovereign-machine-economy-manifest.json", "qa/sovereign-machine-economy-build.json"]:
            self.assertTrue((self.site / relative).is_file(), relative)

    def test_05_homepage_routes_sitemap_and_status_are_additive(self) -> None:
        homepage = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn("<section id='existing'>Preserved</section>", homepage)
        for marker in ["GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_START", "GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_START", "GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_START"]:
            self.assertEqual(homepage.count(marker), 1, marker)
        self.assertEqual(homepage.count('href="sovereign-machine-economy.html">Machine Economy</a>'), 1)
        routes = json.loads((self.site / "routes.json").read_text(encoding="utf-8"))
        self.assertTrue(set(PAGES).issubset(set(routes["routes"])))
        self.assertEqual(routes["sovereign_machine_economy"]["external_actions"], 0)
        self.assertTrue(all(page in (self.site / "sitemap.xml").read_text(encoding="utf-8") for page in PAGES))
        status = json.loads((self.site / "site-status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["sovereign_machine_economy"]["constitutional_gates"], 18)
        self.assertEqual(status["sovereign_machine_economy"]["proof_artifacts"], 36)

    def test_06_sample_docket_has_valid_thirty_six_link_chain(self) -> None:
        docket = json.loads((self.site / "downloads" / "sovereign-machine-economy" / "sample-sovereign-economy-docket.json").read_text(encoding="utf-8"))
        chain = docket["evidence"]["artifacts"]
        self.assertEqual(len(chain), 36)
        previous = "0" * 64
        for item in chain:
            self.assertEqual(item["previous_commitment"], previous)
            commitment = hashlib.sha256(stable({"previous": previous, "payload": item["payload"]}).encode("utf-8")).hexdigest()
            self.assertEqual(item["commitment"], commitment)
            previous = commitment
        self.assertEqual(docket["evidence"]["chain_head"], previous)
        without = dict(docket)
        run_commitment = without.pop("run_commitment")
        self.assertEqual(run_commitment, hashlib.sha256(stable(without).encode("utf-8")).hexdigest())

    def test_07_handoffs_bind_all_three_sovereign_layers(self) -> None:
        docket = json.loads((self.site / "downloads" / "sovereign-machine-economy" / "sample-sovereign-economy-docket.json").read_text(encoding="utf-8"))
        self.assertEqual([(x["from"], x["to"]) for x in docket["handoffs"]], [("META", "NODE"), ("NODE", "JOBS"), ("JOBS", "HUMAN")])
        self.assertTrue(all(len(x["commitment"]) == 64 for x in docket["handoffs"]))
        self.assertEqual(docket["authority"]["terminal_state"], "HUMAN_SETTLEMENT_REVIEW")
        self.assertEqual(docket["authority"]["external_authority"], "NONE_GRANTED")
        self.assertEqual(docket["authority"]["external_actions"], 0)

    def test_08_json_schema_is_valid_and_accepts_sample_docket(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        docket = json.loads((self.site / "downloads" / "sovereign-machine-economy" / "sample-sovereign-economy-docket.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(docket)), [])
        self.assertEqual(schema["properties"]["evidence"]["properties"]["artifacts"]["maxItems"], 36)
        self.assertEqual(len(schema["properties"]["authority"]["properties"]["terminal_state"]["enum"]), 4)

    def test_09_companion_manifests_are_reconciled_without_deletion(self) -> None:
        for filename, schema, _, _ in COMPANIONS:
            manifest = json.loads((self.site / filename).read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], schema)
            self.assertTrue(any(item.get("release_id") == "GOALOS-SOVEREIGN-MACHINE-ECONOMY-001" for item in manifest["integration"]["reconciliations"]))
            for shared in SHARED:
                self.assertEqual(manifest["files"][shared]["sha256"], sha(self.site / shared))

    def test_10_static_verifier_proves_preservation(self) -> None:
        out = Path(self.temp.name) / "static.json"
        subprocess.run([sys.executable, str(VERIFY), "--site", str(self.site), "--root", str(ROOT), "--baseline", str(self.baseline), "--schema", str(SCHEMA), "--output", str(out)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["preservation"]["removed"], [])
        self.assertEqual(report["preservation"]["unexpected_changed"], [])
        self.assertEqual(report["preservation"]["unexpected_added"], [])

    def test_11_second_build_is_byte_identical(self) -> None:
        before = {str(path.relative_to(self.site)): sha(path) for path in self.site.rglob("*") if path.is_file()}
        env = dict(os.environ, SOURCE_DATE_EPOCH="1782320400")
        subprocess.run([sys.executable, str(BUILD), "--site", str(self.site), "--root", str(ROOT)], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
        after = {str(path.relative_to(self.site)): sha(path) for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_12_python_and_javascript_preflights_pass(self) -> None:
        for script in [BUILD, SNAPSHOT, VERIFY, VISUAL]:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script), feature_version=(3, 11))
        result = subprocess.run(["node", "--check", str(ROOT / "website" / "features" / "sovereign-machine-economy" / "assets" / "sovereign-machine-economy.js")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_13_runtime_contains_all_fail_closed_paths_without_network_apis(self) -> None:
        js = (ROOT / "website" / "features" / "sovereign-machine-economy" / "assets" / "sovereign-machine-economy.js").read_text(encoding="utf-8")
        for terminal in ["HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "DISPUTE_OPEN", "SAFE_HOLD"]:
            self.assertIn(terminal, js)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("XMLHttpRequest", js)
        self.assertIn("crypto.subtle.digest(\"SHA-256\"", js)


if __name__ == "__main__":
    unittest.main()
