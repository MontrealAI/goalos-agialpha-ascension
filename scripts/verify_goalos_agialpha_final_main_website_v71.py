#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
STABLE = list(range(1,23)) + list(range(24,32))
REQUIRED = ["index.html","proof-cards.html","ascension.html","proof-treasury.html","proof-treasury-simulation-003.html","proof-treasury-simulation-004.html","proof-treasury-simulation-005.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html","routes.json","sitemap.xml","site-status.json"] + [f"proof-card-{i:03d}.html" for i in STABLE]
FORBIDDEN = ["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]
def fail(msg): print("FAIL:", msg); sys.exit(1)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--site", default="site"); args=ap.parse_args(); site=Path(args.site)
    if not site.exists(): fail(f"missing site folder: {site}")
    for name in REQUIRED:
        if not (site/name).exists(): fail(f"missing required page/file: {name}")
    if (site/'proof-card-023.html').exists(): fail('Proof Card 023 should remain reserved / absent')
    index=(site/'index.html').read_text(encoding='utf-8', errors='replace')
    atlas=(site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
    ascension=(site/'ascension.html').read_text(encoding='utf-8', errors='replace')
    for i in STABLE:
        fn=f"proof-card-{i:03d}.html"
        if fn not in index: fail(f"homepage missing stable proof card link: {fn}")
        if fn not in atlas: fail(f"atlas missing stable proof card link: {fn}")
    for needle in ["Turn AI work into verified capability", "SOTA is a measurement", "Proof Treasury", "v71 Ascension Helix World Launch Visual System"]:
        if needle not in index and needle not in atlas and needle not in ascension: fail(f"missing v71 marker: {needle}")
    treasury=(site/'proof-treasury.html').read_text(encoding='utf-8', errors='replace')
    for needle in ["Simulation 003", "Simulation 004", "Simulation 005"]:
        if needle not in treasury: fail(f"Proof Treasury hub missing {needle}")
    if list(site.rglob('*.zip')): fail('generated public site contains ZIP files')
    for p in site.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.html','.json','.txt','.xml','.webmanifest'}:
            text=p.read_text(encoding='utf-8', errors='replace')
            for bad in FORBIDDEN:
                if bad.lower() in text.lower(): fail(f"forbidden public string {bad} in {p}")
    print('GoalOS AGIALPHA final main website v71 verification passed.')
if __name__ == '__main__': main()
