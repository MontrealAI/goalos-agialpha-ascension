#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
REQUIRED = ["index.html","mission-os.html","mission-os-paper.html","autopilot-mission-builder.html","proof-cards.html","proof-card-019.html","evidence-docket.html","system-map.html","execution-moat.html","routes.json","sitemap.xml","site-status.json"] + [f"proof-card-{i:03d}.html" for i in range(1,20)]
FORBIDDEN=["recursive.com","recursive-org/first-steps","DEPLOYER_PRIVATE_KEY","PRIVATE_KEY=","MNEMONIC=","SEED_PHRASE=","MAINNET_RPC_URL="]
def fail(msg): print('FAIL:',msg); sys.exit(1)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args(); site=Path(args.site)
    if not site.exists(): fail(f'missing site folder: {site}')
    for name in REQUIRED:
        if not (site/name).exists(): fail(f'missing required page/file: {name}')
    index=(site/'index.html').read_text(encoding='utf-8', errors='replace')
    atlas=(site/'proof-cards.html').read_text(encoding='utf-8', errors='replace')
    pc=(site/'proof-card-019.html').read_text(encoding='utf-8', errors='replace')
    for i in range(1,20):
        fn=f'proof-card-{i:03d}.html'
        if fn not in atlas: fail(f'atlas does not link {fn}')
    if 'proof-card-019.html' not in index: fail('homepage does not link proof-card-019.html')
    required_pc = ['Verified Experience Foundry','Proof-Governed Superintelligence Substrate','VerifiedExperienceValue','Large multi-agent operating theater','AEPVerifiedExperienceRegistry','Evidence Docket','RSI upgrade logic','Civilization-scale horizon, bounded by proof']
    for needle in required_pc:
        if needle not in pc: fail(f'Proof Card 019 missing: {needle}')
    if 'pc-section.dark .pc-card h3' not in pc or '.pc-table td' not in pc: fail('Proof Card 019 visual contrast hardening missing')
    if list(site.rglob('*.zip')): fail('generated public site contains zip files')
    for p in site.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.html','.json','.txt','.xml','.webmanifest'}:
            text=p.read_text(encoding='utf-8', errors='replace').lower()
            for bad in FORBIDDEN:
                if bad.lower() in text: fail(f'forbidden public string {bad} in {p}')
    print('GoalOS AGIALPHA final main website v54 verification passed.')
if __name__=='__main__': main()
