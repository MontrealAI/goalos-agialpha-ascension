#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

CANONICAL_AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
RELEASE_TAG = "v4.4.0-mainnet-2026-06-21"
RELEASE_URL = "https://github.com/MontrealAI/goalos-agialpha-ascension/releases/tag/v4.4.0-mainnet-2026-06-21"
HOME_START = "<!-- GOALOS_MAINNET_V87_START -->"
HOME_END = "<!-- GOALOS_MAINNET_V87_END -->"
HOME_STYLE_START = "<!-- GOALOS_MAINNET_V87_STYLE_START -->"
HOME_STYLE_END = "<!-- GOALOS_MAINNET_V87_STYLE_END -->"
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


class MainnetPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.contract_links: list[dict[str, str]] = []
        self.links: list[str] = []
        self.forms = 0
        self.h1 = 0
        self.main = 0
        self.details = 0
        self.current_contract: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k: (v or "") for k, v in attrs}
        if tag == "a":
            href = data.get("href", "")
            if href:
                self.links.append(href)
            if data.get("data-mainnet-contract") == "true":
                self.contract_links.append({
                    "href": href,
                    "classification": data.get("data-classification", ""),
                    "address": data.get("data-address", ""),
                    "rel": data.get("rel", ""),
                    "target": data.get("target", ""),
                })
        elif tag == "form":
            self.forms += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "main":
            self.main += 1
        elif tag == "details":
            self.details += 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_registry(registry_path: Path) -> list[dict[str, str]]:
    registry = load_json(registry_path)
    if not isinstance(registry, dict):
        raise ValueError("contract registry must be a JSON object")

    metadata = registry.get("metadata")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("contract registry metadata must be an object")

    chain_id = registry.get("chainId", metadata.get("chainId"))
    if chain_id != 1:
        raise ValueError("contract registry must describe Ethereum Mainnet chainId 1")

    raw_contracts = registry.get("contracts")
    if not isinstance(raw_contracts, list) or len(raw_contracts) != 49:
        raise ValueError("contract registry must contain exactly 49 entries")

    normalized: list[dict[str, str]] = []
    seen_addresses: set[str] = set()
    seen_names: set[str] = set()

    for raw in raw_contracts:
        if not isinstance(raw, dict):
            raise ValueError("every registry entry must be an object")
        name = raw.get("name")
        address = raw.get("address")
        entry_chain_id = raw.get("chainId", chain_id)
        if not isinstance(name, str) or not name:
            raise ValueError("registry entry has no valid name")
        if not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            raise ValueError(f"invalid Ethereum address for {name}")
        if entry_chain_id != 1:
            raise ValueError(f"wrong chainId for {name}")

        classification = raw.get("classification")
        if classification not in {"deployed", "external"}:
            if raw.get("external") is True and raw.get("deployedByGoalOS") is False:
                classification = "external"
            elif raw.get("external") is False and raw.get("deployedByGoalOS") is True:
                classification = "deployed"
            else:
                raise ValueError(f"cannot determine classification for {name}")

        key = address.lower()
        if key in seen_addresses:
            raise ValueError(f"duplicate contract address: {address}")
        if name in seen_names:
            raise ValueError(f"duplicate contract name: {name}")
        seen_addresses.add(key)
        seen_names.add(name)
        normalized.append({"name": name, "address": address, "classification": classification})

    deployed = sum(c["classification"] == "deployed" for c in normalized)
    external = sum(c["classification"] == "external" for c in normalized)
    if deployed != 48 or external != 1:
        raise ValueError(f"expected 48 deployed and 1 external entries, got {deployed}/{external}")

    agialpha = next((c for c in normalized if c["name"] == "AGIALPHA"), None)
    if agialpha is None or agialpha["address"].lower() != CANONICAL_AGIALPHA.lower() or agialpha["classification"] != "external":
        raise ValueError("canonical external AGIALPHA entry is missing or incorrect")
    return normalized


