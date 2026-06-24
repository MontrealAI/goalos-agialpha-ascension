from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "agi-alpha-node-v0.json"
SOURCE = ROOT / "website" / "features" / "agi-alpha-node-v0"
CANONICAL = ROOT / "website" / "v86_actual_site"
BUILD_SCRIPT = ROOT / "scripts" / "website" / "build_agi_alpha_node_v0.py"
VERIFY_SCRIPT = ROOT / "scripts" / "website" / "verify_agi_alpha_node_v0.py"
SNAPSHOT_SCRIPT = ROOT / "scripts" / "website" / "snapshot_agi_alpha_node_v0_site.py"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def tree_digest(root: Path) -> str:
    value = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        value.update(path.relative_to(root).as_posix().encode())
        value.update(path.read_bytes())
    return value.hexdigest()


class AGIAlphaNodeV0WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.temp.name)
        cls.site = cls.work / "site"
        shutil.copytree(CANONICAL, cls.site)
        cls.canonical_before = tree_digest(CANONICAL)
        cls.baseline = cls.work / "baseline.json"
        subprocess.run(["python", str(SNAPSHOT_SCRIPT), "--site", str(cls.site), "--output", str(cls.baseline)], check=True, capture_output=True, text=True)
        env = dict(os.environ, SOURCE_DATE_EPOCH="1782216000")
        subprocess.run(["python", str(BUILD_SCRIPT), "--site", str(cls.site), "--root", str(ROOT)], check=True, capture_output=True, text=True, env=env)
        cls.data = json.loads((cls.site / "data" / "agi-alpha-node-v0.json").read_text())
        cls.sample = json.loads((cls.site / "downloads" / "agi-alpha-node-v0" / "sample-node-evidence-docket.json").read_text())

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_01_release_contract_is_prestigious_and_exact(self) -> None:
        self.assertEqual(self.data["release_title"], "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨")
        self.assertEqual(self.data["version"], "3.0.0-sovereign-citadel")
        self.assertEqual(self.data["tagline"], "One node. Many minds. Zero unearned authority.")
        self.assertEqual(self.data["status"], "interactive-sovereign-proof-node-digital-twin")

    def test_02_architecture_has_full_constitutional_depth(self) -> None:
        expected = {"pipeline": 10, "node_roles": 10, "peers": 12, "validators": 7, "guardians": 5, "artifacts": 16, "lineage_fingerprints": 15}
        for key, count in expected.items():
            self.assertEqual(len(self.data[key]), count, key)
        self.assertEqual(self.data["pipeline"][-1]["state"], "HUMAN_REVIEW_REQUIRED")

    def test_03_security_is_default_deny(self) -> None:
        security = self.data["security"]
        for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "local_storage", "live_ens_resolution", "live_compute"]:
            self.assertIs(security[key], False, key)
        self.assertEqual(security["external_authority"], "none")
        self.assertTrue(security["human_review_required"])

    def test_04_build_outputs_all_three_public_surfaces(self) -> None:
        for name in ["agi-alpha-node-v0.html", "agi-alpha-node-v0-architecture.html", "agi-alpha-node-v0-proof-ledger.html"]:
            self.assertTrue((self.site / name).is_file(), name)
        self.assertTrue((self.site / "assets" / "agi-alpha-node-v0.css").is_file())
        self.assertTrue((self.site / "assets" / "agi-alpha-node-v0.js").is_file())

    def test_05_homepage_integration_is_additive_and_idempotent(self) -> None:
        env = dict(os.environ, SOURCE_DATE_EPOCH="1782216000")
        before = {path.relative_to(self.site).as_posix(): digest(path) for path in self.site.rglob("*") if path.is_file()}
        subprocess.run(["python", str(BUILD_SCRIPT), "--site", str(self.site), "--root", str(ROOT)], check=True, capture_output=True, text=True, env=env)
        after = {path.relative_to(self.site).as_posix(): digest(path) for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        home = (self.site / "index.html").read_text()
        self.assertEqual(home.count("GOALOS_AGI_ALPHA_NODE_V0_HOME_START"), 1)
        self.assertEqual(home.count('id="agi-alpha-node-v0"'), 1)

    def test_06_sample_docket_has_valid_sixteen_link_chain(self) -> None:
        chain = self.sample["proof_chronicle"]["artifacts"]
        self.assertEqual(len(chain), 16)
        previous = "0" * 64
        for index, artifact in enumerate(chain, 1):
            payload = json.dumps(artifact["payload"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            artifact_hash = hashlib.sha256(payload.encode()).hexdigest()
            commitment = hashlib.sha256(f"{previous}:{artifact_hash}:{artifact['name']}".encode()).hexdigest()
            self.assertEqual(artifact["index"], index)
            self.assertEqual(artifact["previous_commitment"], previous)
            self.assertEqual(artifact["artifact_hash"], artifact_hash)
            self.assertEqual(artifact["commitment"], commitment)
            previous = commitment
        self.assertEqual(self.sample["proof_chronicle"]["chain_head"], previous)

    def test_07_sample_preserves_dissent_and_human_boundary(self) -> None:
        consensus = self.sample["validator_consensus"]
        self.assertTrue(consensus["quorum_met"])
        self.assertEqual(consensus["pass"], 6)
        self.assertEqual(consensus["dissent"], 1)
        self.assertEqual(consensus["reject"], 0)
        self.assertEqual(self.sample["authority"]["final_state"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(self.sample["authority"]["external_actions"], 0)

    def test_08_runtime_contains_fail_closed_paths_without_network_apis(self) -> None:
        js = (self.site / "assets" / "agi-alpha-node-v0.js").read_text()
        for forbidden in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "window.ethereum", "localStorage", "sessionStorage"]:
            self.assertNotIn(forbidden, js)
        for required in ["SAFE_HOLD", "HUMAN_REVIEW_REQUIRED", "createConsensus", "createGuardians", "createArtifactChain", "quarantined", "shadow"]:
            self.assertIn(required, js)

    def test_09_manifest_hashes_every_declared_output(self) -> None:
        manifest = json.loads((self.site / "agi-alpha-node-v0-manifest.json").read_text())
        self.assertEqual(manifest["schema"], "goalos.agi_alpha_node_v0.website_manifest.v2")
        for relative, entry in manifest["files"].items():
            path = self.site / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(digest(path), entry["sha256"], relative)
            self.assertEqual(path.stat().st_size, entry["bytes"], relative)

    def test_10_mainnet_record_keeps_claim_boundaries(self) -> None:
        record = self.data["mainnet_record"]
        self.assertEqual(record["contracts"], 48)
        self.assertEqual(record["verification"], "48/48")
        self.assertEqual(record["phase_b_grants"], "14/14")
        self.assertEqual(record["production_activation"], "NOT_ACTIVATED")
        self.assertEqual(record["user_fund_authorization"], "NO")
        self.assertEqual(record["source_identity"], "PENDING")

    def test_11_static_verifier_and_preservation_audit_pass(self) -> None:
        output = self.work / "verify.json"
        completed = subprocess.run(["python", str(VERIFY_SCRIPT), "--site", str(self.site), "--root", str(ROOT), "--baseline", str(self.baseline), "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads(output.read_text())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["checks_failed"], 0)
        self.assertEqual(report["preservation"]["removed"], [])
        self.assertEqual(report["preservation"]["unexpected_changed"], [])

    def test_12_canonical_v86_source_tree_is_byte_identical(self) -> None:
        self.assertEqual(tree_digest(CANONICAL), self.canonical_before)
        for relative in ["index.html", "routes.json", "site-status.json"]:
            self.assertNotIn("GOALOS_AGI_ALPHA_NODE_V0", (CANONICAL / relative).read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
