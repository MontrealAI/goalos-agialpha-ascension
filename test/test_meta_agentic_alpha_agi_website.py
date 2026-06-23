from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("goalos_meta_agentic_builder", ROOT / "scripts" / "website" / "build_meta_agentic_alpha_agi.py")
VERIFIER = load_module("goalos_meta_agentic_verifier", ROOT / "scripts" / "website" / "verify_meta_agentic_alpha_agi.py")


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


class MetaAgenticAlphaAgiWebsiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.site = Path(self.temp.name) / "site"
        (self.site / "assets").mkdir(parents=True)
        (self.site / "assets" / "goalos-v86-preserve.css").write_text("body{margin:0}\n", encoding="utf-8")
        (self.site / "assets" / "goalos-v86-dynamic-ai.js").write_text("document.documentElement.dataset.v86='ready';\n", encoding="utf-8")
        (self.site / "assets" / "preserved.js").write_text("window.preserved=true;\n", encoding="utf-8")
        (self.site / "index.html").write_text(
            "<!doctype html><html><head><title>GoalOS</title></head><body><header><nav><a href='index.html'>Home</a></nav></header><main><h1>GoalOS</h1></main></body></html>\n",
            encoding="utf-8",
        )
        (self.site / "mission-os.html").write_text("<!doctype html><html><body>Mission OS</body></html>\n", encoding="utf-8")
        (self.site / "preserved.html").write_text("<!doctype html><html><body>Preserve me exactly.</body></html>\n", encoding="utf-8")
        (self.site / "routes.json").write_text(json.dumps({"version": "test", "routes": ["index.html", "mission-os.html", "preserved.html"]}), encoding="utf-8")
        (self.site / "site-status.json").write_text(json.dumps({"status": "test"}), encoding="utf-8")
        (self.site / "sitemap.xml").write_text("<?xml version='1.0'?><urlset><url><loc>./index.html</loc></url>\n</urlset>\n", encoding="utf-8")
        self.content = ROOT / "content" / "meta-agentic-alpha-agi.json"
        self.source = ROOT / "website" / "features" / "meta-agentic-alpha-agi"
        self.previous_epoch = os.environ.get("SOURCE_DATE_EPOCH")
        os.environ["SOURCE_DATE_EPOCH"] = "1782172800"

    def tearDown(self) -> None:
        if self.previous_epoch is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = self.previous_epoch
        self.temp.cleanup()

    def test_release_contract_is_complete_and_default_deny(self) -> None:
        data = json.loads(self.content.read_text(encoding="utf-8"))
        BUILDER.validate_release(data)
        self.assertEqual(data["release_title"], BUILDER.RELEASE_TITLE)
        self.assertEqual(data["version"], "2.0.0-ascension-alpha")
        self.assertEqual(len(data["mission_flow"]), 8)
        self.assertEqual(len(data["agents"]), 9)
        self.assertEqual(len(data["objectives"]), 5)
        self.assertEqual(len(data["artifacts"]), 16)
        self.assertEqual(data["candidate_engine"]["generations"], 4)
        self.assertEqual(data["candidate_engine"]["population_per_generation"], 6)
        self.assertEqual(data["candidate_engine"]["generations"] * data["candidate_engine"]["population_per_generation"], 24)
        self.assertFalse(data["security"]["external_dependencies"])
        self.assertFalse(data["security"]["network_writes"])
        self.assertFalse(data["security"]["wallet_connection"])
        self.assertTrue(data["security"]["human_review_required"])
        self.assertEqual(data["security"]["settlement_mode"], "none")

    def test_build_is_additive_complete_and_verifiable(self) -> None:
        canonical = ROOT / "website" / "v86_actual_site"
        before = tree_digest(canonical)
        report = BUILDER.build(self.site, self.content, self.source)
        after = tree_digest(canonical)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(before, after)
        for relative in [
            "meta-agentic-alpha-agi.html",
            "meta-agentic-alpha-agi-architecture.html",
            "meta-agentic-alpha-agi-manifest.json",
            "assets/meta-agentic-alpha-agi.css",
            "assets/meta-agentic-alpha-agi.js",
            "data/meta-agentic-alpha-agi.json",
        ]:
            self.assertTrue((self.site / relative).is_file(), relative)
        verification = VERIFIER.verify(self.site)
        failures = [item for item in verification["checks"] if item["status"] != "PASS"]
        self.assertEqual(verification["status"], "PASS", failures)
        self.assertGreaterEqual(verification["checks_total"], 50)

    def test_build_preserves_every_unrelated_file_byte_for_byte(self) -> None:
        preserved = {
            "mission-os.html": (self.site / "mission-os.html").read_bytes(),
            "preserved.html": (self.site / "preserved.html").read_bytes(),
            "assets/preserved.js": (self.site / "assets" / "preserved.js").read_bytes(),
            "assets/goalos-v86-preserve.css": (self.site / "assets" / "goalos-v86-preserve.css").read_bytes(),
            "assets/goalos-v86-dynamic-ai.js": (self.site / "assets" / "goalos-v86-dynamic-ai.js").read_bytes(),
        }
        BUILDER.build(self.site, self.content, self.source)
        for relative, expected in preserved.items():
            self.assertEqual((self.site / relative).read_bytes(), expected, relative)

    def test_second_build_is_byte_idempotent(self) -> None:
        BUILDER.build(self.site, self.content, self.source)
        first = tree_digest(self.site)
        BUILDER.build(self.site, self.content, self.source)
        second = tree_digest(self.site)
        self.assertEqual(first, second)
        index = (self.site / "index.html").read_text(encoding="utf-8")
        for marker in BUILDER.MARKERS:
            self.assertEqual(index.count(marker), 1, marker)
        routes = json.loads((self.site / "routes.json").read_text(encoding="utf-8"))["routes"]
        self.assertEqual(routes.count("meta-agentic-alpha-agi.html"), 1)
        self.assertEqual(routes.count("meta-agentic-alpha-agi-architecture.html"), 1)
        sitemap = (self.site / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(sitemap.count("./meta-agentic-alpha-agi.html"), 1)
        self.assertEqual(sitemap.count("./meta-agentic-alpha-agi-architecture.html"), 1)

    def test_manifest_v2_describes_real_institution_foundry(self) -> None:
        BUILDER.build(self.site, self.content, self.source)
        manifest = json.loads((self.site / "meta-agentic-alpha-agi-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "goalos.meta_agentic_alpha_agi.website_manifest.v2")
        self.assertEqual(manifest["experience"]["default_population"], 24)
        self.assertEqual(manifest["experience"]["selection"], "pareto-frontier-plus-posture-weighting")
        self.assertTrue(manifest["experience"]["human_authorization_required"])
        self.assertFalse(manifest["integration"]["canonical_v86_source_modified"])
        self.assertGreaterEqual(len(manifest["files"]), 9)

    def test_homepage_integration_is_single_additive_gateway(self) -> None:
        BUILDER.build(self.site, self.content, self.source)
        index = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index.count('class="maa-home-gateway"'), 1)
        self.assertEqual(index.count('assets/meta-agentic-alpha-agi.css'), 1)
        self.assertIn("Enter the Institution Foundry", index)
        self.assertIn("evolve twenty-four rival agent institutions", index)
        self.assertIn("all external authority withheld", index)
        self.assertIn("<h1>GoalOS</h1>", index)

    def test_browser_runtime_source_contains_genuine_evolution_and_proof_boundary(self) -> None:
        javascript = (self.source / "assets" / "meta-agentic-alpha-agi.js").read_text(encoding="utf-8")
        for token in [
            "createCandidatePopulation",
            "dominates",
            "markParetoFrontier",
            "selectCandidate",
            "renderLineageGraph",
            "renderParetoPlot",
            "goalos.meta_agentic_alpha_agi.evidence_docket.v2",
            "deterministic_seed",
            "HUMAN_REVIEW_READY",
            "factual_correctness: 'NOT_CERTIFIED'",
            "external_actions: 0",
            "authority: 'NONE_GRANTED'",
        ]:
            self.assertIn(token, javascript)
        self.assertEqual(javascript.count("fetch("), 1)
        self.assertNotIn("localStorage", javascript)
        self.assertNotIn("window.ethereum", javascript)
        self.assertNotIn("new Function", javascript)

    def test_templates_are_semantic_accessible_and_responsive(self) -> None:
        experience = (self.source / "templates" / "meta-agentic-alpha-agi.html").read_text(encoding="utf-8")
        architecture = (self.source / "templates" / "meta-agentic-alpha-agi-architecture.html").read_text(encoding="utf-8")
        css = (self.source / "assets" / "meta-agentic-alpha-agi.css").read_text(encoding="utf-8")
        for token in ["Content-Security-Policy", 'id="maa-mission-form"', 'id="maa-lineage-svg"', 'id="maa-pareto-svg"', 'id="maa-download-md"', 'aria-live="polite"']:
            self.assertIn(token, experience)
        for token in ['id="maa-translation-map"', 'id="maa-architecture-stages"', 'id="maa-governance-grid"']:
            self.assertIn(token, architecture)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("@media (max-width:720px)", css)

    def test_existing_v86_autonomous_actions_build_test_and_deploy_feature(self) -> None:
        final = (ROOT / ".github" / "workflows" / "goalos-agialpha-ascension-v86-final.yml").read_text(encoding="utf-8")
        smoke = (ROOT / ".github" / "workflows" / "goalos-agialpha-ascension-v86-smoke-test.yml").read_text(encoding="utf-8")
        for workflow in [final, smoke]:
            self.assertIn("content/meta-agentic-alpha-agi.json", workflow)
            self.assertIn("website/features/meta-agentic-alpha-agi/**", workflow)
            self.assertIn("python3 scripts/website/build_meta_agentic_alpha_agi.py --site site", workflow)
            self.assertIn("python3 scripts/website/verify_meta_agentic_alpha_agi.py --site site", workflow)
            self.assertIn("python3 scripts/website/visual_check_meta_agentic_alpha_agi.py", workflow)
        self.assertIn("actions/upload-pages-artifact@v4", final)
        self.assertIn("actions/deploy-pages@v4", final)


if __name__ == "__main__":
    unittest.main()
