#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys
REQUIRED={
 'index.html':['GoalOS AGIALPHA Ascension','Three proof cards'],
 'flagship-use-case.html':['Sovereign AI Procurement Control Tower','AGIALPHA coordinates'],
 'proof-card-003.html':['Proof Card 003','AEPGoalOSCommitRegistry','AEPSelectionGate'],
 'agialpha-ledger-route.html':['Where AGIALPHA becomes useful','ProofSubmissionRegistry','ProofCredentialRegistry'],
 'sovereign-rsi-control-plane.html':['Sovereign RSI through proof-backed upgrade rights','Selection Gate'],
 'evidence-docket.html':['Evidence Docket','RollbackReceipt'],
 'season-001.html':['Season 001','Proof Card 001'],
 'share.html':['The intelligence stays private','proof becomes verifiable'],
 'data/flagship-use-case-receipt.json':['AGIALPHA','proof-backed upgrade rights'],
 'evidence/proof-card-003-evidence-docket-template.json':['Evidence Docket','GoalOSCommit']
}
BAD=['BEGIN PRIVATE KEY','PRIVATE_KEY=','AWS_SECRET_ACCESS_KEY','api_secret','seed phrase','mnemonic']
FORBIDDEN=re.compile(r'\bRecursive\b')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site); errors=[]
 for rel, markers in REQUIRED.items():
  p=site/rel
  if not p.exists(): errors.append(f'missing {rel}'); continue
  txt=p.read_text(encoding='utf-8',errors='replace')
  for m in markers:
   if m not in txt: errors.append(f'{rel} missing marker {m}')
  if FORBIDDEN.search(txt): errors.append(f'{rel} contains forbidden named-startup reference')
  for b in BAD:
   if b in txt: errors.append(f'{rel} contains secret-like marker {b}')
 if errors:
  print('VERIFICATION_FAILED')
  for e in errors: print('-',e)
  sys.exit(1)
 print('VERIFICATION_PASSED')
 print('Pages checked:', len(REQUIRED))
if __name__=='__main__': main()
