#!/usr/bin/env python3
"""Build the additive GoalOS AGIALPHA Ascension AGI Alpha Node v0 Sovereign Citadel."""

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
FEATURE_PAGES = [
    "agi-alpha-node-v0.html",
    "agi-alpha-node-v0-architecture.html",
    "agi-alpha-node-v0-proof-ledger.html",
]
SHARED_INTEGRATION_OUTPUTS = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
COMPANION_MANIFESTS = {
    "meta-agentic-alpha-agi-manifest.json": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
}
STYLE_START = "<!-- GOALOS_AGI_ALPHA_NODE_V0_STYLE_START -->"
STYLE_END = "<!-- GOALOS_AGI_ALPHA_NODE_V0_STYLE_END -->"
NAV_START = "<!-- GOALOS_AGI_ALPHA_NODE_V0_NAV_START -->"
NAV_END = "<!-- GOALOS_AGI_ALPHA_NODE_V0_NAV_END -->"
HOME_START = "<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_START -->"
HOME_END = "<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_END -->"


def utc_now() -> datetime:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc) if epoch else datetime.now(timezone.utc)


def iso_seconds(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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
    expected_scalars = {
        "schema_version": "2.0.0",
        "release_title": RELEASE_TITLE,
        "version": "3.0.0-sovereign-citadel",
        "status": "interactive-sovereign-proof-node-digital-twin",
        "tagline": "One node. Many minds. Zero unearned authority.",
    }
    for key, expected in expected_scalars.items():
        if data.get(key) != expected:
            errors.append(f"{key} must equal {expected!r}")
    required_arrays = {
        "hero_metrics": 5,
        "thesis": 5,
        "work_unit_classes": 5,
        "presets": 5,
        "postures": 4,
        "risk_profiles": 3,
        "incidents": 4,
        "pipeline": 10,
        "node_roles": 10,
        "peers": 12,
        "validators": 7,
        "guardians": 5,
        "artifacts": 16,
        "architecture_translation": 10,
        "governance_principles": 7,
        "threats": 8,
        "claim_boundary": 7,
        "lineage_fingerprints": 15,
    }
    for key, exact in required_arrays.items():
        value = data.get(key)
        if not isinstance(value, list) or len(value) != exact:
            errors.append(f"{key} must contain exactly {exact} entries")
    expected_states = [
        "NODE_IDENTITY_SEALED",
        "WORK_UNIT_CONTRACTED",
        "POLICY_COMPILED",
        "RESOURCE_ENVELOPE_ADMITTED",
        "PEER_ROUTES_COMMITTED",
        "SANDBOX_RECEIPT_READY",
        "MULTI_AXIS_EVALUATION_READY",
        "VALIDATOR_QUORUM_RECORDED",
        "GUARDIAN_REVIEW_PACKAGED",
        "HUMAN_REVIEW_REQUIRED",
    ]
    observed_states = [item.get("state") for item in data.get("pipeline", []) if isinstance(item, dict)]
    if observed_states != expected_states:
        errors.append("pipeline must preserve the approved ten-state order")
    for posture in data.get("postures", []):
        weights = posture.get("weights") if isinstance(posture, dict) else None
        expected_weight_keys = {"quality", "reliability", "energy", "latency", "evidence", "diversity"}
        if not isinstance(weights, dict) or set(weights) != expected_weight_keys:
            errors.append(f"posture {posture.get('id', '?')} must define six weights")
        elif abs(sum(float(v) for v in weights.values()) - 1.0) > 1e-9:
            errors.append(f"posture {posture.get('id', '?')} weights must sum to 1")
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
        "content_security_policy": "connect-src none",
    }
    if not isinstance(security, dict):
        errors.append("security must be an object")
    else:
        for key, expected in expected_security.items():
            if security.get(key) != expected:
                errors.append(f"security.{key} must equal {expected!r}")
    lineage_paths = [item.get("path") for item in data.get("lineage_fingerprints", []) if isinstance(item, dict)]
    if len(lineage_paths) != len(set(lineage_paths)):
        errors.append("lineage_fingerprints paths must be unique")
    if errors:
        raise ValueError("Invalid AGI Alpha Node v0 release data:\n- " + "\n- ".join(errors))


