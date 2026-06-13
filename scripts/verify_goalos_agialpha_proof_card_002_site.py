#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args=ap.parse_args()
    site=Path(args.site)
    required=[
        'index.html','sovereign-procurement-trust-room.html','proof-card-001.html','proof-card-002.html','agialpha-contract-flow.html','sovereign-rsi-loop.html','proof-mission-002.html','share-sovereign-trust-room.html','data/proof-card-002-sovereign-trust-room.json','evidence/proof-card-002-evidence-docket-template.json'
    ]
    missing=[f for f in required if not (site/f).exists()]
    if missing:
        raise SystemExit('Missing generated files: '+', '.join(missing))
    all_text='\n'.join((site/f).read_text(encoding='utf-8', errors='replace') for f in required if (site/f).suffix in ['.html','.json'])
    must=['Buyer Rescue Workflow','AGIALPHA','AEPGoalOSCommitRegistry','ProofSubmissionRegistry','ProofCardRegistry','ReputationRegistry','AEPSelectionGate','RSI','proof-backed upgrade rights','Sovereign Procurement Trust Room']
    absent=[m for m in must if m not in all_text]
    if absent:
        raise SystemExit('Missing required content markers: '+', '.join(absent))
    unsafe=['guaranteed return','investment return','achieved AGI','achieved ASI','legally approved','tax approved','security approved']
    bad=[u for u in unsafe if u.lower() in all_text.lower()]
    if bad:
        raise SystemExit('Unsafe claim markers found: '+', '.join(bad))
    if re.search(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL\s*=)', all_text):
        raise SystemExit('Potential secret-like string found in generated pages')
    print('Proof Card 002 website verification passed.')
if __name__=='__main__': main()
