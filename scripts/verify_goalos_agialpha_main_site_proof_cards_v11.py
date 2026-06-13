#!/usr/bin/env python3
from pathlib import Path
import argparse, re
REQUIRED=['index.html','proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html','proof-card-005.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
NEEDLES=['Proof Card 001','Proof Card 002','Proof Card 003','Proof Card 004','Proof Card 005','Sovereign RSI Value-to-Capability Treasury','value-to-capability','AGIALPHA','Evidence Docket','Sovereign RSI','proof-backed upgrade rights','AlphaWorkUnitLedger','AEPRewardVault','TreasuryRouter','CommercializationPerformanceVault']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', required=True); args=ap.parse_args(); site=Path(args.site); errors=[]; texts=[]
    for f in REQUIRED:
        p=site/f
        if not p.exists(): errors.append(f'missing required page: {f}')
        else: texts.append(p.read_text(encoding='utf-8', errors='replace'))
    all_text='\n'.join(texts); idx=(site/'index.html').read_text(encoding='utf-8', errors='replace') if (site/'index.html').exists() else ''
    for needle in NEEDLES:
        if needle not in all_text: errors.append(f'missing content marker: {needle}')
    for card in ['001','002','003','004','005']:
        if f'proof-card-{card}.html' not in idx and f'Proof Card {card}' not in idx: errors.append(f'homepage does not link or name Proof Card {card}')
    for pat in [r'PRIVATE_KEY',r'SEED_PHRASE',r'MNEMONIC',r'DEPLOYER_PRIVATE_KEY',r'MAINNET_RPC_URL\s*=']:
        if re.search(pat, all_text, flags=re.I): errors.append(f'secret-like pattern found: {pat}')
    
    if re.search(r'\bRecursive\b(?!\s+self-improvement|\s+Self-Improvement)', all_text): errors.append('forbidden named-startup reference found')
    if errors:
        print('Verification failed:'); [print('-',e) for e in errors]; raise SystemExit(1)
    print('Main website Proof Cards 001-005 integration verified.')
if __name__=='__main__': main()