def derive_mainnet_record(root: Path) -> dict[str, Any]:
    release_state = load_json(root / "qa" / "mainnet-release-state.json")
    registry = load_json(root / "config" / "ethereum-mainnet.contracts.json")
    contracts = registry.get("contracts", [])
    if not isinstance(contracts, list):
        raise ValueError("Mainnet contract registry contracts must be an array")
    goalos_contracts = [item for item in contracts if isinstance(item, dict) and item.get("deployedByGoalOS") is True]
    verified = [item for item in goalos_contracts if item.get("verifiedEvidence") is True]
    summary = release_state.get("summary", {})
    activation = release_state.get("activation", {})
    metadata = registry.get("metadata", {})
    return {
        "contracts": len(goalos_contracts),
        "verification": metadata.get("operatorVerificationEvidence", f"{len(verified)}/{len(goalos_contracts)}"),
        "phase_b_grants": summary.get("PHASE_B_GRANTS", "UNKNOWN"),
        "production_activation": activation.get("status", summary.get("PRODUCTION_ACTIVATION_EFFECTIVE", "UNKNOWN")),
        "user_fund_authorization": summary.get("USER_FUNDS_AUTHORIZED", metadata.get("userFundAuthorization", "UNKNOWN")),
        "source_identity": "PENDING",
        "chain_id": release_state.get("deployment", {}).get("chainId", 1),
        "record_source": ["qa/mainnet-release-state.json", "config/ethereum-mainnet.contracts.json"],
        "claim_boundary": metadata.get("claimBoundary", "Repository-derived evidence with explicit qualifiers."),
    }


