
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, html, shutil
from pathlib import Path

ROOT = Path('.')
DATA_PATH = ROOT / 'data' / 'proof-cards' / 'proof-cards-v20.json'
AGIALPHA = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'

CSS = r'''
:root{
  --pc-bg:#07101f; --pc-ink:#f8fbff; --pc-muted:#b9c6d8; --pc-card:#0c1730;
  --pc-card2:#101d3a; --pc-line:rgba(255,255,255,.14); --pc-gold:#d7b46a;
  --pc-cyan:#89e7ff; --pc-green:#80f0b0; --pc-red:#ff7d88; --pc-ivory:#fff8ea;
}
.proof-atlas-v20{background:linear-gradient(180deg,#07101f,#0b1326 58%,#08111f);color:var(--pc-ink);padding:56px 20px;border-top:1px solid var(--pc-line);border-bottom:1px solid var(--pc-line);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.proof-atlas-v20 *{box-sizing:border-box}.proof-atlas-v20 a{color:var(--pc-cyan)}
.pc-wrap{max-width:1220px;margin:0 auto}.pc-eyebrow{color:var(--pc-gold);text-transform:uppercase;letter-spacing:.16em;font-size:12px;font-weight:900}.pc-hero-title{font-size:clamp(38px,6vw,78px);line-height:.92;letter-spacing:-.07em;margin:10px 0 18px}.pc-lede{font-size:20px;line-height:1.55;color:var(--pc-muted);max-width:900px}.pc-grid{display:grid;gap:18px}.pc-grid.cards{grid-template-columns:repeat(auto-fit,minmax(250px,1fr));margin-top:26px}.pc-card{background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.035));border:1px solid var(--pc-line);border-radius:28px;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.25)}.pc-card h3{margin:8px 0 10px;font-size:21px;letter-spacing:-.025em}.pc-card p{color:var(--pc-muted);line-height:1.45}.pc-badge{display:inline-block;border:1px solid rgba(215,180,106,.5);color:var(--pc-gold);border-radius:999px;padding:5px 10px;font-size:12px;font-weight:800}.pc-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}.pc-button{display:inline-flex;align-items:center;gap:8px;text-decoration:none;border:1px solid var(--pc-line);border-radius:999px;padding:10px 14px;background:rgba(255,255,255,.06);font-weight:800}.pc-button.gold{background:linear-gradient(135deg,#d7b46a,#fff1b4);color:#08111f;border:0}.pc-section{margin:44px auto;max-width:1220px}.pc-section h2{font-size:clamp(30px,4vw,54px);line-height:1;letter-spacing:-.055em;margin:0 0 14px}.pc-two{display:grid;grid-template-columns:1fr 1fr;gap:18px}.pc-three{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.pc-table{width:100%;border-collapse:separate;border-spacing:0;background:rgba(255,255,255,.04);border:1px solid var(--pc-line);border-radius:22px;overflow:hidden}.pc-table th,.pc-table td{padding:12px 14px;text-align:left;border-bottom:1px solid var(--pc-line);vertical-align:top}.pc-table th{color:#fff;text-transform:uppercase;font-size:11px;letter-spacing:.1em;background:rgba(255,255,255,.07)}.pc-table td{color:var(--pc-muted);font-size:14px;line-height:1.35}.pc-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:18px}.pc-flow div{border:1px solid var(--pc-line);border-radius:18px;padding:14px;background:rgba(255,255,255,.05);min-height:84px}.pc-flow b{display:block;color:var(--pc-green);margin-bottom:8px}.pc-kpi{display:grid;gap:10px}.pc-kpi-row{display:grid;grid-template-columns:180px 1fr 58px;gap:10px;align-items:center}.pc-bar{height:12px;border-radius:999px;background:rgba(255,255,255,.12);overflow:hidden}.pc-bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--pc-cyan),var(--pc-green),var(--pc-gold))}.pc-chart{border:1px solid var(--pc-line);border-radius:24px;background:rgba(255,255,255,.045);padding:18px;overflow:hidden}.pc-svg{width:100%;height:auto}.pc-callout{border-left:4px solid var(--pc-gold);background:rgba(215,180,106,.09);border-radius:16px;padding:18px;color:var(--pc-ivory)}.pc-meta{display:flex;gap:10px;flex-wrap:wrap}.pc-meta span{border:1px solid var(--pc-line);border-radius:999px;padding:7px 10px;color:var(--pc-muted);font-size:13px}.pc-footer-nav{display:flex;gap:12px;flex-wrap:wrap;justify-content:space-between;margin-top:30px}.pc-masthead{padding:55px 20px 28px;background:radial-gradient(circle at 20% 10%,rgba(137,231,255,.16),transparent 32%),linear-gradient(135deg,#08111f,#111d38);color:#fff;border-bottom:1px solid var(--pc-line)}.pc-masthead .pc-wrap{max-width:1220px}.pc-masthead h1{font-size:clamp(42px,6vw,84px);line-height:.9;letter-spacing:-.07em;margin:10px 0 18px}.pc-page{background:#07101f;color:#f8fbff;min-height:100vh;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}.pc-page main{max-width:1220px;margin:0 auto;padding:36px 20px 70px}.pc-page p{color:var(--pc-muted);line-height:1.6}.pc-nav{position:sticky;top:0;z-index:10;background:rgba(7,16,31,.9);backdrop-filter:blur(16px);border-bottom:1px solid var(--pc-line);padding:12px 20px}.pc-nav-inner{max-width:1220px;margin:0 auto;display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:space-between}.pc-nav a{text-decoration:none;color:var(--pc-muted);font-weight:800;font-size:14px}.pc-nav .brand{color:#fff}.pc-plain{font-size:22px;line-height:1.45;color:#fff;background:rgba(255,255,255,.055);border:1px solid var(--pc-line);border-radius:24px;padding:22px}.pc-number{font-size:64px;letter-spacing:-.08em;color:var(--pc-gold);font-weight:950}.pc-toc{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.pc-toc a{font-size:13px;text-decoration:none;border:1px solid var(--pc-line);border-radius:999px;padding:8px 10px;color:var(--pc-muted)}
@media(max-width:820px){.pc-two,.pc-three{grid-template-columns:1fr}.pc-kpi-row{grid-template-columns:1fr}.pc-masthead h1,.pc-hero-title{letter-spacing:-.045em}}
'''

