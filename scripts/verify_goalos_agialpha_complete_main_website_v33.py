#!/usr/bin/env python3
from pathlib import Path
import argparse, re

REQUIRED = ['index.html','start-here.html','personal-proof-sprint.html','proof-sprint-builder.html','use-cases.html','resources.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html'] + [f'proof-card-{i:03d}.html' for i in range(1,18)]
FORBIDDEN = ['PRIVATE_KEY','SEED_PHRASE','MNEMONIC','DEPLOYER_PRIVATE_KEY','MAINNET_RPC_URL=','SEPOLIA_RPC_URL=','recursive.com/articles','github.com/recursive-org']

def read(p): return p.read_text(encoding='utf-8', errors='replace')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args()
    site=Path(args.site)
    missing=[name for name in REQUIRED if not (site/name).exists()]
    if missing: raise SystemExit('Missing required pages: '+', '.join(missing))
    index=read(site/'index.html'); atlas=read(site/'proof-cards.html')
    for i in range(1,18):
        href=f'proof-card-{i:03d}.html'
        if href not in index: raise SystemExit(f'Homepage missing {href}')
        if href not in atlas: raise SystemExit(f'Atlas missing {href}')
        text=read(site/href)
        if '<style' not in text: raise SystemExit(f'{href} missing inline CSS fallback')
    for name in ['index.html','start-here.html','proof-sprint-builder.html','proof-cards.html','evidence-docket.html']:
        t=read(site/name)
        for bad in FORBIDDEN:
            if bad.lower() in t.lower(): raise SystemExit(f'Forbidden public string {bad} in {name}')
    for marker in ['AI makes action cheap','GoalOS makes progress provable','30-Day GoalOS Money Sprint','Proof Card Command Center','Evidence Docket','Start in 10 minutes']:
        if marker not in index: raise SystemExit(f'Homepage missing marker: {marker}')
    if 'function generate()' not in read(site/'proof-sprint-builder.html'):
        raise SystemExit('Sprint builder missing generator JS')
    print('Complete main website v33 verification passed.')

if __name__ == '__main__': main()
