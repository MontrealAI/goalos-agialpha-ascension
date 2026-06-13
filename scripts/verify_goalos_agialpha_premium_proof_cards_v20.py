
#!/usr/bin/env python3
from pathlib import Path
import argparse, re, json

def fail(msg):
    print('ERROR:', msg)
    raise SystemExit(1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--site', default='site')
    args=p.parse_args()
    site=Path(args.site)
    required=['index.html','proof-cards.html']+[f'proof-card-{i:03d}.html' for i in range(1,11)]+['agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html','assets/proof-atlas-v20.css']
    missing=[x for x in required if not (site/x).exists()]
    if missing: fail('missing pages: '+', '.join(missing))
    index=(site/'index.html').read_text(encoding='utf-8', errors='replace')
    if 'proof-card-command-center' not in index: fail('homepage missing proof-card command center')
    for i in range(1,11):
        if f'proof-card-{i:03d}.html' not in index and f'proof-card-{i:03d}.html' not in (site/'proof-cards.html').read_text(encoding='utf-8', errors='replace'):
            fail(f'proof card {i:03d} not linked')
        text=(site/f'proof-card-{i:03d}.html').read_text(encoding='utf-8', errors='replace')
        need=['In plain English','Visual operating overview','Large specialist-agent operating theater','Skills used','Plans used','Goals and success criteria','AGIALPHA','Evidence Docket checklist','Recursive Self-Improvement logic','Claim boundary','FAQ','Glossary']
        for n in need:
            if n not in text: fail(f'proof-card-{i:03d} missing section {n}')
        if len(text) < 18000: fail(f'proof-card-{i:03d} too thin ({len(text)} chars)')
    combined='\n'.join(p.read_text(encoding='utf-8',errors='replace') for p in site.glob('*.html'))
    forbidden_patterns=[r'recursive\.com', r'recursive-org', r'First Steps Toward Automated AI Research']
    for f in forbidden_patterns:
        if re.search(f, combined, re.I): fail(f'forbidden competitor reference: {f}')
    secret_patterns=[r'PRIVATE_KEY',r'SEED_PHRASE',r'MNEMONIC',r'RPC_URL\s*=',r'DEPLOYER_PRIVATE_KEY']
    for pat in secret_patterns:
        if re.search(pat, combined, re.I): fail(f'secret-like pattern found: {pat}')
    if 'AGIALPHA' not in combined: fail('AGIALPHA missing')
    if 'Evidence Docket' not in combined: fail('Evidence Docket missing')
    if 'Selection Gate' not in combined: fail('Selection Gate missing')
    print(json.dumps({'status':'passed','proof_cards':10,'site':str(site)}, indent=2))

if __name__=='__main__': main()
