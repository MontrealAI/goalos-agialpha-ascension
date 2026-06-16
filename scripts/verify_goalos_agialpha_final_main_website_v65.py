#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = [
    "index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html",
    "proof-cards.html","proof-card-031.html","evidence-docket.html","system-map.html",
    "execution-moat.html","roadmap.html","research.html","routes.json","sitemap.xml","site-status.json"
] + [f"proof-card-{i:03d}.html" for i in range(1,23)] + [f"proof-card-{i:03d}.html" for i in range(24,32)]
FORBIDDEN = ["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--site", default="site"); args = ap.parse_args(); site = Path(args.site)
    if not site.exists(): fail(f"missing site folder: {site}")
    for name in REQUIRED:
        if not (site/name).exists(): fail(f"missing required page/file: {name}")
    if (site/'proof-card-023.html').exists(): fail('proof-card-023.html should remain reserved for later')
    index = (site/'index.html').read_text(encoding='utf-8', errors='replace')
    atlas = (site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
    pc31 = (site/'proof-card-031.html').read_text(encoding='utf-8', errors='replace')
    if 'proof-card-031.html' not in index: fail('homepage does not link Proof Card 031')
    if 'proof-card-031.html' not in atlas: fail('atlas does not link Proof Card 031')
    required = [
        'Ascension Helios','proof-governed value-to-energy flywheel','SOTA vs Ascension Helios',
        'Large specialist-agent institution','$AGIALPHA as the capacity rail','AI-first startup domains',
        'Skills, plans, contracts, goals','Contract-call surface','RSI through proof','Metrics that matter',
        'Claim boundary'
    ]
    for needle in required:
        if needle not in pc31: fail(f'Proof Card 031 missing: {needle}')
    if '.pc31-table td' not in pc31 or 'color:#06111f' not in pc31: fail('Proof Card 031 visual hardening missing')
    if list(site.rglob('*.zip')): fail('generated public site contains ZIP files')
    for p in site.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.html','.json','.txt','.xml','.webmanifest'}:
            text = p.read_text(encoding='utf-8', errors='replace').lower()
            for bad in FORBIDDEN:
                if bad.lower() in text: fail(f'forbidden public string {bad} in {p}')
    print('GoalOS AGIALPHA final main website v65 verification passed.')
if __name__ == '__main__': main()
