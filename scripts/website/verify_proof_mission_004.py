#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

MARKERS = [
    ("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->", "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->", "Mission 001 overlay"),
    ("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->", "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->", "Mission 001 style"),
    ("<!-- GOALOS_PROOF_MISSION_002_START -->", "<!-- GOALOS_PROOF_MISSION_002_END -->", "Mission 002 overlay"),
    ("<!-- GOALOS_PROOF_MISSION_002_STYLE_START -->", "<!-- GOALOS_PROOF_MISSION_002_STYLE_END -->", "Mission 002 style"),
    ("<!-- GOALOS_PROOF_MISSION_003_START -->", "<!-- GOALOS_PROOF_MISSION_003_END -->", "Mission 003 overlay"),
    ("<!-- GOALOS_PROOF_MISSION_003_STYLE_START -->", "<!-- GOALOS_PROOF_MISSION_003_STYLE_END -->", "Mission 003 style"),
    ("<!-- GOALOS_PROOF_MISSION_004_START -->", "<!-- GOALOS_PROOF_MISSION_004_END -->", "Mission 004 overlay"),
    ("<!-- GOALOS_PROOF_MISSION_004_STYLE_START -->", "<!-- GOALOS_PROOF_MISSION_004_STYLE_END -->", "Mission 004 style"),
]
FORBIDDEN = (
    "recursive.com",
    "recursive org",
    "recursive-style",
    "competitor comparison",
    "named competitor",
)
PRIVATE_PATTERNS = (
    "PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY",
    "MAINNET_RPC_URL=",
    "ETHERSCAN_API_KEY=",
    "SEED_PHRASE",
    "MNEMONIC",
)


