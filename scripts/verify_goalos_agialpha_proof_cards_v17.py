#!/usr/bin/env python3
from pathlib import Path
import argparse,re
ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--expected',type=int,default=10); args=ap.parse_args(); site=Path(args.site); errors=[]
idx=site/'index.html'
if not idx.exists(): errors.append('Missing index.html')
else:
    text=idx.read_text(encoding='utf-8',errors='replace')
    if 'GOALOS_PROOF_CARDS_V17_START' not in text: errors.append('Homepage missing proof-card command center marker')
    for i in range(1,args.expected+1):
        if f'proof-card-{i:03d}.html' not in text: errors.append(f'Homepage missing link to proof-card-{i:03d}.html')
required=['proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']+[f'proof-card-{i:03d}.html' for i in range(1,args.expected+1)]
for r in required:
    p=site/r
    if not p.exists(): errors.append(f'Missing {r}'); continue
    t=p.read_text(encoding='utf-8',errors='replace')
    if r.startswith('proof-card-'):
        for m in ['AGIALPHA','Evidence Docket','RSI']:
            if m not in t: errors.append(f'{r} missing {m}')
    if re.search(r'recursive\.com|recursive-org|@Recursive|Recursive_SI|Launching Recursive|First Steps Toward Automated AI Research', t, re.I): errors.append(f'{r} contains forbidden competitor reference')
all_text='\n'.join(p.read_text(encoding='utf-8',errors='replace') for p in site.glob('*.html'))
if re.search(r'PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=', all_text): errors.append('Secret-like string detected')
if errors:
    print('Verification failed:'); [print(' -',e) for e in errors]; raise SystemExit(1)
print(f'Main website proof cards verification passed: Proof Cards 001-{args.expected:03d} are present, linked, and complete.')
