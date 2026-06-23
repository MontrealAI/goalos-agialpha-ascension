#!/usr/bin/env python3
"""Statically verify GoalOS AGIALPHA Ascension AGI Alpha Node v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨"
FEATURE_PAGES = ["agi-alpha-node-v0.html", "agi-alpha-node-v0-architecture.html"]
NODE_MARKERS = [
    "GOALOS_AGI_ALPHA_NODE_V0_STYLE_START",
    "GOALOS_AGI_ALPHA_NODE_V0_STYLE_END",
    "GOALOS_AGI_ALPHA_NODE_V0_NAV_START",
    "GOALOS_AGI_ALPHA_NODE_V0_NAV_END",
    "GOALOS_AGI_ALPHA_NODE_V0_HOME_START",
    "GOALOS_AGI_ALPHA_NODE_V0_HOME_END",
]
META_MARKERS = [
    "GOALOS_META_AGENTIC_ALPHA_AGI_STYLE_START",
    "GOALOS_META_AGENTIC_ALPHA_AGI_STYLE_END",
    "GOALOS_META_AGENTIC_ALPHA_AGI_NAV_START",
    "GOALOS_META_AGENTIC_ALPHA_AGI_NAV_END",
    "GOALOS_META_AGENTIC_ALPHA_AGI_HOME_START",
    "GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END",
]


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.scripts: list[str] = []
        self.styles: list[str] = []
        self.meta_csp: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.references.append((attribute, values[attribute]))
        if tag.lower() == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if tag.lower() == "link" and values.get("rel", "").lower() == "stylesheet" and values.get("href"):
            self.styles.append(values["href"])
        if tag.lower() == "meta" and values.get("http-equiv", "").lower() == "content-security-policy":
            self.meta_csp.append(values.get("content", ""))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition: bool, label: str, checks: list[dict[str, Any]], detail: Any = "") -> None:
    checks.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})


def local_target(site: Path, page: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    target = (page.parent / path).resolve()
    try:
        target.relative_to(site.resolve())
    except ValueError:
        return target
    return target


def finish(site: Path, checks: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [item for item in checks if item["status"] != "PASS"]
    report = {
        "schema": "goalos.agi_alpha_node_v0.static_verification.v1",
        "release_title": RELEASE_TITLE,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "checks": checks,
    }
    qa = site / "qa"
    write_json(qa / "agi-alpha-node-v0-static-verify.json", report)
    lines = [
        "# AGI Alpha Node v0 static verification",
        "",
        f"**Status:** {report['status']}",
        f"**Checks:** {report['checks_passed']} / {report['checks_total']} passed",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    for item in checks:
        detail = str(item.get("detail", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item['label']} | {item['status']} | {detail} |")
    (qa / "agi-alpha-node-v0-static-verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def verify(site: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    required = [
        *FEATURE_PAGES,
        "assets/agi-alpha-node-v0.css",
        "assets/agi-alpha-node-v0.js",
        "data/agi-alpha-node-v0.json",
        "agi-alpha-node-v0-manifest.json",
        "index.html",
        "routes.json",
        "sitemap.xml",
        "site-status.json",
    ]
    missing = [relative for relative in required if not (site / relative).is_file()]
    check(not missing, "required-files", checks, "missing: " + ", ".join(missing) if missing else f"{len(required)} required files present")
    if missing:
        return finish(site, checks)

    data = load_json(site / "data" / "agi-alpha-node-v0.json")
    check(isinstance(data, dict), "release-data-object", checks)
    if not isinstance(data, dict):
        return finish(site, checks)
    check(data.get("release_title") == RELEASE_TITLE, "exact-release-title", checks, data.get("release_title"))
    check(data.get("version") == "1.0.0-ascension-alpha", "release-version", checks, data.get("version"))
    check(data.get("status") == "interactive-sovereign-node-simulation", "release-status", checks, data.get("status"))

    expected_lengths = {
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
    for key, expected in expected_lengths.items():
        value = data.get(key)
        observed = len(value) if isinstance(value, list) else "not-list"
        check(isinstance(value, list) and len(value) == expected, f"data-{key}", checks, f"expected {expected}; observed {observed}")

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
    states = [item.get("state") for item in data.get("pipeline", []) if isinstance(item, dict)]
    check(states == expected_states, "eight-state-order", checks, states)
    class_ids = [item.get("id") for item in data.get("work_unit_classes", []) if isinstance(item, dict)]
    check(class_ids == ["reason", "build", "verify", "orchestrate"], "work-class-order", checks, class_ids)
    role_symbols = [item.get("symbol") for item in data.get("node_roles", []) if isinstance(item, dict)]
    check(role_symbols == ["ID", "OR", "RG", "EX", "QT", "V7", "G5", "CH"], "node-role-constellation", checks, role_symbols)

    weight_failures: list[str] = []
    expected_weight_keys = {"quality", "reliability", "energy", "latency", "evidence"}
    for posture in data.get("postures", []):
        weights = posture.get("weights", {}) if isinstance(posture, dict) else {}
        if set(weights) != expected_weight_keys or abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
            weight_failures.append(str(posture.get("id")))
    check(not weight_failures, "posture-weight-contract", checks, weight_failures or "all five-dimensional weights sum to 1")

    security = data.get("security", {})
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
    for key, expected in expected_security.items():
        check(isinstance(security, dict) and security.get(key) == expected, f"security-{key}", checks, security.get(key) if isinstance(security, dict) else "not-object")

    page_requirements = {
        "agi-alpha-node-v0.html": [
            RELEASE_TITLE,
            'id="aan-node-form"',
            'id="aan-stage-rail"',
            'id="aan-mesh-svg"',
            'id="aan-peer-table"',
            'id="aan-validator-grid"',
            'id="aan-artifact-list"',
            'id="aan-download-json"',
            'id="aan-release-data"',
            "Content-Security-Policy",
            "connect-src 'none'",
            "assets/agi-alpha-node-v0.css",
            "assets/agi-alpha-node-v0.js",
        ],
        "agi-alpha-node-v0-architecture.html": [
            RELEASE_TITLE,
            'id="aan-system-map"',
            'id="aan-translation-grid"',
            'id="aan-arch-pipeline"',
            'id="aan-boundary-list"',
            'id="aan-release-data"',
            "Content-Security-Policy",
            "connect-src 'none'",
            "assets/agi-alpha-node-v0.css",
            "assets/agi-alpha-node-v0.js",
        ],
    }
    for filename, tokens in page_requirements.items():
        path = site / filename
        text = path.read_text(encoding="utf-8")
        missing_tokens = [token for token in tokens if token not in text]
        check(not missing_tokens, f"page-contract-{filename}", checks, missing_tokens or "all required tokens present")
        check("@@" not in text, f"template-resolved-{filename}", checks)
        word_count = len(re.sub(r"<[^>]+>", " ", text).split())
        check(word_count >= 260, f"substantive-content-{filename}", checks, word_count)
        parser = ReferenceParser()
        parser.feed(text)
        duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        check(not duplicate_ids, f"unique-dom-ids-{filename}", checks, duplicate_ids or len(parser.ids))
        check(len(parser.meta_csp) == 1 and "connect-src 'none'" in parser.meta_csp[0], f"strict-csp-{filename}", checks, parser.meta_csp)
        external_scripts = [value for value in parser.scripts if urlsplit(value).scheme or urlsplit(value).netloc]
        external_styles = [value for value in parser.styles if urlsplit(value).scheme or urlsplit(value).netloc]
        check(not external_scripts, f"local-scripts-{filename}", checks, external_scripts or parser.scripts)
        check(not external_styles, f"local-styles-{filename}", checks, external_styles or parser.styles)
        broken: list[str] = []
        for _, reference in parser.references:
            target = local_target(site, path, reference)
            if target is not None and not target.exists():
                broken.append(reference)
        check(not broken, f"local-links-{filename}", checks, sorted(set(broken)) or "all local references resolve")

    javascript = (site / "assets" / "agi-alpha-node-v0.js").read_text(encoding="utf-8")
    stylesheet = (site / "assets" / "agi-alpha-node-v0.css").read_text(encoding="utf-8")
    safe_javascript = javascript.replace("http://www.w3.org/2000/svg", "")
    forbidden_js = {
        "dynamic-code-eval": r"\beval\s*\(|\bnew\s+Function\s*\(",
        "network-api": r"\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\s*\(|\bEventSource\s*\(",
        "persistent-storage": r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b",
        "wallet-provider": r"window\.ethereum|eth_requestAccounts|wallet_requestPermissions",
        "external-network-target": r"https?://|wss?://",
        "secret-material": r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|sk-[A-Za-z0-9]{20,}|MNEMONIC|SEED_PHRASE",
        "document-write": r"document\.write\s*\(",
    }
    for label, pattern in forbidden_js.items():
        match = re.search(pattern, safe_javascript if label == "external-network-target" else javascript, flags=re.IGNORECASE)
        check(match is None, f"js-{label}", checks, match.group(0) if match else "not present")

    required_js_tokens = [
        "createPeerRoute",
        "calculateAlphaWorkUnit",
        "createValidatorConsensus",
        "buildNodeEvidenceDocket",
        "goalos.agi_alpha_node_v0.node_evidence_docket.v1",
        "HUMAN_REVIEW_REQUIRED",
        "external_actions: 0",
        "authority: 'NONE_GRANTED'",
        "factual_correctness: 'NOT_CERTIFIED'",
        "deterministic_seed",
        "dissent_preserved",
        "external_compute_calls: 0",
        "external_connections: 0",
        "authority_conferred: false",
    ]
    for token in required_js_tokens:
        check(token in javascript, f"js-capability-{re.sub(r'[^a-z0-9]+', '-', token.lower()).strip('-')[:60]}", checks, token)
    check(javascript.count("runtime.runToken") >= 5, "runtime-cancellation-boundary", checks, javascript.count("runtime.runToken"))
    check("Blob" in javascript and "URL.createObjectURL" in javascript, "local-evidence-export", checks)

    required_css_tokens = [
        ".aan-home-gateway",
        ".aan-stage.is-complete",
        ".aan-mesh-node.accepted",
        ".aan-validator-card.dissent",
        ".aan-artifact-ledger li.sealed",
        "@media (max-width:980px)",
        "@media (max-width:640px)",
        "prefers-reduced-motion",
        ":focus-visible",
    ]
    for token in required_css_tokens:
        check(token in stylesheet, f"css-contract-{re.sub(r'[^a-z0-9]+', '-', token.lower()).strip('-')[:50]}", checks, token)

    index_text = (site / "index.html").read_text(encoding="utf-8")
    for marker in NODE_MARKERS:
        check(index_text.count(marker) == 1, f"homepage-node-marker-{marker.lower()}", checks, index_text.count(marker))
    check(index_text.count('href="agi-alpha-node-v0.html"') >= 2, "homepage-node-links", checks, index_text.count('href="agi-alpha-node-v0.html"'))
    check('id="agi-alpha-node-v0"' in index_text and "SOVEREIGN PROOF NODE" in index_text, "homepage-gateway-contract", checks)
    meta_present = any(marker in index_text for marker in META_MARKERS)
    check(meta_present, "meta-agentic-integration-preserved", checks, "present" if meta_present else "missing")
    if meta_present:
        for marker in META_MARKERS:
            check(index_text.count(marker) == 1, f"homepage-meta-marker-preserved-{marker.lower()}", checks, index_text.count(marker))

    routes = load_json(site / "routes.json")
    route_list = routes.get("routes", []) if isinstance(routes, dict) else []
    check(all(page in route_list for page in FEATURE_PAGES), "routes-feature-pages", checks, route_list)
    route_metadata = routes.get("agi_alpha_node_v0", {}) if isinstance(routes, dict) else {}
    check(route_metadata.get("external_actions") == 0 and route_metadata.get("pages") == FEATURE_PAGES, "routes-feature-metadata", checks, route_metadata)

    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    for page in FEATURE_PAGES:
        check(sitemap.count(f"./{page}") == 1, f"sitemap-{page}", checks, sitemap.count(f"./{page}"))

    status = load_json(site / "site-status.json")
    node_status = status.get("agi_alpha_node_v0", {}) if isinstance(status, dict) else {}
    check(node_status.get("status") == "interactive-sovereign-node-simulation", "site-status-release", checks, node_status)
    check(node_status.get("external_actions") == 0 and node_status.get("human_review_required") is True, "site-status-boundary", checks, node_status)

    manifest = load_json(site / "agi-alpha-node-v0-manifest.json")
    check(manifest.get("schema") == "goalos.agi_alpha_node_v0.website_manifest.v1", "manifest-schema", checks, manifest.get("schema"))
    check(manifest.get("release_title") == RELEASE_TITLE, "manifest-title", checks, manifest.get("release_title"))
    experience = manifest.get("experience", {}) if isinstance(manifest, dict) else {}
    check(experience.get("final_state") == "HUMAN_REVIEW_REQUIRED" and experience.get("external_actions") == 0, "manifest-authority-boundary", checks, experience)
    manifest_files = manifest.get("files", {}) if isinstance(manifest, dict) else {}
    hash_failures: list[str] = []
    if isinstance(manifest_files, dict):
        for relative, record in manifest_files.items():
            path = site / relative
            if not path.is_file() or not isinstance(record, dict) or sha256(path) != record.get("sha256") or path.stat().st_size != record.get("bytes"):
                hash_failures.append(relative)
    else:
        hash_failures.append("manifest.files-not-object")
    check(not hash_failures, "manifest-file-integrity", checks, hash_failures or f"{len(manifest_files)} files match")

    archive_files = sorted(path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file() and path.suffix.lower() in {".zip", ".7z", ".tar", ".gz", ".rar"})
    check(not archive_files, "no-public-archives", checks, archive_files or "none")
    sensitive_pattern = re.compile(r"PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY|SEED_PHRASE|MNEMONIC|MAINNET_RPC_URL=|ETHERSCAN_API_KEY=")
    sensitive_hits: list[str] = []
    for path in [site / "agi-alpha-node-v0.html", site / "agi-alpha-node-v0-architecture.html", site / "assets" / "agi-alpha-node-v0.js", site / "data" / "agi-alpha-node-v0.json"]:
        if sensitive_pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
            sensitive_hits.append(path.relative_to(site).as_posix())
    check(not sensitive_hits, "no-private-material", checks, sensitive_hits or "none")

    return finish(site, checks)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = verify(args.site.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
