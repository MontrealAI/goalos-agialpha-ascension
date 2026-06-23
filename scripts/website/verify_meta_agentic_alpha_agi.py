#!/usr/bin/env python3
"""Verify the generated GoalOS META-Agentic α-AGI flagship release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

RELEASE_TITLE = "GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨"
FEATURE_PAGES = ["meta-agentic-alpha-agi.html", "meta-agentic-alpha-agi-architecture.html"]
MARKERS = [
    "GOALOS_META_AGENTIC_ALPHA_AGI_STYLE_START",
    "GOALOS_META_AGENTIC_ALPHA_AGI_STYLE_END",
    "GOALOS_META_AGENTIC_ALPHA_AGI_NAV_START",
    "GOALOS_META_AGENTIC_ALPHA_AGI_NAV_END",
    "GOALOS_META_AGENTIC_ALPHA_AGI_HOME_START",
    "GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END",
]


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []
        self.scripts: list[str] = []
        self.stylesheets: list[str] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs if value is not None}
        for key in ("href", "src"):
            if key in values:
                self.references.append((key, values[key]))
        if values.get("id"):
            self.ids.append(values["id"])
        if tag.lower() == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if tag.lower() == "link" and "stylesheet" in values.get("rel", "").lower() and values.get("href"):
            self.stylesheets.append(values["href"])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check(condition: bool, label: str, checks: list[dict[str, Any]], detail: str = "") -> None:
    checks.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})


def local_target(site: Path, page: Path, reference: str) -> Path | None:
    split = urlsplit(reference)
    if split.scheme or split.netloc or reference.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    path = unquote(split.path)
    if not path:
        return None
    target = (page.parent / path).resolve()
    try:
        target.relative_to(site.resolve())
    except ValueError:
        return Path("/__OUTSIDE_SITE__")
    return target


def finish(site: Path, checks: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [item for item in checks if item["status"] != "PASS"]
    report = {
        "schema": "goalos.meta_agentic_alpha_agi.website_verification.v2",
        "release_title": RELEASE_TITLE,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "checks": checks,
    }
    write_json(site / "qa" / "meta-agentic-alpha-agi-verification.json", report)
    lines = [
        "# GoalOS META-Agentic α-AGI Verification",
        "",
        f"**Status:** {report['status']}",
        f"**Checks:** {report['checks_passed']}/{report['checks_total']} passed",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    for item in checks:
        detail = str(item.get("detail", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item['label']} | {item['status']} | {detail} |")
    (site / "qa").mkdir(parents=True, exist_ok=True)
    (site / "qa" / "meta-agentic-alpha-agi-verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def verify(site: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    required = [
        *FEATURE_PAGES,
        "assets/meta-agentic-alpha-agi.css",
        "assets/meta-agentic-alpha-agi.js",
        "assets/goalos-v86-preserve.css",
        "assets/goalos-v86-dynamic-ai.js",
        "data/meta-agentic-alpha-agi.json",
        "meta-agentic-alpha-agi-manifest.json",
        "index.html",
        "routes.json",
        "sitemap.xml",
        "site-status.json",
    ]
    missing = [relative for relative in required if not (site / relative).is_file()]
    check(not missing, "required-files", checks, "missing: " + ", ".join(missing) if missing else f"{len(required)} required files present")
    if missing:
        return finish(site, checks)

    data = load_json(site / "data" / "meta-agentic-alpha-agi.json")
    check(isinstance(data, dict), "release-data-object", checks)
    if not isinstance(data, dict):
        return finish(site, checks)
    check(data.get("release_title") == RELEASE_TITLE, "exact-release-title", checks, str(data.get("release_title")))
    check(data.get("version") == "2.0.0-ascension-alpha", "release-version-v2", checks, str(data.get("version")))
    expected_lengths = {
        "hero_metrics": 4,
        "thesis": 3,
        "mission_flow": 8,
        "agents": 9,
        "objectives": 5,
        "artifacts": 16,
        "presets": 4,
        "risk_postures": 3,
        "architecture_translation": 6,
        "governance_principles": 6,
        "claim_boundary": 6,
    }
    for key, expected in expected_lengths.items():
        value = data.get(key)
        observed = len(value) if isinstance(value, list) else "not-list"
        check(isinstance(value, list) and len(value) == expected, f"data-{key}", checks, f"expected {expected}; observed {observed}")

    engine = data.get("candidate_engine", {})
    engine_ok = (
        isinstance(engine, dict)
        and engine.get("generations") == 4
        and engine.get("population_per_generation") == 6
        and all(isinstance(engine.get(key), list) and len(engine[key]) == 6 for key in ["topologies", "reasoning_modes", "verifier_models", "governance_models", "memory_models", "execution_models"])
        and isinstance(engine.get("mutation_operators"), list)
        and len(engine["mutation_operators"]) >= 8
    )
    check(engine_ok, "candidate-engine-contract", checks, json.dumps(engine, ensure_ascii=False, sort_keys=True))

    objective_ids = [item.get("id") for item in data.get("objectives", []) if isinstance(item, dict)]
    check(objective_ids == ["evidence", "utility", "safety", "efficiency", "novelty"], "five-objective-contract", checks, ", ".join(objective_ids))
    weight_failures: list[str] = []
    for posture in data.get("risk_postures", []):
        weights = posture.get("weights", {}) if isinstance(posture, dict) else {}
        if set(weights) != set(objective_ids) or abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
            weight_failures.append(str(posture.get("id")))
    check(not weight_failures, "posture-weight-contract", checks, ", ".join(weight_failures) if weight_failures else "all posture weights cover five objectives and sum to 1")

    security = data.get("security", {})
    expected_security = {
        "external_dependencies": False,
        "api_keys": False,
        "wallet_connection": False,
        "network_writes": False,
        "local_storage": False,
        "human_review_required": True,
        "settlement_mode": "none",
    }
    check(isinstance(security, dict) and all(security.get(key) == value for key, value in expected_security.items()), "security-boundary-data", checks, json.dumps(security, ensure_ascii=False, sort_keys=True))

    page_requirements = {
        "meta-agentic-alpha-agi.html": [
            RELEASE_TITLE,
            'data-maa-page="experience"',
            'id="maa-mission-form"',
            'id="maa-lineage-svg"',
            'id="maa-pareto-svg"',
            'id="maa-candidate-list"',
            'id="maa-constitution-list"',
            'id="maa-download"',
            'id="maa-download-md"',
            'id="maa-boundary-list"',
            "Content-Security-Policy",
            "assets/goalos-v86-preserve.css",
            "assets/meta-agentic-alpha-agi.css",
            "assets/meta-agentic-alpha-agi.js",
            "assets/goalos-v86-dynamic-ai.js",
            'id="goalos-v86-critical"',
        ],
        "meta-agentic-alpha-agi-architecture.html": [
            RELEASE_TITLE,
            'data-maa-page="architecture"',
            'id="maa-translation-map"',
            'id="maa-architecture-stages"',
            'id="maa-architecture-agents"',
            'id="maa-governance-grid"',
            'id="lineage-map"',
            'id="governance"',
            "Content-Security-Policy",
            "assets/goalos-v86-preserve.css",
            "assets/meta-agentic-alpha-agi.js",
            'id="goalos-v86-critical"',
        ],
    }
    parsed_pages: dict[str, ReferenceParser] = {}
    for filename, required_text in page_requirements.items():
        path = site / filename
        text = path.read_text(encoding="utf-8")
        absent = [token for token in required_text if token not in text]
        check(not absent, f"page-contract-{filename}", checks, "missing: " + ", ".join(absent) if absent else "all required elements present")
        check("@@" not in text, f"template-resolved-{filename}", checks)
        check(len(re.sub(r"<[^>]+>", " ", text).split()) >= 300, f"substantive-content-{filename}", checks, "at least 300 text tokens")
        parser = ReferenceParser()
        parser.feed(text)
        parsed_pages[filename] = parser
        duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        check(not duplicate_ids, f"unique-dom-ids-{filename}", checks, ", ".join(duplicate_ids) if duplicate_ids else f"{len(parser.ids)} unique ids")
        bad_scripts = [src for src in parser.scripts if urlsplit(src).scheme or urlsplit(src).netloc]
        check(not bad_scripts, f"local-scripts-{filename}", checks, ", ".join(bad_scripts) if bad_scripts else "all scripts are local")
        broken: list[str] = []
        for _, reference in parser.references:
            target = local_target(site, path, reference)
            if target is not None and not target.exists():
                broken.append(reference)
        check(not broken, f"local-links-{filename}", checks, ", ".join(sorted(set(broken))) if broken else "all local references resolve")

    javascript = (site / "assets" / "meta-agentic-alpha-agi.js").read_text(encoding="utf-8")
    stylesheet = (site / "assets" / "meta-agentic-alpha-agi.css").read_text(encoding="utf-8")
    forbidden_js = {
        "dynamic-code-eval": r"\beval\s*\(|\bnew\s+Function\s*\(",
        "persistent-browser-storage": r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b",
        "wallet-provider": r"window\.ethereum|eth_requestAccounts|wallet_requestPermissions",
        "external-network-target": r"https?://|wss?://",
        "secret-material": r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|sk-[A-Za-z0-9]{20,}",
        "websocket-or-event-source": r"\bWebSocket\s*\(|\bEventSource\s*\(",
    }
    network_safe_javascript = javascript.replace("http://www.w3.org/2000/svg", "")
    for label, pattern in forbidden_js.items():
        scan_target = network_safe_javascript if label == "external-network-target" else javascript
        match = re.search(pattern, scan_target, flags=re.IGNORECASE)
        check(match is None, f"js-{label}", checks, match.group(0) if match else "not present")
    required_js = [
        "createCandidatePopulation",
        "dominates",
        "markParetoFrontier",
        "selectCandidate",
        "renderLineageGraph",
        "renderParetoPlot",
        "goalos.meta_agentic_alpha_agi.evidence_docket.v2",
        "deterministic_seed",
        "HUMAN_REVIEW_READY",
        "factual_correctness: 'NOT_CERTIFIED'",
        "external_actions: 0",
        "authority: 'NONE_GRANTED'",
        "population_per_generation",
    ]
    absent_js = [token for token in required_js if token not in javascript]
    check(not absent_js, "js-institution-foundry-contract", checks, "missing: " + ", ".join(absent_js) if absent_js else "candidate evolution, Pareto selection, docket v2, and authorization boundary present")
    check(javascript.count("fetch(") == 1 and "fetch(DATA_URL" in javascript, "single-local-data-fetch", checks, f"fetch-count={javascript.count('fetch(')}")
    check("@import" not in stylesheet and not re.search(r"url\(\s*['\"]?https?://", stylesheet, flags=re.IGNORECASE), "css-no-external-runtime-assets", checks)
    check("prefers-reduced-motion" in stylesheet and ":focus-visible" in stylesheet, "css-accessibility-contract", checks, "reduced motion and keyboard focus styles present")
    check("@media (max-width:1020px)" in stylesheet and "@media (max-width:720px)" in stylesheet, "css-responsive-contract", checks, "desktop, tablet, and mobile breakpoints present")

    index = (site / "index.html").read_text(encoding="utf-8")
    bad_marker_counts = {marker: index.count(marker) for marker in MARKERS if index.count(marker) != 1}
    check(not bad_marker_counts, "homepage-idempotent-markers", checks, json.dumps(bad_marker_counts, sort_keys=True) if bad_marker_counts else "six markers appear exactly once")
    check('href="meta-agentic-alpha-agi.html"' in index and 'class="maa-home-gateway"' in index and "Institution Foundry" in index, "homepage-flagship-entry-point", checks)
    check(index.count("assets/meta-agentic-alpha-agi.css") == 1, "homepage-single-feature-stylesheet", checks, f"count={index.count('assets/meta-agentic-alpha-agi.css')}")

    routes = load_json(site / "routes.json")
    route_values = routes.get("routes", []) if isinstance(routes, dict) else []
    route_meta = routes.get("meta_agentic_alpha_agi", {}) if isinstance(routes, dict) else {}
    check(all(page in route_values for page in FEATURE_PAGES), "routes-registered", checks, ", ".join(FEATURE_PAGES))
    check(route_meta.get("runtime") == "deterministic-local-institution-foundry" and route_meta.get("version") == data.get("version"), "routes-feature-metadata", checks, json.dumps(route_meta, ensure_ascii=False, sort_keys=True))

    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_counts = {page: sitemap.count(f"./{page}") for page in FEATURE_PAGES}
    check(all(count == 1 for count in sitemap_counts.values()), "sitemap-registered-once", checks, json.dumps(sitemap_counts, sort_keys=True))

    status = load_json(site / "site-status.json")
    status_feature = status.get("meta_agentic_alpha_agi", {}) if isinstance(status, dict) else {}
    status_ok = (
        status_feature.get("release_title") == RELEASE_TITLE
        and status_feature.get("version") == data.get("version")
        and status_feature.get("status") == "interactive-institution-foundry"
        and status_feature.get("candidate_population") == 24
        and status_feature.get("pareto_selection") is True
        and status_feature.get("human_review_required") is True
        and status_feature.get("external_actions") == 0
    )
    check(status_ok, "site-status-feature", checks, json.dumps(status_feature, ensure_ascii=False, sort_keys=True))
    root_count = len(list(site.glob("*.html")))
    all_count = len(list(site.rglob("*.html")))
    check(status.get("root_html_pages") == root_count and status.get("published_html_pages_including_resources") == all_count, "site-status-page-counts", checks, f"root={root_count}; all={all_count}")

    manifest = load_json(site / "meta-agentic-alpha-agi-manifest.json")
    check(isinstance(manifest, dict) and manifest.get("schema") == "goalos.meta_agentic_alpha_agi.website_manifest.v2", "manifest-v2-schema", checks, str(manifest.get("schema") if isinstance(manifest, dict) else None))
    manifest_files = manifest.get("files", {}) if isinstance(manifest, dict) else {}
    manifest_failures: list[str] = []
    for relative, metadata in manifest_files.items():
        path = site / relative
        if not path.is_file():
            manifest_failures.append(f"missing:{relative}")
        elif not isinstance(metadata, dict) or metadata.get("sha256") != sha256(path) or metadata.get("bytes") != path.stat().st_size:
            manifest_failures.append(f"mismatch:{relative}")
    check(bool(manifest_files) and not manifest_failures, "manifest-integrity", checks, ", ".join(manifest_failures) if manifest_failures else f"{len(manifest_files)} hashes verified")
    integration = manifest.get("integration", {}) if isinstance(manifest, dict) else {}
    experience = manifest.get("experience", {}) if isinstance(manifest, dict) else {}
    check(integration.get("mode") == "additive-post-build" and integration.get("canonical_v86_source_modified") is False, "manifest-preservation-contract", checks, json.dumps(integration, sort_keys=True))
    check(experience.get("default_population") == 24 and experience.get("selection") == "pareto-frontier-plus-posture-weighting" and experience.get("human_authorization_required") is True, "manifest-experience-contract", checks, json.dumps(experience, ensure_ascii=False, sort_keys=True))

    archive_suffixes = {".zip", ".tar", ".gz", ".7z", ".rar"}
    archives = [path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file() and path.suffix.lower() in archive_suffixes]
    check(not archives, "no-archives-in-public-site", checks, ", ".join(archives) if archives else "none")
    suspicious = [path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file() and any(part.lower() in {"private", "secrets", ".env", "node_modules"} for part in path.parts)]
    check(not suspicious, "no-private-material-in-public-site", checks, ", ".join(suspicious) if suspicious else "none")

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
