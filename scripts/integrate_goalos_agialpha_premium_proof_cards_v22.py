#!/usr/bin/env python3
from pathlib import Path
import argparse, html, json, re, shutil

def esc(s): return html.escape(str(s), quote=True)

def load_cards(data_path):
    return json.loads(Path(data_path).read_text(encoding='utf-8'))['cards']

# This CSS is intentionally embedded so the proof atlas remains stable even if the main site CSS changes.
CSS = ''' + repr(CSS) + r'''

def inject_css(site):
    assets=site/'assets'; assets.mkdir(parents=True,exist_ok=True)
    (assets/'proof-cards-v22.css').write_text(CSS,encoding='utf-8')

def patch_head(html_text):
    link='<link rel="stylesheet" href="assets/proof-cards-v22.css">'
    if 'proof-cards-v22.css' in html_text: return html_text
    return html_text.replace('</head>', link+'</head>') if '</head>' in html_text else link+html_text

def card_tile(c):
    return f'''<article class="card"><span class="pill">Proof Card {esc(c['id'])}</span><h3>{esc(c['title'])}</h3><p>{esc(c['short'])}</p><p class="tiny"><strong>Domain:</strong> {esc(c['domain'])}</p><a class="button primary" href="proof-card-{esc(c['id'])}.html">Open stable page</a></article>'''

def atlas_section(cards):
    return f'''<section id="proof-card-command-center" class="section"><div class="wrap"><div class="eyebrow">Proof Card Command Center</div><h2>Proof Cards 001-011</h2><p>Each Proof Card is a substantial public-safe micro-dossier: plain-English explanation, visual operating flow, large multi-agent theater, skills, plans, goals, AGIALPHA route, Evidence Docket checklist, RSI upgrade logic, and claim boundary.</p><div class="grid cards">{''.join(card_tile(c) for c in cards)}</div><div class="actions"><a class="button primary" href="proof-cards.html">Open full proof-card atlas</a><a class="button secondary" href="sovereign-rsi-control-plane.html">View Sovereign RSI control plane</a></div></div></section>'''

