#!/usr/bin/env python3
"""Build the GoalOS Sovereign Machine Economy integration additively."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEATURE_ID = "sovereign-machine-economy"
RELEASE_TITLE = "GoalOS AGIALPHA Ascension Sovereign Machine Economy 👁️⚡️✨"
PAGES = [
    "sovereign-machine-economy.html",
    "sovereign-machine-economy-observatory.html",
    "sovereign-machine-economy-architecture.html",
    "sovereign-machine-economy-ledger.html",
    "sovereign-machine-economy-memory.html",
    "sovereign-machine-economy-passport.html",
]
SHARED = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
COMPANION_MANIFESTS = [
    ("meta-agentic-alpha-agi-manifest.json", "goalos.meta_agentic_alpha_agi.website_manifest.v2"),
    ("agi-alpha-node-v0-manifest.json", "goalos.agi_alpha_node_v0.website_manifest.v2"),
    ("agi-jobs-v0-v2-manifest.json", "goalos.agi_jobs_v0_v2.website_manifest.v3"),
]
DEPENDENCY_PAGES = [
    "meta-agentic-alpha-agi.html",
    "meta-agentic-alpha-agi-architecture.html",
    "agi-alpha-node-v0.html",
    "agi-alpha-node-v0-architecture.html",
    "agi-alpha-node-v0-proof-ledger.html",
    "agi-jobs-v0-v2.html",
    "agi-jobs-v0-v2-market.html",
    "agi-jobs-v0-v2-proof.html",
    "agi-jobs-v0-v2-settlement.html",
    "agi-jobs-v0-v2-architecture.html",
]
STYLE_START = "<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_START -->"
STYLE_END = "<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_END -->"
NAV_START = "<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_START -->"
NAV_END = "<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_END -->"
HOME_START = "<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_START -->"
HOME_END = "<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_END -->"
AGI_JOBS_NAV_END = "<!-- GOALOS_AGI_JOBS_V0_V2_NAV_END -->"
AGI_JOBS_HOME_END = "<!-- GOALOS_AGI_JOBS_V0_V2_HOME_END -->"
BASE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"


def utc_now() -> datetime:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc) if epoch else datetime.now(timezone.utc)


def iso_seconds(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_value(value: Any) -> str:
    return sha_bytes(stable(value).encode("utf-8"))


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_content(content: dict[str, Any]) -> None:
    errors: list[str] = []
    expected = {
        "schema_version": "2.0.0",
        "release_id": "GOALOS-AGIALPHA-SOVEREIGN-MACHINE-ECONOMY-002",
        "release_title": RELEASE_TITLE,
        "version": "2.0.0-constitutional-civilization-engine",
        "status": "interactive-constitutional-machine-economy-civilization-engine",
        "tagline": "A mind that builds minds. A node that turns intelligence into proof. A market that turns proof into accountable value.",
        "doctrine": "Minds are formed. Nodes execute. Markets coordinate. Proof earns permission. Humans authorize.",
    }
    for key, value in expected.items():
        if content.get(key) != value:
            errors.append(f"{key} must equal {value!r}")
    counts = {
        "source_releases": 3,
        "hero_metrics": 6,
        "thesis": 7,
        "mission_presets": 8,
        "postures": 4,
        "risk_profiles": 4,
        "incidents": 8,
        "gates": 21,
        "handoffs": 15,
        "artifact_classes": 48,
        "governance_principles": 10,
        "threats": 10,
        "memory_rules": 9,
        "review_actions": 4,
        "universes": 3,
        "constitutional_rights": 8,
        "claim_boundary": 10,
    }
    for key, count in counts.items():
        value = content.get(key)
        if not isinstance(value, list) or len(value) != count:
            errors.append(f"{key} must contain exactly {count} entries")
    if [item.get("id") for item in content.get("gates", [])] != [f"G{i:02d}" for i in range(1, 22)]:
        errors.append("gates must be ordered G01 through G21")
    if [item.get("id") for item in content.get("handoffs", [])] != [f"H{i:02d}" for i in range(1, 16)]:
        errors.append("handoffs must be ordered H01 through H15")
    planes = [item.get("plane") for item in content.get("artifact_classes", [])]
    if any(planes.count(plane) != 16 for plane in ["MIND", "NODE", "MARKET"]):
        errors.append("artifact planes must contain sixteen MIND, NODE, and MARKET records")
    security = content.get("security", {})
    for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "live_model_calls", "live_compute", "live_token_movement", "credential_issuance", "local_storage"]:
        if security.get(key) is not False:
            errors.append(f"security.{key} must be false")
    if security.get("external_authority") != "none" or security.get("human_review_required") is not True:
        errors.append("security authority boundary mismatch")
    if errors:
        raise RuntimeError("; ".join(errors))


def validate_dependencies(site: Path, meta: dict[str, Any], node: dict[str, Any], jobs: dict[str, Any]) -> None:
    expected = [
        (meta, "GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨"),
        (node, "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨"),
        (jobs, "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"),
    ]
    for release, title in expected:
        if release.get("release_title") != title:
            raise RuntimeError(f"dependency title mismatch: expected {title!r}")
    missing = [name for name in DEPENDENCY_PAGES if not (site / name).is_file() or (site / name).stat().st_size < 1000]
    missing += [name for name, _ in COMPANION_MANIFESTS if not (site / name).is_file()]
    if missing:
        raise RuntimeError("Build META-Agentic, AGI Alpha Node, and AGI Jobs before the Sovereign Machine Economy: " + ", ".join(missing))


def lineage(root: Path, site: Path) -> tuple[list[dict[str, Any]], str]:
    paths = [
        root / "content/meta-agentic-alpha-agi.json",
        root / "content/agi-alpha-node-v0.json",
        root / "content/agi-jobs-v0-v2.json",
        root / "scripts/website/build_meta_agentic_alpha_agi.py",
        root / "scripts/website/build_agi_alpha_node_v0.py",
        root / "scripts/website/build_agi_jobs_v0_v2.py",
        root / "website/features/meta-agentic-alpha-agi/assets/meta-agentic-alpha-agi.js",
        root / "website/features/agi-alpha-node-v0/assets/agi-alpha-node-v0.js",
        root / "website/features/agi-jobs-v0-v2/assets/agi-jobs-v0-v2.js",
        site / "meta-agentic-alpha-agi-manifest.json",
        site / "agi-alpha-node-v0-manifest.json",
        site / "agi-jobs-v0-v2-manifest.json",
        root / "content/sovereign-machine-economy.json",
        root / "scripts/website/build_sovereign_machine_economy.py",
        root / "website/features/sovereign-machine-economy/assets/sovereign-machine-economy.js",
    ]
    rows = []
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"lineage input missing: {path}")
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            relative = f"generated/{path.name}"
        if path.parent == site and path.name in {name for name, _ in COMPANION_MANIFESTS}:
            manifest = load_json(path)
            files = manifest.get("files")
            if isinstance(files, dict):
                for mutable in [*SHARED, *[name for name, _ in COMPANION_MANIFESTS]]:
                    files.pop(mutable, None)
            integration = manifest.get("integration")
            if isinstance(integration, dict):
                integration.pop("reconciliations", None)
            normalized = stable(manifest).encode("utf-8")
            fingerprint = sha_bytes(normalized)
            fingerprint_bytes = len(normalized)
        else:
            fingerprint = sha_file(path)
            fingerprint_bytes = path.stat().st_size
        rows.append({"path": relative, "sha256": fingerprint, "bytes": fingerprint_bytes})
    return rows, sha_value([item["sha256"] for item in rows])


def compile_data(content: dict[str, Any], meta: dict[str, Any], node: dict[str, Any], jobs: dict[str, Any], mainnet: dict[str, Any], fingerprints: list[dict[str, Any]], lineage_root: str, built_at: str) -> dict[str, Any]:
    payload = json.loads(json.dumps(content))
    payload["built_at"] = built_at
    payload["dependencies"] = {
        "meta": {"release_id": meta.get("release_id"), "title": meta.get("release_title"), "version": meta.get("version"), "status": meta.get("status"), "agents": meta.get("agents", [])},
        "node": {"release_id": node.get("release_id"), "title": node.get("release_title"), "version": node.get("version"), "status": node.get("status"), "peers": node.get("peers", []), "validators": node.get("validators", []), "guardians": node.get("guardians", [])},
        "jobs": {"release_id": jobs.get("release_id"), "title": jobs.get("release_title"), "version": jobs.get("version"), "status": jobs.get("status"), "institutions": jobs.get("institutions", []), "validators": jobs.get("validators", []), "guardians": jobs.get("guardians", [])},
    }
    payload["mainnet_record"] = {
        "network": mainnet.get("network", "Ethereum Mainnet"),
        "contracts": mainnet.get("goalosCreatedContractCount", 48),
        "verification": f"{mainnet.get('verification', {}).get('verified', 48)}/{mainnet.get('verification', {}).get('goalosContracts', 48)}",
        "production_activation": "NOT_ACTIVATED",
        "user_fund_authorization": "NO",
    }
    payload["lineage_fingerprints"] = fingerprints
    payload["lineage_root"] = lineage_root
    return payload


def deterministic_choice(items: list[dict[str, Any]], seed: str, count: int, salt: str) -> list[dict[str, Any]]:
    ranked = sorted(items, key=lambda item: sha_value([seed, salt, item]), reverse=True)
    return ranked[: min(count, len(ranked))]


def sample_docket(data: dict[str, Any]) -> dict[str, Any]:
    preset = data["mission_presets"][1]
    posture = next(x for x in data["postures"] if x["id"] == "balanced")
    risk = next(x for x in data["risk_profiles"] if x["id"] == "high")
    incident = next(x for x in data["incidents"] if x["id"] == "none")
    commission = {
        "mission": preset["mission"],
        "preset": preset,
        "domain": preset["domain"],
        "posture": posture,
        "risk": risk,
        "incident": incident,
    }
    seed = sha_value({
        "release": data["release_id"],
        "mission": commission["mission"],
        "preset": preset["id"],
        "posture": posture["id"],
        "risk": risk["id"],
        "incident": incident["id"],
    })
    agents = deterministic_choice(data["dependencies"]["meta"]["agents"], seed, 6, "agents")
    peers = deterministic_choice(data["dependencies"]["node"]["peers"], seed, 7, "peers")
    guilds = deterministic_choice(data["dependencies"]["jobs"]["institutions"], seed, 6, "guilds")
    validator_catalog = data["dependencies"]["jobs"]["validators"]
    dissent_seat = next((item for item in validator_catalog if str(item.get("id", "")).upper() == "V09" or "independent dissent" in str(item.get("name", "")).lower()), None)
    validator_pool = [item for item in validator_catalog if item is not dissent_seat]
    validators = deterministic_choice(validator_pool, seed, max(0, risk["validator_seats"] - (1 if dissent_seat else 0)), "validators")
    if dissent_seat:
        validators.append(dissent_seat)
    validators = validators[: risk["validator_seats"]]
    institution = {
        "id": "INST-" + sha_value([seed, "institution"])[:12].upper(),
        "name": "Apex Research Covenant",
        "roles": [{"id": x.get("id"), "name": x.get("name"), "authority": x.get("boundary") or x.get("mandate")} for x in agents],
        "metrics": {"evidence": 94, "safety": 92, "rights": 91, "utility": 90, "efficiency": 84, "novelty": 88},
        "candidate_count": 9,
        "frontier_count": 4,
        "lineage_root": sha_value({"seed": seed, "roles": [x.get("id") for x in agents], "mission": commission["mission"]}),
        "charter_commitment": sha_value({"mission": commission["mission"], "roles": [x.get("id") for x in agents], "posture": posture["id"]}),
        "authority": "BOUNDED_AND_REVOCABLE",
    }
    route = {
        "primary": [{"id": x.get("id"), "name": x.get("name"), "region": x.get("region", "DECLARED")} for x in peers[:4]],
        "shadow": [{"id": x.get("id"), "name": x.get("name"), "region": x.get("region", "DECLARED")} for x in peers[4:7]],
    }
    envelope = {
        "risk": risk["id"],
        "multiplier": risk["resource_multiplier"],
        "max_external_actions": 0,
        "network_requests": 0,
        "wallet_connections": 0,
        "live_token_movements": 0,
    }
    node_record = {
        "id": "NODE-" + sha_value([seed, "node"])[:12].upper(),
        "route_id": "ROUTE-" + sha_value(route)[:12].upper(),
        **route,
        "identity_commitment": sha_value({"institution": institution["id"], "lineage": institution["lineage_root"], "release": data["dependencies"]["node"]["version"], "route": route}),
        "resource_constitution": envelope,
        "resource_commitment": sha_value(envelope),
        "receipt_id": "AWU-" + sha_value([seed, "receipt"])[:16].upper(),
        "external_actions": 0,
        "wallet_connections": 0,
        "network_requests": 0,
    }
    opinions = []
    for index, validator in enumerate(validators):
        protected_dissent = validator is dissent_seat if dissent_seat else index == len(validators) - 1
        verdict = "DISSENT" if protected_dissent else "PASS"
        score = 66 if verdict == "DISSENT" else 84 + index
        opinions.append({
            "id": validator.get("id"),
            "name": validator.get("name"),
            "verdict": verdict,
            "score": score,
            "conflict": "NONE_DECLARED",
            "commitment": sha_value({"seed": seed, "index": index, "verdict": verdict, "score": score}),
        })
    market = {
        "id": "MARKET-" + sha_value([seed, "market"])[:12].upper(),
        "frontier": [{"id": x.get("id"), "name": x.get("name"), "weighted_score": 90 - index} for index, x in enumerate(guilds[:4])],
        "coalition_id": "COALITION-" + sha_value([x.get("id") for x in guilds])[:12].upper(),
        "coalition": [{"id": x.get("id"), "name": x.get("name"), "role": role, "weighted_score": 94 - index} for index, (x, role) in enumerate(zip(guilds, ["PRIME", "EVIDENCE", "ASSURANCE", "DELIVERY", "SHADOW", "RESERVE"]))],
        "parliament": {
            "seats": len(validators),
            "threshold": risk["threshold"],
            "pass": max(0, len(validators) - 1),
            "dissent": 1,
            "reject": 0,
            "opinions": opinions,
        },
        "challenge_hours": risk["challenge_hours"],
        "charter_commitment": sha_value({"mission": commission["mission"], "institution": institution["id"], "node": node_record["id"]}),
        "settlement": {"status": "HUMAN_SETTLEMENT_REVIEW", "live": False, "wallet_connection": False, "token_movement": False, "external_actions": 0},
    }
    handoffs = []
    previous = "0" * 64
    for item in data["handoffs"]:
        payload = {"id": item["id"], "from": item["from"], "to": item["to"], "name": item["name"], "mission": commission["mission"], "institution": institution["id"], "node": node_record["id"], "market": market["id"], "previous": previous}
        commitment = sha_value(payload)
        handoffs.append({**item, "previous_commitment": previous, "commitment": commitment})
        previous = commitment
    artifacts = []
    previous = "0" * 64
    for index, meta in enumerate(data["artifact_classes"], 1):
        payload = {
            "id": f"A{index:02d}",
            "plane": meta["plane"],
            "name": meta["name"],
            "run_seed": seed,
            "mission": commission["mission"],
            "institution": institution["id"],
            "node": node_record["id"],
            "market": market["id"],
            "terminal": "HUMAN_SETTLEMENT_REVIEW",
        }
        artifact_hash = sha_value(payload)
        commitment = sha_value({"previous": previous, "payload": payload, "artifact_hash": artifact_hash})
        artifacts.append({"id": f"A{index:02d}", "plane": meta["plane"], "name": meta["name"], "previous_commitment": previous, "artifact_hash": artifact_hash, "commitment": commitment, "payload": payload})
        previous = commitment
    memory = {
        "id": "MEM-" + sha_value([seed, "memory"])[:12].upper(),
        "status": "HUMAN_PROMOTION_REQUIRED",
        "scope": preset["domain"],
        "expiry": "90_DAYS_AFTER_APPROVAL",
        "revocable": True,
        "evidence_root": previous,
        "automatic_promotion": False,
        "failure_memory_preserved": True,
    }
    universes = []
    for universe in data["universes"]:
        universe_posture = next(x for x in data["postures"] if x["id"] == universe["posture"])
        shift = {"prudential": 3, "balanced": 0, "frontier": -2}[universe["id"]]
        universes.append({
            "id": universe["id"],
            "label": universe["label"],
            "promise": universe["promise"],
            "posture": universe_posture["id"],
            "institution": "INST-" + sha_value([seed, universe["id"], "institution"])[:12].upper(),
            "route": "ROUTE-" + sha_value([seed, universe["id"], "route"])[:12].upper(),
            "coalition": "COALITION-" + sha_value([seed, universe["id"], "coalition"])[:12].upper(),
            "terminal_state": "HUMAN_SETTLEMENT_REVIEW",
            "authority": "NONE_GRANTED",
            "external_actions": 0,
            "scores": {"evidence": 92 + shift, "safety": 90 + shift, "rights": 89 + shift, "utility": 88 - shift, "efficiency": 82 - shift, "novelty": 84 - shift},
            "commitment": sha_value({"seed": seed, "universe": universe["id"], "posture": universe_posture["weights"]}),
        })
    review = {
        "status": "PENDING_HUMAN_REVIEW",
        "selected_action": None,
        "record": None,
        "available_actions": data["review_actions"],
        "authority_granted": False,
        "settlement_authorized": False,
        "memory_promoted": False,
    }
    docket = {
        "schema": "goalos.sovereign_machine_economy.docket.v2",
        "release_id": data["release_id"],
        "run_id": "SME-" + seed[:16].upper(),
        "mission": commission,
        "institution": institution,
        "node": node_record,
        "market": market,
        "handoffs": handoffs,
        "evidence": {"artifact_count": len(artifacts), "chain_head": previous, "artifacts": artifacts},
        "counterfactuals": universes,
        "review": review,
        "memory": memory,
        "incident": {"id": incident["id"], "label": incident["label"], "effect": incident["effect"], "stop_gate": incident["stop_gate"]},
        "authority": {
            "terminal_state": "HUMAN_SETTLEMENT_REVIEW",
            "external_authority": "NONE_GRANTED",
            "factual_correctness": "NOT_CERTIFIED",
            "production_activation": "NOT_ACTIVATED",
            "user_fund_authorization": "NO",
            "automatic_memory_promotion": "NOT_AUTHORIZED",
            "external_actions": 0,
            "network_requests": 0,
            "wallet_connections": 0,
            "live_token_movements": 0,
        },
        "claim_boundary": data["claim_boundary"],
    }
    docket["economy_root"] = sha_value({"institution": institution["charter_commitment"], "node": node_record["identity_commitment"], "market": market["charter_commitment"], "handoffs": handoffs[-1]["commitment"], "evidence": previous, "counterfactuals": [x["commitment"] for x in universes], "memory": memory["id"], "review": review["status"], "terminal": "HUMAN_SETTLEMENT_REVIEW"})
    docket["run_commitment"] = sha_value(docket)
    return docket


def executive_brief(docket: dict[str, Any]) -> str:
    return f"""# GoalOS Sovereign Machine Economy Ω — Executive Review Brief

