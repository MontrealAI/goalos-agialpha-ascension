#!/usr/bin/env python3
"""Build GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) additively."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"
FEATURE_ID = "agi-jobs-v0-v2"
FEATURE_PAGES = [
    "agi-jobs-v0-v2.html",
    "agi-jobs-v0-v2-market.html",
    "agi-jobs-v0-v2-proof.html",
    "agi-jobs-v0-v2-settlement.html",
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
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
SCORE_DIMENSIONS = ["capability", "evidence", "reliability", "efficiency", "latency", "safety", "originality"]


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


def require_unique_ids(data: dict[str, Any], key: str, errors: list[str]) -> None:
    values = data.get(key)
    if not isinstance(values, list):
        return
    ids = [item.get("id") for item in values if isinstance(item, dict)]
    if len(ids) != len(values) or any(not isinstance(item, str) or not item for item in ids):
        errors.append(f"{key} entries must each have a non-empty id")
    elif len(ids) != len(set(ids)):
        errors.append(f"{key} ids must be unique")


def validate_release(data: dict[str, Any]) -> None:
    errors: list[str] = []
    expected_scalars = {
        "schema_version": "3.0.0",
        "release_id": "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002",
        "release_title": RELEASE_TITLE,
        "edition": "Sovereign Work Civilization",
        "version": "3.0.0-sovereign-work-civilization",
        "status": "interactive-proof-settled-machine-work-civilization-digital-twin",
        "tagline": "A market of minds. A parliament of proof. A treasury that cannot move without permission.",
    }
    for key, expected in expected_scalars.items():
        if data.get(key) != expected:
            errors.append(f"{key} must equal {expected!r}")

    required_arrays = {
        "hero_metrics": 5,
        "thesis": 7,
        "job_classes": 7,
        "presets": 8,
        "postures": 5,
        "risk_profiles": 4,
        "incidents": 7,
        "lifecycle": 16,
        "institutions": 12,
        "validators": 9,
        "guardians": 6,
        "modules": 16,
        "council_roles": 5,
        "work_packages": 8,
        "job_archetypes": 16,
        "artifacts": 24,
        "architecture_translation": 16,
        "governance_principles": 10,
        "threats": 10,
        "claim_boundary": 10,
        "lineage_fingerprints": 32,
    }
    for key, exact in required_arrays.items():
        value = data.get(key)
        if not isinstance(value, list) or len(value) != exact:
            actual = len(value) if isinstance(value, list) else type(value).__name__
            errors.append(f"{key} must contain exactly {exact} entries; observed {actual}")
    for key in [
        "job_classes", "presets", "postures", "risk_profiles", "incidents", "lifecycle", "institutions",
        "validators", "guardians", "modules", "council_roles", "work_packages", "job_archetypes", "artifacts",
    ]:
        require_unique_ids(data, key, errors)

    expected_states = [
        "WORK_CONSTITUTION_SEALED",
        "PARTICIPANT_IDENTITIES_ADMITTED",
        "RIGHTS_AND_DATA_BOUNDARY_DECLARED",
        "ECONOMIC_ENVELOPE_RESERVED",
        "GUILD_BIDS_COMMITTED",
        "PARETO_MARKET_CLEARED",
        "EXECUTION_COUNCIL_CONSTITUTED",
        "PROOF_PRODUCING_WORK_GRAPH_COMPILED",
        "BOUNDED_EXECUTION_RECORDED",
        "SOURCE_AND_CLAIM_GRAPH_SEALED",
        "VALIDATOR_COMMITMENTS_SEALED",
        "VALIDATOR_PARLIAMENT_REVEALED",
        "DISPUTE_WINDOW_ADJUDICATED",
        "REVOCABLE_MEMORY_CANDIDATES_COMPILED",
        "SETTLEMENT_CONSTITUTION_COMPILED",
        "HUMAN_SETTLEMENT_REVIEW",
    ]
    observed_states = [item.get("state") for item in data.get("lifecycle", []) if isinstance(item, dict)]
    if observed_states != expected_states:
        errors.append("lifecycle must preserve the approved sixteen-state constitutional order")

    for posture in data.get("postures", []):
        weights = posture.get("weights") if isinstance(posture, dict) else None
        if not isinstance(weights, dict) or list(weights) != SCORE_DIMENSIONS:
            errors.append(f"posture {posture.get('id', '?')} must define the seven declared weights in canonical order")
        elif abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
            errors.append(f"posture {posture.get('id', '?')} weights must sum to 1")

    risk_profiles = data.get("risk_profiles", [])
    observed_seats = [item.get("validator_seats") for item in risk_profiles if isinstance(item, dict)]
    observed_thresholds = [item.get("validator_threshold") for item in risk_profiles if isinstance(item, dict)]
    if observed_seats != [3, 5, 7, 9]:
        errors.append("risk profile validator seats must be 3, 5, 7, 9")
    if observed_thresholds != [2, 4, 5, 7]:
        errors.append("risk profile validator thresholds must be 2, 4, 5, 7")

    settlement = data.get("settlement_policy")
    allocations = settlement.get("allocations", []) if isinstance(settlement, dict) else []
    if len(allocations) != 6:
        errors.append("settlement_policy.allocations must contain exactly six entries")
    if sum(int(item.get("pct", 0)) for item in allocations if isinstance(item, dict)) != 100:
        errors.append("settlement allocations must total 100%")
    if isinstance(settlement, dict):
        if settlement.get("live_token_movement") is not False or settlement.get("wallet_connection") is not False:
            errors.append("settlement policy must prohibit live token movement and wallet connection")
        if settlement.get("settlement_authority") != "NONE_GRANTED":
            errors.append("settlement authority must remain NONE_GRANTED")

    expected_security = {
        "external_dependencies": False,
        "api_keys": False,
        "wallet_connection": False,
        "network_reads": False,
        "network_writes": False,
        "local_storage": False,
        "live_ens_resolution": False,
        "live_compute": False,
        "live_token_movement": False,
        "credential_issuance": False,
        "human_review_required": True,
        "settlement_mode": "demonstration-only",
        "external_authority": "none",
        "content_security_policy": "default-src self; connect-src none; object-src none; base-uri none",
    }
    security = data.get("security")
    if not isinstance(security, dict):
        errors.append("security must be an object")
    else:
        for key, expected in expected_security.items():
            if security.get(key) != expected:
                errors.append(f"security.{key} must equal {expected!r}")

    origin = data.get("origin")
    expected_origin = {
        "repository": "https://github.com/MontrealAI/AGIJobsv0",
        "snapshot_zip_sha256": "085905a710b3021db79b21263495a9025cdff9fd829d2c5c8dba881426e15239",
        "snapshot_tree_files": 4085,
        "snapshot_tree_root": "71663cf756cad1347f71a70e1f9cf6071101ab3f494def62e13d268a9066f6fd",
        "selected_lineage_root": "c5ef16a1f3b5dd096f243aa34d2e97d123c85b391e0389fcd2d2627f3025e8d4",
    }
    if not isinstance(origin, dict):
        errors.append("origin must be an object")
    else:
        for key, expected in expected_origin.items():
            if origin.get(key) != expected:
                errors.append(f"origin.{key} must equal {expected!r}")

    lineage = data.get("lineage_fingerprints", [])
    paths = [item.get("path") for item in lineage if isinstance(item, dict)]
    if len(paths) != len(set(paths)):
        errors.append("lineage_fingerprints paths must be unique")
    for item in lineage:
        if not isinstance(item, dict):
            errors.append("lineage_fingerprints entries must be objects")
            break
        if not isinstance(item.get("sha256"), str) or len(item["sha256"]) != 64:
            errors.append(f"invalid lineage SHA-256 for {item.get('path', '?')}")
        if not isinstance(item.get("bytes"), int) or item["bytes"] <= 0:
            errors.append(f"invalid lineage byte count for {item.get('path', '?')}")

    terminal_states = {item.get("terminal") for item in data.get("incidents", []) if isinstance(item, dict)}
    if terminal_states != {"HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "DISPUTE_OPEN", "SAFE_HOLD"}:
        errors.append("incidents must cover all four approved terminal states")

    if errors:
        raise ValueError("Invalid AGI Jobs v0 (v2) release data:\n- " + "\n- ".join(errors))


def derive_mainnet_record(root: Path) -> dict[str, Any]:
    state_path = root / "qa" / "mainnet-release-state.json"
    registry_path = root / "config" / "ethereum-mainnet.contracts.json"
    record_path = root / "data" / "mainnet" / "v4.4.0-mainnet-2026-06-21.json"
    if not state_path.is_file() or not registry_path.is_file() or not record_path.is_file():
        return {
            "network": "Ethereum Mainnet",
            "chain_id": 1,
            "contracts": "repository record unavailable in this snapshot",
            "verification": "not asserted",
            "phase_b_grants": "UNKNOWN",
            "production_activation": "NOT_ACTIVATED",
            "user_fund_authorization": "NO",
            "external_audit_claim": "NONE",
            "claim_boundary": "The feature does not upgrade absent repository evidence.",
        }
    release_state = load_json(state_path)
    registry = load_json(registry_path)
    record = load_json(record_path)
    metadata = registry.get("metadata", {})
    summary = release_state.get("summary", {})
    activation = release_state.get("activation", {})
    verification = record.get("verification", {})
    return {
        "network": "Ethereum Mainnet",
        "chain_id": int(record.get("chainId", 1)),
        "contracts": int(record.get("goalosCreatedContractCount", 0)),
        "verification": f"{verification.get('verified', 0)}/{verification.get('goalosContracts', 0)}",
        "verification_failures": int(verification.get("failed", 0)),
        "phase_b_grants": summary.get("PHASE_B_GRANTS", f"{record.get('phaseBGrantCount', 0)}/{record.get('phaseBGrantCount', 0)}"),
        "production_activation": "NOT_ACTIVATED" if activation.get("productionActivated") is False else str(activation.get("status", "UNKNOWN")),
        "user_fund_authorization": summary.get("USER_FUNDS_AUTHORIZED", metadata.get("userFundAuthorization", "NO")),
        "external_audit_claim": "NONE" if record.get("notExternallyAudited") is True else "NOT_ASSERTED",
        "claim_boundary": metadata.get("claimBoundary", "Repository-derived infrastructure evidence with explicit qualifiers."),
    }


def risk_allows(limit: str, risk: str) -> bool:
    return RISK_ORDER.get(limit, 0) >= RISK_ORDER.get(risk, 0)


def class_fit(institution: dict[str, Any], job_class: dict[str, Any]) -> float:
    wanted = set(job_class.get("skills", []))
    overlap = len(set(institution.get("capabilities", [])) & wanted)
    return overlap / max(1, len(wanted))


def institution_score(institution: dict[str, Any], posture: dict[str, Any], job_class: dict[str, Any]) -> float:
    weighted = sum(float(institution.get(key, 0)) * float(weight) for key, weight in posture["weights"].items())
    fit = class_fit(institution, job_class)
    reputation = float(institution.get("reputation", 0))
    capacity = float(institution.get("capacity", 0)) / 100
    return min(1.0, max(0.0, weighted * 0.86 + fit * 0.07 + reputation * 0.045 + capacity * 0.025))


def is_dominated(candidate: dict[str, Any], all_rows: list[dict[str, Any]]) -> bool:
    return any(
        other["id"] != candidate["id"]
        and all(float(other[dimension]) >= float(candidate[dimension]) for dimension in SCORE_DIMENSIONS)
        and any(float(other[dimension]) > float(candidate[dimension]) for dimension in SCORE_DIMENSIONS)
        for other in all_rows
    )


def market_snapshot(data: dict[str, Any], job_class_id: str, posture_id: str, risk_id: str) -> dict[str, Any]:
    job_class = next(item for item in data["job_classes"] if item["id"] == job_class_id)
    posture = next(item for item in data["postures"] if item["id"] == posture_id)
    risk = next(item for item in data["risk_profiles"] if item["id"] == risk_id)
    rows: list[dict[str, Any]] = []
    for item in data["institutions"]:
        row = deepcopy(item)
        row["score"] = institution_score(item, posture, job_class)
        row["admitted"] = risk_allows(str(item["risk_limit"]), risk_id)
        row["fit"] = class_fit(item, job_class)
        row["evidence_axis"] = (float(item["evidence"]) + float(item["safety"]) + float(item["reliability"])) / 3
        row["utility_axis"] = (float(item["capability"]) + float(item["efficiency"]) + float(item["latency"]) + float(item["originality"])) / 4
        rows.append(row)
    active = [item for item in rows if item["admitted"]]
    frontier = [item for item in active if not is_dominated(item, active)]
    rows.sort(key=lambda item: (not item["admitted"], -float(item["score"]), str(item["name"])))
    leader = next(item for item in rows if item["admitted"])
    return {"job_class": job_class, "posture": posture, "risk": risk, "rows": rows, "active": active, "frontier": frontier, "leader": leader}


def choose_distinct(candidates: list[dict[str, Any]], used: set[str], metric: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    pool = [item for item in candidates if item["id"] not in used]
    pool.sort(key=lambda item: (-metric(item), -float(item["score"]), str(item["name"])))
    chosen = pool[0] if pool else next(item for item in candidates if item["id"] not in used)
    used.add(chosen["id"])
    return chosen


def constitute_council(snapshot: dict[str, Any]) -> dict[str, Any]:
    candidates = [item for item in snapshot["rows"] if item["admitted"]]
    used: set[str] = set()
    prime = candidates[0]
    used.add(prime["id"])
    evidence = choose_distinct(candidates, used, lambda item: float(item["evidence"]) + float(item["reliability"]) + float(item["fit"]))
    assurance = choose_distinct(candidates, used, lambda item: float(item["safety"]) + float(item["evidence"]) + float(item["reputation"]))
    delivery = choose_distinct(candidates, used, lambda item: float(item["efficiency"]) + float(item["latency"]) + float(item["capacity"]) / 100)
    shadow = choose_distinct(candidates, used, lambda item: float(item["originality"]) + float(item["evidence"]) + float(item["safety"]))
    reserves = [item for item in candidates if item["id"] not in used][:2]
    council_hash = sha256_bytes("|".join(item["id"] for item in [prime, evidence, assurance, delivery, shadow]).encode("utf-8"))
    return {
        "prime": prime,
        "evidence": evidence,
        "assurance": assurance,
        "delivery": delivery,
        "shadow": shadow,
        "reserves": reserves,
        "id": f"COUNCIL-{council_hash[:12].upper()}",
    }


def work_graph(data: dict[str, Any], council: dict[str, Any]) -> list[dict[str, Any]]:
    owners = [council["prime"], council["evidence"], council["prime"], council["delivery"], council["assurance"], council["shadow"], council["delivery"], council["evidence"]]
    roles = ["prime", "evidence", "prime", "delivery", "assurance", "shadow", "delivery", "evidence"]
    return [{**item, "owner": owners[index]["name"], "role": roles[index], "status": "COMPLETE"} for index, item in enumerate(data["work_packages"])]


def round_half_up(value: float) -> int:
    return int(value + 0.5)


def validator_judgments(data: dict[str, Any], commission: dict[str, Any], council: dict[str, Any], snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    seats = int(commission["risk"]["validator_seats"])
    selected = data["validators"][:seats]
    quality = round_half_up((float(council["prime"]["score"]) * 0.55 + float(council["evidence"]["evidence"]) * 0.15 + float(council["assurance"]["safety"]) * 0.15 + float(snapshot["leader"]["reliability"]) * 0.15) * 100)
    judgments: list[dict[str, Any]] = []
    for index, validator in enumerate(selected):
        verdict = "DISSENT" if index == len(selected) - 1 else "PASS"
        score = max(55, min(99, quality - (index % 4) * 2 + (3 if index == 0 else 0)))
        rationale = f"{validator['focus']}; evidence package is sufficient for human review with stated boundaries."
        if verdict == "DISSENT":
            score = max(62, quality - 11)
            rationale = "Minority view: narrow external claims, preserve unresolved assumptions, and require independent replication before reliance."
        effect = commission["incident"]["effect"]
        if effect == "validation" and index < (seats + 2) // 3:
            verdict = "REJECT" if index == 0 else "ABSTAIN"
            score = 34 + index * 4
            rationale = "Correlated reveal pattern and conflict signal require a capture investigation."
        if effect in {"identity", "evidence", "goal"} and index < 2:
            verdict = "REJECT"
            score = 28 + index * 5
            rationale = f"Material {effect} breach invalidates continuation."
        if effect == "rights" and (index == 0 or index == seats - 1):
            verdict = "DISSENT"
            score = 52
            rationale = "Source-rights conflict requires dispute and clearance before reuse or settlement readiness."
        if effect == "budget" and index == seats - 1:
            verdict = "DISSENT"
            score = 58
            rationale = "Resource envelope exceeded; require human repricing and scope reduction."
        salt = sha256_bytes(f"{commission['mission']}|{validator['id']}|{score}|{verdict}".encode("utf-8"))[:16]
        commitment = sha256_bytes(stable_json({"validator": validator["id"], "verdict": verdict, "score": score, "salt": salt}).encode("utf-8"))
        judgments.append({**validator, "verdict": verdict, "score": score, "rationale": rationale, "salt": salt, "commitment": commitment, "conflict": "NONE_DECLARED"})
    return judgments


def guardian_status(data: dict[str, Any], commission: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = {"identity": "H01", "evidence": "H02", "rights": "H03", "budget": "H04", "validation": "H05", "goal": "H06"}
    return [{**guardian, "status": "VETO" if mapping.get(commission["incident"]["effect"]) == guardian["id"] else "CLEAR"} for guardian in data["guardians"]]


def artifact_payload(artifact: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    commission = context["commission"]
    council = context["council"]
    snapshot = context["snapshot"]
    validators = context["validators"]
    base = {
        "artifact_id": artifact["id"],
        "name": artifact["name"],
        "plane": artifact["plane"],
        "purpose": artifact["purpose"],
        "run_id": context["run_id"],
        "release_id": context["data"]["release_id"],
    }
    council_record: dict[str, Any] = {}
    for role, value in council.items():
        if isinstance(value, dict) and value.get("id"):
            council_record[role] = {"id": value["id"], "name": value["name"], "identity": value["identity"]}
    summaries = {
        "intent": {"mission": commission["mission"], "risk": commission["risk"]["id"], "posture": commission["posture"]["id"]},
        "identity": {"council": council_record},
        "rights": {"mode": "synthetic-demonstration-only", "external_sources": 0, "live_data": 0},
        "economics": {"reward_units": commission["reward"], "live_token_movement": 0, "authority": "NONE_GRANTED"},
        "market": {"leader": snapshot["leader"]["id"], "frontier": [item["id"] for item in snapshot["frontier"]], "admitted": [item["id"] for item in snapshot["active"]]},
        "selection": {"council_id": council["id"], "prime": council["prime"]["id"], "shadow": council["shadow"]["id"]},
        "planning": {"packages": [{"id": item["id"], "owner": item["owner"], "proof": item["proof"]} for item in context["graph"]]},
        "execution": {"mode": "deterministic-browser-local", "external_actions": 0, "network_requests": 0},
        "proof": {"artifact_count": len(context["data"]["artifacts"]), "claim_boundary": context["data"]["claim_boundary"][:3]},
        "evaluation": {"evidence_floor": commission["risk"]["evidence_floor"], "leader_score": round(float(snapshot["leader"]["score"]), 4)},
        "validation": {"judgments": [{"id": item["id"], "verdict": item["verdict"], "score": item["score"], "commitment": item["commitment"]} for item in validators], "threshold": commission["risk"]["validator_threshold"]},
        "challenge": {"incident": commission["incident"]["id"], "terminal": context["terminal"]},
        "memory": {"status": "CANDIDATE_ONLY", "expiry": "90_DAYS_AFTER_HUMAN_REVIEW", "revocable": True},
        "credential": {"status": "HUMAN_APPROVAL_PENDING", "transferable": False},
        "settlement": {"policy": context["data"]["settlement_policy"], "live_movement": 0},
        "human-review": {"terminal": context["terminal"], "authority": "NONE_GRANTED", "external_actions": 0},
    }
    return {**base, "record": summaries.get(artifact["plane"], {"terminal": context["terminal"], "incident": commission["incident"]["id"]})}


def build_sample_docket(data: dict[str, Any]) -> dict[str, Any]:
    preset = data["presets"][0]
    job_class = next(item for item in data["job_classes"] if item["id"] == preset["job_class"])
    posture = next(item for item in data["postures"] if item["id"] == preset["posture"])
    risk = next(item for item in data["risk_profiles"] if item["id"] == preset["risk"])
    incident = next(item for item in data["incidents"] if item["id"] == "none")
    commission = {
        "preset": preset,
        "mission": preset["mission"],
        "job_class": job_class,
        "posture": posture,
        "risk": risk,
        "reward": preset["reward_units"],
        "incident": incident,
    }
    snapshot = market_snapshot(data, job_class["id"], posture["id"], risk["id"])
    council = constitute_council(snapshot)
    graph = work_graph(data, council)
    validators = validator_judgments(data, commission, council, snapshot)
    guardians = guardian_status(data, commission)
    run_seed = stable_json({
        "mission": commission["mission"],
        "posture": posture["id"],
        "risk": risk["id"],
        "reward": commission["reward"],
        "incident": incident["id"],
        "release": data["release_id"],
    })
    run_id = f"AJ-{sha256_bytes(run_seed.encode('utf-8'))[:16].upper()}"
    terminal = incident["terminal"]
    context = {
        "data": data,
        "commission": commission,
        "snapshot": snapshot,
        "council": council,
        "graph": graph,
        "validators": validators,
        "guardians": guardians,
        "run_id": run_id,
        "terminal": terminal,
    }
    previous = "0" * 64
    artifacts: list[dict[str, Any]] = []
    for artifact in data["artifacts"]:
        payload = artifact_payload(artifact, context)
        commitment = sha256_bytes(stable_json({"previous": previous, "payload": payload}).encode("utf-8"))
        artifacts.append({**artifact, "previous_commitment": previous, "commitment": commitment, "payload": payload})
        previous = commitment
    pass_count = len([item for item in validators if item["verdict"] == "PASS"])
    reject_count = len([item for item in validators if item["verdict"] == "REJECT"])
    dissent_count = len([item for item in validators if item["verdict"] == "DISSENT"])
    abstain_count = len([item for item in validators if item["verdict"] == "ABSTAIN"])
    allocation = [{**item, "units": round(float(commission["reward"]) * float(item["pct"]) / 100, 2)} for item in data["settlement_policy"]["allocations"]]
    docket: dict[str, Any] = {
        "schema": "goalos.agi_jobs_v0_v2.evidence_docket.v3",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "version": data["version"],
        "run_id": run_id,
        "work_constitution": {
            "mission": commission["mission"],
            "preset": preset["id"],
            "job_class": job_class["id"],
            "posture": posture["id"],
            "risk": risk["id"],
            "reward_units": commission["reward"],
            "deliverables": preset["deliverables"],
            "forbidden_runtime_actions": ["wallet connection", "token movement", "network request", "external action", "autonomous authorization"],
        },
        "market": {
            "leader": snapshot["leader"]["id"],
            "frontier": [item["id"] for item in snapshot["frontier"]],
            "ranking": [{"id": item["id"], "admitted": item["admitted"], "score": round(float(item["score"]), 5), "fit": round(float(item["fit"]), 3)} for item in snapshot["rows"]],
            "council": {
                "id": council["id"],
                "prime": council["prime"]["id"],
                "evidence": council["evidence"]["id"],
                "assurance": council["assurance"]["id"],
                "delivery": council["delivery"]["id"],
                "shadow": council["shadow"]["id"],
                "reserves": [item["id"] for item in council["reserves"]],
            },
        },
        "work_graph": graph,
        "parliament": {
            "seats": len(validators),
            "threshold": risk["validator_threshold"],
            "pass": pass_count,
            "reject": reject_count,
            "dissent": dissent_count,
            "abstain": abstain_count,
            "judgments": validators,
        },
        "guardians": guardians,
        "incident": incident,
        "evidence": {"artifact_count": len(artifacts), "chain_head": previous, "artifacts": artifacts},
        "settlement": {
            "mode": data["settlement_policy"]["mode"],
            "unit": data["settlement_policy"]["unit"],
            "allocation": allocation,
            "conditions_precedent": data["settlement_policy"]["conditions_precedent"],
            "live_token_movement": 0,
            "wallet_connections": 0,
            "settlement_authority": "NONE_GRANTED",
        },
        "memory": {
            "reputation_delta_candidate": {"prime": 3, "evidence_partner": 2, "assurance_partner": 2, "delivery_partner": 2, "shadow": 1, "validators": "scope-bounded"},
            "capability_passport_candidate": {
                "institution": council["prime"]["id"],
                "status": "HUMAN_APPROVAL_PENDING",
                "scope": job_class["label"],
                "skills": council["prime"]["capabilities"],
                "expiry": "90_DAYS_AFTER_HUMAN_REVIEW",
                "revocable": True,
                "transferable": False,
            },
        },
        "authority": {
            "terminal_state": terminal,
            "external_authority": "NONE_GRANTED",
            "production_activation": "NOT_ACTIVATED",
            "user_fund_authorization": "NO",
            "external_actions": 0,
            "network_requests": 0,
            "wallet_connections": 0,
            "live_token_movements": 0,
            "factual_correctness": "NOT_CERTIFIED",
        },
        "claim_boundary": data["claim_boundary"],
    }
    docket["run_commitment"] = sha256_bytes(stable_json(docket).encode("utf-8"))
    return docket


def render_template(template: str, data: dict[str, Any], built_at: datetime) -> str:
    embedded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    replacements = {
        "@@TITLE@@": str(data["release_title"]),
        "@@DESCRIPTION@@": str(data["description"]),
        "@@VERSION@@": str(data["version"]),
        "@@ORIGIN_URL@@": str(data["origin"]["repository"]),
        "@@BUILD_DATE@@": built_at.strftime("%B %d, %Y"),
        "@@LINEAGE_ROOT@@": str(data["origin"]["snapshot_tree_root"]),
        "@@SELECTED_LINEAGE_ROOT@@": str(data["origin"]["selected_lineage_root"]),
        "@@ZIP_SHA@@": str(data["origin"]["snapshot_zip_sha256"]),
        "@@SAMPLE_RUN_COMMITMENT@@": str(data["sample_docket"]["run_commitment"]),
        "@@DATA_JSON@@": embedded,
    }
    rendered = template
    for token, replacement in replacements.items():
        rendered = rendered.replace(token, replacement)
    if "@@" in rendered:
        unresolved = sorted(set(part.split("@@", 1)[0] for part in rendered.split("@@")[1::2]))
        raise ValueError(f"Unresolved template token remains: {unresolved}")
    return rendered


def replace_marked_block(text: str, start: str, end: str, block: str) -> str:
    if text.count(start) != text.count(end):
        raise ValueError(f"Unbalanced integration markers: {start} / {end}")
    if start not in text:
        return text
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return prefix + block + suffix


def insert_after_marker(text: str, marker: str, block: str) -> str | None:
    position = text.find(marker)
    if position < 0:
        return None
    position += len(marker)
    return text[:position] + "\n" + block + text[position:]


def patch_homepage(index_path: Path) -> None:
    text = index_path.read_text(encoding="utf-8")
    style = f'{STYLE_START}\n<link rel="stylesheet" href="assets/agi-jobs-v0-v2.css" data-goalos-agi-jobs-v0-v2>\n{STYLE_END}'
    nav = f'{NAV_START}<a href="agi-jobs-v0-v2.html">AGI Jobs</a>{NAV_END}'
    home = f'''{HOME_START}
<section class="aj-home-gateway" id="agi-jobs-v0-v2" data-goalos-feature="agi-jobs-v0-v2" aria-labelledby="aj-home-title">
  <div class="aj-home-inner">
    <div class="aj-home-copy">
      <small>GOALOS AGIALPHA ASCENSION · SOVEREIGN WORK CIVILIZATION</small>
      <h2 id="aj-home-title">THE WORK <span>CIVILIZATION</span></h2>
      <p><strong>A market of minds. A parliament of proof. A treasury that cannot move without permission.</strong> Commission bounded machine work, convene twelve rival guilds, clear a transparent Pareto market, preserve a nine-seat validator parliament, seal a twenty-four-artifact Evidence Docket, and stop at the human authority boundary.</p>
      <div class="aj-home-stats"><div class="aj-home-stat"><strong>12</strong><span>agent guilds</span></div><div class="aj-home-stat"><strong>16</strong><span>constitutional gates</span></div><div class="aj-home-stat"><strong>9</strong><span>validator seats</span></div><div class="aj-home-stat"><strong>24</strong><span>evidence artifacts</span></div></div>
      <div class="aj-home-actions"><a href="agi-jobs-v0-v2.html">Enter the Work Civilization →</a><a href="agi-jobs-v0-v2-market.html">Open the Guild Market</a><a href="agi-jobs-v0-v2-proof.html">Enter the Proof Parliament</a><a href="agi-jobs-v0-v2-settlement.html">Inspect Settlement</a><a href="agi-jobs-v0-v2-architecture.html">Read the Constitution</a></div>
    </div>
    <div class="aj-home-monument" aria-hidden="true"><div class="aj-home-core"><small>GOALOS</small><b>αJ</b><span>SOVEREIGN<br>WORK CIVILIZATION</span></div><span class="aj-home-node n1">MARKET</span><span class="aj-home-node n2">PROOF</span><span class="aj-home-node n3">MEMORY</span><span class="aj-home-node n4">DISPUTE</span><span class="aj-home-node n5">HUMAN</span></div>
  </div>
</section>
{HOME_END}'''

    text = replace_marked_block(text, STYLE_START, STYLE_END, style)
    if STYLE_START not in text:
        if "</head>" not in text:
            raise ValueError("Homepage is missing </head>")
        text = text.replace("</head>", style + "\n</head>", 1)

    text = replace_marked_block(text, NAV_START, NAV_END, nav)
    if NAV_START not in text:
        inserted = None
        for marker in ["<!-- GOALOS_AGI_ALPHA_NODE_V0_NAV_END -->", "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_NAV_END -->"]:
            inserted = insert_after_marker(text, marker, nav)
            if inserted is not None:
                break
        if inserted is None:
            if "</nav>" not in text:
                raise ValueError("Homepage is missing </nav>")
            inserted = text.replace("</nav>", nav + "\n</nav>", 1)
        text = inserted

    text = replace_marked_block(text, HOME_START, HOME_END, home)
    if HOME_START not in text:
        inserted = None
        for marker in ["<!-- GOALOS_FIRST_REAL_LOOP_END -->", "<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_END -->", "<!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END -->", "<!-- GOALOS_PROOF_MISSION_008_END -->"]:
            inserted = insert_after_marker(text, marker, home)
            if inserted is not None:
                break
        if inserted is None:
            if "</main>" not in text:
                raise ValueError("Homepage is missing </main>")
            inserted = text.replace("</main>", home + "\n</main>", 1)
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
        "edition": data["edition"],
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "integration": "additive-post-build",
        "runtime": "deterministic-browser-local-sovereign-work-civilization",
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
        text = text.replace("</urlset>", entries + "</urlset>", 1)
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
        "edition": data["edition"],
        "version": data["version"],
        "pages": FEATURE_PAGES,
        "public_surfaces": len(FEATURE_PAGES),
        "constitutional_gates": 16,
        "agent_guilds": 12,
        "validator_seats": 9,
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
    if not site.is_dir():
        raise FileNotFoundError(f"Site directory does not exist: {site}")
    if not (site / "index.html").is_file():
        raise FileNotFoundError(f"Site index does not exist: {site / 'index.html'}")

    data = load_json(content_path)
    validate_release(data)
    data["mainnet_record"] = derive_mainnet_record(root)
    data["lineage_root"] = data["origin"]["snapshot_tree_root"]
    data["selected_lineage_root"] = data["origin"]["selected_lineage_root"]
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

    sample_output = site / "downloads" / FEATURE_ID / "sample-agi-jobs-evidence-docket.json"
    write_json(sample_output, data["sample_docket"])
    outputs.append(sample_output)

    patch_homepage(site / "index.html")
    update_routes(site, data)
    update_sitemap(site)
    update_site_status(site, data, built_at)
    outputs.extend(site / relative for relative in SHARED_INTEGRATION_OUTPUTS)

    companion_outputs = reconcile_companion_manifests(site, data, built_at)
    outputs.extend(companion_outputs)

    manifest_files = {
        path.relative_to(site).as_posix(): {"sha256": sha256(path), "bytes": path.stat().st_size}
        for path in outputs
    }
    manifest = {
        "schema": "goalos.agi_jobs_v0_v2.website_manifest.v3",
        "release_id": data["release_id"],
        "release_title": data["release_title"],
        "edition": data["edition"],
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "experience": {
            "runtime": "deterministic-browser-local-sovereign-work-civilization",
            "constitutional_gates": 16,
            "agent_guilds": 12,
            "validator_seats": 9,
            "evidence_artifacts": 24,
            "public_surfaces": len(FEATURE_PAGES),
            "terminal_states": ["HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "DISPUTE_OPEN", "SAFE_HOLD"],
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
        "source_lineage": {
            "repository": data["origin"]["repository"],
            "snapshot_zip_sha256": data["origin"]["snapshot_zip_sha256"],
            "snapshot_tree_files": data["origin"]["snapshot_tree_files"],
            "snapshot_tree_root": data["origin"]["snapshot_tree_root"],
            "selected_lineage_root": data["origin"]["selected_lineage_root"],
            "fingerprints": len(data["lineage_fingerprints"]),
        },
        "sample_run_commitment": data["sample_docket"]["run_commitment"],
        "files": manifest_files,
    }
    manifest_path = site / "agi-jobs-v0-v2-manifest.json"
    write_json(manifest_path, manifest)

    report = {
        "status": "PASS",
        "schema": "goalos.agi_jobs_v0_v2.build_report.v3",
        "release_title": RELEASE_TITLE,
        "edition": data["edition"],
        "version": data["version"],
        "built_at": iso_seconds(built_at),
        "site": str(site),
        "pages": FEATURE_PAGES,
        "sample_run_commitment": data["sample_docket"]["run_commitment"],
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