def esc(x): return html.escape(str(x), quote=True)
def slug_card(card): return f"proof-card-{card['id']}.html"
def read_text(p): return Path(p).read_text(encoding='utf-8', errors='replace')
def write(site, path, text):
    out = site / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')

def page(title, body):
    nav = '''<nav class="pc-nav"><div class="pc-nav-inner"><a class="brand" href="index.html">GoalOS AGIALPHA Ascension</a><span><a href="proof-cards.html">Proof Cards</a> · <a href="agialpha-ledger-route.html">AGIALPHA Route</a> · <a href="sovereign-rsi-control-plane.html">Sovereign RSI</a> · <a href="evidence-docket.html">Evidence Docket</a></span></div></nav>'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><link rel="stylesheet" href="assets/proof-atlas-v20.css"></head><body class="pc-page">{nav}{body}</body></html>'''

def kpi_chart(scores):
    rows=[]
    for item in scores:
        rows.append(f'''<div class="pc-kpi-row"><strong>{esc(item['label'])}</strong><div class="pc-bar"><i style="width:{int(item['score'])}%"></i></div><span>{int(item['score'])}%</span></div>''')
    return '<div class="pc-kpi">' + ''.join(rows) + '</div>'

def flow(items):
    return '<div class="pc-flow">' + ''.join(f'<div><b>{i+1}. {esc(x)}</b><span></span></div>' for i,x in enumerate(items)) + '</div>'

def table(rows, heads=("Layer","Explanation")):
    body=''.join(f'<tr><td><strong>{esc(r[0])}</strong></td><td>{esc(r[1])}</td></tr>' for r in rows)
    return f'<table class="pc-table"><thead><tr><th>{esc(heads[0])}</th><th>{esc(heads[1])}</th></tr></thead><tbody>{body}</tbody></table>'

