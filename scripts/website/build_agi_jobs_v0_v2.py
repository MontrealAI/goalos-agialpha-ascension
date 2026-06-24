#!/usr/bin/env python3
"""Build GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) additively."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"
FEATURE_ID = "agi-jobs-v0-v2"
FEATURE_PAGES = [
    "agi-jobs-v0-v2.html",
    "agi-jobs-v0-v2-market.html",
    "agi-jobs-v0-v2-settlement.html",
    "agi-jobs-v0-v2-memory.html",
    "agi-jobs-v0-v2-architecture.html",
]
SHARED_INTEGRATION_OUTPUTS = ["index.html", "routes.json", "sitemap.xml", "site-status.json"]
COMPANION_MANIFESTS = {
    "meta-agentic-alpha-agi-manifest.json": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
    "agi-alpha-node-v0-manifest.json": "goalos.agi_alpha_node_v0.website_manifest.v2",
}
STYLE_START = "<!-- GOALOS_AGI_JOBS_V0_V2_STYLE_START -->"
STYLE_END = "<!-- GOALOS_AGI_JOBS_V0_V2_STYLE_END -->"
NAV_START = "<!-- GOALOS_AGI_JOBS_V0_V2_NAV_START -->"
NAV_END = "<!-- GOALOS_AGI_JOBS_V0_V2_NAV_END -->"
HOME_START = "<!-- GOALOS_AGI_JOBS_V0_V2_HOME_START -->"
HOME_END = "<!-- GOALOS_AGI_JOBS_V0_V2_HOME_END -->"
SOURCE_LINEAGE_ROOT = "ef43db8a6632192f9347083bf42f2c1cdbb6eb662f634408fde5139ea516d2a0"


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
        "schema_version": "3.0.0",
        "release_id": "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002",
        "release_title": RELEASE_TITLE,
        "version": "3.0.0-sovereign-labor-civilization",
        "status": "interactive-constitutional-ai-labor-economy-digital-twin",
        "tagline": "Every mission becomes a market. Every market becomes proof. Every proof becomes accountable value.",
    }
    for key, expected in expected_scalars.items():
        if data.get(key) != expected:
            errors.append(f"{key} must equal {expected!r}")
    expected_counts = {
        "hero_metrics": 6,
        "thesis": 7,
        "job_classes": 7,
        "presets": 8,
        "postures": 5,
        "risk_profiles": 4,
        "incidents": 7,
        "lifecycle": 14,
        "institutions": 12,
        "validators": 7,
        "guardians": 5,
        "guardrails": 10,
        "modules": 14,
        "job_archetypes": 16,
        "artifacts": 24,
        "architecture_translation": 16,
        "governance_principles": 10,
        "threats": 10,
        "memory_rules": 8,
        "economic_invariants": 8,
        "claim_boundary": 9,
        "lineage_fingerprints": 32,
    }
    for key, expected in expected_counts.items():
        value = data.get(key)
        if not isinstance(value, list) or len(value) != expected:
            errors.append(f"{key} must contain exactly {expected} entries")
    expected_states = [
        "JOB_CHARTER_SEALED",
        "IDENTITY_ADMISSION_RECORDED",
        "OPPORTUNITY_THESIS_COMMITTED",
        "SETTLEMENT_ENVELOPE_RESERVED",
        "INSTITUTION_BIDS_COMMITTED",
        "INSTITUTION_BIDS_REVEALED",
        "EXECUTION_COALITION_SELECTED",
        "WORK_GRAPH_COMPILED",
        "BOUNDED_WORK_EXECUTED",
        "EVIDENCE_CHAIN_SEALED",
        "VALIDATOR_PARLIAMENT_REVEALED",
        "GUARDIAN_CHALLENGE_RESOLVED",
        "SETTLEMENT_PACKET_COMPILED",
        "HUMAN_SETTLEMENT_REVIEW",
    ]
    observed_states = [item.get("state") for item in data.get("lifecycle", []) if isinstance(item, dict)]
    if observed_states != expected_states:
        errors.append("lifecycle must preserve the approved fourteen-state order")
    weight_keys = {"capability", "evidence", "reliability", "efficiency", "latency", "safety", "energy"}
    for posture in data.get("postures", []):
        weights = posture.get("weights") if isinstance(posture, dict) else None
        if not isinstance(weights, dict) or set(weights) != weight_keys:
            errors.append(f"posture {posture.get('id', '?')} must define seven weights")
        elif abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
            errors.append(f"posture {posture.get('id', '?')} weights must sum to 1")
    allocations = data.get("settlement_policy", {}).get("allocations", [])
    if sum(int(item.get("pct", 0)) for item in allocations if isinstance(item, dict)) != 100:
        errors.append("settlement allocations must total 100%")
    required_security = {
        "external_dependencies": False,
        "api_keys": False,
        "wallet_connection": False,
        "network_reads": False,
        "network_writes": False,
        "local_storage": False,
        "live_ens_resolution": False,
        "live_compute": False,
        "live_token_movement": False,
        "human_review_required": True,
        "settlement_mode": "demonstration-only",
        "external_authority": "none",
        "content_security_policy": "connect-src none",
    }
    security = data.get("security")
    if not isinstance(security, dict):
        errors.append("security must be an object")
    else:
        for key, expected in required_security.items():
            if security.get(key) != expected:
                errors.append(f"security.{key} must equal {expected!r}")
    lineage_paths = [item.get("path") for item in data.get("lineage_fingerprints", []) if isinstance(item, dict)]
    if len(lineage_paths) != len(set(lineage_paths)):
        errors.append("lineage_fingerprints paths must be unique")
    if data.get("origin", {}).get("snapshot_lineage_root") != SOURCE_LINEAGE_ROOT:
        errors.append("original source lineage root mismatch")
    if errors:
        raise ValueError("Invalid AGI Jobs v0 (v2) release data:\n- " + "\n- ".join(errors))


def derive_mainnet_record(root: Path) -> dict[str, Any]:
    state_path = root / "qa" / "mainnet-release-state.json"
    registry_path = root / "config" / "ethereum-mainnet.contracts.json"
    if not state_path.is_file() or not registry_path.is_file():
        return {
            "network": "Ethereum Mainnet",
            "contracts": "repository record unavailable in this snapshot",
            "verification": "not asserted",
            "production_activation": "NOT_ACTIVATED",
            "user_fund_authorization": "NO",
            "claim_boundary": "Feature build proceeds without upgrading absent repository evidence.",
        }
    release_state = load_json(state_path)
    registry = load_json(registry_path)
    contracts = registry.get("contracts", [])
    goalos_contracts = [item for item in contracts if isinstance(item, dict) and item.get("deployedByGoalOS") is True]
    metadata = registry.get("metadata", {})
    summary = release_state.get("summary", {})
    activation = release_state.get("activation", {})
    return {
        "network": "Ethereum Mainnet",
        "contracts": len(goalos_contracts),
        "verification": metadata.get("operatorVerificationEvidence", "repository-derived"),
        "phase_b_grants": summary.get("PHASE_B_GRANTS", "UNKNOWN"),
        "production_activation": activation.get("status", summary.get("PRODUCTION_ACTIVATION_EFFECTIVE", "NOT_ACTIVATED")),
        "user_fund_authorization": summary.get("USER_FUNDS_AUTHORIZED", metadata.get("userFundAuthorization", "NO")),
        "claim_boundary": metadata.get("claimBoundary", "Repository-derived evidence with explicit qualifiers."),
    }


def weighted_score(institution: dict[str, Any], posture: dict[str, Any], job_class: dict[str, Any]) -> float:
    score = sum(float(institution[key]) * float(weight) for key, weight in posture["weights"].items())
    overlap = len(set(institution.get("capabilities", [])) & set(job_class.get("skills", [])))
    return min(1.0, score + min(0.05, overlap * 0.016) + float(institution.get("reputation", 0)) * 0.02)


def dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    dimensions = ("capability", "evidence", "reliability", "efficiency", "latency", "safety", "energy")
    return all(float(left[key]) >= float(right[key]) for key in dimensions) and any(float(left[key]) > float(right[key]) for key in dimensions)


def pareto_frontier(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in ranked if not any(other["id"] != item["id"] and dominates(other, item) for other in ranked)]


def build_sample_docket(data: dict[str, Any]) -> dict[str, Any]:
    preset = data["presets"][0]
    posture = next(item for item in data["postures"] if item["id"] == preset["posture"])
    risk = next(item for item in data["risk_profiles"] if item["id"] == preset["risk"])
    job_class = next(item for item in data["job_classes"] if item["id"] == preset["job_class"])
    ranked = sorted(
        ({**item, "score": weighted_score(item, posture, job_class)} for item in data["institutions"]),
        key=lambda item: (-item["score"], item["id"]),
    )
    frontier = pareto_frontier(ranked)
    prime = ranked[0]
    specialists = ranked[1:3]
    shadow = ranked[3]
    reserves = ranked[4:6]
    seed = sha256_bytes(stable_json({"release": data["release_id"], "preset": preset, "posture": posture["id"]}).encode("utf-8"))
    run_id = f"job-{seed[:16]}"
    allocations = [
        {**item, "units": round(preset["reward_units"] * item["pct"] / 100, 2)}
        for item in data["settlement_policy"]["allocations"]
    ]
    contribution_weights = [0.43, 0.19, 0.16, 0.12, 0.10]
    coalition_members = [prime, *specialists, shadow, reserves[0]]
    contributions = [
        {
            "institution_id": member["id"],
            "institution": member["name"],
            "role": ["prime", "evidence-specialist", "systems-specialist", "shadow-council", "reserve"][index],
            "contribution_weight": contribution_weights[index],
            "demonstration_units": round(preset["reward_units"] * 0.68 * contribution_weights[index], 2),
            "live_transfer": False,
        }
        for index, member in enumerate(coalition_members)
    ]
    votes = []
    for index, validator in enumerate(data["validators"]):
        vote = "DISSENT" if index == 5 else "PASS"
        votes.append({
            **validator,
            "vote": vote,
            "score": round(0.934 - index * 0.009 if vote == "PASS" else 0.704, 3),
            "rationale": "Residual uncertainty remains material and is preserved for independent human review." if vote == "DISSENT" else "The declared proof and authority boundaries satisfy this seat's review threshold.",
        })
    parliament = {
        "votes": votes,
        "pass": 6,
        "dissent": 1,
        "reject": 0,
        "threshold": risk["validator_threshold"],
        "quorum_met": True,
        "summary": "6 PASS · 1 DISSENT · 0 REJECT",
    }
    guardians = {
        "seats": [{**item, "disposition": "CLEAR", "rationale": "No constitutional veto condition was observed in the sample run."} for item in data["guardians"]],
        "clear": 5,
        "veto": 0,
        "threshold": risk["guardian_threshold"],
        "summary": "5 CLEAR · 0 VETO",
    }
    energy = {
        "declared_ceiling": risk["energy_ceiling"],
        "observed": round(max(0.41, risk["energy_ceiling"] - 0.12), 3),
        "useful_work_ratio": 0.91,
        "status": "PASS",
    }
    evaluation = {
        **{key: round(float(prime[key]), 3) for key in ("capability", "evidence", "reliability", "efficiency", "latency", "safety", "energy")},
        "weighted_score": round(prime["score"], 4),
        "evidence_floor": risk["evidence_floor"],
        "market_integrity": 0.96,
        "proof_density": 0.94,
        "settlement_readiness": 0.93,
    }
    coalition = {
        "prime": {"id": prime["id"], "name": prime["name"], "score": round(prime["score"], 4)},
        "specialists": [{"id": item["id"], "name": item["name"], "score": round(item["score"], 4)} for item in specialists],
        "shadow": {"id": shadow["id"], "name": shadow["name"], "score": round(shadow["score"], 4)},
        "reserves": [{"id": item["id"], "name": item["name"], "score": round(item["score"], 4)} for item in reserves],
        "quarantined": [],
        "pareto_frontier": [{"id": item["id"], "name": item["name"]} for item in frontier],
    }
    work_graph = [
        {"id": "W01", "name": "Charter interpretation", "owner": prime["id"], "depends_on": [], "proof": "intent-commitment"},
        {"id": "W02", "name": "Source and evidence map", "owner": specialists[0]["id"], "depends_on": ["W01"], "proof": "source-register"},
        {"id": "W03", "name": "Systems model", "owner": specialists[1]["id"], "depends_on": ["W01"], "proof": "model-artifact"},
        {"id": "W04", "name": "Counterfactual challenge", "owner": shadow["id"], "depends_on": ["W02", "W03"], "proof": "challenge-record"},
        {"id": "W05", "name": "Intervention synthesis", "owner": prime["id"], "depends_on": ["W02", "W03", "W04"], "proof": "claim-matrix"},
        {"id": "W06", "name": "Resource and energy audit", "owner": reserves[0]["id"], "depends_on": ["W05"], "proof": "energy-ledger"},
        {"id": "W07", "name": "Independent evaluation", "owner": "validator-parliament", "depends_on": ["W05", "W06"], "proof": "evaluator-report"},
        {"id": "W08", "name": "Human review packet", "owner": "human-authority", "depends_on": ["W07"], "proof": "executive-review-brief"},
    ]
    memory_candidate = {
        "id": f"memory-{seed[:12]}",
        "scope": preset["job_class"],
        "source_run": run_id,
        "status": "HUMAN_APPROVAL_PENDING",
        "expiry": "2026-09-22",
        "revocable": True,
        "promotion_authority": "HUMAN_ONLY",
        "external_actions": 0,
    }
    payloads: list[Any] = [
        {"mission": preset["mission"], "deliverables": preset["deliverables"], "risk": preset["risk"], "forbidden_actions": ["wallet", "token transfer", "RPC", "API", "production execution"]},
        {"institutions": [{"id": item["id"], "identity": item["identity"], "capabilities": item["capabilities"]} for item in data["institutions"]]},
        {"job_class": job_class, "opportunity": "Bounded public-interest systems mission", "counterfactual": "No coalition convened"},
        {"reward_units": preset["reward_units"], "allocations": allocations, "authority": "NONE_GRANTED"},
        {"commitments": [{"id": item["id"], "commitment": sha256_bytes(f"{seed}:{item['id']}:commit".encode())} for item in ranked]},
        {"reveals": [{"id": item["id"], "score": round(item["score"], 4)} for item in ranked], "frontier": [item["id"] for item in frontier]},
        coalition,
        {"shadow": coalition["shadow"], "challenge_rights": ["counterfactual", "evidence gap", "capture", "energy"]},
        {"nodes": work_graph, "stop_conditions": ["evidence floor missed", "identity drift", "quorum failure", "energy breach"]},
        {"mode": "deterministic-browser-local", "phases": [item["state"] for item in data["lifecycle"]], "external_actions": 0},
        energy,
        {"sources": 12, "identity_mode": "declared-synthetic", "network_reads": 0},
        {"claims": 10, "supported": 9, "unresolved": 1},
        {"contradictions": 2, "disposition": "preserved-for-review"},
        evaluation,
        {"commitments": [{"id": item["id"], "commitment": sha256_bytes(f"{seed}:{item['id']}:validator".encode())} for item in data["validators"]]},
        parliament,
        {"minority": [item for item in votes if item["vote"] == "DISSENT"], "condition": "No stronger external claim without independent replication."},
        {"signal": "CLEAR", "entropy_commitment": sha256_bytes(f"{seed}:entropy".encode()), "correlated_vote_risk": 0.12},
        guardians,
        {"incident": "none", "terminal": "HUMAN_SETTLEMENT_REVIEW", "remediation": "Human review remains mandatory."},
        {"allocations": allocations, "contributions": contributions, "live_token_movement": False, "settlement_authority": "NONE_GRANTED"},
        memory_candidate,
        {"run_id": run_id, "terminal": "HUMAN_SETTLEMENT_REVIEW", "coalition": coalition, "quorum": parliament["summary"], "guardian_disposition": guardians["summary"], "authority": "NONE_GRANTED"},
    ]
    previous = "0" * 64
    chain = []
    for index, (meta, payload) in enumerate(zip(data["artifacts"], payloads, strict=True), start=1):
        artifact_hash = sha256_bytes(stable_json(payload).encode("utf-8"))
        commitment = sha256_bytes(f"{previous}:{artifact_hash}:{meta['name']}".encode("utf-8"))
        chain.append({**meta, "index": index, "payload": payload, "previous_commitment": previous, "artifact_hash": artifact_hash, "commitment": commitment})
        previous = commitment
    return {
        "schema": "goalos.agi_jobs_v0_v2.evidence_docket.v3",
        "release": {"id": data["release_id"], "title": data["release_title"], "version": data["version"]},
        "generated_at": "2026-06-24T00:00:00Z",
        "run_id": run_id,
        "deterministic_seed": seed,
        "job_charter": {
            "mission": preset["mission"],
            "job_class": preset["job_class"],
            "posture": preset["posture"],
            "risk": preset["risk"],
            "reward_units": preset["reward_units"],
            "unit": data["settlement_policy"]["unit"],
            "forbidden_actions": ["live funds", "external execution", "factual certification", "autonomous settlement", "autonomous memory promotion"],
        },
        "market": {"coalition": coalition, "ranked": [{"id": item["id"], "name": item["name"], "score": round(item["score"], 4)} for item in ranked]},
        "work_graph": work_graph,
        "evaluation": evaluation,
        "energy": energy,
        "validator_parliament": parliament,
        "guardian_chamber": guardians,
        "incident": data["incidents"][0],
        "settlement": {
            "ready_for_human_review": True,
            "allocations": allocations,
            "contributions": contributions,
            "live_token_movement": False,
            "wallet_connections": 0,
            "authority": "NONE_GRANTED",
        },
        "memory_candidate": memory_candidate,
        "proof_chronicle": {"artifacts": chain, "chain_head": previous},
        "terminal": {
            "state": "HUMAN_SETTLEMENT_REVIEW",
            "external_actions": 0,
            "production": "NOT_ACTIVATED",
            "factual_correctness": "NOT_CERTIFIED",
            "funds_authorization": "NO",
            "memory_promotion": "HUMAN_APPROVAL_PENDING",
            "authority": "NONE_GRANTED",
        },
        "claim_boundary": data["claim_boundary"],
    }


def executive_brief(data: dict[str, Any], docket: dict[str, Any]) -> str:
    coalition = docket["market"]["coalition"]
    return f"""# GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) — Executive Review Brief

