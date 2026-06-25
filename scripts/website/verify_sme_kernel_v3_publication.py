#!/usr/bin/env python3
"""Verify the repository-aligned GoalOS Kernel v3 institutional publication source and generated site."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

FEATURE_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.v2"
MANIFEST_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.website_manifest.v2"
SNAPSHOT_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.prebuild_snapshot.v1"
BUILD_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.build_report.v2"
RELEASE_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.release_manifest.v2"
REPORT_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.verification_report.v2"
BASE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
RELEASE_PATH = "release/kernel-v3-institutional-publication-v3.0.0-r2/RELEASE_MANIFEST.json"
WORKFLOW_PATH = ".github/workflows/goalos-agialpha-ascension-v86-final.yml"
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
ASSETS = [
  "sme-kernel-v3-publication.css",
  "sme-kernel-v3-publication.js",
  "cover-institutional-use-case-edition-v3.png",
  "kernel-v3-figure-gallery.jpg",
  "kernel-v3-use-case-gallery.jpg",
]
SHARED = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
MANIFEST_CHAIN = [
  ("meta-agentic-alpha-agi-manifest.json", "goalos.meta_agentic_alpha_agi.website_manifest.v2"),
  ("agi-alpha-node-v0-manifest.json", "goalos.agi_alpha_node_v0.website_manifest.v2"),
  ("agi-jobs-v0-v2-manifest.json", "goalos.agi_jobs_v0_v2.website_manifest.v3"),
  ("sovereign-machine-economy-manifest.json", "goalos.sovereign_machine_economy.website_manifest.v2"),
  ("sme-kernel-v3-manifest.json", "goalos.sme.kernel.v3.website_manifest.v1"),
]
PROTECTED_SOURCE_PATHS = [
  "content/sme-kernel-v3.json",
  "docs/SOVEREIGN_MACHINE_ECONOMY_KERNEL_V3.md",
  "schemas/sme-kernel-v3-envelope.schema.json",
  "schemas/sme-kernel-v3-mission-bundle.schema.json",
  "scripts/website/build_sme_kernel_v3.py",
  "scripts/website/verify_sme_kernel_v3.py",
  "scripts/website/visual_check_sme_kernel_v3.py",
  "test/test_sme_kernel_v3_website.py",
  "website/features/sme-kernel-v3/assets/sme-kernel-v3-adapters.js",
  "website/features/sme-kernel-v3/assets/sme-kernel-v3-core.js",
  "website/features/sme-kernel-v3/assets/sme-kernel-v3-worker.js",
  "website/features/sme-kernel-v3/assets/sme-kernel-v3.css",
  "website/features/sme-kernel-v3/assets/sme-kernel-v3.js",
  "website/features/sme-kernel-v3/templates/sovereign-machine-economy-kernel-v3-chronicle.html",
  "website/features/sme-kernel-v3/templates/sovereign-machine-economy-kernel-v3-protocol.html",
  "website/features/sme-kernel-v3/templates/sovereign-machine-economy-kernel-v3-sdk.html",
  "website/features/sme-kernel-v3/templates/sovereign-machine-economy-kernel-v3-verifier.html",
  "website/features/sme-kernel-v3/templates/sovereign-machine-economy-kernel-v3.html",
]
HOMEPAGE_MARKERS = [
  "GOALOS_SME_KERNEL_V3_PUBLICATION_STYLE_START",
  "GOALOS_SME_KERNEL_V3_PUBLICATION_NAV_START",
  "GOALOS_SME_KERNEL_V3_PUBLICATION_HOME_START",
]
WORKFLOW_MARKERS = [
  "GOALOS_SME_KERNEL_V3_PUBLICATION_PATHS_START",
  "GOALOS_SME_KERNEL_V3_PUBLICATION_COMPILE_START",
  "GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_START",
  "GOALOS_SME_KERNEL_V3_PUBLICATION_SUMMARY_START",
  "GOALOS_SME_KERNEL_V3_PUBLICATION_ARTIFACTS_START",
]
PRIVATE_PATTERNS = [
  r"PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY",
  r"SEED_PHRASE",
  r"MNEMONIC",
  r"MAINNET_RPC_URL=",
  r"ETHERSCAN_API_KEY=",
]
ARCHIVE_SUFFIXES = {".zip", ".7z", ".tar", ".gz", ".rar"}


class AuditParser(HTMLParser):
  def __init__(self) -> None:
    super().__init__(convert_charrefs=True)
    self.ids: set[str] = set()
    self.links: list[dict[str, str]] = []
    self.images: list[dict[str, str]] = []
    self.h1_count = 0
    self.title_count = 0
    self.main_count = 0
    self.canonicals: list[str] = []
    self._json_capture = False
    self._json_parts: list[str] = []
    self.json_ld: list[str] = []

  def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
    values = {key: value or "" for key, value in attrs}
    if values.get("id"):
      self.ids.add(values["id"])
    if tag == "a":
      self.links.append(values)
    elif tag == "img":
      self.images.append(values)
    elif tag == "h1":
      self.h1_count += 1
    elif tag == "title":
      self.title_count += 1
    elif tag == "main":
      self.main_count += 1
    elif tag == "link" and values.get("rel") == "canonical":
      self.canonicals.append(values.get("href", ""))
    elif tag == "script" and values.get("type") == "application/ld+json":
      self._json_capture = True
      self._json_parts = []

  def handle_endtag(self, tag: str) -> None:
    if tag == "script" and self._json_capture:
      self.json_ld.append("".join(self._json_parts).strip())
      self._json_capture = False
      self._json_parts = []

  def handle_data(self, data: str) -> None:
    if self._json_capture:
      self._json_parts.append(data)


def sha(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
      digest.update(chunk)
  return digest.hexdigest()


def file_record(path: Path) -> dict[str, object]:
  return {"sha256": sha(path), "bytes": path.stat().st_size}


def load(path: Path) -> dict:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise ValueError(f"Expected JSON object: {path}")
  return value


def source_set_digest(root: Path, relatives: list[str]) -> tuple[str, dict[str, dict[str, object]], list[str]]:
  records: dict[str, dict[str, object]] = {}
  missing: list[str] = []
  for relative in sorted(relatives):
    path = root / relative
    if not path.is_file():
      missing.append(relative)
    else:
      records[relative] = file_record(path)
  material = "".join(f"{relative}\0{records[relative]['sha256']}\0{records[relative]['bytes']}\n" for relative in sorted(records))
  return hashlib.sha256(material.encode("utf-8")).hexdigest(), records, missing


def v86_tree_digest(root: Path) -> str:
  directory = root / "website/v86_actual_site"
  if not directory.is_dir():
    return "missing"
  lines = [f"{sha(path)}  {path.relative_to(root).as_posix()}\n" for path in sorted((item for item in directory.rglob("*") if item.is_file()), key=lambda item: item.relative_to(root).as_posix())]
  return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def record(checks: list[dict], name: str, passed: bool, detail: str) -> None:
  checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def verify_release_manifest(root: Path, data: dict, checks: list[dict]) -> None:
  path = root / RELEASE_PATH
  if not path.is_file():
    record(checks, "source.release_manifest", False, f"missing {RELEASE_PATH}")
    return
  release = load(path)
  files = release.get("files")
  failures: list[str] = []
  if release.get("schema") != RELEASE_SCHEMA:
    failures.append("schema")
  if release.get("release_id") != data.get("release_id"):
    failures.append("release id")
  if release.get("integration_revision") != "r2":
    failures.append("integration revision")
  if release.get("repository_alignment", {}).get("baseline_commit") != data.get("repository_alignment", {}).get("baseline_commit"):
    failures.append("baseline commit")
  if not isinstance(files, dict):
    failures.append("files object")
    files = {}
  for relative, expected in files.items():
    target = root / relative
    if not target.is_file():
      failures.append(f"missing {relative}")
    elif not isinstance(expected, dict) or expected.get("sha256") != sha(target) or expected.get("bytes") != target.stat().st_size:
      failures.append(f"drift {relative}")
  material = "".join(f"{relative}\0{files[relative].get('sha256')}\0{files[relative].get('bytes')}\n" for relative in sorted(files))
  observed = hashlib.sha256(material.encode("utf-8")).hexdigest()
  if release.get("source_file_count") != len(files):
    failures.append("source file count")
  if release.get("source_set_sha256") != observed:
    failures.append("source set digest")
  record(checks, "source.release_manifest", not failures, f"{len(files)} versioned integration files verified" if not failures else "; ".join(failures[:10]))


def assert_source(root: Path, checks: list[dict]) -> dict:
  required_relatives = [
    "content/sme-kernel-v3-institutional-publication.json",
    "website/features/sme-kernel-v3-publication/templates/base.html",
    *[f"website/features/sme-kernel-v3-publication/assets/{name}" for name in ASSETS],
    "scripts/website/build_sme_kernel_v3_publication.py",
    "scripts/website/snapshot_sme_kernel_v3_publication_site.py",
    "scripts/website/verify_sme_kernel_v3_publication.py",
    "scripts/website/visual_check_sme_kernel_v3_publication.py",
    "scripts/website/patch_v86_for_sme_kernel_v3_publication.py",
    "test/test_sme_kernel_v3_publication_website.py",
    "docs/SME_KERNEL_V3_INSTITUTIONAL_PUBLICATION.md",
    ".github/workflows/goalos-sme-kernel-v3-institutional-publication-smoke-test.yml",
    RELEASE_PATH,
  ]
  missing = [relative for relative in required_relatives if not (root / relative).is_file()]
  record(checks, "source.required_files", not missing, "all versioned source, QA, documentation, and release files present" if not missing else ", ".join(missing))
  content_path = root / "content/sme-kernel-v3-institutional-publication.json"
  if not content_path.is_file():
    return {}
  data = load(content_path)
  counts = {
    "artifacts": 4,
    "materials": 6,
    "metrics": 6,
    "kernel_metrics": 6,
    "reader_paths": 6,
    "lineage": 4,
    "architecture": 4,
    "use_cases": 10,
    "case_studies": 7,
    "validation": 8,
  }
  contract = (
    data.get("schema") == FEATURE_SCHEMA
    and data.get("release_id") == "GOALOS-AGIALPHA-SME-KERNEL-V3-INSTITUTIONAL-PUBLICATION-V3.0-R2"
    and data.get("version") == "3.0.0"
    and data.get("integration_revision") == "r2"
    and data.get("status") == "claim-bounded-repository-aligned-institutional-publication-suite"
    and data.get("doctrine") == "A model can answer. An agent can act. An institution must prove."
    and all(isinstance(data.get(key), list) and len(data[key]) == count for key, count in counts.items())
  )
  record(checks, "source.content_contract", contract, "repository-aligned v2 contract and all declared publication counts")
  identifiers = [item.get("id") for item in data.get("use_cases", [])] == [f"UC-{index:02d}" for index in range(1, 11)] and [item.get("id") for item in data.get("case_studies", [])] == list("ABCDEFG")
  record(checks, "source.identifiers", identifiers, "ten ordered use cases and seven ordered reference studies")
  lineage = [item.get("url") for item in data.get("lineage", [])]
  expected_lineage = [
    "https://github.com/MontrealAI/AGI-Alpha-Agent-v0",
    "https://github.com/MontrealAI/AGI-Alpha-Node-v0",
    "https://github.com/MontrealAI/AGIJobsv0",
    "https://github.com/MontrealAI/goalos-agialpha-ascension",
  ]
  publication_links = [*data.get("artifacts", []), *data.get("materials", [])]
  links_ok = str(data.get("canonical_suite_url", "")).startswith("https://montrealai.github.io/") and all(str(item.get("url", "")).startswith("https://montrealai.github.io/") for item in publication_links) and lineage == expected_lineage
  record(checks, "source.canonical_links", links_ok, "canonical publication host and four-repository lineage preserved")

  alignment = data.get("repository_alignment", {})
  kernel_path = root / "content/sme-kernel-v3.json"
  workflow_path = root / WORKFLOW_PATH
  kernel_ok = kernel_path.is_file() and sha(kernel_path) == alignment.get("kernel_content_sha256")
  kernel = load(kernel_path) if kernel_path.is_file() else {}
  phase_ids = [item.get("id") for item in kernel.get("autonomy_chain", [])]
  phase_labels = [item.get("label") for item in kernel.get("autonomy_chain", [])]
  counts_ok = len(kernel.get("autonomy_chain", [])) == 6 and len(kernel.get("states", [])) == 17 and len(kernel.get("envelope_types", [])) == 10 and len(kernel.get("roles", [])) == 5
  phase_ok = phase_ids == alignment.get("autonomy_chain_ids") and phase_labels == alignment.get("autonomy_chain_labels") and alignment.get("kernel_interface_release") == "Autonomous End-to-End Constellation v3.2.0"
  record(checks, "source.kernel_alignment", kernel_ok and counts_ok and phase_ok, "current six-stage v3.2.0 constellation, 17 states, 10 envelopes, and 5 authorities match the audited contract")

  workflow_raw = workflow_path.read_text(encoding="utf-8") if workflow_path.is_file() else ""
  workflow_sha = sha(workflow_path) if workflow_path.is_file() else "missing"
  unpatched = workflow_sha == alignment.get("active_workflow_sha256")
  patched = all(workflow_raw.count(marker) == 1 for marker in WORKFLOW_MARKERS) and "GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_END" in workflow_raw
  record(checks, "source.active_workflow", workflow_path.is_file() and (unpatched or patched), f"active v86 workflow {'matches audited pre-integration digest' if unpatched else 'contains the complete additive publication patch' if patched else 'drifted'}")

  protected_sha, protected_records, protected_missing = source_set_digest(root, PROTECTED_SOURCE_PATHS)
  protected_ok = not protected_missing and len(protected_records) == alignment.get("protected_source_file_count") == 18 and protected_sha == alignment.get("protected_source_set_sha256")
  record(checks, "source.protected_kernel_set", protected_ok, f"18 protected Kernel source files match {protected_sha}" if protected_ok else f"missing={protected_missing} observed={protected_sha}")
  observed_v86 = v86_tree_digest(root)
  v86_ok = observed_v86 == alignment.get("canonical_v86_tree_sha256") and alignment.get("canonical_v86_source_modified") is False
  record(checks, "source.canonical_v86_boundary", v86_ok, "canonical website/v86_actual_site tree remains byte-identical to the audited source")

  asset_dir = root / "website/features/sme-kernel-v3-publication/assets"
  asset_failures: list[str] = []
  for name, item in data.get("assets", {}).items():
    path = asset_dir / str(item.get("local", ""))
    if not path.is_file() or sha(path) != item.get("sha256"):
      asset_failures.append(name)
  pdf_meta_ok = all(re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))) and isinstance(item.get("bytes"), int) and item.get("bytes", 0) > 0 for item in data.get("artifacts", []) if item.get("id") != "source-suite")
  record(checks, "source.pinned_provenance", not asset_failures and pdf_meta_ok, "three publication visuals match pinned SHA-256 values and principal PDF metadata is fully recorded" if not asset_failures and pdf_meta_ok else f"visual failures={asset_failures}")

  template_path = root / "website/features/sme-kernel-v3-publication/templates/base.html"
  template = template_path.read_text(encoding="utf-8") if template_path.is_file() else ""
  tokens = {"@@TITLE@@", "@@DESCRIPTION@@", "@@CANONICAL@@", "@@OG_IMAGE@@", "@@PAPER_URL@@", "@@JSON_LD@@", "@@MAIN@@", "@@SUITE_URL@@", "@@REPO_URL@@", "@@INTEGRATION_REVISION@@", "@@ALIGNMENT_LABEL@@", "@@ALIGNMENT_COMMIT@@"}
  record(checks, "source.template_contract", all(token in template for token in tokens), "all SEO, structured-data, content, and repository-alignment tokens present")
  css_path = asset_dir / "sme-kernel-v3-publication.css"
  js_path = asset_dir / "sme-kernel-v3-publication.js"
  css = css_path.read_text(encoding="utf-8") if css_path.is_file() else ""
  js = js_path.read_text(encoding="utf-8") if js_path.is_file() else ""
  asset_security = "@import" not in css.lower() and not re.search(r"url\s*\(\s*['\"]?https?://", css, re.I) and "eval(" not in js and "new Function" not in js
  record(checks, "source.asset_security", asset_security, "no remote CSS imports, remote CSS URLs, eval, or dynamic Function execution")
  boundary = data.get("claim_boundary", {})
  record(checks, "source.claim_boundary", isinstance(boundary.get("positive"), str) and len(boundary.get("not_claimed", [])) >= 8, "positive scope and explicit non-claims remain publication-visible")

  smoke_path = root / ".github/workflows/goalos-sme-kernel-v3-institutional-publication-smoke-test.yml"
  smoke = smoke_path.read_text(encoding="utf-8") if smoke_path.is_file() else ""
  action_refs = re.findall(r"uses:\s*([^\s#]+)", smoke)
  action_pins_ok = bool(action_refs) and all(re.search(r"@[0-9a-f]{40}$", ref) for ref in action_refs)
  record(checks, "source.action_pins", action_pins_ok, f"{len(action_refs)} smoke-test action references pinned to full commit SHAs")
  verify_release_manifest(root, data, checks)
  return data


def parse_page(path: Path) -> AuditParser:
  parser = AuditParser()
  parser.feed(path.read_text(encoding="utf-8", errors="replace"))
  return parser


def resolve_local(site: Path, current: str, value: str) -> tuple[Path | None, str]:
  if not value or value.startswith(("mailto:", "tel:", "javascript:", "data:")):
    return None, ""
  parsed = urlparse(value)
  if parsed.scheme in {"http", "https"} or parsed.netloc:
    return None, parsed.fragment
  path_part = unquote(parsed.path)
  if not path_part:
    target = site / current
  elif path_part.startswith("/"):
    target = site / path_part.lstrip("/")
  else:
    target = (site / current).parent / path_part
  if target.is_dir():
    target = target / "index.html"
  return target.resolve(), parsed.fragment


def audit_page(site: Path, relative: str, checks: list[dict], data: dict) -> None:
  path = site / relative
  parser = parse_page(path)
  structural = parser.h1_count == 1 and parser.title_count == 1 and parser.main_count == 1 and parser.canonicals == [BASE_URL + relative]
  record(checks, f"page.{relative}.structure", structural, "one title, one h1, one main landmark, and exact canonical URL")
  json_ok = len(parser.json_ld) == 1
  if json_ok:
    try:
      payload = json.loads(parser.json_ld[0])
      json_ok = payload.get("@type") == "ScholarlyArticle" and payload.get("version") == data.get("version") and payload.get("url") == BASE_URL + relative
    except json.JSONDecodeError:
      json_ok = False
  record(checks, f"page.{relative}.structured_data", json_ok, "valid ScholarlyArticle JSON-LD bound to the canonical page")
  raw = path.read_text(encoding="utf-8")
  unresolved = "@@" in raw
  record(checks, f"page.{relative}.tokens", not unresolved, "no unresolved generation tokens")
  failures: list[str] = []
  for attrs in parser.links:
    href = attrs.get("href", "")
    if href.startswith(("http://", "https://")) and attrs.get("target") == "_blank" and "noopener" not in set(attrs.get("rel", "").split()):
      failures.append(f"noopener {href}")
    target, fragment = resolve_local(site, relative, href)
    if target is None:
      continue
    try:
      target.relative_to(site.resolve())
    except ValueError:
      failures.append(f"escape {href}")
      continue
    if not target.is_file():
      failures.append(f"missing {href}")
    elif fragment and fragment not in parse_page(target).ids:
      failures.append(f"fragment {href}")
  for attrs in parser.images:
    src = attrs.get("src", "")
    target, _ = resolve_local(site, relative, src)
    if target is None or not target.is_file():
      failures.append(f"image {src}")
    if not attrs.get("alt") or not attrs.get("width") or not attrs.get("height"):
      failures.append(f"image metadata {src}")
  record(checks, f"page.{relative}.references", not failures, "all local references resolve; images are described and dimensioned; new-tab links are protected" if not failures else "; ".join(failures[:8]))
  if relative == PAGES[0]:
    feature = raw.count('data-alignment-phase="') == 6 and raw.count('class="pub-artifact"') == 4 and "Autonomous End-to-End Constellation v3.2.0" in raw and 'class="pub-alignment-strip"' in raw
  elif relative == PAGES[1]:
    feature = raw.count("data-use-category=") == 10 and raw.count('class="pub-case"') == 7 and "Institutional deployment atlas" in raw
  else:
    feature = 'id="repository-alignment"' in raw and 'id="publication-citation"' in raw and 'data-copy-citation="#publication-citation"' in raw and data["repository_alignment"]["baseline_commit"] in raw
  record(checks, f"page.{relative}.feature_contract", feature, "page-specific institutional publication contract present")


def verify_manifest_hashes(site: Path, manifest: dict, checks: list[dict]) -> None:
  entries = manifest.get("files")
  failures: list[str] = []
  if not isinstance(entries, dict):
    failures.append("files object")
    entries = {}
  for relative, expected in entries.items():
    path = site / relative
    if not path.is_file():
      failures.append(f"missing {relative}")
    elif not isinstance(expected, dict) or expected.get("sha256") != sha(path) or expected.get("bytes") != path.stat().st_size:
      failures.append(f"drift {relative}")
  record(checks, "site.manifest_hashes", not failures, f"{len(entries)} generated file records verified" if not failures else "; ".join(failures[:8]))


def source_subset_matches(generated: dict, source: dict) -> bool:
  return all(generated.get(key) == value for key, value in source.items())


def assert_site(root: Path, site: Path, baseline: Path | None, checks: list[dict], data: dict) -> None:
  required = [
    *PAGES,
    *KERNEL_PAGES,
    *[f"assets/{name}" for name in ASSETS],
    "data/sme-kernel-v3-institutional-publication.json",
    "downloads/sme-kernel-v3-publication/publication-provenance.json",
    "downloads/sme-kernel-v3-publication/repository-alignment.json",
    "downloads/sme-kernel-v3-publication/kernel-v3-institutional-publication.bib",
    "downloads/sme-kernel-v3-publication/institutional-use-case-qualification-worksheet.md",
    "sme-kernel-v3-publication-manifest.json",
    "qa/sme-kernel-v3-publication-build.json",
    *SHARED,
    *[name for name, _ in MANIFEST_CHAIN],
  ]
  missing = [relative for relative in required if not (site / relative).is_file()]
  record(checks, "site.required_outputs", not missing, "all publication, Kernel cross-link, metadata, download, and QA outputs present" if not missing else ", ".join(missing))
  if missing:
    return
  for page in PAGES:
    audit_page(site, page, checks, data)
  homepage = (site / "index.html").read_text(encoding="utf-8")
  homepage_ok = all(homepage.count(marker) == 1 for marker in HOMEPAGE_MARKERS) and homepage.count('data-goalos-feature="sme-kernel-v3-institutional-publication"') == 1 and homepage.count("Repository-aligned to") == 1
  record(checks, "site.homepage_integration", homepage_ok, "one additive style, navigation, and repository-aligned institutional gateway block")
  kernel_failures: list[str] = []
  for relative in KERNEL_PAGES:
    raw = (site / relative).read_text(encoding="utf-8")
    if raw.count("GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_LINK_START") != 1 or raw.count("data-goalos-kernel-publication-link") != 1:
      kernel_failures.append(relative)
  main_raw = (site / KERNEL_PAGES[0]).read_text(encoding="utf-8")
  if main_raw.count("GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_CTA_START") != 1 or main_raw.count("data-goalos-kernel-publication-cta") != 1:
    kernel_failures.append("main CTA")
  record(checks, "site.kernel_cross_links", not kernel_failures, "all five executable Kernel surfaces link to the institutional paper; flagship Kernel includes a dedicated CTA" if not kernel_failures else ", ".join(kernel_failures))

  routes = load(site / "routes.json")
  route_list = routes.get("routes", [])
  route_meta = routes.get("sme_kernel_v3_institutional_publication", {})
  route_ok = all(page in route_list for page in PAGES) and route_meta.get("release_id") == data.get("release_id") and route_meta.get("autonomy_phases") == 6 and route_meta.get("baseline_commit") == data["repository_alignment"]["baseline_commit"] and route_meta.get("claim_bounded") is True
  record(checks, "site.routes", route_ok, "three public routes and v3.2.0 repository-alignment metadata registered")
  sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
  record(checks, "site.sitemap", all((BASE_URL + page) in sitemap for page in PAGES), "all publication routes indexed")
  status = load(site / "site-status.json").get("sme_kernel_v3_institutional_publication", {})
  status_ok = status.get("version") == data.get("version") and status.get("integration_revision") == "r2" and status.get("use_cases") == 10 and status.get("case_studies") == 7 and status.get("autonomy_phases") == 6 and status.get("baseline_commit") == data["repository_alignment"]["baseline_commit"] and status.get("claim_bounded") is True and status.get("canonical_v86_source_modified") is False
  record(checks, "site.status", status_ok, "release, institutional counts, autonomous phases, baseline, and preservation status exposed")

  manifest = load(site / "sme-kernel-v3-publication-manifest.json")
  manifest_ok = manifest.get("schema") == MANIFEST_SCHEMA and manifest.get("release_id") == data.get("release_id") and manifest.get("integration_revision") == "r2" and manifest.get("integration", {}).get("mode") == "additive-post-kernel-v3" and manifest.get("integration", {}).get("canonical_v86_source_modified") is False and manifest.get("repository_alignment", {}).get("status") == "PASS"
  record(checks, "site.manifest_contract", manifest_ok, "v2 manifest declares additive post-Kernel integration and passed repository alignment")
  verify_manifest_hashes(site, manifest, checks)
  build = load(site / "qa/sme-kernel-v3-publication-build.json")
  build_ok = build.get("schema") == BUILD_SCHEMA and build.get("status") == "PASS" and not build.get("files_removed") and not build.get("unexpected_existing_file_changes") and set(build.get("kernel_pages_cross_linked", [])) == set(KERNEL_PAGES) and build.get("repository_alignment", {}).get("status") == "PASS" and build.get("canonical_v86_source_modified") is False
  record(checks, "site.build_preservation", build_ok, "no pre-existing file removed, no undeclared change, five Kernel surfaces cross-linked, and alignment passed")

  generated = load(site / "data/sme-kernel-v3-institutional-publication.json")
  content_ok = source_subset_matches(generated, data) and generated.get("observed_repository_alignment", {}).get("status") == "PASS" and len(generated.get("kernel_autonomy_chain", [])) == 6
  record(checks, "site.content_copy", content_ok, "public machine-readable source is intact and augmented only with observed alignment and current autonomy chain")
  alignment = load(site / "downloads/sme-kernel-v3-publication/repository-alignment.json")
  align_ok = alignment.get("status") == "PASS" and alignment.get("baseline_commit") == data["repository_alignment"]["baseline_commit"] and alignment.get("kernel_interface_release") == "Autonomous End-to-End Constellation v3.2.0" and alignment.get("canonical_v86_source_modified") is False and len(alignment.get("protected_files", {})) == 18
  record(checks, "site.repository_alignment", align_ok, "downloadable proof ledger binds the build to the audited commit, six-stage constellation, protected source set, and v86 boundary")
  provenance = load(site / "downloads/sme-kernel-v3-publication/publication-provenance.json")
  prov_ok = provenance.get("schema") == "goalos.sme_kernel_v3.publication_provenance.v2" and provenance.get("release_id") == data.get("release_id") and provenance.get("artifacts") == data.get("artifacts") and provenance.get("repository_alignment", {}).get("status") == "PASS"
  record(checks, "site.provenance", prov_ok, "canonical PDF provenance and repository-alignment proof are emitted together")

  chain_failures: list[str] = []
  for filename, schema in MANIFEST_CHAIN:
    payload = load(site / filename)
    if payload.get("schema") != schema or not isinstance(payload.get("files"), dict):
      chain_failures.append(f"contract {filename}")
      continue
    declared = list(SHARED) + (KERNEL_PAGES if filename == "sme-kernel-v3-manifest.json" else [])
    for relative in declared:
      if relative in payload["files"]:
        expected = payload["files"][relative]
        if not isinstance(expected, dict) or expected.get("sha256") != sha(site / relative) or expected.get("bytes") != (site / relative).stat().st_size:
          chain_failures.append(f"stale {filename}:{relative}")
    history = payload.get("integration", {}).get("reconciliations", [])
    if not isinstance(history, list) or not any(isinstance(entry, dict) and entry.get("release_id") == data.get("release_id") and entry.get("integration_revision") == "r2" for entry in history):
      chain_failures.append(f"reconciliation {filename}")
  record(checks, "site.constitutional_manifest_chain", not chain_failures, "all five predecessor manifests reconciled against final shared and Kernel navigation surfaces" if not chain_failures else "; ".join(chain_failures[:8]))

  if baseline:
    snapshot = load(baseline)
    before = snapshot.get("files", {})
    current = {path.relative_to(site).as_posix(): sha(path) for path in site.rglob("*") if path.is_file()}
    removed = sorted(set(before) - set(current))
    changed = sorted(relative for relative, value in before.items() if relative in current and current[relative] != (value.get("sha256") if isinstance(value, dict) else value))
    allowed = set(SHARED) | set(KERNEL_PAGES) | {name for name, _ in MANIFEST_CHAIN}
    unexpected = sorted(set(changed) - allowed)
    baseline_ok = snapshot.get("schema") == SNAPSHOT_SCHEMA and not removed and not unexpected
    record(checks, "site.baseline_preservation", baseline_ok, f"{len(before)} pre-build files preserved; {len(changed)} declared integration surfaces changed" if baseline_ok else f"removed={removed[:5]} unexpected={unexpected[:5]}")

  archives = [path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file() and path.suffix.lower() in ARCHIVE_SUFFIXES]
  record(checks, "site.no_archives", not archives, "no archive files in the public Pages artifact" if not archives else ", ".join(archives[:8]))
  expression = re.compile("|".join(PRIVATE_PATTERNS))
  hits: list[str] = []
  for path in site.rglob("*"):
    if path.is_file() and path.suffix.lower() in {".html", ".json", ".js", ".css", ".md", ".txt", ".xml", ".bib"} and expression.search(path.read_text(encoding="utf-8", errors="ignore")):
      hits.append(path.relative_to(site).as_posix())
  record(checks, "site.no_private_material", not hits, "no private operator material or secret placeholders" if not hits else ", ".join(hits[:8]))


def main() -> int:
  default_root = Path(__file__).resolve().parents[2]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--root", type=Path, default=default_root)
  parser.add_argument("--site", type=Path, default=default_root / "site")
  parser.add_argument("--baseline", type=Path)
  parser.add_argument("--output", type=Path)
  parser.add_argument("--source-only", action="store_true")
  args = parser.parse_args()
  root = args.root.resolve()
  site = args.site.resolve()
  checks: list[dict] = []
  data = assert_source(root, checks)
  if not args.source_only and data:
    if site.is_dir():
      assert_site(root, site, args.baseline.resolve() if args.baseline else None, checks, data)
    else:
      record(checks, "site.exists", False, f"missing generated site: {site}")
  failures = [item for item in checks if item["status"] != "PASS"]
  report = {
    "schema": REPORT_SCHEMA,
    "status": "PASS" if not failures else "FAIL",
    "mode": "source-only" if args.source_only else "full-site",
    "checks_passed": len(checks) - len(failures),
    "checks_total": len(checks),
    "checks": checks,
    "failures": [item["check"] for item in failures],
  }
  if args.output:
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  print(json.dumps(report, ensure_ascii=False, indent=2))
  return 0 if not failures else 1


if __name__ == "__main__":
  raise SystemExit(main())
