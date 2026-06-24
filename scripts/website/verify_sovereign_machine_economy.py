#!/usr/bin/env python3
"""Verify the GoalOS Sovereign Machine Economy release and preservation boundary."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

RELEASE_TITLE = "GoalOS AGIALPHA Ascension Sovereign Machine Economy 👁️⚡️✨"
PAGES = [
    "sovereign-machine-economy.html",
    "sovereign-machine-economy-observatory.html",
    "sovereign-machine-economy-architecture.html",
    "sovereign-machine-economy-ledger.html",
    "sovereign-machine-economy-memory.html",
    "sovereign-machine-economy-passport.html",
]
DEPENDENCY_PAGES = [
    "meta-agentic-alpha-agi.html", "meta-agentic-alpha-agi-architecture.html",
    "agi-alpha-node-v0.html", "agi-alpha-node-v0-architecture.html", "agi-alpha-node-v0-proof-ledger.html",
    "agi-jobs-v0-v2.html", "agi-jobs-v0-v2-market.html", "agi-jobs-v0-v2-proof.html", "agi-jobs-v0-v2-settlement.html", "agi-jobs-v0-v2-architecture.html",
]
COMPANION_MANIFESTS = {
    "meta-agentic-alpha-agi-manifest.json": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
    "agi-alpha-node-v0-manifest.json": "goalos.agi_alpha_node_v0.website_manifest.v2",
    "agi-jobs-v0-v2-manifest.json": "goalos.agi_jobs_v0_v2.website_manifest.v3",
}
SHARED = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
NEW_OUTPUTS = {
    *PAGES,
    "sovereign-machine-economy-manifest.json",
    "assets/sovereign-machine-economy.css",
    "assets/sovereign-machine-economy.js",
    "data/sovereign-machine-economy.json",
    "downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json",
    "downloads/sovereign-machine-economy/sovereign-machine-economy-executive-brief.md",
    "qa/sovereign-machine-economy-build.json",
}
ALLOWED_CHANGED = SHARED | set(COMPANION_MANIFESTS)


def stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_value(value: Any) -> str:
    return sha_bytes(stable(value).encode("utf-8"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict): raise ValueError(f"expected JSON object: {path}")
    return value


def local_targets(raw: str) -> list[str]:
    return re.findall(r'(?:href|src)=["\']([^"\']+)["\']', raw, re.I)


def run(site: Path, root: Path, content_path: Path, schema_path: Path, baseline_path: Path | None, output: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    preservation: dict[str, Any] = {}
    def check(label: str, condition: bool, detail: Any = "") -> None:
        checks.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("site-exists", site.is_dir(), str(site))
    required = [
        *PAGES,
        "sovereign-machine-economy-manifest.json",
        "assets/sovereign-machine-economy.css",
        "assets/sovereign-machine-economy.js",
        "data/sovereign-machine-economy.json",
        "downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json",
        "downloads/sovereign-machine-economy/sovereign-machine-economy-executive-brief.md",
        "qa/sovereign-machine-economy-build.json",
        *sorted(SHARED),
        *DEPENDENCY_PAGES,
        *COMPANION_MANIFESTS,
    ]
    for relative in required:
        path = site / relative
        check(f"required:{relative}", path.is_file() and path.stat().st_size > 0, path.stat().st_size if path.is_file() else 0)
    if not all((site / relative).is_file() for relative in required):
        report = {"schema":"goalos.sovereign_machine_economy.static_qa.v2","status":"FAIL","checks_total":len(checks),"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_failed":sum(x["status"]=="FAIL" for x in checks),"checks":checks,"preservation":preservation}
        output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return report

    content = load(content_path)
    data = load(site / "data/sovereign-machine-economy.json")
    docket = load(site / "downloads/sovereign-machine-economy/sample-sovereign-machine-economy-docket.json")
    manifest = load(site / "sovereign-machine-economy-manifest.json")
    build_report = load(site / "qa/sovereign-machine-economy-build.json")

    expected_scalars = {
        "schema_version":"2.0.0",
        "release_id":"GOALOS-AGIALPHA-SOVEREIGN-MACHINE-ECONOMY-002",
        "release_title":RELEASE_TITLE,
        "version":"2.0.0-constitutional-civilization-engine",
        "status":"interactive-constitutional-machine-economy-civilization-engine",
        "tagline":"A mind that builds minds. A node that turns intelligence into proof. A market that turns proof into accountable value.",
        "doctrine":"Minds are formed. Nodes execute. Markets coordinate. Proof earns permission. Humans authorize.",
    }
    for key, expected in expected_scalars.items():
        check(f"content:{key}", content.get(key) == expected, content.get(key))
        check(f"generated-data:{key}", data.get(key) == expected, data.get(key))
    expected_counts = {"source_releases":3,"hero_metrics":6,"thesis":7,"mission_presets":8,"postures":4,"risk_profiles":4,"incidents":8,"gates":21,"handoffs":15,"artifact_classes":48,"governance_principles":10,"threats":10,"memory_rules":9,"review_actions":4,"universes":3,"constitutional_rights":8,"claim_boundary":10}
    for key, count in expected_counts.items():
        check(f"content-count:{key}", isinstance(content.get(key),list) and len(content[key]) == count, len(content.get(key,[])))
        check(f"data-count:{key}", isinstance(data.get(key),list) and len(data[key]) == count, len(data.get(key,[])))

    security = data.get("security", {})
    for key in ["external_dependencies","api_keys","wallet_connection","network_reads","network_writes","live_model_calls","live_compute","live_token_movement","credential_issuance","local_storage"]:
        check(f"security-default-deny:{key}", security.get(key) is False, security.get(key))
    check("security-human-review", security.get("human_review_required") is True, security.get("human_review_required"))
    check("security-no-authority", security.get("external_authority") == "none", security.get("external_authority"))

    dependency_expectations = {
        "meta": ("GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨", "2.0.0-ascension-alpha"),
        "node": ("GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨", "3.0.0-sovereign-citadel"),
        "jobs": ("GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨", "3.0.0-sovereign-work-civilization"),
    }
    for key, (title, version) in dependency_expectations.items():
        dep = data.get("dependencies",{}).get(key,{})
        check(f"dependency-title:{key}", dep.get("title") == title, dep.get("title"))
        check(f"dependency-version:{key}", dep.get("version") == version, dep.get("version"))
    check("dependency-meta-agents", len(data.get("dependencies",{}).get("meta",{}).get("agents",[])) >= 8, len(data.get("dependencies",{}).get("meta",{}).get("agents",[])))
    check("dependency-node-peers", len(data.get("dependencies",{}).get("node",{}).get("peers",[])) == 12, len(data.get("dependencies",{}).get("node",{}).get("peers",[])))
    check("dependency-jobs-institutions", len(data.get("dependencies",{}).get("jobs",{}).get("institutions",[])) == 12, len(data.get("dependencies",{}).get("jobs",{}).get("institutions",[])))
    check("dependency-jobs-validators", len(data.get("dependencies",{}).get("jobs",{}).get("validators",[])) >= 7, len(data.get("dependencies",{}).get("jobs",{}).get("validators",[])))

    page_contract = {
        "sovereign-machine-economy.html": ["THE SOVEREIGN", "MACHINE ECONOMY", "sme-mission-form", "sme-gate-rail", "sme-review-chamber", "sme-universe-preview"],
        "sovereign-machine-economy-observatory.html": ["COUNTERFACTUAL", "OBSERVATORY", "sme-observatory-preset", "sme-universe-grid", "sme-comparison-table"],
        "sovereign-machine-economy-architecture.html": ["THREE ENGINES", "ONE CONSTITUTION", "sme-architecture-stack", "sme-rights-grid", "sme-authority-matrix"],
        "sovereign-machine-economy-ledger.html": ["PROOF", "CHRONICLE", "sme-ledger-handoffs", "sme-artifact-ledger", "sme-sample-json"],
        "sovereign-machine-economy-memory.html": ["MEMORY WITHOUT", "SELF-PROMOTION", "sme-memory-cycle", "sme-memory-rules", "sme-rollback-flow"],
        "sovereign-machine-economy-passport.html": ["MISSION", "PASSPORT", "sme-passport-file", "sme-passport-glyph", "sme-passport-fields"],
    }
    for page, needles in page_contract.items():
        path = site / page; raw = path.read_text(encoding="utf-8")
        check(f"page-size:{page}", path.stat().st_size > 5000, path.stat().st_size)
        check(f"page-doctype:{page}", raw.lstrip().lower().startswith("<!doctype html>"), raw[:30])
        check(f"page-csp:{page}", "Content-Security-Policy" in raw and "connect-src 'none'" in raw, "CSP")
        check(f"page-data:{page}", 'id="sme-data"' in raw, "sme-data")
        check(f"page-css:{page}", 'href="assets/sovereign-machine-economy.css"' in raw, "css")
        check(f"page-js:{page}", 'src="assets/sovereign-machine-economy.js"' in raw, "js")
        check(f"page-no-external-runtime:{page}", not re.search(r'(?:src|href)=["\'](?:https?:)?//', raw, re.I), "external ref scan")
        for needle in needles:
            check(f"page-contract:{page}:{needle}", needle in raw, needle)
        for target in local_targets(raw):
            clean = unquote(target.split("#",1)[0].split("?",1)[0])
            if not clean or clean.startswith(("#","data:","mailto:","tel:","javascript:")) or clean.startswith(("http://","https://","//")):
                continue
            check(f"local-target:{page}:{clean}", (site / clean).exists(), clean)

    homepage = (site / "index.html").read_text(encoding="utf-8")
    for marker in ["GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_START","GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_END","GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_START","GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_END","GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_START","GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_END"]:
        check(f"homepage-marker:{marker}", homepage.count(marker) == 1, homepage.count(marker))
    check("homepage-nav-once", homepage.count('href="sovereign-machine-economy.html">Machine Economy Ω</a>') == 1, homepage.count('href="sovereign-machine-economy.html">Machine Economy Ω</a>'))
    check("homepage-gateway-once", homepage.count('id="sovereign-machine-economy"') == 1, homepage.count('id="sovereign-machine-economy"'))
    for title in ["META-AGENTIC α‑AGI", "AGI Alpha Node", "AGI Jobs v0 (v2)"]:
        check(f"homepage-triad-copy:{title}", title in homepage, title)
    check("homepage-style-link", homepage.count('assets/sovereign-machine-economy.css') == 1, homepage.count('assets/sovereign-machine-economy.css'))

    routes = load(site / "routes.json")
    check("routes-pages", set(PAGES).issubset(set(routes.get("routes",[]))), routes.get("routes",[]))
    route = routes.get("sovereign_machine_economy",{})
    check("routes-gates", route.get("constitutional_gates") == 21, route.get("constitutional_gates"))
    check("routes-handoffs", route.get("handoffs") == 15, route.get("handoffs"))
    check("routes-artifacts", route.get("artifacts") == 48, route.get("artifacts"))
    check("routes-external-actions", route.get("external_actions") == 0, route.get("external_actions"))
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    for page in PAGES: check(f"sitemap:{page}", page in sitemap, page)
    full_status = load(site / "site-status.json")
    status = full_status.get("sovereign_machine_economy",{})
    for key, expected in {"engines":3,"constitutional_gates":21,"handoffs":15,"evidence_artifacts":48,"counterfactual_universes":3,"human_review_actions":4,"terminal_state":"HUMAN_SETTLEMENT_REVIEW","external_authority":"NONE_GRANTED","external_actions":0}.items():
        check(f"site-status:{key}", status.get(key) == expected, status.get(key))
    root_count = len(list(site.glob("*.html")))
    all_count = len(list(site.rglob("*.html")))
    check("site-status-page-counts", full_status.get("root_html_pages") == root_count and full_status.get("published_html_pages_including_resources") == all_count, {"stored_root":full_status.get("root_html_pages"),"actual_root":root_count,"stored_all":full_status.get("published_html_pages_including_resources"),"actual_all":all_count})

    check("docket-schema", docket.get("schema") == "goalos.sovereign_machine_economy.docket.v2", docket.get("schema"))
    check("docket-release", docket.get("release_id") == data.get("release_id"), docket.get("release_id"))
    check("docket-handoffs", len(docket.get("handoffs",[])) == 15, len(docket.get("handoffs",[])))
    previous = "0" * 64
    for index, item in enumerate(docket.get("handoffs",[]), 1):
        check(f"handoff-id:{index}", item.get("id") == f"H{index:02d}", item.get("id"))
        check(f"handoff-previous:{index}", item.get("previous_commitment") == previous, item.get("previous_commitment"))
        payload = {"id": item["id"], "from": item["from"], "to": item["to"], "name": item["name"], "mission": docket["mission"]["mission"], "institution": docket["institution"]["id"], "node": docket["node"]["id"], "market": docket["market"]["id"], "previous": previous}
        expected_commitment = sha_value(payload)
        check(f"handoff-commitment:{index}", item.get("commitment") == expected_commitment, item.get("commitment"))
        previous = expected_commitment

    artifacts = docket.get("evidence",{}).get("artifacts",[])
    check("docket-artifact-count", len(artifacts) == 48 and docket.get("evidence",{}).get("artifact_count") == 48, len(artifacts))
    previous = "0" * 64
    for index, item in enumerate(artifacts, 1):
        check(f"artifact-id:{index}", item.get("id") == f"A{index:02d}", item.get("id"))
        check(f"artifact-previous:{index}", item.get("previous_commitment") == previous, item.get("previous_commitment"))
        expected_hash = sha_value(item.get("payload"))
        expected_commitment = sha_value({"previous":previous,"payload":item.get("payload"),"artifact_hash":expected_hash})
        check(f"artifact-hash:{index}", item.get("artifact_hash") == expected_hash, item.get("artifact_hash"))
        check(f"artifact-commitment:{index}", item.get("commitment") == expected_commitment, item.get("commitment"))
        previous = expected_commitment
    check("docket-chain-head", docket.get("evidence",{}).get("chain_head") == previous, docket.get("evidence",{}).get("chain_head"))
    expected_root = sha_value({"institution":docket["institution"]["charter_commitment"],"node":docket["node"]["identity_commitment"],"market":docket["market"]["charter_commitment"],"handoffs":docket["handoffs"][-1]["commitment"],"evidence":previous,"counterfactuals":[item["commitment"] for item in docket["counterfactuals"]],"memory":docket["memory"]["id"],"review":docket["review"]["status"],"terminal":docket["authority"]["terminal_state"]})
    check("docket-economy-root", docket.get("economy_root") == expected_root, docket.get("economy_root"))
    without_run = dict(docket); run_commitment = without_run.pop("run_commitment")
    check("docket-run-commitment", run_commitment == sha_value(without_run), run_commitment)
    authority = docket.get("authority",{})
    for key, expected in {"terminal_state":"HUMAN_SETTLEMENT_REVIEW","external_authority":"NONE_GRANTED","factual_correctness":"NOT_CERTIFIED","production_activation":"NOT_ACTIVATED","user_fund_authorization":"NO","automatic_memory_promotion":"NOT_AUTHORIZED","external_actions":0,"network_requests":0,"wallet_connections":0,"live_token_movements":0}.items():
        check(f"docket-authority:{key}", authority.get(key) == expected, authority.get(key))
    check("docket-memory-human", docket.get("memory",{}).get("status") == "HUMAN_PROMOTION_REQUIRED", docket.get("memory",{}).get("status"))
    check("docket-memory-revocable", docket.get("memory",{}).get("revocable") is True and docket.get("memory",{}).get("automatic_promotion") is False, docket.get("memory",{}))
    parliament = docket.get("market",{}).get("parliament",{})
    dissent_opinions = [item for item in parliament.get("opinions",[]) if item.get("verdict") == "DISSENT"]
    check("docket-dissent", parliament.get("dissent") == 1 and len(dissent_opinions) == 1, parliament)
    check("docket-independent-dissent-seat", bool(dissent_opinions) and (str(dissent_opinions[0].get("id", "")).upper() == "V09" or "independent dissent" in str(dissent_opinions[0].get("name", "")).lower()), dissent_opinions)
    counterfactuals = docket.get("counterfactuals", [])
    check("docket-counterfactual-count", len(counterfactuals) == 3, len(counterfactuals))
    check("docket-counterfactual-identities", [item.get("id") for item in counterfactuals] == ["prudential", "balanced", "frontier"], [item.get("id") for item in counterfactuals])
    check("docket-counterfactual-authority", all(item.get("authority") == "NONE_GRANTED" and item.get("external_actions") == 0 for item in counterfactuals), counterfactuals)
    check("docket-counterfactual-commitments", all(re.fullmatch(r"[a-f0-9]{64}", str(item.get("commitment", ""))) is not None for item in counterfactuals), [item.get("commitment") for item in counterfactuals])
    review = docket.get("review", {})
    check("docket-review-pending", review.get("status") == "PENDING_HUMAN_REVIEW", review.get("status"))
    check("docket-review-actions", len(review.get("available_actions", [])) == 4, len(review.get("available_actions", [])))
    check("docket-review-no-authority", review.get("authority_granted") is False and review.get("settlement_authorized") is False and review.get("memory_promoted") is False, review)

    try:
        import jsonschema
        errors = sorted(jsonschema.Draft202012Validator(load(schema_path)).iter_errors(docket), key=lambda error: list(error.path))
        check("json-schema", not errors, [error.message for error in errors[:10]])
    except Exception as exc:
        check("json-schema-import", False, str(exc))

    check("manifest-schema", manifest.get("schema") == "goalos.sovereign_machine_economy.website_manifest.v2", manifest.get("schema"))
    check("manifest-release", manifest.get("release_id") == data.get("release_id"), manifest.get("release_id"))
    check("manifest-lineage-root", manifest.get("lineage_root") == data.get("lineage_root"), manifest.get("lineage_root"))
    check("manifest-sample-root", manifest.get("sample_economy_root") == docket.get("economy_root"), manifest.get("sample_economy_root"))
    files = manifest.get("files",{})
    for relative, record in files.items():
        target = site / relative
        check(f"manifest-file-exists:{relative}", target.is_file(), relative)
        if target.is_file():
            check(f"manifest-file-hash:{relative}", record.get("sha256") == sha(target), record.get("sha256"))
            check(f"manifest-file-bytes:{relative}", record.get("bytes") == target.stat().st_size, record.get("bytes"))
    check("manifest-required-coverage", NEW_OUTPUTS - {"qa/sovereign-machine-economy-build.json"} <= set(files) | {"sovereign-machine-economy-manifest.json"}, sorted(NEW_OUTPUTS - set(files)))
    check("build-report-pass", build_report.get("status") == "PASS", build_report.get("status"))
    check("build-report-no-removals", build_report.get("files_removed") == [], build_report.get("files_removed"))
    check("build-report-no-unexpected", build_report.get("unexpected_existing_file_changes") == [], build_report.get("unexpected_existing_file_changes"))

    for filename, schema in COMPANION_MANIFESTS.items():
        companion = load(site / filename)
        check(f"companion-schema:{filename}", companion.get("schema") == schema, companion.get("schema"))
        companion_files = companion.get("files",{})
        for relative in SHARED:
            record = companion_files.get(relative,{})
            target = site / relative
            check(f"companion-shared-hash:{filename}:{relative}", record.get("sha256") == sha(target), record.get("sha256"))
        history = companion.get("integration",{}).get("reconciliations",[])
        check(f"companion-reconciliation:{filename}", any(isinstance(item,dict) and item.get("release_id") == data.get("release_id") for item in history), history[-2:] if isinstance(history,list) else history)

    fingerprint_rows = data.get("lineage_fingerprints",[])
    check("lineage-count", len(fingerprint_rows) == 15, len(fingerprint_rows))
    check("lineage-root-shape", isinstance(data.get("lineage_root"),str) and re.fullmatch(r"[a-f0-9]{64}", data["lineage_root"]) is not None, data.get("lineage_root"))
    check("lineage-root-recompute", data.get("lineage_root") == sha_value([item["sha256"] for item in fingerprint_rows]), data.get("lineage_root"))
    for index, item in enumerate(fingerprint_rows,1):
        check(f"lineage-shape:{index}", re.fullmatch(r"[a-f0-9]{64}", item.get("sha256", "")) is not None and item.get("bytes",0) > 0, item)

    js = (root / "website/features/sovereign-machine-economy/assets/sovereign-machine-economy.js").read_text(encoding="utf-8")
    css = (root / "website/features/sovereign-machine-economy/assets/sovereign-machine-economy.css").read_text(encoding="utf-8")
    check("runtime-state-hook", "window.__SME_STATE__" in js, "__SME_STATE__")
    check("runtime-sha256", "function sha256" in js and "0x428a2f98" in js, "sha256")
    check("runtime-no-fetch", not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(", js), "network API scan")
    check("runtime-no-storage", "localStorage" not in js and "sessionStorage" not in js, "storage scan")
    check("runtime-downloads", "sample-sovereign-machine-economy" not in js and "download(" in js, "download helper")
    check("runtime-counterfactual-engine", "runUniverses" in js and "renderUniverseCards" in js, "counterfactual engine")
    check("runtime-human-review-chamber", "applyReviewAction" in js and "PENDING_HUMAN_REVIEW" in js, "review chamber")
    check("runtime-passport", "renderPassport" in js and "sme-passport-glyph" in js, "mission passport")
    check("runtime-forty-eight-artifacts", "artifact_classes" in js and "A48" not in js, "data-driven evidence chain")
    check("css-scoped", ".sme-body" in css and ".sme-home-gateway" in css, "scoped selectors")
    check("css-responsive", ("@media (max-width:760px)" in css or "@media(max-width:760px)" in css), "mobile media")
    check("css-reduced-motion", "prefers-reduced-motion" in css, "reduced motion")

    forbidden = ["PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY", "SEED_PHRASE", "MNEMONIC", "MAINNET_RPC_URL=", "ETHERSCAN_API_KEY="]
    feature_text = "\n".join((site / relative).read_text(encoding="utf-8",errors="ignore") for relative in [*PAGES,"assets/sovereign-machine-economy.js","assets/sovereign-machine-economy.css","data/sovereign-machine-economy.json"])
    for phrase in forbidden:
        present = phrase in feature_text
        token_id = sha_bytes(phrase.encode("utf-8"))[:12]
        check(f"secret-scan:{token_id}", not present, "detected" if present else "absent")
    for phrase in ["production authorized","user funds authorized","guaranteed return","guaranteed roi"]:
        check(f"claim-scan:{phrase}", phrase not in feature_text.lower(), phrase)

    python_sources = [
        root / "scripts/website/build_sovereign_machine_economy.py",
        root / "scripts/website/snapshot_sovereign_machine_economy_site.py",
        root / "scripts/website/verify_sovereign_machine_economy.py",
        root / "scripts/website/visual_check_sovereign_machine_economy.py",
        root / "test/test_sovereign_machine_economy_website.py",
    ]
    for path in python_sources:
        if path.is_file():
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3,11))
                check(f"python311:{path.name}", True, "PASS")
            except SyntaxError as exc:
                check(f"python311:{path.name}", False, str(exc))

    if baseline_path:
        snapshot = load(baseline_path)
        before = snapshot.get("files",{})
        current = {path.relative_to(site).as_posix(): {"sha256":sha(path),"bytes":path.stat().st_size} for path in site.rglob("*") if path.is_file()}
        removed = sorted(set(before) - set(current))
        changed = sorted(name for name in set(before) & set(current) if before[name].get("sha256") != current[name].get("sha256"))
        added = sorted(set(current) - set(before))
        unexpected_changed = sorted(set(changed) - ALLOWED_CHANGED)
        unexpected_added = sorted(set(added) - NEW_OUTPUTS - {output.relative_to(site).as_posix()} if output.is_relative_to(site) else set(added) - NEW_OUTPUTS)
        preservation = {"baseline_count":len(before),"current_count":len(current),"removed":removed,"changed":changed,"added":added,"unexpected_changed":unexpected_changed,"unexpected_added":unexpected_added,"allowed_changed":sorted(ALLOWED_CHANGED)}
        check("preservation-baseline-count", len(before) == snapshot.get("file_count"), {"listed":len(before),"declared":snapshot.get("file_count")})
        check("preservation-no-removals", not removed, removed)
        check("preservation-no-unexpected-changes", not unexpected_changed, unexpected_changed)
        check("preservation-only-declared-additions", not unexpected_added, unexpected_added)
    else:
        check("preservation-baseline-optional", True, "No baseline supplied; structural preservation checks applied.")

    failed = [item for item in checks if item["status"] == "FAIL"]
    report = {
        "schema":"goalos.sovereign_machine_economy.static_qa.v2",
        "release_title":RELEASE_TITLE,
        "status":"PASS" if not failed else "FAIL",
        "checks_total":len(checks),
        "checks_passed":len(checks)-len(failed),
        "checks_failed":len(failed),
        "checks":checks,
        "preservation":preservation,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--content", type=Path, default=root / "content/sovereign-machine-economy.json")
    parser.add_argument("--schema", type=Path, default=root / "schemas/sovereign-machine-economy-docket.schema.json")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.site / "qa/sovereign-machine-economy-static.json"
    report = run(args.site.resolve(),args.root.resolve(),args.content.resolve(),args.schema.resolve(),args.baseline.resolve() if args.baseline else None,output.resolve())
    print(json.dumps({"status":report["status"],"checks_total":report["checks_total"],"checks_passed":report["checks_passed"],"checks_failed":report["checks_failed"],"output":str(output)},indent=2))
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__": raise SystemExit(main())
