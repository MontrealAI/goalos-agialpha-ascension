#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
REQUIRED = ["index.html","mission-os.html","autopilot-mission-builder.html","start-here.html","regular-person.html","personal-proof-sprint.html","proof-sprint-builder.html","use-cases.html","resources.html","proof-cards.html","system-map.html","how-it-works.html","execution-moat.html","roadmap.html","pilot-guide.html","research.html","agialpha-ledger-route.html","sovereign-rsi-control-plane.html","evidence-docket.html","sitemap.xml","robots.txt","manifest.webmanifest","routes.json","site-status.json"] + [f"proof-card-{i:03d}.html" for i in range(1,18)]
FORBIDDEN=["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]
def fail(m): print("FAIL:",m); sys.exit(1)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--site", default="site"); args=ap.parse_args(); site=Path(args.site)
    if not site.exists(): fail(f"missing site folder: {site}")
    for n in REQUIRED:
        if not (site/n).exists(): fail(f"missing required page/file: {n}")
    index=(site/"index.html").read_text(encoding="utf-8", errors="replace"); atlas=(site/"proof-cards.html").read_text(encoding="utf-8", errors="replace"); mission=(site/"mission-os.html").read_text(encoding="utf-8", errors="replace")
    for i in range(1,18):
        fn=f"proof-card-{i:03d}.html"
        if fn not in index: fail(f"homepage does not link {fn}")
        if fn not in atlas: fail(f"atlas does not link {fn}")
    for term in ["GoalOS Mission OS","The Proof OS for Autonomous AI Work","mission-builder","Mission OS Packet Builder","Verifier","Chronicle","AGIALPHA","Evidence Docket","RSI"]:
        if term not in mission: fail(f"mission-os missing {term}")
    if "mission-os-v47-anchor-fix" not in mission: fail("mission builder anchor fallback missing")
    if list(site.rglob("*.zip")): fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest",".js"}:
            text=p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in text.lower(): fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA final main website v47 verification passed.")
if __name__=="__main__": main()
