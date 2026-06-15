#!/usr/bin/env python3
from pathlib import Path
import argparse, sys, re

REQUIRED = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","evidence-docket.html","system-map.html","execution-moat.html",
    "roadmap.html","research.html","routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,18)]

FORBIDDEN = ["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

def main():
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
    paper = (site / "mission-os-paper.html").read_text(encoding="utf-8", errors="replace")
    for i in range(1,18):
        fn = f"proof-card-{i:03d}.html"
        if fn not in index:
            fail(f"homepage does not link {fn}")
        if fn not in atlas:
            fail(f"atlas does not link {fn}")
    required_paper = [
        "The Proof OS for Autonomous AI Work",
        "Source-synced from docs/papers/mission-os",
        "A specialist-agent institution, not a single assistant",
        "Use AGIALPHA where proof changes state",
        "GoalOS_Mission_OS_Paper.md",
        "v50 visual QA hardening",
    ]
    for needle in required_paper:
        if needle not in paper:
            fail(f"paper page missing: {needle}")
    # Visual contrast hardening checks.
    if ".paper-table td" not in paper or "color:#071427" not in paper:
        fail("paper table contrast hardening missing")
    if ".dark .card" not in paper:
        fail("dark card contrast hardening missing")
    # No zips in generated public site.
    if list(site.rglob("*.zip")):
        fail("generated public site contains zip files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v50 verification passed.")

if __name__ == "__main__":
    main()
