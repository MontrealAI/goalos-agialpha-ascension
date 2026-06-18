#!/usr/bin/env python3
from pathlib import Path
import argparse,json,threading,http.server,socketserver,contextlib,time,sys
from playwright.sync_api import sync_playwright
PAGES=['index.html','whitepaper.html','resources.html','proof-cards.html','proof-card-001.html','proof-card-020.html','proof-card-023.html','proof-card-028.html','proof-card-031.html','mission-os.html','ascension.html','proof-treasury.html','sovereign-rsi-control-plane.html','paper.html']
VIEWS=[(320,800),(375,812),(768,1024),(1024,768),(1440,1000)]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--screenshots',default='qa/screenshots-v85'); a=ap.parse_args(); root=Path(a.site).resolve(); shots=root/a.screenshots; shots.mkdir(parents=True,exist_ok=True)
    handler=lambda *args,**kw: Quiet(*args,directory=str(root),**kw); server=socketserver.TCPServer(('127.0.0.1',0),handler); port=server.server_address[1]; thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start(); errors=[]; checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for w,h in VIEWS:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
            for rel in PAGES:
                page.goto(f'http://127.0.0.1:{port}/{rel}',wait_until='networkidle')
                page.wait_for_timeout(250)
                data=page.evaluate('''() => { const de=document.documentElement; const bad=[]; document.querySelectorAll('img,svg,canvas,.v75-figure,.figure,.diagram-frame,.visual-shell,.proof-card-visual,.hero-card,.v85-card').forEach(el=>{const r=el.getBoundingClientRect();const p=el.parentElement?.getBoundingClientRect();if(r.width>innerWidth+2)bad.push(el.tagName+' viewport '+r.width);if(p&&(r.left<p.left-3||r.right>p.right+3)&&!el.closest('.v85-more-panel'))bad.push(el.tagName+' parent escape')}); const unreadable=[...document.querySelectorAll('a,button')].filter(el=>{const s=getComputedStyle(el),c=s.color,b=s.backgroundColor;return el.offsetParent!==null && (c==='rgba(0, 0, 0, 0)'||s.fontSize==='0px')}).length; return {scrollWidth:de.scrollWidth,innerWidth, bad, unreadable, title:document.title, bodyHeight:document.body.scrollHeight}; }''')
                ok=data['scrollWidth']<=w+2 and not data['bad'] and data['bodyHeight']>h*1.4
                checks.append({'page':rel,'viewport':[w,h],**data,'ok':ok})
                if not ok: errors.append(f'{rel}@{w}: {data}')
                if w==1440 and rel in ['index.html','whitepaper.html','resources.html','proof-cards.html','sovereign-rsi-control-plane.html']:
                    page.screenshot(path=str(shots/f'{Path(rel).stem}-{w}.png'),full_page=True)
            page.close()
        browser.close()
    server.shutdown(); report=root/'qa/layout-report-v85.json'; report.parent.mkdir(exist_ok=True); report.write_text(json.dumps({'errors':errors,'checks':checks},indent=2))
    if errors: print('\n'.join(errors)); sys.exit(1)
    print('Visual QA passed')
if __name__=='__main__': main()
