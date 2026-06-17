#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
STABLE=list(range(1,23))+list(range(24,32))
REQUIRED=["index.html","executive-brief.html","proof-observatory.html","proof-cards.html","ascension.html","proof-treasury.html","proof-treasury-simulation-003.html","proof-treasury-simulation-004.html","proof-treasury-simulation-005.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html","proof-card-023.html","routes.json","sitemap.xml","site-status.json"]+[f"proof-card-{i:03d}.html" for i in STABLE]
FORBIDDEN=["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]
def fail(m): print("FAIL:",m); sys.exit(1)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--site",default="site"); args=ap.parse_args(); site=Path(args.site)
    if not site.exists(): fail(f"missing site {site}")
    for name in REQUIRED:
        if not (site/name).exists(): fail(f"missing {name}")
    index=(site/"index.html").read_text(encoding="utf-8",errors="replace"); atlas=(site/"proof-cards.html").read_text(encoding="utf-8",errors="replace")
    for i in STABLE:
        fn=f"proof-card-{i:03d}.html"
        if fn not in atlas: fail(f"atlas missing {fn}")
    markers=["v74 ASI Aura + RSI Dynamic Ascension Visual System","asi-canvas","asi-field","asi-rsi-helix","data-asi-count","ASI horizon bounded by proof"]
    for needle in markers:
        if needle not in index: fail(f"homepage missing dynamic marker {needle}")
    for name in ["executive-brief.html","proof-observatory.html","ascension.html","proof-treasury.html"]:
        text=(site/name).read_text(encoding="utf-8",errors="replace")
        if "asi-hero" not in text or "asi-field" not in text: fail(f"{name} missing ASI dynamic hero/effects")
    for phrase in ["17 Proof Cards","Proof Cards 001–019"]:
        if phrase in index or phrase in atlas: fail(f"stale phrase {phrase}")
    if list(site.rglob("*.zip")): fail("generated public site contains ZIP files")
    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".html",".json",".txt",".xml",".webmanifest"}:
            txt=p.read_text(encoding="utf-8",errors="replace")
            for bad in FORBIDDEN:
                if bad.lower() in txt.lower(): fail(f"forbidden public string {bad} in {p}")
    print("GoalOS AGIALPHA Ascension Website v74 verification passed.")
if __name__=="__main__": main()
