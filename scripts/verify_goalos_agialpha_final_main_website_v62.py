#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","proof-card-028.html","evidence-docket.html","system-map.html",
    "execution-moat.html","roadmap.html","research.html","routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,23)] + [f"proof-card-{i:03d}.html" for i in range(24,29)]

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
    pc28 = (site / "proof-card-028.html").read_text(encoding="utf-8", errors="replace")
    if "proof-card-028.html" not in index:
        fail("homepage does not link proof-card-028.html")
    if "proof-card-028.html" not in atlas:
        fail("atlas does not link proof-card-028.html")
    required_pc28 = [
        "Ascension Helix",
        "SOTA is a measurement. Ascension is the mission",
        "Ascension is proof-governed compounding intelligence",
        "$AGIALPHA makes proof operational",
        "Large multi-agent constellation",
        "Evidence Docket",
        "Recursive Self",
        "Claim boundary",
    ]
    for needle in required_pc28:
        if needle not in pc28:
            fail(f"Proof Card 028 missing: {needle}")
    if "pc028-extra-visual-hardening" not in pc28:
        fail("Proof Card 028 visual hardening missing")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v62 verification passed.")

if __name__ == "__main__":
    main()
