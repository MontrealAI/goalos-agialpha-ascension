#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
REQUIRED = [
 'index.html','start-here.html','regular-person.html','personal-proof-sprint.html','proof-sprint-builder.html','autopilot-mission-builder.html','use-cases.html','resources.html','proof-cards.html','system-map.html','how-it-works.html','execution-moat.html','roadmap.html','pilot-guide.html','research.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','sitemap.xml','robots.txt','manifest.webmanifest','routes.json','site-status.json','assets/wow.js'
] + [f'proof-card-{i:03d}.html' for i in range(1,18)]
FORBIDDEN=['recursive.com','recursive-org/first-steps','DEPLOYER_PRIVATE_KEY','PRIVATE_KEY=','MNEMONIC' + '=','SEED_PHRASE' + '=','MAINNET_RPC_URL=']
def fail(m): print('FAIL:',m); sys.exit(1)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site)
 for name in REQUIRED:
  if not (site/name).exists(): fail(f'missing {name}')
 idx=(site/'index.html').read_text(encoding='utf-8', errors='replace')
 atlas=(site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
 for i in range(1,18):
  fn=f'proof-card-{i:03d}.html'
  if fn not in idx: fail(f'homepage missing {fn}')
  if fn not in atlas: fail(f'atlas missing {fn}')
 for word in ['Turn AI activity into proof-backed progress','Build my first mission','WOW','Autopilot','Evidence Docket','AGIALPHA','RSI','proofField','data-count']:
  if word not in idx: fail(f'homepage missing marker {word}')
 for p in site.rglob('*'):
  if p.is_file() and p.suffix.lower() in {'.html','.json','.txt','.xml','.webmanifest','.js'}:
   txt=p.read_text(encoding='utf-8', errors='replace')
   for bad in FORBIDDEN:
    if bad.lower() in txt.lower(): fail(f'forbidden string {bad} in {p}')
 print('GoalOS AGIALPHA final WOW website v40 verification passed.')
if __name__=='__main__': main()