def agent_table(card):
    rows = card.get('agent_roles', [])
    body=''.join(f'<tr><td><strong>{esc(r[0])}</strong></td><td>{esc(r[1])}</td><td>{esc(r[2])}</td><td>{esc(r[3])}</td><td>{esc(r[4])}</td></tr>' for r in rows)
    return f'<table class="pc-table"><thead><tr><th>Agent cell</th><th>Mandate</th><th>Input</th><th>Output</th><th>Control</th></tr></thead><tbody>{body}</tbody></table>'

def architecture_svg(card):
    # simple institutional SVG diagram
    nodes = ["GoalOS Aim", "Agent Cells", "Evaluator Harness", "ProofBundle", "Reviewer / Red Team", "Selection Gate", "Chronicle", "Future Work"]
    w = 1100; h = 300
    x0=40; gap=130
    rects=[]; arrows=[]
    for i,n in enumerate(nodes):
        x=x0+i*gap; y=100 if i%2==0 else 150
        rects.append(f'<rect x="{x}" y="{y}" width="118" height="58" rx="14" fill="rgba(255,255,255,.08)" stroke="rgba(255,255,255,.25)"/><text x="{x+59}" y="{y+26}" text-anchor="middle" fill="#f8fbff" font-size="13" font-weight="700">{esc(n.split()[0])}</text><text x="{x+59}" y="{y+43}" text-anchor="middle" fill="#b9c6d8" font-size="11">{esc(' '.join(n.split()[1:]))}</text>')
        if i < len(nodes)-1:
            arrows.append(f'<path d="M{x+118},{y+29} C{x+140},{y+29} {x+gap-22},{(150 if (i+1)%2 else 100)+29} {x+gap},{(150 if (i+1)%2 else 100)+29}" fill="none" stroke="#d7b46a" stroke-width="2" marker-end="url(#arrow)"/>')
    return f'''<div class="pc-chart"><svg class="pc-svg" viewBox="0 0 {w} {h}" role="img" aria-label="Proof Card {card['id']} architecture diagram"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#d7b46a"/></marker></defs><text x="30" y="34" fill="#d7b46a" font-size="18" font-weight="900">Institutional proof flow</text><text x="30" y="58" fill="#b9c6d8" font-size="13">{esc(card['title'])}: from mission to selected reusable capability.</text>{''.join(arrows)}{''.join(rects)}</svg></div>'''

def value_ladder_svg(card):
    steps = card.get('value_ladder', [])[:8]
    w=1000; h=360
    bars=[]
    for i,step in enumerate(steps):
        height=34 + i*22
        x=60+i*105; y=300-height
        bars.append(f'<rect x="{x}" y="{y}" width="76" height="{height}" rx="12" fill="rgba(137,231,255,{0.18+i*0.07})" stroke="rgba(255,255,255,.22)"/><text x="{x+38}" y="{y-10}" fill="#f8fbff" text-anchor="middle" font-size="11">{i+1}</text><text x="{x+38}" y="322" fill="#b9c6d8" text-anchor="middle" font-size="10">{esc(step[:18])}</text>')
    return f'''<div class="pc-chart"><svg class="pc-svg" viewBox="0 0 {w} {h}" role="img" aria-label="Value ladder chart"><text x="40" y="35" fill="#d7b46a" font-size="18" font-weight="900">Value-to-capability ladder</text><line x1="40" x2="940" y1="300" y2="300" stroke="rgba(255,255,255,.2)"/>{''.join(bars)}</svg></div>'''