def verify(site: Path, registry_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    index_path = site / "index.html"
    page_path = site / "ethereum-mainnet.html"
    sitemap_path = site / "sitemap.xml"
    status_path = site / "site-status.json"

    for path in (index_path, page_path, sitemap_path, status_path):
        if not path.is_file():
            errors.append(f"missing generated file: {path}")
    if errors:
        return errors, warnings

    index = index_path.read_text(encoding="utf-8", errors="ignore")
    page = page_path.read_text(encoding="utf-8", errors="ignore")
    sitemap = sitemap_path.read_text(encoding="utf-8", errors="ignore")

    if index.count(HOME_START) != 1 or index.count(HOME_END) != 1:
        errors.append("homepage must contain exactly one v87 Mainnet marker block")
    if index.count(HOME_STYLE_START) != 1 or index.count(HOME_STYLE_END) != 1:
        errors.append("homepage must contain exactly one scoped Mainnet design block")
    if "href='ethereum-mainnet.html'" not in index and 'href="ethereum-mainnet.html"' not in index:
        errors.append("homepage does not link to ethereum-mainnet.html")
    if "Production activation, user-fund authorization, and public production reliance remain disabled" not in index:
        errors.append("homepage Mainnet feature is missing the activation boundary")
    for required_home in ("mn-home-shell","mn-home-btn--primary","mn-home-btn--secondary","background-color:#ffffff","color:#07111f"):
        if required_home not in index:
            errors.append(f"homepage Mainnet design is missing: {required_home}")

    for required in (
        "assets/goalos-v86-preserve.css","assets/goalos-v86-dynamic-ai.js","goalos-v86-critical",
        "goalos-mainnet-v88-design","data-design-version='v88-institutional'",RELEASE_URL,
        "Production activation: NO","user-fund authorization","external audit",
        "Independent dual-provider release revalidation",CANONICAL_AGIALPHA,
        "mn-btn--primary","mn-btn--secondary","mn-btn--ghost","font-family:Inter","proof-gradient-challenge.html",
    ):
        if required.lower() not in page.lower():
            errors.append(f"Mainnet page is missing required content/design: {required}")

    parser = MainnetPageParser()
    parser.feed(page)
    if parser.h1 != 1:
        errors.append(f"Mainnet page must contain one h1, found {parser.h1}")
    if parser.main != 1:
        errors.append(f"Mainnet page must contain one main landmark, found {parser.main}")
    if parser.forms:
        errors.append("Mainnet page must not contain forms")
    if parser.details != 5:
        errors.append(f"Mainnet page must contain five contract groups, found {parser.details}")
    if len(parser.contract_links) != 49:
        errors.append(f"expected 49 contract links, found {len(parser.contract_links)}")

    addresses = [entry["address"] for entry in parser.contract_links]
    if len({a.lower() for a in addresses}) != len(addresses):
        errors.append("duplicate contract address on Mainnet page")
    for entry in parser.contract_links:
        address = entry["address"]
        if not ADDRESS_RE.fullmatch(address):
            errors.append(f"invalid address in Mainnet page: {address}")
        if entry["classification"] not in {"deployed", "external"}:
            errors.append(f"invalid classification for {address}")
        if entry["target"] != "_blank" or "noopener" not in entry["rel"] or "noreferrer" not in entry["rel"]:
            errors.append(f"external Etherscan link is missing safe target/rel attributes: {address}")
        parsed = urlparse(entry["href"])
        if parsed.scheme != "https" or parsed.netloc != "etherscan.io":
            errors.append(f"contract link is not an HTTPS Etherscan URL: {entry['href']}")

    deployed = sum(e["classification"] == "deployed" for e in parser.contract_links)
    external = sum(e["classification"] == "external" for e in parser.contract_links)
    if deployed != 48 or external != 1:
        errors.append(f"expected 48 deployed and 1 external contract links, found {deployed}/{external}")

    try:
        registry_contracts = normalize_registry(registry_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid canonical registry: {exc}")
        registry_contracts = []
    page_addresses = {(e["address"].lower(), e["classification"]) for e in parser.contract_links}
    expected_addresses = {(c["address"].lower(), c["classification"]) for c in registry_contracts}
    if page_addresses != expected_addresses:
        errors.append("Mainnet page address/classification set does not match canonical registry")

    low = page.lower()
    for token in ("window.ethereum","eth_sendtransaction","walletconnect","connect wallet","approve token","send funds","fund now"):
        if token in low:
            errors.append(f"Mainnet page contains a prohibited write/wallet surface: {token}")

    if "ethereum-mainnet.html" not in sitemap:
        errors.append("sitemap.xml does not contain ethereum-mainnet.html")

    status = load_json(status_path)
    expected_status = {
        "ethereum_mainnet_page":"ethereum-mainnet.html","ethereum_mainnet_release":RELEASE_TAG,
        "ethereum_mainnet_chain_id":1,"ethereum_mainnet_registry_entries":49,
        "goalos_mainnet_contracts":48,"operator_etherscan_verification":"48/48",
        "mainnet_configured":True,"production_activated":False,"user_funds_authorized":False,
    }
    for key, value in expected_status.items():
        if status.get(key) != value:
            errors.append(f"site-status.json {key} expected {value!r}, got {status.get(key)!r}")

    if len(re.findall(r"\b[\w$αΑ-]+\b", re.sub(r"<[^>]+>", " ", page))) < 250:
        errors.append("Mainnet page is unexpectedly short")
    return errors, warnings
def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the generated GoalOS Ethereum Mainnet page and homepage card")
    parser.add_argument("--site", default="site")
    parser.add_argument("--registry", default="config/ethereum-mainnet.contracts.json")
    args = parser.parse_args()

    site = Path(args.site)
    registry = Path(args.registry)
    errors, warnings = verify(site, registry)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "page": "ethereum-mainnet.html",
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "contract_links_expected": 49,
            "goalos_contracts_expected": 48,
            "external_contracts_expected": 1,
            "homepage_marker": "GOALOS_MAINNET_V87",
            "write_actions_enabled": False,
        },
    }
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "mainnet-page-static-verify-v87.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = ["# GoalOS Ethereum Mainnet Page Static Verification", "", f"Status: **{report['status']}**", "", "## Errors"]
    md += [f"- {error}" for error in errors] or ["- None"]
    md += ["", "## Warnings"]
    md += [f"- {warning}" for warning in warnings] or ["- None"]
    (qa / "mainnet-page-static-verify-v87.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