def write_page(path, title, body):
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><link rel="stylesheet" href="assets/proof-cards-v22.css"></head><body><div class="top"><div class="wrap nav"><div class="brand">GoalOS AGIALPHA Ascension</div><div><a href="index.html">Home</a><a href="proof-cards.html">Proof Cards</a><a href="agialpha-ledger-route.html">AGIALPHA Route</a><a href="sovereign-rsi-control-plane.html">Sovereign RSI</a><a href="evidence-docket.html">Evidence Docket</a></div></div></div>{body}<footer class="footer"><div class="wrap"><p><strong>GoalOS AGIALPHA Ascension</strong> - public-safe proof-card atlas.</p><p class="tiny">Experimental proof-card system. No claim of achieved AGI, guaranteed financial return, or Ethereum mainnet deployment.</p></div></footer></body></html>'''
    path.write_text(page,encoding='utf-8')

def explain_item(x):
    lx=x.lower()
    if 'commit' in lx or 'goalos' in lx: return 'Turns a mission into a bounded institutional commitment with authority, scope, and success criteria.'
    if 'run' in lx: return 'Defines execution context and replayable route.'
    if 'proof' in lx: return 'Captures inspectable evidence for claims.'
    if 'review' in lx or 'attestation' in lx: return 'Adds accountable validation and challenge.'
    if 'selection' in lx: return 'Determines which artifacts may shape future work.'
    if 'rollback' in lx: return 'Defines how unsafe changes are reversed or contained.'
    if 'chronicle' in lx or 'graph' in lx or 'memory' in lx: return 'Preserves institutional memory for future RSI.'
    if 'treasury' in lx or 'vault' in lx: return 'Routes verified value into settlement and future capability.'
    return 'Supports the proof mission with a bounded artifact or control surface.'

def svg_flow(labels):
    width=980; height=160; n=len(labels); gap=18; boxw=(width-80-gap*(n-1))/n
    parts=[f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="proof flow diagram"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#154276"/><stop offset="1" stop-color="#3cbfd2"/></linearGradient></defs>']
    for i,lbl in enumerate(labels):
        x=40+i*(boxw+gap); y=46
        parts.append(f'<rect x="{x:.1f}" y="{y}" rx="18" width="{boxw:.1f}" height="70" fill="url(#g)"/>')
        parts.append(f'<text x="{x+boxw/2:.1f}" y="{y+31}" text-anchor="middle" fill="white" font-size="13" font-weight="800">{esc(lbl)}</text>')
        if i<n-1: parts.append(f'<path d="M{x+boxw+5:.1f},{y+35} L{x+boxw+gap-5:.1f},{y+35}" stroke="#f2c66d" stroke-width="4" stroke-linecap="round"/>')
    parts.append('</svg>')
    return '<div class="diagram">'+''.join(parts)+'</div>'

def metrics_svg(metrics):
    y=30; rows=''
    for k,v in metrics.items():
        rows += f'<text x="20" y="{y+9}" fill="#dfe9f6" font-size="13" font-weight="700">{esc(k)}</text><rect x="250" y="{y}" width="520" height="14" rx="7" fill="rgba(255,255,255,.15)"/><rect x="250" y="{y}" width="{520*v/100:.1f}" height="14" rx="7" fill="#f2c66d"/><text x="790" y="{y+11}" fill="#fff" font-size="13" font-weight="900">{v}%</text>'
        y += 34
    return f'<div class="diagram"><svg viewBox="0 0 900 {y+20}" role="img" aria-label="proof maturity dashboard">{rows}</svg></div>'

def table_list(title, items):
    rows=''.join(f'<tr><td><strong>{esc(x)}</strong></td><td>{esc(explain_item(x))}</td></tr>' for x in items)
    return f'<h3>{esc(title)}</h3><div class="table-wrap"><table><thead><tr><th>Item</th><th>Explanation</th></tr></thead><tbody>{rows}</tbody></table></div>'

def card_page(c, prev_id, next_id):
    route_rows=''.join(f'<tr><td>{i+1}</td><td><span class="kbd">{esc(x)}</span></td><td>{esc(explain_item(x))}</td></tr>' for i,x in enumerate(c['contracts']))
    agent_rows=''.join(f'<tr><td><strong>{esc(a)}</strong></td><td>{esc(explain_item(a))}</td><td>Evidence artifact, review signal, or control decision.</td></tr>' for a in c['agents'])
    evidence=['GoalOSCommit','RunCommitment','ProofBundle','Evaluator report','Reviewer / red-team attestation','Cost and risk ledger','SelectionCertificate or rejection note','Rollback path','ChronicleEntry']
    evidence_rows=''.join(f'<tr><td>{i+1}</td><td>{esc(x)}</td><td>{esc(explain_item(x))}</td></tr>' for i,x in enumerate(evidence))
    ladder=''.join(f'<div class="stepbox"><b>{i+1}. {esc(s)}</b><p>{esc(explain_item(s))}</p></div>' for i,s in enumerate(c.get('value_steps',[])))
    prev_link=f'<a class="button secondary" href="proof-card-{prev_id}.html">Previous</a>' if prev_id else '<span></span>'
    next_link=f'<a class="button primary" href="proof-card-{next_id}.html">Next</a>' if next_id else '<a class="button primary" href="proof-cards.html">Back to atlas</a>'
    body=f'''<section class="proof-hero"><div class="wrap hero-grid"><div><div class="eyebrow">Proof Card {esc(c['id'])} / {esc(c['domain'])}</div><h1>{esc(c['title'])}</h1><p>{esc(c['short'])}</p><div class="chips"><span class="chip">{esc(c['proof_level'])}</span><span class="chip">AGIALPHA</span><span class="chip">Evidence Docket</span><span class="chip">RSI</span></div></div><div class="hero-card"><div class="eyebrow">In plain English</div><p>{esc(c['mission'])}</p><p><strong>Status:</strong> {esc(c['status'])}</p></div></div></section><section class="section"><div class="wrap page-grid"><aside class="toc"><a href="#why">Why it matters</a><a href="#flow">Visual flow</a><a href="#agents">Agents</a><a href="#skills">Skills / plans / goals</a><a href="#contracts">Contracts</a><a href="#evidence">Evidence</a><a href="#rsi">RSI</a><a href="#boundary">Boundary</a></aside><main><section id="why"><h2>Why this matters</h2><p>{esc(c['problem'])}</p><div class="callout"><div class="quote">{esc(c['why'])}</div></div></section><section id="flow"><h2>Visual operating flow</h2>{svg_flow(['Aim','Decompose','Route','Build','Evaluate','Review','Select','Chronicle'])}{metrics_svg(c['metrics'])}<h3>Value-to-capability ladder</h3><div class="value-ladder">{ladder}</div></section><section id="agents"><h2>Large specialist-agent operating theater</h2><p>Each specialist cell has a bounded mandate, emits evidence, and hands work to the next control surface.</p><div class="table-wrap"><table><thead><tr><th>Agent cell</th><th>Responsibility</th><th>Output</th></tr></thead><tbody>{agent_rows}</tbody></table></div></section><section id="skills"><h2>Skills, plans, and goals</h2>{table_list('Skills used', c['skills'])}{table_list('Plans used', c['plans'])}{table_list('Goals used', c['goals'])}</section><section id="contracts"><h2>AGIALPHA + contract route</h2><p>AGIALPHA coordinates proof-settled mission budgets, bonds, proof submission, review, proof-card actions, credential issuance, reputation-linked routing, reward-vault settlement, treasury reinvestment, and Chronicle memory.</p><div class="table-wrap"><table><thead><tr><th>#</th><th>Contract / registry</th><th>Purpose</th></tr></thead><tbody>{route_rows}</tbody></table></div></section><section id="evidence"><h2>Evidence Docket</h2><div class="table-wrap"><table><thead><tr><th>#</th><th>Evidence item</th><th>Purpose</th></tr></thead><tbody>{evidence_rows}</tbody></table></div></section><section id="rsi"><h2>Recursive Self-Improvement logic</h2><p>RSI is proof-backed upgrade rights. Unproven work cannot become future operating context. Replayed, reviewed, and selected work can.</p>{svg_flow(['Weakness','Candidate','Proof','Review','Selection','Upgrade Rights','Future Work'])}</section><section id="boundary"><h2>Claim boundary</h2><p>Experimental proof-card page. It does not claim achieved AGI, achieved superintelligence, guaranteed financial return, legal/tax/security approval, Ethereum mainnet deployment, or Kardashev Type II achievement.</p></section><div class="proof-nav">{prev_link}{next_link}</div></main></div></section>'''
    return body