**Release:** `{data['release_id']}`  
**Version:** `{data['version']}`  
**Run:** `{docket['run_id']}`  
**Chain head:** `{docket['proof_chronicle']['chain_head']}`  
**Terminal state:** `{docket['terminal']['state']}`  
**Authority:** `{docket['terminal']['authority']}`

## Constitutional result

A bounded mission charter was transformed into a twelve-institution market, a prime coalition with specialist and shadow seats, an eight-node proof-producing work graph, a seven-seat validator parliament, a five-seat guardian chamber, a six-part demonstration settlement waterfall, and a reversible capability-memory candidate.

## Selected coalition

- Prime: **{coalition['prime']['name']}**
- Specialists: **{', '.join(item['name'] for item in coalition['specialists'])}**
- Shadow council: **{coalition['shadow']['name']}**
- Validator result: **{docket['validator_parliament']['summary']}**
- Guardian result: **{docket['guardian_chamber']['summary']}**
- Evidence artifacts: **{len(docket['proof_chronicle']['artifacts'])}**

## Non-authority boundary

No wallet was connected, no live value moved, no external action occurred, no factual correctness was certified, no production activation was granted, and no capability memory was promoted. Human settlement and memory review remain mandatory.
"""


def render_template(template: str, data: dict[str, Any], built_at: datetime) -> str:
    embedded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    replacements = {
        "@@TITLE@@": str(data["release_title"]),
        "@@DESCRIPTION@@": str(data["description"]),
        "@@VERSION@@": str(data["version"]),
        "@@ORIGIN_URL@@": str(data["origin"]["repository"]),
        "@@BUILD_DATE@@": built_at.strftime("%B %d, %Y"),
        "@@LINEAGE_ROOT@@": str(data["lineage_root"]),
        "@@DATA_JSON@@": embedded,
    }
    rendered = template
    for token, replacement in replacements.items():
        rendered = rendered.replace(token, replacement)
    if "@@" in rendered:
        raise ValueError("Unresolved template token remains")
    return rendered


def join_block(prefix: str, block: str, suffix: str, *, leading_newline: bool = False) -> str:
    before = "\n" if leading_newline else ""
    after = "" if block.endswith("\n") else "\n"
    return f"{prefix}{before}{block}{after}{suffix.lstrip(chr(10))}"


def replace_existing_block(text: str, start: str, end: str, block: str) -> str:
    if text.count(start) != text.count(end):
        raise ValueError(f"Unbalanced integration markers: {start} / {end}")
    if start not in text:
        return text
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return join_block(prefix, block, suffix)


def insert_after_marker(text: str, marker: str, block: str) -> str | None:
    position = text.find(marker)
    if position < 0:
        return None
    position += len(marker)
    return join_block(text[:position], block, text[position:], leading_newline=True)


def patch_homepage(index_path: Path) -> None:
    text = index_path.read_text(encoding="utf-8")
    style = f'{STYLE_START}\n<link rel="stylesheet" href="assets/agi-jobs-v0-v2.css">\n{STYLE_END}\n'
    nav = f'{NAV_START}<a href="agi-jobs-v0-v2.html">AGI Jobs</a>{NAV_END}'
    home = f'''{HOME_START}
<section class="aj-home-gateway" id="agi-jobs-v0-v2" data-goalos-feature="agi-jobs-v0-v2" aria-labelledby="aj-home-title">
  <div class="aj-home-inner">
    <div class="aj-home-copy">
      <small>GOALOS AGIALPHA ASCENSION · SOVEREIGN LABOR CIVILIZATION</small>
      <h2 id="aj-home-title">AGI JOBS <span>v0 (v2)</span></h2>
      <p><strong>Every mission becomes a market. Every market becomes proof. Every proof becomes accountable value.</strong> Convene twelve bounded institutions, construct a Pareto coalition, traverse fourteen constitutional gates, preserve seven-seat dissent and five guardian vetoes, seal twenty-four evidence artifacts, and stop before settlement or memory gains authority.</p>
      <div class="aj-home-stats"><div class="aj-home-stat"><strong>14</strong><span>constitutional gates</span></div><div class="aj-home-stat"><strong>12</strong><span>agent institutions</span></div><div class="aj-home-stat"><strong>24</strong><span>chained artifacts</span></div><div class="aj-home-stat"><strong>0</strong><span>live value moved</span></div></div>
      <div class="aj-home-actions"><a href="agi-jobs-v0-v2.html">Enter the Sovereign Labor Exchange →</a><a href="agi-jobs-v0-v2-market.html">Open the Market Atlas</a><a href="agi-jobs-v0-v2-settlement.html">Inspect Settlement</a><a href="agi-jobs-v0-v2-memory.html">Review Capability Memory</a><a href="agi-jobs-v0-v2-architecture.html">Read the Constitution</a></div>
    </div>
    <div class="aj-home-seal" aria-hidden="true"><span class="aj-home-orbit-label l1">MISSION</span><span class="aj-home-orbit-label l2">MARKET</span><span class="aj-home-orbit-label l3">PROOF</span><span class="aj-home-orbit-label l4">REVIEW</span><span class="aj-home-orbit-label l5">MEMORY</span><span class="aj-home-orbit-label l6">GUARDIANS</span><div class="aj-home-core"><b>αJ</b><span>SOVEREIGN<br>LABOR CIVILIZATION</span></div></div>
  </div>
</section>
{HOME_END}
'''
    text = replace_existing_block(text, STYLE_START, STYLE_END, style)
    if STYLE_START not in text:
        if "</head>" not in text:
            raise ValueError("Homepage is missing </head>")
        text = text.replace("</head>", f"{style}</head>", 1)
    text = replace_existing_block(text, NAV_START, NAV_END, nav)
    if NAV_START not in text:
        inserted = None
        for marker in ["<!-- GOALOS_FIRST_REAL_LOOP_NAV_END -->", "<!-- GOALOS_AGI_ALPHA_NODE_V0_NAV_END -->", "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_NAV_END -->"]:
            inserted = insert_after_marker(text, marker, nav)
            if inserted is not None:
                break
        if inserted is None:
            if "</nav>" not in text:
                raise ValueError("Homepage is missing </nav>")
            inserted = text.replace("</nav>", f"{nav}\n</nav>", 1)
        text = inserted
    text = replace_existing_block(text, HOME_START, HOME_END, home)
    if HOME_START not in text:
        inserted = None
        for marker in ["<!-- GOALOS_FIRST_REAL_LOOP_END -->", "<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_END -->", "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END -->", "<!-- GOALOS_PROOF_MISSION_008_END -->"]:
            inserted = insert_after_marker(text, marker, home)
            if inserted is not None:
                break
        if inserted is None:
            if "</main>" not in text:
                raise ValueError("Homepage is missing </main>")
            inserted = text.replace("</main>", f"{home}</main>", 1)
        text = inserted
    index_path.write_text(text, encoding="utf-8")


def update_routes(site: Path, data: dict[str, Any]) -> None:
    path = site / "routes.json"
    payload = load_json(path) if path.exists() else {"version": "unknown", "routes": []}
    routes = payload.get("routes", [])
    if not isinstance(routes, list):
        raise ValueError("routes.json routes must be an array")
    payload["routes"] = sorted(set(map(str, routes)).union(FEATURE_PAGES))
    payload["agi_jobs_v0_v2"] = {
        "release_id": data["release_id"],
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "integration": "additive-post-build",
        "runtime": "deterministic-browser-local-sovereign-labor-civilization",
        "external_actions": 0,
        "live_token_movement": False,
    }
    write_json(path, payload)


def update_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    text = path.read_text(encoding="utf-8") if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n</urlset>\n"
    entries = "".join(f"  <url><loc>./{page}</loc></url>\n" for page in FEATURE_PAGES if page not in text)
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
        for companion_name in COMPANION_MANIFESTS:
            target = site / companion_name
            if companion_name in files and target.is_file() and target != path:
                files[companion_name] = {"sha256": sha256(target), "bytes": target.stat().st_size}
        integration = payload.setdefault("integration", {})
        history = integration.setdefault("reconciliations", [])
        if not isinstance(history, list):
            raise ValueError(f"Companion manifest reconciliations must be an array: {path}")
        history[:] = [item for item in history if not isinstance(item, dict) or item.get("release_id") != data["release_id"]]
        history.append({
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
    payload["agi_jobs_v0_v2"] = {
        "status": data["status"],
        "release_title": RELEASE_TITLE,
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "lifecycle_gates": 14,
        "agent_institutions": 12,
        "validator_seats": 7,
        "guardian_seats": 5,
        "evidence_artifacts": 24,
        "evidence_docket_schema": "goalos.agi_jobs_v0_v2.evidence_docket.v3",
        "built_at": iso_seconds(built_at),
        "human_review_required": True,
        "external_actions": 0,
        "live_token_movement": False,
    }
    write_json(path, payload)


def build(site: Path, content_path: Path, source: Path, root: Path) -> dict[str, Any]:
    built_at = utc_now()
    if not site.is_dir() or not (site / "index.html").is_file():
        raise FileNotFoundError(f"Built GoalOS site is missing: {site}")
    data = load_json(content_path)
    validate_release(data)
    data["mainnet_record"] = derive_mainnet_record(root)
    data["lineage_root"] = data["origin"]["snapshot_lineage_root"]
    data["sample_docket"] = build_sample_docket(data)
    template_dir = source / "templates"
    asset_dir = source / "assets"
    page_templates = {page: template_dir / page for page in FEATURE_PAGES}
    required = [*page_templates.values(), asset_dir / "agi-jobs-v0-v2.css", asset_dir / "agi-jobs-v0-v2.js"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing AGI Jobs v0 (v2) sources:\n- " + "\n- ".join(missing))
    outputs: list[Path] = []
    for name, template in page_templates.items():
        output = site / name
        output.write_text(render_template(template.read_text(encoding="utf-8"), data, built_at), encoding="utf-8")
        outputs.append(output)
    (site / "assets").mkdir(parents=True, exist_ok=True)
    for filename in ["agi-jobs-v0-v2.css", "agi-jobs-v0-v2.js"]:
        output = site / "assets" / filename
        shutil.copy2(asset_dir / filename, output)
        outputs.append(output)
    data_output = site / "data" / "agi-jobs-v0-v2.json"
    write_json(data_output, data)
    outputs.append(data_output)
    download_dir = site / "downloads" / FEATURE_ID
    sample_output = download_dir / "sample-agi-jobs-evidence-docket.json"
    memory_output = download_dir / "agi-jobs-v0-v2-economic-memory.json"
    brief_output = download_dir / "agi-jobs-v0-v2-executive-review-brief.md"
    write_json(sample_output, data["sample_docket"])
    write_json(memory_output, {
        "schema": "goalos.agi_jobs_v0_v2.economic_memory.v1",
        "release_id": data["release_id"],
        "candidate": data["sample_docket"]["memory_candidate"],
        "rules": data["memory_rules"],
        "economic_invariants": data["economic_invariants"],
        "authority": "HUMAN_ONLY",
        "external_actions": 0,
    })
    brief_output.parent.mkdir(parents=True, exist_ok=True)
    brief_output.write_text(executive_brief(data, data["sample_docket"]), encoding="utf-8")
    outputs.extend([sample_output, memory_output, brief_output])
    patch_homepage(site / "index.html")
    update_routes(site, data)
    update_sitemap(site)
    update_site_status(site, data, built_at)
    outputs.extend(site / relative for relative in SHARED_INTEGRATION_OUTPUTS)
    companion_outputs = reconcile_companion_manifests(site, data, built_at)
    outputs.extend(companion_outputs)
    manifest_files = {path.relative_to(site).as_posix(): {"sha256": sha256(path), "bytes": path.stat().st_size} for path in outputs}
    manifest = {
        "schema": "goalos.agi_jobs_v0_v2.website_manifest.v3",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "experience": {
            "runtime": "deterministic-browser-local-sovereign-labor-civilization",
            "lifecycle_gates": 14,
            "agent_institutions": 12,
            "validator_seats": 7,
            "guardian_seats": 5,
            "evidence_artifacts": 24,
            "terminal_states": ["HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "SAFE_HOLD"],
            "external_actions": 0,
            "live_token_movement": False,
        },
        "integration": {
            "mode": "additive-post-build",
            "canonical_v86_source_modified": False,
            "homepage_markers": [STYLE_START, NAV_START, HOME_START],
            "existing_outputs_allowed_to_change": [*SHARED_INTEGRATION_OUTPUTS, *[path.name for path in companion_outputs]],
            "companion_manifests_reconciled": [path.name for path in companion_outputs],
        },
        "repository_evidence": data["mainnet_record"],
        "source_lineage_root": data["lineage_root"],
        "files": manifest_files,
    }
    manifest_path = site / "agi-jobs-v0-v2-manifest.json"
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
    write_json(site / "qa" / "agi-jobs-v0-v2-build.json", report)
    return report


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--content", type=Path, default=root / "content" / "agi-jobs-v0-v2.json")
    parser.add_argument("--source", type=Path, default=root / "website" / "features" / "agi-jobs-v0-v2")
    parser.add_argument("--root", type=Path, default=root)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build(args.site.resolve(), args.content.resolve(), args.source.resolve(), args.root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
