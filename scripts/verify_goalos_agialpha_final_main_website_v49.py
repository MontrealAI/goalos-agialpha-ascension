#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
REQUIRED = [
    "index.html", "mission-os.html", "mission-os-paper.html", "autopilot-mission-builder.html", "proof-cards.html",
    "evidence-docket.html", "system-map.html", "execution-moat.html", "roadmap.html", "research.html",
    "agialpha-ledger-route.html", "sovereign-rsi-control-plane.html", "sitemap.xml", "robots.txt", "manifest.webmanifest", "routes.json", "site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,18)]
FORBIDDEN = ["recursive.com", "recursive-org/first-steps", "DEPLOYER_PRIVATE_KEY", "PRIVATE_KEY=", "MNEMONIC=", "SEED_PHRASE=", "MAINNET_RPC_URL="]
def fail(msg):
    print("FAIL:", msg); sys.exit(1)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--site", default="site"); args = ap.parse_args()
    site = Path(args.site)
    if not site.exists(): fail(f"missing site folder: {site}")
    for name in REQUIRED:
        if not (site/name).exists(): fail(f"missing required page/file: {name}")
    index = (site/'index.html').read_text(encoding='utf-8', errors='replace')
    paper = (site/'mission-os-paper.html').read_text(encoding='utf-8', errors='replace')
    atlas = (site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
    for phrase in ["GoalOS Mission OS Paper", "The Proof OS for Autonomous AI Work", "AI creates output. GoalOS creates proof", "AGIALPHA", "Evidence Docket", "Recursive Self-Improvement"]:
        if phrase not in paper: fail(f"paper missing phrase: {phrase}")
    if "mission-os-paper.html" not in index: fail("homepage does not link mission-os-paper.html")
    for i in range(1,18):
        fn = f"proof-card-{i:03d}.html"
        if fn not in index: fail(f"homepage missing {fn}")
        if fn not in atlas: fail(f"atlas missing {fn}")
    if list(site.rglob('*.zip')): fail("generated public site contains zip files")
    for p in site.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.html','.json','.txt','.xml','.webmanifest'}:
            text = p.read_text(encoding='utf-8', errors='replace').lower()
            for bad in FORBIDDEN:
                if bad.lower() in text: fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v49 verification passed.")
if __name__ == "__main__": main()
