#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def fail(msg):
    print('ERROR:',msg)
    raise SystemExit(1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site)
    required=['index.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']+[f'proof-card-{i:03d}.html' for i in range(1,12)]
    for f in required:
        if not (site/f).exists(): fail(f'missing {f}')
    root=(site/'index.html').read_text(encoding='utf-8',errors='replace')
    for i in range(1,12):
        if f'proof-card-{i:03d}.html' not in root: fail(f'homepage missing proof card {i:03d} link')
        txt=(site/f'proof-card-{i:03d}.html').read_text(encoding='utf-8',errors='replace')
        for term in ['AGIALPHA','Evidence Docket','Recursive Self-Improvement','Claim boundary','Skills','Plans','Goals']:
            if term not in txt: fail(f'proof-card-{i:03d} missing {term}')
    combined='\n'.join((site/f).read_text(encoding='utf-8',errors='replace') for f in required)
    bad_secret=re.search(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)', combined, re.I)
    if bad_secret: fail('secret-like string found')
    bad_ref=re.search(r'(recursive\.com|recursive-org|First Steps Toward Automated AI Research)', combined, re.I)
    if bad_ref: fail('named competitor reference found')
    print('Premium proof-card system verification passed for Proof Cards 001-011.')
if __name__=='__main__': main()