def card_page(cards, idx):
    card = cards[idx]
    prev = cards[idx-1] if idx>0 else None
    nxt = cards[idx+1] if idx < len(cards)-1 else None
    body = f'''<header class="pc-masthead"><div class="pc-wrap"><div class="pc-eyebrow">Proof Card {esc(card['id'])} · {esc(card['portfolio_position'])}</div><h1>{esc(card['title'])}</h1><p class="pc-lede">{esc(card['short'])}</p><div class="pc-meta"><span>{esc(card['domain'])}</span><span>{esc(card['level'])}</span><span>{esc(card['status'])}</span><span>AGIALPHA proof-settlement route</span><span>RSI: proof-backed upgrade rights</span></div><div class="pc-actions"><a class="pc-button gold" href="proof-cards.html">All proof cards</a><a class="pc-button" href="agialpha-ledger-route.html">AGIALPHA route</a><a class="pc-button" href="evidence-docket.html">Evidence Docket</a></div></div></header><main>'''
    body += f'''<div class="pc-toc"><a href="#summary">Summary</a><a href="#visual">Visuals</a><a href="#agents">Agents</a><a href="#skills">Skills</a><a href="#contracts">Contracts</a><a href="#evidence">Evidence</a><a href="#rsi">RSI</a><a href="#boundary">Boundary</a></div>'''
    body += f'''<section id="summary" class="pc-section"><div class="pc-two"><div><h2>In plain English</h2><div class="pc-plain">{esc(card['plain_english'])}</div><p>{esc(card['problem'])}</p></div><div class="pc-card"><span class="pc-badge">Proof mission</span><h3>{esc(card['mission'])}</h3><p><strong>Why it matters:</strong> {esc(card['why'])}</p></div></div></section>'''
    body += f'''<section id="visual" class="pc-section"><h2>Visual operating overview</h2>{architecture_svg(card)}<div class="pc-two"><div><h3>Proof maturity dashboard</h3>{kpi_chart(card['maturity_scores'])}</div><div>{value_ladder_svg(card)}</div></div></section>'''
    body += f'''<section class="pc-section"><h2>Execution flow</h2>{flow(['GoalOSCommit', 'RunCommitment', 'Specialist-agent execution', 'Evaluator report', 'ProofBundle', 'Reviewer/red-team validation', 'SelectionCertificate', 'Chronicle memory'])}</section>'''
    body += f'''<section id="agents" class="pc-section"><h2>Large specialist-agent operating theater</h2><p>The system demonstrates large-scale autonomous coordination by giving each specialist cell a bounded mandate, an input, an output artifact, and a control surface.</p>{agent_table(card)}</section>'''
    body += f'''<section id="skills" class="pc-section"><div class="pc-two"><div><h2>Skills used</h2>{table(card['skill_explanations'][:12], ('Skill','Why it matters'))}</div><div><h2>Plans used</h2>{table(card['plan_explanations'], ('Plan','Execution logic'))}</div></div><div class="pc-section"><h2>Goals and success criteria</h2>{table(card['goal_explanations'][:12], ('Goal','Explanation'))}</div></section>'''
    body += f'''<section id="contracts" class="pc-section"><h2>AGIALPHA and smart-contract / registry route</h2><div class="pc-callout">{esc(card.get('agialpha','AGIALPHA coordinates mission budgets, bonds, review, settlement, credentials, proof cards, and reputation.'))}</div>{table(card['contract_explanations'], ('Contract / Registry','Plain-English function'))}</section>'''
    body += f'''<section id="evidence" class="pc-section"><h2>Evidence Docket checklist</h2><p>Evidence Dockets make claims inspectable without exposing private intelligence or sensitive data.</p>{table(card['evidence_checklist'], ('Evidence item','What it proves'))}</section>'''
    body += f'''<section id="rsi" class="pc-section"><h2>Recursive Self-Improvement logic</h2><div class="pc-callout">{esc(card.get('rsi','Only artifacts that survive proof, evaluation, review, selection, and rollback readiness can influence future work.'))}</div>{flow(['Observe weakness','Improve artifact','Prove change','Review evidence','Select','Grant scoped upgrade rights','Improve future work','Chronicle outcome'])}</section>'''
    body += f'''<section id="boundary" class="pc-section"><h2>Claim boundary</h2><p>This proof card is an experimental public-safe proof-card dossier. It does not claim achieved AGI, superintelligence, guaranteed financial return, legal approval, tax approval, security approval, Ethereum mainnet deployment, or Kardashev Type II achievement.</p><div class="pc-two"><div><h3>FAQ</h3>{table(card['faq'], ('Question','Answer'))}</div><div><h3>Glossary</h3>{table(card['glossary'], ('Term','Meaning'))}</div></div><div class="pc-footer-nav">{f'<a class="pc-button" href="{slug_card(prev)}">← Proof Card {prev["id"]}</a>' if prev else '<span></span>'}<a class="pc-button gold" href="proof-cards.html">Back to proof-card atlas</a>{f'<a class="pc-button" href="{slug_card(nxt)}">Proof Card {nxt["id"]} →</a>' if nxt else '<span></span>'}</div></section>'''
    body += '</main>'
    return page(f"Proof Card {card['id']} - {card['title']}", body)

