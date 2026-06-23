#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil,sys
from pathlib import Path
def inline(site:Path,r:str)->str:
 raw=(site/r).read_text(); css=(site/'assets/goalos-v86-preserve.css').read_text(); js=(site/'assets/goalos-v86-dynamic-ai.js').read_text(); raw=raw.replace('<link rel="stylesheet" href="assets/goalos-v86-preserve.css">',f'<style>{css}</style>'); raw=raw.replace('<script src="assets/goalos-v86-dynamic-ai.js" defer></script>',f'<script>{js}</script>'); raw=raw.replace('<script defer src="assets/goalos-v86-dynamic-ai.js"></script>',f'<script>{js}</script>'); return raw
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--screenshots',action='store_true'); a=ap.parse_args(); site=Path(a.site).resolve(); qa=site/'qa/proof-mission-005'; qa.mkdir(parents=True,exist_ok=True)
 try: from playwright.sync_api import sync_playwright
 except Exception as e: print('ERROR:',e,file=sys.stderr); return 2
 errors=[]; shots=[]
 with sync_playwright() as p:
  ex=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome'); b=p.chromium.launch(headless=True,executable_path=ex) if ex else p.chromium.launch(headless=True)
  mission=inline(site,'proof-mission-005.html'); hub=inline(site,'proof-missions.html')
  for name,w,h in [('desktop',1440,1100),('mobile',390,844)]:
   pg=b.new_page(viewport={'width':w,'height':h}); pg.emulate_media(reduced_motion='reduce'); pg.set_content(mission,wait_until='load')
   if 'Interinstitutional Accord' not in pg.title(): errors.append(name+': wrong title')
   if pg.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2'): errors.append(name+': horizontal overflow')
   if pg.locator('.ia-route-item').count()!=40: errors.append(name+': route count')
   if pg.locator('.ia-validator').count()!=6: errors.append(name+': validator count')
   if pg.locator('text=No treaty without proof.').count()<1: errors.append(name+': constitution missing')
   if name=='desktop':
    q=pg.locator('#ia-route-search'); q.fill('TreasuryRouter'); n=pg.locator('.ia-route-item:not(.hidden)').count();
    if n!=1: errors.append(f'desktop: route search expected 1, found {n}')
   if a.screenshots:
    t=qa/f'proof-mission-005-{name}.png'; pg.screenshot(path=str(t),full_page=True); shots.append(str(t.relative_to(site)))
   pg.close()
  for name,w,h in [('hub-desktop',1440,1000),('hub-mobile',390,844)]:
   pg=b.new_page(viewport={'width':w,'height':h}); pg.set_content(hub,wait_until='load')
   if pg.locator('.pm-card').count()!=5: errors.append(name+': expected five mission cards')
   if pg.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2'): errors.append(name+': hub overflow')
   if pg.locator('text=The Interinstitutional Accord').count()<1: errors.append(name+': Mission 005 missing')
   if a.screenshots:
    t=qa/f'proof-missions-{name}.png'; pg.screenshot(path=str(t),full_page=True); shots.append(str(t.relative_to(site)))
   pg.close()
  home=b.new_page(viewport={'width':1440,'height':1000}); home.set_content(inline(site,'index.html'),wait_until='load')
  for sel,label in [('.pgs-home','001'),('.ap-home','002'),('.cc-home','003'),('.si-home','004'),('.ia-home','005')]:
   if home.locator(sel).count()!=1: errors.append('homepage '+label+' panel count')
  if home.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2'): errors.append('homepage overflow')
  if a.screenshots:
   t=qa/'proof-mission-005-homepage-panel.png'; home.locator('.ia-home').screenshot(path=str(t)); shots.append(str(t.relative_to(site)))
  home.close(); b.close()
 report={'status':'PASS' if not errors else 'FAIL','errors':errors,'screenshots':shots,'viewports':['1440x1100','390x844'],'publicNetworkTransactionSent':False}; (qa/'visual-check.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
