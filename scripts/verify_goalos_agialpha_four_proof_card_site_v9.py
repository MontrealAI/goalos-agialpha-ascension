#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys
required_pages = ['index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
required_terms = ['AGIALPHA','Proof Card 004','Persistent Goal-Seeking Intelligence','Evidence Docket','Selection Gate','proof-backed upgrade rights','AEPGoalOSCommitRegistry','AEPChronicleRegistry']
forbidden = ['Recursive self-improving superintelligence to automate knowledge discovery', 'Recursive Co-Founders']
secret_re = re.compile(r'(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|[A-Za-z0-9_]*PRIVATE_KEY\s*=)', re.I)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args()
    root=Path(args.site)
    errors=[]
    for p in required_pages:
        if not (root/p).exists(): errors.append(f'missing page: {p}')
    if (root/'index.html').exists():
        idx=(root/'index.html').read_text(errors='ignore')
        for card in ['proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html']:
            if card not in idx: errors.append(f'homepage does not link {card}')
    text='\n'.join(p.read_text(errors='ignore') for p in root.rglob('*') if p.is_file() and p.suffix in ['.html','.json','.xml'])
    for t in required_terms:
        if t not in text: errors.append(f'missing required term: {t}')
    for f in forbidden:
        if f in text: errors.append(f'forbidden text present: {f}')
    if secret_re.search(text): errors.append('possible secret-like string found')
    if errors:
        print('Verification failed:')
        for e in errors: print(' - '+e)
        sys.exit(1)
    print('Four Proof Card Demand Center verification passed.')
if __name__=='__main__': main()
