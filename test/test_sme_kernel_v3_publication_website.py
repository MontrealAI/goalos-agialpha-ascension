#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content/sme-kernel-v3-institutional-publication.json"
KERNEL_CONTENT = ROOT / "content/sme-kernel-v3.json"
ASSETS = ROOT / "website/features/sme-kernel-v3-publication/assets"
PAGES = [
  "sovereign-machine-economy-kernel-v3-paper.html",
  "sovereign-machine-economy-kernel-v3-use-cases.html",
  "sovereign-machine-economy-kernel-v3-publication-proof.html",
]
KERNEL_PAGES = [
  "sovereign-machine-economy-kernel-v3.html",
  "sovereign-machine-economy-kernel-v3-protocol.html",
  "sovereign-machine-economy-kernel-v3-chronicle.html",
  "sovereign-machine-economy-kernel-v3-verifier.html",
  "sovereign-machine-economy-kernel-v3-sdk.html",
]
MANIFESTS = [
  ("meta-agentic-alpha-agi-manifest.json", "goalos.meta_agentic_alpha_agi.website_manifest.v2"),
  ("agi-alpha-node-v0-manifest.json", "goalos.agi_alpha_node_v0.website_manifest.v2"),
  ("agi-jobs-v0-v2-manifest.json", "goalos.agi_jobs_v0_v2.website_manifest.v3"),
  ("sovereign-machine-economy-manifest.json", "goalos.sovereign_machine_economy.website_manifest.v2"),
  ("sme-kernel-v3-manifest.json", "goalos.sme.kernel.v3.website_manifest.v1"),
]