**Run:** `{docket['run_id']}`  
**Economy root:** `{docket['economy_root']}`  
**Terminal state:** `{docket['authority']['terminal_state']}`  
**Authority:** `{docket['authority']['external_authority']}`

## Mission

{docket['mission']['mission']}

## Constitutional civilization engine

- Mind Foundry: **{docket['institution']['name']}** (`{docket['institution']['id']}`)
- Proof Node: **{docket['node']['id']}**; route `{docket['node']['route_id']}`
- Work Economy: **{docket['market']['coalition_id']}**; {docket['market']['parliament']['seats']} validator seats
- Human Review Chamber: **{docket['review']['status']}**

## Proof fabric

- Typed interinstitutional handoffs: **{len(docket['handoffs'])}**
- Chained evidence artifacts: **{docket['evidence']['artifact_count']}**
- Counterfactual universes: **{len(docket['counterfactuals'])}**
- Evidence chain head: `{docket['evidence']['chain_head']}`
- Independent dissent preserved: **{docket['market']['parliament']['dissent']}**

## Authority boundary

- External actions: **0**
- Network requests: **0**
- Wallet connections: **0**
- Live token movements: **0**
- Production activation: **NOT_ACTIVATED**
- Automatic memory promotion: **NOT_AUTHORIZED**
- Factual correctness: **NOT_CERTIFIED**