def build_sample_docket(data: dict[str, Any]) -> dict[str, Any]:
    preset = data["presets"][0]
    primary = data["peers"][:4]
    shadow = data["peers"][4:7]
    config = {
        "node_name": "1.alpha.node.agi.eth",
        "mission": preset["mission"],
        "work_class": preset["work_class"],
        "risk": preset["risk"],
        "posture": "sovereign",
        "energy_target": 0.72,
        "latency_ceiling": 220,
        "incidents": [],
        "seed": 1776044417,
    }
    route = {
        "route_id": "route-9ec5ab3df901c2",
        "primary": [{"id": p["id"], "name": p["name"], "region": p["region"], "score": round(0.946 - i * 0.018, 3)} for i, p in enumerate(primary)],
        "shadow": [{"id": p["id"], "name": p["name"], "region": p["region"], "score": round(0.871 - i * 0.021, 3)} for i, p in enumerate(shadow)],
        "quarantined": [],
        "mitigation": "No incident-specific route mitigation required.",
    }
    receipt = {
        "work_unit_id": "awu-6dbf4c08db7461f9",
        "normalized_work_units": 1.184,
        "duration_ms": 482,
        "energy_score": 0.714,
        "memory_mb": 693,
        "streams": 21,
        "concurrency": 5,
        "packets": 166,
        "route_id": route["route_id"],
        "resource_pressure": 0.84,
        "resource_compliant": True,
        "mode": "deterministic-browser-local-simulation",
        "external_compute": False,
        "timestamp": "2026-06-23T12:14:24.170Z",
    }
    evaluation = {
        "quality": 0.917,
        "reliability": 0.961,
        "evidence": 0.908,
        "diversity": 0.857,
        "energy": 0.941,
        "latency": 0.963,
        "uncertainty": 0.112,
        "readiness": 0.914,
    }
    votes = []
    for index, validator in enumerate(data["validators"]):
        vote = "DISSENT" if index == 4 else "PASS"
        votes.append({**validator, "vote": vote, "score": 0.672 if vote == "DISSENT" else round(0.901 - index * 0.011, 3), "rationale": "Residual epistemic uncertainty must remain visible to the human reviewer." if vote == "DISSENT" else "The simulated gate evidence satisfies the review threshold."})
    consensus = {"votes": votes, "pass": 6, "dissent": 1, "reject": 0, "threshold": 5, "quorum_met": True, "summary": "6 pass · 1 dissent · 0 reject"}
    guardians = []
    for index, guardian in enumerate(data["guardians"]):
        disposition = "CAUTION" if index == 4 else "APPROVE"
        guardians.append({**guardian, "disposition": disposition, "rationale": "Recovery posture is documented; residual risk remains for human review." if disposition == "CAUTION" else "The constitutional boundary is intact for human review."})
    terminal = {
        "state": "HUMAN_REVIEW_REQUIRED",
        "title": "The proof package is ready for a human decision.",
        "copy": "The route, receipt, evaluation, validator quorum, dissent, guardian review, and chained evidence are complete. Factual correctness and external action remain unapproved.",
    }
    payloads = [
        {"node_name": config["node_name"], "origin": data["origin"]},
        {"mission": config["mission"], "work_class": config["work_class"], "risk": config["risk"]},
        {"posture": config["posture"], "prohibitions": ["network", "wallet", "transaction", "settlement", "production"]},
        {"latency_ceiling_ms": config["latency_ceiling"], "energy_target": config["energy_target"], "resource_compliant": True},
        {"candidates": [{"id": p["id"], "score": round(0.946 - i * 0.018, 3)} for i, p in enumerate(data["peers"])]},
        route,
        {"incidents": [], "quarantined": [], "residual_risk": "baseline"},
        receipt,
        {"latency_ms": 52.7, "reliability": 0.961, "evidence": 0.908, "external_network": False},
        evaluation,
        consensus,
        {"seats": guardians, "vetoes": []},
        {"state": terminal["state"], "permissions": {"external_action": False, "production": False, "funds": False, "factual_certification": False}},
        {"pipeline": [stage["state"] for stage in data["pipeline"]], "algorithm": "SHA-256"},
        {"schema": "goalos.agi_alpha_node_v0.node_evidence_docket.v2", "release_id": data["release_id"]},
        {"title": "Executive Review Brief", "recommendation": terminal["title"], "unresolved": [votes[4]["name"]]},
    ]
    previous = "0" * 64
    chain = []
    for index, meta in enumerate(data["artifacts"]):
        payload = payloads[index]
        artifact_hash = sha256_bytes(stable_json(payload).encode("utf-8"))
        commitment = sha256_bytes(f"{previous}:{artifact_hash}:{meta['name']}".encode("utf-8"))
        chain.append({
            "index": index + 1,
            "id": meta["id"],
            "name": meta["name"],
            "plane": meta["plane"],
            "purpose": meta["purpose"],
            "payload": payload,
            "previous_commitment": previous,
            "artifact_hash": artifact_hash,
            "commitment": commitment,
        })
        previous = commitment
    return {
        "schema": "goalos.agi_alpha_node_v0.node_evidence_docket.v2",
        "release": {"id": data["release_id"], "title": data["release_title"], "version": data["version"]},
        "generated_at": "2026-06-23T12:14:38.000Z",
        "deterministic_seed": config["seed"],
        "cryptographic_chain": "SHA-256",
        "node": {"identity": config["node_name"], "origin": data["origin"], "mode": "browser-local-digital-twin"},
        "mission": config,
        "peer_route": route,
        "alpha_work_unit_receipt": receipt,
        "evaluation": evaluation,
        "validator_consensus": consensus,
        "guardian_review": guardians,
        "terminal_disposition": terminal,
        "proof_chronicle": {"artifacts": chain, "chain_head": previous},
        "claim_boundary": data["claim_boundary"],
        "authority": {"factual_correctness": "NOT_CERTIFIED", "production_activation": "NOT_ACTIVATED", "funds_authorization": "NO", "external_actions": 0, "final_state": terminal["state"]},
    }


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
    if "@@" in rendered:
        raise ValueError("Unresolved template token remains")
    return rendered


def replace_block(text: str, start: str, end: str, block: str, fallback_marker: str) -> str:
    if text.count(start) != text.count(end):
        raise ValueError(f"Unbalanced integration markers: {start} / {end}")
    if start in text:
        prefix, remainder = text.split(start, 1)
        _, suffix = remainder.split(end, 1)
        return f"{prefix}{block}{suffix.lstrip(chr(10))}"
    position = text.find(fallback_marker)
    if position < 0:
        raise ValueError(f"Could not find integration point {fallback_marker!r}")
    return f"{text[:position]}{block}{text[position:]}"


