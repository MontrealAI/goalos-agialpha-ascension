
#!/usr/bin/env python3
from pathlib import Path
import argparse, re, json, sys
MARKER='GOALOS_AGIALPHA_TRIPLE_PROOF_CARD_DEMAND_CENTER_V8'
REQUIRED=['index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','flagship-use-case.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html','data/proof-cards.json','evidence/proof-card-001-evidence-docket-template.json','evidence/proof-card-002-evidence-docket-template.json','evidence/proof-card-003-evidence-docket-template.json']
TERMS=['AGIALPHA','Evidence Docket','Proof Card','ReputationRegistry','ProofCredentialRegistry','ProofCardRegistry','AEPSelectionGate','AEPChronicleRegistry']
FORBIDDEN=[r'PRIVATE KEY',r'BEGIN RSA PRIVATE KEY',r'BEGIN OPENSSH PRIVATE KEY',r'SECRET_ACCESS_KEY',r'github_pat_',r'sk-[A-Za-z0-9]{20,}',r'Recursive\b']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site); errors=[]
    for p in REQUIRED:
        if not (site/p).exists(): errors.append(f'missing {p}')
    all_text='\n'.join(p.read_text(errors='ignore', encoding='utf-8') for p in site.rglob('*') if p.is_file() and p.suffix.lower() in ['.html','.json','.txt','.xml'])
    if MARKER not in all_text: errors.append('missing build marker')
    for t in TERMS:
        if t not in all_text: errors.append(f'missing term {t}')
    for i in ['001','002','003']:
        txt=(site/f'proof-card-{i}.html').read_text(encoding='utf-8') if (site/f'proof-card-{i}.html').exists() else ''
        for t in ['The buyer problem','The proof mission','Where AGIALPHA becomes useful','Smart-contract / registry route','Evidence Docket checklist','Sovereign RSI upgrade logic','Claim boundary','Illustrative until live Evidence Docket is completed']:
            if t not in txt: errors.append(f'proof-card-{i}.html missing {t}')
        if len(re.findall(r'<section', txt)) < 6: errors.append(f'proof-card-{i}.html too short')
    idx=(site/'index.html').read_text(encoding='utf-8') if (site/'index.html').exists() else ''
    for i in ['001','002','003']:
        if f'proof-card-{i}.html' not in idx: errors.append(f'index missing proof-card-{i}.html')
    for pat in FORBIDDEN:
        if re.search(pat, all_text): errors.append(f'forbidden pattern found: {pat}')
    try:
        data=json.loads((site/'data/proof-cards.json').read_text(encoding='utf-8'))
        if len(data.get('proof_cards',[])) != 3: errors.append('proof-cards.json must have exactly three cards')
    except Exception as e: errors.append(f'proof-cards json invalid: {e}')
    if errors:
        print('Verification failed:')
        for e in errors: print(' -', e)
        sys.exit(1)
    print('Triple Proof Card Demand Center v8 verification passed.')
if __name__=='__main__': main()
