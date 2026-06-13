#!/usr/bin/env python3
from pathlib import Path
import argparse, re, json, sys

REQUIRED_PAGES = [
    'index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html',
    'agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html',
    'data/proof-cards/proof-cards-index.json'
]
REQUIRED_TEXT = {
    'index.html': ['Proof Card 001','Proof Card 002','Proof Card 003','Proof Card 004','AGIALPHA','Sovereign RSI'],
    'proof-cards.html': ['Buyer Rescue Workflow','Sovereign Procurement Trust Room','Sovereign AI Procurement Control Tower','Persistent Goal-Seeking Intelligence Accumulation Engine'],
    'agialpha-ledger-route.html': ['AGIALPHA','JobRegistry','ProofSubmissionRegistry','ReviewerBondRegistry','AEPSelectionGate'],
    'sovereign-rsi-control-plane.html': ['proof-backed upgrade rights','Weak artifact','Selection'],
    'evidence-docket.html': ['Evidence Docket','public-safe evidence','private evidence'],
}
BAD_PATTERNS = [r'PRIVATE_KEY\s*=', r'SEED_PHRASE', r'MNEMONIC', r'DEPLOYER_PRIVATE_KEY\s*=', r'MAINNET_RPC_URL\s*=']

def text(path): return path.read_text(encoding='utf-8', errors='replace')

def main(site):
    site = Path(site)
    errors = []
    for p in REQUIRED_PAGES:
        if not (site/p).exists(): errors.append(f'missing required page/file: {p}')
    for p, needles in REQUIRED_TEXT.items():
        fp = site/p
        if fp.exists():
            t = text(fp)
            for n in needles:
                if n not in t: errors.append(f'{p} missing text: {n}')
    for card_id in ['001','002','003','004']:
        page = site/f'proof-card-{card_id}.html'
        if page.exists():
            t = text(page)
            for n in ['Where AGIALPHA becomes useful','Smart-contract / registry route','Evidence Docket checklist','RSI upgrade logic','Claim boundary']:
                if n not in t: errors.append(f'proof-card-{card_id}.html missing section: {n}')
    idx = text(site/'index.html') if (site/'index.html').exists() else ''
    for href in ['proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html']:
        if href not in idx: errors.append(f'homepage does not link to {href}')
    all_text = ''
    for fp in site.rglob('*'):
        if fp.is_file() and fp.suffix.lower() in ['.html','.json','.js','.css','.txt','.xml']:
            all_text += '\n' + text(fp)
    for pat in BAD_PATTERNS:
        if re.search(pat, all_text, re.I): errors.append(f'found secret-like pattern: {pat}')
    # Do not block legitimate phrase 'Recursive Self-Improvement'; only block explicit startup/site references.
    if re.search(r'Recursive\s*(SI|_SI|\.com)', all_text):
        errors.append('explicit named-startup reference found')
    data_path = site/'data/proof-cards/proof-cards-index.json'
    if data_path.exists():
        try:
            data = json.loads(text(data_path))
            if len(data.get('proofCards', [])) != 4: errors.append('proof-cards-index.json does not contain four cards')
        except Exception as e: errors.append(f'proof-cards-index.json invalid: {e}')
    if errors:
        print('Verification failed:')
        for e in errors: print(' -', e)
        sys.exit(1)
    print('Main website proof cards verification passed.')
    print('Four proof cards are visible, complete, and linked from the main website.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args = ap.parse_args()
    main(args.site)
