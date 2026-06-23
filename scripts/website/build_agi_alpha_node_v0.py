#!/usr/bin/env python3
"""Build the additive GoalOS AGIALPHA Ascension AGI Alpha Node v0 experience."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨"
FEATURE_ID = "agi-alpha-node-v0"
FEATURE_PAGES = ["agi-alpha-node-v0.html", "agi-alpha-node-v0-architecture.html"]
STYLE_START = "<!-- GOALOS_AGI_ALPHA_NODE_V0_STYLE_START -->"
STYLE_END = "<!-- GOALOS_AGI_ALPHA_NODE_V0_STYLE_END -->"
NAV_START = "<!-- GOALOS_AGI_ALPHA_NODE_V0_NAV_START -->"
NAV_END = "<!-- GOALOS_AGI_ALPHA_NODE_V0_NAV_END -->"
HOME_START = "<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_START -->"
HOME_END = "<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_END -->"
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
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def validate_release(data: dict[str, Any]) -> None:
    errors: list[str] = []
    expected_scalars = {
        "release_title": RELEASE_TITLE,
        "version": "1.0.0-ascension-alpha",
        "status": "interactive-sovereign-node-simulation",
    }
    for key, expected in expected_scalars.items():
        if data.get(key) != expected:
            errors.append(f"{key} must equal {expected!r}")

    required_arrays = {
        "hero_metrics": 4,
        "thesis": 3,
        "pipeline": 8,
        "node_roles": 8,
        "work_unit_classes": 4,
        "presets": 4,
        "postures": 3,
        "peers": 8,
        "validators": 7,
        "guardians": 5,
        "artifacts": 14,
        "architecture_translation": 8,
        "governance_principles": 6,
        "claim_boundary": 7,
    }
    for key, exact in required_arrays.items():
        value = data.get(key)
        if not isinstance(value, list) or len(value) != exact:
            errors.append(f"{key} must contain exactly {exact} entries")

    pipeline = data.get("pipeline", [])
    expected_states = [
        "NODE_IDENTITY_COMMITTED",
        "WORK_UNIT_CONTRACTED",
        "RESOURCE_ENVELOPE_ADMITTED",
        "PEER_ROUTE_COMMITTED",
        "SANDBOX_RECEIPT_READY",
        "QUALITY_EVALUATION_READY",
        "VALIDATOR_QUORUM_RECORDED",
        "HUMAN_REVIEW_REQUIRED",
    ]
    observed_states = [item.get("state") for item in pipeline if isinstance(item, dict)]
    if observed_states != expected_states:
        errors.append("pipeline must preserve the approved eight-state order")

    work_classes = data.get("work_unit_classes", [])
    class_ids = [item.get("id") for item in work_classes if isinstance(item, dict)]
    if class_ids != ["reason", "build", "verify", "orchestrate"]:
        errors.append("work_unit_classes must preserve the approved order")

    for posture in data.get("postures", []):
        weights = posture.get("weights") if isinstance(posture, dict) else None
        expected_weight_keys = {"quality", "reliability", "energy", "latency", "evidence"}
        if not isinstance(weights, dict) or set(weights) != expected_weight_keys:
            errors.append(f"posture {posture.get('id') if isinstance(posture, dict) else '?'} must define five weights")
        elif abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
            errors.append(f"posture {posture.get('id')} weights must sum to 1")

    security = data.get("security")
    expected_security = {
        "external_dependencies": False,
        "api_keys": False,
        "wallet_connection": False,
        "network_reads": False,
        "network_writes": False,
        "local_storage": False,
        "live_ens_resolution": False,
        "live_compute": False,
        "human_review_required": True,
        "settlement_mode": "none",
        "external_authority": "none",
    }
    if not isinstance(security, dict):
        errors.append("security must be an object")
    else:
        for key, expected in expected_security.items():
            if security.get(key) != expected:
                errors.append(f"security.{key} must equal {expected!r}")

    if errors:
        raise ValueError("Invalid AGI Alpha Node v0 release data:\n- " + "\n- ".join(errors))


def render_template(template: str, data: dict[str, Any], built_at: datetime) -> str:
    embedded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    replacements = {
        "@@TITLE@@": str(data["release_title"]),
        "@@DESCRIPTION@@": str(data["description"]),
        "@@VERSION@@": str(data["version"]),
        "@@ORIGIN_URL@@": str(data["origin"]["repository"]),
        "@@BUILD_DATE@@": built_at.strftime("%B %d, %Y"),
        "@@DATA_JSON@@": embedded,
    }
    rendered = template
    for token, replacement in replacements.items():
        rendered = rendered.replace(token, replacement)
    unresolved = [token for token in replacements if token in rendered]
    if unresolved or "@@" in rendered:
        raise ValueError(f"Unresolved template tokens: {', '.join(unresolved) or '@@'}")
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
    style_block = f'{STYLE_START}\n<link rel="stylesheet" href="assets/agi-alpha-node-v0.css">\n{STYLE_END}\n'
    nav_block = f'{NAV_START}<a href="agi-alpha-node-v0.html">AGI Alpha Node</a>{NAV_END}'
    home_block = f'''{HOME_START}
<section class="aan-home-gateway" id="agi-alpha-node-v0" aria-labelledby="aan-home-title">
  <div class="aan-home-gateway-inner">
    <div class="aan-home-gateway-copy">
      <span class="aan-home-kicker">SOVEREIGN COMPUTE · PROOF-CARRYING WORK · FLAGSHIP PUBLIC ALPHA</span>
      <h2 id="aan-home-title">AGI ALPHA <em>NODE v0</em><small>GOALOS AGIALPHA ASCENSION ⚡️✨</small></h2>
      <p>Compose one bounded work unit. Admit a deterministic peer route. Inspect normalized Alpha Work Units, resource and energy policy, telemetry, validator quorum, preserved dissent, guardian separation, and a fourteen-artifact Evidence Docket—while every real-world permission remains withheld.</p>
      <div class="aan-home-gateway-doctrine"><span>8 proof-gated states</span><span>7 validator seats</span><span>5 guardian seats</span><span>0 external actions</span></div>
      <div class="aan-home-gateway-actions">
        <a href="agi-alpha-node-v0.html">Enter the sovereign node →</a>
        <a href="agi-alpha-node-v0-architecture.html">Open the architecture dossier</a>
      </div>
    </div>
    <div class="aan-home-node-seal" aria-hidden="true"><i></i><i></i><i></i><i></i><span>GOALOS AGIALPHA</span><b>α</b><strong>SOVEREIGN PROOF NODE</strong><small>IDENTITY · WORK · QUORUM · AUTHORITY</small></div>
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
    payload["agi_alpha_node_v0"] = {
        "release_id": data["release_id"],
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "integration": "additive-post-build",
        "runtime": "deterministic-browser-local-sovereign-proof-node",
        "external_actions": 0,
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
    payload["agi_alpha_node_v0"] = {
        "status": data["status"],
        "release_title": RELEASE_TITLE,
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "proof_gated_states": len(data["pipeline"]),
        "validator_seats": len(data["validators"]),
        "guardian_seats": len(data["guardians"]),
        "evidence_artifacts": len(data["artifacts"]),
        "evidence_docket_schema": "goalos.agi_alpha_node_v0.node_evidence_docket.v1",
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
        template_dir / "agi-alpha-node-v0.html",
        template_dir / "agi-alpha-node-v0-architecture.html",
        asset_dir / "agi-alpha-node-v0.css",
        asset_dir / "agi-alpha-node-v0.js",
    ]
    missing = [str(path) for path in required_sources if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing AGI Alpha Node v0 sources:\n- " + "\n- ".join(missing))

    outputs: list[Path] = []
    page_templates = {
        "agi-alpha-node-v0.html": template_dir / "agi-alpha-node-v0.html",
        "agi-alpha-node-v0-architecture.html": template_dir / "agi-alpha-node-v0-architecture.html",
    }
    for output_name, template_path in page_templates.items():
        output_path = site / output_name
        output_path.write_text(render_template(template_path.read_text(encoding="utf-8"), data, built_at), encoding="utf-8")
        outputs.append(output_path)

    (site / "assets").mkdir(parents=True, exist_ok=True)
    for filename in ["agi-alpha-node-v0.css", "agi-alpha-node-v0.js"]:
        destination = site / "assets" / filename
        shutil.copy2(asset_dir / filename, destination)
        outputs.append(destination)

    data_destination = site / "data" / "agi-alpha-node-v0.json"
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
        "schema": "goalos.agi_alpha_node_v0.website_manifest.v1",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "experience": {
            "node_runtime": "deterministic-browser-local-simulation",
            "peer_route": "policy-scored-and-reviewable",
            "work_unit": "proof-carrying-normalized-alpha-work-unit",
            "validator_seats": 7,
            "guardian_seats": 5,
            "evidence_artifacts": 14,
            "final_state": "HUMAN_REVIEW_REQUIRED",
            "external_actions": 0,
            "human_authorization_required": True,
        },
        "integration": {
            "mode": "additive-post-build",
            "canonical_v86_source_modified": False,
            "homepage_markers": [STYLE_START, NAV_START, HOME_START],
        },
        "files": manifest_files,
    }
    manifest_path = site / "agi-alpha-node-v0-manifest.json"
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
    write_json(site / "qa" / "agi-alpha-node-v0-build.json", report)
    return report


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--content", type=Path, default=root / "content" / "agi-alpha-node-v0.json")
    parser.add_argument("--source", type=Path, default=root / "website" / "features" / "agi-alpha-node-v0")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build(args.site.resolve(), args.content.resolve(), args.source.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
