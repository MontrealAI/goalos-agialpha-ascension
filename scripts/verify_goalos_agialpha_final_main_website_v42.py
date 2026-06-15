#!/usr/bin/env python3
from pathlib import Path
import argparse, sys

REQUIRED = ['index.html','start-here.html','regular-person.html','personal-proof-sprint.html','proof-sprint-builder.html','autopilot-mission-builder.html','use-cases.html','resources.html','proof-cards.html','system-map.html','how-it-works.html','execution-moat.html','roadmap.html','pilot-guide.html','research.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','sitemap.xml','robots.txt','manifest.webmanifest','routes.json','site-status.json'] + [f'proof-card-{i:03d}.html' for i in range(1,18)]
FORBIDDEN=['recursive.com','recursive-org/first-steps','DEPLOYER_PRIVATE_KEY','PRIVATE_KEY=','MNEMONIC' + '=','SEED_PHRASE' + '=','MAINNET_RPC_URL=']
def fail(m): print('FAIL:',m); sys.exit(1)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site)
    if not site.exists(): fail(f'missing site folder: {site}')
    for n in REQUIRED:
        if not (site/n).exists(): fail(f'missing required page/file: {n}')
    index=(site/'index.html').read_text(encoding='utf-8',errors='replace'); atlas=(site/'proof-cards.html').read_text(encoding='utf-8',errors='replace')
    for i in range(1,18):
        fn=f'proof-card-{i:03d}.html'
        if fn not in index: fail(f'homepage does not link {fn}')
        if fn not in atlas: fail(f'atlas does not link {fn}')
    for s in ['world-ready','Build my first mission','Autopilot','Evidence Docket','AGIALPHA','RSI','WOW at first glance']:
        if s not in index: fail(f'homepage missing important wording: {s}')
    for f in ['system-map.html','how-it-works.html','execution-moat.html','roadmap.html','pilot-guide.html','regular-person.html','research.html']:
        if f not in index: fail(f'homepage missing route link: {f}')
    if any(site.rglob('*.zip')): fail('zip file found inside GitHub Pages site assets')
    for p in site.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.html','.json','.txt','.xml','.webmanifest'}:
            text=p.read_text(encoding='utf-8',errors='replace').lower()
            for bad in FORBIDDEN:
                if bad.lower() in text: fail(f'forbidden public string {bad} in {p}')
    print('GoalOS AGIALPHA final main website v42 verification passed.')
if __name__=='__main__': main()
