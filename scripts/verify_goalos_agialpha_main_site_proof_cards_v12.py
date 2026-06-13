#!/usr/bin/env python3
from pathlib import Path
import argparse,re
REQ=['index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html','proof-card-005.html','proof-card-006.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
TOKENS=['Proof Card 006','Sovereign Enterprise RSI Operating System','AGIALPHA','AEPGoalOSCommitRegistry','AEPRunCommitmentRegistry','JobRegistry','JobClaimBondManager','ProofSubmissionRegistry','ReviewerBondRegistry','ProofCardRegistry','ProofCredentialRegistry','ReputationRegistry','AEPEvidenceDocketRegistry','AEPSelectionGate','AEPChronicleRegistry','AlphaWorkUnitLedger','AEPRewardVault','TreasuryRouter','CommercializationPerformanceVault','Evidence Docket','Sovereign RSI','proof-backed upgrade rights']
SECRET_RE=re.compile(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)',re.I)
FORBIDDEN=['Recur' + 'sive']
def main():
 p=argparse.ArgumentParser(); p.add_argument('--site',required=True); a=p.parse_args(); site=Path(a.site); errors=[]
 for f in REQ:
  if not (site/f).exists(): errors.append('Missing '+f)
 index=(site/'index.html').read_text(encoding='utf-8',errors='replace') if (site/'index.html').exists() else ''
 for i in range(1,7):
  if f'proof-card-00{i}.html' not in index: errors.append(f'Homepage does not link proof-card-00{i}.html')
 combined='\n'.join(x.read_text(encoding='utf-8',errors='replace') for x in site.glob('*.html'))
 for t in TOKENS:
  if t not in combined: errors.append('Missing token/section: '+t)
 if SECRET_RE.search(combined): errors.append('Potential secret-like string found')
 for bad in FORBIDDEN:
  if bad in combined: errors.append('Forbidden named-startup reference found: '+bad)
 pc6=(site/'proof-card-006.html').read_text(encoding='utf-8',errors='replace') if (site/'proof-card-006.html').exists() else ''
 for section in ['Large multi-agent coordination','Kardashev-aligned horizon','Goals used','Plans used','Skills used','Claim boundary']:
  if section not in pc6: errors.append('Proof Card 006 missing section: '+section)
 if errors:
  [print('ERROR:',e) for e in errors]
  raise SystemExit(1)
 print('Main website Proof Cards 001-006 integration verified.')
if __name__=='__main__': main()
