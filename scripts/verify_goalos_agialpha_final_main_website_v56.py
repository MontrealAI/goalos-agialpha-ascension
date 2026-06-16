#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","proof-card-021.html","evidence-docket.html","system-map.html",
    "execution-moat.html","roadmap.html","research.html","routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,22)]

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
    pc21 = (site / "proof-card-021.html").read_text(encoding="utf-8", errors="replace")
    for i in range(1,22):
        fn = f"proof-card-{i:03d}.html"
        if i == 21 and fn not in index:
            fail(f"homepage does not link {fn}")
        if fn not in atlas and i == 21:
            fail(f"atlas does not link {fn}")
    required_pc21 = [
        "Superintelligence needs proof",
        "$AGIALPHA is the settlement fuel for verified work",
        "Request → Escrow → Execute → Proof → Validate → Settle → Chronicle",
        "Canonical call surface",
        "Large multi-agent settlement theater",
        "Readiness ladder",
        "Claim boundary",
    ]
    for needle in required_pc21:
        if needle not in pc21:
            fail(f"Proof Card 021 missing: {needle}")
    if ".pc21-table td" not in pc21 or "color:#06111f" not in pc21:
        fail("Proof Card 021 contrast hardening missing")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v56 verification passed.")

if __name__ == "__main__":
    main()
