#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","proof-card-026.html","proof-card-025.html","proof-card-024.html",
    "evidence-docket.html","system-map.html","execution-moat.html","roadmap.html","research.html",
    "routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,23)]

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
    if (site / "proof-card-023.html").exists():
        fail("proof-card-023.html should remain reserved for later")
    index = (site / "index.html").read_text(encoding="utf-8", errors="replace")
    atlas = (site / "proof-cards.html").read_text(encoding="utf-8", errors="replace")
    pc26 = (site / "proof-card-026.html").read_text(encoding="utf-8", errors="replace")
    for fn in ["proof-card-026.html", "proof-card-025.html", "proof-card-024.html"]:
        if fn not in index:
            fail(f"homepage does not link {fn}")
        if fn not in atlas:
            fail(f"atlas does not link {fn}")
    required_pc26 = [
        "Ascension Operating Theater",
        "SOTA is a measurement. Ascension is the mission.",
        "Maximum verified effect",
        "Large specialist-agent system",
        "AI-first startup domains",
        "$AGIALPHA proof economy",
        "Ascension readiness ladder",
        "Recursive Self",
        "Claim boundary",
    ]
    for needle in required_pc26:
        if needle not in pc26:
            fail(f"Proof Card 026 missing: {needle}")
    if ".a26-table td" not in pc26 or "color:#05111f" not in pc26:
        fail("Proof Card 026 visual contrast hardening missing")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v60 verification passed.")

if __name__ == "__main__":
    main()
