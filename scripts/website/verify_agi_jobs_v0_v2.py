#!/usr/bin/env python3
"""Verify GoalOS AGI Jobs v0 (v2), its evidence chain, and additive preservation boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"
PAGES = [
    "agi-jobs-v0-v2.html",
    "agi-jobs-v0-v2-market.html",
    "agi-jobs-v0-v2-proof.html",
    "agi-jobs-v0-v2-settlement.html",
    "agi-jobs-v0-v2-architecture.html",
]
NEW_OUTPUTS = {
    *PAGES,
    "agi-jobs-v0-v2-manifest.json",
    "assets/agi-jobs-v0-v2.css",
    "assets/agi-jobs-v0-v2.js",
    "data/agi-jobs-v0-v2.json",
    "downloads/agi-jobs-v0-v2/sample-agi-jobs-evidence-docket.json",
    "qa/agi-jobs-v0-v2-build.json",
}
SHARED_INTEGRATION_OUTPUTS = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
COMPANION_MANIFEST_SCHEMAS = {
    "meta-agentic-alpha-agi-manifest.json": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
    "agi-alpha-node-v0-manifest.json": "goalos.agi_alpha_node_v0.website_manifest.v2",
}
OPTIONAL_COMPANION_MANIFESTS = set(COMPANION_MANIFEST_SCHEMAS)
ALLOWED_CHANGED = SHARED_INTEGRATION_OUTPUTS | OPTIONAL_COMPANION_MANIFESTS | NEW_OUTPUTS
MARKERS = [
    "GOALOS_AGI_JOBS_V0_V2_STYLE_START",
    "GOALOS_AGI_JOBS_V0_V2_STYLE_END",
    "GOALOS_AGI_JOBS_V0_V2_NAV_START",
    "GOALOS_AGI_JOBS_V0_V2_NAV_END",
    "GOALOS_AGI_JOBS_V0_V2_HOME_START",
    "GOALOS_AGI_JOBS_V0_V2_HOME_END",
]
EXPECTED_COUNTS = {
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


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def file_inventory(site: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(site).as_posix(): {"sha256": digest(path), "bytes": path.stat().st_size}
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    }


def run(site: Path, root: Path, baseline: Path | None, schema: Path | None, output: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(label: str, condition: bool, detail: Any = "") -> None:
        checks.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("site-exists", site.is_dir(), str(site))
    required_relative = [
        *PAGES,
        "assets/agi-jobs-v0-v2.css",
        "assets/agi-jobs-v0-v2.js",
        "data/agi-jobs-v0-v2.json",
        "downloads/agi-jobs-v0-v2/sample-agi-jobs-evidence-docket.json",
        "agi-jobs-v0-v2-manifest.json",
        "qa/agi-jobs-v0-v2-build.json",
    ]
    required = [site / item for item in required_relative]
    for path in required:
        relative = path.relative_to(site).as_posix()
        check(f"required-file:{relative}", path.is_file() and path.stat().st_size > 0, path.stat().st_size if path.is_file() else 0)
    if not all(path.is_file() for path in required):
        report = {
            "schema": "goalos.agi_jobs_v0_v2.static_qa.v3",
            "release_title": RELEASE_TITLE,
            "status": "FAIL",
            "checks_total": len(checks),
            "checks_passed": len([item for item in checks if item["status"] == "PASS"]),
            "checks_failed": len([item for item in checks if item["status"] == "FAIL"]),
            "checks": checks,
            "preservation": {"baseline_supplied": bool(baseline)},
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    data = load(site / "data" / "agi-jobs-v0-v2.json")
    docket = load(site / "downloads" / "agi-jobs-v0-v2" / "sample-agi-jobs-evidence-docket.json")
    manifest = load(site / "agi-jobs-v0-v2-manifest.json")
    build_report = load(site / "qa" / "agi-jobs-v0-v2-build.json")

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
        check(f"release:{key}", data.get(key) == expected, data.get(key))
    for key, expected in EXPECTED_COUNTS.items():
        value = data.get(key)
        check(f"count:{key}", isinstance(value, list) and len(value) == expected, len(value) if isinstance(value, list) else type(value).__name__)

    origin = data.get("origin", {})
    expected_origin = {
        "snapshot_zip_sha256": "085905a710b3021db79b21263495a9025cdff9fd829d2c5c8dba881426e15239",
        "snapshot_tree_files": 4085,
        "snapshot_tree_root": "71663cf756cad1347f71a70e1f9cf6071101ab3f494def62e13d268a9066f6fd",
        "selected_lineage_root": "c5ef16a1f3b5dd096f243aa34d2e97d123c85b391e0389fcd2d2627f3025e8d4",
    }
    for key, expected in expected_origin.items():
        check(f"lineage:{key}", origin.get(key) == expected, origin.get(key))
    check("lineage-runtime-root", data.get("lineage_root") == expected_origin["snapshot_tree_root"], data.get("lineage_root"))
    check("lineage-selected-runtime-root", data.get("selected_lineage_root") == expected_origin["selected_lineage_root"], data.get("selected_lineage_root"))
    lineage = data.get("lineage_fingerprints", [])
    check("lineage-paths-unique", len({item.get("path") for item in lineage}) == 32, len({item.get("path") for item in lineage}))
    check("lineage-hashes-valid", all(isinstance(item.get("sha256"), str) and re.fullmatch(r"[a-f0-9]{64}", item["sha256"]) for item in lineage), "32 expected")
    check("lineage-bytes-positive", all(isinstance(item.get("bytes"), int) and item["bytes"] > 0 for item in lineage), "all positive")

    security = data.get("security", {})
    for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "local_storage", "live_ens_resolution", "live_compute", "live_token_movement", "credential_issuance"]:
        check(f"security:{key}-false", security.get(key) is False, security.get(key))
    check("security:human-review-required", security.get("human_review_required") is True, security.get("human_review_required"))
    check("security:external-authority-none", security.get("external_authority") == "none", security.get("external_authority"))
    check("security:csp-connect-none", "connect-src none" in str(security.get("content_security_policy")), security.get("content_security_policy"))
    allocations = data.get("settlement_policy", {}).get("allocations", [])
    check("settlement-six-allocations", len(allocations) == 6, len(allocations))
    check("settlement-allocation-total", sum(item.get("pct", 0) for item in allocations) == 100, sum(item.get("pct", 0) for item in allocations))
    check("settlement-no-live-token", data.get("settlement_policy", {}).get("live_token_movement") is False, data.get("settlement_policy"))
    check("settlement-no-wallet", data.get("settlement_policy", {}).get("wallet_connection") is False, data.get("settlement_policy"))
    check("settlement-no-authority", data.get("settlement_policy", {}).get("settlement_authority") == "NONE_GRANTED", data.get("settlement_policy"))

    mainnet = data.get("mainnet_record", {})
    check("mainnet-network", mainnet.get("network") == "Ethereum Mainnet", mainnet)
    check("mainnet-contract-record", mainnet.get("contracts") == 48, mainnet)
    check("mainnet-verification-record", mainnet.get("verification") == "48/48" and mainnet.get("verification_failures") == 0, mainnet)
    check("mainnet-phase-b-record", mainnet.get("phase_b_grants") == "14/14", mainnet)
    check("mainnet-production-off", mainnet.get("production_activation") == "NOT_ACTIVATED", mainnet)
    check("mainnet-user-funds-no", mainnet.get("user_fund_authorization") == "NO", mainnet)
    check("mainnet-no-external-audit-claim", mainnet.get("external_audit_claim") == "NONE", mainnet)

    check("docket-schema", docket.get("schema") == "goalos.agi_jobs_v0_v2.evidence_docket.v3", docket.get("schema"))
    check("docket-release-id", docket.get("release_id") == expected_scalars["release_id"], docket.get("release_id"))
    check("docket-version", docket.get("version") == expected_scalars["version"], docket.get("version"))
    check("docket-run-id", bool(re.fullmatch(r"AJ-[A-F0-9]{16}", str(docket.get("run_id", "")))), docket.get("run_id"))
    ranking = docket.get("market", {}).get("ranking", [])
    council = docket.get("market", {}).get("council", {})
    check("docket-twelve-market-records", len(ranking) == 12, len(ranking))
    check("docket-council-five-authorities", all(council.get(key) for key in ["prime", "evidence", "assurance", "delivery", "shadow"]), council)
    check("docket-two-reserves", len(council.get("reserves", [])) == 2, council.get("reserves"))
    check("docket-eight-work-packages", len(docket.get("work_graph", [])) == 8, len(docket.get("work_graph", [])))

    parliament = docket.get("parliament", {})
    judgments = parliament.get("judgments", [])
    check("docket-nine-validator-seats", parliament.get("seats") == 9 and len(judgments) == 9, parliament.get("seats"))
    check("docket-validator-threshold-seven", parliament.get("threshold") == 7, parliament.get("threshold"))
    check("docket-eight-pass-one-dissent", parliament.get("pass") == 8 and parliament.get("dissent") == 1 and parliament.get("reject") == 0 and parliament.get("abstain") == 0, parliament)
    check("docket-validator-commitments", all(re.fullmatch(r"[a-f0-9]{64}", str(item.get("commitment", ""))) for item in judgments), "all commitments")
    check("docket-six-guardians", len(docket.get("guardians", [])) == 6, len(docket.get("guardians", [])))
    check("docket-guardians-clear", all(item.get("status") == "CLEAR" for item in docket.get("guardians", [])), docket.get("guardians"))

    evidence = docket.get("evidence", {})
    chain = evidence.get("artifacts", [])
    check("docket-twenty-four-artifacts", evidence.get("artifact_count") == 24 and len(chain) == 24, len(chain))
    previous = "0" * 64
    chain_valid = True
    for index, item in enumerate(chain, start=1):
        expected_id = f"A{index:02d}"
        expected_commitment = hashlib.sha256(stable_json({"previous": previous, "payload": item.get("payload")}).encode("utf-8")).hexdigest()
        if item.get("id") != expected_id or item.get("previous_commitment") != previous or item.get("commitment") != expected_commitment:
            chain_valid = False
            break
        previous = expected_commitment
    check("docket-chain-valid", chain_valid, previous)
    check("docket-chain-head", evidence.get("chain_head") == previous, evidence.get("chain_head"))
    commitment_source = deepcopy(docket)
    observed_commitment = commitment_source.pop("run_commitment", None)
    expected_commitment = hashlib.sha256(stable_json(commitment_source).encode("utf-8")).hexdigest()
    check("docket-run-commitment-valid", observed_commitment == expected_commitment, observed_commitment)

    settlement = docket.get("settlement", {})
    authority = docket.get("authority", {})
    check("docket-six-settlement-allocations", len(settlement.get("allocation", [])) == 6, len(settlement.get("allocation", [])))
    check("docket-settlement-total", round(sum(float(item.get("units", 0)) for item in settlement.get("allocation", [])), 2) == float(docket.get("work_constitution", {}).get("reward_units", -1)), settlement.get("allocation"))
    check("docket-zero-wallets", settlement.get("wallet_connections") == 0 and authority.get("wallet_connections") == 0, {"settlement": settlement.get("wallet_connections"), "authority": authority.get("wallet_connections")})
    check("docket-zero-live-token-movement", settlement.get("live_token_movement") == 0 and authority.get("live_token_movements") == 0, authority)
    check("docket-zero-network-and-external-actions", authority.get("network_requests") == 0 and authority.get("external_actions") == 0, authority)
    check("docket-authority-none", authority.get("external_authority") == "NONE_GRANTED", authority)
    check("docket-human-settlement-review", authority.get("terminal_state") == "HUMAN_SETTLEMENT_REVIEW", authority)
    check("docket-production-off", authority.get("production_activation") == "NOT_ACTIVATED", authority)
    check("docket-user-funds-no", authority.get("user_fund_authorization") == "NO", authority)
    check("docket-factual-not-certified", authority.get("factual_correctness") == "NOT_CERTIFIED", authority)
    check("docket-claim-boundary-ten", len(docket.get("claim_boundary", [])) == 10, len(docket.get("claim_boundary", [])))

    for page in PAGES:
        text = (site / page).read_text(encoding="utf-8")
        check(f"page-title:{page}", "AGI Jobs v0 (v2)" in text, text[:180])
        check(f"page-local-css:{page}", 'href="assets/agi-jobs-v0-v2.css"' in text, "")
        check(f"page-local-js:{page}", 'src="assets/agi-jobs-v0-v2.js"' in text, "")
        check(f"page-embedded-data:{page}", 'id="agi-jobs-data"' in text, "")
        check(f"page-csp-connect-none:{page}", "connect-src 'none'" in text, "")
        check(f"page-no-remote-runtime:{page}", not re.search(r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://', text, re.I), "")
        check(f"page-no-unresolved-token:{page}", "@@" not in text, "")

    page_checks = {
        "agi-jobs-v0-v2.html": ["aj-hero-title", "aj-job-form", "aj-gate-rail", "aj-market-table", "aj-council-roles", "aj-work-graph", "aj-validator-ring", "aj-artifact-constellation", "aj-terminal-state"],
        "agi-jobs-v0-v2-market.html": ["aj-pareto-chart", "aj-market-ranking", "aj-guild-grid", "aj-archetype-grid"],
        "agi-jobs-v0-v2-proof.html": ["aj-proof-parliament-grid", "aj-ledger", "aj-threat-theatre", "aj-docket-json"],
        "agi-jobs-v0-v2-settlement.html": ["aj-settlement-grid", "aj-condition-grid", "aj-passport-name", "aj-memory-deltas"],
        "agi-jobs-v0-v2-architecture.html": ["aj-module-stack", "aj-translation-table", "aj-principle-grid", "aj-threat-grid", "aj-lineage-table", "aj-mainnet-context", "aj-claim-list"],
    }
    for page, ids in page_checks.items():
        text = (site / page).read_text(encoding="utf-8")
        for identifier in ids:
            check(f"page-id:{page}:{identifier}", f'id="{identifier}"' in text, "")

    javascript = (site / "assets" / "agi-jobs-v0-v2.js").read_text(encoding="utf-8")
    check("runtime-all-terminal-states", all(item in javascript for item in ["HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "DISPUTE_OPEN", "SAFE_HOLD"]), "")
    check("runtime-no-fetch", not re.search(r"\bfetch\s*\(|XMLHttpRequest|WebSocket\s*\(|EventSource\s*\(", javascript), "")
    check("runtime-no-storage", not re.search(r"localStorage|sessionStorage|indexedDB", javascript), "")
    check("runtime-no-wallet", not re.search(r"ethereum\.request|window\.ethereum|walletconnect", javascript, re.I), "")
    check("runtime-deterministic-sha256", "function sha256" in javascript and "function stable" in javascript, "")
    check("runtime-state-exposed", "window.__AGI_JOBS_STATE__" in javascript, "")
    check("runtime-pareto-frontier", "isDominated" in javascript and "frontier" in javascript, "")
    check("runtime-risk-sized-parliament", "validator_seats" in javascript and "validator_threshold" in javascript, "")
    check("runtime-twenty-four-chain", "data.artifacts.length" in javascript and "chain_head" in javascript, "")
    check("runtime-downloads", all(item in javascript for item in ["evidence-docket.json", "executive-brief.md", "download("]), "")

    homepage = (site / "index.html").read_text(encoding="utf-8")
    for marker in MARKERS:
        check(f"homepage-marker-once:{marker}", homepage.count(marker) == 1, homepage.count(marker))
    check("homepage-gateway-once", homepage.count('id="agi-jobs-v0-v2"') == 1, homepage.count('id="agi-jobs-v0-v2"'))
    check("homepage-nav-link-once", homepage.count('href="agi-jobs-v0-v2.html">AGI Jobs</a>') == 1, homepage.count('href="agi-jobs-v0-v2.html">AGI Jobs</a>'))
    check("homepage-five-feature-links", all(f'href="{page}"' in homepage for page in PAGES), "")
    check("homepage-flagship-copy", "A market of minds. A parliament of proof." in homepage and "THE WORK" in homepage and "CIVILIZATION" in homepage, "")
    check("homepage-counts", all(value in homepage for value in [">12<", ">16<", ">9<", ">24<"]), "")

    routes = load(site / "routes.json")
    check("routes-all-pages", all(page in routes.get("routes", []) for page in PAGES), routes.get("agi_jobs_v0_v2"))
    check("routes-release-id", routes.get("agi_jobs_v0_v2", {}).get("release_id") == expected_scalars["release_id"], routes.get("agi_jobs_v0_v2"))
    status = load(site / "site-status.json")
    status_record = status.get("agi_jobs_v0_v2", {})
    check("site-status-artifacts", status_record.get("evidence_artifacts") == 24, status_record)
    check("site-status-gates", status_record.get("constitutional_gates") == 16, status_record)
    check("site-status-pages", status_record.get("pages") == PAGES, status_record)
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    check("sitemap-all-pages", all(page in sitemap for page in PAGES), "")

    check("manifest-schema", manifest.get("schema") == "goalos.agi_jobs_v0_v2.website_manifest.v3", manifest.get("schema"))
    check("manifest-release", manifest.get("release_title") == RELEASE_TITLE and manifest.get("release_id") == expected_scalars["release_id"], {"title": manifest.get("release_title"), "id": manifest.get("release_id")})
    experience = manifest.get("experience", {})
    check("manifest-counts", experience.get("constitutional_gates") == 16 and experience.get("agent_guilds") == 12 and experience.get("validator_seats") == 9 and experience.get("evidence_artifacts") == 24 and experience.get("public_surfaces") == 5, experience)
    check("manifest-terminal-states", experience.get("terminal_states") == ["HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "DISPUTE_OPEN", "SAFE_HOLD"], experience.get("terminal_states"))
    source_lineage = manifest.get("source_lineage", {})
    check("manifest-source-lineage", source_lineage.get("snapshot_tree_root") == expected_origin["snapshot_tree_root"] and source_lineage.get("fingerprints") == 32, source_lineage)
    check("manifest-sample-commitment", manifest.get("sample_run_commitment") == docket.get("run_commitment"), manifest.get("sample_run_commitment"))
    manifest_files = manifest.get("files", {})
    manifest_hashes_valid = isinstance(manifest_files, dict) and bool(manifest_files)
    if manifest_hashes_valid:
        for relative, record in manifest_files.items():
            target = site / relative
            if not isinstance(record, dict) or not target.is_file() or digest(target) != record.get("sha256") or target.stat().st_size != record.get("bytes"):
                manifest_hashes_valid = False
                break
    check("manifest-hashes-valid", manifest_hashes_valid, len(manifest_files) if isinstance(manifest_files, dict) else 0)

    for companion_name, expected_schema in COMPANION_MANIFEST_SCHEMAS.items():
        companion_path = site / companion_name
        if not companion_path.is_file():
            check(f"companion-optional:{companion_name}", True, "not installed")
            continue
        companion = load(companion_path)
        check(f"companion-schema:{companion_name}", companion.get("schema") == expected_schema, companion.get("schema"))
        companion_files = companion.get("files", {})
        companion_integrity = isinstance(companion_files, dict) and bool(companion_files)
        if companion_integrity:
            for relative, record in companion_files.items():
                target = site / relative
                if not isinstance(record, dict) or not target.is_file() or digest(target) != record.get("sha256") or target.stat().st_size != record.get("bytes"):
                    companion_integrity = False
                    break
        check(f"companion-integrity:{companion_name}", companion_integrity, len(companion_files) if isinstance(companion_files, dict) else 0)
        reconciliations = companion.get("integration", {}).get("reconciliations", [])
        reconciliation_present = isinstance(reconciliations, list) and any(isinstance(item, dict) and item.get("release_id") == expected_scalars["release_id"] for item in reconciliations)
        check(f"companion-reconciliation:{companion_name}", reconciliation_present, reconciliations)

    check("build-report-pass", build_report.get("status") == "PASS", build_report.get("status"))
    check("build-report-schema", build_report.get("schema") == "goalos.agi_jobs_v0_v2.build_report.v3", build_report.get("schema"))
    check("build-report-pages", build_report.get("pages") == PAGES, build_report.get("pages"))
    check("build-report-no-removals", build_report.get("preservation", {}).get("files_removed") == 0, build_report.get("preservation"))

    check("schema-file-present", schema is None or schema.is_file(), str(schema) if schema else "not supplied")
    if schema and schema.is_file():
        schema_data = load(schema)
        check("schema-id", str(schema_data.get("$id", "")).endswith("agi-jobs-v0-v2-evidence-docket.schema.json"), schema_data.get("$id"))
        check("schema-v3", schema_data.get("properties", {}).get("schema", {}).get("const") == "goalos.agi_jobs_v0_v2.evidence_docket.v3", schema_data.get("properties", {}).get("schema"))
        check("schema-requires-run-commitment", "run_commitment" in schema_data.get("required", []), schema_data.get("required"))
        check("schema-twenty-four-artifacts", schema_data.get("properties", {}).get("evidence", {}).get("properties", {}).get("artifacts", {}).get("minItems") == 24, "")
        check("schema-four-terminal-states", len(schema_data.get("properties", {}).get("authority", {}).get("properties", {}).get("terminal_state", {}).get("enum", [])) == 4, "")

    preservation: dict[str, Any] = {"baseline_supplied": bool(baseline)}
    if baseline:
        snapshot = load(baseline)
        baseline_files = snapshot.get("files", {})
        current_files = file_inventory(site)
        try:
            output_relative = output.relative_to(site).as_posix()
            current_files.pop(output_relative, None)
        except ValueError:
            pass
        removed = sorted(set(baseline_files) - set(current_files))
        changed = sorted(path for path in set(baseline_files) & set(current_files) if baseline_files[path].get("sha256") != current_files[path].get("sha256"))
        added = sorted(set(current_files) - set(baseline_files))
        unexpected_changed = sorted(set(changed) - ALLOWED_CHANGED)
        expected_additions = NEW_OUTPUTS - set(baseline_files)
        unexpected_added = sorted(set(added) - expected_additions)
        missing_additions = sorted(expected_additions - set(added))
        preservation.update({
            "removed": removed,
            "changed": changed,
            "added": added,
            "unexpected_changed": unexpected_changed,
            "unexpected_added": unexpected_added,
            "missing_additions": missing_additions,
        })
        check("preservation-no-removals", not removed, removed)
        check("preservation-only-declared-changes", not unexpected_changed, unexpected_changed)
        check("preservation-only-declared-additions", not unexpected_added, unexpected_added)
        check("preservation-all-additions-present", not missing_additions, missing_additions)
        check("preservation-baseline-count", len(baseline_files) == snapshot.get("file_count"), {"listed": len(baseline_files), "declared": snapshot.get("file_count")})
    else:
        check("preservation-baseline-optional", True, "No baseline supplied; structural checks still applied.")

    source_root = root / "website" / "v86_actual_site"
    check("canonical-v86-source-present", source_root.is_dir(), str(source_root))
    forbidden_public = [path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file() and path.suffix.lower() in {".zip", ".7z", ".rar", ".gz", ".tar"}]
    check("public-site-no-archives", not forbidden_public, forbidden_public)

    failed = [item for item in checks if item["status"] == "FAIL"]
    report = {
        "schema": "goalos.agi_jobs_v0_v2.static_qa.v3",
        "release_title": RELEASE_TITLE,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "checks": checks,
        "preservation": preservation,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--schema", type=Path, default=root / "schemas" / "agi-jobs-v0-v2-evidence-docket.schema.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.site / "qa" / "agi-jobs-v0-v2-static.json"
    report = run(args.site.resolve(), args.root.resolve(), args.baseline.resolve() if args.baseline else None, args.schema.resolve() if args.schema else None, output.resolve())
    print(json.dumps({"status": report["status"], "checks_total": report["checks_total"], "checks_passed": report["checks_passed"], "checks_failed": report["checks_failed"], "output": str(output)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
