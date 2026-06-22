#!/usr/bin/env python3
"""Static integration checks for the unified GoalOS public website artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MAINNET_MARKERS = (
    "<!-- GOALOS_MAINNET_V87_START -->",
    "<!-- GOALOS_MAINNET_V87_END -->",
    "<!-- GOALOS_MAINNET_V87_STYLE_START -->",
    "<!-- GOALOS_MAINNET_V87_STYLE_END -->",
)
PROOF_MARKERS = (
    "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->",
    "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->",
    "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->",
    "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    args = parser.parse_args()
    site = Path(args.site)
    errors: list[str] = []
    warnings: list[str] = []

    index_path = site / "index.html"
    mainnet_path = site / "ethereum-mainnet.html"
    proof_path = site / "proof-gradient-challenge.html"
    sitemap_path = site / "sitemap.xml"
    status_path = site / "site-status.json"
    for path in (index_path, mainnet_path, proof_path, sitemap_path, status_path):
        if not path.is_file():
            errors.append(f"missing unified public artifact: {path}")
    if not errors:
        index = index_path.read_text(encoding="utf-8", errors="ignore")
        mainnet = mainnet_path.read_text(encoding="utf-8", errors="ignore")
        proof = proof_path.read_text(encoding="utf-8", errors="ignore")
        sitemap = sitemap_path.read_text(encoding="utf-8", errors="ignore")

        for marker in (*MAINNET_MARKERS, *PROOF_MARKERS):
            if index.count(marker) != 1:
                errors.append(f"homepage marker must occur exactly once: {marker}")

        if "proof-gradient-challenge.html" not in mainnet:
            errors.append("Ethereum Mainnet page does not link to the Proof Gradient")
        if "ethereum-mainnet.html" not in proof:
            errors.append("Proof Gradient page does not link to the Ethereum Mainnet record")
        if "ethereum-mainnet.html" not in index or "proof-gradient-challenge.html" not in index:
            errors.append("homepage does not link to both unified flagship pages")
        if "ethereum-mainnet.html" not in sitemap or "proof-gradient-challenge.html" not in sitemap:
            errors.append("sitemap does not include both unified flagship pages")

        if "data-design-version='v88-institutional'" not in mainnet:
            errors.append("Mainnet institutional design marker missing")
        if 'data-proof-gradient-edition="sovereign-v3"' not in proof:
            errors.append("Proof Gradient Sovereign v3 design marker missing")

        status = load_json(status_path)
        expected = {
            "ethereum_mainnet_page": "ethereum-mainnet.html",
            "ethereum_mainnet_chain_id": 1,
            "ethereum_mainnet_registry_entries": 49,
            "goalos_mainnet_contracts": 48,
            "operator_etherscan_verification": "48/48",
            "mainnet_configured": True,
            "production_activated": False,
            "user_funds_authorized": False,
        }
        for key, value in expected.items():
            if status.get(key) != value:
                errors.append(f"site-status.json {key} expected {value!r}, got {status.get(key)!r}")
        proof_status = status.get("proofGradient")
        if not isinstance(proof_status, dict):
            errors.append("site-status.json proofGradient block missing")
        else:
            proof_expected = {
                "edition": "SOVEREIGN_V3",
                "missionId": "GOALOS-PUBLIC-PROOF-MISSION-001",
                "page": "proof-gradient-challenge.html",
                "goalosContracts": 48,
                "verified": 48,
                "failed": 0,
                "publicNetworkTransactionSent": False,
            }
            for key, value in proof_expected.items():
                if proof_status.get(key) != value:
                    errors.append(f"proofGradient.{key} expected {value!r}, got {proof_status.get(key)!r}")

        if index.find(MAINNET_MARKERS[0]) == index.find(PROOF_MARKERS[0]):
            errors.append("homepage flagship sections overlap unexpectedly")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "pages": ["index.html", "ethereum-mainnet.html", "proof-gradient-challenge.html"],
        "crossLinksRequired": True,
        "singlePagesDeployment": True,
        "publicNetworkTransactionSent": False,
    }
    qa = site / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    (qa / "unified-public-site-verify.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
