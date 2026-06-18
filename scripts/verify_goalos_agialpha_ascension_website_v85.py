#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import argparse,re,json,sys
class P(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.img=[]; self.text=[]; self.stack=[]; self.css=False; self.js=False
    def handle_starttag(self,t,a):
        d=dict(a); self.stack.append(t)
        if t=='a' and d.get('href'): self.links.append(d['href'])
        if t=='img': self.img.append((d.get('src',''),d.get('alt','')))
        if t=='link' and 'goalos-v85.css' in d.get('href',''): self.css=True
        if t=='script' and 'goalos-v85.js' in d.get('src',''): self.js=True
    def handle_endtag(self,t):
        if self.stack: self.stack.pop()
    def handle_data(self,d): self.text.append(d)
REQUIRED=['index.html','whitepaper.html','paper.html','mission-os.html','ascension.html','proof-cards.html','proof-treasury.html','resources.html','evidence-docket.html','sovereign-rsi-control-plane.html']+[f'proof-card-{i:03d}.html' for i in range(1,32)]+[f'proof-treasury-simulation-{i:03d}.html' for i in range(3,6)]
DENY=['achieved AGI','achieved ASI','achieved superintelligence','guaranteed ROI','guaranteed return','token appreciation','profit share','live Mainnet settlement','Kardashev Type II achieved']
NEG=['does not claim','not claimed','no achieved','no live','not equity','not a guaranteed']
def words(s): return len(re.findall(r"[A-Za-z0-9$α‑'-]+",re.sub('<[^>]+>',' ',s)))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); a=ap.parse_args(); root=Path(a.site); err=[]; report={}
    for f in REQUIRED:
        if not (root/f).exists(): err.append('missing '+f)
    for p in root.glob('*.html'):
        s=p.read_text(errors='ignore'); parser=P(); parser.feed(s); text=' '.join(parser.text); low=text.lower()
        if not parser.css: err.append(f'{p.name}: missing v85 css link')
        if not parser.js: err.append(f'{p.name}: missing v85 js')
        if 'goalos-v85-inline' not in s: err.append(f'{p.name}: missing inline CSS fallback')
        if p.name=='index.html' and 'bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png' not in s: err.append('index: main asset missing')
        for src,alt in parser.img:
            if not alt.strip(): err.append(f'{p.name}: image missing alt: {src}')
        for href in parser.links:
            if href.startswith(('http:','https:','mailto:','#','javascript:')): continue
            target=href.split('#')[0].split('?')[0]
            if target and not (root/target).exists(): err.append(f'{p.name}: broken {href}')
        for phrase in DENY:
            pos=low.find(phrase.lower())
            if pos>=0:
                ctx=low[max(0,pos-100):pos+len(phrase)+100]
                if not any(n in ctx for n in NEG): err.append(f'{p.name}: unbounded claim {phrase}')
        w=words(s); report[p.name]={'words':w,'sections':s.count('<section'),'tables':s.count('<table'),'images':s.count('<img'),'svg':s.count('<svg'),'links':len(parser.links)}
        if p.name.startswith('proof-card-') and w<1100: err.append(f'{p.name}: too thin ({w} words)')
        if p.name in ['resources.html','whitepaper.html','sovereign-rsi-control-plane.html','proof-treasury.html','proof-cards.html'] and w<1200: err.append(f'{p.name}: too thin ({w} words)')
        if 'Proof Run 001' in ''.join(re.findall(r'<nav[^>]*>(.*?)</nav>',s,re.S)) and p.name!='proof-run-001.html': err.append(f'{p.name}: Proof Run 001 in primary nav')
        if 'Asset-driven proof, coordination, and RSI visuals.' in s: err.append(f'{p.name}: obsolete asset gallery heading')
    if any(root.rglob('*.zip')): err.append('ZIP inside public site')
    (root/'qa').mkdir(exist_ok=True); (root/'qa/verify-report-v85.json').write_text(json.dumps({'errors':err,'pages':report},indent=2))
    if err:
        print('\n'.join(err)); sys.exit(1)
    print(f'Verification passed: {len(report)} HTML pages')
if __name__=='__main__': main()
