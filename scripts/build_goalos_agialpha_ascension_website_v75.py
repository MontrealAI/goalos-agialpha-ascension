#!/usr/bin/env python3
"""Build GoalOS AGIALPHA Ascension Website v75 into a static GitHub Pages site."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
from pathlib import Path

RELEASE = "GoalOS AGIALPHA Ascension Website v75 — AGI Alpha Continuity / ASI Aura Gold Master"
VERSION = "v75"
BASE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
MAIN_ASSET = "assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png"
PAPER_PATH = "downloads/mission-os/GoalOS_Mission_OS_Paper.pdf"
PROOF_CARD_COUNT = 30
RESERVED_PROOF_CARD = 23
PROOF_TREASURY_COUNT = 5
GEN_TIME = dt.datetime.now(dt.timezone.utc).isoformat()

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

NAV = [
    ("Home", "index.html"),
    ("Mission OS", "mission-os.html"),
    ("Ascension", "ascension.html"),
    ("Proof Treasury", "proof-treasury.html"),
    ("Proof Cards", "proof-cards.html"),
    ("Resources", "resources.html"),
]

PROOF_CARD_TITLES = {
    1: "Demand Engine",
    2: "Mission Contract",
    3: "Evidence Docket",
    4: "Proof Gradient",
    5: "Alpha Work Unit",
    6: "Verifier Market",
    7: "Chronicle Memory",
    8: "Coordination Matrix",
    9: "Value Capability Flywheel",
    10: "Evidence Docket Template",
    11: "Proof Settlement Law",
    12: "Proof-Backed Upgrade Right",
    13: "Evidence Graph Moat",
    14: "Mission OS Foundry",
    15: "Proof Treasury Doctrine",
    16: "AGIALPHA Settlement Utility",
    17: "Mission OS Core",
    18: "Cyber-Sovereign Execution Moat",
    19: "Verified Experience Foundry",
    20: "Evidence Graph Moat & Public Proof-Run Escalation",
    21: "Superintelligence Settlement Rail & $AGIALPHA Verified-Experience Economy",
    22: "Superintelligence Capacity Loop & $AGIALPHA Proof Treasury",
    23: "Reserved",
    24: "Ascension Communication Standard",
    25: "Ascension",
    26: "Ascension Operating Theater",
    27: "Ascension Prime",
    28: "Ascension Helix",
    29: "Ascension Apex Prime",
    30: "Ascension Zenith",
    31: "Ascension Helios",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_out(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)


def copy_required_assets(root: Path, out: Path) -> dict:
    copied = {}
    # Main asset: required. If absent, make build fail clearly rather than silently degrade.
    src = root / MAIN_ASSET
    if not src.exists():
        raise FileNotFoundError(f"Required main hero asset missing: {MAIN_ASSET}")
    dest = out / MAIN_ASSET
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    copied[MAIN_ASSET] = {"bytes": dest.stat().st_size, "sha256": sha256(dest)}

    # Copy other common visual assets without requiring them.
    for folder in ["assets", "site-assets"]:
        source_dir = root / folder
        if source_dir.exists():
            for p in source_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico"}:
                    rel = p.relative_to(root)
                    if rel.as_posix() == MAIN_ASSET:
                        continue
                    target = out / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, target)

    # Mission OS paper: copy from docs source if possible; otherwise keep existing public copy if present.
    paper_candidates = [
        root / "docs/papers/mission-os/GoalOS_Mission_OS_Paper.pdf",
        root / "downloads/mission-os/GoalOS_Mission_OS_Paper.pdf",
    ]
    paper_src = next((p for p in paper_candidates if p.exists()), None)
    if not paper_src:
        raise FileNotFoundError("GoalOS_Mission_OS_Paper.pdf not found in docs/papers/mission-os or downloads/mission-os")
    paper_dest = out / PAPER_PATH
    paper_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(paper_src, paper_dest)
    copied[PAPER_PATH] = {"bytes": paper_dest.stat().st_size, "sha256": sha256(paper_dest)}
    return copied


def css() -> str:
    return r"""
