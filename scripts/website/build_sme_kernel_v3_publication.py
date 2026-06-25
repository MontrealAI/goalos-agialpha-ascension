#!/usr/bin/env python3
"""Build the repository-aligned GoalOS Kernel v3 institutional publication suite additively."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

FEATURE_ID = "sme-kernel-v3-institutional-publication"
RELEASE_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.v2"
MANIFEST_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.website_manifest.v2"
BUILD_SCHEMA = "goalos.sme_kernel_v3.institutional_publication.build_report.v2"
BASE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
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
STYLE_START = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_STYLE_START -->"
STYLE_END = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_STYLE_END -->"
NAV_START = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_NAV_START -->"
NAV_END = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_NAV_END -->"
HOME_START = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_HOME_START -->"
HOME_END = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_HOME_END -->"
KERNEL_LINK_START = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_LINK_START -->"
KERNEL_LINK_END = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_LINK_END -->"
KERNEL_CTA_START = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_CTA_START -->"
KERNEL_CTA_END = "<!-- GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_CTA_END -->"
KERNEL_NAV_END = "<!-- GOALOS_SME_KERNEL_V3_NAV_END -->"
KERNEL_HOME_END = "<!-- GOALOS_SME_KERNEL_V3_HOME_END -->"


def now() -> datetime:
  epoch = os.environ.get("SOURCE_DATE_EPOCH")
  return datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc)


def iso(value: datetime) -> str:
  return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def esc(value: Any) -> str:
  return html.escape("" if value is None else str(value), quote=True)


def load(path: Path) -> dict[str, Any]:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise ValueError(f"Expected JSON object: {path}")
  return value


def dump(path: Path, value: Any) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha_file(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
      digest.update(chunk)
  return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
  return {"sha256": sha_file(path), "bytes": path.stat().st_size}


def source_set_digest(root: Path, relatives: list[str]) -> tuple[str, dict[str, dict[str, Any]]]:
  records: dict[str, dict[str, Any]] = {}
  for relative in sorted(relatives):
    target = root / relative
    if not target.is_file():
      raise RuntimeError(f"Protected source missing: {relative}")
    records[relative] = file_record(target)
  material = "".join(f"{relative}\0{records[relative]['sha256']}\0{records[relative]['bytes']}\n" for relative in sorted(records))
  return hashlib.sha256(material.encode("utf-8")).hexdigest(), records


def v86_tree_digest(root: Path) -> str:
  directory = root / "website/v86_actual_site"
  if not directory.is_dir():
    raise RuntimeError(f"Canonical v86 source missing: {directory}")
  lines: list[str] = []
  for target in sorted((item for item in directory.rglob("*") if item.is_file()), key=lambda item: item.relative_to(root).as_posix()):
    relative = target.relative_to(root).as_posix()
    lines.append(f"{sha_file(target)}  {relative}\n")
  return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def git_sha(root: Path) -> str:
  env_sha = os.environ.get("GITHUB_SHA", "").strip()
  if re.fullmatch(r"[0-9a-f]{40}", env_sha):
    return env_sha
  try:
    value = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else "unavailable"
  except (OSError, subprocess.CalledProcessError):
    return "unavailable"


def validate_content(data: dict[str, Any]) -> None:
  errors: list[str] = []
  expected = {
    "schema": RELEASE_SCHEMA,
    "version": "3.0.0",
    "integration_revision": "r2",
    "status": "claim-bounded-repository-aligned-institutional-publication-suite",
    "doctrine": "A model can answer. An agent can act. An institution must prove.",
  }
  for key, value in expected.items():
    if data.get(key) != value:
      errors.append(f"{key} mismatch")
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
  for key, count in counts.items():
    if not isinstance(data.get(key), list) or len(data[key]) != count:
      errors.append(f"{key} must contain {count} entries")
  if [item.get("id") for item in data.get("use_cases", [])] != [f"UC-{index:02d}" for index in range(1, 11)]:
    errors.append("use-case order or identifiers mismatch")
  if [item.get("id") for item in data.get("case_studies", [])] != list("ABCDEFG"):
    errors.append("case-study order or identifiers mismatch")
  expected_lineage = [
    "https://github.com/MontrealAI/AGI-Alpha-Agent-v0",
    "https://github.com/MontrealAI/AGI-Alpha-Node-v0",
    "https://github.com/MontrealAI/AGIJobsv0",
    "https://github.com/MontrealAI/goalos-agialpha-ascension",
  ]
  if [item.get("url") for item in data.get("lineage", [])] != expected_lineage:
    errors.append("evolutionary lineage repositories mismatch")
  alignment = data.get("repository_alignment")
  if not isinstance(alignment, dict):
    errors.append("repository alignment missing")
  else:
    if not re.fullmatch(r"[0-9a-f]{40}", str(alignment.get("baseline_commit", ""))):
      errors.append("baseline commit invalid")
    for key in ["active_workflow_sha256", "kernel_content_sha256", "protected_source_set_sha256", "canonical_v86_tree_sha256"]:
      if not re.fullmatch(r"[0-9a-f]{64}", str(alignment.get(key, ""))):
        errors.append(f"repository alignment digest invalid: {key}")
    if alignment.get("autonomy_chain_ids") != ["identify", "learn", "think", "design", "strategise", "execute"]:
      errors.append("repository alignment phase identifiers mismatch")
    if alignment.get("autonomy_chain_labels") != ["IDENTIFY", "OUT-LEARN", "OUT-THINK", "OUT-DESIGN", "OUT-STRATEGISE", "OUT-EXECUTE"]:
      errors.append("repository alignment phase labels mismatch")
    if alignment.get("canonical_v86_source_modified") is not False:
      errors.append("canonical v86 source boundary must remain false")
  boundary = data.get("claim_boundary", {})
  if not isinstance(boundary.get("not_claimed"), list) or len(boundary["not_claimed"]) < 8:
    errors.append("claim boundary is incomplete")
  for artifact in data.get("artifacts", []):
    url = str(artifact.get("url", ""))
    if not url.startswith("https://montrealai.github.io/"):
      errors.append(f"artifact URL is outside the canonical publication host: {artifact.get('id')}")
    if artifact.get("id") != "source-suite" and not re.fullmatch(r"[0-9a-f]{64}", str(artifact.get("sha256", ""))):
      errors.append(f"artifact digest invalid: {artifact.get('id')}")
  for key, asset in data.get("assets", {}).items():
    if not re.fullmatch(r"[0-9a-f]{64}", str(asset.get("sha256", ""))):
      errors.append(f"asset digest invalid: {key}")
  if errors:
    raise RuntimeError("; ".join(errors))


def validate_repository_alignment(data: dict[str, Any], root: Path, kernel_path: Path, workflow_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
  alignment = data["repository_alignment"]
  if not kernel_path.is_file():
    raise RuntimeError(f"Kernel content missing: {kernel_path}")
  if not workflow_path.is_file():
    raise RuntimeError(f"Active workflow missing: {workflow_path}")
  actual_kernel_sha = sha_file(kernel_path)
  actual_workflow_sha = sha_file(workflow_path)
  if actual_kernel_sha != alignment["kernel_content_sha256"]:
    raise RuntimeError(f"Kernel content drifted: expected {alignment['kernel_content_sha256']}, observed {actual_kernel_sha}")
  if actual_workflow_sha != alignment["active_workflow_sha256"] and "GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_START" not in workflow_path.read_text(encoding="utf-8"):
    raise RuntimeError(f"Active workflow drifted before publication integration: expected {alignment['active_workflow_sha256']}, observed {actual_workflow_sha}")
  kernel = load(kernel_path)
  phases = kernel.get("autonomy_chain", [])
  if [item.get("id") for item in phases] != alignment["autonomy_chain_ids"]:
    raise RuntimeError("Kernel autonomy-chain identifiers do not match the audited constellation")
  if [item.get("label") for item in phases] != alignment["autonomy_chain_labels"]:
    raise RuntimeError("Kernel autonomy-chain labels do not match the audited constellation")
  expected_counts = {"autonomy_chain": 6, "roles": 5, "states": 17, "envelope_types": 10}
  for key, count in expected_counts.items():
    if not isinstance(kernel.get(key), list) or len(kernel[key]) != count:
      raise RuntimeError(f"Kernel {key} must contain {count} entries")
  protected_sha, protected_records = source_set_digest(root, PROTECTED_SOURCE_PATHS)
  if protected_sha != alignment["protected_source_set_sha256"]:
    raise RuntimeError(f"Protected Kernel source set drifted: expected {alignment['protected_source_set_sha256']}, observed {protected_sha}")
  actual_v86 = v86_tree_digest(root)
  if actual_v86 != alignment["canonical_v86_tree_sha256"]:
    raise RuntimeError(f"Canonical v86 source tree drifted: expected {alignment['canonical_v86_tree_sha256']}, observed {actual_v86}")
  observation = {
    "schema": "goalos.sme_kernel_v3.institutional_publication.repository_alignment.v1",
    "status": "PASS",
    "baseline_commit": alignment["baseline_commit"],
    "build_commit": git_sha(root),
    "kernel_interface_release": alignment["kernel_interface_release"],
    "integration_revision": data["integration_revision"],
    "active_workflow": alignment["active_workflow"],
    "active_workflow_sha256_before_integration": alignment["active_workflow_sha256"],
    "active_workflow_sha256_observed": actual_workflow_sha,
    "kernel_content_sha256": actual_kernel_sha,
    "protected_source_set_sha256": protected_sha,
    "canonical_v86_tree_sha256": actual_v86,
    "canonical_v86_source_modified": False,
    "autonomy_chain": phases,
    "kernel_contract": {
      "version": kernel.get("version"),
      "status": kernel.get("status"),
      "states": len(kernel["states"]),
      "typed_envelopes": len(kernel["envelope_types"]),
      "signing_authorities": len(kernel["roles"]),
      "external_actions": next((item.get("value") for item in kernel.get("hero_metrics", []) if item.get("label") == "external actions"), None),
    },
    "protected_files": protected_records,
  }
  return kernel, observation


def replace_block(raw: str, start: str, end: str, replacement: str) -> str:
  if start in raw or end in raw:
    if raw.count(start) != 1 or raw.count(end) != 1:
      raise RuntimeError(f"Invalid marker count for {start}")
    return re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, raw, count=1, flags=re.S)
  return raw


def page_shell(template: str, data: dict[str, Any], page: str, title: str, description: str, main: str) -> str:
  canonical = BASE_URL + page
  paper_url = next(item["url"] for item in data["artifacts"] if item["id"] == "flagship")
  alignment = data["repository_alignment"]
  json_ld = {
    "@context": "https://schema.org",
    "@type": "ScholarlyArticle",
    "headline": data["title"],
    "alternativeHeadline": data["edition"],
    "description": data["description"],
    "author": {"@type": "Person", "name": data["author"]["name"]},
    "publisher": {"@type": "Organization", "name": "MONTREAL.AI"},
    "datePublished": "2026-06",
    "version": data["version"],
    "url": canonical,
    "sameAs": data["canonical_suite_url"],
    "encoding": [{"@type": "MediaObject", "contentUrl": paper_url, "encodingFormat": "application/pdf"}],
    "isPartOf": {"@type": "SoftwareApplication", "name": "GoalOS AGIALPHA Ascension Sovereign Machine Economy Kernel v3", "url": data["executable_kernel_url"]},
    "isBasedOn": [item["url"] for item in data["lineage"]],
    "inLanguage": "en",
    "keywords": ["GoalOS", "proof-bearing autonomous work", "institutional AI", "constitutional execution", "Sovereign Machine Economy", alignment["kernel_interface_release"]],
  }
  replacements = {
    "@@TITLE@@": esc(title),
    "@@DESCRIPTION@@": esc(description),
    "@@CANONICAL@@": esc(canonical),
    "@@OG_IMAGE@@": esc(BASE_URL + "assets/cover-institutional-use-case-edition-v3.png"),
    "@@PAPER_URL@@": esc(paper_url),
    "@@JSON_LD@@": json.dumps(json_ld, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c"),
    "@@MAIN@@": main,
    "@@SUITE_URL@@": esc(data["canonical_suite_url"]),
    "@@REPO_URL@@": esc(data["repository_url"]),
    "@@INTEGRATION_REVISION@@": esc(data["integration_revision"]),
    "@@ALIGNMENT_LABEL@@": esc(alignment["kernel_interface_release"]),
    "@@ALIGNMENT_COMMIT@@": esc(alignment["baseline_commit_short"]),
  }
  output = template
  for token, value in replacements.items():
    output = output.replace(token, value)
  key = {PAGES[0]: "paper", PAGES[1]: "use-cases", PAGES[2]: "proof"}[page]
  output = output.replace(f'data-page="{key}"', f'data-page="{key}" aria-current="page"')
  if "@@" in output:
    raise RuntimeError(f"Unresolved template token in {page}")
  return output


def buttons(data: dict[str, Any], include_companion: bool = True) -> str:
  flagship = next(item for item in data["artifacts"] if item["id"] == "flagship")
  companion = next(item for item in data["artifacts"] if item["id"] == "companion")
  links = [f'<a class="pub-button primary" href="{esc(flagship["url"])}" target="_blank" rel="noopener">Open 48-page publication ↗</a>']
  if include_companion:
    links.append(f'<a class="pub-button secondary" href="{esc(companion["url"])}" target="_blank" rel="noopener">Open boardroom companion ↗</a>')
  links.append('<a class="pub-button secondary" href="sovereign-machine-economy-kernel-v3.html">Launch executable Kernel</a>')
  return "".join(links)


def render_constellation(kernel: dict[str, Any]) -> str:
  phases = "".join(
    f'<article class="pub-phase" data-alignment-phase="{esc(item["id"])}"><span>{esc(item["index"])}</span><div><strong>{esc(item["label"])} <i aria-hidden="true">{esc(item["icon"])}</i></strong><p>{esc(item["artifact"])}</p></div></article>'
    for item in kernel["autonomy_chain"]
  )
  return f'<div class="pub-constellation" aria-label="Source-generated six-stage autonomous capability chain">{phases}</div>'


def render_alignment_strip(data: dict[str, Any], observation: dict[str, Any]) -> str:
  alignment = data["repository_alignment"]
  return f'''<aside class="pub-alignment-strip" aria-label="Repository alignment"><span class="pub-alignment-status">ALIGNED</span><div><strong>{esc(alignment["kernel_interface_release"])}</strong><small>Audited repository baseline <code>{esc(alignment["baseline_commit_short"])}</code> · protected source set <code>{esc(observation["protected_source_set_sha256"][:12])}</code></small></div><a href="sovereign-machine-economy-kernel-v3-publication-proof.html#repository-alignment">Inspect alignment proof</a></aside>'''


def render_paper(data: dict[str, Any], kernel: dict[str, Any], observation: dict[str, Any]) -> str:
  metrics = "".join(f'<div class="pub-metric"><strong>{esc(item["value"])}</strong><span>{esc(item["label"])}</span></div>' for item in data["metrics"])
  kernel_metrics = "".join(f'<article><strong>{esc(item["value"])}</strong><span>{esc(item["label"])}</span></article>' for item in data["kernel_metrics"])
  lineage = "".join(f'<a class="pub-lineage" href="{esc(item["url"])}" target="_blank" rel="noopener"><span>{esc(item["index"])}</span><div><small>{esc(item["repository"])}</small><h3>{esc(item["label"])}</h3><p>{esc(item["role"])}</p></div><b aria-hidden="true">↗</b></a>' for item in data["lineage"])
  architecture = "".join(f'<article class="pub-card" data-accent="{esc(item["accent"])}"><small>{esc(item["index"])}</small><h3>{esc(item["label"])}</h3><p>{esc(item["role"])}</p></article>' for item in data["architecture"])
  artifacts = "".join(f'<a class="pub-artifact" href="{esc(item["url"])}" target="_blank" rel="noopener"><span class="pub-artifact-icon">{esc(item["format"].split(" ")[0])}</span><span><h3>{esc(item["label"])}</h3><p>{esc(item["description"])}</p><span class="pub-artifact-meta"><span>{esc(str(item["pages"]) + " pages" if item["pages"] else item["format"])}</span><span>Canonical source ↗</span></span></span></a>' for item in data["artifacts"])
  materials = "".join(f'<a class="pub-material" href="{esc(item["url"])}" target="_blank" rel="noopener"><span>{esc(item["format"])}</span><div><h3>{esc(item["label"])}</h3><p>{esc(item["description"])}</p></div><b aria-hidden="true">↗</b></a>' for item in data["materials"])
  readers = "".join(f'<article class="pub-reader"><h3>{esc(item["audience"])}</h3><p>{esc(item["question"])}</p><span>Read {esc(item["sections"])}</span></article>' for item in data["reader_paths"])
  not_claimed = "".join(f"<li>{esc(item)}</li>" for item in data["claim_boundary"]["not_claimed"])
  return f'''
<section class="pub-hero">
  <div class="pub-shell pub-hero-grid">
    <div>
      <p class="pub-kicker">Institutional Paper v3.0 · Repository Integration r2</p>
      <h1>Sovereign Machine Economy <em>Kernel v3</em></h1>
      <p class="pub-doctrine">{esc(data["doctrine"])}</p>
      <div class="pub-actions">{buttons(data)}</div>
    </div>
    <figure class="pub-cover-wrap"><img class="pub-cover" src="assets/cover-institutional-use-case-edition-v3.png" width="1654" height="2339" alt="Cover of the GoalOS Sovereign Machine Economy Kernel v3 Institutional Use-Case Edition"></figure>
  </div>
</section>
<div class="pub-shell">{render_alignment_strip(data, observation)}<div class="pub-metrics" aria-label="Publication metrics">{metrics}</div></div>
<section class="pub-section">
  <div class="pub-shell">
    <div class="pub-section-head"><div><p class="pub-eyebrow">The category</p><h2>Verifiable autonomous work infrastructure.</h2></div><p class="pub-lead">Not another agent framework: a proof-to-permission control plane that separates machine capability from institutional authority.</p></div>
    <blockquote class="pub-quote">{esc(data["doctrine"])}</blockquote>
  </div>
</section>
<section class="pub-section dark" id="autonomous-constellation">
  <div class="pub-shell">
    <div class="pub-section-head"><div><p class="pub-eyebrow">Current executable alignment</p><h2>Autonomous. End-to-end. Constitutionally bounded.</h2></div><p class="pub-lead">This six-stage constellation is generated from the current <code>content/sme-kernel-v3.json</code> source contract—not copied into the page by hand.</p></div>
    {render_constellation(kernel)}
    <div class="pub-kernel-metrics" aria-label="Executable Kernel contract">{kernel_metrics}</div>
  </div>
</section>
<section class="pub-section compact">
  <div class="pub-shell">
    <div class="pub-section-head"><div><p class="pub-eyebrow">Evolutionary lineage</p><h2>From the original α-AGI constellation to GoalOS.</h2></div><p class="pub-lead">The institutional kernel is a GoalOS-native reimplementation and constitutional synthesis of the original META-AGENTIC α-AGI, AGI Alpha Node, and AGI Jobs systems. The originating repositories remain directly inspectable.</p></div>
    <div class="pub-lineage-grid">{lineage}</div>
  </div>
</section>
<section class="pub-section dark">
  <div class="pub-shell">
    <div class="pub-section-head"><div><p class="pub-eyebrow">Constitutional architecture</p><h2>Replace the intelligence. Never the constitution.</h2></div><p class="pub-lead">Three specialized engines operate beneath a typed, signed, append-only, human-gated constitutional kernel.</p></div>
    <div class="pub-cards">{architecture}</div>
    <div class="pub-pipeline" aria-label="Proof-to-permission pipeline">
      <article><span>01 · Objective</span><strong>Mission committed</strong></article><article><span>02 · Execution</span><strong>Work bounded</strong></article><article><span>03 · Evidence</span><strong>Docket sealed</strong></article><article><span>04 · Challenge</span><strong>Validation exposed</strong></article><article><span>05 · Authority</span><strong>Human scope recorded</strong></article>
    </div>
  </div>
</section>
<section class="pub-section"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Publication library</p><h2>One definitive suite. Every serious reading path.</h2></div><p class="pub-lead">Open the flagship publication, boardroom companion, native typesetting edition, or complete editable source suite.</p></div><div class="pub-library">{artifacts}</div></div></section>
<section class="pub-section compact"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Editable source &amp; institutional instruments</p><h2>Review it. Reproduce it. Operationalize it.</h2></div><p class="pub-lead">Direct access to the Word and Markdown manuscripts, LaTeX project, dossier template, qualification checklist, and validation evidence.</p></div><div class="pub-material-grid">{materials}</div></div></section>
<section class="pub-section compact"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Reader map</p><h2>Enter at the level of consequence.</h2></div><p class="pub-lead">The publication is deliberately navigable by executive, operator, engineer, evaluator, governance, and board audiences.</p></div><div class="pub-reader-grid">{readers}</div></div></section>
<section class="pub-section"><div class="pub-shell"><div class="pub-boundary"><div><p class="pub-eyebrow">Publication-safe boundary</p><h3>Grand ambition. Exact claims.</h3><p>{esc(data["claim_boundary"]["positive"])}</p></div><ul>{not_claimed}</ul></div></div></section>
'''


def render_use_cases(data: dict[str, Any], kernel: dict[str, Any], observation: dict[str, Any]) -> str:
  categories = ["All", *sorted({item["category"] for item in data["use_cases"]})]
  filters = "".join(f'<button class="pub-filter" type="button" data-pub-filter="{esc(category)}" aria-pressed="{"true" if category == "All" else "false"}">{esc(category)}</button>' for category in categories)
  cases = "".join(f'<article class="pub-use" data-use-category="{esc(item["category"])}"><div class="pub-use-top"><span class="pub-use-code">{esc(item["id"])}</span><span class="pub-tag">{esc(item["category"])}</span></div><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p><dl><div><dt>Evidence burden</dt><dd>{esc(item["evidence"])}</dd></div><div><dt>Authority boundary</dt><dd>{esc(item["authority"])}</dd></div><div class="fail"><dt>Fail closed when</dt><dd>{esc(item["fail_closed"])}</dd></div></dl></article>' for item in data["use_cases"])
  studies = "".join(f'<article class="pub-case"><b>{esc(item["id"])}</b><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p></article>' for item in data["case_studies"])
  companion = next(item for item in data["artifacts"] if item["id"] == "companion")
  return f'''
<section class="pub-page-hero"><div class="pub-shell"><p class="pub-eyebrow">Institutional deployment atlas</p><h1>Ten operating patterns. Seven proof-to-permission scenarios.</h1><p>Each pattern makes its evidence burden, authority boundary, and fail-closed condition explicit. The scenarios are reference implementations—not customer outcome claims.</p><div class="pub-actions"><a class="pub-button primary" href="{esc(companion["url"])}" target="_blank" rel="noopener">Open 13-page companion ↗</a><a class="pub-button secondary on-light" href="sovereign-machine-economy-kernel-v3-paper.html">Return to flagship paper</a></div>{render_alignment_strip(data, observation)}</div></section>
<section class="pub-section"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Qualification frontier</p><h2>More consequence requires more constitution.</h2></div><p class="pub-lead">Use GoalOS where evidence, reversibility, independent challenge, and explicit human authority matter—not where a simple low-consequence automation is sufficient.</p></div><img class="pub-gallery" src="assets/kernel-v3-use-case-gallery.jpg" width="1520" height="1940" alt="Gallery of the GoalOS institutional use-case qualification frontier and reference case-study figures"></div></section>
<section class="pub-section compact"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Quintessential use cases</p><h2>Evidence before reliance.</h2></div><p class="pub-lead">Filter the institutional patterns by operating domain.</p></div><div class="pub-filterbar" aria-label="Filter use cases">{filters}</div><div class="pub-use-grid">{cases}</div></div></section>
<section class="pub-section dark"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Worked reference case studies</p><h2>Seven complete scenarios.</h2></div><p class="pub-lead">Each scenario follows objective → mission contract → bounded execution → Evidence Docket → challenge → Human Review Certificate → revocable memory.</p></div><div class="pub-case-grid">{studies}</div></div></section>
'''


def render_proof(data: dict[str, Any], kernel: dict[str, Any], observation: dict[str, Any]) -> str:
  validation = "".join(f'<article class="pub-proof"><strong>{esc(item["value"])}</strong><span>{esc(item["label"])}</span></article>' for item in data["validation"])
  rows: list[str] = []
  for item in data["artifacts"]:
    digest = item["sha256"] or "See canonical source suite"
    size = f'{item["bytes"]:,} bytes' if item["bytes"] else "Multiple source artifacts"
    pages = str(item["pages"]) if item["pages"] else "—"
    rows.append(f'<tr><td><strong>{esc(item["label"])}</strong><br>{esc(item["format"])}</td><td>{esc(pages)}</td><td>{esc(size)}</td><td><code>{esc(digest)}</code></td><td><a href="{esc(item["url"])}" target="_blank" rel="noopener">Open ↗</a></td></tr>')
  alignment = data["repository_alignment"]
  alignment_rows = [
    ("Repository baseline", alignment["baseline_commit"], alignment["baseline_commit_title"]),
    ("Active v86 workflow", observation["active_workflow_sha256_before_integration"], alignment["active_workflow"]),
    ("Kernel content contract", observation["kernel_content_sha256"], "content/sme-kernel-v3.json"),
    ("Protected Kernel source set", observation["protected_source_set_sha256"], f"{len(observation['protected_files'])} audited files"),
    ("Canonical v86 source tree", observation["canonical_v86_tree_sha256"], "website/v86_actual_site/** remains unchanged"),
  ]
  alignment_table = "".join(f'<tr><td><strong>{esc(label)}</strong><br><span>{esc(detail)}</span></td><td><code>{esc(value)}</code></td></tr>' for label, value, detail in alignment_rows)
  citation = f'Boucher, Vincent. “{data["title"]}.” GoalOS AGIALPHA Ascension: Sovereign Machine Economy Kernel v3, {data["edition"]}, MONTREAL.AI and QUEBEC.AI, June 2026. {data["canonical_suite_url"]}'
  boundary = "".join(f"<li>{esc(item)}</li>" for item in data["claim_boundary"]["not_claimed"])
  return f'''
<section class="pub-page-hero"><div class="pub-shell"><p class="pub-eyebrow">Publication proof</p><h1>Rendered, audited, provenance-bound, and claim-bounded.</h1><p>The publication suite exposes its validation record, canonical artifacts, repository alignment, checksums, publication law, and explicit non-claims in one reviewable surface.</p><div class="pub-actions"><a class="pub-button primary" href="{esc(data["canonical_suite_url"])}" target="_blank" rel="noopener">Open complete source suite ↗</a><a class="pub-button secondary on-light" href="downloads/sme-kernel-v3-publication/publication-provenance.json">Download provenance JSON</a><a class="pub-button secondary on-light" href="downloads/sme-kernel-v3-publication/repository-alignment.json">Download alignment JSON</a></div></div></section>
<section class="pub-section"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Validation record</p><h2>Publication quality is part of the proof.</h2></div><p class="pub-lead">The figures below reproduce the canonical suite’s reported publication QA—not an independent certification.</p></div><div class="pub-proof-grid">{validation}</div></div></section>
<section class="pub-section compact"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Canonical provenance</p><h2>Stable URLs. Recorded digests.</h2></div><p class="pub-lead">The site links to the authoritative publication host and records the observed SHA-256 digests and byte sizes for the three principal PDFs.</p></div><table class="pub-provenance"><thead><tr><th>Artifact</th><th>Pages</th><th>Size</th><th>SHA-256</th><th>Source</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>
<section class="pub-section" id="repository-alignment"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Repository alignment ledger</p><h2>Bound to the current executable constellation.</h2></div><p class="pub-lead">The installer fails closed if any protected Kernel v3 source, the active v86 workflow, or the canonical v86 source tree differs from the audited repository snapshot.</p></div><table class="pub-provenance pub-alignment-table"><thead><tr><th>Protected surface</th><th>Recorded value</th></tr></thead><tbody>{alignment_table}</tbody></table><div class="pub-alignment-note"><strong>{esc(alignment["kernel_interface_release"])}</strong><span>{esc(" → ".join(item["label"].title() for item in kernel["autonomy_chain"]))}</span></div></div></section>
<section class="pub-section dark"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Autonomous publication law</p><h2>Generate autonomously. Publish constitutionally.</h2></div><p class="pub-lead">The website integration itself follows the paper’s proof discipline and cannot deploy unless every gate passes.</p></div><div class="pub-law"><article><b>1</b><strong>Versioned source</strong></article><article><b>2</b><strong>Deterministic build</strong></article><article><b>3</b><strong>Static verification</strong></article><article><b>4</b><strong>Browser QA</strong></article><article><b>5</b><strong>Human-review PR</strong></article><article><b>6</b><strong>Pages deployment</strong></article></div></div></section>
<section class="pub-section"><div class="pub-shell"><div class="pub-boundary"><div><p class="pub-eyebrow">Claim boundary</p><h3>What this edition establishes—and what it does not.</h3><p>{esc(data["claim_boundary"]["positive"])}</p></div><ul>{boundary}</ul></div></div></section>
<section class="pub-section compact"><div class="pub-shell"><div class="pub-section-head"><div><p class="pub-eyebrow">Citation</p><h2>Cite the institutional edition.</h2></div><p class="pub-lead">A machine-readable BibTeX file is also included in the publication downloads.</p></div><div class="pub-citation"><pre id="publication-citation" tabindex="0">{esc(citation)}</pre><button class="pub-copy" type="button" data-copy-citation="#publication-citation">Copy citation</button></div></div></section>
'''


def homepage_blocks(data: dict[str, Any]) -> tuple[str, str, str]:
  style = f'{STYLE_START}<link rel="stylesheet" href="assets/sme-kernel-v3-publication.css" data-goalos-sme-kernel-v3-publication>{STYLE_END}'
  nav = f'{NAV_START}<a href="{PAGES[0]}">Institutional Paper</a>{NAV_END}'
  alignment = data["repository_alignment"]
  home = f'''{HOME_START}<section class="kv3pub-home" id="kernel-v3-institutional-publication" data-goalos-feature="{FEATURE_ID}"><div class="kv3pub-home-inner"><div><small>INSTITUTIONAL PAPER v3.0 × AUTONOMOUS END-TO-END v3.2.0</small><h2>THE INSTITUTIONAL <span>EDITION</span></h2><p><strong>{esc(data["doctrine"])}</strong> The definitive publication suite connects the current six-stage executable constellation to ten institutional operating patterns, seven worked reference case studies, boardroom materials, editable sources, and explicit publication proof.</p><div class="kv3pub-home-stats"><div class="kv3pub-home-stat"><strong>48</strong><span>primary pages</span></div><div class="kv3pub-home-stat"><strong>10</strong><span>use cases</span></div><div class="kv3pub-home-stat"><strong>7</strong><span>case studies</span></div><div class="kv3pub-home-stat"><strong>6</strong><span>autonomous phases</span></div></div><div class="kv3pub-home-actions"><a href="{PAGES[0]}">Enter the Institutional Edition</a><a href="{PAGES[1]}">Explore Use Cases</a><a href="{PAGES[2]}">Inspect Publication Proof</a></div><p class="kv3pub-home-alignment">Repository-aligned to <strong>{esc(alignment["baseline_commit_short"])}</strong> · canonical v86 source preserved.</p></div><div class="kv3pub-home-visual" aria-label="Proof-to-permission institutional publication"><div class="kv3pub-home-orbit"></div><div class="kv3pub-home-core">PROOF<br>→<br>PERMISSION</div><span class="kv3pub-home-node a">MISSION</span><span class="kv3pub-home-node b">AUTHORITY</span><span class="kv3pub-home-node c">MEMORY</span><span class="kv3pub-home-node d">EVIDENCE</span></div></div></section>{HOME_END}'''
  return style, nav, home


def patch_homepage(path: Path, data: dict[str, Any]) -> None:
  raw = path.read_text(encoding="utf-8")
  style, nav, home = homepage_blocks(data)
  if STYLE_START in raw:
    raw = replace_block(raw, STYLE_START, STYLE_END, style)
  elif "</head>" in raw:
    raw = raw.replace("</head>", style + "\n</head>", 1)
  else:
    raise RuntimeError("Homepage missing </head>")
  if NAV_START in raw:
    raw = replace_block(raw, NAV_START, NAV_END, nav)
  elif KERNEL_NAV_END in raw:
    raw = raw.replace(KERNEL_NAV_END, KERNEL_NAV_END + "\n" + nav, 1)
  elif "</nav>" in raw:
    raw = raw.replace("</nav>", nav + "\n</nav>", 1)
  else:
    raise RuntimeError("Homepage missing navigation insertion point")
  if HOME_START in raw:
    raw = replace_block(raw, HOME_START, HOME_END, home)
  elif KERNEL_HOME_END in raw:
    raw = raw.replace(KERNEL_HOME_END, KERNEL_HOME_END + "\n" + home, 1)
  elif "</main>" in raw:
    raw = raw.replace("</main>", home + "\n</main>", 1)
  elif "</body>" in raw:
    raw = raw.replace("</body>", home + "\n</body>", 1)
  else:
    raise RuntimeError("Homepage missing content insertion point")
  path.write_text(raw, encoding="utf-8")


def patch_kernel_surfaces(site: Path) -> list[str]:
  changed: list[str] = []
  link = f'{KERNEL_LINK_START}<a href="{PAGES[0]}" data-goalos-kernel-publication-link>Institutional Paper</a>{KERNEL_LINK_END}'
  anchor = '<a class="kv3-home-link" href="sovereign-machine-economy.html">Machine Economy Ω</a>'
  for relative in KERNEL_PAGES:
    path = site / relative
    raw = path.read_text(encoding="utf-8")
    before = raw
    if KERNEL_LINK_START in raw:
      raw = replace_block(raw, KERNEL_LINK_START, KERNEL_LINK_END, link)
    elif anchor in raw:
      raw = raw.replace(anchor, link + anchor, 1)
    else:
      raise RuntimeError(f"Kernel navigation insertion point missing: {relative}")
    if relative == KERNEL_PAGES[0]:
      cta = f'{KERNEL_CTA_START}<a class="kv3-btn" href="{PAGES[0]}" data-goalos-kernel-publication-cta>Read the institutional paper</a>{KERNEL_CTA_END}'
      cta_anchor = '<a class="kv3-btn" href="sovereign-machine-economy-kernel-v3-verifier.html">Verify a mission bundle</a>'
      if KERNEL_CTA_START in raw:
        raw = replace_block(raw, KERNEL_CTA_START, KERNEL_CTA_END, cta)
      elif cta_anchor in raw:
        raw = raw.replace(cta_anchor, cta_anchor + cta, 1)
      else:
        raise RuntimeError("Kernel hero CTA insertion point missing")
    if raw != before:
      path.write_text(raw, encoding="utf-8")
    changed.append(relative)
  return changed


def update_routes(path: Path, data: dict[str, Any]) -> None:
  payload = load(path) if path.exists() else {"version": "unknown", "routes": []}
  routes = payload.get("routes", [])
  if not isinstance(routes, list):
    raise RuntimeError("routes.json routes must be an array")
  payload["routes"] = sorted(set(map(str, routes)).union(PAGES))
  payload["sme_kernel_v3_institutional_publication"] = {
    "release_id": data["release_id"],
    "version": data["version"],
    "integration_revision": data["integration_revision"],
    "pages": PAGES,
    "use_cases": 10,
    "case_studies": 7,
    "autonomy_phases": 6,
    "kernel_interface_release": data["repository_alignment"]["kernel_interface_release"],
    "baseline_commit": data["repository_alignment"]["baseline_commit"],
    "canonical_suite_url": data["canonical_suite_url"],
    "claim_bounded": True,
  }
  dump(path, payload)


def update_sitemap(path: Path) -> None:
  raw = path.read_text(encoding="utf-8") if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>"
  for page in PAGES:
    url = BASE_URL + page
    if url not in raw:
      if "</urlset>" not in raw:
        raise RuntimeError("sitemap missing </urlset>")
      raw = raw.replace("</urlset>", f"<url><loc>{url}</loc><lastmod>2026-06-25</lastmod></url></urlset>", 1)
  path.write_text(raw, encoding="utf-8")


def update_status(path: Path, data: dict[str, Any], built_at: str) -> None:
  site = path.parent
  payload = load(path) if path.exists() else {}
  payload["root_html_pages"] = len(list(site.glob("*.html")))
  payload["published_html_pages_including_resources"] = len(list(site.rglob("*.html")))
  payload["sme_kernel_v3_institutional_publication"] = {
    "release": data["release_id"],
    "version": data["version"],
    "integration_revision": data["integration_revision"],
    "status": data["status"],
    "pages": PAGES,
    "primary_pages": 48,
    "latex_pages": 53,
    "use_cases": 10,
    "case_studies": 7,
    "autonomy_phases": 6,
    "kernel_interface_release": data["repository_alignment"]["kernel_interface_release"],
    "baseline_commit": data["repository_alignment"]["baseline_commit"],
    "canonical_suite_url": data["canonical_suite_url"],
    "claim_bounded": True,
    "canonical_v86_source_modified": False,
    "built_at": built_at,
  }
  dump(path, payload)


def reconcile_manifests(site: Path, data: dict[str, Any], built_at: str) -> list[str]:
  reconciled: list[str] = []
  for index, (filename, schema) in enumerate(MANIFEST_CHAIN):
    path = site / filename
    if not path.is_file():
      raise RuntimeError(f"Required companion manifest missing: {filename}")
    payload = load(path)
    if payload.get("schema") != schema:
      raise RuntimeError(f"Unrecognized companion manifest schema: {filename}")
    files = payload.get("files")
    if not isinstance(files, dict):
      raise RuntimeError(f"Companion manifest files missing: {filename}")
    declared = list(SHARED)
    if filename == "sme-kernel-v3-manifest.json":
      declared.extend(KERNEL_PAGES)
    for relative in declared:
      target = site / relative
      if target.is_file():
        files[relative] = file_record(target)
    for earlier_name, _ in MANIFEST_CHAIN[:index]:
      target = site / earlier_name
      if earlier_name in files and target.is_file():
        files[earlier_name] = file_record(target)
    integration = payload.setdefault("integration", {})
    history = integration.setdefault("reconciliations", [])
    if not isinstance(history, list):
      raise RuntimeError(f"Invalid reconciliation history: {filename}")
    history[:] = [entry for entry in history if not isinstance(entry, dict) or entry.get("release_id") != data["release_id"]]
    history.append({
      "release_id": data["release_id"],
      "version": data["version"],
      "integration_revision": data["integration_revision"],
      "built_at": built_at,
      "reason": "Repository-aligned Kernel v3 institutional publication extended declared shared and Kernel navigation surfaces",
      "files": declared,
      "canonical_v86_source_modified": False,
    })
    dump(path, payload)
    reconciled.append(filename)
  return reconciled


def write_downloads(site: Path, data: dict[str, Any], observation: dict[str, Any], built_at: str) -> list[Path]:
  target = site / "downloads/sme-kernel-v3-publication"
  target.mkdir(parents=True, exist_ok=True)
  alignment = dict(observation)
  alignment["observed_at"] = built_at
  alignment["expected"] = data["repository_alignment"]
  dump(target / "repository-alignment.json", alignment)
  provenance = {
    "schema": "goalos.sme_kernel_v3.publication_provenance.v2",
    "release_id": data["release_id"],
    "version": data["version"],
    "integration_revision": data["integration_revision"],
    "observed_at": built_at,
    "canonical_suite_url": data["canonical_suite_url"],
    "artifacts": data["artifacts"],
    "repository_alignment": alignment,
    "note": "SHA-256 values identify the canonical principal PDFs observed for this versioned publication suite. Validation claims remain those of the canonical publication package. Repository alignment proves source identity and build boundaries, not independent certification or production authorization.",
  }
  dump(target / "publication-provenance.json", provenance)
  citation = f'''@techreport{{boucher2026goaloskernelv3,
  author = {{Vincent Boucher}},
  title = {{{data['title']}}},
  institution = {{MONTREAL.AI and QUEBEC.AI}},
  year = {{2026}},
  month = {{June}},
  type = {{Research and Protocol Paper}},
  number = {{Institutional Use-Case and Case-Study Edition v3.0}},
  url = {{{data['canonical_suite_url']}}}
}}
'''
  (target / "kernel-v3-institutional-publication.bib").write_text(citation, encoding="utf-8")
  worksheet = """# GoalOS Kernel v3 — Institutional Use-Case Qualification Worksheet

