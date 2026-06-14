#!/usr/bin/env python3
from pathlib import Path
import argparse

def fail(msg): raise SystemExit(f"ERROR: {msg}")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site)
    required=['index.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html']+[f'proof-card-{i:03d}.html' for i in range(1,16)]
    for name in required:
        if not (site/name).exists(): fail(f'missing {name}')
    index=(site/'index.html').read_text(encoding='utf-8',errors='replace'); atlas=(site/'proof-cards.html').read_text(encoding='utf-8',errors='replace')
    for i in range(1,16):
        slug=f'proof-card-{i:03d}.html'
        if slug not in index: fail(f'homepage does not link {slug}')
        if slug not in atlas: fail(f'atlas does not link {slug}')
        page=(site/slug).read_text(encoding='utf-8',errors='replace')
        for marker in ['AGIALPHA','Evidence Docket','RSI','Claim boundary','<table','<svg','<style']:
            if marker not in page: fail(f'{slug} missing marker {marker}')
    corpus='\n'.join((site/name).read_text(encoding='utf-8',errors='replace') for name in required)
    for b in ['PRIVATE_KEY','MNEMONIC','SEED_PHRASE','DEPLOYER_PRIVATE_KEY','recursive.com','recursive-org','first-steps-toward-automated-ai-research']:
        if b in corpus: fail(f'forbidden public string found: {b}')
    print('Main website Proof Cards 001-015 verification passed.')
if __name__=='__main__': main()