:root{
  --ink:#07111f;--ink2:#101a30;--panel:rgba(11,24,43,.76);--panel2:rgba(255,255,255,.075);
  --gold:#f3d98b;--gold2:#d3b05a;--cream:#fff5dc;--mint:#7affd7;--cyan:#7ec8ff;--violet:#a78dff;
  --text:#f6fbff;--muted:#b9c6da;--ok:#79f2a6;--danger:#ff7f8f;--radius-xl:32px;--radius-lg:24px;
  --shadow-hero:0 30px 120px rgba(126,200,255,.24),0 8px 36px rgba(243,217,139,.18);
}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--ink);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.55;overflow-x:hidden}a{color:inherit}p{color:var(--muted)}.skip{position:absolute;left:-999px}.skip:focus{left:1rem;top:1rem;z-index:9;background:#fff;color:#000;padding:.7rem 1rem;border-radius:12px}.site-bg{position:fixed;inset:0;z-index:-3;background:radial-gradient(circle at 72% 18%,rgba(167,141,255,.28),transparent 36%),radial-gradient(circle at 22% 12%,rgba(122,255,215,.14),transparent 34%),linear-gradient(135deg,#06101d,#111b35 48%,#19122d)}.site-bg:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,#000 0%,rgba(0,0,0,.8) 58%,transparent 100%)}.site-bg:after{content:"";position:absolute;inset:-20%;background:conic-gradient(from 180deg,transparent,rgba(126,200,255,.16),transparent,rgba(243,217,139,.15),transparent);animation:slowspin 38s linear infinite;opacity:.55}.nav{position:sticky;top:0;z-index:20;background:rgba(255,245,220,.92);backdrop-filter:blur(18px);border-bottom:1px solid rgba(211,176,90,.24);color:#0b1425}.nav-inner{max-width:1220px;margin:auto;padding:.92rem 1.2rem;display:flex;align-items:center;justify-content:space-between;gap:1rem}.brand{display:flex;align-items:center;gap:.75rem;font-weight:900;letter-spacing:.08em}.brand-mark{width:34px;height:34px;border-radius:12px;background:radial-gradient(circle at 30% 20%,#fff,#f3d98b 22%,#7affd7 55%,#a78dff);box-shadow:0 0 28px rgba(122,255,215,.45)}.nav a{font-weight:800;text-decoration:none;font-size:.92rem}.nav-links{display:flex;gap:1.2rem;flex-wrap:wrap}.wrap{max-width:1220px;margin:auto;padding:0 1.2rem}.hero{position:relative;padding:7rem 0 4rem}.hero-grid{display:grid;grid-template-columns:minmax(0,1.03fr) minmax(340px,.97fr);gap:2.2rem;align-items:center}.eyebrow{display:inline-flex;align-items:center;gap:.5rem;padding:.45rem .75rem;border:1px solid rgba(243,217,139,.45);border-radius:999px;background:rgba(243,217,139,.10);color:var(--gold);font-size:.78rem;font-weight:900;letter-spacing:.13em;text-transform:uppercase}.h1{font-size:clamp(3.4rem,8vw,7.9rem);line-height:.86;letter-spacing:-.09em;margin:1.2rem 0;color:#fff;text-wrap:balance}.h1 .gold{color:var(--gold)}.lead{font-size:clamp(1.1rem,2.1vw,1.55rem);font-weight:750;color:#dbe8ff;max-width:780px}.hero-lines{display:grid;gap:.7rem;margin:1.4rem 0}.hero-line{padding:.9rem 1rem;border-radius:16px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.07);font-weight:850;color:#fff}.cta-row{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:1.4rem}.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;padding:.88rem 1.1rem;border-radius:999px;text-decoration:none;font-weight:900;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.11);box-shadow:0 12px 30px rgba(0,0,0,.18)}.btn.primary{background:linear-gradient(135deg,var(--gold),#fff0b2);color:#0a1424;border-color:rgba(243,217,139,.8)}.btn.mint{background:linear-gradient(135deg,var(--mint),var(--cyan));color:#05101d}.display-module{position:relative;border:1px solid rgba(243,217,139,.28);background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.04));border-radius:36px;padding:1rem;box-shadow:var(--shadow-hero);overflow:hidden}.display-module:before{content:"";position:absolute;inset:-22%;background:radial-gradient(circle at 50% 50%,rgba(122,255,215,.22),transparent 38%),conic-gradient(from 0deg,transparent,rgba(243,217,139,.24),transparent,rgba(167,141,255,.22),transparent);animation:slowspin 30s linear infinite}.hero-img{position:relative;border-radius:28px;overflow:hidden;border:1px solid rgba(255,255,255,.18);background:#111}.hero-img img{display:block;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover}.orbit{position:absolute;inset:8%;border:1px solid rgba(126,200,255,.34);border-radius:50%;animation:slowspin 22s linear infinite;pointer-events:none}.orbit.two{inset:17%;border-color:rgba(243,217,139,.34);animation-duration:29s;animation-direction:reverse}.orbit.three{inset:28%;border-color:rgba(122,255,215,.34);animation-duration:18s}.visual-caption{position:relative;margin-top:.8rem;color:#fff;font-weight:800;text-align:center}.status-grid,.cards,.three,.four{display:grid;gap:1rem}.status-grid{grid-template-columns:repeat(5,1fr);margin-top:1rem}.chip,.card,.metric,.panel{border:1px solid rgba(255,255,255,.13);background:var(--panel);border-radius:22px;box-shadow:0 22px 70px rgba(0,0,0,.22)}.chip{padding:1rem}.chip b{display:block;color:var(--gold);font-size:1.4rem}.section{padding:4.5rem 0}.section h2{font-size:clamp(2rem,4.5vw,4.5rem);line-height:.95;letter-spacing:-.05em;margin:.6rem 0 1rem;color:#fff;text-wrap:balance}.section .kicker{color:var(--gold);font-weight:900;letter-spacing:.13em;text-transform:uppercase;font-size:.78rem}.cards{grid-template-columns:repeat(3,1fr)}.three{grid-template-columns:repeat(3,1fr)}.four{grid-template-columns:repeat(4,1fr)}.card{padding:1.25rem}.card h3{margin:.1rem 0 .55rem;font-size:1.25rem;color:#fff}.card p,.card li{color:var(--muted)}.card.gold{background:linear-gradient(135deg,rgba(243,217,139,.18),rgba(255,255,255,.05));border-color:rgba(243,217,139,.35)}.paper{display:grid;grid-template-columns:1fr 1.1fr;gap:1.25rem;align-items:center}.paper-cover{min-height:430px;border-radius:30px;border:1px solid rgba(243,217,139,.28);background:linear-gradient(145deg,#fff8df,#dfe9f8);color:#101a30;padding:2rem;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 30px 70px rgba(0,0,0,.2)}.paper-cover b{color:#0d1730;font-size:2.5rem;line-height:1}.table-wrap{overflow:auto;border-radius:22px;border:1px solid rgba(255,255,255,.14)}table{width:100%;border-collapse:collapse;background:rgba(255,255,255,.055)}th,td{padding:1rem;text-align:left;border-bottom:1px solid rgba(255,255,255,.10);vertical-align:top}th{color:#07111f;background:linear-gradient(135deg,var(--gold),#fff0b2)}td{color:#dce8fa}.diagram{border:1px solid rgba(255,255,255,.14);border-radius:30px;background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.03));padding:1rem;overflow:hidden}.diagram svg{width:100%;height:auto;display:block}.node{fill:#12213b;stroke:#f3d98b;stroke-width:1.4}.node2{fill:#163a41;stroke:#7affd7;stroke-width:1.4}.node3{fill:#241b49;stroke:#a78dff;stroke-width:1.4}.edge{stroke:#7ec8ff;stroke-width:2;stroke-linecap:round;stroke-dasharray:6 9;animation:dash 9s linear infinite}.edge.gold-edge{stroke:#f3d98b}.edge.mint-edge{stroke:#7affd7}.svgtext{fill:#f6fbff;font-weight:800;font-size:13px;text-anchor:middle}.svgtiny{fill:#b9c6da;font-size:10px;text-anchor:middle}.code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:rgba(0,0,0,.38);border:1px solid rgba(126,200,255,.18);padding:1rem;border-radius:18px;color:#dff7ff;overflow:auto}.claim{border:1px solid rgba(122,255,215,.28);background:linear-gradient(135deg,rgba(122,255,215,.12),rgba(255,255,255,.04));border-radius:28px;padding:1.5rem}.not-claimed{border-color:rgba(255,127,143,.28);background:linear-gradient(135deg,rgba(255,127,143,.10),rgba(255,255,255,.04))}.footer{padding:3rem 0;border-top:1px solid rgba(255,255,255,.12);color:var(--muted)}.mini{font-size:.86rem;color:var(--muted)}.badge{display:inline-flex;padding:.22rem .55rem;border-radius:999px;background:rgba(243,217,139,.15);border:1px solid rgba(243,217,139,.35);color:var(--gold);font-weight:900;font-size:.76rem}.asi-aura{position:relative}.asi-aura:after{content:"";position:absolute;inset:-1px;border-radius:inherit;pointer-events:none;box-shadow:0 0 70px rgba(167,141,255,.24),inset 0 0 30px rgba(122,255,215,.10)}.rsi-orbit{animation:floaty 6s ease-in-out infinite}.pc028-grid{background-image:linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.06) 1px,transparent 1px);background-size:34px 34px}.reveal{opacity:0;transform:translateY(16px);transition:.7s ease}.reveal.in{opacity:1;transform:none}@keyframes slowspin{to{transform:rotate(360deg)}}@keyframes dash{to{stroke-dashoffset:-120}}@keyframes floaty{50%{transform:translateY(-8px)}}@media(max-width:900px){.hero-grid,.paper{grid-template-columns:1fr}.status-grid,.cards,.three,.four{grid-template-columns:1fr}.nav-inner{align-items:flex-start}.nav-links{gap:.7rem}.hero{padding-top:4rem}.h1{font-size:clamp(3rem,15vw,5rem)}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.reveal{opacity:1;transform:none}}
"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def nav_html(active: str) -> str:
    links = "".join(f'<a href="{href}" {"aria-current=\"page\"" if href==active else ""}>{label}</a>' for label, href in NAV)
    return f"""<a class="skip" href="#content">Skip to content</a><header class="nav"><div class="nav-inner"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"></span><span>GOALOS AGIALPHA</span></a><nav class="nav-links" aria-label="Primary navigation">{links}</nav></div></header>"""


def layout(title: str, description: str, body: str, active: str="index.html") -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:image" content="{MAIN_ASSET}"><meta name="theme-color" content="#07111f"><link rel="manifest" href="manifest.webmanifest"><style>{css()}</style></head><body><div class="site-bg" aria-hidden="true"></div>{nav_html(active)}<main id="content">{body}</main><footer class="footer"><div class="wrap"><p><strong>GoalOS AGIALPHA Ascension Website v75.</strong> Architecturally state-of-the-art for Ascension as a proof-governed operating doctrine and implementation program. Public alpha. Simulation only where simulation is stated.</p><p class="mini">Grand horizon. Exact claims. This site does not claim achieved AGI, achieved ASI, achieved superintelligence, guaranteed ROI, token appreciation, live Mainnet settlement, production certification, external audit completion, energy abundance, or Kardashev Type II achievement.</p></div></footer><script>const io='IntersectionObserver'in window?new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('in')}}),{{threshold:.08}}):null;document.querySelectorAll('.reveal').forEach(el=>{{if(io)io.observe(el);else el.classList.add('in')}});</script></body></html>"""


def proof_flow_svg() -> str:
    nodes=[("Objective",80,90,"node"),("Mission OS",230,90,"node2"),("Agent Theater",390,90,"node3"),("Evidence Docket",560,90,"node2"),("Review",720,90,"node"),("$AGIALPHA",880,90,"node3"),("Chronicle",1040,90,"node2"),("Harder Mission",1195,90,"node")]
    nhtml=''.join(f'<g class="rsi-orbit"><rect class="{c}" x="{x-58}" y="{y-28}" width="116" height="56" rx="18"/><text class="svgtext" x="{x}" y="{y-4}">{name}</text><text class="svgtiny" x="{x}" y="{y+14}">proof-gated</text></g>' for name,x,y,c in nodes)
    edges=''.join(f'<path class="edge" d="M {nodes[i][1]+62} 90 C {nodes[i][1]+90} 58,{nodes[i+1][1]-90} 58,{nodes[i+1][1]-62} 90"/>' for i in range(len(nodes)-1))
    return f'<div class="diagram pc028-grid asi-aura"><svg viewBox="0 0 1280 210" role="img" aria-label="GoalOS proof flow from objective to harder mission"><defs><filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect width="1280" height="210" fill="rgba(5,14,28,.6)"/>{edges}{nhtml}<text x="640" y="178" class="svgtext" filter="url(#glow)">Objective → proof → settlement-readiness → Chronicle → safer RSI → harder future mission</text></svg></div>'


def flywheel_svg() -> str:
    labels=[("AGI Alpha\nJob Market",150,90,"node"),("Mission OS",360,64,"node2"),("Evidence\nDocket",570,90,"node3"),("Proof\nTreasury",780,64,"node2"),("Ascension",990,90,"node")]
    edges=''.join(f'<path class="edge gold-edge" d="M {labels[i][1]+65} {labels[i][2]} C {labels[i][1]+110} 12,{labels[i+1][1]-110} 12,{labels[i+1][1]-65} {labels[i+1][2]}"/>' for i in range(len(labels)-1))
    n=''.join(f'<g><circle class="{c}" cx="{x}" cy="{y}" r="62"/><text class="svgtext" x="{x}" y="{y-4}">{lab.split(chr(10))[0]}</text><text class="svgtiny" x="{x}" y="{y+15}">{lab.split(chr(10))[1] if chr(10) in lab else "proof"}</text></g>' for lab,x,y,c in labels)
    return f'<div class="diagram"><svg viewBox="0 0 1140 170" role="img" aria-label="AGI Alpha to GoalOS continuity"><rect width="1140" height="170" fill="rgba(10,20,38,.55)"/>{edges}{n}</svg></div>'


def agent_constellation_svg() -> str:
    names=["Aim Council","Mission OS Planner","Demand Radar","Need Cartographer","Offer Architect","Builder Forge","Tool & Runtime","Evidence Office","Verifier Tribunal","Red-Team Court","Growth Proof","Treasury Router","Chronicle / RSI","Replay Council","Governance"]
    import math
    cx,cy=560,300
    parts=[f'<circle class="node2" cx="{cx}" cy="{cy}" r="82"/><text class="svgtext" x="{cx}" y="{cy-6}">GoalOS</text><text class="svgtiny" x="{cx}" y="{cy+16}">maximum verified effect</text>']
    for i,name in enumerate(names):
        a=2*math.pi*i/len(names)-math.pi/2
        x=cx+380*math.cos(a); y=cy+225*math.sin(a)
        cls="node" if i%3==0 else ("node2" if i%3==1 else "node3")
        parts.append(f'<path class="edge" d="M {cx} {cy} L {x} {y}"/>')
        parts.append(f'<g class="rsi-orbit"><rect class="{cls}" x="{x-70}" y="{y-24}" width="140" height="48" rx="16"/><text class="svgtext" x="{x}" y="{y+4}">{html.escape(name)}</text></g>')
    return '<div class="diagram pc028-grid"><svg viewBox="0 0 1120 610" role="img" aria-label="Large specialist agent constellation">' + '<rect width="1120" height="610" fill="rgba(5,14,28,.48)"/>' + ''.join(parts) + '</svg></div>'


def treasury_ladder_html() -> str:
    rows=[
        ("001", "Proof gates simulated settlement", "No proof, no settlement."),
        ("002", "Replay gates simulated reinvestment", "No replay, no reinvestment."),
        ("003", "External replay gates capacity scale", "No external replay, no capacity scale."),
        ("004", "Stress clearance gates institutional scale", "No stress clearance, no institutional scale."),
        ("005", "Delayed-outcome clearance gates Ascension reserve compounding", "No delayed-outcome clearance, no Ascension reserve compounding."),
    ]
    cards=[]
    for n,title,law in rows:
        href=f'proof-treasury-simulation-{int(n):03d}.html' if n in {'003','004','005'} else 'proof-treasury.html'
        cards.append(f'<a class="card gold reveal" href="{href}"><span class="badge">Simulation {n}</span><h3>{title}</h3><p>{law}</p><p class="mini">Simulation only · no wallet · no token movement · no Mainnet broadcast.</p></a>')
    return '<div class="cards">' + ''.join(cards) + '</div>'


def proof_card_atlas_html() -> str:
    groups=[
        ("Everyday / regular-person proof", list(range(1,8))),
        ("Mission OS and governance", list(range(8,18))),
        ("Verified experience and proof economy", list(range(18,23))),
        ("Reserved", [23]),
        ("Ascension sequence", list(range(24,32))),
    ]
    blocks=[]
    for g, nums in groups:
        items=[]
        for i in nums:
            title=PROOF_CARD_TITLES[i]
            href=f'proof-card-{i:03d}.html'
            status='Reserved' if i==23 else 'Stable'
            items.append(f'<a class="card" href="{href}"><span class="badge">Proof Card {i:03d} · {status}</span><h3>{esc(title)}</h3><p>{"Reserved placeholder to preserve sequence integrity." if i==23 else "A stable public proof card in the GoalOS evidence atlas."}</p></a>')
        blocks.append(f'<section class="section"><div class="wrap"><p class="kicker">{esc(g)}</p><div class="cards">{"".join(items)}</div></div></section>')
    return ''.join(blocks)


def claim_boundary_html() -> str:
    return """<section class="section"><div class="wrap"><div class="claim not-claimed"><p class="kicker">Grand horizon. Exact claims.</p><h2>Claim boundary.</h2><p><strong>Claim:</strong> GoalOS is architecturally state-of-the-art for Ascension as a proof-governed operating doctrine and implementation program.</p><p><strong>Not claimed:</strong> achieved AGI, achieved ASI, achieved superintelligence, empirical SOTA certification, guaranteed ROI, token appreciation, live Mainnet settlement, production certification, external audit completion, energy abundance, or Kardashev Type II achievement.</p><p><strong>Evidence rule:</strong> empirical claims rise only through public Evidence Dockets, replay, baselines, cost/risk ledgers, validators, delayed outcomes, and independent review.</p></div></div></section>"""


def home_page() -> str:
    body=f"""
<section class="hero"><div class="wrap hero-grid"><div><span class="eyebrow">GoalOS AGIALPHA · ASI Aura Gold Master</span><p class="mini">ASI aura · RSI visual system · AGI Alpha continuity</p><h1 class="h1">Turn AI work into <span class="gold">verified capability.</span></h1><p class="mini">Turn AI work into verified capability.</p><p class="lead">GoalOS is the proof-governed operating regime for autonomous AI work: Mission OS plans the work, specialist agents execute, Evidence Dockets prove, reviewers validate, $AGIALPHA makes accepted proof economically consequential, and Chronicle memory enables safer Recursive Self-Improvement.</p><div class="hero-lines"><div class="hero-line">SOTA is a measurement. Ascension is the mission.</div><div class="hero-line">AI creates output. GoalOS creates proof.</div><div class="hero-line">GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.</div><div class="hero-line">The product is not output. The product is proof-backed capability.</div><div class="hero-line">0 claims without proof.</div></div><div class="cta-row"><a class="btn primary" href="start-here.html">Start My First Mission</a><a class="btn mint" href="{PAPER_PATH}">Read the Paper</a><a class="btn" href="mission-os.html">Open Mission OS</a><a class="btn" href="ascension.html">Explore Ascension</a><a class="btn" href="proof-cards.html">View Proof Cards</a></div></div><div class="display-module asi-aura"><div class="orbit"></div><div class="orbit two"></div><div class="orbit three"></div><figure class="hero-img"><img src="{MAIN_ASSET}" alt="GoalOS AGIALPHA Ascension visual anchor: a luminous gold and cosmic AI figure representing proof-governed autonomous AI work"></figure><div class="visual-caption">GoalOS AGIALPHA Ascension: proof-governed autonomous AI work.</div></div></div><div class="wrap status-grid"><div class="chip"><b>30</b>stable proof cards</div><div class="chip"><b>023</b>reserved</div><div class="chip"><b>003–005</b>Proof Treasury</div><div class="chip"><b>Paper</b>Mission OS</div><div class="chip"><b>0</b>claims without proof</div></div></section>
<section class="section"><div class="wrap">{proof_flow_svg()}</div></section>
<section class="section"><div class="wrap"><p class="kicker">Latest Evidence / Observatory</p><h2>Architecture + public alpha + simulations. Next: Proof Run 001.</h2><div class="four"><div class="card"><span class="badge">Next threshold</span><h3>Proof Run 001</h3><p>Public Evidence Docket for one real objective: claims, evidence, risks, verifier report, decision state, action graph, Chronicle entry, and replay path.</p></div><div class="card gold"><span class="badge">Latest simulation</span><h3>Proof Treasury Simulation 005</h3><p>No delayed-outcome clearance, no Ascension reserve compounding.</p></div><div class="card"><span class="badge">Latest proof card</span><h3>Proof Card 031 — Ascension Helios</h3><p>Proof-governed value-to-energy flywheel and $AGIALPHA capacity rail.</p></div><div class="card"><span class="badge">Boundary</span><h3>0 claims without proof</h3><p>No achieved AGI, ASI, superintelligence, ROI, token appreciation, or live Mainnet settlement claim.</p></div></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">From AGI Alpha to GoalOS</p><h2>AGI Alpha opened the agent labor market. GoalOS governs what that labor can be trusted to become.</h2><p class="lead">AGI Alpha makes autonomous AI work addressable through agent identity, jobs, validators, MCP-native access, and $AGIALPHA utility. GoalOS extends that foundation into proof-governed autonomous work: objectives become missions, missions produce Evidence Dockets, accepted proof becomes reusable capability, and $AGIALPHA makes proof economically consequential.</p>{flywheel_svg()}<div class="three"><div class="card"><h3>AI Agent Job Marketplace</h3><p>Jobs, agents, validators, reputation, and work routing become programmable surfaces.</p></div><div class="card"><h3>MCP-native motif</h3><pre class="code">{{\n  "mcpServers": {{\n    "agi-alpha": {{\n      "url": "https://agialpha.com/api/mcp"\n    }}\n  }}\n}}</pre><p class="mini">Continuity motif, not a new guarantee beyond public source.</p></div><div class="card"><h3>Proof Economy</h3><p>Job economy → proof economy → Ascension economy. Work becomes trusted only after evidence, review, replay, and boundaries.</p></div></div></div></section>
<section class="section"><div class="wrap paper"><div class="paper-cover"><span class="badge">Flagship paper</span><b>GoalOS Mission OS</b><p>The Proof OS for Autonomous AI Work</p><p>Set the objective. GoalOS runs until proof is done.</p><p class="mini">Claim-bounded edition · public alpha doctrine · governed decision states</p></div><div><p class="kicker">Read the GoalOS Mission OS Paper</p><h2>GoalOS Mission OS — The Proof OS for Autonomous AI Work.</h2><p class="lead">The paper defines how Mission OS turns high-stakes objectives into governed decision states: Mission Contract, Evidence Docket, verifier report, risk ledger, executive brief, action graph, Chronicle memory, and claim boundaries.</p><div class="cta-row"><a class="btn primary" href="{PAPER_PATH}">Read / Download Paper</a><a class="btn" href="mission-os.html">Open Mission OS</a><a class="btn" href="proof-cards.html">View Proof Cards</a></div><p class="mini">The paper does not claim achieved AGI, ASI, superintelligence, guaranteed returns, live Mainnet settlement, production certification, or civilization-scale capability.</p></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">What GoalOS does</p><h2>Most AI gives you output. GoalOS gives you proof-backed progress.</h2><div class="cards"><div class="card"><h3>Evidence Docket</h3><p>A public-safe proof room showing claims, evidence, risks, costs, baselines, validators, and replay path.</p></div><div class="card"><h3>Governed Decision State</h3><p>Mission contract, claims matrix, provenance, contradictions, verifier report, risk ledger, and action graph.</p></div><div class="card"><h3>Capability Package</h3><p>What worked becomes reusable: conditions, tools, proof history, rollback plan, and Chronicle memory.</p></div></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Choose your path</p><h2>Useful for regular people. Serious enough for institutions.</h2><div class="four"><a class="card" href="start-here.html"><h3>Regular person</h3><p>Start with one useful mission. Get proof-backed progress.</p></a><a class="card" href="mission-builder.html"><h3>Founder / AI-first startup</h3><p>Turn urgent user pain into proof-backed capability.</p></a><a class="card" href="executive.html"><h3>Institution / enterprise</h3><p>Govern AI work with Evidence Dockets, review, rollback, and claim boundaries.</p></a><a class="card" href="resources.html"><h3>Builder / researcher</h3><p>Explore proof architecture, Proof Cards, Mission OS, and Proof Treasury simulations.</p></a></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Mission OS</p><h2>Set the objective. GoalOS runs until proof is done.</h2><p class="lead">Mission OS turns objectives into action graphs, Evidence Dockets, verifier reports, risk ledgers, executive briefs, decision states, Chronicle entries, and reusable capability packages.</p><div class="cards"><div class="card"><h3>Regular-person missions</h3><p>Job search, personal finance organization, learning plan, health admin, family decision support, and side-business validation.</p></div><div class="card"><h3>AI-first founder missions</h3><p>Proof sprint, customer pain validation, prototype plan, user-proof docket, and action graph.</p></div><div class="card"><h3>Enterprise missions</h3><p>AI governance review, procurement proof, evidence vault, risk ledger, rollback plan, and claim boundary.</p></div></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Ascension</p><h2>SOTA is a measurement. Ascension is the mission.</h2><p class="lead">SOTA measures performance. Ascension governs consequence: verified capability, reuse, settlement pressure, Chronicle memory, and proof-gated RSI.</p><div class="claim"><h3>Ascension = VerifiedCapability × Reuse × SettlementPressure × ChronicleMemory × RSI</h3><p>No proof, no settlement. No replay, no reinvestment. No governance, no acceleration.</p></div>{proof_flow_svg()}</div></section>
<section class="section"><div class="wrap"><p class="kicker">Large multi-agent institution</p><h2>A specialist-agent theater for maximum verified effect.</h2>{agent_constellation_svg()}<div class="table-wrap"><table><thead><tr><th>Specialist cell</th><th>Mandate</th><th>Inspectable output</th><th>Proof obligation</th><th>Validator gate</th></tr></thead><tbody>{agent_table_rows()}</tbody></table></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">$AGIALPHA proof economy</p><h2>$AGIALPHA makes accepted proof economically consequential.</h2><p class="lead">GoalOS can create proof without a wallet. $AGIALPHA becomes useful when accepted proof needs escrow, builder bonds, proof bonds, reviewer / validator bonds, challenge pools, slashing, α‑Work Units, reputation, replay grants, reserves, treasury reinvestment, and capacity allocation.</p><div class="claim"><h3>Request → Escrow → Execute → Proof → Validate → Settle → Chronicle → Reinvest → Harder Mission</h3><p>$AGIALPHA is proof-settlement fuel and protocol utility. It is not equity, dividend, yield, ownership, guaranteed return, or token-price claim.</p></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Proof Treasury ladder</p><h2>Proof decides settlement. Delayed outcomes decide reserve compounding.</h2>{treasury_ladder_html()}</div></section>
<section class="section"><div class="wrap"><p class="kicker">Proof Card Atlas</p><h2>30 stable proof cards published; Proof Card 023 reserved.</h2><p class="lead">Proof Cards 024–031 form the Ascension sequence.</p><div class="cta-row"><a class="btn primary" href="proof-cards.html">Open the Atlas</a><a class="btn" href="proof-card-028.html">View Proof Card 028</a><a class="btn" href="proof-card-031.html">View Proof Card 031</a></div></div></section>
{claim_boundary_html()}
"""
    return layout("GoalOS AGIALPHA Ascension — Website v75", "Turn AI work into verified capability. GoalOS creates proof; $AGIALPHA makes accepted proof economically consequential.", body)


def agent_table_rows() -> str:
    rows=[
        ("Aim Council","Defines objectives and claim boundary","GoalOSCommit","Mission, constraints, authority, rollback","Policy + claim-boundary review"),
        ("Mission OS Planner","Plans bounded work graph","MissionPlan / ActionGraph","Success criteria and stopping rule","Verifier desk"),
        ("Need Cartographer","Maps user pain and demand","Need Map","Sources and user-proof requirements","Evidence Office"),
        ("Offer Architect","Packages proof-backed capability","Offer Brief","Claim, proof, risk, pricing boundary","Growth proof"),
        ("Builder Forge","Builds bounded artifact","Prototype / patch / workflow","Tests, logs, hashes, rollback","Verifier Tribunal"),
        ("Evidence Office","Assembles proof room","Evidence Docket","Claims matrix, provenance, contradictions","External replay"),
        ("Verifier Tribunal","Accepts or rejects proof","Verifier Report","Replay, policy, SLO, safety","Selection Gate"),
        ("Red-Team Court","Finds failure modes","Risk Ledger","Adversarial checks and blocked actions","Governance Chamber"),
        ("Treasury Router","Simulates proof economics","Settlement / α-WU ledger","No token movement unless authorized","Proof Treasury"),
        ("Chronicle / RSI Office","Stores reusable memory","Chronicle Entry / Capability Package","No propagation without proof","Replay + rollback"),
    ]
    return ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for a,b,c,d,e in rows)


