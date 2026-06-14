#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args=ap.parse_args()
    site=Path(args.site)
    errors=[]
    pages=['index.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html']+[f'proof-card-{i:03d}.html' for i in range(1,13)]
    for p in pages:
        if not (site/p).exists(): errors.append(f'missing {p}')
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    idx=(site/'index.html').read_text(encoding='utf-8', errors='replace')
    gallery=(site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
    for i in range(1,13):
        href=f'proof-card-{i:03d}.html'
        if href not in idx: errors.append(f'homepage does not link {href}')
        if href not in gallery: errors.append(f'gallery does not link {href}')
        txt=(site/href).read_text(encoding='utf-8', errors='replace')
        for needle in ['AGIALPHA','Evidence Docket','RSI','Claim boundary','<style>','Visual operating flow']:
            if needle not in txt: errors.append(f'{href} missing {needle}')
        if i==12:
            for needle in ['AI-Startup Venture Grid','Market Intelligence Swarm','Revenue Proof','AEPVentureMandateRegistry','Proof-to-portfolio roadmap']:
                if needle not in txt: errors.append(f'{href} missing {needle}')
    combined='\n'.join((site/p).read_text(encoding='utf-8', errors='replace') for p in pages)
    forbidden=['recursive.com','recursive-org','Recursive\'s','Recursive’s','@Recursive_SI','Launching Recursive']
    for f in forbidden:
        if f in combined: errors.append(f'forbidden named-competitor reference found: {f}')
    secret_re=re.compile(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)', re.I)
    if secret_re.search(combined): errors.append('secret-like string found')
    if errors:
        print('Verification failed:')
        print('\n'.join(errors))
        sys.exit(1)
    print('Proof Card 012 and Proof Cards 001-012 main website verification passed.')
if __name__=='__main__': main()