def patch_homepage(index_path: Path) -> None:
    text = index_path.read_text(encoding="utf-8")
    style = f'{STYLE_START}\n<link rel="stylesheet" href="assets/agi-alpha-node-v0.css">\n{STYLE_END}\n'
    nav = f'{NAV_START}<a href="agi-alpha-node-v0.html">Alpha Node</a>{NAV_END}'
    home = f'''{HOME_START}
<section class="aan-home-gateway" id="agi-alpha-node-v0" aria-labelledby="aan-home-title">
  <div class="aan-home-gateway-inner">
    <div class="aan-home-gateway-copy">
      <span class="aan-home-kicker">SOVEREIGN CITADEL · PRIMARY + SHADOW MESH · PROOF BEFORE PERMISSION</span>
      <h2 id="aan-home-title">AGI ALPHA <em>NODE v0</em><small>GOALOS AGIALPHA ASCENSION ⚡️✨</small></h2>
      <p>One node. Many minds. Zero unearned authority. Contract a consequential mission, compile its constitution, admit bounded resources, route twelve peer institutions, rehearse adversarial incidents, preserve validator dissent, convene five guardians, and seal a sixteen-artifact Evidence Docket.</p>
      <div class="aan-home-gateway-doctrine"><span>10 proof gates</span><span>12 peer institutions</span><span>7 validators</span><span>5 guardians</span><span>16 chained artifacts</span><span>0 external actions</span></div>
      <div class="aan-home-gateway-actions"><a href="agi-alpha-node-v0.html">Enter the Sovereign Node Theatre →</a><a href="agi-alpha-node-v0-architecture.html">Read the constitution</a><a href="agi-alpha-node-v0-proof-ledger.html">Inspect the proof ledger</a></div>
    </div>
    <div class="aan-home-node-seal" aria-hidden="true"><i></i><i></i><i></i><i></i><span>GOALOS AGIALPHA</span><b>α</b><strong>SOVEREIGN CITADEL</strong><small>IDENTITY · MESH · PROOF · HUMAN AUTHORITY</small></div>
  </div>
</section>
{HOME_END}
'''
    text = replace_block(text, STYLE_START, STYLE_END, style, "</head>")
    text = replace_block(text, NAV_START, NAV_END, nav, "</nav>")
    text = replace_block(text, HOME_START, HOME_END, home, "</main>")
    index_path.write_text(text, encoding="utf-8")


def update_routes(site: Path, data: dict[str, Any]) -> None:
    path = site / "routes.json"
    payload = load_json(path) if path.exists() else {"version": "unknown", "routes": []}
    routes = payload.get("routes", [])
    if not isinstance(routes, list):
        raise ValueError("routes.json routes must be an array")
    payload["routes"] = sorted(set(map(str, routes)).union(FEATURE_PAGES))
    payload["agi_alpha_node_v0"] = {
        "release_id": data["release_id"],
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "integration": "additive-post-build",
        "runtime": "deterministic-browser-local-sovereign-citadel",
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


def reconcile_companion_manifests(site: Path, data: dict[str, Any], built_at: datetime) -> list[Path]:
    reconciled: list[Path] = []
    for filename, expected_schema in COMPANION_MANIFESTS.items():
        path = site / filename
        if not path.is_file():
            continue
        payload = load_json(path)
        if payload.get("schema") != expected_schema:
            raise ValueError(f"Refusing to reconcile unrecognized companion manifest: {path}")
        files = payload.get("files")
        if not isinstance(files, dict) or not all(name in files for name in SHARED_INTEGRATION_OUTPUTS):
            raise ValueError(f"Companion manifest is missing shared integration outputs: {path}")
        for relative in SHARED_INTEGRATION_OUTPUTS:
            target = site / relative
            if not target.is_file():
                raise FileNotFoundError(f"Shared integration output is missing: {target}")
            files[relative] = {"sha256": sha256(target), "bytes": target.stat().st_size}
        integration = payload.setdefault("integration", {})
        reconciliations = integration.setdefault("reconciliations", [])
        if not isinstance(reconciliations, list):
            raise ValueError(f"Companion manifest reconciliations must be an array: {path}")
        reconciliations[:] = [item for item in reconciliations if not isinstance(item, dict) or item.get("release_id") != data["release_id"]]
        reconciliations.append({
            "release_id": data["release_id"],
            "version": data["version"],
            "built_at": iso_seconds(built_at),
            "reason": "shared additive website surfaces were extended after the companion release",
            "files": SHARED_INTEGRATION_OUTPUTS,
        })
        write_json(path, payload)
        reconciled.append(path)
    return reconciled


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
        "proof_gated_states": 10,
        "peer_institutions": 12,
        "validator_seats": 7,
        "guardian_seats": 5,
        "evidence_artifacts": 16,
        "evidence_docket_schema": "goalos.agi_alpha_node_v0.node_evidence_docket.v2",
        "built_at": iso_seconds(built_at),
        "human_review_required": True,
        "external_actions": 0,
        "settlement_mode": "none",
    }
    write_json(path, payload)