**The proof package is ready for human settlement review. No external authority, execution authority, fund authority, or memory-promotion authority has been granted.**
"""


def common_head(title: str, description: str) -> str:
    csp = "default-src 'none'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'none'; media-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'"
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#07090d"><meta name="description" content="{html_escape(description)}"><meta http-equiv="Content-Security-Policy" content="{csp}"><title>{html_escape(title)}</title><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 rx=%2718%27 fill=%27%2307090d%27/%3E%3Ccircle cx=%2732%27 cy=%2732%27 r=%2721%27 fill=%27none%27 stroke=%27%2379f0da%27 stroke-width=%273%27/%3E%3Ccircle cx=%2732%27 cy=%2716%27 r=%276%27 fill=%27%23e8cd77%27/%3E%3Ccircle cx=%2718%27 cy=%2741%27 r=%276%27 fill=%27%2379f0da%27/%3E%3Ccircle cx=%2746%27 cy=%2741%27 r=%276%27 fill=%27%239b84ff%27/%3E%3C/svg%3E"><link rel="stylesheet" href="assets/sovereign-machine-economy.css"><script defer src="assets/sovereign-machine-economy.js"></script>'''


def html_escape(value: Any) -> str:
    import html
    return html.escape(str(value), quote=True)


def nav(current: str) -> str:
    links = [
        ("experience", "sovereign-machine-economy.html", "Civilization"),
        ("observatory", "sovereign-machine-economy-observatory.html", "Observatory"),
        ("architecture", "sovereign-machine-economy-architecture.html", "Constitution"),
        ("ledger", "sovereign-machine-economy-ledger.html", "Chronicle"),
        ("memory", "sovereign-machine-economy-memory.html", "Memory"),
        ("passport", "sovereign-machine-economy-passport.html", "Passport"),
    ]
    own = "".join(f'<a href="{href}" aria-current="page">{label}</a>' if key == current else f'<a href="{href}">{label}</a>' for key, href, label in links)
    engines = '<a class="sme-nav-engine" href="meta-agentic-alpha-agi.html">META‑AGENTIC</a><a class="sme-nav-engine" href="agi-alpha-node-v0.html">Alpha Node</a><a class="sme-nav-engine" href="agi-jobs-v0-v2.html">AGI Jobs</a>'
    return f'''<a class="sme-skip" href="#main">Skip to content</a><nav class="sme-nav" aria-label="Sovereign Machine Economy navigation"><div class="sme-shell sme-navin"><a class="sme-brand" href="index.html"><span class="sme-brand-mark" aria-hidden="true"></span><span>GoalOS · Sovereign Machine Economy Ω</span></a><div class="sme-navlinks">{own}{engines}<a href="index.html">GoalOS Home</a></div></div></nav>'''


def footer(data: dict[str, Any]) -> str:
    return f'''<footer class="sme-footer"><div class="sme-shell sme-footerin"><span><strong>{html_escape(data['release_title'])}</strong> · {html_escape(data['version'])}</span><span>Three sovereign engines · twenty-one proof gates · human authority remains final</span></div></footer>'''


def render_template(path: Path, page_key: str, data: dict[str, Any]) -> str:
    titles = {
        "experience": (data["release_title"], data["description"]),
        "observatory": ("Sovereign Machine Economy Ω — Counterfactual Observatory", "Compare three constitutional universes under identical mission constraints."),
        "architecture": ("Sovereign Machine Economy Ω — Constitutional Architecture", "Three separately governed engines joined by proof-bearing handoffs and rights."),
        "ledger": ("Sovereign Machine Economy Ω — Proof Chronicle", "The forty-eight-artifact evidence standard and fifteen cross-engine commitments."),
        "memory": ("Sovereign Machine Economy Ω — Recursive Capability Memory", "Scoped, expiring, revocable capability memory without self-promotion."),
        "passport": ("Sovereign Machine Economy Ω — Mission Passport", "A portable local proof passport for human review of constitutional machine work."),
    }
    raw = path.read_text(encoding="utf-8")
    embedded = stable(data).replace("</script", "<\\/script")
    replacements = {
        "{{COMMON_HEAD}}": common_head(*titles[page_key]),
        "{{NAV}}": nav(page_key),
        "{{FOOTER}}": footer(data),
        "{{DATA_SCRIPT}}": f'<script type="application/json" id="sme-data">{embedded}</script>',
    }
    for key, value in replacements.items():
        raw = raw.replace(key, value)
    if "{{" in raw:
        raise RuntimeError(f"unresolved template token in {path}")
    return raw


def replace_marked(raw: str, start: str, end: str, replacement: str) -> str:
    if raw.count(start) != 1 or raw.count(end) != 1:
        raise RuntimeError(f"marker count mismatch for {start}")
    return re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, raw, count=1, flags=re.S)


def home_gateway() -> str:
    return f'''{HOME_START}<section class="sme-home-gateway" id="sovereign-machine-economy" data-goalos-feature="sovereign-machine-economy"><div class="sme-home-in"><div><div class="sme-home-kicker">GOALOS AGIALPHA ASCENSION · CONSTITUTIONAL CIVILIZATION ENGINE Ω</div><h2>THE SOVEREIGN <span>MACHINE ECONOMY</span></h2><p><strong>A mind that builds minds. A node that turns intelligence into proof. A market that turns proof into accountable value.</strong> Three sovereign engines now form one inspectable constitutional civilization—with counterfactual worlds, typed handoffs, a forty-eight-artifact Chronicle, portable mission passports, and an explicit Human Review Chamber.</p><p class="sme-home-constellation"><strong>GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨</strong> × <strong>GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨</strong> × <strong>GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨</strong></p><div class="sme-home-pills"><span>3 sovereign engines</span><span>21 proof gates</span><span>15 typed handoffs</span><span>48 evidence artifacts</span><span>3 counterfactual worlds</span><span>0 external actions</span></div><div class="sme-home-actions"><a href="sovereign-machine-economy.html">Enter the Civilization</a><a href="sovereign-machine-economy-observatory.html">Open the Observatory</a><a href="sovereign-machine-economy-passport.html">Inspect the Passport</a></div></div><div class="sme-home-triad" aria-label="Mind foundry, proof node, work economy, and human authority"><div class="sme-home-flow"></div><div class="sme-home-engine meta"><span><small>👁️</small>MIND<br>FOUNDRY</span></div><div class="sme-home-engine node"><span><small>⚡</small>PROOF<br>NODE</span></div><div class="sme-home-engine jobs"><span><small>✦</small>WORK<br>ECONOMY</span></div><div class="sme-home-core">GOALOS<br>Ω PROOF<br>ECONOMY</div><div class="sme-home-human">HUMAN CONSTITUTIONAL BOUNDARY</div><i></i><i></i><i></i></div></div></section>{HOME_END}'''


def inject_homepage(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    style = f'{STYLE_START}<link rel="stylesheet" href="assets/sovereign-machine-economy.css" data-goalos-sovereign-machine-economy>{STYLE_END}'
    if STYLE_START in raw:
        raw = replace_marked(raw, STYLE_START, STYLE_END, style)
    elif "</head>" in raw:
        raw = raw.replace("</head>", style + "\n</head>", 1)
    else:
        raise RuntimeError("homepage lacks </head>")
    nav_html = f'{NAV_START}<a href="sovereign-machine-economy.html">Machine Economy Ω</a>{NAV_END}'
    if NAV_START in raw:
        raw = replace_marked(raw, NAV_START, NAV_END, nav_html)
    elif AGI_JOBS_NAV_END in raw:
        raw = raw.replace(AGI_JOBS_NAV_END, AGI_JOBS_NAV_END + nav_html, 1)
    elif "</nav>" in raw:
        raw = raw.replace("</nav>", nav_html + "</nav>", 1)
    else:
        raise RuntimeError("homepage lacks a safe navigation insertion point")
    section = home_gateway()
    if HOME_START in raw:
        raw = replace_marked(raw, HOME_START, HOME_END, section)
    elif AGI_JOBS_HOME_END in raw:
        raw = raw.replace(AGI_JOBS_HOME_END, AGI_JOBS_HOME_END + "\n" + section, 1)
    elif "</main>" in raw:
        raw = raw.replace("</main>", section + "\n</main>", 1)
    elif "</body>" in raw:
        raw = raw.replace("</body>", section + "\n</body>", 1)
    else:
        raise RuntimeError("homepage lacks a safe section insertion point")
    path.write_text(raw, encoding="utf-8")


def update_routes(path: Path, data: dict[str, Any]) -> None:
    payload = load_json(path) if path.exists() else {"version": "unknown", "routes": []}
    routes = payload.get("routes", [])
    if not isinstance(routes, list):
        raise RuntimeError("routes.json routes must be an array")
    payload["routes"] = sorted(set(map(str, routes)).union(PAGES))
    payload["sovereign_machine_economy"] = {
        "release_id": data["release_id"],
        "version": data["version"],
        "pages": PAGES,
        "engines": [x["id"] for x in data["source_releases"]],
        "constitutional_gates": len(data["gates"]),
        "handoffs": len(data["handoffs"]),
        "artifacts": len(data["artifact_classes"]),
        "external_actions": 0,
    }
    write_json(path, payload)


def update_sitemap(path: Path) -> None:
    raw = path.read_text(encoding="utf-8") if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset></urlset>"
    for page in PAGES:
        if page in raw:
            continue
        if "</urlset>" not in raw:
            raise RuntimeError("invalid sitemap")
        raw = raw.replace("</urlset>", f"  <url><loc>{BASE_URL}{page}</loc></url>\n</urlset>", 1)
    path.write_text(raw, encoding="utf-8")


def update_status(path: Path, data: dict[str, Any], docket: dict[str, Any]) -> None:
    payload = load_json(path) if path.exists() else {}
    site = path.parent
    payload["root_html_pages"] = len(list(site.glob("*.html")))
    payload["published_html_pages_including_resources"] = len(list(site.rglob("*.html")))
    payload["sovereign_machine_economy"] = {
        "release": data["release_id"],
        "version": data["version"],
        "pages": PAGES,
        "engines": len(data["source_releases"]),
        "constitutional_gates": len(data["gates"]),
        "handoffs": len(data["handoffs"]),
        "evidence_artifacts": len(data["artifact_classes"]),
        "counterfactual_universes": len(data["universes"]),
        "human_review_actions": len(data["review_actions"]),
        "sample_economy_root": docket["economy_root"],
        "terminal_state": "HUMAN_SETTLEMENT_REVIEW",
        "external_authority": "NONE_GRANTED",
        "external_actions": 0,
    }
    write_json(path, payload)


def reconcile_manifests(site: Path, data: dict[str, Any]) -> list[str]:
    reconciled: list[str] = []
    for filename, schema in COMPANION_MANIFESTS:
        path = site / filename
        payload = load_json(path)
        if payload.get("schema") != schema:
            raise RuntimeError(f"unrecognized companion manifest schema: {filename}")
        files = payload.get("files")
        if not isinstance(files, dict):
            raise RuntimeError(f"companion manifest files map missing: {filename}")
        for relative in SHARED:
            target = site / relative
            if not target.is_file():
                raise RuntimeError(f"shared integration output missing: {target}")
            files[relative] = {"sha256": sha_file(target), "bytes": target.stat().st_size}
        for companion, _ in COMPANION_MANIFESTS:
            target = site / companion
            if companion in files and target.is_file():
                files[companion] = {"sha256": sha_file(target), "bytes": target.stat().st_size}
        integration = payload.setdefault("integration", {})
        history = integration.setdefault("reconciliations", [])
        if not isinstance(history, list):
            raise RuntimeError(f"invalid reconciliation history: {filename}")
        history[:] = [item for item in history if not isinstance(item, dict) or item.get("release_id") != data["release_id"]]
        history.append({"release_id": data["release_id"], "version": data["version"], "built_at": data["built_at"], "reason": "shared GoalOS website surfaces extended by the Sovereign Machine Economy", "files": SHARED})
        write_json(path, payload)
        reconciled.append(filename)
    return reconciled


def snapshot_site(site: Path) -> dict[str, str]:
    return {path.relative_to(site).as_posix(): sha_file(path) for path in site.rglob("*") if path.is_file()}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--content", type=Path, default=root / "content" / "sovereign-machine-economy.json")
    parser.add_argument("--mainnet", type=Path, default=root / "data" / "mainnet" / "v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()
    root = args.root.resolve(); site = args.site.resolve(); content_path = args.content.resolve(); mainnet_path = args.mainnet.resolve()
    if not site.is_dir():
        raise RuntimeError(f"missing built site: {site}")
    content = load_json(content_path); validate_content(content)
    meta = load_json(root / "content" / "meta-agentic-alpha-agi.json")
    node = load_json(root / "content" / "agi-alpha-node-v0.json")
    jobs = load_json(root / "content" / "agi-jobs-v0-v2.json")
    mainnet = load_json(mainnet_path)
    validate_dependencies(site, meta, node, jobs)
    built_at = iso_seconds(utc_now())
    fingerprints, lineage_root = lineage(root, site)
    data = compile_data(content, meta, node, jobs, mainnet, fingerprints, lineage_root, built_at)
    docket = sample_docket(data); data["sample_docket"] = docket
    before = snapshot_site(site)

    feature = root / "website" / "features" / FEATURE_ID
    assets = feature / "assets"; templates = feature / "templates"
    asset_out = site / "assets"; asset_out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(assets / "sovereign-machine-economy.css", asset_out / "sovereign-machine-economy.css")
    shutil.copy2(assets / "sovereign-machine-economy.js", asset_out / "sovereign-machine-economy.js")
    page_map = {
        "sovereign-machine-economy.html": "experience",
        "sovereign-machine-economy-observatory.html": "observatory",
        "sovereign-machine-economy-architecture.html": "architecture",
        "sovereign-machine-economy-ledger.html": "ledger",
        "sovereign-machine-economy-memory.html": "memory",
        "sovereign-machine-economy-passport.html": "passport",
    }
    for page, key in page_map.items():
        (site / page).write_text(render_template(templates / page, key, data), encoding="utf-8")
    write_json(site / "data" / "sovereign-machine-economy.json", data)
    downloads = site / "downloads" / FEATURE_ID; downloads.mkdir(parents=True, exist_ok=True)
    write_json(downloads / "sample-sovereign-machine-economy-docket.json", docket)
    (downloads / "sovereign-machine-economy-executive-brief.md").write_text(executive_brief(docket), encoding="utf-8")

    inject_homepage(site / "index.html")
    update_routes(site / "routes.json", data)
    update_sitemap(site / "sitemap.xml")
    update_status(site / "site-status.json", data, docket)
    reconciled = reconcile_manifests(site, data)

    manifest_files = [
        *PAGES,
        "assets/sovereign-machine-economy.css",
        "assets/sovereign-machine-economy.js",
        "data/sovereign-machine-economy.json",
        "downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json",
        "downloads/sovereign-machine-economy/sovereign-machine-economy-executive-brief.md",
        *SHARED,
        *[name for name, _ in COMPANION_MANIFESTS],
    ]
    manifest = {
        "schema": "goalos.sovereign_machine_economy.website_manifest.v2",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "version": data["version"],
        "built_at": built_at,
        "dependencies": {key: {k: value for k, value in release.items() if k in {"release_id", "title", "version", "status"}} for key, release in data["dependencies"].items()},
        "lineage_root": lineage_root,
        "sample_economy_root": docket["economy_root"],
        "files": {},
        "integration": {"strategy": "additive-post-agi-jobs-constitutional-civilization-engine", "shared_outputs": SHARED, "companion_manifests_reconciled": reconciled},
        "authority": docket["authority"],
    }
    for relative in manifest_files:
        path = site / relative
        manifest["files"][relative] = {"sha256": sha_file(path), "bytes": path.stat().st_size}
    write_json(site / "sovereign-machine-economy-manifest.json", manifest)

    after = snapshot_site(site)
    removed = sorted(set(before) - set(after))
    allowed_changed = set(SHARED) | {name for name, _ in COMPANION_MANIFESTS}
    unexpected_changed = sorted(name for name in set(before) & set(after) if before[name] != after[name] and name not in allowed_changed)
    report = {
        "schema": "goalos.sovereign_machine_economy.build_report.v2",
        "status": "PASS" if not removed and not unexpected_changed else "FAIL",
        "release_title": RELEASE_TITLE,
        "version": data["version"],
        "built_at": built_at,
        "pages": PAGES,
        "engines": 3,
        "gates": len(data["gates"]),
        "handoffs": len(data["handoffs"]),
        "artifacts": len(data["artifact_classes"]),
        "counterfactual_universes": len(data["universes"]),
        "review_actions": len(data["review_actions"]),
        "sample_economy_root": docket["economy_root"],
        "lineage_root": lineage_root,
        "files_removed": removed,
        "unexpected_existing_file_changes": unexpected_changed,
        "declared_mutable_integration_surfaces": sorted(allowed_changed),
        "declared_feature_outputs": sorted([
            *PAGES,
            "sovereign-machine-economy-manifest.json",
            "assets/sovereign-machine-economy.css",
            "assets/sovereign-machine-economy.js",
            "data/sovereign-machine-economy.json",
            "downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json",
            "downloads/sovereign-machine-economy/sovereign-machine-economy-executive-brief.md",
        ]),
    }
    write_json(site / "qa" / "sovereign-machine-economy-build.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
