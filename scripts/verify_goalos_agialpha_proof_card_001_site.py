#!/usr/bin/env python3
from pathlib import Path
import json, re
SITE=Path('site')
req=['index.html','usage-example.html','proof-card-001.html','smart-contract-flow.html','sovereign-rsi-loop.html','season-001.html','share.html','data/usage-example-proof-card-001.json','evidence/proof-card-001-evidence-docket-template.json']
generated_for_text=['usage-example.html','proof-card-001.html','smart-contract-flow.html','sovereign-rsi-loop.html','season-001.html','share.html','data/usage-example-proof-card-001.json','evidence/proof-card-001-evidence-docket-template.json']
missing=[p for p in req if not (SITE/p).exists()]
if missing: raise SystemExit('Missing files: '+', '.join(missing))
text='\n'.join((SITE/p).read_text(encoding='utf-8',errors='replace') for p in generated_for_text if (SITE/p).suffix in ['.html','.json'])
need=['AGIALPHA','0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA','JobRegistry.postJob','ProofSubmissionRegistry.submitProof','ProofCardRegistry.registerProofCard','ProofCredentialRegistry.issueCredential','ReputationRegistry.recordApprovedProof','AEPEvidenceDocketRegistry.registerEvidenceDocket','RSI','proof-backed upgrade rights']
miss=[x for x in need if x not in text]
if miss: raise SystemExit('Missing terms: '+', '.join(miss))
unsafe=['PRIVATE_KEY','MNEMONIC','API_SECRET','BEGIN PRIVATE KEY','guaranteed return','price target']
for u in unsafe:
    if u.lower() in text.lower(): raise SystemExit('Unsafe term: '+u)
if re.search(r'\bRecursive\b', text): raise SystemExit('Capitalized named-startup reference found')
receipt=json.loads((SITE/'data/usage-example-proof-card-001.json').read_text(encoding='utf-8'))
if len(receipt.get('contractFlow',[]))<10: raise SystemExit('Contract flow too thin')
print('Proof Card 001 demand engine verification passed.')
