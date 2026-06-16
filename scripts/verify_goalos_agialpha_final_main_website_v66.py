#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","proof-treasury-simulation-003.html","evidence-docket.html",
    "system-map.html","execution-moat.html","roadmap.html","research.html",
    "routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in list(range(1,23)) + list(range(24,32))]

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
    sim = (site / "proof-treasury-simulation-003.html").read_text(encoding="utf-8", errors="replace")
    if "proof-treasury-simulation-003.html" not in index:
        fail("homepage does not link simulation 003")
    required_sim = [
        "No external replay, no capacity scale",
        "External Replay Market",
        "Capacity Auction",
        "Proof Treasury Simulation 003 completed",
        "10,000,000",
        "870",
        "Generated public site contains no ZIP",
    ]
    # Last phrase may not be present; use hardening checks below
    for needle in required_sim[:-1]:
        if needle not in sim:
            fail(f"simulation page missing: {needle}")
    if ".pts-table td" not in sim or "color:#06111f" not in sim:
        fail("simulation visual contrast hardening missing")
    if list(site.rglob("*.zip")):
        fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest",".md",".csv"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower():
                    fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v66 verification passed.")

if __name__ == "__main__":
    main()