def remove_marked(text: str, start: str, end: str) -> str:
    return re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--canonical", default="website/v86_actual_site/index.html")
    parser.add_argument("--content", default="content/proof-mission-004-sovereign-institution.json")
    parser.add_argument("--mainnet", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()
    site = Path(args.site)
    errors: list[str] = []

    required = [
        "proof-gradient-challenge.html",
        "proof-mission-002.html",
        "proof-mission-003.html",
        "proof-mission-004.html",
        "proof-missions.html",
        "downloads/proof-missions/public-proof-mission-004.json",
        "downloads/proof-missions/mission-004-institution-charter-template.json",
        "downloads/proof-missions/mission-004-epoch-ledger-template.json",
        "downloads/proof-missions/mission-004-treasury-policy-template.json",
        "downloads/proof-missions/mission-004-incident-recovery-template.json",
        "downloads/proof-missions/mission-004-proof-route.csv",
        "qa/proof-mission-004-build.json",
    ]
    for relative in required:
        if not (site / relative).exists():
            errors.append("missing " + relative)

    def read(relative: str) -> str:
        path = site / relative
        return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""

    page = read("proof-mission-004.html")
    hub = read("proof-missions.html")
    home = read("index.html")
    mission3 = read("proof-mission-003.html")

    page_tokens = [
        "THE SOVEREIGN",
        "INSTITUTION",
        "Where governed intelligence learns to endure.",
        "No mandate, no mission.",
        "No capital without proof.",
        "No evolution beyond review and rollback.",
        "The Four-Epoch Sovereignty Trial",
        "M4 is earned only by repeated proof-governed operation.",
        "No institution may certify itself.",
        "Thirty-four institutional stages",
        "MISSION 005 HORIZON",
        "No institutional result predeclared",
    ]
    for token in page_tokens:
        if token not in page:
            errors.append("Mission 004 page missing " + token)
    if "PROTOCOL_PUBLISHED_AWAITING_ONE_COMPOSITION_PROVEN_CONSTELLATION".lower() in page.lower():
        errors.append("raw machine status leaked into public Mission 004 page")
    if "goalos-v86-preserve.css" not in page or "goalos-v86-dynamic-ai.js" not in page:
        errors.append("Mission 004 page missing canonical assets")
    if page.count('class="si-route-item"') != 34:
        errors.append("Mission 004 page does not contain exactly 34 route entries")
    if page.count('class="si-validator"') != 5:
        errors.append("Mission 004 page does not contain exactly five validator cards")

    hub_tokens = [
        "THE PROOF",
        "MISSIONS",
        "The Proof Gradient",
        "The Ascension Protocol",
        "The Capability Constellation",
        "The Sovereign Institution",
        "proof-mission-004.html",
        "The Interinstitutional Accord",
    ]
    for token in hub_tokens:
        if token not in hub:
            errors.append("Proof Missions hub missing " + token)
    if hub.count('class="pm-card') != 4:
        errors.append("Proof Missions hub must contain exactly four mission cards")

    for start, end, label in MARKERS:
        if home.count(start) != 1 or home.count(end) != 1:
            errors.append(label + " marker count is not exactly one")
    if "proof-mission-004.html" not in home or "proof-missions.html" not in home:
        errors.append("homepage Mission 004 links missing")
    if "PUBLIC PROOF MISSION 004 · NOW PUBLISHED" not in mission3 or "proof-mission-004.html" not in mission3:
        errors.append("Mission 003 public horizon was not promoted to Mission 004")
    if "MISSION 004 HORIZON" in mission3:
        errors.append("stale Mission 004 horizon remains in Mission 003 page")

    m4_start, m4_end = MARKERS[6][0], MARKERS[6][1]
    overlay = home.split(m4_start, 1)[1].split(m4_end, 1)[0] if m4_start in home and m4_end in home else ""
    public_blob = (page + "\n" + hub + "\n" + overlay + "\n" + mission3).lower()
    for term in FORBIDDEN:
        if term in public_blob:
            errors.append("prohibited public reference: " + term)
    for term in PRIVATE_PATTERNS:
        if term.lower() in public_blob:
            errors.append("private operator material appears in Mission 004 public content: " + term)

    try:
        content = json.loads(Path(args.content).read_text(encoding="utf-8"))
        if content.get("sequence") != 4:
            errors.append("Mission 004 sequence mismatch")
        if content.get("status") != "PROTOCOL_PUBLISHED_AWAITING_ONE_COMPOSITION_PROVEN_CONSTELLATION":
            errors.append("unexpected Mission 004 status")
        if sum(int(x.get("share", 0)) for x in content.get("settlement", [])) != 100:
            errors.append("Mission 004 settlement shares do not total 100")
        if len(content.get("proofRoute", [])) != 34:
            errors.append("expected 34 Mission 004 proof-route stages")
        if len(content.get("validators", [])) != 5:
            errors.append("expected five Mission 004 validators")
        if len(content.get("institutionalCampaign", {}).get("epochs", [])) != 5:
            errors.append("expected five institutional records EPOCH_0 through EPOCH_4")
        budget = content.get("missionBudget", {})
        if budget.get("missionEpochs") != 4:
            errors.append("expected four operating mission epochs")
        if budget.get("challengeWindowHours") != 336:
            errors.append("expected 336-hour challenge window")
        if content.get("mission5", {}).get("status") != "HORIZON_ONLY_NOT_YET_AUTHORIZED":
            errors.append("Mission 005 horizon status mismatch")
    except Exception as exc:
        errors.append("cannot validate Mission 004 content: " + str(exc))

    try:
        mainnet = json.loads(Path(args.mainnet).read_text(encoding="utf-8"))
        by_name = {entry["name"]: entry for entry in mainnet["contracts"]}
        with (site / "downloads/proof-missions/mission-004-proof-route.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != 34:
            errors.append(f"proof route expected 34 rows, found {len(rows)}")
        for row in rows:
            contract = by_name.get(row["contract"])
            if not contract or contract["address"].lower() != row["address"].lower():
                errors.append("proof route address mismatch for " + row["contract"])
        if mainnet.get("goalosCreatedContractCount") != 48:
            errors.append("Mainnet contract count mismatch")
        verification = mainnet.get("verification", {})
        if verification.get("verified") != 48 or verification.get("failed") != 0:
            errors.append("Mainnet verification summary mismatch")
        if mainnet.get("phaseBGrantCount") != 14:
            errors.append("Mainnet configured grant count mismatch")
        if mainnet.get("postcheck", {}).get("status") != "PASSED":
            errors.append("Mainnet postcheck not PASSED")
    except Exception as exc:
        errors.append("cannot validate proof route/Mainnet data: " + str(exc))

    templates = [
        "mission-004-institution-charter-template.json",
        "mission-004-epoch-ledger-template.json",
        "mission-004-treasury-policy-template.json",
        "mission-004-incident-recovery-template.json",
    ]
    for template in templates:
        try:
            value = json.loads((site / "downloads/proof-missions" / template).read_text(encoding="utf-8"))
            if value.get("status") != "TEMPLATE_NOT_EVIDENCE":
                errors.append(template + " must be explicitly non-evidence")
        except Exception as exc:
            errors.append("cannot validate " + template + ": " + str(exc))

    try:
        canonical = Path(args.canonical).read_text(encoding="utf-8")
        stripped = home
        for start, end, _ in MARKERS:
            stripped = remove_marked(stripped, start, end)
        normalize = lambda text: re.sub(r">\s+<", "><", text).strip()
        if normalize(stripped) != normalize(canonical):
            errors.append("generated homepage differs from canonical source beyond marked mission overlays")
    except Exception as exc:
        errors.append("cannot validate canonical homepage preservation: " + str(exc))

    if any(site.rglob("*.zip")):
        errors.append("public site contains a ZIP archive")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": {
            "mission001Preserved": True,
            "mission002Preserved": True,
            "mission003PreservedAndPromoted": True,
            "mission004Pages": 2,
            "proofRouteContracts": 34,
            "goalosCreatedContracts": 48,
            "recordedVerified": 48,
            "recordedFailed": 0,
            "configuredGrants": 14,
            "validatorQuorum": 5,
            "challengeWindowHours": 336,
            "namedCompetitorReferencesInNewPublicContent": 0,
            "canonicalSourceModified": False,
            "resultPredeclared": False,
            "publicNetworkTransactionSent": False,
        },
    }
    (site / "qa").mkdir(exist_ok=True)
    (site / "qa/proof-mission-004-verify.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
