#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil, html, datetime, hashlib, subprocess, os, textwrap, re

RELEASE = 'v81'
ROOT = Path(__file__).resolve().parents[1]
ASSET_MAIN = 'assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png'
PAPER_SRC = 'docs/papers/mission-os/GoalOS_Mission_OS_Paper.pdf'
PAPER_OUT = 'downloads/mission-os/GoalOS_Mission_OS_Paper.pdf'
PRIMARY_NAV = [('Home','index.html'),('Mission OS','mission-os.html'),('Ascension','ascension.html'),('Proof Treasury','proof-treasury.html'),('Proof Cards','proof-cards.html'),('Paper','paper.html'),('Resources','resources.html')]
SECONDARY_NAV = [('Proof Run 001','proof-run-001.html'),('Evidence Docket','evidence-docket.html'),('Observatory','observatory.html'),('AGI Alpha Continuity','agialpha-continuity.html'),('Start Here','start-here.html'),('Mission Builder','mission-builder.html')]
CANON = [
'Turn AI work into verified capability.', 'AI creates output. GoalOS creates proof.', 'GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.', 'SOTA is a measurement. Ascension is the mission.', 'The product is not output. The product is proof-backed capability.', 'No proof, no settlement.', 'No replay, no reinvestment.', 'No external replay, no capacity scale.', 'No stress clearance, no institutional scale.', 'No delayed-outcome clearance, no Ascension reserve compounding.', 'No governance, no acceleration.', '0 claims without proof.'
]
PROOF_CARDS = json.loads((ROOT/'website/content/proof_cards_v81.json').read_text(encoding='utf-8'))
ASSET_MANIFEST = json.loads((ROOT/'website/content/assets_manifest_v81.json').read_text(encoding='utf-8'))

def esc(s): return html.escape(str(s), quote=True)

def h(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:12]