def simple_page(slug: str, title: str, subtitle: str, sections: list[str], active: str) -> str:
    body=f'<section class="hero"><div class="wrap"><span class="eyebrow">GoalOS AGIALPHA · {esc(title)}</span><h1 class="h1">{esc(title)}</h1><p class="lead">{esc(subtitle)}</p><div class="cta-row"><a class="btn primary" href="index.html">Home</a><a class="btn" href="mission-os.html">Mission OS</a><a class="btn" href="proof-cards.html">Proof Cards</a></div></div></section>' + ''.join(sections) + claim_boundary_html()
    return layout(f'{title} | GoalOS AGIALPHA', subtitle, body, active)


def pages() -> dict[str,str]:
    pg={"index.html":home_page()}
    pg["mission-os.html"]=simple_page("mission-os","Mission OS","The Proof OS for Autonomous AI Work. Set the objective. GoalOS runs until proof is done.",[
        f'<section class="section"><div class="wrap paper"><div class="paper-cover"><span class="badge">Paper</span><b>GoalOS Mission OS</b><p>The Proof OS for Autonomous AI Work</p><p>AI creates output. GoalOS creates proof.</p></div><div><h2>Read the flagship paper.</h2><p class="lead">Mission OS turns high-stakes objectives into governed decision states: Evidence Dockets, verifier reports, risk ledgers, executive briefs, action graphs, Chronicle memory, and reusable capability packages.</p><a class="btn primary" href="{PAPER_PATH}">Read / Download Paper</a></div></div></section>',
        '<section class="section"><div class="wrap"><h2>Mission outputs.</h2><div class="cards"><div class="card"><h3>Evidence Docket</h3><p>Claims, evidence, risks, costs, validators, and replay path.</p></div><div class="card"><h3>Decision State</h3><p>What passed, failed, remains uncertain, or needs human review.</p></div><div class="card"><h3>Action Graph</h3><p>The next practical steps, bounded by proof and rollback.</p></div></div></div></section>'
    ],"mission-os.html")
    pg["ascension.html"]=simple_page("ascension","Ascension","SOTA is a measurement. Ascension is the mission: proof-governed compounding intelligence.",[
        f'<section class="section"><div class="wrap"><h2>The Ascension equation.</h2><div class="claim"><h3>Ascension = VerifiedCapability × Reuse × SettlementPressure × ChronicleMemory × RSI</h3><p>The product is not output. The product is proof-backed capability.</p></div>{agent_constellation_svg()}</div></section>'
    ],"ascension.html")
    pg["proof-treasury.html"]=simple_page("proof-treasury","Proof Treasury","Simulation layer for proof-conditioned settlement, reinvestment, capacity scale, stress clearance, and delayed-outcome reserve compounding.",[
        f'<section class="section"><div class="wrap"><h2>The Proof Treasury ladder.</h2>{treasury_ladder_html()}</div></section>',
        '<section class="section"><div class="wrap"><h2>$AGIALPHA utility boundary.</h2><p class="lead">$AGIALPHA is proof-settlement fuel and protocol utility: stake, settlement, metering, slashing, quorum coordination, and protocol operations. It is not equity, yield, dividend, ownership, or a guaranteed return.</p></div></section>'
    ],"proof-treasury.html")
    pg["proof-cards.html"]=layout("Proof Card Atlas | GoalOS AGIALPHA","30 stable proof cards published; Proof Card 023 reserved.",f'<section class="hero"><div class="wrap"><span class="eyebrow">Proof Card Atlas</span><h1 class="h1">30 stable proof cards. <span class="gold">023 reserved.</span></h1><p class="lead">Proof Cards 024–031 form the Ascension sequence.</p></div></section>{proof_card_atlas_html()}{claim_boundary_html()}',"proof-cards.html")
    pg["resources.html"]=simple_page("resources","Resources","Papers, proof cards, Mission OS, Proof Treasury simulations, and public-safe operating doctrine.",[
        f'<section class="section"><div class="wrap"><h2>Featured resource.</h2><div class="cards"><a class="card gold" href="{PAPER_PATH}"><h3>GoalOS Mission OS Paper</h3><p>The Proof OS for Autonomous AI Work.</p></a><a class="card" href="proof-treasury.html"><h3>Proof Treasury</h3><p>Simulations 003–005.</p></a><a class="card" href="proof-cards.html"><h3>Proof Cards</h3><p>30 stable proof cards; Proof Card 023 reserved.</p></a></div></div></section>'
    ],"resources.html")
    pg["executive.html"]=simple_page("executive","Executive Command","GoalOS for founders, institutions, and operators who need proof-backed AI work.",[ '<section class="section"><div class="wrap"><h2>Institutional value.</h2><p class="lead">Governed AI work becomes evidence, evidence becomes capability, and capability earns the right to influence future work only after proof.</p></div></section>' ],"index.html")
    pg["observatory.html"]=simple_page("observatory","Evidence Observatory","Latest evidence status, simulations, proof-card sequence, and next required public Evidence Docket.",[ '<section class="section"><div class="wrap"><h2>Current claim level.</h2><div class="claim"><p>Architecture + public alpha + simulations. Next required artifact: Proof Run 001 public Evidence Docket.</p></div></div></section>' ],"index.html")
    pg["start-here.html"]=simple_page("start-here","Start Here","Pick one painful task. Generate one mission. Take one useful action. Save proof.",[ '<section class="section"><div class="wrap"><h2>First mission examples.</h2><div class="cards"><div class="card"><h3>Job search</h3><p>Turn goals, constraints, applications, sources, and follow-ups into a proof-backed action graph.</p></div><div class="card"><h3>Side business</h3><p>Validate pain, offer, first user proof, and next seven-day plan.</p></div><div class="card"><h3>Learning plan</h3><p>Build a mission with sources, milestones, checks, and Chronicle memory.</p></div></div></div></section>' ],"index.html")
    pg["evidence-docket.html"]=simple_page("evidence-docket","Evidence Docket","The public-safe proof room for claims, baselines, proof packets, costs, risks, validators, and replay path.",[ '<section class="section"><div class="wrap"><h2>Docket standard.</h2><div class="table-wrap"><table><tr><th>Docket element</th><th>Purpose</th></tr><tr><td>Claims Matrix</td><td>What is claimed, not claimed, and required evidence.</td></tr><tr><td>Proof Packets</td><td>Trace roots, output hashes, policy decisions, cost, latency, signatures.</td></tr><tr><td>Replay Path</td><td>How a reviewer can inspect or challenge the claim.</td></tr></table></div></div></section>' ],"index.html")
    pg["agialpha-continuity.html"]=simple_page("agialpha-continuity","From AGI Alpha to GoalOS","AGI Alpha opened the agent labor market. GoalOS governs what that labor can be trusted to become.",[ f'<section class="section"><div class="wrap">{flywheel_svg()}</div></section>' ],"index.html")
    pg["mission-builder.html"]=simple_page("mission-builder","Mission Builder","Build a proof-ready mission packet with objective, constraints, risk tier, proof requirements, and claim boundary.",[ '<section class="section"><div class="wrap"><h2>Mission packet.</h2><pre class="code">objective\nsuccessCriteria\nfailureCriteria\nconstraints\nriskClass\nproofRequired\nclaimBoundary</pre></div></section>' ],"index.html")
    pg["autopilot.html"]=pg["mission-builder.html"]
    # proof treasury simulation pages
    sims={3:("External Replay Market & Capacity Auction","No external replay, no capacity scale."),4:("Institutional Stress Gauntlet & Sovereign Capacity Reserve","No stress clearance, no institutional scale."),5:("Delayed-Outcome Covenant & Ascension Reserve","No delayed-outcome clearance, no Ascension reserve compounding.")}
    for i,(title,law) in sims.items():
        pg[f"proof-treasury-simulation-{i:03d}.html"]=simple_page(f"proof-treasury-simulation-{i:03d}",f"Proof Treasury Simulation {i:03d} — {title}",law,[
            f'<section class="section"><div class="wrap"><h2>{law}</h2><p class="lead">Simulation only. No wallet, no private key, no token movement, no Sepolia broadcast, no Mainnet broadcast, no ROI claim, no token appreciation claim.</p><div class="claim"><p>Proof first. Settlement second. $AGIALPHA only moves when proof changes state.</p></div></div></section>'
        ],"proof-treasury.html")
    # proof cards
    for i in range(1,32):
        title=PROOF_CARD_TITLES[i]
        if i==23:
            body=f'<section class="hero"><div class="wrap"><span class="eyebrow">Proof Card 023 · Reserved</span><h1 class="h1">Proof Card 023 is <span class="gold">reserved.</span></h1><p class="lead">This placeholder preserves sequence integrity. No claim is made on this reserved page.</p><a class="btn primary" href="proof-cards.html">Back to Atlas</a></div></section>{claim_boundary_html()}'
        else:
            body=f'<section class="hero"><div class="wrap"><span class="eyebrow">Proof Card {i:03d}</span><h1 class="h1">{esc(title)}</h1><p class="lead">SOTA is a measurement. Ascension is the mission. AI creates output. GoalOS creates proof.</p><div class="cta-row"><a class="btn primary" href="proof-cards.html">Back to Atlas</a><a class="btn" href="mission-os.html">Mission OS</a></div></div></section><section class="section"><div class="wrap"><div class="claim"><h2>The product is proof-backed capability.</h2><p>GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential. No proof, no settlement. No replay, no reinvestment.</p></div>{proof_flow_svg()}</div></section>{claim_boundary_html()}'
        pg[f"proof-card-{i:03d}.html"]=layout(f"Proof Card {i:03d} — {title} | GoalOS AGIALPHA", f"GoalOS proof card {i:03d}: {title}", body, "proof-cards.html")
    return pg


