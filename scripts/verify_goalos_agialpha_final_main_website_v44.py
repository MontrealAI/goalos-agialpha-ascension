#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

REQUIRED = [
    "index.html", "mission-os.html", "start-here.html", "regular-person.html",
    "personal-proof-sprint.html", "proof-sprint-builder.html",
    "autopilot-mission-builder.html", "use-cases.html", "resources.html",
    "proof-cards.html", "system-map.html", "how-it-works.html",
    "execution-moat.html", "roadmap.html", "pilot-guide.html", "research.html",
    "agialpha-ledger-route.html", "sovereign-rsi-control-plane.html",
    "evidence-docket.html", "sitemap.xml", "robots.txt",
    "manifest.webmanifest", "routes.json", "site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1, 18)]

FORBIDDEN = [
    "recursive.com",
    "recursive-org/first-steps",
    "DEPLOYER_PRIVATE_KEY",
    "PRIVATE_KEY=",
    "MNEMONIC=",
    "SEED_PHRASE=",
    "MAINNET_RPC_URL=",
]

def fail(message: str) -> None:
    print("FAIL:", message)
    sys.exit(1)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)

    if not site.exists():
        fail(f"missing site folder: {site}")

    for name in REQUIRED:
        if not (site / name).exists():
            fail(f"missing required page/file: {name}")

    index = (site / "index.html").read_text(encoding="utf-8", errors="replace")
    atlas = (site / "proof-cards.html").read_text(encoding="utf-8", errors="replace")
    mission = (site / "mission-os.html").read_text(encoding="utf-8", errors="replace")

    for i in range(1, 18):
        fn = f"proof-card-{i:03d}.html"
        if fn not in index:
            fail(f"homepage missing {fn}")
        if fn not in atlas:
            fail(f"atlas missing {fn}")

    for token in [
        "Mission OS",
        "The Proof OS for Autonomous AI Work",
        "Autopilot",
        "Evidence Docket",
        "AGIALPHA",
        "RSI",
    ]:
        if token not in index:
            fail(f"homepage missing {token}")

    for token in [
        "Set the objective",
        "GoalOS runs until proof is done",
        "Action Graph",
        "Verifier",
        "Chronicle",
        "Claim boundary",
    ]:
        if token not in mission:
            fail(f"mission-os missing {token}")

    for z in site.rglob("*.zip"):
        fail(f"zip file present in public site: {z}")

    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html", ".json", ".txt", ".xml", ".webmanifest", ".md", ".csv"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")

    print("GoalOS AGIALPHA final main website v44 verification passed.")

if __name__ == "__main__":
    main()
