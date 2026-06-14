#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args = ap.parse_args()
    site = Path(args.site)
    errors = []
    for i in range(1,14):
        p = site / f'proof-card-{i:03d}.html'
        if not p.exists():
            errors.append(f'missing {p.name}')
            continue
        txt = p.read_text(encoding='utf-8', errors='replace')
        for token in ['AGIALPHA','Evidence Docket','RSI','Claim boundary','<style>','<table','<svg']:
            if token not in txt:
                errors.append(f'{p.name} missing {token}')
        if len(txt) < 12000:
            errors.append(f'{p.name} appears too thin')
    idx = site / 'index.html'
    gal = site / 'proof-cards.html'
    if not idx.exists(): errors.append('missing index.html')
    if not gal.exists(): errors.append('missing proof-cards.html')
    if idx.exists():
        txt = idx.read_text(encoding='utf-8', errors='replace')
        if 'proof-card-013.html' not in txt: errors.append('homepage does not link Proof Card 013')
        if 'GOALOS_PROOF_CARD_ATLAS_START' not in txt and 'Proof Card Command Center' not in txt: errors.append('homepage missing Proof Card Command Center')
    if gal.exists() and 'proof-card-013.html' not in gal.read_text(encoding='utf-8', errors='replace'):
        errors.append('gallery does not link Proof Card 013')
    secret_pat = re.compile(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)', re.I)
    for p in site.glob('*.html'):
        txt = p.read_text(encoding='utf-8', errors='replace')
        if secret_pat.search(txt): errors.append(f'secret-like string in {p.name}')
        if 'recursive.com' in txt.lower() or 'recursive-org' in txt.lower(): errors.append(f'named competitor URL/repo in {p.name}')
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
    print('Proof Cards 001-013 main website verification passed.')
if __name__ == '__main__':
    main()