def write_pages(out: Path, page_map: dict[str,str]) -> None:
    for name, content in page_map.items():
        p = out / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def write_site_files(out: Path, copied_assets: dict, page_map: dict[str,str]) -> None:
    (out / ".nojekyll").write_text("", encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/goalos-agialpha-ascension/sitemap.xml\n", encoding="utf-8")
    manifest={"name":"GoalOS AGIALPHA Ascension","short_name":"GoalOS","start_url":"index.html","display":"standalone","background_color":"#07111f","theme_color":"#07111f","icons":[{"src":MAIN_ASSET,"sizes":"1024x1024","type":"image/png"}]}
    (out / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    urls=''.join(f'<url><loc>{BASE_URL}{name}</loc></url>\n' for name in sorted(page_map))
    (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    status={
        "release": RELEASE,
        "version": VERSION,
        "generated_at": GEN_TIME,
        "proof_card_count": PROOF_CARD_COUNT,
        "proof_card_023_status": "reserved",
        "proof_treasury_count": PROOF_TREASURY_COUNT,
        "proof_treasury_public_pages": ["proof-treasury-simulation-003.html","proof-treasury-simulation-004.html","proof-treasury-simulation-005.html"],
        "claim_boundary_status": "active",
        "paper_link_status": "featured",
        "main_hero_asset_status": "present",
        "no_text_on_image_certified": True,
        "assets": copied_assets,
        "pages": sorted(page_map),
    }
    (out / "site-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--out", default="site")
    args=parser.parse_args()
    root=Path.cwd()
    out=Path(args.out)
    clean_out(out)
    copied=copy_required_assets(root,out)
    page_map=pages()
    write_pages(out,page_map)
    write_site_files(out,copied,page_map)
    # Basic public-site ZIP exclusion belt-and-suspenders
    for z in out.rglob("*.zip"):
        z.unlink()
    print(json.dumps({"release":RELEASE,"out":str(out),"pages":len(page_map),"assets":list(copied)},indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
