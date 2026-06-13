#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys
REQUIRED = ['index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html','proof-card-005.html','proof-card-006.html','proof-card-007.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
SECRET_RE = re.compile(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)', re.I)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site); errors=[]
    for f in REQUIRED:
        if not (site/f).exists(): errors.append('missing '+f)
    if errors: print('\n'.join(errors)); sys.exit(1)
    index=(site/'index.html').read_text(encoding='utf-8', errors='ignore')
    gallery=(site/'proof-cards.html').read_text(encoding='utf-8', errors='ignore')
    for n in ['001','002','003','004','005','006','007']:
        if f'proof-card-{n}.html' not in index: errors.append(f'homepage does not link proof-card-{n}.html')
        if f'proof-card-{n}.html' not in gallery: errors.append(f'gallery does not link proof-card-{n}.html')
        txt=(site/f'proof-card-{n}.html').read_text(encoding='utf-8', errors='ignore')
        for term in ['AGIALPHA','Evidence Docket','Proof Card','claim boundary']:
            if term not in txt: errors.append(f'proof-card-{n}.html missing {term}')
    pc7=(site/'proof-card-007.html').read_text(encoding='utf-8', errors='ignore')
    for term in ['Sovereign Enterprise Autoresearch Reactor','Large multi-agent autonomous coordination fabric','Skills used','Plans used','Goals used','AEPAutoresearchPortfolioRegistry','AEPBenchmarkRegistry','AEPSlashingCourt','AlphaWorkUnitLedger','TreasuryRouter','Kardashev','Recursive self-improvement']:
        if term not in pc7: errors.append('proof-card-007 missing '+term)
    full='\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in site.glob('*.html'))
    forbidden=['recursive.com','Recursive_SI','First Steps Toward Automated AI Research']
    for bad in forbidden:
        if bad in full: errors.append('forbidden competitor marker found: '+bad)
    if SECRET_RE.search(full): errors.append('secret-like string found in generated site')
    if errors: print('Verification failed:'); print('\n'.join(errors)); sys.exit(1)
    print('Main website Proof Cards 001-007 integration verified.')
if __name__ == '__main__': main()
