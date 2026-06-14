#!/usr/bin/env python3
from pathlib import Path
import argparse, re

REQUIRED = [
 'index.html','start-here.html','personal-proof-sprint.html','proof-sprint-builder.html','use-cases.html','resources.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html'
] + [f'proof-card-{i:03d}.html' for i in range(1,18)]
FORBIDDEN = ['recursive.com','recursive-org','Recursive_SI','PRIVATE_KEY','SEED_PHRASE','MNEMONIC','DEPLOYER_PRIVATE_KEY']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args = ap.parse_args()
    site = Path(args.site)
    missing = [p for p in REQUIRED if not (site / p).exists()]
    if missing:
        raise SystemExit('Missing required pages: ' + ', '.join(missing))
    index = (site/'index.html').read_text(encoding='utf-8', errors='replace')
    atlas = (site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
    for i in range(1,18):
        ref = f'proof-card-{i:03d}.html'
        if ref not in index:
            raise SystemExit(f'Homepage does not link {ref}')
        if ref not in atlas:
            raise SystemExit(f'Atlas does not link {ref}')
        txt = (site/ref).read_text(encoding='utf-8', errors='replace')
        for needle in ['AGIALPHA','Evidence Docket','RSI','Claim boundary','<svg','<table']:
            if needle not in txt:
                raise SystemExit(f'{ref} missing {needle}')
    all_text = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in site.rglob('*.html'))
    bad = [b for b in FORBIDDEN if b in all_text]
    if bad:
        raise SystemExit('Forbidden string(s) found: ' + ', '.join(bad))
    print('Complete main website v34 verification passed.')

if __name__ == '__main__':
    main()
