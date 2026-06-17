#!/usr/bin/env python3
from pathlib import Path
import argparse, sys, re, json
STABLE = list(range(1,23)) + list(range(24,32))
REQUIRED = [
    "index.html","executive-brief.html","proof-observatory.html","proof-cards.html",
    "ascension.html","proof-treasury.html","proof-treasury-simulation-003.html",
    "proof-treasury-simulation-004.html","proof-treasury-simulation-005.html",
    "mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-card-023.html","routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in STABLE]
FORBIDDEN = ["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]
def fail(msg):
    print("FAIL:", msg); sys.exit(1)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args=ap.parse_args()
    site=Path(args.site)
    if not site.exists(): fail(f"missing site folder: {site}")
    for name in REQUIRED:
        if not (site/name).exists(): fail(f"missing {name}")
    index=(site/"index.html").read_text(encoding="utf-8", errors="replace")
    atlas=(site/"proof-cards.html").read_text(encoding="utf-8", errors="replace")
    for i in STABLE:
        fn=f"proof-card-{i:03d}.html"
        if fn not in index and i in [28,29,30,31]:
            fail(f"homepage missing latest proof card {fn}")
        if fn not in atlas:
            fail(f"atlas missing {fn}")
    if "proof-card-023.html" not in atlas or "Reserved" not in (site/"proof-card-023.html").read_text(encoding="utf-8", errors="replace"):
        fail("reserved proof-card-023 missing or not marked reserved")
    required_home = ["Turn AI work into verified capability", "Proof Treasury 003–005", "Mission OS", "Ascension", "Proof Observatory"]
    for needle in required_home:
        if needle not in index: fail(f"homepage missing: {needle}")
    if "v72 Platinum World Launch System" not in index:
        fail("v72 visual system marker missing")
    # Stale copy checks
    stale = ["17 Proof Cards", "Proof Cards 001–019"]
    for p in [site/"index.html", site/"proof-cards.html"]:
        text=p.read_text(encoding="utf-8", errors="replace")
        for s in stale:
            if s in text: fail(f"stale phrase {s} in {p.name}")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text=p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA Ascension Website v72 verification passed.")
if __name__=="__main__":
    main()
