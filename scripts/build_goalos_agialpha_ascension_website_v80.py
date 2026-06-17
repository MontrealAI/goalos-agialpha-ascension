#!/usr/bin/env python3
"""Build GoalOS AGIALPHA Ascension Website v80 into a static GitHub Pages site."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

RELEASE = "GoalOS AGIALPHA Ascension Website v80 — Complete Platinum Ascension / Proof Card Atlas Gold Master"
VERSION = "v80"
BASE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
MAIN_ASSET = "assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png"
PAPER_SRC = "docs/papers/mission-os/GoalOS_Mission_OS_Paper.pdf"
PAPER_PATH = "downloads/mission-os/GoalOS_Mission_OS_Paper.pdf"
PAPER_COVER = "assets/generated/mission-os-paper-cover.png"
PROOF_CARD_COUNT = 30
RESERVED_PROOF_CARD = 23
PROOF_TREASURY_COUNT = 5
GEN_TIME = dt.datetime.now(dt.timezone.utc).isoformat()

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

NAV = [
    ("Home", "index.html"),
    ("Mission OS", "mission-os.html"),
    ("Ascension", "ascension.html"),
    ("Proof Treasury", "proof-treasury.html"),
    ("Proof Run 001", "proof-run-001.html"),
    ("Paper", "paper.html"),
    ("Proof Cards", "proof-cards.html"),
    ("Resources", "resources.html"),
]

PROOF_CARD_TITLES = {
    1: ("Demand Engine", "Turn one painful need into a proof-ready mission."),
    2: ("Mission Contract", "Objectives become constraints, success criteria, risk, budget, and authority."),
    3: ("Evidence Docket", "A public-safe proof room for claims, evidence, risks, and replay."),
    4: ("Proof Gradient", "Select upgrades by evidence, transfer, risk, cost, and rollback readiness."),
    5: ("Alpha Work Unit", "Accepted verified machine labor becomes measurable."),
    6: ("Verifier Market", "Review capacity becomes a first-class economic resource."),
    7: ("Chronicle Memory", "What worked becomes durable institutional memory."),
    8: ("Coordination Matrix", "Specialist agents coordinate for maximum verified effect."),
    9: ("Value Capability Flywheel", "Verified work becomes reusable capability and future capacity."),
    10: ("Evidence Docket Template", "Make proof inspectable, reusable, and publication-safe."),
    11: ("Proof Settlement Law", "No ProofBundle, no settlement."),
    12: ("Proof-Backed Upgrade Right", "Only proven artifacts may influence future work."),
    13: ("Evidence Graph Moat", "A living evidence graph cannot be fabricated retroactively."),
    14: ("Mission OS Foundry", "GoalOS turns objectives into governed decision states."),
    15: ("Proof Treasury Doctrine", "Proof controls budget, validators, and future capacity."),
    16: ("AGIALPHA Settlement Utility", "$AGIALPHA makes accepted proof economically consequential."),
    17: ("Mission OS Core", "Set the objective. GoalOS runs until proof is done."),
    18: ("Cyber-Sovereign Execution Moat", "Defensive capability requires proof, boundaries, and human review."),
    19: ("Verified Experience Foundry", "GoalOS converts autonomous work into verified experience."),
    20: ("Evidence Graph Moat & Public Proof-Run Escalation", "Public proof runs make the evidence graph defensible."),
    21: ("Superintelligence Settlement Rail", "Superintelligence needs proof before economic authority."),
    22: ("Superintelligence Capacity Loop", "$AGIALPHA can become a proof treasury and capacity rail."),
    23: ("Reserved", "Reserved to preserve sequence integrity."),
    24: ("Ascension Communication Standard", "State the mission with precision: Ascension, not benchmark chasing."),
    25: ("Ascension", "SOTA is a measurement. Ascension is the mission."),
    26: ("Ascension Operating Theater", "A specialist-agent institution for AI-first capability formation."),
    27: ("Ascension Prime", "AI-first startup sovereignty through proof-backed capability."),
    28: ("Ascension Helix", "Proof strand and capacity strand compound verified intelligence."),
    29: ("Ascension Apex Prime", "Sovereign verified-experience engine and capability foundry."),
    30: ("Ascension Zenith", "Civilization-scale capability horizon under proof boundaries."),
    31: ("Ascension Helios", "Proof-governed value-to-energy flywheel and capacity rail."),
}

ASSET_CAPTIONS = {
    "assets/AGI_ALPHA_v12.png": "AGI Alpha continuity visual: coordinated autonomous sovereignty and validation icons.",
    "assets/AGI_ALPHA_v13.png": "AGI Alpha continuity visual: energy, incentives, swarms, validation, and growth.",
    "assets/AGI_ALPHA_v14.png": "AGI Alpha visual thesis: α‑AGI Ascension, far-from-equilibrium intelligence, and coordinated swarms.",
    "assets/AGI_ALPHA_v16.png": "AGI Alpha symbol: a luminous coordination system for autonomous work.",
    "assets/AGI_ALPHA_v18.png": "AGI Alpha institutional poster: data, work, governance, validation, iteration, and $AGIALPHA.",
    "assets/AGI_ALPHA_v20.png": "AGI Alpha panorama: coordinated, autonomous, sovereign Ascension system.",
    "assets/AGI_Ascension_Autonomous_Multi-Agent_Coordination_v10.png": "Ascension multi-agent system visual: insight, sovereign jobs, marketplace, validators, and economics.",
    "assets/AGI_Ascension_Autonomous_Multi-Agent_Coordination_v9.png": "Autonomous multi-agent coordination visual: one system, infinite impact, proof-bound coordination.",
}


def esc(x: object) -> str:
    return html.escape(str(x), quote=True)


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


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_assets(root: Path, out: Path) -> dict:
    report = {"copied": {}, "missing_optional": []}
    main_src = root / MAIN_ASSET
    if not main_src.exists():
        raise FileNotFoundError(f"Required main hero asset missing: {MAIN_ASSET}")
    copy_file(main_src, out / MAIN_ASSET)
    report["copied"][MAIN_ASSET] = {"bytes": (out / MAIN_ASSET).stat().st_size, "sha256": sha256(out / MAIN_ASSET)}

    for rel in REQUIRED_ASSETS:
        src = root / rel
        if src.exists():
            copy_file(src, out / rel)
            report["copied"][rel] = {"bytes": (out / rel).stat().st_size, "sha256": sha256(out / rel)}
        else:
            report["missing_optional"].append(rel)

    # Copy any other safe visual assets; intentionally skip ZIPs.
    for folder in ["assets", "site-assets"]:
        source_dir = root / folder
        if source_dir.exists():
            for p in source_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico"}:
                    rel = p.relative_to(root).as_posix()
                    dest = out / rel
                    if dest.exists():
                        continue
                    copy_file(p, dest)

    paper_candidates = [root / PAPER_SRC, root / PAPER_PATH]
    paper_src = next((p for p in paper_candidates if p.exists()), None)
    if not paper_src:
        raise FileNotFoundError(f"Mission OS paper not found at {PAPER_SRC} or {PAPER_PATH}")
    copy_file(paper_src, out / PAPER_PATH)
    report["copied"][PAPER_PATH] = {"bytes": (out / PAPER_PATH).stat().st_size, "sha256": sha256(out / PAPER_PATH)}
    return report


def render_paper_cover(root: Path, out: Path) -> dict:
    cover = out / PAPER_COVER
    cover.parent.mkdir(parents=True, exist_ok=True)
    pdf = out / PAPER_PATH
    status = {"path": PAPER_COVER, "method": "fallback"}
    # Try pdftoppm if present.
    try:
        subprocess.run(["pdftoppm", "-png", "-f", "1", "-singlefile", "-r", "144", str(pdf), str(cover.with_suffix(""))], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cover.exists():
            status["method"] = "pdftoppm"
            return status
    except Exception:
        pass
    # Fallback deterministic PNG cover.
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (900, 1200), (9, 17, 31))
        draw = ImageDraw.Draw(img)
        try:
            font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 68)
            font_mid = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
            font_small = ImageFont.truetype("DejaVuSans.ttf", 28)
        except Exception:
            font_big = font_mid = font_small = None
        for i in range(0, 900, 40):
            draw.line((i, 0, i, 1200), fill=(20, 36, 62))
        for j in range(0, 1200, 40):
            draw.line((0, j, 900, j), fill=(20, 36, 62))
        draw.rectangle((70, 70, 830, 1130), outline=(243, 217, 139), width=3)
        draw.text((110, 170), "GOALOS", fill=(243, 217, 139), font=font_mid)
        draw.text((110, 280), "The Proof OS", fill=(255, 255, 255), font=font_big)
        draw.text((110, 365), "for Autonomous", fill=(255, 255, 255), font=font_big)
        draw.text((110, 450), "AI Work", fill=(255, 255, 255), font=font_big)
        draw.text((110, 610), "Set the objective. GoalOS runs until proof is done.", fill=(185, 198, 218), font=font_small)
        draw.text((110, 665), "AI creates output. GoalOS creates proof.", fill=(122, 255, 215), font=font_small)
        draw.text((110, 980), "GoalOS Mission OS Paper", fill=(243, 217, 139), font=font_mid)
        img.save(cover)
        status["method"] = "PIL fallback"
        return status
    except Exception:
        # Last fallback SVG plus zero-byte impossible avoided by writing simple PNG header isn't safe. Use SVG and report.
        svg = cover.with_suffix(".svg")
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200"><rect width="900" height="1200" fill="#07111f"/><text x="80" y="160" fill="#f3d98b" font-size="50" font-family="sans-serif">GOALOS MISSION OS</text><text x="80" y="280" fill="#fff" font-size="70" font-family="sans-serif">The Proof OS</text><text x="80" y="370" fill="#fff" font-size="70" font-family="sans-serif">for Autonomous</text><text x="80" y="460" fill="#fff" font-size="70" font-family="sans-serif">AI Work</text></svg>', encoding="utf-8")
        status["path"] = svg.relative_to(out).as_posix()
        status["method"] = "svg fallback"
        return status


def stylesheet() -> str:
    return r'''
:root{--ink:#07111f;--ink2:#101a30;--panel:rgba(11,24,43,.76);--panel2:rgba(255,255,255,.075);--gold:#f3d98b;--gold2:#d3b05a;--cream:#fff5dc;--mint:#7affd7;--cyan:#7ec8ff;--violet:#a78dff;--text:#f6fbff;--muted:#b9c6da;--ok:#79f2a6;--danger:#ff7f8f;--radius-xl:32px;--radius-lg:24px;--shadow-hero:0 30px 120px rgba(126,200,255,.24),0 8px 36px rgba(243,217,139,.18)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--ink);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.55;overflow-x:hidden}a{color:inherit}p{color:var(--muted)}img{max-width:100%;height:auto}.skip{position:absolute;left:-999px}.skip:focus{left:1rem;top:1rem;z-index:99;background:#fff;color:#000;padding:.7rem 1rem;border-radius:12px}.site-bg{position:fixed;inset:0;z-index:-3;background:radial-gradient(circle at 75% 10%,rgba(167,141,255,.28),transparent 34%),radial-gradient(circle at 22% 12%,rgba(122,255,215,.14),transparent 34%),linear-gradient(135deg,#06101d,#111b35 48%,#19122d)}.site-bg:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,#000 0%,rgba(0,0,0,.8) 62%,transparent 100%)}.site-bg:after{content:"";position:absolute;inset:-20%;background:conic-gradient(from 180deg,transparent,rgba(126,200,255,.16),transparent,rgba(243,217,139,.15),transparent);animation:slowspin 38s linear infinite;opacity:.55}.nav{position:sticky;top:0;z-index:20;background:rgba(255,245,220,.93);backdrop-filter:blur(18px);border-bottom:1px solid rgba(211,176,90,.24);color:#0b1425}.nav-inner{max-width:1260px;margin:auto;padding:.92rem 1.2rem;display:flex;align-items:center;justify-content:space-between;gap:1rem}.brand{display:flex;align-items:center;gap:.75rem;font-weight:950;letter-spacing:.08em}.brand-mark{width:34px;height:34px;border-radius:12px;background:radial-gradient(circle at 30% 20%,#fff,#f3d98b 22%,#7affd7 55%,#a78dff);box-shadow:0 0 28px rgba(122,255,215,.45)}.nav a{font-weight:850;text-decoration:none;font-size:.9rem}.nav-links{display:flex;gap:1rem;flex-wrap:wrap}.wrap{max-width:1260px;margin:auto;padding:0 1.2rem}.hero{position:relative;padding:7rem 0 4rem}.hero-grid{display:grid;grid-template-columns:minmax(0,1.02fr) minmax(340px,.98fr);gap:2.2rem;align-items:center}.eyebrow,.badge{display:inline-flex;align-items:center;gap:.5rem;padding:.45rem .75rem;border:1px solid rgba(243,217,139,.45);border-radius:999px;background:rgba(243,217,139,.10);color:var(--gold);font-size:.76rem;font-weight:950;letter-spacing:.13em;text-transform:uppercase}.h1{font-size:clamp(3.4rem,8vw,7.8rem);line-height:.86;letter-spacing:-.085em;margin:1.2rem 0;color:#fff;text-wrap:balance}.h1 .gold{color:var(--gold)}h1,h2,h3{letter-spacing:-.045em}h2{font-size:clamp(2.2rem,4.4vw,4.7rem);line-height:.95;margin:.3rem 0 1rem}h3{font-size:clamp(1.25rem,2.1vw,1.8rem);line-height:1.05}.lead{font-size:clamp(1.1rem,2.1vw,1.5rem);font-weight:750;color:#dbe8ff;max-width:850px}.hero-lines{display:grid;gap:.7rem;margin:1.4rem 0}.hero-line{padding:.9rem 1rem;border-radius:16px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.07);font-weight:850;color:#fff}.cta-row{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:1.4rem}.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;padding:.88rem 1.1rem;border-radius:999px;text-decoration:none;font-weight:900;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.11);box-shadow:0 12px 30px rgba(0,0,0,.18)}.btn.primary{background:linear-gradient(135deg,var(--gold),#fff0b2);color:#0a1424;border-color:rgba(243,217,139,.8)}.btn.mint{background:linear-gradient(135deg,var(--mint),var(--cyan));color:#05101d}.display-module{position:relative;border:1px solid rgba(243,217,139,.28);background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.04));border-radius:36px;padding:1rem;box-shadow:var(--shadow-hero);overflow:hidden}.display-module:before{content:"";position:absolute;inset:-22%;background:radial-gradient(circle at 50% 50%,rgba(122,255,215,.22),transparent 38%),conic-gradient(from 0deg,transparent,rgba(243,217,139,.24),transparent,rgba(167,141,255,.22),transparent);animation:slowspin 30s linear infinite}.hero-img{position:relative;border-radius:28px;overflow:hidden;border:1px solid rgba(255,255,255,.18);background:#111}.hero-img img{display:block;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover}.orbit{position:absolute;inset:8%;border:1px solid rgba(126,200,255,.34);border-radius:50%;animation:slowspin 22s linear infinite;pointer-events:none}.orbit.two{inset:17%;border-color:rgba(243,217,139,.34);animation-duration:29s;animation-direction:reverse}.orbit.three{inset:28%;border-color:rgba(122,255,215,.34);animation-duration:18s}.visual-caption{position:relative;margin-top:.8rem;color:#fff;font-weight:850;text-align:center}.status-grid,.cards,.three,.four{display:grid;gap:1rem}.status-grid{grid-template-columns:repeat(5,1fr);margin-top:1rem}.chip,.card,.metric,.panel{border:1px solid rgba(255,255,255,.13);background:linear-gradient(135deg,rgba(255,255,255,.10),rgba(255,255,255,.045));border-radius:var(--radius-lg);padding:1rem;box-shadow:0 18px 70px rgba(0,0,0,.15)}.chip b{display:block;color:var(--gold);font-size:1.75rem}.section{padding:4.8rem 0}.kicker{color:var(--gold);font-weight:950;letter-spacing:.16em;text-transform:uppercase;font-size:.78rem}.cards{grid-template-columns:repeat(3,1fr)}.three{grid-template-columns:repeat(3,1fr)}.four{grid-template-columns:repeat(4,1fr)}.card{transition:transform .25s ease,border-color .25s ease;background-color:var(--panel)}.card:hover{transform:translateY(-4px);border-color:rgba(243,217,139,.45)}.card.gold{background:linear-gradient(135deg,rgba(243,217,139,.18),rgba(255,255,255,.055))}.card.mint{background:linear-gradient(135deg,rgba(122,255,215,.14),rgba(255,255,255,.055))}.diagram{border:1px solid rgba(243,217,139,.26);border-radius:var(--radius-xl);overflow:hidden;background:rgba(5,14,28,.62);box-shadow:var(--shadow-hero)}.diagram svg{width:100%;display:block}.svgtext{fill:#f6fbff;font-weight:900;font-size:22px;text-anchor:middle}.svgtiny{fill:#b9c6da;font-weight:800;font-size:14px;text-anchor:middle}.edge{stroke:#f3d98b;stroke-width:5;stroke-linecap:round;filter:drop-shadow(0 0 8px rgba(243,217,139,.4));stroke-dasharray:8 12;animation:dash 8s linear infinite}.node{fill:rgba(12,24,43,.94);stroke:#7ec8ff;stroke-width:2}.node2{fill:rgba(40,30,70,.94);stroke:#a78dff;stroke-width:2}.node3{fill:rgba(36,35,18,.94);stroke:#f3d98b;stroke-width:2}.paper{display:grid;grid-template-columns:320px 1fr;gap:1.6rem;align-items:center;border:1px solid rgba(243,217,139,.26);border-radius:var(--radius-xl);padding:1.2rem;background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.045));box-shadow:var(--shadow-hero)}.paper-cover{border-radius:24px;overflow:hidden;background:#fff;color:#06101d;min-height:420px;display:flex;align-items:center;justify-content:center;padding:.8rem}.paper-cover img{width:100%;border-radius:18px;box-shadow:0 22px 60px rgba(0,0,0,.22)}table{width:100%;border-collapse:collapse;overflow:hidden;border-radius:18px;background:rgba(255,255,255,.06)}th,td{padding:.9rem;border:1px solid rgba(255,255,255,.12);vertical-align:top}th{background:rgba(255,255,255,.11);color:var(--gold);text-align:left}.gallery{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}.figure{border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.06);border-radius:22px;overflow:hidden}.figure img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block}.figure figcaption{padding:.8rem;color:var(--muted);font-size:.9rem}.code{font-size:.82rem;white-space:pre-wrap;background:rgba(0,0,0,.35);padding:1rem;border-radius:16px;border:1px solid rgba(255,255,255,.12);color:#dff}.claim{border:1px solid rgba(122,255,215,.28);background:linear-gradient(135deg,rgba(122,255,215,.12),rgba(255,255,255,.05));border-radius:var(--radius-xl);padding:1.2rem}.not-claimed{border-color:rgba(255,127,143,.35);background:linear-gradient(135deg,rgba(255,127,143,.08),rgba(255,255,255,.05))}.mini{font-size:.88rem;color:#95a6c0}.footer{border-top:1px solid rgba(255,255,255,.12);padding:2.2rem 0;color:var(--muted);background:rgba(0,0,0,.20)}.pc-hero{padding:5rem 0 2rem}.pc-visual{min-height:280px;display:flex;align-items:center;justify-content:center}.rsi-orbit{animation:float 6s ease-in-out infinite}.reveal{opacity:0;transform:translateY(18px);transition:opacity .65s ease,transform .65s ease}.reveal.on{opacity:1;transform:none}@keyframes slowspin{to{transform:rotate(360deg)}}@keyframes dash{to{stroke-dashoffset:-160}}@keyframes float{50%{transform:translateY(-8px)}}@media(max-width:980px){.hero-grid,.paper{grid-template-columns:1fr}.status-grid,.four,.three,.cards,.gallery{grid-template-columns:1fr 1fr}.h1{font-size:clamp(3rem,14vw,5rem)}}@media(max-width:640px){.nav-inner{align-items:flex-start;flex-direction:column}.status-grid,.four,.three,.cards,.gallery{grid-template-columns:1fr}.section{padding:3.5rem 0}.hero{padding:4rem 0 3rem}.nav-links{gap:.7rem}.nav a{font-size:.82rem}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.reveal{opacity:1;transform:none}}
'''


def nav_html() -> str:
    links = ''.join(f'<a href="{href}">{esc(label)}</a>' for label, href in NAV)
    return f'<a class="skip" href="#main">Skip to content</a><div class="site-bg" aria-hidden="true"></div><nav class="nav" aria-label="Primary"><div class="nav-inner"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"></span><span>GOALOS AGIALPHA</span></a><div class="nav-links">{links}</div></div></nav>'


def footer_html() -> str:
    return '''<footer class="footer"><div class="wrap"><p><strong>GoalOS AGIALPHA Ascension</strong> · Public alpha · Static GitHub Pages site · Proof-first doctrine.</p><p>No token movement. No live Mainnet settlement unless explicitly proven. No achieved AGI, ASI, superintelligence, guaranteed ROI, token appreciation, production certification, external audit completion, energy abundance, or Kardashev Type II achievement claim.</p><p>A model can answer. An agent can act. An institution must prove. Do not put intelligence on-chain. Put proof of intelligence on-chain.</p></div></footer>'''


def html_page(title: str, body: str, description: str = "GoalOS AGIALPHA Ascension") -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:image" content="{MAIN_ASSET}"><link rel="manifest" href="manifest.webmanifest"><style>{stylesheet()}</style></head><body>{nav_html()}<main id="main">{body}</main>{footer_html()}<script>document.querySelectorAll('.reveal').forEach((e)=>{{if(!('IntersectionObserver'in window)){{e.classList.add('on');return}};new IntersectionObserver((entries,obs)=>{{entries.forEach(x=>{{if(x.isIntersecting){{x.target.classList.add('on');obs.unobserve(x.target)}}}})}}).observe(e)}})</script></body></html>'''


def flow_svg(title="Proof-flow operating route") -> str:
    nodes = ["Objective", "Mission OS", "Agent Theater", "Evidence Docket", "Review", "$AGIALPHA", "Chronicle", "Harder Mission"]
    xs = [90, 235, 390, 545, 690, 820, 950, 1070]
    parts = [f'<text class="svgtext" x="560" y="58">{esc(title)}</text>']
    for i, n in enumerate(nodes):
        y = 145 if i % 2 == 0 else 285
        if i < len(nodes)-1:
            y2 = 145 if (i+1) % 2 == 0 else 285
            parts.append(f'<path class="edge" d="M {xs[i]+55} {y} C {xs[i]+90} {y} {xs[i+1]-90} {y2} {xs[i+1]-55} {y2}"/>')
        cls = "node" if i%3==0 else ("node2" if i%3==1 else "node3")
        parts.append(f'<g class="rsi-orbit"><circle class="{cls}" cx="{xs[i]}" cy="{y}" r="56"/><text class="svgtext" x="{xs[i]}" y="{y-4}">{esc(n.split()[0])}</text><text class="svgtiny" x="{xs[i]}" y="{y+18}">{esc(" ".join(n.split()[1:]) or "proof")}</text></g>')
    parts.append('<text class="svgtiny" x="560" y="380">No proof → no settlement. No replay → no reinvestment. No delayed-outcome clearance → no Ascension reserve compounding.</text>')
    return '<div class="diagram"><svg viewBox="0 0 1160 430" role="img" aria-label="Proof flow from objective to harder mission"><rect width="1160" height="430" fill="rgba(5,14,28,.50)"/>' + ''.join(parts) + '</svg></div>'


def flywheel_svg() -> str:
    labels = ["Agent Market", "Mission OS", "Evidence Docket", "Proof Treasury", "Chronicle", "Ascension"]
    import math
    cx, cy, r = 560, 260, 215
    parts = ['<text class="svgtext" x="560" y="52">AGI Alpha Continuity → GoalOS Proof Economy → Ascension</text>']
    for i, lab in enumerate(labels):
        a = 2*math.pi*i/len(labels)-math.pi/2
        x, y = cx+r*math.cos(a), cy+r*math.sin(a)
        parts.append(f'<path class="edge" d="M {cx} {cy} L {x} {y}"/>')
        cls = "node" if i%2==0 else "node2"
        parts.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="62"/><text class="svgtext" x="{x}" y="{y+5}">{esc(lab.split()[0])}</text>')
    parts.append('<circle class="node3" cx="560" cy="260" r="86"/><text class="svgtext" x="560" y="252">$AGIALPHA</text><text class="svgtiny" x="560" y="278">proof utility</text>')
    return '<div class="diagram"><svg viewBox="0 0 1120 560" role="img" aria-label="Alpha Flywheel visual continuity"><rect width="1120" height="560" fill="rgba(5,14,28,.50)"/>' + ''.join(parts) + '</svg></div>'


def agent_constellation_svg() -> str:
    names = ["Aim Council","Mission Planner","Demand Radar","Need Cartographer","Offer Architect","Builder Forge","Tool Cell","Evidence Office","Verifier Tribunal","Red-Team Court","Growth Proof","Treasury Router","Chronicle RSI","Replay Council","Governance"]
    import math
    cx, cy = 560, 310
    parts = ['<text class="svgtext" x="560" y="52">Specialist-agent constellation for maximum verified effect</text><circle class="node3" cx="560" cy="310" r="94"/><text class="svgtext" x="560" y="305">GoalOS</text><text class="svgtiny" x="560" y="332">proof-governed</text>']
    for i, name in enumerate(names):
        a = 2*math.pi*i/len(names)-math.pi/2
        x, y = cx+390*math.cos(a), cy+220*math.sin(a)
        cls = "node" if i%3==0 else ("node2" if i%3==1 else "node3")
        parts.append(f'<path class="edge" d="M {cx} {cy} L {x} {y}"/>')
        parts.append(f'<rect class="{cls}" x="{x-72}" y="{y-25}" width="144" height="50" rx="16"/><text class="svgtiny" x="{x}" y="{y+4}">{esc(name)}</text>')
    return '<div class="diagram"><svg viewBox="0 0 1120 640" role="img" aria-label="Large specialist agent constellation"><rect width="1120" height="640" fill="rgba(5,14,28,.50)"/>' + ''.join(parts) + '</svg></div>'


def proof_card_visual(num: int, title: str) -> str:
    if num == 23:
        text = "Reserved"
    else:
        text = title.split()[0]
    import math
    parts = [f'<text class="svgtext" x="560" y="55">Proof Card {num:03d} · {esc(title)}</text>']
    cx, cy = 560, 260
    for i in range(9):
        a = 2*math.pi*i/9 + num*.13
        x, y = cx+310*math.cos(a), cy+140*math.sin(a)
        parts.append(f'<path class="edge" d="M {cx} {cy} L {x} {y}"/>')
        parts.append(f'<circle class="{"node" if i%3==0 else "node2" if i%3==1 else "node3"}" cx="{x}" cy="{y}" r="34"/>')
    parts.append(f'<circle class="node3" cx="{cx}" cy="{cy}" r="90"/><text class="svgtext" x="{cx}" y="{cy+5}">{esc(text)}</text>')
    return '<div class="diagram pc-visual"><svg viewBox="0 0 1120 430" role="img" aria-label="Unique proof card visual"><rect width="1120" height="430" fill="rgba(5,14,28,.50)"/>' + ''.join(parts) + '</svg></div>'


def claim_boundary_block() -> str:
    return '''<section class="section"><div class="wrap"><div class="claim not-claimed"><p class="kicker">Grand horizon. Exact claims.</p><h2>Claim boundary.</h2><p><strong>Claim:</strong> GoalOS is architecturally state-of-the-art for Ascension as a proof-governed operating doctrine and implementation program.</p><p><strong>Not claimed:</strong> achieved AGI, achieved ASI, achieved superintelligence, empirical SOTA certification, guaranteed ROI, token appreciation, live Mainnet settlement, production certification, external audit completion, energy abundance, or Kardashev Type II achievement.</p><p><strong>Evidence rule:</strong> empirical claims rise only through public Evidence Dockets, replay, baselines, cost/risk ledgers, validators, delayed outcomes, and independent review.</p></div></div></section>'''


def treasury_ladder_cards() -> str:
    rows = [
        ("001", "Proof gates settlement", "No proof, no settlement."),
        ("002", "Replay gates reinvestment", "No replay, no reinvestment."),
        ("003", "External replay gates capacity scale", "No external replay, no capacity scale."),
        ("004", "Stress clearance gates institutional scale", "No stress clearance, no institutional scale."),
        ("005", "Delayed-outcome clearance gates Ascension reserve compounding", "No delayed-outcome clearance, no Ascension reserve compounding."),
    ]
    cards = []
    for n, title, law in rows:
        href = f'proof-treasury-simulation-{int(n):03d}.html' if n in {"003","004","005"} else 'proof-treasury.html'
        cards.append(f'<a class="card gold reveal" href="{href}"><span class="badge">Simulation {n}</span><h3>{esc(title)}</h3><p>{esc(law)}</p><p class="mini">Simulation only · no wallet · no token movement · no Mainnet broadcast.</p></a>')
    return '<div class="cards">' + ''.join(cards) + '</div>'


def image_gallery() -> str:
    figs = []
    for rel in REQUIRED_ASSETS:
        cap = ASSET_CAPTIONS.get(rel, "GoalOS AGIALPHA visual asset.")
        figs.append(f'<figure class="figure reveal"><img src="{rel}" alt="{esc(cap)}"><figcaption>{esc(cap)}</figcaption></figure>')
    return '<div class="gallery">' + ''.join(figs) + '</div>'


def homepage(cover_path: str) -> str:
    body = f'''
<section class="hero"><div class="wrap hero-grid"><div><span class="eyebrow">GoalOS AGIALPHA · Complete Platinum Ascension</span><p class="mini">ASI aura · proof-gated RSI · AGI Alpha continuity · autonomous GitHub Actions release</p><h1 class="h1">Turn AI work into <span class="gold">verified capability.</span></h1><p class="lead">GoalOS is the proof-governed operating regime for autonomous AI work: Mission OS plans the work, specialist agents execute, Evidence Dockets prove, reviewers validate, $AGIALPHA makes accepted proof economically consequential, and Chronicle memory enables safer Recursive Self-Improvement.</p><div class="hero-lines"><div class="hero-line">SOTA is a measurement. Ascension is the mission.</div><div class="hero-line">AI creates output. GoalOS creates proof.</div><div class="hero-line">Turn AI work into verified capability.</div><div class="hero-line">The product is not output. The product is proof-backed capability.</div><div class="hero-line">No proof, no settlement. No replay, no reinvestment.</div><div class="hero-line">No governance, no acceleration.</div><div class="hero-line">0 claims without proof.</div></div><div class="cta-row"><a class="btn primary" href="start-here.html">Start My First Mission</a><a class="btn mint" href="paper.html">Read the Paper</a><a class="btn" href="mission-os.html">Open Mission OS</a><a class="btn" href="ascension.html">Explore Ascension</a><a class="btn" href="proof-cards.html">View Proof Cards</a></div></div><div class="display-module asi-aura"><div class="orbit"></div><div class="orbit two"></div><div class="orbit three"></div><figure class="hero-img"><img src="{MAIN_ASSET}" alt="GoalOS AGIALPHA Ascension visual anchor: proof-governed autonomous AI work"></figure><div class="visual-caption">GoalOS AGIALPHA Ascension: proof-governed autonomous AI work.</div></div></div><div class="wrap status-grid"><div class="chip"><b>30</b>stable proof cards</div><div class="chip"><b>023</b>reserved</div><div class="chip"><b>003–005</b>Proof Treasury</div><div class="chip"><b>Paper</b>Mission OS</div><div class="chip"><b>0</b>claims without proof</div></div></section>
<section class="section"><div class="wrap">{flow_svg()}</div></section>
<section class="section"><div class="wrap"><p class="kicker">Latest Evidence / Observatory</p><h2>Architecture + public alpha + simulations. Next: Proof Run 001.</h2><div class="four"><a class="card mint" href="proof-run-001.html"><span class="badge">Next threshold</span><h3>Proof Run 001</h3><p>Public Evidence Docket for one real objective: claims, evidence, risks, verifier report, decision state, action graph, Chronicle entry, and replay path.</p></a><a class="card gold" href="proof-treasury-simulation-005.html"><span class="badge">Latest simulation</span><h3>Proof Treasury Simulation 005</h3><p>No delayed-outcome clearance, no Ascension reserve compounding.</p></a><a class="card" href="proof-card-031.html"><span class="badge">Latest proof card</span><h3>Proof Card 031 — Ascension Helios</h3><p>Proof-governed value-to-energy flywheel and $AGIALPHA capacity rail.</p></a><div class="card"><span class="badge">Boundary</span><h3>0 claims without proof</h3><p>No achieved AGI, ASI, superintelligence, ROI, token appreciation, or live Mainnet settlement claim.</p></div></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">From AGI Alpha to GoalOS</p><h2>AGI Alpha opened the agent labor market. GoalOS governs what that labor can be trusted to become.</h2><p class="lead">AGI Alpha makes autonomous AI work addressable through agent identity, jobs, validators, MCP-native access, and $AGIALPHA utility. GoalOS extends that foundation into proof-governed autonomous work: objectives become missions, missions produce Evidence Dockets, accepted proof becomes reusable capability, and $AGIALPHA makes proof economically consequential.</p>{flywheel_svg()}<div class="three"><div class="card"><h3>AI Agent Job Marketplace</h3><p>Jobs, agents, validators, reputation, and work routing become programmable surfaces.</p></div><div class="card"><h3>MCP-native motif</h3><pre class="code">{{\n  "mcpServers": {{\n    "agi-alpha": {{\n      "url": "&lt;mcp-endpoint&gt;"\n    }}\n  }}\n}}</pre><p class="mini">Continuity motif only; no outbound public link or new API guarantee.</p></div><div class="card"><h3>17 tools / one endpoint motif</h3><p>Read tools, write tools, and utility tools become a continuity language for machine labor; GoalOS adds proof, review, Chronicle memory, and claim boundaries.</p></div></div><div class="cta-row"><a class="btn" href="agialpha-continuity.html">Open AGI Alpha continuity</a></div></div></section>
<section class="section"><div class="wrap paper"><div class="paper-cover"><img src="{cover_path}" alt="Front page preview of the GoalOS Mission OS Paper"></div><div><p class="kicker">Read the GoalOS Mission OS Paper</p><h2>GoalOS Mission OS — The Proof OS for Autonomous AI Work.</h2><p class="lead">The paper defines how Mission OS turns high-stakes objectives into governed decision states: Mission Contract, Evidence Docket, verifier report, risk ledger, executive brief, action graph, Chronicle memory, and claim boundaries.</p><div class="cta-row"><a class="btn primary" href="{PAPER_PATH}">Read / Download Paper</a><a class="btn" href="mission-os.html">Open Mission OS</a><a class="btn" href="proof-cards.html">View Proof Cards</a></div><p class="mini">The paper does not claim achieved AGI, ASI, superintelligence, guaranteed returns, live Mainnet settlement, production certification, or civilization-scale capability.</p></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Ascension AI Visual System</p><h2>Asset-driven proof, coordination, and RSI visuals.</h2><p class="lead">The site uses repository imagery as curated figures, not as text containers. All important claims remain live HTML.</p>{image_gallery()}</div></section>
<section class="section"><div class="wrap"><p class="kicker">What GoalOS does</p><h2>Most AI gives you output. GoalOS gives you proof-backed progress.</h2><div class="cards"><div class="card"><h3>Evidence Docket</h3><p>A public-safe proof room showing claims, evidence, risks, costs, baselines, validators, and replay path.</p></div><div class="card"><h3>Governed Decision State</h3><p>Mission contract, claims matrix, source provenance, contradiction register, verifier report, risk ledger, and action graph.</p></div><div class="card"><h3>Capability Package</h3><p>What worked becomes reusable: initiation conditions, tools, proof history, rollback plan, and Chronicle memory.</p></div></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Choose your path</p><h2>Useful to regular people. Serious for institutions.</h2><div class="four"><a class="card" href="start-here.html"><h3>Regular person</h3><p>Start with one useful mission. Get proof-backed progress.</p></a><a class="card" href="mission-builder.html"><h3>Founder / AI-first startup</h3><p>Turn urgent user pain into proof-backed capability.</p></a><a class="card" href="executive.html"><h3>Institution / enterprise</h3><p>Govern AI work with Evidence Dockets, review, rollback, and claim boundaries.</p></a><a class="card" href="proof-cards.html"><h3>Builder / researcher</h3><p>Explore the proof architecture, Proof Cards, Mission OS, and Proof Treasury simulations.</p></a></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Large multi-agent institution</p><h2>A specialist-agent constellation for maximum verified effect.</h2>{agent_constellation_svg()}<table><thead><tr><th>Specialist cell</th><th>Mandate</th><th>Inspectable output</th><th>Proof obligation</th><th>Validator gate</th></tr></thead><tbody>{''.join(f'<tr><td>{esc(name)}</td><td>Perform bounded specialist work.</td><td>Trace, artifact, or decision object.</td><td>Evidence Docket section and risk ledger.</td><td>Review, replay, or escalation.</td></tr>' for name in ['Aim Council','Mission OS Planner','Demand Radar','Need Cartographer','Offer Architect','Builder Forge','Tool & Runtime Cell','Evidence Office','Verifier Tribunal','Red-Team Court','Treasury Router','Chronicle / RSI Office','Governance Chamber'])}</tbody></table></div></section>
<section class="section"><div class="wrap"><p class="kicker">$AGIALPHA Proof Economy</p><h2>$AGIALPHA makes accepted proof economically consequential.</h2><p class="lead">GoalOS can create proof without a wallet. $AGIALPHA becomes useful when accepted proof needs mission escrow, builder bonds, proof bonds, reviewer / validator bonds, validator incentives, challenge pools, slashing, α‑Work Units, reputation updates, compute-credit allocation, external replay grants, rollback reserves, stress reserves, delayed-outcome reserves, treasury reinvestment, and capacity allocation.</p>{flow_svg('Request → Escrow → Execute → Proof → Validate → Settle → Chronicle → Reinvest')}<div class="claim"><p>$AGIALPHA is proof-settlement fuel and protocol utility. It is not equity, dividend, yield, ownership, guaranteed return, or token-price claim.</p></div></div></section>
<section class="section"><div class="wrap"><p class="kicker">Proof Treasury Ladder</p><h2>Proof decides settlement. Replay decides reinvestment. Delayed outcomes decide reserve compounding.</h2>{treasury_ladder_cards()}</div></section>
<section class="section"><div class="wrap"><p class="kicker">Proof Card Atlas</p><h2>30 stable proof cards published; Proof Card 023 reserved.</h2><p class="lead">Proof Cards 001–022 establish everyday proof, Mission OS, governance, verified experience, and proof economy foundations. Proof Cards 024–031 form the Ascension sequence.</p><div class="cta-row"><a class="btn primary" href="proof-cards.html">Open Proof Card Atlas</a><a class="btn" href="proof-card-028.html">Open Proof Card 028</a><a class="btn" href="proof-card-031.html">Open Proof Card 031</a></div></div></section>
{claim_boundary_block()}
'''
    return html_page("GoalOS AGIALPHA Ascension — Complete Platinum v80", body, "GoalOS turns AI work into verified capability.")


def generic_page(slug: str, title: str, subtitle: str, body_extra: str="") -> str:
    body = f'''
<section class="pc-hero"><div class="wrap"><span class="eyebrow">GoalOS AGIALPHA · {esc(VERSION)}</span><h1 class="h1">{esc(title)}</h1><p class="lead">{esc(subtitle)}</p><div class="cta-row"><a class="btn primary" href="index.html">Home</a><a class="btn" href="mission-os.html">Mission OS</a><a class="btn" href="proof-run-001.html">Proof Run 001</a><a class="btn" href="paper.html">Paper</a></div></div></section>
<section class="section"><div class="wrap">{flow_svg(title)}</div></section>
{body_extra}
{claim_boundary_block()}
'''
    return html_page(f"{title} | GoalOS AGIALPHA", body, subtitle)


def proof_card_page(num: int) -> str:
    title, subtitle = PROOF_CARD_TITLES[num]
    if num == 23:
        body = f'''
<section class="pc-hero"><div class="wrap"><span class="eyebrow">Proof Card 023 · Reserved</span><h1 class="h1">Proof Card <span class="gold">023</span></h1><p class="lead">Reserved to preserve continuity in the GoalOS public proof sequence. This page is intentionally stable, not missing.</p><div class="cta-row"><a class="btn primary" href="proof-cards.html">Back to Proof Card Atlas</a><a class="btn" href="proof-card-024.html">Continue to Proof Card 024</a></div></div></section><section class="section"><div class="wrap">{proof_card_visual(num,title)}</div></section>{claim_boundary_block()}'''
        return html_page("Proof Card 023 — Reserved | GoalOS AGIALPHA", body, "Reserved proof card page.")
    ascension = 24 <= num <= 31
    motif = ["orbit", "ledger", "helix", "flywheel", "constellation", "reactor", "docket", "reserve"][num % 8]
    object_rows = [
        ("GoalOS object", "Mission, artifact, proof packet, Evidence Docket, Chronicle entry."),
        ("Proof obligation", "Claims matrix, provenance, risk ledger, verifier report, and replay path."),
        ("Validator gate", "Review, challenge, replay, delayed-outcome, or rollback gate depending on risk."),
        ("Next proof", "Proof Run 001 public Evidence Docket."),
    ]
    body = f'''
<section class="pc-hero"><div class="wrap"><span class="eyebrow">Proof Card {num:03d} · {'Ascension sequence' if ascension else 'GoalOS evidence atlas'}</span><h1 class="h1">{esc(title)}</h1><p class="lead">{esc(subtitle)}</p><div class="hero-lines"><div class="hero-line">The product is not output. The product is proof-backed capability.</div><div class="hero-line">GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.</div></div><div class="cta-row"><a class="btn primary" href="mission-os.html">Open Mission OS</a><a class="btn" href="proof-cards.html">Proof Cards</a><a class="btn" href="proof-treasury.html">Proof Treasury</a><a class="btn" href="proof-run-001.html">Proof Run 001</a><a class="btn" href="paper.html">Paper</a></div></div></section>
<section class="section"><div class="wrap">{proof_card_visual(num,title)}</div></section>
<section class="section"><div class="wrap"><div class="three"><div class="card"><p class="kicker">Thesis</p><h3>{esc(title)}</h3><p>{esc(subtitle)} The card converts doctrine into an inspectable proof object.</p></div><div class="card gold"><p class="kicker">What it proves</p><p>This page shows how the motif <strong>{esc(motif)}</strong> maps to GoalOS proof, evidence, and future capability.</p></div><div class="card mint"><p class="kicker">Why it matters</p><p>Autonomous AI work becomes valuable when it can be reviewed, replayed, bounded, settled, rolled back, and reused.</p></div></div></div></section>
<section class="section"><div class="wrap"><h2>GoalOS object model.</h2><table><thead><tr><th>Layer</th><th>Explanation</th></tr></thead><tbody>{''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>' for a,b in object_rows)}</tbody></table></div></section>
<section class="section"><div class="wrap"><h2>$AGIALPHA role.</h2><p>$AGIALPHA does not create intelligence. It can make accepted proof economically consequential through escrow, bonds, verifier incentives, α‑Work Units, reputation, slashing, treasury routing, and capacity allocation.</p><div class="claim"><p>No proof → no settlement. No replay → no reinvestment. No governance → no acceleration.</p></div></div></section>
<section class="section"><div class="wrap"><h2>Evidence / next step.</h2><p>The next empirical threshold is Proof Run 001: a public Evidence Docket with claims, baselines, provenance, risks, verifier report, action graph, Chronicle entry, and replay path.</p><a class="btn primary" href="proof-run-001.html">Open Proof Run 001</a></div></section>
{claim_boundary_block()}
'''
    return html_page(f"Proof Card {num:03d} — {title} | GoalOS AGIALPHA", body, subtitle)


def proof_cards_page() -> str:
    groups = [
        ("Everyday proof", range(1,8)),
        ("Mission OS", range(8,15)),
        ("Proof economy and verified experience", range(15,23)),
        ("Reserved", [23]),
        ("Ascension sequence", range(24,32)),
    ]
    blocks = []
    for group, nums in groups:
        cards = []
        for i in nums:
            title, subtitle = PROOF_CARD_TITLES[i]
            cards.append(f'<a class="card" href="proof-card-{i:03d}.html"><span class="badge">Proof Card {i:03d}</span><h3>{esc(title)}</h3><p>{esc(subtitle)}</p></a>')
        blocks.append(f'<section class="section"><div class="wrap"><p class="kicker">{esc(group)}</p><div class="cards">{"".join(cards)}</div></div></section>')
    return generic_page("proof-cards.html", "Proof Card Atlas", "30 stable proof cards published; Proof Card 023 reserved. Every Proof Card page is unique, substantial, complete, dynamic, and well illustrated.", ''.join(blocks))


def treasury_page() -> str:
    extra = f'<section class="section"><div class="wrap"><h2>Proof Treasury ladder.</h2>{treasury_ladder_cards()}</div></section>'
    return generic_page("proof-treasury.html", "Proof Treasury", "$AGIALPHA proof-treasury simulations show how proof can govern settlement, replay, capacity, stress, and delayed-outcome reserve compounding.", extra)


def treasury_sim_page(n: int) -> str:
    data = {
        3: ("External Replay Market & Capacity Auction", "No external replay, no capacity scale.", "10,000,000 simulated $AGIALPHA"),
        4: ("Institutional Stress Gauntlet & Sovereign Capacity Reserve", "No stress clearance, no institutional scale.", "100,000,000 simulated $AGIALPHA"),
        5: ("Delayed-Outcome Covenant & Ascension Reserve", "No delayed-outcome clearance, no Ascension reserve compounding.", "1,000,000,000 simulated $AGIALPHA"),
    }[n]
    title, law, budget = data
    extra = f'''
<section class="section"><div class="wrap"><div class="three"><div class="card gold"><span class="badge">Law</span><h3>{esc(law)}</h3></div><div class="card"><span class="badge">Budget scale</span><h3>{esc(budget)}</h3><p>Simulation only. No wallet. No private key. No token movement. No Mainnet broadcast.</p></div><div class="card"><span class="badge">Output artifacts</span><p>Evidence Docket, ledger CSVs, thermostat signals, no-token-movement certificate, Chronicle entry, and run-state.</p></div></div></div></section>
<section class="section"><div class="wrap"><h2>Protocol-level call surface.</h2><table><thead><tr><th>Call</th><th>Purpose</th></tr></thead><tbody><tr><td>ProofTreasuryVault.fundEpoch</td><td>Funds the simulated epoch budget.</td></tr><tr><td>ExternalReplayMarket.submitReplayAttestation</td><td>Records external replay state.</td></tr><tr><td>InstitutionalStressGate.recordStressVerdict</td><td>Records stress-clearance state.</td></tr><tr><td>DelayedOutcomeOracle.recordDelayedOutcome</td><td>Records delayed-outcome state.</td></tr><tr><td>TreasuryRouter.allocateAscensionReserve</td><td>Allocates only to cleared proof states.</td></tr></tbody></table><p class="mini">These are protocol-level templates, not live on-chain calls.</p></div></section>
'''
    return generic_page(f"proof-treasury-simulation-{n:03d}.html", f"Proof Treasury Simulation {n:03d}", f"{title}. {law}", extra)


def paper_page(cover_path: str) -> str:
    extra = f'<section class="section"><div class="wrap paper"><div class="paper-cover"><img src="{cover_path}" alt="Front page preview of GoalOS Mission OS Paper"></div><div><h2>GoalOS Mission OS — The Proof OS for Autonomous AI Work</h2><p class="lead">Set the objective. GoalOS runs until proof is done. AI creates output. GoalOS creates proof.</p><p>The paper defines governed decision states, Evidence Dockets, verifier reports, risk ledgers, executive briefs, action graphs, Chronicle memory, and claim boundaries.</p><a class="btn primary" href="{PAPER_PATH}">Read / Download Paper</a></div></div></section>'
    return generic_page("paper.html", "GoalOS Mission OS Paper", "The flagship paper for Mission OS and proof-to-action work.", extra)


def page_extras(slug: str) -> str:
    if slug == "mission-os.html":
        return '<section class="section"><div class="wrap"><h2>Set the objective. GoalOS runs until proof is done.</h2><div class="cards"><div class="card"><h3>1. Choose the goal</h3><p>Pick one useful mission: job search, side-business validation, learning plan, paperwork, finance, family decision support, or AI-first founder proof sprint.</p></div><div class="card"><h3>2. Generate proof objects</h3><p>Mission Contract, Claims Matrix, Evidence Docket, Verifier Report, Risk Ledger, Decision State, Action Graph, and Chronicle Entry.</p></div><div class="card"><h3>3. Review and reuse</h3><p>Only accepted proof becomes reusable capability. No proof, no propagation.</p></div></div></div></section>'
    if slug == "ascension.html":
        return f'<section class="section"><div class="wrap"><h2>SOTA is a measurement. Ascension is the mission.</h2>{flow_svg("Ascension = VerifiedCapability × Reuse × SettlementPressure × ChronicleMemory × RSI")}</div></section>'
    if slug == "agialpha-continuity.html":
        return f'<section class="section"><div class="wrap"><h2>AGI Alpha Job Market → GoalOS Proof Economy → Ascension</h2>{flywheel_svg()}<p>No outbound agialpha.com link is emitted. This page preserves continuity without creating an external dependency.</p></div></section>'
    if slug == "evidence-docket.html":
        return '<section class="section"><div class="wrap"><h2>Evidence Docket standard.</h2><table><thead><tr><th>Docket element</th><th>Purpose</th></tr></thead><tbody><tr><td>Manifest</td><td>Claim, version, signer, public/private boundary.</td></tr><tr><td>Claims matrix</td><td>What is claimed, not claimed, and required evidence.</td></tr><tr><td>Proof packets</td><td>Trace roots, output hashes, policy decisions, cost, latency, signatures.</td></tr><tr><td>Safety ledger</td><td>Incidents, blocked actions, unsafe candidates, rollback drills.</td></tr></tbody></table></div></section>'
    if slug == "resources.html":
        return f'<section class="section"><div class="wrap"><h2>Core resources.</h2><div class="cards"><a class="card" href="{PAPER_PATH}"><h3>Mission OS Paper</h3><p>Read / Download Paper.</p></a><a class="card" href="proof-cards.html"><h3>Proof Card Atlas</h3><p>30 stable proof cards; Proof Card 023 reserved.</p></a><a class="card" href="proof-treasury.html"><h3>Proof Treasury</h3><p>Proof-conditioned economics simulations.</p></a></div></div></section>'
    if slug == "proof-run-001.html":
        return '<section class="section"><div class="wrap"><h2>Proof Run 001 public Evidence Docket threshold.</h2><p>Proof Run 001 turns Ascension from doctrine into public evidence.</p><table><thead><tr><th>Artifact</th><th>Required proof</th></tr></thead><tbody><tr><td>Mission Contract</td><td>Objective, constraints, success and failure criteria.</td></tr><tr><td>Claims Matrix</td><td>What is claimed, not claimed, and required evidence.</td></tr><tr><td>Evidence Docket</td><td>Proof packets, provenance, risks, costs, verifier report, replay path.</td></tr><tr><td>Chronicle Entry</td><td>Reusable memory and next proof step.</td></tr></tbody></table></div></section>'
    if slug == "observatory.html":
        return '<section class="section"><div class="wrap"><h2>Current claim level.</h2><div class="three"><div class="card"><h3>Architecture</h3><p>Strong and category-defining.</p></div><div class="card"><h3>Public alpha</h3><p>Live site, proof cards, Mission OS paper, simulations.</p></div><div class="card"><h3>Next threshold</h3><p>Proof Run 001 public Evidence Docket.</p></div></div></div></section>'
    return '<section class="section"><div class="wrap"><div class="cards"><div class="card"><h3>Proof-backed progress</h3><p>Objectives become Mission Contracts and Evidence Dockets.</p></div><div class="card"><h3>Verification</h3><p>Review, replay, stress, delayed outcomes, and claim boundaries.</p></div><div class="card"><h3>Reuse</h3><p>Chronicle memory turns proof into future capability.</p></div></div></div></section>'


def build_site(root: Path, out: Path) -> None:
    clean_out(out)
    asset_report = copy_assets(root, out)
    cover_status = render_paper_cover(root, out)
    cover_path = cover_status["path"]
    if cover_path.startswith("site/"):
        cover_path = cover_path[5:]
    (out / "style.css").write_text(stylesheet(), encoding="utf-8")
    pages = {}
    pages["index.html"] = homepage(cover_path)
    pages["proof-cards.html"] = proof_cards_page()
    pages["proof-treasury.html"] = treasury_page()
    pages["paper.html"] = paper_page(cover_path)
    for n in [3,4,5]:
        pages[f"proof-treasury-simulation-{n:03d}.html"] = treasury_sim_page(n)
    for slug, title, subtitle in [
        ("executive.html", "Executive Command", "Institutional overview for partners, leaders, and governance readers."),
        ("observatory.html", "Ascension Observatory", "Latest proof state, evidence threshold, and claim level."),
        ("mission-os.html", "Mission OS", "The Proof OS for Autonomous AI Work."),
        ("ascension.html", "Ascension", "SOTA is a measurement. Ascension is the mission."),
        ("resources.html", "Resources", "Papers, proof cards, simulations, and onboarding."),
        ("autopilot.html", "Autopilot", "Proof-ready mission drafting and operator guidance."),
        ("mission-builder.html", "Mission Builder", "Build a proof-ready mission packet."),
        ("start-here.html", "Start Here", "A nontechnical path to one useful proof-backed mission."),
        ("evidence-docket.html", "Evidence Docket", "The public-safe proof room for GoalOS work."),
        ("proof-run-001.html", "Proof Run 001", "The next public Evidence Docket threshold."),
        ("agialpha-continuity.html", "AGI Alpha Continuity", "Agent job market lineage to GoalOS proof economy."),
    ]:
        pages[slug] = generic_page(slug, title, subtitle, page_extras(slug))
    for i in range(1, 32):
        pages[f"proof-card-{i:03d}.html"] = proof_card_page(i)
    for name, content in pages.items():
        (out / name).write_text(content, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + BASE_URL + "sitemap.xml\n", encoding="utf-8")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name in sorted(pages):
        sitemap.append(f"<url><loc>{BASE_URL}{name}</loc></url>")
    sitemap.append("</urlset>")
    (out / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")
    manifest = {"name":"GoalOS AGIALPHA Ascension","short_name":"GoalOS","start_url":"index.html","display":"standalone","background_color":"#07111f","theme_color":"#f3d98b"}
    (out / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    status = {
        "release": RELEASE,
        "version": VERSION,
        "generated_at": GEN_TIME,
        "proof_cards_published": PROOF_CARD_COUNT,
        "proof_card_023": "reserved",
        "proof_treasury_count": PROOF_TREASURY_COUNT,
        "claim_boundary": "active",
        "paper_link": PAPER_PATH,
        "paper_cover_status": cover_status,
        "main_hero_asset": MAIN_ASSET,
        "asset_report": asset_report,
        "pages_generated": sorted(pages.keys()),
        "no_zip_files_in_site": True,
        "next_recommended_artifact": "Proof Run 001 public Evidence Docket",
    }
    (out / "site-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site")
    args = ap.parse_args()
    root = Path.cwd()
    build_site(root, root / args.out)
    print(f"Built {RELEASE} into {args.out}")

if __name__ == "__main__":
    main()
