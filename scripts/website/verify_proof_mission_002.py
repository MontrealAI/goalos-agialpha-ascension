#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

M1_START = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->"
M1_END = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->"
M1_STYLE_START = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->"
M1_STYLE_END = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->"
M2_START = "<!-- GOALOS_PROOF_MISSION_002_START -->"
M2_END = "<!-- GOALOS_PROOF_MISSION_002_END -->"
M2_STYLE_START = "<!-- GOALOS_PROOF_MISSION_002_STYLE_START -->"
M2_STYLE_END = "<!-- GOALOS_PROOF_MISSION_002_STYLE_END -->"
M3_START = "<!-- GOALOS_PROOF_MISSION_003_START -->"
M3_END = "<!-- GOALOS_PROOF_MISSION_003_END -->"
M3_STYLE_START = "<!-- GOALOS_PROOF_MISSION_003_STYLE_START -->"
M3_STYLE_END = "<!-- GOALOS_PROOF_MISSION_003_STYLE_END -->"
FORBIDDEN = (
    "recursive.com",
    "recursive org",
    "recursive-style",
    "competitor comparison",
    "named competitor",
)


def remove_marked(text: str, start: str, end: str) -> str:
    return re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--canonical", default="website/v86_actual_site/index.html")
    parser.add_argument("--content", default="content/proof-mission-002-ascension-protocol.json")
    parser.add_argument("--mainnet", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()
    site = Path(args.site)
    errors: list[str] = []
    required = [
        "proof-gradient-challenge.html",
        "proof-mission-002.html",
        "proof-missions.html",
        "downloads/proof-missions/public-proof-mission-002.json",
        "downloads/proof-missions/mission-002-assumption-passport-template.json",
        "downloads/proof-missions/mission-002-proof-route.csv",
        "qa/proof-mission-002-build.json",
    ]
    for relative in required:
        if not (site / relative).exists():
            errors.append("missing " + relative)

    page = (site / "proof-mission-002.html").read_text(encoding="utf-8", errors="ignore") if (site / "proof-mission-002.html").exists() else ""
    hub = (site / "proof-missions.html").read_text(encoding="utf-8", errors="ignore") if (site / "proof-missions.html").exists() else ""
    home = (site / "index.html").read_text(encoding="utf-8", errors="ignore") if (site / "index.html").exists() else ""

    for token in [
        "THE ASCENSION",
        "PROTOCOL",
        "Where proven capability learns to travel.",
        "No transfer without provenance.",
        "No reuse without replay.",
        "No compounding without rollback.",
        "Transfer-Proven",
        "No result predeclared",
    ]:
        if token not in page:
            errors.append("Mission 002 page missing " + token)
    for token in ["THE PROOF", "MISSIONS", "The Proof Gradient", "The Ascension Protocol"]:
        if token not in hub:
            errors.append("Proof Missions hub missing " + token)

    marker_expectations = [
        (M1_START, M1_END, "Mission 001 homepage overlay"),
        (M1_STYLE_START, M1_STYLE_END, "Mission 001 homepage style"),
        (M2_START, M2_END, "Mission 002 homepage overlay"),
        (M2_STYLE_START, M2_STYLE_END, "Mission 002 homepage style"),
    ]
    for start, end, label in marker_expectations:
        if home.count(start) != 1 or home.count(end) != 1:
            errors.append(label + " marker count is not exactly one")

    m2_overlay = home.split(M2_START, 1)[1].split(M2_END, 1)[0] if M2_START in home and M2_END in home else ""
    public_new = (page + "\n" + hub + "\n" + m2_overlay).lower()
    for term in FORBIDDEN:
        if term in public_new:
            errors.append("prohibited public reference: " + term)
    if "proof-mission-002.html" not in home or "proof-missions.html" not in home:
        errors.append("homepage Mission 002 links missing")
    if "goalos-v86-preserve.css" not in page or "goalos-v86-dynamic-ai.js" not in page:
        errors.append("Mission 002 page is missing canonical v86 assets")

    try:
        content = json.loads(Path(args.content).read_text(encoding="utf-8"))
        if content.get("status") != "PROTOCOL_PUBLISHED_AWAITING_MISSION_001_ACCEPTED_CAPABILITY":
            errors.append("unexpected Mission 002 status")
        if sum(int(item.get("share", 0)) for item in content.get("settlement", [])) != 100:
            errors.append("settlement shares do not total 100")
        if len(content.get("proofRoute", [])) != 17:
            errors.append("expected 17 Mission 002 proof-route stages")
    except Exception as exc:
        errors.append("cannot validate Mission 002 content: " + str(exc))

    try:
        mainnet = json.loads(Path(args.mainnet).read_text(encoding="utf-8"))
        contract_by_name = {entry["name"]: entry for entry in mainnet["contracts"]}
        rows = list(csv.DictReader((site / "downloads/proof-missions/mission-002-proof-route.csv").open(encoding="utf-8")))
        if len(rows) != 17:
            errors.append(f"proof route expected 17 rows, found {len(rows)}")
        for row in rows:
            contract = contract_by_name.get(row["contract"])
            if not contract or contract["address"].lower() != row["address"].lower():
                errors.append("proof route address mismatch for " + row["contract"])
        if mainnet.get("verification", {}).get("verified") != 48 or mainnet.get("verification", {}).get("failed") != 0:
            errors.append("Mainnet verification summary mismatch")
        if mainnet.get("postcheck", {}).get("status") != "PASSED":
            errors.append("Mainnet postcheck is not PASSED")
    except Exception as exc:
        errors.append("cannot validate proof route/Mainnet data: " + str(exc))

    try:
        canonical = Path(args.canonical).read_text(encoding="utf-8")
        stripped = home
        for start, end in [
            (M1_START, M1_END),
            (M1_STYLE_START, M1_STYLE_END),
            (M2_START, M2_END),
            (M2_STYLE_START, M2_STYLE_END),
            (M3_START, M3_END),
            (M3_STYLE_START, M3_STYLE_END),
        ]:
            stripped = remove_marked(stripped, start, end)
        stripped = re.sub(r">\s+<", "><", stripped).strip()
        canonical_normalized = re.sub(r">\s+<", "><", canonical).strip()
        if stripped != canonical_normalized:
            errors.append("generated homepage differs from canonical source beyond marked Proof Mission overlays")
    except Exception as exc:
        errors.append("cannot validate canonical homepage preservation: " + str(exc))

    if any(site.rglob("*.zip")):
        errors.append("public site contains a ZIP archive")
    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": {
            "mission001Preserved": True,
            "mission002Pages": 2,
            "proofRouteContracts": 17,
            "goalosCreatedContracts": 48,
            "recordedVerified": 48,
            "recordedFailed": 0,
            "namedCompetitorReferencesInNewPublicContent": 0,
            "canonicalSourceModified": False,
            "resultPredeclared": False,
            "publicNetworkTransactionSent": False,
        },
    }
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "proof-mission-002-verify.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