## 1. Consequential objective
- Decision or action:
- Authorized owner:
- Success criterion:
- Failure criterion:
- Stop condition:

## 2. Evidence burden
- Primary sources required:
- Provenance and freshness requirements:
- Contradictions to surface:
- Independent evaluator:
- Dissent and challenge path:

## 3. Bounded execution
- Allowed tools and systems:
- Prohibited actions:
- Resource envelope:
- Data and privacy boundary:
- Monitoring and incident triggers:

## 4. Permission boundary
- Machine-complete state:
- Human reviewer:
- Permitted consequence:
- Expiry:
- Revocation and rollback:

## 5. Falsification
- What result would reject the thesis?
- What evidence would block permission?
- What remains unresolved?

This worksheet is a derivative operational aid. Use the canonical publication suite for the complete dossier standard and claim boundary.
"""
  (target / "institutional-use-case-qualification-worksheet.md").write_text(worksheet, encoding="utf-8")
  return [
    target / "publication-provenance.json",
    target / "repository-alignment.json",
    target / "kernel-v3-institutional-publication.bib",
    target / "institutional-use-case-qualification-worksheet.md",
  ]


def main() -> int:
  repo_default = Path(__file__).resolve().parents[2]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--site", type=Path, default=repo_default / "site")
  parser.add_argument("--root", type=Path, default=repo_default)
  parser.add_argument("--content", type=Path, default=repo_default / "content/sme-kernel-v3-institutional-publication.json")
  parser.add_argument("--kernel-content", type=Path, default=repo_default / "content/sme-kernel-v3.json")
  parser.add_argument("--workflow", type=Path, default=repo_default / ".github/workflows/goalos-agialpha-ascension-v86-final.yml")
  parser.add_argument("--source", type=Path, default=repo_default / "website/features/sme-kernel-v3-publication")
  args = parser.parse_args()
  site = args.site.resolve()
  root = args.root.resolve()
  source = args.source.resolve()
  content_path = args.content.resolve()
  built_at = iso(now())
  if not site.is_dir() or not (site / "index.html").is_file():
    raise RuntimeError(f"Built GoalOS site missing: {site}")
  prerequisites = [*KERNEL_PAGES, *[name for name, _ in MANIFEST_CHAIN]]
  for name in prerequisites:
    if not (site / name).is_file():
      raise RuntimeError(f"Build Kernel v3 before the institutional publication: {name}")
  data = load(content_path)
  validate_content(data)
  kernel, observation = validate_repository_alignment(data, root, args.kernel_content.resolve(), args.workflow.resolve())
  observation["observed_at"] = built_at
  before = {path.relative_to(site).as_posix(): sha_file(path) for path in site.rglob("*") if path.is_file()}
  template_path = source / "templates/base.html"
  if not template_path.is_file():
    raise RuntimeError(f"Missing template: {template_path}")
  template = template_path.read_text(encoding="utf-8")
  renderers: list[tuple[str, str, str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], str]]] = [
    (PAGES[0], "GoalOS Kernel v3 Institutional Paper — Proof-Bearing Autonomous Work", data["description"], render_paper),
    (PAGES[1], "GoalOS Kernel v3 Institutional Use Cases — Ten Operating Patterns", "Ten institutional operating patterns and seven claim-bounded proof-to-permission reference case studies.", render_use_cases),
    (PAGES[2], "GoalOS Kernel v3 Publication Proof — Validation, Provenance & Repository Alignment", "Validation, provenance, repository alignment, publication law, checksums, citation, and explicit claim boundaries for the GoalOS Kernel v3 institutional edition.", render_proof),
  ]
  outputs: list[Path] = []
  for page, title, description, renderer in renderers:
    output = site / page
    output.write_text(page_shell(template, data, page, title, description, renderer(data, kernel, observation)), encoding="utf-8")
    outputs.append(output)
  out_assets = site / "assets"
  out_assets.mkdir(parents=True, exist_ok=True)
  for asset in ASSETS:
    source_asset = source / "assets" / asset
    if not source_asset.is_file():
      raise RuntimeError(f"Missing publication asset: {source_asset}")
    destination = out_assets / asset
    shutil.copy2(source_asset, destination)
    outputs.append(destination)
  generated_data = dict(data)
  generated_data["observed_repository_alignment"] = observation
  generated_data["kernel_autonomy_chain"] = kernel["autonomy_chain"]
  data_output = site / "data/sme-kernel-v3-institutional-publication.json"
  dump(data_output, generated_data)
  outputs.append(data_output)
  patch_homepage(site / "index.html", data)
  kernel_pages_changed = patch_kernel_surfaces(site)
  update_routes(site / "routes.json", data)
  update_sitemap(site / "sitemap.xml")
  update_status(site / "site-status.json", data, built_at)
  reconciled = reconcile_manifests(site, data, built_at)
  downloads = write_downloads(site, data, observation, built_at)
  outputs.extend(downloads)
  outputs.extend(site / relative for relative in SHARED)
  outputs.extend(site / relative for relative in KERNEL_PAGES)
  outputs.extend(site / relative for relative in reconciled)
  after_core = {path.relative_to(site).as_posix(): sha_file(path) for path in site.rglob("*") if path.is_file()}
  removed = sorted(set(before) - set(after_core))
  changed = sorted(name for name in set(before) & set(after_core) if before[name] != after_core[name])
  own_outputs = set(PAGES + [f"assets/{asset}" for asset in ASSETS] + [
    "data/sme-kernel-v3-institutional-publication.json",
    "sme-kernel-v3-publication-manifest.json",
    "qa/sme-kernel-v3-publication-build.json",
    "downloads/sme-kernel-v3-publication/publication-provenance.json",
    "downloads/sme-kernel-v3-publication/repository-alignment.json",
    "downloads/sme-kernel-v3-publication/kernel-v3-institutional-publication.bib",
    "downloads/sme-kernel-v3-publication/institutional-use-case-qualification-worksheet.md",
  ])
  allowed_existing = set(SHARED) | set(KERNEL_PAGES) | set(reconciled) | own_outputs
  unexpected = sorted(set(changed) - allowed_existing)
  report = {
    "schema": BUILD_SCHEMA,
    "status": "PASS" if not removed and not unexpected and set(kernel_pages_changed) == set(KERNEL_PAGES) else "FAIL",
    "release_id": data["release_id"],
    "version": data["version"],
    "integration_revision": data["integration_revision"],
    "built_at": built_at,
    "pages": PAGES,
    "kernel_pages_cross_linked": kernel_pages_changed,
    "files_removed": removed,
    "existing_files_changed": changed,
    "declared_existing_files_allowed_to_change": sorted(allowed_existing | own_outputs),
    "unexpected_existing_file_changes": unexpected,
    "companion_manifests_reconciled": reconciled,
    "repository_alignment": observation,
    "canonical_v86_source_modified": False,
  }
  report_path = site / "qa/sme-kernel-v3-publication-build.json"
  dump(report_path, report)
  outputs.append(report_path)
  if report["status"] != "PASS":
    raise RuntimeError(f"Institutional publication preservation failed: {report}")
  files = {path.relative_to(site).as_posix(): file_record(path) for path in sorted(set(outputs))}
  manifest = {
    "schema": MANIFEST_SCHEMA,
    "release_id": data["release_id"],
    "title": data["title"],
    "version": data["version"],
    "integration_revision": data["integration_revision"],
    "built_at": built_at,
    "publication": {"primary_pages": 48, "latex_pages": 53, "use_cases": 10, "case_studies": 7, "claim_bounded": True},
    "repository_alignment": observation,
    "integration": {
      "mode": "additive-post-kernel-v3",
      "canonical_v86_source_modified": False,
      "homepage_markers": [STYLE_START, NAV_START, HOME_START],
      "kernel_markers": [KERNEL_LINK_START, KERNEL_CTA_START],
      "allowed_existing_changes": sorted(allowed_existing),
      "canonical_suite_url": data["canonical_suite_url"],
    },
    "files": files,
  }
  manifest_path = site / "sme-kernel-v3-publication-manifest.json"
  dump(manifest_path, manifest)
  print(json.dumps({"status": "PASS", "release": data["release_id"], "pages": PAGES, "alignment": observation["status"], "report": str(report_path)}, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
