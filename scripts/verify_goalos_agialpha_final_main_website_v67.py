#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = [
    "index.html","proof-treasury-simulation-004.html","proof-treasury-simulation-003.html",
    "mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,23)] + [f"proof-card-{i:03d}.html" for i in range(24,32)]

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
    sim004 = (site / "proof-treasury-simulation-004.html").read_text(encoding="utf-8", errors="replace")
    if "proof-treasury-simulation-004.html" not in index:
        fail("homepage does not link Proof Treasury Simulation 004")
    for needle in [
        "No stress clearance, no institutional scale",
        "Institutional Stress Gauntlet",
        "Sovereign Capacity Reserve",
        "Proof Treasury Simulation 004",
        "100,000,000",
        "Institutional scale is partially allowed",
        "No token movement",
        "No Mainnet broadcast",
    ]:
        if needle not in sim004:
            fail(f"Simulation 004 page missing: {needle}")
    if ".sim004-table td" not in sim004 or "color:#06111f" not in sim004:
        fail("Simulation 004 visual contrast hardening missing")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest",".md",".csv"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v67 verification passed.")

if __name__ == "__main__":
    main()
