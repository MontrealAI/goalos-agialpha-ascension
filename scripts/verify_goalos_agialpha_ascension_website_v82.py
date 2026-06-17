#!/usr/bin/env python3
from pathlib import Path
import argparse,re,json,sys
REQ=['index.html','resources.html','proof-cards.html','mission-os.html','ascension.html','proof-treasury.html','paper.html','start-here.html','evidence-docket.html','agialpha-continuity.html','executive.html','observatory.html','mission-builder.html','autopilot.html','proof-run-001.html']+[f'proof-card-{i:03d}.html' for i in range(1,32)]+[f'proof-treasury-simulation-{i:03d}.html' for i in [3,4,5]]
CANON=['Turn AI work into verified capability.','AI creates output. GoalOS creates proof.','GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.','SOTA is a measurement. Ascension is the mission.','The product is not output. The product is proof-backed capability.','No proof, no settlement.','No replay, no reinvestment.','No external replay, no capacity scale.','No stress clearance, no institutional scale.','No delayed-outcome clearance, no Ascension reserve compounding.','No governance, no acceleration.','0 claims without proof.']
FORBID=['guaranteed ROI','guaranteed return','token appreciation','profit share','dividend','equity','ownership rights','live Mainnet settlement','Mainnet deployed','production certified','external audit complete','Kardashev Type II achieved','energy abundance achieved','empirical SOTA proven']
def fail(m): print('ERROR:',m); sys.exit(1)
def text(h): return re.sub('<[^>]+>',' ',h)
def wc(h): return len(re.findall(r'[A-Za-z0-9$α‑-]+',text(h)))
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); a=ap.parse_args(); site=Path(a.site)
    for r in REQ:
        if not (site/r).exists(): fail('missing '+r)
    if list(site.rglob('*.zip')): fail('zip files in site')
    home=(site/'index.html').read_text(encoding='utf-8')
    for c in CANON:
        if c not in home: fail('missing canonical '+c)
    if 'bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png' not in home: fail('main hero asset missing')
    nav=re.search(r'<nav.*?</nav>',home,re.S).group(0)
    if 'Proof Run 001' in nav: fail('Proof Run 001 in primary nav')
    allhtml='\n'.join(p.read_text(encoding='utf-8') for p in site.glob('*.html'))
    if 'agialpha.com' in allhtml: fail('agialpha.com outbound link/string found')
    for p in site.glob('*.html'):
        h=p.read_text(encoding='utf-8'); low=h.lower()
        for f in FORBID:
            if f.lower() in low:
                for m in re.finditer(re.escape(f.lower()), low):
                    ctx=low[max(0,m.start()-220):m.end()+120]
                    if any(x in ctx for x in ['does not claim','does not prove','do not claim','not claim','not claimed','what is not claimed','no '+f.lower(),'not '+f.lower(),'not equity','not a token-price claim']):
                        continue
                    fail(f'{f} in {p.name}')
        if p.name!='proof-card-023.html':
            if '<table' not in h: fail('table missing '+p.name)
            if '<svg' not in h and '<img' not in h: fail('diagram or figure missing '+p.name)
        if p.name.startswith('proof-card-') and p.name!='proof-card-023.html' and wc(h)<1200: fail('thin proof card '+p.name+' '+str(wc(h)))
        major_min={'index.html':3500,'mission-os.html':3000,'ascension.html':3000,'proof-treasury.html':2500,'proof-cards.html':2500,'resources.html':2500,'paper.html':2000,'start-here.html':2000,'evidence-docket.html':2200,'agialpha-continuity.html':2000,'mission-builder.html':2000,'autopilot.html':2000,'observatory.html':2000,'executive.html':2000,'proof-run-001.html':1800}
        if p.name in major_min and wc(h)<major_min[p.name]: fail('thin major '+p.name+' '+str(wc(h))+' < '+str(major_min[p.name]))
        if p.name.startswith('proof-treasury-simulation-') and wc(h)<1800: fail('thin treasury simulation '+p.name+' '+str(wc(h)))
        if p.name=='resources.html' and h.count('resource-block')<8: fail('resources center lacks 8 resource blocks')
        if p.name=='proof-cards.html' and h.count('Thematic proof cards')<7: fail('atlas lacks thematic groups')
        for im in re.findall(r'<img[^>]+>',h):
            if 'alt=' not in im: fail('image missing alt '+p.name)
    for p in site.glob('*.html'):
        h=p.read_text(encoding='utf-8')
        for href in re.findall(r'href="([^"]+)"',h):
            if href.startswith(('http','mailto:','#')): continue
            target=href.split('#')[0]
            if not target: continue
            if target.endswith('.html') and not (site/target).exists(): fail('broken link '+href+' in '+p.name)
            if target.endswith('.pdf') and not (site/target).exists(): fail('missing pdf '+href)
    if not (site/'qa/content-report-v82.json').exists(): fail('content report missing')
    (site/'qa').mkdir(exist_ok=True)
    (site/'qa/verify-report-v82.json').write_text(json.dumps({'status':'passed'},indent=2),encoding='utf-8')
    print('Verification passed.')