CSS = r'''
:root{--ink:#06111f;--ink2:#0d1830;--panel:rgba(10,22,42,.78);--panel2:rgba(255,255,255,.075);--gold:#f3d98b;--gold2:#d6ad4d;--cream:#fff4dc;--mint:#74ffd6;--cyan:#78c8ff;--violet:#a78dff;--text:#f7fbff;--muted:#b9c6d8;--danger:#ff7f8f;--ok:#7df2ac;--line:rgba(255,255,255,.14);--r:28px;--shadow:0 30px 90px rgba(0,0,0,.42),0 0 60px rgba(116,255,214,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:radial-gradient(circle at 16% 10%,rgba(116,255,214,.16),transparent 25%),radial-gradient(circle at 82% 18%,rgba(167,141,255,.20),transparent 30%),linear-gradient(135deg,#051120,#131a39 58%,#211335);color:var(--text);overflow-x:clip}a{color:inherit;text-decoration:none}img,svg,canvas,video{max-width:100%;height:auto}p{line-height:1.65;color:#dce7f6} .skip{position:absolute;left:-999px}.skip:focus{left:1rem;top:1rem;background:#fff;color:#000;padding:.7rem;border-radius:.5rem;z-index:1000}.nav{position:sticky;top:0;z-index:50;background:rgba(255,244,220,.94);backdrop-filter:blur(18px);border-bottom:1px solid rgba(0,0,0,.08)}.nav .inner{max-width:1180px;margin:auto;display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.8rem 1rem}.brand{display:flex;gap:.7rem;align-items:center;color:#06111f;font-weight:1000;letter-spacing:.08em;font-size:.88rem}.mark{width:34px;height:34px;border-radius:12px;background:radial-gradient(circle at 35% 25%,#ffe08a,#74ffd6 45%,#a78dff);box-shadow:0 0 25px rgba(116,255,214,.55)}.links{display:flex;gap:.25rem;flex-wrap:wrap;justify-content:flex-end}.links a{color:#07111f;font-weight:900;font-size:.86rem;padding:.72rem .78rem;border-radius:999px}.links a:hover,.links a:focus{background:rgba(6,17,31,.08);outline:none}.wrap{width:min(1120px,calc(100% - 2rem));margin:0 auto}.hero{position:relative;min-height:calc(100vh - 64px);display:grid;align-items:center;padding:6rem 0 5rem}.hero-grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(320px,.95fr);gap:3rem;align-items:center}.eyebrow{display:inline-flex;align-items:center;gap:.5rem;border:1px solid rgba(243,217,139,.58);background:rgba(243,217,139,.12);color:var(--gold);font-weight:1000;letter-spacing:.14em;text-transform:uppercase;border-radius:999px;padding:.55rem .85rem;font-size:.74rem}.h1{font-size:clamp(3.3rem,8vw,8.7rem);line-height:.88;margin:.8rem 0 1rem;letter-spacing:-.08em;font-weight:1000;text-wrap:balance}.h2{font-size:clamp(2.2rem,5vw,5.1rem);line-height:.95;margin:.5rem 0 1rem;letter-spacing:-.06em;font-weight:1000;text-wrap:balance}.lead{font-size:clamp(1.1rem,2vw,1.45rem);max-width:780px;font-weight:750;color:#dce8f6}.accent{color:var(--gold)}.cta{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.4rem}.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;border-radius:999px;padding:.95rem 1.2rem;font-weight:1000;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.09);box-shadow:0 8px 30px rgba(0,0,0,.22)}.btn.primary{background:linear-gradient(135deg,var(--gold),#fff0ae);color:#06111f;border-color:rgba(255,224,138,.75)}.btn:hover,.btn:focus{transform:translateY(-1px);outline:2px solid rgba(116,255,214,.4)}.chips{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1.5rem}.chip{border:1px solid var(--line);background:rgba(255,255,255,.08);border-radius:18px;padding:.75rem 1rem;font-weight:900;color:#eaf3ff}.visual-shell,.figure-frame,.diagram-frame,.proof-card-visual,.card,.panel{overflow:hidden;position:relative;contain:layout paint}.visual-shell{border:1px solid rgba(255,255,255,.17);background:linear-gradient(145deg,rgba(255,255,255,.10),rgba(255,255,255,.04));border-radius:34px;padding:1rem;box-shadow:var(--shadow)}.visual-shell:before{content:"";position:absolute;inset:-20%;background:conic-gradient(from 45deg,transparent,rgba(116,255,214,.26),transparent,rgba(167,141,255,.28),transparent);animation:spin 20s linear infinite;opacity:.55}.visual-shell>*{position:relative}.hero-img{border-radius:26px;width:100%;display:block;object-fit:contain;background:#07111f}.caption{font-size:.86rem;color:#bfd1e8;margin:.7rem .4rem 0}.section{padding:5rem 0}.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.09),rgba(255,255,255,.04));border-radius:var(--r);padding:1.35rem;box-shadow:0 18px 60px rgba(0,0,0,.25)}.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.25rem}.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.25rem}.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}.card{border:1px solid var(--line);background:rgba(255,255,255,.07);border-radius:24px;padding:1.2rem}.card h3,.panel h3{margin:.1rem 0 .5rem;font-size:1.25rem}.tag{display:inline-block;color:var(--gold);font-weight:1000;text-transform:uppercase;letter-spacing:.13em;font-size:.72rem}.diagram-frame{background:rgba(1,10,22,.78);border:1px solid rgba(255,255,255,.12);border-radius:26px;padding:1rem;margin:1rem 0;box-shadow:inset 0 0 0 1px rgba(243,217,139,.05)}.diagram-frame svg{width:100%;height:auto;display:block}.figure-frame{border:1px solid rgba(255,255,255,.15);border-radius:24px;background:rgba(255,255,255,.06);padding:.65rem}.figure-frame img{width:100%;display:block;border-radius:18px;object-fit:contain}.table-wrap{overflow:auto;border-radius:20px;border:1px solid var(--line);margin:1rem 0}table{width:100%;border-collapse:collapse;min-width:640px;background:rgba(255,255,255,.05)}th,td{text-align:left;border-bottom:1px solid rgba(255,255,255,.12);padding:1rem;vertical-align:top}th{color:var(--gold);background:rgba(0,0,0,.22);font-weight:1000}.law{border-left:4px solid var(--gold);padding:1rem 1.1rem;background:rgba(243,217,139,.09);border-radius:0 20px 20px 0;font-weight:900}.claim{border:1px solid rgba(255,127,143,.35);background:rgba(255,127,143,.07)}.footer{padding:3rem 0;border-top:1px solid var(--line);background:rgba(0,0,0,.24)}.asset-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.proof-atlas{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.proof-tile{min-height:250px;display:flex;flex-direction:column;justify-content:space-between}.proof-tile .num{color:var(--gold);font-size:2rem;font-weight:1000}.paper-cover{aspect-ratio:3/4;display:grid;place-items:center;background:linear-gradient(135deg,#f8fafc,#dbeafe);color:#07111f;border-radius:22px;text-align:left;padding:1.5rem;box-shadow:0 20px 55px rgba(0,0,0,.25)}.paper-cover b{font-size:2rem;line-height:1}.halo{position:absolute;inset:-10%;pointer-events:none;background:radial-gradient(circle at 30% 30%,rgba(116,255,214,.2),transparent 25%),radial-gradient(circle at 70% 50%,rgba(167,141,255,.22),transparent 32%);filter:blur(8px);animation:pulse 6s ease-in-out infinite}.bg-grid{position:fixed;inset:0;z-index:-2;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(to bottom,#000,transparent 88%)}.bg-aura{position:fixed;inset:0;z-index:-3;background:linear-gradient(135deg,#051120,#111c36 58%,#201233)}@keyframes spin{to{transform:rotate(360deg)}}@keyframes pulse{50%{opacity:.65;transform:scale(1.03)}}@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;scroll-behavior:auto!important;transition:none!important}}@media (max-width:900px){.hero-grid,.grid2,.grid3,.grid4,.asset-row,.proof-atlas{grid-template-columns:1fr}.hero{min-height:auto}.links{max-width:100%;justify-content:center}.h1{font-size:clamp(3rem,16vw,5.4rem)}}@media (max-width:520px){.nav .inner{flex-direction:column}.links a{font-size:.78rem;padding:.55rem}.wrap{width:min(100% - 1rem,1120px)}.section{padding:3rem 0}.panel,.card{padding:1rem}.h1{letter-spacing:-.06em}}
'''


def write(path, s):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding='utf-8')


