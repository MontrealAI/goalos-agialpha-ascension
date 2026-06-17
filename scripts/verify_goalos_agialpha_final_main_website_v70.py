#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

STABLE = [f"proof-card-{i:03d}.html" for i in range(1,23)] + [f"proof-card-{i:03d}.html" for i in range(24,32)]
REQUIRED = [
    "index.html","proof-cards.html","ascension.html","proof-treasury.html",
    "proof-treasury-simulation-003.html","proof-treasury-simulation-004.html","proof-treasury-simulation-005.html",
    "mission-os.html","mission-os-paper.html","autopilot-mission-builder.html","evidence-docket.html",
    "routes.json","sitemap.xml","site-status.json"
] + STABLE
FORBIDDEN = ["17 Proof Cards","Proof Cards 001–019","recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]
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
    if (site / "proof-card-023.html").exists():
        fail("proof-card-023.html should remain reserved / absent")
    index = (site/"index.html").read_text(encoding="utf-8", errors="replace")
    atlas = (site/"proof-cards.html").read_text(encoding="utf-8", errors="replace")
    for fn in STABLE:
        if fn not in index:
            fail(f"homepage missing {fn}")
        if fn not in atlas:
            fail(f"atlas missing {fn}")
    for needle in ["Proof Cards 001–022 + 024–031","Proof Treasury 003–005","World Launch Gold Master","SOTA is a measurement. Ascension is the mission."]:
        if needle not in index and needle not in atlas and needle not in (site/"ascension.html").read_text(encoding="utf-8", errors="replace"):
            fail(f"missing key wording: {needle}")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden/stale string {bad} in {p}")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    print("GoalOS AGIALPHA final main website v70 verification passed.")
if __name__ == "__main__":
    main()
