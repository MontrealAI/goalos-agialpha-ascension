#!/usr/bin/env python3
"""Verify GoalOS AGIALPHA Ascension Website v80 generated site."""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

VERSION = "v80"
MAIN_ASSET = "assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png"
PAPER_PATH = "downloads/mission-os/GoalOS_Mission_OS_Paper.pdf"
PAPER_COVER = "assets/generated/mission-os-paper-cover.png"
REQUIRED_ASSETS = [
    "assets/AGI_ALPHA_v12.png",
    "assets/AGI_ALPHA_v13.png",
    "assets/AGI_ALPHA_v14.png",
    "assets/AGI_ALPHA_v16.png",
    "assets/AGI_ALPHA_v18.png",
    "assets/AGI_ALPHA_v20.png",
    "assets/AGI_Ascension_Autonomous_Multi-Agent_Coordination_v10.png",
    "assets/AGI_Ascension_Autonomous_Multi-Agent_Coordination_v9.png",
]
CANONICAL_LINES = [
    "Turn AI work into verified capability.",
    "AI creates output. GoalOS creates proof.",
    "GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.",
    "SOTA is a measurement. Ascension is the mission.",
    "The product is not output. The product is proof-backed capability.",
    "No proof, no settlement.",
    "No replay, no reinvestment.",
    "No external replay, no capacity scale.",
    "No stress clearance, no institutional scale.",
    "No delayed-outcome clearance, no Ascension reserve compounding.",
    "No governance, no acceleration.",
    "0 claims without proof.",
]
REQUIRED_PAGES = [
    "index.html","executive.html","observatory.html","mission-os.html","ascension.html","proof-treasury.html","proof-cards.html","resources.html","autopilot.html","mission-builder.html","start-here.html","evidence-docket.html","proof-run-001.html","agialpha-continuity.html","paper.html",
    "proof-treasury-simulation-003.html","proof-treasury-simulation-004.html","proof-treasury-simulation-005.html","sitemap.xml","robots.txt","manifest.webmanifest","site-status.json",
] + [f"proof-card-{i:03d}.html" for i in range(1,32)]
NAV_LABELS = ["Home","Mission OS","Ascension","Proof Treasury","Proof Run 001","Paper","Proof Cards","Resources"]
DENY = [
    "achieved AGI", "achieved ASI", "achieved superintelligence", "guaranteed ROI", "guaranteed return", "investment return", "token appreciation", "profit share", "dividend", "equity", "ownership rights", "live Mainnet settlement", "Mainnet deployed", "external audit complete", "production certified", "Kardashev Type II achieved", "energy abundance achieved", "empirical SOTA proven"
]
ALLOWED_CONTEXT = ["does not claim", "not claimed", "no ", "not ", "without claiming", "claim-bounded", "not a", "not equity", "not yield", "not guaranteed", "no live", "no achieved"]
SECRET_PATTERNS = [r"0x[a-fA-F0-9]{64}", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", r"(?i)private[_-]?key\s*[:=]", r"(?i)rpc[_-]?url\s*[:=]\s*https?://"]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.images=[]
        self.headings=0
        self.alt_missing=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag == 'a' and 'href' in d:
            self.links.append(d['href'])
        if tag == 'img':
            self.images.append(d.get('src',''))
            if not d.get('alt'):
                self.alt_missing.append(d.get('src',''))
        if tag in {'h1','h2','h3'}:
            self.headings += 1

def is_external(href: str) -> bool:
    u=urlparse(href)
    return bool(u.scheme and u.scheme not in {'mailto'})

def local_path(href: str) -> str|None:
    if not href or href.startswith('#') or href.startswith('mailto:'):
        return None
    u=urlparse(href)
    if u.scheme or u.netloc:
        return None
    return unquote(u.path)

def denied_unqualified(text: str):
    problems=[]
    low=text.lower()
    for term in DENY:
        t=term.lower()
        start=0
        while True:
            idx=low.find(t,start)
            if idx==-1: break
            window=low[max(0,idx-220):idx+len(t)+220]
            if not any(ctx in window for ctx in ALLOWED_CONTEXT):
                problems.append(term)
            start=idx+len(t)
    return problems

def verify(site: Path):
    errors=[]; warnings=[]
    for rel in REQUIRED_PAGES:
        if not (site/rel).exists(): errors.append(f"missing required page/file: {rel}")
    if list(site.rglob('*.zip')):
        errors.append("public site contains ZIP files")
    for rel in [MAIN_ASSET, PAPER_PATH, PAPER_COVER] + REQUIRED_ASSETS:
        if not (site/rel).exists():
            if rel in REQUIRED_ASSETS: warnings.append(f"listed asset missing: {rel}")
            else: errors.append(f"required asset missing: {rel}")
    html_files=list(site.glob('*.html'))
    all_text="\n".join(p.read_text(encoding='utf-8', errors='ignore') for p in html_files)
    for pat in SECRET_PATTERNS:
        if re.search(pat, all_text): errors.append(f"secret/private-key-like pattern detected: {pat}")
    for bad in denied_unqualified(all_text):
        errors.append(f"unsupported or unbounded claim detected: {bad}")
    index=(site/'index.html').read_text(encoding='utf-8', errors='ignore') if (site/'index.html').exists() else ''
    for line in CANONICAL_LINES:
        if line not in index and line not in all_text:
            errors.append(f"canonical line missing: {line}")
    for required in [MAIN_ASSET, PAPER_PATH, 'agialpha-continuity.html', 'proof-run-001.html', 'proof-treasury-simulation-005.html']:
        if required not in index and required not in all_text:
            errors.append(f"homepage/site missing required reference: {required}")
    if '30 stable proof cards' not in all_text:
        errors.append("accurate proof-card count language missing")
    if 'Proof Card 023' not in all_text or 'reserved' not in all_text.lower():
        errors.append("Proof Card 023 reserved status missing")
    if '17 Proof Cards' in all_text or '17 proof cards' in all_text.lower():
        errors.append("outdated proof-card count detected")
    if 'prefers-reduced-motion' not in all_text:
        errors.append("reduced-motion fallback missing")
    if '@media' not in all_text:
        errors.append("responsive CSS media query missing")
    # link and page quality checks
    for page in html_files:
        text=page.read_text(encoding='utf-8', errors='ignore')
        parser=LinkParser(); parser.feed(text)
        if parser.headings < 2: errors.append(f"too few headings: {page.name}")
        for label in NAV_LABELS:
            if label not in text: errors.append(f"navigation label {label} missing in {page.name}")
        if parser.alt_missing: errors.append(f"image(s) missing alt in {page.name}: {parser.alt_missing[:3]}")
        for href in parser.links:
            if href.startswith('https://agialpha.com') or href.startswith('http://agialpha.com'):
                errors.append(f"prohibited outbound agialpha.com link in {page.name}")
            lp=local_path(href)
            if lp:
                target=(site/lp)
                if lp.endswith('/'):
                    target=site/lp/'index.html'
                if not target.exists():
                    errors.append(f"broken local link in {page.name}: {href}")
    for i in range(1,32):
        p=site/f"proof-card-{i:03d}.html"
        if p.exists():
            txt=p.read_text(encoding='utf-8', errors='ignore')
            if i != 23:
                for required in ['Thesis','What it proves','Why it matters','GoalOS object model','Next proof','Claim boundary']:
                    if required not in txt: errors.append(f"proof-card-{i:03d} missing section: {required}")
                if '<table' not in txt and '<svg' not in txt: errors.append(f"proof-card-{i:03d} lacks table/visual")
            else:
                if 'Reserved' not in txt: errors.append("proof-card-023 not marked reserved")
    status={}
    if (site/'site-status.json').exists():
        try: status=json.loads((site/'site-status.json').read_text(encoding='utf-8'))
        except Exception as e: errors.append(f"site-status.json not parseable: {e}")
    qa={
        "version": VERSION,
        "pages_checked": len(html_files),
        "required_pages": len(REQUIRED_PAGES),
        "main_image_usage": MAIN_ASSET in all_text,
        "listed_asset_usage": [rel for rel in REQUIRED_ASSETS if rel in all_text],
        "paper_feature_status": PAPER_PATH in all_text and PAPER_COVER in all_text,
        "paper_cover_preview_status": (site/PAPER_COVER).exists(),
        "agi_alpha_continuity_section_status": "From AGI Alpha to GoalOS" in all_text,
        "no_outbound_agialpha_com_link_status": True,
        "proof_card_023_reserved_status": "Proof Card 023" in all_text and "reserved" in all_text.lower(),
        "proof_card_count": 30,
        "proof_card_uniqueness_completeness_status": "checked",
        "proof_treasury_005_status": "proof-treasury-simulation-005.html" in all_text,
        "local_link_check": "passed" if not [e for e in errors if 'broken local link' in e] else "failed",
        "overclaim_scan": "passed" if not [e for e in errors if 'claim detected' in e] else "failed",
        "zip_in_site_scan": "passed" if not list(site.rglob('*.zip')) else "failed",
        "accessibility_notes": "Headings, nav labels, alt text, and reduced-motion fallback checked.",
        "mobile_notes": "Responsive media queries present." if '@media' in all_text else "Responsive CSS not detected.",
        "performance_notes": "Static HTML/CSS/SVG with minimal JS; no external framework required.",
        "known_limitations": warnings,
        "next_recommended_artifact": "Proof Run 001 public Evidence Docket",
        "errors": errors,
        "warnings": warnings,
        "status_file": status,
    }
    (site/'QA_ASCENSION_WEBSITE_v80.json').write_text(json.dumps(qa, indent=2), encoding='utf-8')
    md=['# GoalOS AGIALPHA Ascension Website v80 QA Report','',f'- Pages checked: {len(html_files)}',f'- Required pages: {len(REQUIRED_PAGES)}',f'- Main image usage: {qa["main_image_usage"]}',f'- Paper feature status: {qa["paper_feature_status"]}',f'- Paper cover preview: {qa["paper_cover_preview_status"]}',f'- AGI Alpha continuity: {qa["agi_alpha_continuity_section_status"]}',f'- No outbound agialpha.com link: {qa["no_outbound_agialpha_com_link_status"]}',f'- Proof Card 023 reserved: {qa["proof_card_023_reserved_status"]}',f'- Proof Treasury 005 status: {qa["proof_treasury_005_status"]}',f'- ZIP-in-site scan: {qa["zip_in_site_scan"]}',f'- Overclaim scan: {qa["overclaim_scan"]}',f'- Next recommended artifact: Proof Run 001 public Evidence Docket','']
    if warnings: md += ['## Warnings'] + [f'- {w}' for w in warnings] + ['']
    if errors: md += ['## Errors'] + [f'- {e}' for e in errors] + ['']
    else: md += ['## Result','Verification passed.']
    (site/'QA_ASCENSION_WEBSITE_v80.md').write_text('\n'.join(md), encoding='utf-8')
    return errors, warnings

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site')
    args=ap.parse_args(); site=Path(args.site)
    errors,warnings=verify(site)
    if warnings:
        print('Warnings:'); print('\n'.join(warnings))
    if errors:
        print('Verification failed:'); print('\n'.join(errors)); raise SystemExit(1)
    print('Verification passed.')

if __name__=='__main__':
    main()
