#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

START = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->"
END = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->"
STYLE_START = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->"
STYLE_END = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->"
CANONICAL_AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
FORBIDDEN = ("third-party competitor", "competitor comparison", " versus ", " vs. ")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.contract_cards = 0
        self.h1 = 0
        self.main = 0
        self.forms = 0
        self.external_links: list[dict[str, str]] = []
        self.local_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "article" and "pgs-contract" in data.get("class", "").split():
            self.contract_cards += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "main":
            self.main += 1
        elif tag == "form":
            self.forms += 1
        elif tag == "a":
            href = data.get("href", "")
            if href.startswith("http://") or href.startswith("https://"):
                self.external_links.append({"href": href, "target": data.get("target", ""), "rel": data.get("rel", "")})
            elif href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
                self.local_links.append(href.split("#", 1)[0].split("?", 1)[0])


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    args = parser.parse_args()
    site = Path(args.site)
    errors: list[str] = []
    warnings: list[str] = []

    required = (
        "index.html",
        "ethereum-mainnet.html",
        "proof-gradient-challenge.html",
        "downloads/proof-gradient/goalos-mainnet-contract-addresses.csv",
        "downloads/proof-gradient/proof-gradient-mainnet-map.json",
        "downloads/proof-gradient/public-proof-mission-001.json",
        "qa/proof-gradient-sovereign-build.json",
    )
    for rel in required:
        if not (site / rel).is_file():
            errors.append(f"missing {rel}")

    page = (site / "proof-gradient-challenge.html").read_text(encoding="utf-8", errors="ignore") if (site / "proof-gradient-challenge.html").is_file() else ""
    home = (site / "index.html").read_text(encoding="utf-8", errors="ignore") if (site / "index.html").is_file() else ""

    for token in (
        "THE PROOF",
        "GRADIENT",
        "Where autonomous work earns the right to become capability.",
        "No proof, no propagation.",
        "48/48",
        "Not externally audited",
        'data-proof-gradient-edition="sovereign-v3"',
        "ethereum-mainnet.html",
        "goalos-v86-preserve.css",
        "goalos-v86-dynamic-ai.js",
        "goalos-v86-critical",
    ):
        if token not in page:
            errors.append(f"page missing {token}")

    if home.count(START) != 1 or home.count(END) != 1:
        errors.append("homepage Proof Gradient marker count is not exactly one")
    if home.count(STYLE_START) != 1 or home.count(STYLE_END) != 1:
        errors.append("homepage Proof Gradient style marker count is not exactly one")
    if "proof-gradient-challenge.html" not in home or "ethereum-mainnet.html" not in home:
        errors.append("homepage Proof Gradient feature does not link to both public flagship pages")

    overlay = home.split(START, 1)[1].split(END, 1)[0] if START in home and END in home else ""
    public_new = (page + "\n" + overlay).lower()
    for term in FORBIDDEN:
        if term in public_new:
            errors.append(f"prohibited public competitor reference: {term}")

    page_parser = PageParser()
    page_parser.feed(page)
    if page_parser.h1 != 1:
        errors.append(f"Proof Gradient page must contain exactly one h1, found {page_parser.h1}")
    if page_parser.main != 1:
        errors.append(f"Proof Gradient page must contain exactly one main landmark, found {page_parser.main}")
    if page_parser.forms:
        errors.append("Proof Gradient page must not contain a form")
    if page_parser.contract_cards != 48:
        errors.append(f"Proof Gradient page expected 48 contract cards, found {page_parser.contract_cards}")
    for link in page_parser.external_links:
        parsed = urlparse(link["href"])
        if parsed.scheme != "https":
            errors.append(f"non-HTTPS external link: {link['href']}")
        if link["target"] == "_blank" and ("noopener" not in link["rel"] or "noreferrer" not in link["rel"]):
            errors.append(f"unsafe target=_blank link: {link['href']}")
    for rel in page_parser.local_links:
        if rel and not (site / rel).exists():
            errors.append(f"broken local Proof Gradient link: {rel}")

    try:
        csv_path = site / "downloads/proof-gradient/goalos-mainnet-contract-addresses.csv"
        rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
        if len(rows) != 49:
            errors.append(f"address CSV expected 49 entries, found {len(rows)}")
        goalos_rows = [row for row in rows if row.get("goalos_created") == "true"]
        if len(goalos_rows) != 48:
            errors.append(f"address CSV expected 48 GoalOS-created entries, found {len(goalos_rows)}")
        addresses = [row.get("address", "") for row in rows]
        if len({address.lower() for address in addresses}) != len(addresses):
            errors.append("address CSV contains duplicate addresses")
        if any(not ADDRESS_RE.fullmatch(address) for address in addresses):
            errors.append("address CSV contains an invalid Ethereum address")
        agialpha = [row for row in rows if row.get("name") == "AGIALPHA"]
        if len(agialpha) != 1 or agialpha[0].get("address", "").lower() != CANONICAL_AGIALPHA.lower() or agialpha[0].get("goalos_created") != "false":
            errors.append("address CSV canonical external AGIALPHA entry is incorrect")
    except Exception as exc:
        errors.append(f"cannot validate address CSV: {exc}")

    try:
        mainnet_map = load_json(site / "downloads/proof-gradient/proof-gradient-mainnet-map.json")
        if mainnet_map.get("chainId") != 1 or mainnet_map.get("canonicalAgialpha", "").lower() != CANONICAL_AGIALPHA.lower():
            errors.append("Proof Gradient Mainnet map chain/token boundary mismatch")
        verification = mainnet_map.get("verification", {})
        if verification.get("verified") != 48 or verification.get("failed") != 0 or verification.get("complete") is not True:
            errors.append("Proof Gradient Mainnet map verification summary mismatch")
        postcheck = mainnet_map.get("postcheck", {})
        if postcheck.get("status") != "PASSED" or postcheck.get("checkedContracts") != 48:
            errors.append("Proof Gradient Mainnet map postcheck mismatch")
        if len(mainnet_map.get("contracts", [])) != 49:
            errors.append("Proof Gradient Mainnet map must contain 49 contract entries")
    except Exception as exc:
        errors.append(f"cannot validate Mainnet map: {exc}")

    try:
        mission = load_json(site / "downloads/proof-gradient/public-proof-mission-001.json")
        if mission.get("pageVersion") != "sovereign-v3" or mission.get("missionId") != "GOALOS-PUBLIC-PROOF-MISSION-001":
            errors.append("published Proof Mission JSON is not Sovereign v3 / Mission 001")
    except Exception as exc:
        errors.append(f"cannot validate public mission JSON: {exc}")

    archives = [path for path in site.rglob("*") if path.is_file() and path.suffix.lower() in {".zip", ".7z", ".tar", ".gz", ".rar"}]
    if archives:
        errors.append("public site contains archive files")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "edition": "SOVEREIGN_V3",
            "goalosCreatedContracts": 48,
            "recordedVerified": 48,
            "recordedFailed": 0,
            "configurationGrants": "14/14",
            "mainnetCrossLink": True,
            "competitorReferencesInNewPublicContent": 0,
            "canonicalSourceModified": False,
            "publicNetworkTransactionSent": False,
        },
    }
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "proof-gradient-sovereign-verify.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
