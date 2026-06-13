#!/usr/bin/env python3
from pathlib import Path
import argparse
ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site)
req=[f'proof-card-{i:03d}.html' for i in range(1,11)]+['index.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
missing=[p for p in req if not (site/p).exists()]
if missing: raise SystemExit('Missing pages: '+', '.join(missing))
text='\n'.join((site/p).read_text(errors='ignore') for p in req)
for marker in ['Proof Card 010','Cyber-Sovereign Proof Benchmark Market','AGIALPHA','Evidence Docket','AEPSelectionGate','Recursive Self-Improvement','Proof Cards 001-010']:
    if marker not in text: raise SystemExit('Missing marker: '+marker)
for forbidden in ['Recursive_SI','recursive.com','recursive-org','First Steps Toward Automated AI Research','Launching Recursive']:
    if forbidden.lower() in text.lower(): raise SystemExit('Forbidden named-startup reference found')
for secret in ['ghp_','BEGIN PRIVATE KEY','AKIA','OPENAI_API_KEY','PRIVATE_KEY=']:
    if secret in text: raise SystemExit('Secret-like string found')
print('Main website Proof Cards 001-010 integration verified.')
