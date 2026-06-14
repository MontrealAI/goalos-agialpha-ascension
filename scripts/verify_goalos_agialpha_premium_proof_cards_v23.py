#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys
REQUIRED = [
 'index.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html',
] + [f'proof-card-{i:03d}.html' for i in range(1,12)]
MARKERS = ['AGIALPHA','Evidence Docket','Recursive Self-Improvement','Claim boundary','Large specialist-agent operating theater','AGIALPHA + smart-contract route','Skills, plans, and goals']
BAD = ['recursive.com','recursive-org','Recursive_SI','Launching Recursive','First Steps Toward Automated AI Research']
SECRET = re.compile(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)', re.I)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site)
    errors=[]
    for fn in REQUIRED:
        p=site/fn
        if not p.exists(): errors.append(f'Missing {fn}'); continue
        txt=p.read_text(encoding='utf-8',errors='replace')
        if '<style>' not in txt: errors.append(f'{fn} missing inline style fallback')
        if SECRET.search(txt): errors.append(f'{fn} contains secret-like string')
        for bad in BAD:
            if bad.lower() in txt.lower(): errors.append(f'{fn} contains forbidden named competitor reference: {bad}')
    for i in range(1,12):
        txt=(site/f'proof-card-{i:03d}.html').read_text(encoding='utf-8',errors='replace')
        for marker in MARKERS:
            if marker not in txt: errors.append(f'proof-card-{i:03d}.html missing marker {marker}')
        # substantial enough: require tables and figures
        if txt.count('<table') < 4: errors.append(f'proof-card-{i:03d}.html has too few tables')
        if txt.count('<svg') < 2: errors.append(f'proof-card-{i:03d}.html has too few SVG figures')
    home=(site/'index.html').read_text(encoding='utf-8',errors='replace') if (site/'index.html').exists() else ''
    for i in range(1,12):
        if f'proof-card-{i:03d}.html' not in home: errors.append(f'Homepage missing link to proof-card-{i:03d}.html')
    if errors:
        for e in errors: print('ERROR:',e)
        sys.exit(1)
    print('Premium proof-card atlas verification passed: Proof Cards 001-011 are styled, substantial, and linked.')
if __name__=='__main__': main()
