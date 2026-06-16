#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED_BASE = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","proof-card-030.html","evidence-docket.html","system-map.html",
    "execution-moat.html","roadmap.html","research.html","routes.json","sitemap.xml","site-status.json"
]
REQUIRED_PROOF_CARDS = [f"proof-card-{i:03d}.html" for i in range(1,23)] + [f"proof-card-{i:03d}.html" for i in range(24,31)]
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
    for name in REQUIRED_BASE + REQUIRED_PROOF_CARDS:
        if not (site / name).exists():
            fail(f"missing required page/file: {name}")
    if (site / "proof-card-023.html").exists():
        fail("proof-card-023.html should remain reserved for later")
    index = (site / "index.html").read_text(encoding="utf-8", errors="replace")
    atlas = (site / "proof-cards.html").read_text(encoding="utf-8", errors="replace")
    pc30 = (site / "proof-card-030.html").read_text(encoding="utf-8", errors="replace")
    if "proof-card-030.html" not in index:
        fail("homepage does not link proof-card-030.html")
    if "proof-card-030.html" not in atlas:
        fail("Proof Card Atlas does not link proof-card-030.html")
    required_pc30 = [
        "Ascension Zenith",
        "SOTA is a measurement",
        "Ascension is the mission",
        "Large specialist-agent institution",
        "$AGIALPHA",
        "Evidence Docket",
        "Claim boundary",
    ]
    for needle in required_pc30:
        if needle not in pc30:
            fail(f"Proof Card 030 missing: {needle}")
    if "pc030-v64-visual-hardening" not in pc30:
        fail("Proof Card 030 visual hardening missing")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v64 verification passed.")

if __name__ == "__main__":
    main()
