#!/usr/bin/env python3
"""Verify the generated GoalOS AGI Alpha Node v0 Sovereign Citadel release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨"
PAGES = ["agi-alpha-node-v0.html", "agi-alpha-node-v0-architecture.html", "agi-alpha-node-v0-proof-ledger.html"]
NEW_OUTPUTS = {
    *PAGES,
    "agi-alpha-node-v0-manifest.json",
    "assets/agi-alpha-node-v0.css",
    "assets/agi-alpha-node-v0.js",
    "data/agi-alpha-node-v0.json",
    "downloads/agi-alpha-node-v0/sample-node-evidence-docket.json",
    "qa/agi-alpha-node-v0-build.json",
}
SHARED_INTEGRATION_OUTPUTS = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
OPTIONAL_COMPANION_MANIFEST = "meta-agentic-alpha-agi-manifest.json"
ALLOWED_CHANGED = {*SHARED_INTEGRATION_OUTPUTS, OPTIONAL_COMPANION_MANIFEST}
MARKERS = [
    "GOALOS_AGI_ALPHA_NODE_V0_STYLE_START",
    "GOALOS_AGI_ALPHA_NODE_V0_STYLE_END",
    "GOALOS_AGI_ALPHA_NODE_V0_NAV_START",
    "GOALOS_AGI_ALPHA_NODE_V0_NAV_END",
    "GOALOS_AGI_ALPHA_NODE_V0_HOME_START",
    "GOALOS_AGI_ALPHA_NODE_V0_HOME_END",
]


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


def run(site: Path, root: Path, baseline: Path | None, output: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(label: str, condition: bool, detail: Any = "") -> None:
        checks.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("site-exists", site.is_dir(), str(site))
    content_path = site / "data" / "agi-alpha-node-v0.json"
    manifest_path = site / "agi-alpha-node-v0-manifest.json"
    sample_path = site / "downloads" / "agi-alpha-node-v0" / "sample-node-evidence-docket.json"
    required = [site / item for item in [*PAGES, "assets/agi-alpha-node-v0.css", "assets/agi-alpha-node-v0.js", "data/agi-alpha-node-v0.json", "downloads/agi-alpha-node-v0/sample-node-evidence-docket.json", "agi-alpha-node-v0-manifest.json"]]
    for path in required:
        check(f"required-file:{path.relative_to(site).as_posix()}", path.is_file(), path.stat().st_size if path.is_file() else 0)
    if not all(path.is_file() for path in required):
        report = {"schema": "goalos.agi_alpha_node_v0.static_qa.v2", "status": "FAIL", "checks": checks}
        output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(report, indent=2) + "\n")
        return report

    data = load(content_path)
    manifest = load(manifest_path)
    sample = load(sample_path)
    check("release-title", data.get("release_title") == RELEASE_TITLE, data.get("release_title"))
    check("release-version", data.get("version") == "3.0.0-sovereign-citadel", data.get("version"))
    check("release-status", data.get("status") == "interactive-sovereign-proof-node-digital-twin", data.get("status"))
    check("release-tagline", data.get("tagline") == "One node. Many minds. Zero unearned authority.", data.get("tagline"))
    expected_counts = {
        "hero_metrics": 5, "thesis": 5, "work_unit_classes": 5, "presets": 5, "postures": 4, "risk_profiles": 3,
        "incidents": 4, "pipeline": 10, "node_roles": 10, "peers": 12, "validators": 7, "guardians": 5, "artifacts": 16,
        "architecture_translation": 10, "governance_principles": 7, "threats": 8, "claim_boundary": 7, "lineage_fingerprints": 15,
    }
    for key, count in expected_counts.items():
        check(f"content-count:{key}", isinstance(data.get(key), list) and len(data[key]) == count, len(data.get(key, [])) if isinstance(data.get(key), list) else None)
    expected_states = ["NODE_IDENTITY_SEALED", "WORK_UNIT_CONTRACTED", "POLICY_COMPILED", "RESOURCE_ENVELOPE_ADMITTED", "PEER_ROUTES_COMMITTED", "SANDBOX_RECEIPT_READY", "MULTI_AXIS_EVALUATION_READY", "VALIDATOR_QUORUM_RECORDED", "GUARDIAN_REVIEW_PACKAGED", "HUMAN_REVIEW_REQUIRED"]
    check("pipeline-order", [item.get("state") for item in data["pipeline"]] == expected_states, [item.get("state") for item in data["pipeline"]])
    for posture in data["postures"]:
        weights = posture.get("weights", {})
        check(f"posture-six-axes:{posture['id']}", set(weights) == {"quality", "reliability", "energy", "latency", "evidence", "diversity"}, sorted(weights))
        check(f"posture-normalized:{posture['id']}", abs(sum(weights.values()) - 1.0) < 1e-9, sum(weights.values()))
    security = data.get("security", {})
    for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "local_storage", "live_ens_resolution", "live_compute"]:
        check(f"security-default-deny:{key}", security.get(key) is False, security.get(key))
    check("security-human-review", security.get("human_review_required") is True, security.get("human_review_required"))
    check("security-authority-none", security.get("external_authority") == "none", security.get("external_authority"))
    mainnet = data.get("mainnet_record", {})
    check("mainnet-goalos-contracts", mainnet.get("contracts") == 48, mainnet.get("contracts"))
    check("mainnet-operator-verification", mainnet.get("verification") == "48/48", mainnet.get("verification"))
    check("mainnet-phase-b-grants", mainnet.get("phase_b_grants") == "14/14", mainnet.get("phase_b_grants"))
    check("mainnet-production-not-activated", mainnet.get("production_activation") == "NOT_ACTIVATED", mainnet.get("production_activation"))
    check("mainnet-user-funds-no", mainnet.get("user_fund_authorization") == "NO", mainnet.get("user_fund_authorization"))
    check("mainnet-source-identity-pending", mainnet.get("source_identity") == "PENDING", mainnet.get("source_identity"))

    for page_name in PAGES:
        text = (site / page_name).read_text(encoding="utf-8")
        check(f"page-no-template-token:{page_name}", "@@" not in text, text.count("@@"))
        check(f"page-csp-connect-none:{page_name}", "connect-src 'none'" in text, "connect-src 'none'" in text)
        check(f"page-local-css:{page_name}", 'href="assets/agi-alpha-node-v0.css"' in text, "")
        check(f"page-local-js:{page_name}", 'src="assets/agi-alpha-node-v0.js"' in text, "")
        check(f"page-release-data:{page_name}", 'id="aan-release-data"' in text, "")
        check(f"page-no-external-script:{page_name}", not re.search(r'<script[^>]+src=["\']https?://', text, flags=re.I), "")
        check(f"page-no-external-style:{page_name}", not re.search(r'<link[^>]+href=["\']https?://', text, flags=re.I), "")
    main_text = (site / PAGES[0]).read_text(encoding="utf-8")
    for phrase in [RELEASE_TITLE, "One node. Many minds.", "Zero unearned authority.", "The Sovereign Node Theatre", "HUMAN_REVIEW_REQUIRED", "No live peer dial"]:
        check(f"experience-copy:{phrase[:28]}", phrase in main_text, phrase)
    architecture_text = (site / PAGES[1]).read_text(encoding="utf-8")
    for phrase in ["THE NODE", "HAS A CONSTITUTION.", "TEN CONSTITUTIONAL PLANES", "TRACEABLE REIMPLEMENTATION", "FAIL CLOSED"]:
        check(f"architecture-copy:{phrase}", phrase in architecture_text, phrase)
    ledger_text = (site / PAGES[2]).read_text(encoding="utf-8")
    for phrase in ["THE WORK IS NOT THE PROOF.", "THE TRACE IS.", "16 CLASSES", "HUMAN_REVIEW_REQUIRED"]:
        check(f"ledger-copy:{phrase}", phrase in ledger_text, phrase)

    js = (site / "assets" / "agi-alpha-node-v0.js").read_text(encoding="utf-8")
    css = (site / "assets" / "agi-alpha-node-v0.css").read_text(encoding="utf-8")
    for token in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "window.ethereum", "eth_requestAccounts", "localStorage", "sessionStorage"]:
        check(f"runtime-forbidden:{token}", token not in js, token)
    for token in ["createArtifactChain", "createConsensus", "createGuardians", "determineTerminal", "SAFE_HOLD", "HUMAN_REVIEW_REQUIRED", "shadow", "quarantined", "window.__AAN_STATE__"]:
        check(f"runtime-capability:{token}", token in js, token)
    check("css-no-import", "@import" not in css, "@import" in css)
    check("css-responsive-mobile", "@media(max-width:430px)" in css, "")
    check("css-reduced-motion", "prefers-reduced-motion" in css, "")
    check("css-homepage-gateway", ".aan-home-gateway" in css, "")
    check("css-dynamic-mesh", ".aan-mesh-edge.primary" in css, "")

    home = (site / "index.html").read_text(encoding="utf-8")
    for marker in MARKERS:
        check(f"homepage-marker-once:{marker}", home.count(marker) == 1, home.count(marker))
    check("homepage-gateway-once", home.count('id="agi-alpha-node-v0"') == 1, home.count('id="agi-alpha-node-v0"'))
    check("homepage-three-feature-links", all(f'href="{page}"' in home for page in PAGES), [page for page in PAGES if f'href="{page}"' not in home])
    check("homepage-grand-doctrine", "One node. Many minds. Zero unearned authority." in home, "")

    routes = load(site / "routes.json")
    check("routes-feature-pages", all(page in routes.get("routes", []) for page in PAGES), routes.get("agi_alpha_node_v0"))
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    for page in PAGES:
        check(f"sitemap:{page}", sitemap.count(f"./{page}") == 1, sitemap.count(f"./{page}"))
    status = load(site / "site-status.json").get("agi_alpha_node_v0", {})
    check("site-status-version", status.get("version") == data.get("version"), status)
    check("site-status-artifacts", status.get("evidence_artifacts") == 16, status.get("evidence_artifacts"))
    check("site-status-actions-zero", status.get("external_actions") == 0, status.get("external_actions"))

    check("sample-schema", sample.get("schema") == "goalos.agi_alpha_node_v0.node_evidence_docket.v2", sample.get("schema"))
    check("sample-terminal", sample.get("terminal_disposition", {}).get("state") == "HUMAN_REVIEW_REQUIRED", sample.get("terminal_disposition"))
    authority = sample.get("authority", {})
    check("sample-authority-boundary", authority == {"factual_correctness": "NOT_CERTIFIED", "production_activation": "NOT_ACTIVATED", "funds_authorization": "NO", "external_actions": 0, "final_state": "HUMAN_REVIEW_REQUIRED"}, authority)
    chain = sample.get("proof_chronicle", {}).get("artifacts", [])
    check("sample-sixteen-artifacts", len(chain) == 16, len(chain))
    previous = "0" * 64
    chain_valid = True
    for index, artifact in enumerate(chain):
        artifact_hash = hashlib.sha256(stable_json(artifact.get("payload")).encode("utf-8")).hexdigest()
        commitment = hashlib.sha256(f"{previous}:{artifact_hash}:{artifact.get('name')}".encode("utf-8")).hexdigest()
        valid = artifact.get("index") == index + 1 and artifact.get("previous_commitment") == previous and artifact.get("artifact_hash") == artifact_hash and artifact.get("commitment") == commitment
        check(f"sample-chain-artifact:{index + 1:02d}", valid, artifact.get("name"))
        chain_valid = chain_valid and valid
        previous = commitment
    check("sample-chain-head", chain_valid and sample.get("proof_chronicle", {}).get("chain_head") == previous, previous)
    check("sample-validator-quorum", sample.get("validator_consensus", {}).get("quorum_met") is True and sample.get("validator_consensus", {}).get("pass") == 6, sample.get("validator_consensus"))
    check("sample-dissent-preserved", sample.get("validator_consensus", {}).get("dissent") == 1, sample.get("validator_consensus", {}).get("dissent"))
    check("sample-no-guardian-veto", all(item.get("disposition") != "VETO" for item in sample.get("guardian_review", [])), [item.get("disposition") for item in sample.get("guardian_review", [])])

    check("manifest-schema", manifest.get("schema") == "goalos.agi_alpha_node_v0.website_manifest.v2", manifest.get("schema"))
    check("manifest-version", manifest.get("version") == data.get("version"), manifest.get("version"))
    for relative, entry in manifest.get("files", {}).items():
        path = site / relative
        check(f"manifest-file:{relative}", path.is_file(), "")
        if path.is_file():
            check(f"manifest-hash:{relative}", digest(path) == entry.get("sha256"), {"expected": entry.get("sha256"), "actual": digest(path)})
            check(f"manifest-size:{relative}", path.stat().st_size == entry.get("bytes"), {"expected": entry.get("bytes"), "actual": path.stat().st_size})

    companion_path = site / OPTIONAL_COMPANION_MANIFEST
    if companion_path.is_file():
        companion = load(companion_path)
        check("companion-manifest-schema", companion.get("schema") == "goalos.meta_agentic_alpha_agi.website_manifest.v2", companion.get("schema"))
        companion_files = companion.get("files", {})
        for relative in sorted(SHARED_INTEGRATION_OUTPUTS):
            target = site / relative
            entry = companion_files.get(relative, {}) if isinstance(companion_files, dict) else {}
            check(f"companion-manifest-hash:{relative}", target.is_file() and entry.get("sha256") == digest(target), entry)
            check(f"companion-manifest-size:{relative}", target.is_file() and entry.get("bytes") == target.stat().st_size, entry)
        reconciliations = companion.get("integration", {}).get("reconciliations", [])
        matching = [item for item in reconciliations if isinstance(item, dict) and item.get("release_id") == data.get("release_id")]
        check("companion-manifest-reconciliation", len(matching) == 1 and set(matching[0].get("files", [])) == SHARED_INTEGRATION_OUTPUTS, matching)
    else:
        check("companion-manifest-optional", True, "META-Agentic release not installed")

    canonical = root / "website" / "v86_actual_site"
    check("canonical-v86-source-present", canonical.is_dir(), str(canonical))
    for relative in ["index.html", "routes.json", "site-status.json"]:
        check(f"canonical-v86-no-node-markers:{relative}", "GOALOS_AGI_ALPHA_NODE_V0" not in (canonical / relative).read_text(encoding="utf-8"), relative)

    preservation = {"baseline_supplied": bool(baseline), "removed": [], "unexpected_changed": [], "unchanged": 0, "allowed_changed": []}
    if baseline:
        snapshot = load(baseline)
        baseline_files = snapshot.get("files", {})
        current_files = {path.relative_to(site).as_posix(): digest(path) for path in site.rglob("*") if path.is_file()}
        for relative, entry in baseline_files.items():
            if relative not in current_files:
                preservation["removed"].append(relative)
            elif current_files[relative] == entry.get("sha256"):
                preservation["unchanged"] += 1
            elif relative in ALLOWED_CHANGED:
                preservation["allowed_changed"].append(relative)
            else:
                preservation["unexpected_changed"].append(relative)
        added = sorted(set(current_files) - set(baseline_files))
        unexpected_added = [item for item in added if item not in NEW_OUTPUTS and not item.startswith("qa/agi-alpha-node-v0")]
        preservation["added"] = added
        preservation["unexpected_added"] = unexpected_added
        check("preservation-no-removals", not preservation["removed"], preservation["removed"])
        check("preservation-no-unexpected-changes", not preservation["unexpected_changed"], preservation["unexpected_changed"])
        check("preservation-only-declared-additions", not unexpected_added, unexpected_added)
        check("preservation-declared-integration-surfaces", set(preservation["allowed_changed"]).issubset(ALLOWED_CHANGED), preservation["allowed_changed"])
        check("preservation-baseline-count", len(baseline_files) == snapshot.get("file_count"), {"listed": len(baseline_files), "declared": snapshot.get("file_count")})
    else:
        check("preservation-baseline-optional", True, "No baseline supplied; structural checks still applied.")

    failed = [item for item in checks if item["status"] == "FAIL"]
    report = {
        "schema": "goalos.agi_alpha_node_v0.static_qa.v2",
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
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.site / "qa" / "agi-alpha-node-v0-static.json"
    report = run(args.site.resolve(), args.root.resolve(), args.baseline.resolve() if args.baseline else None, output.resolve())
    print(json.dumps({"status": report["status"], "checks_total": report["checks_total"], "checks_passed": report["checks_passed"], "checks_failed": report["checks_failed"], "output": str(output)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
