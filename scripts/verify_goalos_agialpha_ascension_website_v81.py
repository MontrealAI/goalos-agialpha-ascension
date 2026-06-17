#!/usr/bin/env python3
from pathlib import Path
import argparse, re, json, sys
from html.parser import HTMLParser

PRIMARY_NAV = ['Home','Mission OS','Ascension','Proof Treasury','Proof Cards','Paper','Resources']
CANON = ['Turn AI work into verified capability.','AI creates output. GoalOS creates proof.','GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.','SOTA is a measurement. Ascension is the mission.','The product is not output. The product is proof-backed capability.','No proof, no settlement.','No replay, no reinvestment.','No external replay, no capacity scale.','No stress clearance, no institutional scale.','No delayed-outcome clearance, no Ascension reserve compounding.','No governance, no acceleration.','0 claims without proof.']
REQUIRED = ['index.html','executive.html','observatory.html','mission-os.html','ascension.html','proof-treasury.html','proof-cards.html','resources.html','autopilot.html','mission-builder.html','start-here.html','evidence-docket.html','proof-run-001.html','agialpha-continuity.html','paper.html','sitemap.xml','robots.txt','manifest.webmanifest','site-status.json'] + [f'proof-card-{i:03d}.html' for i in range(1,32)] + [f'proof-treasury-simulation-{i:03d}.html' for i in (3,4,5)]
DENY = ['achieved AGI','achieved ASI','achieved superintelligence','guaranteed ROI','guaranteed return','token appreciation','profit share','dividend','equity','ownership rights','live Mainnet settlement','Mainnet deployed','external audit complete','production certified','Kardashev Type II achieved','energy abundance achieved','empirical SOTA proven']
ALLOWED_PREFIXES = ['does not claim ','no ','not ','not a ','not an ']
class LinkParser(HTMLParser):
    def __init__(self): super().__init__(); self.hrefs=[]; self.imgs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=='a' and 'href' in d: self.hrefs.append(d['href'])
        if tag=='img': self.imgs.append(d)

def text(path): return path.read_text(encoding='utf-8', errors='ignore')
def fail(msg): print('FAIL:', msg); sys.exit(1)

def local_target(h): return h.split('#')[0].split('?')[0]

def allowed_context(content, phrase):
    idx=content.lower().find(phrase.lower())
    if idx < 0: return True
    start=max(0,idx-200); ctx=content[start:idx].lower()
    return any(p in ctx for p in ALLOWED_PREFIXES)

def main(site):
    site=Path(site); report={'checked':[], 'warnings':[]}
    if not site.exists(): fail(f'{site} missing')
    for r in REQUIRED:
        if not (site/r).exists(): fail(f'required page missing: {r}')
    if list(site.rglob('*.zip')): fail('ZIP files found in generated public site')
    idx=text(site/'index.html')
    for c in CANON:
        if c not in idx: fail(f'missing canonical line: {c}')
    if 'Proof Run 001' in re.search(r'<nav.*?</nav>', idx, flags=re.S|re.I).group(0): fail('Proof Run 001 appears in primary nav')
    if 'Asset-driven proof, coordination, and RSI visuals' in idx: fail('generic v80 asset section still present')
    if 'agialpha.com' in ''.join(text(p) for p in site.glob('*.html')): fail('Outbound agialpha.com link/text found in generated public site')
    if 'assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png' not in idx: fail('homepage does not reference main hero asset')
    if 'GoalOS Mission OS — The Proof OS for Autonomous AI Work' not in idx: fail('paper not prominently featured')
    if not (site/'assets/generated/mission-os-paper-cover.svg').exists() and not (site/'assets/generated/mission-os-paper-cover.png').exists(): fail('paper cover visual missing')
    status=json.loads(text(site/'site-status.json'))
    if status.get('stable_proof_cards') != 30 or status.get('proof_card_023') != 'reserved': fail('proof-card count/reserved status wrong')
    for i in range(1,32):
        p=site/f'proof-card-{i:03d}.html'; c=text(p)
        parser=LinkParser(); parser.feed(c)
        if f'Proof Card {i:03d}' not in c: fail(f'proof-card-{i:03d} missing title')
        if i != 23:
            for token in ['Thesis','What this proves','GoalOS Object Model','Claim Boundary']:
                if token not in c: fail(f'proof-card-{i:03d} missing {token}')
            if '<table' not in c: fail(f'proof-card-{i:03d} missing table')
            if '<svg' not in c: fail(f'proof-card-{i:03d} missing diagram SVG')
        else:
            if 'Reserved' not in c or 'intentional' not in c.lower(): fail('proof-card-023 reserved page inadequate')
    # links and images
    for page in site.glob('*.html'):
        c=text(page); parser=LinkParser(); parser.feed(c)
        for h in parser.hrefs:
            if not h or h.startswith(('http://','https://','mailto:','#')): continue
            t=local_target(h)
            if t and not (site/t).exists(): fail(f'broken local href {h} in {page.name}')
        for img in parser.imgs:
            if img.get('aria-hidden')=='true': continue
            if not img.get('alt','').strip(): fail(f'image without alt in {page.name}: {img.get("src")}')
        for n in PRIMARY_NAV:
            if n not in c: fail(f'{page.name} missing primary nav item {n}')
    allhtml='\n'.join(text(p) for p in site.glob('*.html'))
    for phrase in DENY:
        if phrase.lower() in allhtml.lower() and not allowed_context(allhtml, phrase): fail(f'unqualified denied phrase: {phrase}')
    css=idx
    for token in ['overflow-x:clip','prefers-reduced-motion','max-width:100%']:
        if token not in css: fail(f'missing responsive/visual integrity CSS token: {token}')
    (site/'qa').mkdir(exist_ok=True)
    out={'status':'passed','pages':len(list(site.glob('*.html'))),'proof_cards':31,'stable_proof_cards':30,'proof_card_023':'reserved','visual_layout_static':'css constrained; browser QA handled by smoke-test workflow'}
    (site/'qa/verification-v81.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    (site/'qa/verification-v81.md').write_text('# v81 Verification\n\nVerification passed. Browser layout QA runs in the smoke-test workflow.\n', encoding='utf-8')
    print('Verification passed.')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site')
    args=ap.parse_args(); main(args.site)