def sha(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(path: Path) -> dict[str, object]:
  return {"sha256": sha(path), "bytes": path.stat().st_size}


def synthetic_kernel_page(name: str) -> str:
  cta = '<a class="kv3-btn" href="sovereign-machine-economy-kernel-v3-verifier.html">Verify a mission bundle</a>' if name == KERNEL_PAGES[0] else ""
  return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Kernel</title></head><body><nav><a class="kv3-home-link" href="sovereign-machine-economy.html">Machine Economy Ω</a></nav><main><h1>Kernel v3</h1>{cta}</main></body></html>'''


class PublicationTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls) -> None:
    cls.data = json.loads(CONTENT.read_text(encoding="utf-8"))
    cls.kernel = json.loads(KERNEL_CONTENT.read_text(encoding="utf-8"))

  def test_repository_aligned_content_contract(self) -> None:
    self.assertEqual(self.data["schema"], "goalos.sme_kernel_v3.institutional_publication.v2")
    self.assertEqual(self.data["release_id"], "GOALOS-AGIALPHA-SME-KERNEL-V3-INSTITUTIONAL-PUBLICATION-V3.0-R2")
    self.assertEqual(self.data["version"], "3.0.0")
    self.assertEqual(self.data["integration_revision"], "r2")
    self.assertEqual(len(self.data["kernel_metrics"]), 6)
    self.assertEqual(len(self.data["materials"]), 6)
    self.assertEqual(len(self.data["lineage"]), 4)
    self.assertEqual(len(self.data["use_cases"]), 10)
    self.assertEqual(len(self.data["case_studies"]), 7)
    self.assertEqual([item["id"] for item in self.data["use_cases"]], [f"UC-{index:02d}" for index in range(1, 11)])

  def test_current_autonomy_constellation_is_bound(self) -> None:
    alignment = self.data["repository_alignment"]
    self.assertEqual([item["id"] for item in self.kernel["autonomy_chain"]], alignment["autonomy_chain_ids"])
    self.assertEqual([item["label"] for item in self.kernel["autonomy_chain"]], alignment["autonomy_chain_labels"])
    self.assertEqual(alignment["kernel_interface_release"], "Autonomous End-to-End Constellation v3.2.0")
    self.assertEqual(len(self.kernel["states"]), 17)
    self.assertEqual(len(self.kernel["envelope_types"]), 10)
    self.assertEqual(len(self.kernel["roles"]), 5)

  def test_evolutionary_lineage_is_explicit(self) -> None:
    self.assertEqual([item["url"] for item in self.data["lineage"]], [
      "https://github.com/MontrealAI/AGI-Alpha-Agent-v0",
      "https://github.com/MontrealAI/AGI-Alpha-Node-v0",
      "https://github.com/MontrealAI/AGIJobsv0",
      "https://github.com/MontrealAI/goalos-agialpha-ascension",
    ])

  def test_publication_visuals_are_pinned(self) -> None:
    for item in self.data["assets"].values():
      self.assertEqual(sha(ASSETS / item["local"]), item["sha256"])

  def test_claim_boundary_is_explicit(self) -> None:
    boundary = self.data["claim_boundary"]
    self.assertIn("theoretical systems and protocol architecture", boundary["positive"])
    self.assertGreaterEqual(len(boundary["not_claimed"]), 8)
    self.assertTrue(any("AGI" in item for item in boundary["not_claimed"]))

  def test_source_only_verifier(self) -> None:
    subprocess.run([
      sys.executable,
      str(ROOT / "scripts/website/verify_sme_kernel_v3_publication.py"),
      "--root", str(ROOT),
      "--source-only",
    ], check=True, capture_output=True, text=True)

  def test_additive_build_and_full_verification(self) -> None:
    with tempfile.TemporaryDirectory() as temporary:
      work = Path(temporary)
      site = work / "site"
      site.mkdir()
      index = """<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>GoalOS Test</title></head><body><nav><a href=\"sovereign-machine-economy-kernel-v3.html\">Kernel</a><!-- GOALOS_SME_KERNEL_V3_NAV_END --></nav><main><h1>GoalOS</h1><section>Existing website</section><!-- GOALOS_SME_KERNEL_V3_HOME_END --></main></body></html>"""
      (site / "index.html").write_text(index, encoding="utf-8")
      for name in KERNEL_PAGES:
        (site / name).write_text(synthetic_kernel_page(name), encoding="utf-8")
      dump(site / "routes.json", {"version": "test", "routes": ["index.html", *KERNEL_PAGES]})
      (site / "sitemap.xml").write_text("<?xml version=\"1.0\" encoding=\"UTF-8\"?><urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"><url><loc>https://example.test/</loc></url></urlset>", encoding="utf-8")
      dump(site / "site-status.json", {"status": "PASS"})
      shared = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
      for filename, schema in MANIFESTS:
        declared = shared + (KERNEL_PAGES if filename == "sme-kernel-v3-manifest.json" else [])
        dump(site / filename, {"schema": schema, "files": {name: record(site / name) for name in declared}, "integration": {"reconciliations": []}})
      baseline = work / "baseline.json"
      subprocess.run([sys.executable, str(ROOT / "scripts/website/snapshot_sme_kernel_v3_publication_site.py"), "--site", str(site), "--output", str(baseline)], check=True, capture_output=True, text=True)
      environment = dict(os.environ, SOURCE_DATE_EPOCH="1782259200", GITHUB_SHA=self.data["repository_alignment"]["baseline_commit"])
      subprocess.run([
        sys.executable,
        str(ROOT / "scripts/website/build_sme_kernel_v3_publication.py"),
        "--site", str(site),
        "--root", str(ROOT),
      ], check=True, capture_output=True, text=True, env=environment)
      replay_environment = dict(environment, SOURCE_DATE_EPOCH="1782259260")
      subprocess.run([
        sys.executable,
        str(ROOT / "scripts/website/build_sme_kernel_v3_publication.py"),
        "--site", str(site),
        "--root", str(ROOT),
      ], check=True, capture_output=True, text=True, env=replay_environment)
      report = work / "verification.json"
      subprocess.run([
        sys.executable,
        str(ROOT / "scripts/website/verify_sme_kernel_v3_publication.py"),
        "--root", str(ROOT),
        "--site", str(site),
        "--baseline", str(baseline),
        "--output", str(report),
      ], check=True, capture_output=True, text=True)
      payload = json.loads(report.read_text(encoding="utf-8"))
      self.assertEqual(payload["status"], "PASS")
      self.assertEqual((site / "index.html").read_text(encoding="utf-8").count("GOALOS_SME_KERNEL_V3_PUBLICATION_HOME_START"), 1)
      for name in KERNEL_PAGES:
        self.assertEqual((site / name).read_text(encoding="utf-8").count("GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_LINK_START"), 1)
      generated = json.loads((site / "data/sme-kernel-v3-institutional-publication.json").read_text(encoding="utf-8"))
      self.assertEqual(len(generated["kernel_autonomy_chain"]), 6)
      self.assertEqual(generated["observed_repository_alignment"]["status"], "PASS")


if __name__ == "__main__":
  unittest.main()