def gallery(cards):
    cards_html=[]
    for c in cards:
        cards_html.append(f'''<article class="pc-card"><span class="pc-badge">Proof Card {esc(c['id'])}</span><h3>{esc(c['title'])}</h3><p>{esc(c['plain_english'])}</p><p><strong>Domain:</strong> {esc(c['domain'])}</p><a class="pc-button gold" href="{slug_card(c)}">Open card</a></article>''')
    body = f'''<header class="pc-masthead"><div class="pc-wrap"><div class="pc-eyebrow">Institutional Proof Atlas</div><h1>Proof Cards 001-010</h1><p class="pc-lede">Each Proof Card is a public-safe institutional micro-dossier: a proof mission, AGIALPHA coordination route, evidence checklist, RSI upgrade logic, and claim boundary.</p></div></header><main><section class="pc-section"><div class="pc-grid cards">{''.join(cards_html)}</div></section></main>'''
    return page('Proof Cards - GoalOS AGIALPHA Ascension', body)

def support_page(title, subtitle, sections):
    html_sections=[]
    for name, text in sections:
        html_sections.append(f'<section class="pc-section"><h2>{esc(name)}</h2><p>{esc(text)}</p></section>')
    body=f'<header class="pc-masthead"><div class="pc-wrap"><div class="pc-eyebrow">GoalOS AGIALPHA Ascension</div><h1>{esc(title)}</h1><p class="pc-lede">{esc(subtitle)}</p></div></header><main>{"".join(html_sections)}</main>'
    return page(title, body)

def inject_homepage(site, cards):
    index = site/'index.html'
    if not index.exists():
        raise SystemExit('site/index.html missing; refusing to replace main website')
    content=index.read_text(encoding='utf-8', errors='replace')
    if 'assets/proof-atlas-v20.css' not in content:
        content=content.replace('</head>', '<link rel="stylesheet" href="assets/proof-atlas-v20.css">\n</head>')
    cards_html=''.join(f'''<article class="pc-card"><span class="pc-badge">Proof Card {esc(c['id'])}</span><h3>{esc(c['title'])}</h3><p>{esc(c['plain_english'])}</p><a class="pc-button" href="{slug_card(c)}">Open proof card</a></article>''' for c in cards)
    section=f'''<section class="proof-atlas-v20" id="proof-card-command-center"><div class="pc-wrap"><div class="pc-eyebrow">GoalOS AGIALPHA Institutional Proof Atlas</div><h2 class="pc-hero-title">Ten substantial proof-card dossiers.</h2><p class="pc-lede">GoalOS AGIALPHA Ascension turns AI work into auditable institutional capability: AGIALPHA coordinates proof-settled missions, Evidence Dockets make claims inspectable, and RSI reuses only what proved itself.</p><div class="pc-actions"><a class="pc-button gold" href="proof-cards.html">Open the proof-card atlas</a><a class="pc-button" href="agialpha-ledger-route.html">AGIALPHA ledger route</a><a class="pc-button" href="sovereign-rsi-control-plane.html">Sovereign RSI control plane</a></div><div class="pc-grid cards">{cards_html}</div></div></section>'''
    # Remove previous proof sections if present to avoid duplicates
    content = re.sub(r'<section class="proof-atlas-v20" id="proof-card-command-center">.*?</section>\s*', '', content, flags=re.S)
    if '</main>' in content:
        content=content.replace('</main>', section+'</main>')
    elif '</body>' in content:
        content=content.replace('</body>', section+'</body>')
    else:
        content += section
    index.write_text(content, encoding='utf-8')

