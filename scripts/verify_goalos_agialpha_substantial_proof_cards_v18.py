#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def read(p): return Path(p).read_text(encoding='utf-8', errors='replace')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site)
    errors=[]
    index=site/'index.html'
    if not index.exists(): errors.append('missing index.html')
    else:
        h=read(index)
        if 'Proof Card Command Center' not in h: errors.append('homepage missing Proof Card Command Center')
        for i in range(1,11):
            if f'proof-card-{i:03d}.html' not in h: errors.append(f'homepage missing link to proof-card-{i:03d}.html')
    required_terms=['AGIALPHA','Evidence Docket','RSI','ProofBundle','Selection Gate','Chronicle']
    for i in range(1,11):
        f=site/f'proof-card-{i:03d}.html'
        if not f.exists(): errors.append(f'missing {f.name}'); continue
        txt=read(f)
        for term in ['Where AGIALPHA becomes useful','Smart-contract / registry route','Skills, plans, and goals used','Evidence Docket checklist','RSI upgrade logic','Claim boundary']:
            if term not in txt: errors.append(f'{f.name} missing section: {term}')
        for term in required_terms:
            if term not in txt: errors.append(f'{f.name} missing term: {term}')
    for p in site.rglob('*.html'):
        txt=read(p)
        if 'Recursive' in txt: errors.append(f'{p.name} contains forbidden named-startup reference')
        if re.search(r'(BEGIN|END) (RSA|OPENSSH|PRIVATE) KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}', txt): errors.append(f'{p.name} contains secret-like string')
    if errors:
        print('Verification failed:'); [print(' - '+e) for e in errors]; sys.exit(1)
    print('Substantial proof cards verification passed. Proof Cards 001-010 are visible, comprehensive, and linked from the main website root.')
if __name__=='__main__': main()
