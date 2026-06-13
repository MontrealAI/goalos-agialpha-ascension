#!/usr/bin/env python3
from pathlib import Path
import argparse,sys
REQ=['index.html','proof-cards.html']+[f'proof-card-{i:03d}.html' for i in range(1,10)]+['agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
NEED=['Proof Card 009','Cyber-Sovereign Execution Moat','AGIALPHA','Evidence Docket','Selection Gate','Recursive Self-Improvement']
FORBID=['recursive.com','Recursive_SI','First Steps Toward Automated AI Research','PRIVATE_KEY','BEGIN PRIVATE KEY']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); a=ap.parse_args(); s=Path(a.site); errors=[]
    for f in REQ:
        if not (s/f).exists(): errors.append('missing '+f)
    text='\n'.join(p.read_text(errors='ignore') for p in s.glob('*.html'))
    for n in NEED:
        if n not in text: errors.append('missing '+n)
    for n in FORBID:
        if n in text: errors.append('forbidden '+n)
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    print('Main website Proof Cards 001-009 integration verified.')
if __name__=='__main__': main()