def build(site: Path, allow_demo=False):
    cards=json.loads(DATA_PATH.read_text(encoding='utf-8'))
    site.mkdir(parents=True, exist_ok=True)
    if not (site/'index.html').exists():
        if not allow_demo:
            raise SystemExit('site/index.html missing; build existing main website first')
        (site/'index.html').write_text(page('GoalOS AGIALPHA Ascension', '<main><section class="pc-masthead"><div class="pc-wrap"><div class="pc-eyebrow">Demo main website</div><h1>GoalOS AGIALPHA Ascension</h1><p class="pc-lede">Demo shell used only for local proof-card integration QA.</p></div></section></main>'), encoding='utf-8')
    (site/'assets').mkdir(exist_ok=True)
    (site/'assets/proof-atlas-v20.css').write_text(CSS, encoding='utf-8')
    inject_homepage(site, cards)
    write(site, 'proof-cards.html', gallery(cards))
    for i,_ in enumerate(cards):
        write(site, slug_card(cards[i]), card_page(cards, i))
    write(site, 'agialpha-ledger-route.html', support_page('AGIALPHA ledger route', 'Where AGIALPHA becomes useful: mission budgets, bonds, settlement, proof-card actions, credentials, reputation, and upgrade rights.', [('Coordination role','AGIALPHA is the proof-work coordination asset. It should not be framed as a guarantee of return; it coordinates useful proof-settled work.'),('Registry route','GoalOSCommit -> RunCommitment -> JobRegistry -> ClaimBond -> ProofSubmission -> ReviewerBond -> ProofCard -> Credential -> Reputation -> EvidenceDocket -> SelectionGate -> Chronicle.')]))
    write(site, 'sovereign-rsi-control-plane.html', support_page('Sovereign RSI control plane', 'Recursive Self-Improvement becomes institutional when only proven artifacts can shape future work.', [('Proof-backed upgrade rights','Artifacts must survive evidence, evaluation, reviewer validation, scope control, challenge windows, monitoring, and rollback readiness.'),('Efficient improvement','The system avoids waste because rejected artifacts do not become future operating context.')]))
    write(site, 'evidence-docket.html', support_page('Evidence Docket', 'The public-safe proof room behind every proof card.', [('What it contains','GoalOSCommit, RunCommitment, ProofBundle, evaluator report, reviewer attestation, risk ledger, cost ledger, SelectionCertificate, rollback path, and Chronicle entry.'),('Public/private boundary','Private intelligence stays private. Public proof anchors become verifiable.')]))
    write(site, 'season-001.html', support_page('Season 001 proof missions', 'A controlled first season of useful proof work.', [('Recommended scope','Start with support, procurement, trust, persistent intelligence, value-to-capability treasury, enterprise RSI, autoresearch, capability foundry, cyber execution, and cyber benchmark proof cards.'),('Success condition','Every accepted mission must leave a public-safe proof card and an Evidence Docket.')]))
    write(site, 'share.html', support_page('Share the Proof Atlas', 'Public-safe lines for explaining the system.', [('Best public line','GoalOS AGIALPHA Ascension turns AI work into auditable institutional capability: AGIALPHA coordinates proof-settled missions, Evidence Dockets make claims inspectable, and RSI reuses only what proved itself.')]))
    # sitemap-ish
    pages=['index.html','proof-cards.html']+[slug_card(c) for c in cards]+['agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
    write(site,'data/proof-cards/proof-cards-v20.json', json.dumps(cards, indent=2, ensure_ascii=False))
    write(site,'proof-atlas-manifest.json', json.dumps({'schema':'goalos.agialpha.proof_atlas.v20','pages':pages,'proof_cards':len(cards)}, indent=2))
    print(f'Integrated {len(cards)} substantial proof cards into {site}')

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    ap.add_argument('--allow-demo-site', action='store_true')
    args=ap.parse_args()
    build(Path(args.site), args.allow_demo_site)
