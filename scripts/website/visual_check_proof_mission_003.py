#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil,sys
from pathlib import Path

def inline_local_assets(site:Path,relative:str)->str:
    raw=(site/relative).read_text(encoding='utf-8')
    css=(site/'assets/goalos-v86-preserve.css').read_text(encoding='utf-8')
    js=(site/'assets/goalos-v86-dynamic-ai.js').read_text(encoding='utf-8')
    raw=raw.replace('<link rel="stylesheet" href="assets/goalos-v86-preserve.css">',f'<style>{css}</style>')
    raw=raw.replace('<script src="assets/goalos-v86-dynamic-ai.js" defer></script>',f'<script>{js}</script>')
    raw=raw.replace('<script defer src="assets/goalos-v86-dynamic-ai.js"></script>',f'<script>{js}</script>')
    return raw

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--site',default='site'); p.add_argument('--screenshots',action='store_true'); a=p.parse_args()
    site=Path(a.site).resolve(); qa=site/'qa/proof-mission-003'; qa.mkdir(parents=True,exist_ok=True)
    try: from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f'ERROR: Playwright missing: {exc}',file=sys.stderr); return 2
    errors=[]; screenshots=[]
    with sync_playwright() as pw:
        executable=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
        browser=pw.chromium.launch(headless=True,executable_path=executable) if executable else pw.chromium.launch(headless=True)
        mission_html=inline_local_assets(site,'proof-mission-003.html'); hub_html=inline_local_assets(site,'proof-missions.html')
        for name,w,h in [('desktop',1440,1100),('mobile',390,844)]:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1); page.emulate_media(reduced_motion='reduce'); page.set_content(mission_html,wait_until='load')
            if 'Capability Constellation' not in page.title(): errors.append(f'{name}: wrong Mission 003 title')
            if page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2'): errors.append(f'{name}: Mission 003 horizontal overflow')
            if page.locator('.cc-route-item').count()!=24: errors.append(f'{name}: expected 24 proof-route entries')
            if page.locator('text=Where proven capabilities become a governed intelligence.').count()<1: errors.append(f'{name}: hero subtitle missing')
            if page.locator('text=No composition without conformance.').count()<1: errors.append(f'{name}: constitutional rule missing')
            if page.locator('.cc-validator').count()!=4: errors.append(f'{name}: expected four validator cards')
            if a.screenshots:
                target=qa/f'proof-mission-003-{name}.png'; page.screenshot(path=str(target),full_page=True); screenshots.append(str(target.relative_to(site)))
            page.close()
        for name,w,h in [('hub-desktop',1440,1000),('hub-mobile',390,844)]:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1); page.emulate_media(reduced_motion='reduce'); page.set_content(hub_html,wait_until='load')
            if 'Proof Missions' not in page.title(): errors.append(f'{name}: wrong Proof Missions title')
            if page.locator('.pm-card').count()!=3: errors.append(f'{name}: expected three mission cards')
            if page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2'): errors.append(f'{name}: Proof Missions horizontal overflow')
            if a.screenshots:
                target=qa/f'proof-missions-{name}.png'; page.screenshot(path=str(target),full_page=True); screenshots.append(str(target.relative_to(site)))
            page.close()
        home=browser.new_page(viewport={'width':1440,'height':1000}); home.set_content(inline_local_assets(site,'index.html'),wait_until='load')
        for selector,label in [('.pgs-home','Mission 001'),('.ap-home','Mission 002'),('.cc-home','Mission 003')]:
            if home.locator(selector).count()!=1: errors.append(f'homepage: {label} panel count is not one')
        if a.screenshots:
            target=qa/'proof-mission-003-homepage-panel.png'; home.locator('.cc-home').screenshot(path=str(target)); screenshots.append(str(target.relative_to(site)))
        home.close(); browser.close()
    report={'status':'PASS' if not errors else 'FAIL','errors':errors,'screenshots':screenshots,'viewports':['1440x1100','390x844'],'publicNetworkTransactionSent':False}
    (qa/'visual-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
