#!/usr/bin/env python3
"""Verify GoalOS AGI Jobs v0 (v2) and its additive preservation boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"
PAGES = [
    "agi-jobs-v0-v2.html",
    "agi-jobs-v0-v2-market.html",
    "agi-jobs-v0-v2-settlement.html",
    "agi-jobs-v0-v2-memory.html",
    "agi-jobs-v0-v2-architecture.html",
]
DOWNLOADS = [
    "downloads/agi-jobs-v0-v2/sample-agi-jobs-evidence-docket.json",
    "downloads/agi-jobs-v0-v2/agi-jobs-v0-v2-economic-memory.json",
    "downloads/agi-jobs-v0-v2/agi-jobs-v0-v2-executive-review-brief.md",
]
NEW_OUTPUTS = {
    *PAGES,
    "agi-jobs-v0-v2-manifest.json",
    "assets/agi-jobs-v0-v2.css",
    "assets/agi-jobs-v0-v2.js",
    "data/agi-jobs-v0-v2.json",
    *DOWNLOADS,
    "qa/agi-jobs-v0-v2-build.json",
}
SHARED_INTEGRATION_OUTPUTS = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
COMPANION_MANIFEST_SCHEMAS = {
    "meta-agentic-alpha-agi-manifest.json": "goalos.meta_agentic_alpha_agi.website_manifest.v2",
    "agi-alpha-node-v0-manifest.json": "goalos.agi_alpha_node_v0.website_manifest.v2",
}
ALLOWED_CHANGED = SHARED_INTEGRATION_OUTPUTS | set(COMPANION_MANIFEST_SCHEMAS)
MARKERS = [
    "GOALOS_AGI_JOBS_V0_V2_STYLE_START",
    "GOALOS_AGI_JOBS_V0_V2_STYLE_END",
    "GOALOS_AGI_JOBS_V0_V2_NAV_START",
    "GOALOS_AGI_JOBS_V0_V2_NAV_END",
    "GOALOS_AGI_JOBS_V0_V2_HOME_START",
    "GOALOS_AGI_JOBS_V0_V2_HOME_END",
]
SOURCE_LINEAGE_ROOT = "ef43db8a6632192f9347083bf42f2c1cdbb6eb662f634408fde5139ea516d2a0"


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
    required_relatives = [
        *PAGES,
        "assets/agi-jobs-v0-v2.css",
        "assets/agi-jobs-v0-v2.js",
        "data/agi-jobs-v0-v2.json",
        *DOWNLOADS,
        "agi-jobs-v0-v2-manifest.json",
        "qa/agi-jobs-v0-v2-build.json",
    ]
    required = [site / item for item in required_relatives]
    for path in required:
        check(f"required-file:{path.relative_to(site).as_posix()}", path.is_file() and path.stat().st_size > 0, path.stat().st_size if path.is_file() else 0)
    if not all(path.is_file() for path in required):
        report = {"schema": "goalos.agi_jobs_v0_v2.static_qa.v3", "status": "FAIL", "checks": checks}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    data = load(site / "data" / "agi-jobs-v0-v2.json")
    docket = load(site / DOWNLOADS[0])
    memory = load(site / DOWNLOADS[1])
    manifest = load(site / "agi-jobs-v0-v2-manifest.json")
    build_report = load(site / "qa" / "agi-jobs-v0-v2-build.json")

    check("release-title", data.get("release_title") == RELEASE_TITLE, data.get("release_title"))
    check("release-id", data.get("release_id") == "GOALOS-AGIALPHA-AGI-JOBS-V0-V2-002", data.get("release_id"))
    check("release-version", data.get("version") == "3.0.0-sovereign-labor-civilization", data.get("version"))
    check("release-status", data.get("status") == "interactive-constitutional-ai-labor-economy-digital-twin", data.get("status"))
    expected_counts = {
        "hero_metrics": 6, "thesis": 7, "job_classes": 7, "presets": 8, "postures": 5, "risk_profiles": 4,
        "incidents": 7, "lifecycle": 14, "institutions": 12, "validators": 7, "guardians": 5, "guardrails": 10,
        "modules": 14, "job_archetypes": 16, "artifacts": 24, "architecture_translation": 16,
        "governance_principles": 10, "threats": 10, "memory_rules": 8, "economic_invariants": 8,
        "claim_boundary": 9, "lineage_fingerprints": 32,
    }
    for key, expected in expected_counts.items():
        value = data.get(key)
        check(f"count:{key}", isinstance(value, list) and len(value) == expected, len(value) if isinstance(value, list) else type(value).__name__)
    check("source-lineage-root", data.get("lineage_root") == SOURCE_LINEAGE_ROOT, data.get("lineage_root"))
    security = data.get("security", {})
    for key in ["external_dependencies", "api_keys", "wallet_connection", "network_reads", "network_writes", "live_compute", "live_token_movement"]:
        check(f"security:{key}-false", security.get(key) is False, security.get(key))
    check("security-human-review", security.get("human_review_required") is True, security)
    check("settlement-policy-total", sum(item.get("pct", 0) for item in data.get("settlement_policy", {}).get("allocations", [])) == 100, data.get("settlement_policy", {}).get("allocations"))

    check("docket-schema", docket.get("schema") == "goalos.agi_jobs_v0_v2.evidence_docket.v3", docket.get("schema"))
    check("docket-release", docket.get("release", {}).get("id") == data.get("release_id"), docket.get("release"))
    check("docket-ranked-twelve", len(docket.get("market", {}).get("ranked", [])) == 12, len(docket.get("market", {}).get("ranked", [])))
    coalition = docket.get("market", {}).get("coalition", {})
    check("docket-coalition-prime", bool(coalition.get("prime", {}).get("id")), coalition.get("prime"))
    check("docket-coalition-specialists-two", len(coalition.get("specialists", [])) == 2, coalition.get("specialists"))
    check("docket-coalition-shadow", bool(coalition.get("shadow", {}).get("id")), coalition.get("shadow"))
    check("docket-work-graph-eight", len(docket.get("work_graph", [])) == 8, len(docket.get("work_graph", [])))
    check("docket-validator-seven", len(docket.get("validator_parliament", {}).get("votes", [])) == 7, docket.get("validator_parliament", {}).get("summary"))
    check("docket-dissent-preserved", docket.get("validator_parliament", {}).get("dissent") == 1, docket.get("validator_parliament", {}).get("summary"))
    check("docket-guardians-five", len(docket.get("guardian_chamber", {}).get("seats", [])) == 5, docket.get("guardian_chamber", {}).get("summary"))
    check("docket-settlement-six-allocations", len(docket.get("settlement", {}).get("allocations", [])) == 6, docket.get("settlement", {}).get("allocations"))
    check("docket-contribution-ledger", len(docket.get("settlement", {}).get("contributions", [])) >= 4, docket.get("settlement", {}).get("contributions"))
    check("docket-live-token-zero", docket.get("settlement", {}).get("live_token_movement") is False, docket.get("settlement"))
    check("docket-wallet-zero", docket.get("settlement", {}).get("wallet_connections") == 0, docket.get("settlement"))
    check("docket-memory-human-pending", docket.get("memory_candidate", {}).get("status") == "HUMAN_APPROVAL_PENDING", docket.get("memory_candidate"))
    check("docket-memory-revocable", docket.get("memory_candidate", {}).get("revocable") is True, docket.get("memory_candidate"))
    chain = docket.get("proof_chronicle", {}).get("artifacts", [])
    check("docket-twenty-four-artifacts", len(chain) == 24, len(chain))
    previous = "0" * 64
    chain_valid = True
    for index, item in enumerate(chain, start=1):
        payload_hash = hashlib.sha256(stable_json(item.get("payload")).encode("utf-8")).hexdigest()
        expected = hashlib.sha256(f"{previous}:{payload_hash}:{item.get('name')}".encode("utf-8")).hexdigest()
        if item.get("index") != index or item.get("previous_commitment") != previous or item.get("artifact_hash") != payload_hash or item.get("commitment") != expected:
            chain_valid = False
            break
        previous = expected
    check("docket-chain-valid", chain_valid, previous)
    check("docket-chain-head", docket.get("proof_chronicle", {}).get("chain_head") == previous, docket.get("proof_chronicle", {}).get("chain_head"))
    terminal = docket.get("terminal", {})
    check("docket-terminal-human-settlement-review", terminal.get("state") == "HUMAN_SETTLEMENT_REVIEW", terminal)
    check("docket-authority-none", terminal.get("authority") == "NONE_GRANTED", terminal)
    check("docket-external-actions-zero", terminal.get("external_actions") == 0, terminal)
    check("docket-funds-no", terminal.get("funds_authorization") == "NO", terminal)
    check("economic-memory-schema", memory.get("schema") == "goalos.agi_jobs_v0_v2.economic_memory.v1", memory.get("schema"))
    check("economic-memory-human-only", memory.get("authority") == "HUMAN_ONLY" and memory.get("external_actions") == 0, memory)

    for page in PAGES:
        text = (site / page).read_text(encoding="utf-8")
        check(f"page-title:{page}", "AGI Jobs v0 (v2)" in text, text[:160])
        check(f"page-local-css:{page}", 'href="assets/agi-jobs-v0-v2.css"' in text, "")
        check(f"page-local-js:{page}", 'src="assets/agi-jobs-v0-v2.js"' in text, "")
        check(f"page-embedded-data:{page}", 'id="agi-jobs-data"' in text, "")
        check(f"page-no-remote-runtime:{page}", not re.search(r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://', text, re.I), "")
        check(f"page-csp-connect-none:{page}", "connect-src 'none'" in text, "")
    experience = (site / PAGES[0]).read_text(encoding="utf-8")
    for identifier in ["aj-stage-rail", "aj-institution-grid", "aj-artifact-grid", "aj-validator-grid", "aj-guardian-grid", "aj-workgraph"]:
        check(f"experience-surface:{identifier}", f'id="{identifier}"' in experience, "")
    check("experience-human-boundary", "NONE GRANTED" in experience and "HUMAN" in experience, "")
    memory_page = (site / "agi-jobs-v0-v2-memory.html").read_text(encoding="utf-8")
    check("memory-page-rules", 'id="aj-memory-rule-grid"' in memory_page, "")
    check("memory-page-candidates", 'id="aj-memory-candidates"' in memory_page, "")

    javascript = (site / "assets" / "agi-jobs-v0-v2.js").read_text(encoding="utf-8")
    check("runtime-terminal-states", all(value in javascript for value in ["HUMAN_SETTLEMENT_REVIEW", "HUMAN_REVIEW_REQUIRED", "SAFE_HOLD"]), "")
    check("runtime-no-network-api", not re.search(r"\bfetch\s*\(|XMLHttpRequest|WebSocket\s*\(", javascript), "")
    check("runtime-deterministic-sha256", "crypto.subtle.digest" in javascript and "sha256Fallback" in javascript, "")
    check("runtime-state-export", "window.__AGI_JOBS_STATE__" in javascript, "")
    check("runtime-downloads", all(value in javascript for value in ["agi-jobs-v0-v2-evidence-docket.json", "agi-jobs-v0-v2-executive-review-brief.md", "download("]), "")

    homepage = (site / "index.html").read_text(encoding="utf-8")
    for marker in MARKERS:
        check(f"homepage-marker-once:{marker}", homepage.count(marker) == 1, homepage.count(marker))
    check("homepage-gateway-once", homepage.count('id="agi-jobs-v0-v2"') == 1, homepage.count('id="agi-jobs-v0-v2"'))
    check("homepage-nav-link-once", homepage.count('href="agi-jobs-v0-v2.html">AGI Jobs</a>') == 1, homepage.count('href="agi-jobs-v0-v2.html">AGI Jobs</a>'))
    check("homepage-five-links", all(f'href="{page}"' in homepage for page in PAGES), "")
    routes = load(site / "routes.json")
    check("routes-all-pages", all(page in routes.get("routes", []) for page in PAGES), routes.get("agi_jobs_v0_v2"))
    status = load(site / "site-status.json")
    status_record = status.get("agi_jobs_v0_v2", {})
    check("site-status-record", status_record.get("evidence_artifacts") == 24 and status_record.get("guardian_seats") == 5, status_record)
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    check("sitemap-all-pages", all(page in sitemap for page in PAGES), "")

    check("manifest-schema", manifest.get("schema") == "goalos.agi_jobs_v0_v2.website_manifest.v3", manifest.get("schema"))
    check("manifest-release", manifest.get("release_title") == RELEASE_TITLE, manifest.get("release_title"))
    manifest_files = manifest.get("files", {})
    manifest_integrity = isinstance(manifest_files, dict) and bool(manifest_files)
    if manifest_integrity:
        for relative, record in manifest_files.items():
            target = site / relative
            if not target.is_file() or digest(target) != record.get("sha256") or target.stat().st_size != record.get("bytes"):
                manifest_integrity = False
                break
    check("manifest-hashes-valid", manifest_integrity, len(manifest_files) if isinstance(manifest_files, dict) else 0)

    for companion_name, expected_schema in COMPANION_MANIFEST_SCHEMAS.items():
        companion_path = site / companion_name
        if not companion_path.is_file():
            check(f"companion-optional:{companion_name}", True, "not installed")
            continue
        companion = load(companion_path)
        check(f"companion-schema:{companion_name}", companion.get("schema") == expected_schema, companion.get("schema"))
        files = companion.get("files", {})
        integrity = isinstance(files, dict) and bool(files)
        if integrity:
            for relative, record in files.items():
                target = site / relative
                if not isinstance(record, dict) or not target.is_file() or digest(target) != record.get("sha256") or target.stat().st_size != record.get("bytes"):
                    integrity = False
                    break
        check(f"companion-integrity:{companion_name}", integrity, len(files) if isinstance(files, dict) else 0)
        history = companion.get("integration", {}).get("reconciliations", [])
        check(f"companion-reconciliation:{companion_name}", isinstance(history, list) and any(isinstance(item, dict) and item.get("release_id") == data.get("release_id") for item in history), history)

    check("build-report-pass", build_report.get("status") == "PASS", build_report.get("status"))
    check("schema-file-present", schema is None or schema.is_file(), str(schema) if schema else "not supplied")
    if schema and schema.is_file():
        schema_data = load(schema)
        check("schema-id", schema_data.get("$id", "").endswith("agi-jobs-v0-v2-evidence-docket.schema.json"), schema_data.get("$id"))
        check("schema-v3", schema_data.get("properties", {}).get("schema", {}).get("const") == "goalos.agi_jobs_v0_v2.evidence_docket.v3", schema_data.get("properties", {}).get("schema"))
        required_keys = set(schema_data.get("required", []))
        check("schema-requires-governance", {"guardian_chamber", "memory_candidate", "terminal"}.issubset(required_keys), sorted(required_keys))

    preservation: dict[str, Any] = {"baseline_supplied": bool(baseline)}
    if baseline:
        snapshot = load(baseline)
        baseline_files = snapshot.get("files", {})
        current_files = file_inventory(site)
        try:
            current_files.pop(output.relative_to(site).as_posix(), None)
        except ValueError:
            pass
        removed = sorted(set(baseline_files) - set(current_files))
        changed = sorted(path for path in set(baseline_files) & set(current_files) if baseline_files[path].get("sha256") != current_files[path].get("sha256"))
        added = sorted(set(current_files) - set(baseline_files))
        unexpected_changed = sorted(set(changed) - ALLOWED_CHANGED)
        unexpected_added = sorted(set(added) - NEW_OUTPUTS)
        missing_additions = sorted(NEW_OUTPUTS - set(added))
        preservation.update({"removed": removed, "changed": changed, "added": added, "unexpected_changed": unexpected_changed, "unexpected_added": unexpected_added, "missing_additions": missing_additions})
        check("preservation-no-removals", not removed, removed)
        check("preservation-only-declared-changes", not unexpected_changed, unexpected_changed)
        check("preservation-only-declared-additions", not unexpected_added, unexpected_added)
        check("preservation-all-additions-present", not missing_additions, missing_additions)
        check("preservation-baseline-count", len(baseline_files) == snapshot.get("file_count"), {"listed": len(baseline_files), "declared": snapshot.get("file_count")})
    else:
        check("preservation-baseline-optional", True, "No baseline supplied; structural checks still applied.")

    source_root = root / "website" / "v86_actual_site"
    check("canonical-v86-source-present", source_root.is_dir(), str(source_root))
    forbidden_archives = [path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file() and path.suffix.lower() in {".zip", ".7z", ".rar", ".gz", ".tar"}]
    check("public-site-no-archives", not forbidden_archives, forbidden_archives)
    forbidden_secrets = []
    pattern = re.compile(r"PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY|SEED_PHRASE|MNEMONIC|MAINNET_RPC_URL=|ETHERSCAN_API_KEY=")
    for path in site.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".html", ".js", ".json", ".md", ".txt"}:
            try:
                if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                    forbidden_secrets.append(path.relative_to(site).as_posix())
            except OSError:
                pass
    check("public-site-no-private-operator-material", not forbidden_secrets, forbidden_secrets)

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
