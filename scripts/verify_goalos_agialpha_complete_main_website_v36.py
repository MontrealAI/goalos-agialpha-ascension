#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys
REQ=['index.html','start-here.html','personal-proof-sprint.html','proof-sprint-builder.html','autopilot-mission-builder.html','use-cases.html','resources.html','proof-cards.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html']+[f'proof-card-{i:03d}.html' for i in range(1,18)]
SECRET=[r'PRIVATE_KEY',r'SEED_PHRASE',r'MNEMONIC',r'DEPLOYER_PRIVATE_KEY',r'MAINNET_RPC_URL\s*=',r'SEPOLIA_RPC_URL\s*=']
FORBIDDEN=['recursive.com/articles','github.com/recursive-org','@Recursive_SI']
def txt(p): return p.read_text(encoding='utf-8',errors='replace')
def fail(m): print('FAIL:',m); sys.exit(1)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site)
 if not site.exists(): fail('missing site dir')
 for f in REQ:
  if not (site/f).exists(): fail(f'missing required page: {f}')
 idx=txt(site/'index.html'); atlas=txt(site/'proof-cards.html'); auto=txt(site/'autopilot-mission-builder.html')
 for i in range(1,18):
  link=f'proof-card-{i:03d}.html'
  if link not in idx: fail(f'homepage missing {link}')
  if link not in atlas: fail(f'atlas missing {link}')
 for token in ['Autopilot Mission Builder','AGIALPHA','Evidence Docket','RSI','Copy JSON','Download JSON','Start in 10 minutes']:
  if token not in auto and token not in idx: fail(f'missing key token: {token}')
 for p in site.rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.html','.md','.json','.txt','.yml','.yaml']:
   t=txt(p)
   for pat in SECRET:
    if re.search(pat,t,re.I): fail(f'secret-like pattern {pat} in {p}')
   for bad in FORBIDDEN:
    if bad.lower() in t.lower(): fail(f'forbidden competitor reference {bad} in {p}')
 print('GoalOS AGIALPHA complete main website v36 verification passed.')
if __name__=='__main__': main()
