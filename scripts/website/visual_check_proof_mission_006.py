#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from functools import partial

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--output',default='site/qa/proof-mission-006'); a=ap.parse_args()
    site=Path(a.site).resolve(); out=Path(a.output).resolve(); out.mkdir(parents=True,exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print('Playwright is required for browser QA:',e); return 2
    handler=partial(SimpleHTTPRequestHandler,directory=str(site))
    httpd=ThreadingHTTPServer(('127.0.0.1',0),handler); port=httpd.server_address[1]
    thread=threading.Thread(target=httpd.serve_forever,daemon=True); thread.start()
    report={'status':'FAIL','desktop':{},'mobile':{},'search':{},'errors':[]}
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            for label,w,h in [('desktop',1440,1100),('mobile',390,844)]:
                page=browser.new_page(viewport={'width':w,'height':h})
                page.goto(f'http://127.0.0.1:{port}/proof-mission-006.html',wait_until='networkidle')
                title=page.locator('h1').inner_text()
                overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
                page.screenshot(path=str(out/f'proof-mission-006-{label}.png'),full_page=True)
                report[label]={'title':title,'horizontalOverflowPx':overflow,'pass':title.strip()=='THE\nLONG HORIZON' and overflow<=1}
                if label=='desktop':
                    page.locator('#lh-route-search').fill('Chronicle')
                    visible=int(page.locator('#lh-route-visible').inner_text())
                    report['search']={'query':'Chronicle','visible':visible,'pass':visible>=1 and visible<44}
                page.close()
            for rel,name in [('proof-missions.html','proof-missions-hub'),('index.html','proof-mission-006-homepage-panel')]:
                page=browser.new_page(viewport={'width':1440,'height':1000})
                page.goto(f'http://127.0.0.1:{port}/{rel}',wait_until='networkidle')
                if rel=='index.html': page.locator('<!--not-valid-->') if False else None
                page.screenshot(path=str(out/f'{name}.png'),full_page=False)
                overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
                report[name]={'horizontalOverflowPx':overflow,'pass':overflow<=1}
                page.close()
            browser.close()
        report['status']='PASS' if all(x.get('pass') for k,x in report.items() if isinstance(x,dict) and k not in ('errors',)) else 'FAIL'
    except Exception as e:
        report['errors'].append(str(e))
    finally:
        httpd.shutdown(); httpd.server_close()
    (out/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
