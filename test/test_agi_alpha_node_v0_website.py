from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "website" / "build_agi_alpha_node_v0.py"
META_BUILD_PATH = ROOT / "scripts" / "website" / "build_meta_agentic_alpha_agi.py"
CONTENT_PATH = ROOT / "content" / "agi-alpha-node-v0.json"
SOURCE_PATH = ROOT / "website" / "features" / "agi-alpha-node-v0"
V86_PATH = ROOT / "website" / "v86_actual_site"
FINAL_WORKFLOW = ROOT / ".github" / "workflows" / "goalos-agialpha-ascension-v86-final.yml"
SMOKE_WORKFLOW = ROOT / ".github" / "workflows" / "goalos-agialpha-ascension-v86-smoke-test.yml"
RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module(BUILD_PATH, "goalos_node_build")
META_BUILD = load_module(META_BUILD_PATH, "goalos_meta_build_for_node_test")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): file_hash(path) for path in sorted(root.rglob("*")) if path.is_file()}


class AGIAlphaNodeWebsiteTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.old_epoch = os.environ.get("SOURCE_DATE_EPOCH")
        os.environ["SOURCE_DATE_EPOCH"] = "1782172800"

    def tearDown(self) -> None:
        if self.old_epoch is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = self.old_epoch

    def build_site(self, include_meta: bool = True) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        site = Path(temporary.name) / "site"
        shutil.copytree(V86_PATH, site)
        if include_meta:
            META_BUILD.build(site, ROOT / "content" / "meta-agentic-alpha-agi.json", ROOT / "website" / "features" / "meta-agentic-alpha-agi")
        BUILD.build(site, CONTENT_PATH, SOURCE_PATH)
        return temporary, site

    def test_release_contract_and_default_deny(self) -> None:
        data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["release_title"], RELEASE_TITLE)
        self.assertEqual(len(data["pipeline"]), 8)
        self.assertEqual(len(data["peers"]), 8)
        self.assertEqual(len(data["validators"]), 7)
        self.assertEqual(len(data["guardians"]), 5)
        self.assertEqual(len(data["artifacts"]), 14)
        self.assertEqual(data["pipeline"][-1]["state"], "HUMAN_REVIEW_REQUIRED")
        expected_false = ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "local_storage", "live_ens_resolution", "live_compute"]
        for key in expected_false:
            self.assertIs(data["security"][key], False)
        self.assertIs(data["security"]["human_review_required"], True)
        self.assertEqual(data["security"]["external_authority"], "none")

    def test_build_is_additive_and_canonical_source_is_untouched(self) -> None:
        before = tree_hashes(V86_PATH)
        temporary, site = self.build_site()
        try:
            self.assertEqual(tree_hashes(V86_PATH), before)
            self.assertTrue((site / "agi-alpha-node-v0.html").is_file())
            self.assertTrue((site / "agi-alpha-node-v0-architecture.html").is_file())
        finally:
            temporary.cleanup()

    def test_unrelated_generated_files_and_meta_release_are_preserved(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        site = Path(temporary.name) / "site"
        shutil.copytree(V86_PATH, site)
        META_BUILD.build(site, ROOT / "content" / "meta-agentic-alpha-agi.json", ROOT / "website" / "features" / "meta-agentic-alpha-agi")
        before = tree_hashes(site)
        BUILD.build(site, CONTENT_PATH, SOURCE_PATH)
        after = tree_hashes(site)
        mutable = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
        node_prefixes = ("agi-alpha-node-v0", "assets/agi-alpha-node-v0", "data/agi-alpha-node-v0", "qa/agi-alpha-node-v0")
        for relative, digest in before.items():
            if relative in mutable or relative.startswith(node_prefixes):
                continue
            self.assertEqual(after.get(relative), digest, relative)
        for relative in ["meta-agentic-alpha-agi.html", "meta-agentic-alpha-agi-architecture.html", "meta-agentic-alpha-agi-manifest.json", "assets/meta-agentic-alpha-agi.css", "assets/meta-agentic-alpha-agi.js", "data/meta-agentic-alpha-agi.json"]:
            self.assertEqual(after[relative], before[relative], relative)
        temporary.cleanup()

    def test_build_is_idempotent_with_fixed_epoch(self) -> None:
        temporary, site = self.build_site()
        try:
            first = tree_hashes(site)
            BUILD.build(site, CONTENT_PATH, SOURCE_PATH)
            second = tree_hashes(site)
            self.assertEqual(first, second)
            index = (site / "index.html").read_text(encoding="utf-8")
            for marker in BUILD.MARKERS:
                self.assertEqual(index.count(marker), 1, marker)
        finally:
            temporary.cleanup()

    def test_homepage_routes_sitemap_and_meta_coexistence(self) -> None:
        temporary, site = self.build_site()
        try:
            index = (site / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="agi-alpha-node-v0"', index)
            self.assertGreaterEqual(index.count('href="agi-alpha-node-v0.html"'), 2)
            self.assertIn("GOALOS_META_AGENTIC_ALPHA_AGI_HOME_START", index)
            self.assertIn("GOALOS_AGI_ALPHA_NODE_V0_HOME_START", index)
            routes = json.loads((site / "routes.json").read_text(encoding="utf-8"))
            self.assertIn("agi-alpha-node-v0.html", routes["routes"])
            self.assertEqual(routes["agi_alpha_node_v0"]["external_actions"], 0)
            sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
            self.assertEqual(sitemap.count("./agi-alpha-node-v0.html"), 1)
            self.assertEqual(sitemap.count("./agi-alpha-node-v0-architecture.html"), 1)
        finally:
            temporary.cleanup()

    def test_manifest_integrity(self) -> None:
        temporary, site = self.build_site()
        try:
            manifest = json.loads((site / "agi-alpha-node-v0-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], "goalos.agi_alpha_node_v0.website_manifest.v1")
            self.assertEqual(manifest["experience"]["final_state"], "HUMAN_REVIEW_REQUIRED")
            self.assertEqual(manifest["experience"]["external_actions"], 0)
            for relative, record in manifest["files"].items():
                path = site / relative
                self.assertTrue(path.is_file(), relative)
                self.assertEqual(file_hash(path), record["sha256"], relative)
                self.assertEqual(path.stat().st_size, record["bytes"], relative)
        finally:
            temporary.cleanup()

    def test_runtime_is_substantive_deterministic_and_network_free(self) -> None:
        javascript = (SOURCE_PATH / "assets" / "agi-alpha-node-v0.js").read_text(encoding="utf-8")
        for token in ["createPeerRoute", "calculateAlphaWorkUnit", "createValidatorConsensus", "buildNodeEvidenceDocket", "goalos.agi_alpha_node_v0.node_evidence_docket.v1", "HUMAN_REVIEW_REQUIRED", "dissent_preserved", "deterministic_seed", "external_actions: 0", "authority: 'NONE_GRANTED'", "factual_correctness: 'NOT_CERTIFIED'"]:
            self.assertIn(token, javascript)
        for forbidden in ["fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "window.ethereum", "eth_requestAccounts", "WebSocket(", "EventSource("]:
            self.assertNotIn(forbidden, javascript)

    def test_templates_are_accessible_responsive_and_complete(self) -> None:
        flagship = (SOURCE_PATH / "templates" / "agi-alpha-node-v0.html").read_text(encoding="utf-8")
        architecture = (SOURCE_PATH / "templates" / "agi-alpha-node-v0-architecture.html").read_text(encoding="utf-8")
        stylesheet = (SOURCE_PATH / "assets" / "agi-alpha-node-v0.css").read_text(encoding="utf-8")
        for text in [flagship, architecture]:
            self.assertIn("Content-Security-Policy", text)
            self.assertIn("connect-src 'none'", text)
            self.assertIn('id="aan-release-data"', text)
            self.assertIn('aria-label=', text)
            self.assertIn('aan-nav-toggle', text)
        for token in ["@media (max-width:980px)", "@media (max-width:640px)", "prefers-reduced-motion", ":focus-visible", ".aan-home-gateway", ".aan-validator-card.dissent"]:
            self.assertIn(token, stylesheet)

    def test_autonomous_workflows_include_node_build_verify_browser_and_deploy(self) -> None:
        required = [
            "content/agi-alpha-node-v0.json",
            "website/features/agi-alpha-node-v0/**",
            "build_agi_alpha_node_v0.py",
            "verify_agi_alpha_node_v0.py",
            "visual_check_agi_alpha_node_v0.py",
            "test_agi_alpha_node_v0_website.py",
            "site/agi-alpha-node-v0.html",
            "site/agi-alpha-node-v0-architecture.html",
        ]
        for workflow in [FINAL_WORKFLOW, SMOKE_WORKFLOW]:
            text = workflow.read_text(encoding="utf-8")
            for token in required:
                self.assertIn(token, text, f"{workflow.name}: {token}")
            self.assertIn("build_meta_agentic_alpha_agi.py", text)
            self.assertIn("Reject archives and private operator material", text)
        final_text = FINAL_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("actions/upload-pages-artifact@v4", final_text)
        self.assertIn("actions/deploy-pages@v4", final_text)


if __name__ == "__main__":
    unittest.main()
