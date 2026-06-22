#!/usr/bin/env python3
"""Verify the additive Proof Gradient Apex website overlay."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

START = "<!-- GOALOS_PROOF_GRADIENT_APEX_START -->"
END = "<!-- GOALOS_PROOF_GRADIENT_APEX_END -->"
STYLE_START = "<!-- GOALOS_PROOF_GRADIENT_APEX_STYLE_START -->"
STYLE_END = "<!-- GOALOS_PROOF_GRADIENT_APEX_STYLE_END -->"
FORBIDDEN_ARCHIVES = {".zip", ".7z", ".tar", ".gz", ".rar"}
FORBIDDEN_SECRETS = ["PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY", "MNEMONIC", "SEED_PHRASE", "MAINNET_RPC_URL=", "ETHERSCAN_API_KEY="]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))




def manifest_contract_map(manifest):
    raw = manifest.get("contracts")
    if isinstance(raw, dict):
        return {str(name): str(address) for name, address in raw.items()}
    if isinstance(raw, list):
        return {str(item["name"]): str(item["address"]) for item in raw if isinstance(item, dict) and item.get("name") and item.get("address")}
    return {}

def local_targets(raw: str) -> list[str]:
    return re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", raw, re.I)


def verify(site: Path, content_path: Path, manifest_path: Path) -> tuple[dict, int]:
    errors: list[str] = []
    warnings: list[str] = []
    content = read_json(content_path)
    manifest = read_json(manifest_path)
    page = site / "proof-gradient-challenge.html"
    home = site / "index.html"
    build_report_path = site / "qa" / "proof-gradient-apex-build.json"

    for path in [page, home, build_report_path, site / "downloads/proof-gradient/goalos-mainnet-contract-addresses.csv", site / "downloads/proof-gradient/proof-gradient-mainnet-map.json", site / "downloads/proof-gradient/proof-gradient-mission.json", site / "downloads/proof-gradient/proof-gradient-simulation-summary.json"]:
        if not path.exists():
            errors.append(f"missing generated file: {path.relative_to(site) if path.is_relative_to(site) else path}")

    page_raw = page.read_text(encoding="utf-8", errors="ignore") if page.exists() else ""
    home_raw = home.read_text(encoding="utf-8", errors="ignore") if home.exists() else ""

    required_page_fragments = [
        "The Proof Gradient",
        content["missionId"],
        "Synthetic design stress test",
        "Same engine. Same objective. Same compute. One difference: proof governance.",
        "All 48 GoalOS-created Ethereum Mainnet contracts",
        "assets/goalos-v86-preserve.css",
        "assets/goalos-v86-dynamic-ai.js",
        "goalos-v86-critical",
        "proof-gradient-mainnet-map.json",
        "href='ethereum-mainnet.html'",
        "aria-current='page'",
    ]
    for fragment in required_page_fragments:
        if fragment not in page_raw:
            errors.append(f"proof-gradient-challenge.html missing required content: {fragment}")

    if home_raw.count(START) != 1 or home_raw.count(END) != 1:
        errors.append("homepage Proof Gradient feature marker is missing or duplicated")
    if home_raw.count(STYLE_START) != 1 or home_raw.count(STYLE_END) != 1:
        errors.append("homepage Proof Gradient style marker is missing or duplicated")
    if "href='proof-gradient-challenge.html'" not in home_raw and 'href="proof-gradient-challenge.html"' not in home_raw:
        errors.append("homepage does not link to proof-gradient-challenge.html")
    if "href='ethereum-mainnet.html'" not in home_raw and 'href="ethereum-mainnet.html"' not in home_raw:
        errors.append("homepage Proof Gradient feature does not link to ethereum-mainnet.html")
    home_button_count = home_raw.count("class='pg-home-button") + home_raw.count('class="pg-home-button')
    if home_button_count != 3:
        errors.append(f"homepage Proof Gradient feature must contain three actions, found {home_button_count}")

    contracts = manifest_contract_map(manifest)
    if len(contracts) != 49:
        errors.append(f"manifest entry count is {len(contracts)}, expected 49")
    created = {name: address for name, address in contracts.items() if name != "AGIALPHA"}
    if len(created) != 48:
        errors.append(f"GoalOS-created contract count is {len(created)}, expected 48")
    for name, address in created.items():
        if name not in page_raw:
            errors.append(f"page missing contract name: {name}")
        if address.lower() not in page_raw.lower():
            errors.append(f"page missing contract address: {name} {address}")
        if f"https://etherscan.io/address/{address}".lower() not in page_raw.lower():
            errors.append(f"page missing Etherscan address link: {name}")

    if page_raw.lower().count("class='pg-contract'") + page_raw.lower().count('class="pg-contract"') != 48:
        errors.append("generated page does not contain exactly 48 contract cards")

    if build_report_path.exists():
        report = read_json(build_report_path)
        if report.get("status") != "PASS":
            errors.append("overlay build report is not PASS")
        if report.get("canonicalSourceModified") is not False:
            errors.append("overlay build report does not prove canonical source preservation")
        if report.get("removedGeneratedFiles"):
            errors.append("overlay build report records removed generated files")
        if report.get("unexpectedModifiedFiles"):
            errors.append("overlay build report records unexpected modifications")
        allowed_modified = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
        def overlay_owned(path):
            return path == "proof-gradient-challenge.html" or path.startswith("downloads/proof-gradient/") or path.startswith("qa/proof-gradient-")
        unexpected = {path for path in report.get("modifiedExistingGeneratedFiles", []) if path not in allowed_modified and not overlay_owned(path)}
        if unexpected:
            errors.append("unexpected existing generated files changed: " + ", ".join(sorted(unexpected)))
        if report.get("publicNetworkTransactionSent") is not False:
            errors.append("overlay report does not assert zero public-network transactions")

    map_path = site / "downloads/proof-gradient/proof-gradient-mainnet-map.json"
    if map_path.exists():
        public_map = read_json(map_path)
        if public_map.get("chainId") != 1:
            errors.append("public Mainnet map has wrong chainId")
        if public_map.get("goalosCreatedContractCount") != 48:
            errors.append("public Mainnet map has wrong GoalOS-created count")
        if len(public_map.get("contracts", [])) != 49:
            errors.append("public Mainnet map has wrong manifest-entry count")
        if len(public_map.get("proofRoute", [])) != 15:
            errors.append("public Mainnet map has wrong proof-route count")

    csv_path = site / "downloads/proof-gradient/goalos-mainnet-contract-addresses.csv"
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != 49:
            errors.append(f"address CSV contains {len(rows)} data rows, expected 49")
        if sum(row.get("goalos_created") == "true" for row in rows) != 48:
            errors.append("address CSV does not mark exactly 48 GoalOS-created contracts")

    routes_path = site / "routes.json"
    if routes_path.exists():
        routes = read_json(routes_path).get("routes", [])
        if routes.count("proof-gradient-challenge.html") != 1:
            errors.append("routes.json does not contain exactly one Proof Gradient route")
    else:
        warnings.append("routes.json is absent from generated site")

    sitemap = site / "sitemap.xml"
    if not sitemap.exists() or "proof-gradient-challenge.html" not in sitemap.read_text(encoding="utf-8", errors="ignore"):
        errors.append("sitemap does not contain Proof Gradient page")

    for target in local_targets(page_raw):
        if not target or target.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "https://", "http://")):
            continue
        clean = unquote(target.split("#")[0].split("?")[0])
        if clean and not (page.parent / clean).exists():
            errors.append(f"Proof Gradient page has broken local link: {target}")

    archives = [str(path.relative_to(site)) for path in site.rglob("*") if path.is_file() and path.suffix.lower() in FORBIDDEN_ARCHIVES]
    if archives:
        errors.append("generated public site contains archives: " + ", ".join(archives[:20]))

    combined = page_raw + "\n" + home_raw
    for secret_marker in FORBIDDEN_SECRETS:
        if secret_marker in combined:
            errors.append(f"public generated HTML exposes secret-bearing marker: {secret_marker}")
    if re.search(r"(?<![0-9a-fA-F])(?:0x)?[0-9a-fA-F]{64}(?![0-9a-fA-F])", combined):
        errors.append("public generated HTML contains a private-key-shaped 64-hex literal")

    # Ensure synthetic-result language remains visible and comparative claims stay bounded.
    if page_raw.lower().count("synthetic") < 3:
        errors.append("synthetic claim boundary is not sufficiently visible")
    if "not an empirical" not in page_raw.lower():
        errors.append("page does not explicitly state that the simulation is not empirical")
    if "GoalOS has outperformed" in page_raw and "does not claim" not in page_raw:
        errors.append("page contains an unbounded comparative-performance claim")

    report = {
        "schemaVersion": "1.0",
        "status": "PASS" if not errors else "FAIL",
        "missionId": content["missionId"],
        "checks": {
            "homepageFeatureMarkers": home_raw.count(START),
            "goalosCreatedContractsExpected": 48,
            "goalosCreatedContractsFound": len(created),
            "contractCards": page_raw.lower().count("class='pg-contract'") + page_raw.lower().count('class="pg-contract"'),
            "publicArchives": len(archives),
            "publicNetworkTransactionSent": False,
        },
        "errors": errors,
        "warnings": warnings,
    }
    qadir = site / "qa"
    qadir.mkdir(exist_ok=True)
    (qadir / "proof-gradient-apex-verify.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Proof Gradient Website Overlay Verification", "", f"Status: **{report['status']}**", "", "## Errors"]
    lines += [f"- {item}" for item in errors] or ["- None"]
    lines += ["", "## Warnings"] + ([f"- {item}" for item in warnings] or ["- None"])
    (qadir / "proof-gradient-apex-verify.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the generated Proof Gradient Apex website overlay")
    parser.add_argument("--site", default="site")
    parser.add_argument("--content", default="content/proof-gradient-apex.json")
    parser.add_argument("--manifest", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()
    _, code = verify(Path(args.site), Path(args.content), Path(args.manifest))
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