def nav_html():
    links = ''.join(f'<a href="{href}">{label}</a>' for label, href in PRIMARY_NAV)
    return f'<a class="skip" href="#content">Skip to content</a><nav class="nav" aria-label="Primary"><div class="inner"><a class="brand" href="index.html"><span class="mark" aria-hidden="true"></span><span>GOALOS AGIALPHA</span></a><div class="links">{links}</div></div></nav>'


def base(title, body, desc='GoalOS AGIALPHA Ascension'):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | GoalOS AGIALPHA</title><meta name="description" content="{esc(desc)}"><link rel="manifest" href="manifest.webmanifest"><style>{CSS}</style></head><body><div class="bg-aura"></div><div class="bg-grid"></div>{nav_html()}<main id="content">{body}</main>{footer()}<script>document.documentElement.classList.add('js');</script></body></html>'''


def footer():
    secondary = ' · '.join(f'<a href="{href}">{label}</a>' for label, href in SECONDARY_NAV)
    canon = ' '.join(CANON[:4])
    return f'<footer class="footer"><div class="wrap"><p><b>Public alpha · claim-bounded.</b> {esc(canon)}</p><p>{secondary}</p><p class="caption">No achieved AGI, ASI, superintelligence, guaranteed ROI, token appreciation, live Mainnet settlement, production certification, external audit completion, energy abundance, or Kardashev Type II achievement is claimed.</p></div></footer>'


def flow_svg(nodes, title='Proof flow', colors=None):
    colors = colors or ['#78c8ff','#a78dff','#f3d98b','#74ffd6','#d6ad4d','#ff9aaa']
    n = len(nodes); w = 1040; h = 260
    gap = w/(n+1)
    circles = []
    lines = []
    for i,node in enumerate(nodes, start=1):
        x = gap*i; y = h/2 + (18 if i%2==0 else -18)
        if i>1:
            px=gap*(i-1); py=h/2 + (18 if (i-1)%2==0 else -18)
            lines.append(f'<path d="M {px+64:.1f} {py:.1f} C {(px+x)/2:.1f} {py:.1f}, {(px+x)/2:.1f} {y:.1f}, {x-64:.1f} {y:.1f}" fill="none" stroke="#f3d98b" stroke-width="8" stroke-linecap="round" stroke-dasharray="12 16" opacity=".88"/>')
        label = esc(node)
        c = colors[(i-1)%len(colors)]
        circles.append(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="58" fill="rgba(10,22,42,.95)" stroke="{c}" stroke-width="4"/><text x="{x:.1f}" y="{y-5:.1f}" text-anchor="middle" fill="#fff" font-size="22" font-weight="900">{label[:14]}</text><text x="{x:.1f}" y="{y+20:.1f}" text-anchor="middle" fill="#b9c6d8" font-size="14" font-weight="700">{label[14:28]}</text></g>')
    return f'<div class="diagram-frame"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}"><rect width="{w}" height="{h}" rx="28" fill="rgba(2,10,25,.72)"/><text x="{w/2}" y="34" text-anchor="middle" fill="#fff" font-size="24" font-weight="900">{esc(title)}</text>{"".join(lines)}{"".join(circles)}</svg></div>'


def orbit_svg(center, nodes, title='Agent constellation'):
    w=900; h=560; cx=w/2; cy=h/2
    rings = ''.join(f'<ellipse cx="{cx}" cy="{cy}" rx="{220+i*45}" ry="{112+i*22}" fill="none" stroke="rgba(255,255,255,.17)" stroke-width="2" transform="rotate({i*22} {cx} {cy})"/>' for i in range(3))
    items=[]
    import math
    for i,node in enumerate(nodes):
        ang=2*math.pi*i/len(nodes)-math.pi/2
        rx=300 if i%2 else 240; ry=190 if i%2 else 150
        x=cx+rx*math.cos(ang); y=cy+ry*math.sin(ang)
        col=['#78c8ff','#a78dff','#f3d98b','#74ffd6'][i%4]
        items.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="rgba(255,255,255,.16)"/><circle cx="{x}" cy="{y}" r="54" fill="rgba(10,22,42,.96)" stroke="{col}" stroke-width="3"/><text x="{x}" y="{y-2}" text-anchor="middle" fill="#fff" font-size="17" font-weight="900">{esc(node[:12])}</text><text x="{x}" y="{y+17}" text-anchor="middle" fill="#b9c6d8" font-size="12" font-weight="700">{esc(node[12:24])}</text>')
    return f'<div class="diagram-frame"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}"><rect width="{w}" height="{h}" rx="30" fill="rgba(2,10,25,.72)"/><text x="{cx}" y="42" text-anchor="middle" fill="#fff" font-size="26" font-weight="900">{esc(title)}</text>{rings}{"".join(items)}<circle cx="{cx}" cy="{cy}" r="86" fill="rgba(243,217,139,.16)" stroke="#f3d98b" stroke-width="4"/><text x="{cx}" y="{cy-4}" text-anchor="middle" fill="#fff" font-size="26" font-weight="1000">{esc(center)}</text><text x="{cx}" y="{cy+25}" text-anchor="middle" fill="#f3d98b" font-size="15" font-weight="900">maximum verified effect</text></svg></div>'


def table(rows, headers=('Component','Function','Evidence object','Gate','Next action')):
    th=''.join(f'<th>{esc(x)}</th>' for x in headers)
    trs=''.join('<tr>'+''.join(f'<td>{esc(c)}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def page_hero(title, subtitle, eyebrow='GOALOS AGIALPHA · v81', visual=''):
    return f'<section class="hero"><div class="wrap hero-grid"><div><span class="eyebrow">{esc(eyebrow)}</span><h1 class="h1">{esc(title)}</h1><p class="lead">{esc(subtitle)}</p><div class="cta"><a class="btn primary" href="mission-os.html">Open Mission OS</a><a class="btn" href="paper.html">Read the Paper</a><a class="btn" href="proof-cards.html">Proof Cards</a></div></div><div>{visual}</div></div></section>'


def figure_asset(path, caption, alt, extra_cls=''):
    return f'<figure class="figure-frame {extra_cls}"><img src="{esc(path)}" alt="{esc(alt)}"><figcaption class="caption">{esc(caption)}</figcaption></figure>'


def available_asset(filename):
    return (ROOT/filename).exists()


def copy_assets(out):
    qa={'available_assets':[], 'missing_assets':[]}
    for asset in ['assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png','assets/AGI_ALPHA_v12.png','assets/AGI_ALPHA_v13.png','assets/AGI_ALPHA_v14.png','assets/AGI_ALPHA_v16.png','assets/AGI_ALPHA_v18.png','assets/AGI_ALPHA_v20.png','assets/AGI_Ascension_Autonomous_Multi-Agent_Coordination_v10.png','assets/AGI_Ascension_Autonomous_Multi-Agent_Coordination_v9.png','assets/pc008_agent_coordination_matrix.png','assets/pc008_domain_radar.png','assets/pc008_proof_card_ladder.png','assets/pc008_value_capability_flywheel.png','assets/pc009_flywheel.png','assets/pc009_matrix.png','assets/pc009_radar.png']:
        src=ROOT/asset
        if src.exists():
            dst=out/asset; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src,dst); qa['available_assets'].append(asset)
        else:
            qa['missing_assets'].append(asset)
    if not (out/ASSET_MAIN).exists():
        raise SystemExit(f'Missing required main asset: {ASSET_MAIN}')
    if (ROOT/PAPER_SRC).exists():
        dst=out/PAPER_OUT; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/PAPER_SRC,dst)
    return qa


def create_paper_cover(out):
    gen=out/'assets/generated'; gen.mkdir(parents=True, exist_ok=True)
    cover_svg=gen/'mission-os-paper-cover.svg'
    cover_png=gen/'mission-os-paper-cover.png'
    # Fallback SVG is deterministic and good enough if pdftoppm unavailable.
    svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 960"><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#fff7df"/><stop offset="1" stop-color="#cfe7ff"/></linearGradient></defs><rect width="720" height="960" rx="34" fill="url(#g)"/><rect x="55" y="55" width="610" height="850" rx="26" fill="#ffffff" opacity=".82"/><text x="95" y="145" fill="#06111f" font-family="Arial" font-weight="900" font-size="36">GOALOS MISSION OS</text><text x="95" y="245" fill="#06111f" font-family="Arial" font-weight="900" font-size="62">The Proof OS</text><text x="95" y="318" fill="#06111f" font-family="Arial" font-weight="900" font-size="58">for Autonomous</text><text x="95" y="391" fill="#06111f" font-family="Arial" font-weight="900" font-size="58">AI Work</text><text x="95" y="505" fill="#0d4968" font-family="Arial" font-weight="700" font-size="28">Set the objective.</text><text x="95" y="548" fill="#0d4968" font-family="Arial" font-weight="700" font-size="28">GoalOS runs until proof is done.</text><text x="95" y="680" fill="#06111f" font-family="Arial" font-weight="700" font-size="26">AI creates output. GoalOS creates proof.</text><text x="95" y="820" fill="#64748b" font-family="Arial" font-size="24">Publication-safe, claim-bounded edition.</text></svg>'''
    cover_svg.write_text(svg, encoding='utf-8')
    # Try to render PDF cover if possible, else create simple PNG placeholder by copying not possible; keep svg and create tiny png? Use svg as visual and set cover path to svg.
    pdf=out/PAPER_OUT
    if pdf.exists():
        try:
            subprocess.run(['pdftoppm','-png','-singlefile','-f','1','-l','1','-scale-to','900',str(pdf),str(gen/'mission-os-paper-cover')], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return 'assets/generated/mission-os-paper-cover.png'
        except Exception:
            pass
    return 'assets/generated/mission-os-paper-cover.svg'


def hero_visual():
    return f'<div class="visual-shell"><div class="halo"></div><img class="hero-img" src="{ASSET_MAIN}" alt="GoalOS AGIALPHA Ascension hero visual"><p class="caption">GoalOS AGIALPHA Ascension: proof-governed autonomous AI work. All critical claims are live HTML, not image text.</p></div>'


def section(title, subtitle='', content=''):
    return f'<section class="section"><div class="wrap"><span class="tag">{esc(title)}</span>{f"<h2 class=\"h2\">{esc(subtitle)}</h2>" if subtitle else ""}{content}</div></section>'


def homepage(out, cover, asset_qa):
    asset_cards=''
    # Use assets meaningfully with cards only if present; section has a strong title, not generic v80 title.
    roles=[('AGI_ALPHA_v12.png','Lineage figure','AGI Alpha continuity figure for agent labor and proof economy.'),('AGI_ALPHA_v13.png','Marketplace figure','Agent marketplace continuity visual.'),('AGI_ALPHA_v14.png','Proof economy figure','Proof economy and validator orbit visual.'),('AGI_ALPHA_v16.png','Agent identity figure','Agent identity, sovereignty, and coordination visual.'),('AGI_ALPHA_v18.png','Validator economy figure','Validation and incentive continuity visual.'),('AGI_ALPHA_v20.png','Alpha Flywheel figure','Flywheel continuity visual.'),('AGI_Ascension_Autonomous_Multi-Agent_Coordination_v10.png','Multi-agent institution figure','Autonomous multi-agent coordination and proof-bound execution visual.'),('AGI_Ascension_Autonomous_Multi-Agent_Coordination_v9.png','Ascension coordination figure','Coordination swarm and proof-bound intelligence visual.')]
    for fn,role,cap in roles:
        if (out/'assets'/fn).exists():
            asset_cards += f'<div class="card">{figure_asset("assets/"+fn, cap, role)}<h3>{esc(role)}</h3><p>{esc(cap)}</p></div>'
    if not asset_cards:
        # no generic gallery; give a statement and use generated diagrams instead.
        asset_cards = '<div class="panel"><p class="law">Additional AGI Alpha visual assets were not present in this repository checkout. The build reports them in QA and uses generated institutional SVG figures instead of dumping missing placeholders.</p></div>'
    body = page_hero('Turn AI work into verified capability.', 'GoalOS is the proof-governed operating regime for autonomous AI work: Mission OS plans the work, specialist agents execute, Evidence Dockets prove, reviewers validate, $AGIALPHA makes accepted proof economically consequential, and Chronicle memory enables safer Recursive Self-Improvement.', visual=hero_visual())
    body += section('Paper', 'Read the GoalOS Mission OS Paper', f'<div class="grid2"><div class="panel"><h3>GoalOS Mission OS — The Proof OS for Autonomous AI Work</h3><p class="lead">Set the objective. GoalOS runs until proof is done. AI creates output. GoalOS creates proof.</p><p>The paper defines governed decision states, Evidence Dockets, verifier reports, risk ledgers, executive briefs, action graphs, Chronicle memory, and claim boundaries.</p><div class="cta"><a class="btn primary" href="{PAPER_OUT}">Read / Download Paper</a><a class="btn" href="mission-os.html">Open Mission OS</a></div></div>{figure_asset(cover,"Mission OS Paper front-page visual. Title and claims are repeated as live HTML.","Mission OS Paper front-page preview")}</div>')
    body += section('What GoalOS does','Most AI gives you output. GoalOS gives you proof-backed progress. The product is not output. The product is proof-backed capability.', '<div class="grid3">' + ''.join(f'<div class="card"><h3>{x}</h3><p>{d}</p></div>' for x,d in [('Evidence Docket','A public-safe proof room for claims, baselines, proofs, costs, risks, and replay.'),('Claims Matrix','The boundary between what is claimed, not claimed, and not yet known.'),('Chronicle','Durable memory of accepted work, failures, and reusable capability.')]) + '</div>' + flow_svg(['Objective','Mission OS','Agents','Evidence Docket','Review','$AGIALPHA','Chronicle','Harder Mission'],'GoalOS proof-to-capability loop'))
    body += section('From AGI Alpha to GoalOS','Agent labor market → proof-governed Mission OS → Evidence Docket → Proof Treasury → Ascension.', f'<div class="grid2"><div class="panel"><p class="lead">AGI Alpha makes autonomous AI work addressable through agent identity, jobs, validators, MCP-native access, and $AGIALPHA utility. GoalOS governs what that labor can be trusted to become.</p><pre class="panel" aria-label="illustrative MCP motif">{{\n  "mcpServers": {{\n    "agi-alpha": {{ "url": "&lt;mcp-endpoint&gt;" }}\n  }}\n}}</pre><p class="caption">Illustrative continuity motif only; no outbound AGI Alpha reference links are emitted.</p></div><div>{flow_svg(['Agent Job Market','Mission OS','Evidence Docket','Proof Treasury','Ascension'],'AGI Alpha continuity into GoalOS')}</div></div><div class="asset-row">{asset_cards}</div>')
    body += section('Large Multi-Agent Institution','A specialist-agent constellation for maximum verified effect.', orbit_svg('GoalOS',['Aim Council','Planner','Builder Forge','Evidence Office','Verifier Tribunal','Red-Team Court','Treasury Router','Chronicle RSI','Governance']))
    body += section('Ascension','SOTA is a measurement. Ascension is the mission.', '<p class="lead">SOTA measures performance. Ascension governs consequence.</p>'+flow_svg(['Unmet Need','GoalOSCommit','Specialist Theater','Evidence Docket','α-Work Units','$AGIALPHA','Chronicle','RSI','Harder Mission'],'Ascension proof-governed compounding loop')+table([['VerifiedCapability','Accepted work that survives proof.','Evidence Docket','Verifier gate','Reuse'],['SettlementPressure','Economic consequence after proof.','α-Work Unit','$AGIALPHA utility','Capacity allocation'],['ChronicleMemory','Reusable institutional memory.','Chronicle Entry','Replay gate','RSI update']], headers=('Factor','Meaning','Object','Gate','Compounds into')))
    body += section('$AGIALPHA','GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.', '<p class="lead">GoalOS can create proof without a wallet. $AGIALPHA becomes useful when accepted proof needs escrow, bonds, validator incentives, α‑Work Units, reputation, slashing, treasury reinvestment, and capacity allocation.</p>'+flow_svg(['Request','Escrow','Execute','Proof','Validate','Settle','Chronicle','Reinvest'],'$AGIALPHA proof economy rail')+'<p class="law">$AGIALPHA is proof-settlement fuel and protocol utility. It is not equity, dividend, yield, ownership, guaranteed return, or token-price claim.</p>')
    body += section('Proof Treasury','Proof decides settlement. Replay decides reinvestment. Delayed outcomes decide reserve compounding.', '<div class="grid3">' + ''.join(f'<div class="card"><span class="tag">Simulation {i:03d}</span><h3>{title}</h3><p>{law}</p><a class="btn" href="proof-treasury-simulation-{i:03d}.html">Open simulation</a></div>' for i,title,law in [(3,'External Replay Market','No external replay, no capacity scale.'),(4,'Institutional Stress Gauntlet','No stress clearance, no institutional scale.'),(5,'Delayed-Outcome Covenant','No delayed-outcome clearance, no Ascension reserve compounding.')]) + '</div>')
    body += section('Proof Card Atlas','Every Proof Card is a complete, unique, illustrated proof page.', '<p class="lead">30 stable proof cards published; Proof Card 023 reserved.</p><div class="cta"><a class="btn primary" href="proof-cards.html">Open the Atlas</a><a class="btn" href="paper.html">Read the Paper</a></div>')
    body += section('Evidence Roadmap','Proof Run 001 is the next threshold, not the centerpiece.', '<div class="panel"><p>Proof Run 001 exists as a sober evidence-roadmap page. The public centerpiece remains GoalOS, Mission OS, Ascension, Proof Cards, Paper, and Proof Treasury.</p><a class="btn" href="proof-run-001.html">View next evidence threshold</a></div>')
    body += claim_boundary_section()
    write(out/'index.html', base('Home', body, 'Turn AI work into verified capability.'))


def claim_boundary_section():
    laws = '<p class="law">No proof, no settlement. No replay, no reinvestment. No external replay, no capacity scale. No stress clearance, no institutional scale. No delayed-outcome clearance, no Ascension reserve compounding. No governance, no acceleration. 0 claims without proof.</p>'
    return section('Claim Boundary','Grand horizon. Exact claims.', '<div class="panel claim"><p class="lead">GoalOS is architecturally state-of-the-art for Ascension as a proof-governed operating doctrine and implementation program.</p>'+laws+'<p>It does not claim achieved AGI, achieved ASI, achieved superintelligence, empirical benchmark SOTA certification, guaranteed ROI, token appreciation, live Mainnet settlement, production certification, external audit completion, energy abundance, or Kardashev Type II achievement.</p></div>')


def proof_card_page(out, card):
    n=card['id']; title=card['title']; sub=card['subtitle']; thesis=card['thesis']; reserved=card.get('reserved')
    if reserved:
        body = page_hero('Proof Card 023 — Reserved','This stable page preserves the Proof Card sequence for continuity and future publication.', visual=flow_svg(['Reserved','Continuity','Future Proof','Atlas'],'Reserved proof-card continuity'))
        body += section('Reserved Status','Intentional, not broken.', '<p class="lead">Proof Card 023 is reserved so the public sequence remains stable. It is not a missing page.</p><div class="cta"><a class="btn primary" href="proof-cards.html">Return to Proof Card Atlas</a><a class="btn" href="ascension.html">Explore Ascension</a></div>')
        body += claim_boundary_section()
        write(out/card['slug'], base('Proof Card 023 — Reserved', body))
        return
    motif = card.get('motif','orbit')
    visual = orbit_svg(title[:16] or 'Proof',[ 'Mission','Evidence','Verifier','Risk','Chronicle','$AGIALPHA']) if motif in ['orbit','constellation'] else flow_svg(['Mission','Work','Proof','Review','Chronicle','Reuse'], f'Proof Card {n:03d} flow')
    rows=[['Mission', 'Bound the objective and authority.', 'Mission Contract', 'Claim boundary', 'Generate docket'], ['Evidence Docket','Collect claims, sources, risks, and replay path.', 'Evidence Docket', 'Verifier gate', 'Review'], ['Chronicle','Record what worked and what failed.', 'Chronicle Entry', 'Replay gate', 'Reuse capability']]
    if 'Treasury' in card['group'] or '$AGIALPHA' in title or 'Settlement' in title or 'Alpha' in title:
        rows.append(['$AGIALPHA rail','Make accepted proof economically consequential.', 'α-Work Units', 'No proof, no settlement', 'Settlement readiness'])
    body = page_hero(f'Proof Card {n:03d}', f'{title} — {sub}', eyebrow=card['group'], visual=visual)
    body += section('Thesis', title, f'<p class="lead">{esc(thesis)}</p><p>{esc("The page turns the doctrine into an operational object: what must be evidenced, which gates apply, and how the result can influence future work only after proof.")}</p>')
    body += section('What this proves','A proof card is a structured proof object, not a slogan.', '<div class="grid3"><div class="card"><h3>Nontechnical meaning</h3><p>This card explains what a user or institution can trust after the proof path is complete.</p></div><div class="card"><h3>Operational meaning</h3><p>It maps GoalOS objects, verifier gates, risk boundaries, and reusable capability paths.</p></div><div class="card"><h3>Economic meaning</h3><p>Where relevant, accepted proof can inform α‑Work Units, settlement readiness, reputation, and treasury allocation.</p></div></div>')
    body += section('Proof Flow','Contained, responsive, replay-aware.', visual + table(rows))
    body += section('GoalOS Object Model','Objects that turn output into proof-backed capability.', '<div class="grid4">' + ''.join(f'<div class="card"><h3>{x}</h3><p>{d}</p></div>' for x,d in [('Mission','Bounded objective.'),('Evidence Docket','Claims and proof.'),('Verifier Report','Gate result.'),('Risk Ledger','Risks and rollback.'),('Chronicle','Durable memory.'),('Capability Package','Reusable option.'),('Claim Boundary','What is not claimed.'),('$AGIALPHA','Utility rail if accepted proof needs settlement.')]) + '</div>')
    body += section('$AGIALPHA Role','Utility only, after proof.', '<p>$AGIALPHA is useful only when accepted proof must coordinate escrow, bonds, validator incentives, α‑Work Units, reputation, slashing, treasury reinvestment, or capacity allocation. It is not equity, yield, dividend, ownership, guaranteed return, or a token-price claim.</p>')
    body += section('Next Proof Step','Move from doctrine to evidence.', '<div class="cta"><a class="btn primary" href="mission-os.html">Open Mission OS</a><a class="btn" href="paper.html">Read Paper</a><a class="btn" href="proof-treasury.html">Proof Treasury</a><a class="btn" href="proof-cards.html">Atlas</a></div>')
    body += claim_boundary_section()
    write(out/card['slug'], base(f'Proof Card {n:03d} — {title}', body))


def proof_cards_page(out):
    groups=[]
    order=['Everyday Proof','Mission OS','AI-First Startup','Governance','Multi-Agent','Verified Experience','RSI','Ascension','Proof Treasury','$AGIALPHA','Ascension Sequence','Reserved']
    for g in order:
        cards=[c for c in PROOF_CARDS if c['group']==g or (g=='Ascension' and c['group']=='Ascension')]
        if cards: groups.append((g,cards))
    content=''
    for g,cards in groups:
        tiles=''.join(f'<a class="card proof-tile" href="{c["slug"]}"><span class="num">{c["id"]:03d}</span><h3>{esc(c["title"])}</h3><p>{esc(c["subtitle"])} {"Reserved for continuity." if c.get("reserved") else ""}</p><span class="tag">{esc(c["group"])}</span></a>' for c in cards)
        content += f'<section class="section"><div class="wrap"><span class="tag">{esc(g)}</span><div class="proof-atlas">{tiles}</div></div></section>'
    body = page_hero('Proof Card Atlas','30 stable proof cards published; Proof Card 023 reserved. Every card has its own complete, unique, illustrated webpage.', visual=flow_svg(['Objective','Mission OS','Evidence','Review','$AGIALPHA','Chronicle','Harder Mission'],'Proof Card Atlas'))
    body += content
    write(out/'proof-cards.html', base('Proof Card Atlas', body))


def simple_page(out, filename, title, subtitle, body_extra=''):
    body=page_hero(title, subtitle, visual=flow_svg(['Goal','Plan','Proof','Review','Chronicle'], title))
    body += section('Operating View', subtitle, body_extra or '<p class="lead">This page is part of the v81 GoalOS AGIALPHA Ascension public system.</p>')
    body += claim_boundary_section()
    write(out/filename, base(title, body))


def treasury_page(out):
    body=page_hero('Proof Treasury','Simulation-only economics for proof-conditioned capacity allocation.', visual=flow_svg(['Proof','Replay','External Replay','Stress','Delayed Outcome','Reserve'],'Proof Treasury ladder'))
    body += section('Ladder','The economic law of Ascension.', '<div class="grid3">' + ''.join(f'<div class="card"><h3>Simulation {i:03d}</h3><p class="law">{law}</p><a class="btn" href="proof-treasury-simulation-{i:03d}.html">Open page</a></div>' for i,law in [(3,'No external replay, no capacity scale.'),(4,'No stress clearance, no institutional scale.'),(5,'No delayed-outcome clearance, no Ascension reserve compounding.')]) + '</div>')
    body += claim_boundary_section()
    write(out/'proof-treasury.html', base('Proof Treasury', body))
    laws={3:'No external replay, no capacity scale.',4:'No stress clearance, no institutional scale.',5:'No delayed-outcome clearance, no Ascension reserve compounding.'}
    for i,law in laws.items():
        extra='<p class="lead">Simulation only. No wallet, no private key, no token movement, no Mainnet broadcast, no ROI claim.</p>'+table([['Law',law,'ThermostatSignals','Simulation gate','Keep bounded'],['Artifacts','Ledger, docket, allocation report','CSV/JSON/MD','QA gate','Review'],['Contract surface','Protocol-level template only','Call trace','No live execution','Verify before testnet']], headers=('Element','Meaning','Artifact','Gate','Next action'))
        simple_page(out, f'proof-treasury-simulation-{i:03d}.html', f'Proof Treasury Simulation {i:03d}', law, extra)


def main(out_dir):
    out=Path(out_dir)
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    qa=copy_assets(out)
    cover=create_paper_cover(out)
    homepage(out,cover,qa)
    proof_cards_page(out)
    for c in PROOF_CARDS: proof_card_page(out,c)
    treasury_page(out)
    simple_page(out,'mission-os.html','Mission OS','Set the objective. GoalOS runs until proof is done.','<p class="lead">Mission OS turns objectives into action graphs, Evidence Dockets, verifier reports, risk ledgers, executive briefs, decision states, Chronicle entries, and reusable capability packages.</p>'+flow_svg(['Objective','Mission Contract','Agents','Evidence Docket','Decision State','Chronicle'],'Mission OS'))
    simple_page(out,'ascension.html','Ascension','SOTA is a measurement. Ascension is the mission.',orbit_svg('Ascension',['Verified Capability','Reuse','Settlement','Chronicle','RSI','Harder Mission']))
    simple_page(out,'paper.html','GoalOS Mission OS Paper','The Proof OS for Autonomous AI Work.',f'<div class="grid2">{figure_asset(cover,"Mission OS Paper front-page visual.","Mission OS Paper cover")}<div class="panel"><p class="lead">GoalOS Mission OS — The Proof OS for Autonomous AI Work.</p><p>Set the objective. GoalOS runs until proof is done. AI creates output. GoalOS creates proof.</p><a class="btn primary" href="{PAPER_OUT}">Read / Download Paper</a></div></div>')
    simple_page(out,'agialpha-continuity.html','From AGI Alpha to GoalOS','Agent labor market continuity becomes proof-governed Mission OS.',flow_svg(['Agent Job Market','Mission OS','Evidence Docket','Proof Treasury','Ascension'],'Continuity'))
    simple_page(out,'proof-run-001.html','Proof Run 001','Next evidence threshold for the first public Evidence Docket.', '<p class="lead">Proof Run 001 is intentionally positioned as an evidence-roadmap page, not the website centerpiece.</p>'+table([['Objective','real mission','Mission Contract','Claim boundary','Run'],['Evidence','claims, sources, risks','Evidence Docket','Verifier gate','Review'],['Result','decision state','Chronicle','Replay gate','Publish if passes']], headers=('Stage','Meaning','Object','Gate','Next')))
    for fn,title,sub in [('executive.html','Executive Command','Corporate summary for institutions, founders, and partners.'),('observatory.html','Observatory','Evidence status, simulations, and next thresholds.'),('resources.html','Resources','Papers, Proof Cards, simulations, and claim-boundary materials.'),('autopilot.html','Autopilot','Autonomy is earned through proof, replay, rollback, and review.'),('mission-builder.html','Mission Builder','Build a proof-ready mission packet.'),('start-here.html','Start Here','Start with one useful mission.'),('evidence-docket.html','Evidence Docket','The public-safe proof room for claims, baselines, costs, risks, and replay.')]:
        simple_page(out,fn,title,sub)
    # utility files
    (out/'.nojekyll').write_text('', encoding='utf-8')
    pages=[p.name for p in out.glob('*.html')]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>https://montrealai.github.io/goalos-agialpha-ascension/{p}</loc></url>' for p in pages) + '</urlset>'
    write(out/'sitemap.xml', sitemap)
    write(out/'robots.txt','User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/goalos-agialpha-ascension/sitemap.xml\n')
    write(out/'manifest.webmanifest', json.dumps({'name':'GoalOS AGIALPHA Ascension','short_name':'GoalOS','start_url':'index.html','display':'standalone','background_color':'#06111f','theme_color':'#f3d98b'}, indent=2))
    status={'release':RELEASE,'generated_at':datetime.datetime.utcnow().isoformat()+'Z','pages':len(pages),'proof_cards_total':31,'stable_proof_cards':30,'proof_card_023':'reserved','proof_treasury_pages':['003','004','005'],'claim_boundary':'enforced','primary_nav':[x[0] for x in PRIMARY_NAV],'main_asset':ASSET_MAIN,'asset_qa':qa,'paper_cover':cover}
    write(out/'site-status.json', json.dumps(status, indent=2))
    qa_dir=out/'qa'; qa_dir.mkdir(exist_ok=True)
    write(qa_dir/'verification-v81.json', json.dumps({'build':'complete','status':status}, indent=2))
    write(qa_dir/'layout-targets-v81.json', json.dumps({'viewports':['320x800','375x812','768x1024','1024x768','1440x1000'],'pages':['index.html','proof-cards.html','proof-card-001.html','proof-card-023.html','proof-card-024.html','proof-card-028.html','proof-card-031.html','mission-os.html','ascension.html','proof-treasury.html','paper.html']}, indent=2))
    print(json.dumps(status, indent=2))

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out', default='site')
    args=ap.parse_args(); main(args.out)
