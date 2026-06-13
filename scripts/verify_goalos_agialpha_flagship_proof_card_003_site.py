#!/usr/bin/env python3
from pathlib import Path
SITE=Path('site')
required=['index.html','flagship-use-case.html','proof-card-003.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','trust-room-playbook.html','share-flagship.html','data/examples/proof-card-003-sovereign-ai-procurement-control-tower.json','evidence/examples/proof-card-003-evidence-docket-template.json']
missing=[p for p in required if not (SITE/p).exists()]
if missing:
    raise SystemExit('Missing generated files: '+', '.join(missing))
text='\n'.join((SITE/p).read_text(encoding='utf-8',errors='replace') for p in required if (SITE/p).suffix in ['.html','.json'])
lower_text=text.lower()
for n in ['agialpha','sovereign ai procurement control tower','proof card 003','recursive self-improvement','proof-backed upgrade rights','reviewerbondregistry','proofsubmissionregistry','selectiongate']:
    if n not in lower_text:
        raise SystemExit(f'Missing required marker: {n}')
for pat in ['PRIVATE_KEY','SEED_PHRASE','MNEMONIC','DEPLOYER_PRIVATE_KEY','BEGIN PRIVATE KEY']:
    if pat in text:
        raise SystemExit('Secret-like marker found: '+pat)
print('Flagship Proof Card 003 site verification passed.')
