#!/usr/bin/env python3
import argparse, re, sys
from pathlib import Path
REQUIRED = ['index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html','proof-card-005.html','proof-card-006.html','proof-card-007.html','proof-card-008.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
MUST_HAVE = ['AGIALPHA','Evidence Docket','RSI','proof-backed upgrade rights','AEPGoalOSCommitRegistry','AEPSelectionGate','TreasuryRouter','Sovereign Corporate Capability Foundry']
SECRET_PATTERNS=[r'PRIVATE_KEY\s*=',r'API_KEY\s*=',r'BEGIN PRIVATE KEY',r'seed phrase',r'mnemonic']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site)
    errors=[]
    for f in REQUIRED:
        if not (site/f).exists(): errors.append(f'missing page: {f}')
    if (site/'index.html').exists():
        idx=(site/'index.html').read_text(encoding='utf-8', errors='ignore')
        for n in range(1,9):
            if f'proof-card-{n:03d}.html' not in idx and f'proof-card-00{n}.html' not in idx:
                # expected uses 001 style
                errors.append(f'homepage missing proof-card-{n:03d}.html link')
    forbidden = 'Re' + 'cursive'
    pc8=(site/'proof-card-008.html')
    if pc8.exists():
        txt=pc8.read_text(encoding='utf-8', errors='ignore')
        for m in MUST_HAVE:
            if m not in txt: errors.append(f'Proof Card 008 missing marker: {m}')
        if forbidden in txt: errors.append('Proof Card 008 contains forbidden named-startup reference')
    alltext='\n'.join([p.read_text(encoding='utf-8', errors='ignore') for p in site.glob('*.html')])
    for pat in SECRET_PATTERNS:
        if re.search(pat, alltext, re.I): errors.append(f'secret-like pattern: {pat}')
    if forbidden in alltext: errors.append('site contains forbidden named-startup reference')
    if errors:
        print('Verification failed:'); [print('-',e) for e in errors]; sys.exit(1)
    print('Main website Proof Cards 001-008 integration verified.')
if __name__ == '__main__': main()