def render_support_page(title, body):
    return f'<section class="hero"><div class="wrap"><div class="eyebrow">GoalOS AGIALPHA</div><h1>{esc(title)}</h1></div></section><section class="section"><div class="wrap">{body}</div></section>'

def integrate(site, cards):
    site.mkdir(parents=True,exist_ok=True)
    inject_css(site)
    # patch or create homepage
    index=site/'index.html'
    if index.exists():
        txt=patch_head(index.read_text(encoding='utf-8',errors='replace'))
        sec=atlas_section(cards)
        if 'id="proof-card-command-center"' not in txt:
            txt=txt.replace('</body>', sec+'</body>') if '</body>' in txt else txt+sec
        index.write_text(txt,encoding='utf-8')
    else:
        write_page(site/'index.html','GoalOS AGIALPHA Ascension',atlas_section(cards))
    # gallery and cards
    gallery=f'<section class="hero"><div class="wrap"><div class="eyebrow">Proof-card atlas</div><h1>Proof Cards 001-011</h1><p>Substantial public-safe micro-dossiers for GoalOS AGIALPHA Ascension.</p></div></section><section class="section"><div class="wrap"><div class="grid cards">{"".join(card_tile(c) for c in cards)}</div></div></section>'
    write_page(site/'proof-cards.html','Proof Cards',gallery)
    for i,c in enumerate(cards):
        body=card_page(c, cards[i-1]['id'] if i else None, cards[i+1]['id'] if i < len(cards)-1 else None)
        write_page(site/f'proof-card-{c["id"]}.html',f'Proof Card {c["id"]} - {c["title"]}',body)
    write_page(site/'agialpha-ledger-route.html','AGIALPHA ledger route',render_support_page('AGIALPHA ledger route',svg_flow(['Budget','Bond','Proof','Review','Card','Credential','Reputation','Treasury'])))
    write_page(site/'sovereign-rsi-control-plane.html','Sovereign RSI control plane',render_support_page('Sovereign RSI control plane',svg_flow(['Observe','Improve','Prove','Review','Select','Upgrade','Reinvest','Chronicle'])))
    write_page(site/'evidence-docket.html','Evidence Docket',render_support_page('Evidence Docket',svg_flow(['Claim','Baseline','Run','ProofBundle','Attestation','Cost/Risk','Selection','Chronicle'])))
    write_page(site/'season-001.html','Season 001',render_support_page('Season 001 proof missions','<div class="grid cards">'+''.join(card_tile(c) for c in cards[:5])+'</div>'))
    write_page(site/'share.html','Share kit',render_support_page('Share kit','<p>GoalOS AGIALPHA Ascension turns AI work into auditable institutional capability: AGIALPHA coordinates proof-settled missions, Evidence Dockets make claims inspectable, and RSI reuses only what proved itself.</p>'))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--site',default='site')
    ap.add_argument('--data',default='data/proof-cards/proof-cards-v22.json')
    args=ap.parse_args()
    cards=load_cards(args.data)
    integrate(Path(args.site),cards)
    print(f'Integrated premium Proof Cards 001-{cards[-1]["id"]} into {args.site}')
if __name__=='__main__': main()
