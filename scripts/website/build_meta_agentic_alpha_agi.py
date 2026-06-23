#!/usr/bin/env python3
"""Build the additive GoalOS META-Agentic α-AGI flagship experience."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨"
FEATURE_ID = "meta-agentic-alpha-agi"
FEATURE_PAGES = ["meta-agentic-alpha-agi.html", "meta-agentic-alpha-agi-architecture.html"]
STYLE_START = "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_STYLE_START -->"
STYLE_END = "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_STYLE_END -->"
NAV_START = "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_NAV_START -->"
NAV_END = "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_NAV_END -->"
HOME_START = "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_START -->"
HOME_END = "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END -->"
MARKERS = [STYLE_START, STYLE_END, NAV_START, NAV_END, HOME_START, HOME_END]


def utc_now() -> datetime:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc) if epoch else datetime.now(timezone.utc)


def iso_seconds(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_release(data: dict[str, Any]) -> None:
    errors: list[str] = []
    if data.get("release_title") != RELEASE_TITLE:
        errors.append("release_title must match the approved title exactly")
    if data.get("version") != "2.0.0-ascension-alpha":
        errors.append("version must be 2.0.0-ascension-alpha")
    required_arrays = {
        "hero_metrics": 4,
        "thesis": 3,
        "mission_flow": 8,
        "agents": 9,
        "objectives": 5,
        "artifacts": 16,
        "presets": 4,
        "risk_postures": 3,
        "architecture_translation": 6,
        "governance_principles": 6,
        "claim_boundary": 6,
    }
    for key, exact in required_arrays.items():
        value = data.get(key)
        if not isinstance(value, list) or len(value) != exact:
            errors.append(f"{key} must contain exactly {exact} entries")

    engine = data.get("candidate_engine")
    if not isinstance(engine, dict):
        errors.append("candidate_engine must be an object")
    else:
        if engine.get("generations") != 4:
            errors.append("candidate_engine.generations must equal 4")
        if engine.get("population_per_generation") != 6:
            errors.append("candidate_engine.population_per_generation must equal 6")
        for key in ["topologies", "reasoning_modes", "verifier_models", "governance_models", "memory_models", "execution_models"]:
            if not isinstance(engine.get(key), list) or len(engine[key]) != 6:
                errors.append(f"candidate_engine.{key} must contain exactly 6 entries")
        if not isinstance(engine.get("mutation_operators"), list) or len(engine["mutation_operators"]) < 8:
            errors.append("candidate_engine.mutation_operators must contain at least 8 entries")

    objective_ids = [item.get("id") for item in data.get("objectives", []) if isinstance(item, dict)]
    if objective_ids != ["evidence", "utility", "safety", "efficiency", "novelty"]:
        errors.append("objectives must preserve the approved five-objective order")
    for posture in data.get("risk_postures", []):
        weights = posture.get("weights") if isinstance(posture, dict) else None
        if not isinstance(weights, dict) or set(weights) != set(objective_ids):
            errors.append("every risk posture must define all five objective weights")
        elif abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
            errors.append(f"risk posture {posture.get('id')} weights must sum to 1")

    security = data.get("security")
    expected_security = {
        "external_dependencies": False,
        "api_keys": False,
        "wallet_connection": False,
        "network_writes": False,
        "local_storage": False,
        "human_review_required": True,
        "settlement_mode": "none",
    }
    if not isinstance(security, dict):
        errors.append("security must be an object")
    else:
        for key, expected in expected_security.items():
            if security.get(key) != expected:
                errors.append(f"security.{key} must equal {expected!r}")

    if errors:
        raise ValueError("Invalid META-Agentic release data:\n- " + "\n- ".join(errors))


def render_template(template: str, data: dict[str, Any], built_at: datetime) -> str:
    replacements = {
        "@@TITLE@@": str(data["release_title"]),
        "@@DESCRIPTION@@": str(data["description"]),
        "@@VERSION@@": str(data["version"]),
        "@@ORIGIN_URL@@": str(data["origin"]["repository"]),
        "@@BUILD_DATE@@": built_at.strftime("%B %d, %Y"),
    }
    rendered = template
    for token, replacement in replacements.items():
        rendered = rendered.replace(token, replacement)
    unresolved = [token for token in replacements if token in rendered]
    if unresolved:
        raise ValueError(f"Unresolved template tokens: {', '.join(unresolved)}")
    return rendered


def replace_block(text: str, start: str, end: str, block: str, fallback_marker: str, *, before: bool = True) -> str:
    if text.count(start) != text.count(end):
        raise ValueError(f"Unbalanced integration markers: {start} / {end}")
    if start in text:
        prefix, remainder = text.split(start, 1)
        _, suffix = remainder.split(end, 1)
        if block.endswith("\n"):
            suffix = suffix.lstrip("\r\n")
        return f"{prefix}{block}{suffix}"
    position = text.find(fallback_marker)
    if position < 0:
        raise ValueError(f"Could not find integration point {fallback_marker!r}")
    if not before:
        position += len(fallback_marker)
    return f"{text[:position]}{block}{text[position:]}"


def patch_homepage(index_path: Path) -> None:
    text = index_path.read_text(encoding="utf-8")
    style_block = f'{STYLE_START}\n<link rel="stylesheet" href="assets/meta-agentic-alpha-agi.css">\n{STYLE_END}\n'
    nav_block = f'{NAV_START}<a href="meta-agentic-alpha-agi.html">META‑AGENTIC α‑AGI</a>{NAV_END}'
    home_block = f'''{HOME_START}
<section class="maa-home-gateway" id="meta-agentic-alpha-agi" aria-labelledby="maa-home-title">
  <div class="maa-home-gateway-inner">
    <div>
      <span class="maa-home-kicker">GOALOS ASCENSION ENGINE · FLAGSHIP INTERACTIVE PUBLIC ALPHA</span>
      <h2 id="maa-home-title">META‑AGENTIC <em>α‑AGI</em> 👁️✨</h2>
      <p>The intelligence that architects intelligence. Compose one consequential mission; evolve twenty-four rival agent institutions; inspect every lineage, constitution, score, and trade-off; then seal a human-review-ready Evidence Docket with all external authority withheld.</p>
      <div class="maa-home-gateway-actions">
        <a href="meta-agentic-alpha-agi.html">Enter the Institution Foundry →</a>
        <a href="meta-agentic-alpha-agi-architecture.html">Open the architecture dossier</a>
      </div>
    </div>
    <div class="maa-home-seal" aria-hidden="true"><span>GOALOS AGIALPHA</span><b>MΨ</b><strong>META‑AGENTIC</strong><small>CREATE · EVOLVE · PROVE · AUTHORIZE</small></div>
  </div>
</section>
{HOME_END}
'''
    text = replace_block(text, STYLE_START, STYLE_END, style_block, "</head>", before=True)
    text = replace_block(text, NAV_START, NAV_END, nav_block, "</nav>", before=True)
    text = replace_block(text, HOME_START, HOME_END, home_block, "</main>", before=True)
    index_path.write_text(text, encoding="utf-8")


def update_routes(site: Path, data: dict[str, Any]) -> None:
    path = site / "routes.json"
    payload = load_json(path) if path.exists() else {"version": "unknown", "routes": []}
    routes = payload.get("routes")
    if not isinstance(routes, list):
        raise ValueError("routes.json routes must be an array")
    payload["routes"] = sorted(set(str(route) for route in routes).union(FEATURE_PAGES))
    payload["meta_agentic_alpha_agi"] = {
        "release_id": data["release_id"],
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "integration": "additive-post-build",
        "runtime": "deterministic-local-institution-foundry",
    }
    write_json(path, payload)


def update_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    text = path.read_text(encoding="utf-8") if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n</urlset>\n"
    entries = "".join(f"  <url><loc>./{page}</loc></url>\n" for page in FEATURE_PAGES if f"./{page}" not in text)
    if entries:
        if "</urlset>" not in text:
            raise ValueError("sitemap.xml is missing </urlset>")
        text = text.replace("</urlset>", f"{entries}</urlset>", 1)
    path.write_text(text, encoding="utf-8")


def update_site_status(site: Path, data: dict[str, Any], built_at: datetime) -> None:
    path = site / "site-status.json"
    payload = load_json(path) if path.exists() else {}
    payload["root_html_pages"] = len(list(site.glob("*.html")))
    payload["published_html_pages_including_resources"] = len(list(site.rglob("*.html")))
    payload["meta_agentic_alpha_agi"] = {
        "status": "interactive-institution-foundry",
        "release_title": RELEASE_TITLE,
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "candidate_population": data["candidate_engine"]["generations"] * data["candidate_engine"]["population_per_generation"],
        "pareto_selection": True,
        "evidence_docket_schema": "v2",
        "built_at": iso_seconds(built_at),
        "human_review_required": True,
        "external_actions": 0,
        "settlement_mode": "none",
    }
    write_json(path, payload)


def build(site: Path, content_path: Path, source: Path) -> dict[str, Any]:
    built_at = utc_now()
    if not site.is_dir():
        raise FileNotFoundError(f"Site directory does not exist: {site}")
    data = load_json(content_path)
    validate_release(data)
    template_dir = source / "templates"
    asset_dir = source / "assets"
    required_sources = [
        template_dir / "meta-agentic-alpha-agi.html",
        template_dir / "meta-agentic-alpha-agi-architecture.html",
        asset_dir / "meta-agentic-alpha-agi.css",
        asset_dir / "meta-agentic-alpha-agi.js",
    ]
    missing = [str(path) for path in required_sources if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing META-Agentic sources:\n- " + "\n- ".join(missing))

    outputs: list[Path] = []
    page_templates = {
        "meta-agentic-alpha-agi.html": template_dir / "meta-agentic-alpha-agi.html",
        "meta-agentic-alpha-agi-architecture.html": template_dir / "meta-agentic-alpha-agi-architecture.html",
    }
    for output_name, template_path in page_templates.items():
        output_path = site / output_name
        output_path.write_text(render_template(template_path.read_text(encoding="utf-8"), data, built_at), encoding="utf-8")
        outputs.append(output_path)

    (site / "assets").mkdir(parents=True, exist_ok=True)
    for filename in ["meta-agentic-alpha-agi.css", "meta-agentic-alpha-agi.js"]:
        destination = site / "assets" / filename
        shutil.copy2(asset_dir / filename, destination)
        outputs.append(destination)

    data_destination = site / "data" / "meta-agentic-alpha-agi.json"
    data_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(content_path, data_destination)
    outputs.append(data_destination)

    patch_homepage(site / "index.html")
    update_routes(site, data)
    update_sitemap(site)
    update_site_status(site, data, built_at)
    outputs.extend([site / "index.html", site / "routes.json", site / "sitemap.xml", site / "site-status.json"])

    manifest_files: dict[str, dict[str, Any]] = {}
    for path in outputs:
        relative = path.relative_to(site).as_posix()
        manifest_files[relative] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    manifest = {
        "schema": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "experience": {
            "candidate_engine": "deterministic-seeded-search",
            "default_population": 24,
            "generations": 4,
            "objectives": [objective["id"] for objective in data["objectives"]],
            "selection": "pareto-frontier-plus-posture-weighting",
            "evidence_docket": "v2",
            "human_authorization_required": True,
        },
        "integration": {
            "mode": "additive-post-build",
            "canonical_v86_source_modified": False,
            "homepage_markers": [STYLE_START, NAV_START, HOME_START],
        },
        "files": manifest_files,
    }
    manifest_path = site / "meta-agentic-alpha-agi-manifest.json"
    write_json(manifest_path, manifest)

    report = {
        "status": "PASS",
        "release_title": RELEASE_TITLE,
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "site": str(site),
        "pages": FEATURE_PAGES,
        "files_written": sorted([*manifest_files, manifest_path.relative_to(site).as_posix()]),
        "preservation": {
            "canonical_site_source": "untouched",
            "existing_generated_site": "patched only at marked additive integration points",
            "files_removed": 0,
        },
    }
    write_json(site / "qa" / "meta-agentic-alpha-agi-build.json", report)
    return report


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--content", type=Path, default=root / "content" / "meta-agentic-alpha-agi.json")
    parser.add_argument("--source", type=Path, default=root / "website" / "features" / "meta-agentic-alpha-agi")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build(args.site.resolve(), args.content.resolve(), args.source.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
