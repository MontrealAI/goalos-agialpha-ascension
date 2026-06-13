#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args()
    site=Path(args.site)
    errors=[]
    required=['index.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']+[f'proof-card-{i:03d}.html' for i in range(1,11)]
    for r in required:
        if not (site/r).exists(): errors.append(f'missing {r}')
    alltxt=''
    for p in site.rglob('*.html'):
        txt=p.read_text(encoding='utf-8',errors='replace')
        alltxt += txt + '\n'
        for marker in ['AGIALPHA','Evidence Docket','RSI','Proof Card']:
            if marker not in txt and p.name.startswith('proof-card'):
                errors.append(f'{p.name} missing {marker}')
    index=(site/'index.html').read_text(encoding='utf-8',errors='replace') if (site/'index.html').exists() else ''
    for i in range(1,11):
        if f'proof-card-{i:03d}.html' not in index: errors.append(f'homepage missing proof-card-{i:03d}.html link')
    forbidden=['Recursive_SI','recursive.com','Launching Recursive','First Steps Toward Automated AI Research']
    for f in forbidden:
        if f in alltxt: errors.append(f'forbidden named-startup reference: {f}')
    secret_patterns=[r'AKIA[0-9A-Z]{16}', r'(?i)private[_-]?key\s*[:=]', r'(?i)seed\s+phrase']
    for pat in secret_patterns:
        if re.search(pat, alltxt): errors.append(f'secret-like pattern: {pat}')
    if errors:
        print('Verification failed:'); [print(' - '+e) for e in errors]; sys.exit(1)
    print('Institutional Proof Atlas v19 verification passed.')
if __name__=='__main__': main()