def build(site: Path, content_path: Path, source: Path, root: Path) -> dict[str, Any]:
    built_at = utc_now()
    if not site.is_dir():
        raise FileNotFoundError(f"Site directory does not exist: {site}")
    if not (site / "index.html").is_file():
        raise FileNotFoundError(f"Site index does not exist: {site / 'index.html'}")
    data = load_json(content_path)
    validate_release(data)
    data["mainnet_record"] = derive_mainnet_record(root)
    data["sample_docket"] = build_sample_docket(data)
    data["lineage_root"] = sha256_bytes(":".join(item["sha256"] for item in data["lineage_fingerprints"]).encode("utf-8"))
    template_dir = source / "templates"
    asset_dir = source / "assets"
    page_templates = {
        "agi-alpha-node-v0.html": template_dir / "agi-alpha-node-v0.html",
        "agi-alpha-node-v0-architecture.html": template_dir / "agi-alpha-node-v0-architecture.html",
        "agi-alpha-node-v0-proof-ledger.html": template_dir / "agi-alpha-node-v0-proof-ledger.html",
    }
    required = [*page_templates.values(), asset_dir / "agi-alpha-node-v0.css", asset_dir / "agi-alpha-node-v0.js"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing AGI Alpha Node v0 sources:\n- " + "\n- ".join(missing))
    outputs: list[Path] = []
    for name, template in page_templates.items():
        output = site / name
        output.write_text(render_template(template.read_text(encoding="utf-8"), data, built_at), encoding="utf-8")
        outputs.append(output)
    (site / "assets").mkdir(parents=True, exist_ok=True)
    for filename in ["agi-alpha-node-v0.css", "agi-alpha-node-v0.js"]:
        output = site / "assets" / filename
        shutil.copy2(asset_dir / filename, output)
        outputs.append(output)
    data_output = site / "data" / "agi-alpha-node-v0.json"
    write_json(data_output, data)
    outputs.append(data_output)
    sample_output = site / "downloads" / "agi-alpha-node-v0" / "sample-node-evidence-docket.json"
    write_json(sample_output, data["sample_docket"])
    outputs.append(sample_output)
    patch_homepage(site / "index.html")
    update_routes(site, data)
    update_sitemap(site)
    update_site_status(site, data, built_at)
    outputs.extend(site / relative for relative in SHARED_INTEGRATION_OUTPUTS)
    companion_outputs = reconcile_companion_manifests(site, data, built_at)
    outputs.extend(companion_outputs)
    manifest_files = {path.relative_to(site).as_posix(): {"sha256": sha256(path), "bytes": path.stat().st_size} for path in outputs}
    manifest = {
        "schema": "goalos.agi_alpha_node_v0.website_manifest.v2",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "experience": {
            "runtime": "deterministic-browser-local-sovereign-citadel",
            "primary_and_shadow_routes": True,
            "incident_rehearsal": True,
            "proof_gates": 10,
            "peer_institutions": 12,
            "validator_seats": 7,
            "guardian_seats": 5,
            "evidence_artifacts": 16,
            "terminal_states": ["HUMAN_REVIEW_REQUIRED", "SAFE_HOLD"],
            "external_actions": 0,
        },
        "integration": {
            "mode": "additive-post-build",
            "canonical_v86_source_modified": False,
            "homepage_markers": [STYLE_START, NAV_START, HOME_START],
            "existing_outputs_allowed_to_change": [*SHARED_INTEGRATION_OUTPUTS, *[path.name for path in companion_outputs]],
            "companion_manifests_reconciled": [path.name for path in companion_outputs],
        },
        "repository_evidence": data["mainnet_record"],
        "lineage_root": data["lineage_root"],
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
            "existing_generated_site": "patched only at declared additive integration surfaces",
            "companion_manifests_reconciled": [path.name for path in companion_outputs],
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
    parser.add_argument("--root", type=Path, default=root)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build(args.site.resolve(), args.content.resolve(), args.source.resolve(), args.root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
