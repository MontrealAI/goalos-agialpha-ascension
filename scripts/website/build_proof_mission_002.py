#!/usr/bin/env python3
"""Generate GoalOS Public Proof Mission 002 as an additive website overlay.

The canonical website source is never edited. This script operates only on the
transient ``site`` directory produced by the existing v86 website builder.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

START = "<!-- GOALOS_PROOF_MISSION_002_START -->"
END = "<!-- GOALOS_PROOF_MISSION_002_END -->"
STYLE_START = "<!-- GOALOS_PROOF_MISSION_002_STYLE_START -->"
STYLE_END = "<!-- GOALOS_PROOF_MISSION_002_STYLE_END -->"
MISSION1_END = "<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->"
PAGE = "proof-mission-002.html"
HUB = "proof-missions.html"
CANONICAL = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
FORBIDDEN_PUBLIC = (
    "recursive.com",
    "recursive org",
    "recursive-style",
    "competitor comparison",
    "named competitor",
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic boundary
        fail(f"cannot read {path}: {exc}")


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def validate(content: dict[str, Any], mainnet: dict[str, Any]) -> None:
    if content.get("missionId") != "GOALOS-PUBLIC-PROOF-MISSION-002":
        fail("wrong Mission 002 identifier")
    if content.get("sequence") != 2:
        fail("Mission 002 sequence must be 2")
    if sum(int(item.get("share", 0)) for item in content.get("settlement", [])) != 100:
        fail("Mission 002 settlement shares must total 100")
    if mainnet.get("chainId") != 1:
        fail("Mainnet data must use chainId 1")
    if mainnet.get("canonicalAgialpha", "").lower() != CANONICAL.lower():
        fail("wrong canonical AGIALPHA")
    if mainnet.get("goalosCreatedContractCount") != 48:
        fail("expected 48 GoalOS-created contracts")
    verification = mainnet.get("verification", {})
    if verification.get("verified") != 48 or verification.get("failed") != 0:
        fail("expected 48 verified and 0 failed")
    if mainnet.get("deploymentStatus") != "CONFIGURED":
        fail("Mainnet deployment is not CONFIGURED")
    if mainnet.get("phaseBGrantCount") != 14:
        fail("expected 14 configured grants")
    postcheck = mainnet.get("postcheck", {})
    if postcheck.get("status") != "PASSED" or postcheck.get("checkedContracts") != 48:
        fail("postcheck does not cover 48 contracts")
    names = {entry["name"] for entry in mainnet.get("contracts", [])}
    missing = [entry["contractName"] for entry in content.get("proofRoute", []) if entry["contractName"] not in names]
    if missing:
        fail("unknown proof-route contracts: " + ", ".join(missing))
    public_blob = json.dumps(content, ensure_ascii=False).lower()
    for forbidden in FORBIDDEN_PUBLIC:
        if forbidden in public_blob:
            fail(f"prohibited public reference: {forbidden}")


def critical_css() -> str:
    return r'''<style id="goalos-v86-critical">
:root{--ap-night:#061018;--ap-deep:#0a1b28;--ap-ink:#061018;--ap-ivory:#f7f2e7;--ap-gold:#f3c96b;--ap-mint:#7ce4c0;--ap-cyan:#5ce7ff;--ap-violet:#a694ff;--ap-muted:#afc0cb;--ap-line:rgba(255,255,255,.14)}
*{box-sizing:border-box}.ap-body{margin:0;background:var(--ap-night);color:#eef8fb;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow-x:hidden}.ap-body a{color:inherit}.ap-skip{position:absolute;left:-999px;top:0}.ap-skip:focus{left:1rem;top:1rem;z-index:9999;background:#fff;color:#061018;padding:.8rem 1rem;border-radius:999px}.ap-shell{width:min(1180px,calc(100% - 2rem));margin:auto}.ap-nav{position:sticky;top:0;z-index:100;background:rgba(6,16,24,.86);backdrop-filter:blur(18px);border-bottom:1px solid var(--ap-line)}.ap-navin{min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:1rem}.ap-brand{text-decoration:none;font-weight:1000;letter-spacing:-.025em}.ap-brand span{color:var(--ap-gold)}.ap-navlinks{display:flex;gap:.42rem;flex-wrap:wrap;justify-content:flex-end}.ap-navlinks a{padding:.55rem .8rem;border-radius:999px;text-decoration:none;color:#c8d8e1;font-size:.88rem;font-weight:800}.ap-navlinks a:hover,.ap-navlinks a:focus{background:rgba(255,255,255,.09);color:#fff}.ap-hero{position:relative;min-height:calc(100vh - 72px);display:grid;place-items:center;isolation:isolate;background:radial-gradient(circle at 72% 30%,rgba(243,201,107,.18),transparent 26%),radial-gradient(circle at 24% 38%,rgba(124,228,192,.12),transparent 30%),linear-gradient(180deg,#061018 0%,#091723 56%,#0b2130 100%)}.ap-hero:before{content:"";position:absolute;inset:0;z-index:-2;background-image:linear-gradient(rgba(255,255,255,.033) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.033) 1px,transparent 1px);background-size:54px 54px;mask-image:linear-gradient(to bottom,#000,transparent 90%)}.ap-hero-grid{display:grid;grid-template-columns:minmax(0,1.06fr) minmax(360px,.94fr);gap:4rem;align-items:center;padding:5.5rem 0}.ap-kicker,.ap-eyebrow{display:inline-flex;align-items:center;gap:.55rem;text-transform:uppercase;letter-spacing:.15em;font-size:.72rem;font-weight:1000;color:var(--ap-gold)}.ap-kicker:before,.ap-eyebrow:before{content:"";width:30px;height:1px;background:currentColor}.ap-hero h1{font-size:clamp(3.7rem,9vw,7.8rem);line-height:.84;letter-spacing:-.072em;margin:1.15rem 0 1.35rem}.ap-hero h1 span{display:block;color:transparent;background:linear-gradient(95deg,var(--ap-gold),#fff 48%,var(--ap-mint));background-clip:text}.ap-question{font-size:clamp(1.22rem,2.25vw,1.72rem);line-height:1.45;color:#e2edf2;max-width:760px}.ap-manifesto{margin:1.5rem 0;padding:1rem 1.2rem;border-left:3px solid var(--ap-mint);background:linear-gradient(90deg,rgba(124,228,192,.11),transparent);font-size:1.08rem;font-weight:900}.ap-status{display:inline-flex;align-items:center;gap:.6rem;padding:.66rem .9rem;border:1px solid rgba(243,201,107,.3);background:rgba(243,201,107,.08);border-radius:999px;color:#f7dd9e;font-size:.78rem;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.ap-status:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--ap-gold);box-shadow:0 0 18px rgba(243,201,107,.8)}.ap-actions{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1.8rem}.ap-btn{display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:.78rem 1.08rem;border:1px solid rgba(255,255,255,.23);border-radius:999px;text-decoration:none;font-weight:950;background:rgba(255,255,255,.055);transition:.22s ease}.ap-btn:hover,.ap-btn:focus{transform:translateY(-2px);background:rgba(255,255,255,.11)}.ap-btn.primary{background:linear-gradient(100deg,var(--ap-gold),#f9e2a6);color:#061018;border-color:transparent;box-shadow:0 0 38px rgba(243,201,107,.17)}.ap-ascension{position:relative;aspect-ratio:1;border:1px solid rgba(255,255,255,.15);border-radius:50%;background:radial-gradient(circle,rgba(243,201,107,.14),transparent 31%),rgba(255,255,255,.024);box-shadow:inset 0 0 90px rgba(124,228,192,.05),0 34px 110px rgba(0,0,0,.38)}.ap-ring{position:absolute;border-radius:50%;border:1px solid rgba(255,255,255,.15)}.ap-ring.r1{inset:8%}.ap-ring.r2{inset:22%;border-color:rgba(124,228,192,.27)}.ap-ring.r3{inset:35%;border-color:rgba(243,201,107,.32)}.ap-helix{position:absolute;inset:7%;border-radius:50%;border:2px dashed rgba(92,231,255,.28);animation:ap-spin 30s linear infinite}.ap-core{position:absolute;inset:36%;display:grid;place-items:center;text-align:center;border-radius:50%;z-index:5;background:radial-gradient(circle at 35% 30%,#fff,var(--ap-gold) 38%,var(--ap-mint) 72%,#0b2130);box-shadow:0 0 70px rgba(243,201,107,.35);color:#061018;font-weight:1000}.ap-core span{display:block;font-size:.62rem;letter-spacing:.12em}.ap-node{position:absolute;z-index:4;width:94px;height:94px;border-radius:50%;display:grid;place-items:center;text-align:center;padding:.48rem;border:1px solid rgba(255,255,255,.25);background:rgba(8,25,38,.94);font-size:.68rem;font-weight:950;box-shadow:0 15px 42px rgba(0,0,0,.3)}.ap-node.n1{left:7%;top:20%}.ap-node.n2{right:4%;top:19%}.ap-node.n3{right:-2%;top:50%}.ap-node.n4{right:14%;bottom:7%}.ap-node.n5{left:14%;bottom:7%}.ap-node.n6{left:-2%;top:50%}.ap-section{padding:7rem 0;position:relative}.ap-section.light{background:var(--ap-ivory);color:#071522}.ap-section.deep{background:#071522}.ap-section.gold{background:linear-gradient(135deg,#f5d681,#e8b94f);color:#061018}.ap-heading{max-width:900px;margin-bottom:2.6rem}.ap-heading h2{font-size:clamp(2.35rem,5vw,4.7rem);line-height:.98;letter-spacing:-.055em;margin:.85rem 0}.ap-heading p{font-size:1.15rem;line-height:1.7;opacity:.78}.ap-constitution{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.ap-law{padding:2rem;border:1px solid rgba(255,255,255,.15);border-radius:24px;background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025));font-size:clamp(1.22rem,2.2vw,1.76rem);font-weight:950;letter-spacing:-.035em}.light .ap-law{border-color:rgba(5,16,24,.12);background:#fff}.ap-control-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.ap-control{padding:1.65rem;border-radius:24px;border:1px solid rgba(5,16,24,.11);background:#fff;box-shadow:0 16px 50px rgba(7,21,34,.07)}.ap-control small{display:block;color:#8d6a19;font-size:.7rem;font-weight:1000;letter-spacing:.12em}.ap-control h3{font-size:1.45rem;margin:.55rem 0}.ap-control p{color:#526776;line-height:1.62}.ap-control.treatment{background:#071522;color:#fff;border-color:#071522}.ap-control.treatment p{color:#c1d2dd}.ap-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:2rem}.ap-metric{padding:1.35rem;border:1px solid rgba(255,255,255,.15);border-radius:20px;background:rgba(255,255,255,.045)}.ap-metric strong{display:block;font-size:clamp(2rem,4vw,3.25rem);letter-spacing:-.05em}.ap-metric span{color:#bacbd5;font-size:.84rem;font-weight:800}.ap-chain{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}.ap-step{display:grid;grid-template-columns:54px 1fr;gap:1rem;padding:1.45rem;border-radius:22px;background:#fff;color:#071522;border:1px solid rgba(5,16,24,.1)}.ap-step b{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:#071522;color:#fff}.ap-step small{display:block;color:#8b6d26;font-weight:950;text-transform:uppercase;letter-spacing:.1em}.ap-step h3{font-size:1.25rem;margin:.35rem 0}.ap-step p{color:#526776;line-height:1.58;margin:.35rem 0 0}.ap-passport{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}.ap-passport-card{padding:1.45rem;border:1px solid rgba(255,255,255,.15);border-radius:20px;background:rgba(255,255,255,.05)}.ap-passport-card h3{margin:.2rem 0 .55rem;font-size:1.12rem;color:#fff}.ap-passport-card p{margin:0;color:#bfd0da;line-height:1.58}.ap-failure-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:.8rem}.ap-failure{padding:1.2rem;border-radius:18px;background:#fff;border:1px solid rgba(5,16,24,.11)}.ap-failure code{display:block;color:#9a6310;font-weight:950;margin-bottom:.5rem}.ap-failure p{margin:0;color:#526776;line-height:1.55}.ap-ladder{display:grid;grid-template-columns:repeat(5,1fr);gap:.8rem}.ap-level{padding:1.35rem;border-radius:20px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.045);min-height:220px}.ap-level strong{display:inline-grid;place-items:center;width:42px;height:42px;border-radius:50%;background:var(--ap-gold);color:#061018}.ap-level h3{font-size:1.22rem;margin:1rem 0 .55rem}.ap-level p{color:#bfd0da;line-height:1.55}.ap-level.target{border-color:rgba(124,228,192,.55);box-shadow:0 0 38px rgba(124,228,192,.08)}.ap-settlement{display:grid;grid-template-columns:1fr 1fr;gap:2rem;align-items:center}.ap-ring-chart{width:min(420px,100%);aspect-ratio:1;border-radius:50%;margin:auto;background:conic-gradient(#f3c96b 0 35%,#7ce4c0 35% 50%,#5ce7ff 50% 65%,#a694ff 65% 75%,#ff9e9e 75% 85%,#fff0b7 85% 95%,#87bbff 95% 100%);display:grid;place-items:center;box-shadow:0 28px 80px rgba(0,0,0,.28)}.ap-ring-chart:after{content:"PROOF\A SETTLES\A CONDITIONALLY";white-space:pre;text-align:center;display:grid;place-items:center;width:54%;aspect-ratio:1;border-radius:50%;background:#071522;color:#fff;font-weight:1000;letter-spacing:.05em}.ap-settlement-list{display:grid;gap:.65rem}.ap-settlement-row{display:grid;grid-template-columns:1fr auto;gap:1rem;padding:.85rem 0;border-bottom:1px solid rgba(255,255,255,.13)}.ap-settlement-row strong{color:var(--ap-gold)}.ap-route{display:grid;gap:.75rem}.ap-route-item{display:grid;grid-template-columns:52px 1fr auto;gap:1rem;align-items:center;padding:1rem 1.1rem;border:1px solid rgba(5,16,24,.11);border-radius:18px;background:#fff}.ap-route-item b{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#071522;color:#fff}.ap-route-item h3{margin:0;font-size:1.02rem}.ap-route-item p{margin:.28rem 0 0;color:#627784;font-size:.9rem}.ap-route-item a{color:#0c6577;font-weight:900;text-decoration:none}.ap-boundary{padding:2.2rem;border:1px solid rgba(255,255,255,.16);border-radius:28px;background:linear-gradient(145deg,rgba(255,255,255,.07),rgba(255,255,255,.025))}.ap-list{padding:0;list-style:none;margin:0;display:grid;gap:.76rem}.ap-list li{position:relative;padding-left:1.55rem;color:#c7d8e2;line-height:1.56}.ap-list li:before{content:"✓";position:absolute;left:0;color:var(--ap-mint);font-weight:1000}.ap-downloads{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.6rem}.ap-downloads a{padding:.65rem .85rem;border:1px solid rgba(255,255,255,.18);border-radius:999px;text-decoration:none;font-size:.84rem;font-weight:900}.ap-footer{border-top:1px solid rgba(255,255,255,.12);padding:2rem 0;color:#abc0cc}.ap-footerin{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}.ap-horizon{padding:2.2rem;border-radius:28px;background:#fff;color:#071522;box-shadow:0 18px 60px rgba(7,21,34,.08)}.ap-horizon h3{font-size:clamp(2rem,4vw,3.5rem);margin:.5rem 0;letter-spacing:-.045em}.ap-horizon p{font-size:1.06rem;color:#566b78;line-height:1.65}.ap-formula{font-size:clamp(1.35rem,3vw,2.45rem);font-weight:1000;line-height:1.25;letter-spacing:-.035em;padding:1.7rem;border:1px solid rgba(255,255,255,.15);border-radius:22px;background:rgba(255,255,255,.05)}.ap-formula span{color:var(--ap-gold)}
@keyframes ap-spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.ap-helix{animation:none}.ap-btn{transition:none}}@media(max-width:980px){.ap-hero-grid,.ap-settlement{grid-template-columns:1fr}.ap-ascension{max-width:560px;width:100%;margin:auto}.ap-ladder{grid-template-columns:repeat(2,1fr)}.ap-node{width:82px;height:82px}}@media(max-width:760px){.ap-navin{align-items:flex-start;padding:.9rem 0}.ap-navlinks{display:none}.ap-constitution,.ap-control-grid,.ap-chain,.ap-passport,.ap-failure-grid,.ap-metrics{grid-template-columns:1fr}.ap-route-item{grid-template-columns:44px 1fr}.ap-route-item a{grid-column:2}.ap-ladder{grid-template-columns:1fr}.ap-section{padding:5rem 0}}@media(max-width:520px){.ap-shell{width:min(100% - 1.2rem,1180px)}.ap-hero-grid{padding:4rem 0;gap:2.5rem}.ap-hero h1{font-size:3.5rem}.ap-actions .ap-btn{width:100%}.ap-node{width:70px;height:70px;font-size:.58rem}.ap-route-item{padding:.9rem}.ap-question{font-size:1.15rem}}
</style>'''


def proof_route(content: dict[str, Any], mainnet: dict[str, Any]) -> str:
    address_by_name = {entry["name"]: entry for entry in mainnet["contracts"]}
    rows: list[str] = []
    for item in content["proofRoute"]:
        contract = address_by_name[item["contractName"]]
        rows.append(
            f'''<article class="ap-route-item"><b>{int(item["sequence"]):02d}</b><div><h3>{esc(item["stage"])} · {esc(item["contractName"])}</h3><p>{esc(item["purpose"])}</p></div><a href="{esc(contract["etherscanUrl"])}" target="_blank" rel="noreferrer">Etherscan ↗</a></article>'''
        )
    return "".join(rows)


def page(content: dict[str, Any], mainnet: dict[str, Any]) -> str:
    laws = "".join(f'<div class="ap-law">{esc(item)}</div>' for item in content["constitution"])
    controls = "".join(
        f'''<article class="ap-control{' treatment' if item['id']=='TREATMENT' else ''}"><small>{esc(item['id'])}</small><h3>{esc(item['title'])}</h3><p>{esc(item['copy'])}</p></article>'''
        for item in content["controlArms"]
    )
    chain = "".join(
        f'''<article class="ap-step"><b>{idx:02d}</b><div><small>{esc(item['stage'])}</small><h3>{esc(item['title'])}</h3><p>{esc(item['copy'])}</p></div></article>'''
        for idx, item in enumerate(content["proofChain"], 1)
    )
    acceptance = "".join(f"<li>{esc(item)}</li>" for item in content["acceptance"])
    passport = "".join(
        f'''<article class="ap-passport-card"><h3>{esc(item['field'])}</h3><p>{esc(item['purpose'])}</p></article>'''
        for item in content["assumptionPassport"]
    )
    failures = "".join(
        f'''<article class="ap-failure"><code>{esc(item['code'])}</code><p>{esc(item['copy'])}</p></article>'''
        for item in content["failureAtlas"]
    )
    ladder = "".join(
        f'''<article class="ap-level{' target' if item['level']=='M2' else ''}"><strong>{esc(item['level'])}</strong><h3>{esc(item['title'])}</h3><p>{esc(item['copy'])}</p></article>'''
        for item in content["maturityLadder"]
    )
    settlement = "".join(
        f'''<div class="ap-settlement-row"><span>{esc(item['label'])}</span><strong>{int(item['share'])}%</strong></div>'''
        for item in content["settlement"]
    )
    boundary = "".join(f"<li>{esc(item)}</li>" for item in content["claimBoundary"])
    route = proof_route(content, mainnet)
    budget = content["missionBudget"]
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="GoalOS Public Proof Mission 002 — The Ascension Protocol. A public protocol for proving capability transfer, abstention, replay, rollback, and compounding intelligence."><meta name="theme-color" content="#061018"><title>Proof Mission 002 — The Ascension Protocol · GoalOS AGIALPHA</title><link rel="stylesheet" href="assets/goalos-v86-preserve.css">{critical_css()}</head><body class="ap-body"><a class="ap-skip" href="#main">Skip to content</a><header class="ap-nav"><div class="ap-shell ap-navin"><a class="ap-brand" href="index.html">GoalOS <span>AGIALPHA</span></a><nav class="ap-navlinks" aria-label="Proof Mission navigation"><a href="proof-missions.html">Proof Missions</a><a href="proof-gradient-challenge.html">Mission 001</a><a href="#trial">Transfer trial</a><a href="#mainnet">Mainnet route</a><a href="{esc(content['repositoryUrl'])}" target="_blank" rel="noreferrer">GitHub ↗</a></nav></div></header><main id="main"><section class="ap-hero"><div class="ap-shell ap-hero-grid"><div><div class="ap-kicker">{esc(content['kicker'])}</div><h1>THE ASCENSION <span>PROTOCOL</span></h1><p class="ap-question"><strong>{esc(content['subtitle'])}</strong><br>{esc(content['heroQuestion'])}</p><p class="ap-manifesto">{esc(content['manifesto'])}</p><div class="ap-status">Protocol published · no result predeclared</div><div class="ap-actions"><a class="ap-btn primary" href="#trial">Enter the transfer trial</a><a class="ap-btn" href="proof-gradient-challenge.html">Begin with Mission 001</a><a class="ap-btn" href="#mainnet">Inspect the proof route</a></div></div><div class="ap-ascension" aria-label="Capability ascension diagram"><div class="ap-helix"></div><div class="ap-ring r1"></div><div class="ap-ring r2"></div><div class="ap-ring r3"></div><div class="ap-core">M2<span>TRANSFER-PROVEN</span></div><div class="ap-node n1">ACCEPTED<br>CAPABILITY</div><div class="ap-node n2">ASSUMPTION<br>PASSPORT</div><div class="ap-node n3">DOMAIN<br>SHIFT</div><div class="ap-node n4">INDEPENDENT<br>REPLAY</div><div class="ap-node n5">ROLLBACK<br>READY</div><div class="ap-node n6">HARDER<br>MISSION</div></div></div></section>
<section class="ap-section deep"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">The constitutional threshold</span><h2>Winning once is not compounding intelligence.</h2><p>{esc(content['publicThesis'])}</p></div><div class="ap-constitution">{laws}</div><div class="ap-formula" style="margin-top:1rem">Accepted proof <span>×</span> explicit assumptions <span>×</span> replayed transfer <span>×</span> rollback readiness <span>=</span> compounding capability.</div></div></section>
<section class="ap-section light" id="trial"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">The controlled transfer trial</span><h2>Same harder mission. Three institutional conditions.</h2><p>{esc(content['objective'])}</p></div><div class="ap-control-grid">{controls}</div><div class="ap-metrics"><div class="ap-metric"><strong>50%</strong><span>of Mission 001 search budget</span></div><div class="ap-metric"><strong>{int(budget['candidatePatchesPerSearchArm'])}</strong><span>candidate patches per search arm</span></div><div class="ap-metric"><strong>{int(budget['gpuHoursPerSearchArm'])}h</strong><span>GPU budget per search arm</span></div><div class="ap-metric"><strong>{int(budget['challengeWindowHours'])}h</strong><span>public challenge window</span></div></div></div></section>
<section class="ap-section deep"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">Acceptance contract</span><h2>Transfer must outperform memory-free search—and know when to abstain.</h2><p>No capability receives propagation rights merely because it came from an accepted predecessor.</p></div><ul class="ap-list">{acceptance}</ul></div></section>
<section class="ap-section light"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">The proof chain</span><h2>From inherited capability to transfer-proven maturity.</h2><p>Every transition is published. Negative transfer and unsupported reuse are first-class outcomes.</p></div><div class="ap-chain">{chain}</div></div></section>
<section class="ap-section deep"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">Capability assumption passport</span><h2>Every reusable capability travels with its limits.</h2><p>The passport prevents a task-bounded result from silently becoming an unbounded claim.</p></div><div class="ap-passport">{passport}</div></div></section>
<section class="ap-section light"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">Failure atlas</span><h2>What fails becomes institutional memory.</h2><p>Mission 002 is designed to discover where reuse breaks—not to hide those boundaries.</p></div><div class="ap-failure-grid">{failures}</div></div></section>
<section class="ap-section deep"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">Capability maturity</span><h2>Proof earns rights in stages.</h2><p>Mission 002 targets M2. Higher maturity remains explicitly future and evidence-gated.</p></div><div class="ap-ladder">{ladder}</div></div></section>
<section class="ap-section gold"><div class="ap-shell"><div class="ap-settlement"><div><span class="ap-eyebrow">Conditional AGIALPHA settlement</span><h2 style="font-size:clamp(2.6rem,5vw,4.8rem);line-height:.96;letter-spacing:-.055em;margin:.8rem 0 1.2rem">Proof does not merely describe value. It governs where value flows next.</h2><p style="font-size:1.12rem;line-height:1.7">Settlement occurs only after replay, validator approval, and the public challenge window. A declared share is reserved for the next mission rather than treating acceptance as the end of the loop.</p><div class="ap-settlement-list">{settlement}</div></div><div class="ap-ring-chart" aria-label="Mission 002 settlement allocation chart"></div></div></div></section>
<section class="ap-section light"><div class="ap-shell"><div class="ap-horizon"><span class="ap-eyebrow">The next horizon</span><h3>{esc(content['mission3']['title'])}</h3><p>{esc(content['mission3']['copy'])}</p><p><strong>Status:</strong> horizon only; not yet authorized.</p></div></div></section>
<section class="ap-section light" id="mainnet"><div class="ap-shell"><div class="ap-heading"><span class="ap-eyebrow">Ethereum Mainnet proof route</span><h2>The transfer protocol maps to deployed GoalOS infrastructure.</h2><p>The release evidence records 48 GoalOS-created contracts, 48 verified, zero verification failures, 14 active configuration grants, and a passing 48-contract postcheck. Infrastructure existence does not predeclare Mission 002 success.</p></div><div class="ap-route">{route}</div></div></section>
<section class="ap-section deep"><div class="ap-shell"><div class="ap-boundary"><span class="ap-eyebrow">Claim boundary</span><h2 style="font-size:clamp(2.2rem,4vw,3.8rem);letter-spacing:-.045em;margin:.75rem 0 1.2rem">Grand ambition. Exact language.</h2><ul class="ap-list">{boundary}</ul><div class="ap-downloads"><a href="downloads/proof-missions/public-proof-mission-002.json">Mission 002 JSON</a><a href="downloads/proof-missions/mission-002-assumption-passport-template.json">Assumption passport</a><a href="downloads/proof-missions/mission-002-proof-route.csv">Proof route CSV</a><a href="proof-missions.html">Proof Missions hub</a><a href="{esc(content['releaseUrl'])}" target="_blank" rel="noreferrer">Mainnet release ↗</a></div></div></div></section></main><footer class="ap-footer"><div class="ap-shell ap-footerin"><strong>GoalOS AGIALPHA Ascension · Public Proof Mission 002</strong><span>Ethereum Mainnet infrastructure · Not externally audited · No result predeclared</span></div></footer><script src="assets/goalos-v86-dynamic-ai.js" defer></script></body></html>'''


def hub_page(content: dict[str, Any], mainnet: dict[str, Any]) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="The GoalOS Public Proof Missions: a public program for turning autonomous work into accepted, transferable, replayable, rollback-ready capability."><meta name="theme-color" content="#061018"><title>The Proof Missions · GoalOS AGIALPHA</title><link rel="stylesheet" href="assets/goalos-v86-preserve.css"><style id="goalos-v86-critical">
:root{{--pm-night:#061018;--pm-gold:#f3c96b;--pm-cyan:#5ce7ff;--pm-mint:#7ce4c0;--pm-violet:#a694ff;--pm-ivory:#f7f2e7}}*{{box-sizing:border-box}}body{{margin:0;background:#061018;color:#eef7fb;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}a{{color:inherit}}.pm-shell{{width:min(1180px,calc(100% - 2rem));margin:auto}}.pm-nav{{border-bottom:1px solid rgba(255,255,255,.13);background:rgba(6,16,24,.9);position:sticky;top:0;z-index:20;backdrop-filter:blur(18px)}}.pm-navin{{min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:1rem}}.pm-brand{{font-weight:1000;text-decoration:none}}.pm-links{{display:flex;gap:.5rem;flex-wrap:wrap}}.pm-links a{{text-decoration:none;padding:.55rem .8rem;border-radius:999px;color:#c8d8e1;font-weight:800;font-size:.88rem}}.pm-hero{{min-height:76vh;display:grid;place-items:center;background:radial-gradient(circle at 68% 25%,rgba(243,201,107,.17),transparent 25%),radial-gradient(circle at 25% 45%,rgba(92,231,255,.14),transparent 30%),linear-gradient(180deg,#061018,#0a1e2c)}}.pm-hero-in{{padding:6rem 0;text-align:center}}.pm-kicker{{text-transform:uppercase;letter-spacing:.16em;color:var(--pm-gold);font-size:.72rem;font-weight:1000}}h1{{font-size:clamp(4.1rem,10vw,8.5rem);line-height:.82;letter-spacing:-.075em;margin:1.1rem 0}}h1 span{{display:block;color:transparent;background:linear-gradient(90deg,var(--pm-cyan),#fff 48%,var(--pm-gold));background-clip:text}}.pm-lead{{font-size:clamp(1.25rem,2.3vw,1.7rem);line-height:1.5;max-width:900px;margin:auto;color:#d9e8ef}}.pm-law{{margin:1.7rem auto 0;max-width:760px;padding:1rem;border:1px solid rgba(255,255,255,.15);border-radius:18px;background:rgba(255,255,255,.05);font-weight:900}}.pm-section{{padding:6.5rem 0}}.pm-section.light{{background:var(--pm-ivory);color:#071522}}.pm-heading{{max-width:850px;margin-bottom:2.3rem}}.pm-heading h2{{font-size:clamp(2.4rem,5vw,4.6rem);line-height:.98;letter-spacing:-.055em;margin:.75rem 0}}.pm-heading p{{font-size:1.12rem;line-height:1.7;opacity:.78}}.pm-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}}.pm-card{{position:relative;overflow:hidden;padding:2.2rem;border-radius:28px;border:1px solid rgba(255,255,255,.15);background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025));min-height:440px;display:flex;flex-direction:column}}.light .pm-card{{background:#fff;border-color:rgba(5,16,24,.11);box-shadow:0 18px 60px rgba(7,21,34,.08)}}.pm-card:before{{content:"";position:absolute;width:230px;height:230px;border-radius:50%;right:-65px;top:-75px;background:radial-gradient(circle,rgba(92,231,255,.2),transparent 68%)}}.pm-card.m2:before{{background:radial-gradient(circle,rgba(243,201,107,.25),transparent 68%)}}.pm-num{{font-size:.72rem;letter-spacing:.15em;font-weight:1000;color:var(--pm-gold)}}.pm-card h3{{font-size:clamp(2.1rem,4vw,3.6rem);line-height:.98;letter-spacing:-.05em;margin:.8rem 0}}.pm-card p{{font-size:1.06rem;line-height:1.65;color:#c3d3dd}}.light .pm-card p{{color:#566b78}}.pm-status{{display:inline-flex;align-self:flex-start;margin-top:auto;padding:.6rem .8rem;border-radius:999px;border:1px solid rgba(255,255,255,.18);font-size:.72rem;font-weight:900;text-transform:uppercase;letter-spacing:.08em}}.light .pm-status{{border-color:rgba(5,16,24,.15)}}.pm-button{{display:inline-flex;align-self:flex-start;margin-top:1rem;padding:.75rem 1rem;border-radius:999px;text-decoration:none;font-weight:950;background:#071522;color:#fff}}.pm-ladder{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}.pm-step{{padding:1.5rem;border-radius:22px;background:#fff;border:1px solid rgba(5,16,24,.1)}}.pm-step strong{{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#071522;color:#fff}}.pm-step h3{{font-size:1.3rem;margin:1rem 0 .5rem}}.pm-step p{{color:#586c79;line-height:1.58}}.pm-stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.pm-stat{{padding:1.35rem;border:1px solid rgba(255,255,255,.15);border-radius:20px;background:rgba(255,255,255,.045)}}.pm-stat strong{{display:block;font-size:2.8rem;letter-spacing:-.05em}}.pm-stat span{{color:#b8cbd5;font-size:.84rem;font-weight:800}}.pm-footer{{padding:2rem 0;border-top:1px solid rgba(255,255,255,.12);color:#aebfca}}@media(max-width:800px){{.pm-grid,.pm-ladder,.pm-stats{{grid-template-columns:1fr}}.pm-links{{display:none}}.pm-card{{min-height:auto}}}}
</style></head><body><header class="pm-nav"><div class="pm-shell pm-navin"><a class="pm-brand" href="index.html">GoalOS AGIALPHA</a><nav class="pm-links"><a href="index.html">Home</a><a href="proof-gradient-challenge.html">Mission 001</a><a href="proof-mission-002.html">Mission 002</a><a href="{esc(content['repositoryUrl'])}" target="_blank" rel="noreferrer">GitHub ↗</a></nav></div></header><main><section class="pm-hero"><div class="pm-shell pm-hero-in"><div class="pm-kicker">GoalOS Public Program · Ethereum Mainnet</div><h1>THE PROOF <span>MISSIONS</span></h1><p class="pm-lead">A public program for turning autonomous work into capability that can survive evidence, transfer, settlement, institutional memory, and rollback.</p><div class="pm-law">A model can answer. An agent can act. An institution must prove—and a mature institution must prove that what it remembers can travel.</div></div></section><section class="pm-section"><div class="pm-shell"><div class="pm-heading"><div class="pm-kicker">The mission sequence</div><h2>Trust first. Transfer second. Composition only after proof.</h2><p>No mission inherits rights from ambition. Each stage earns a narrower, testable maturity claim.</p></div><div class="pm-grid"><article class="pm-card"><div class="pm-num">PUBLIC PROOF MISSION 001</div><h3>The Proof Gradient</h3><p>Can autonomous work earn the right to become capability through complete experiments, failed branches, reward-hack rejection, independent replay, validator decision, settlement, and Chronicle memory?</p><span class="pm-status">Protocol published · no result predeclared</span><a class="pm-button" href="proof-gradient-challenge.html">Enter Mission 001</a></article><article class="pm-card m2"><div class="pm-num">PUBLIC PROOF MISSION 002</div><h3>The Ascension Protocol</h3><p>Can one accepted capability survive a harder domain under half the original search budget, outperform memory-free search, abstain when unsupported, reproduce independently, and remain rollback-ready?</p><span class="pm-status">Protocol published · awaits Mission 001 capability</span><a class="pm-button" href="proof-mission-002.html">Enter Mission 002</a></article></div></div></section><section class="pm-section light"><div class="pm-shell"><div class="pm-heading"><div class="pm-kicker">The maturity ladder</div><h2>Proof earns propagation rights in stages.</h2><p>The public program deliberately separates task acceptance, transfer evidence, and future compositional maturity.</p></div><div class="pm-ladder"><article class="pm-step"><strong>01</strong><h3>Earn trust</h3><p>Mission 001 accepts only work that survives falsification, hidden evaluation, independent replay, and validator quorum.</p></article><article class="pm-step"><strong>02</strong><h3>Survive transfer</h3><p>Mission 002 tests whether the accepted capability accelerates a harder mission and correctly abstains outside its evidence.</p></article><article class="pm-step"><strong>03</strong><h3>Compose carefully</h3><p>A future mission may test multiple Transfer-Proven capabilities together. No compositional claim is made today.</p></article></div></div></section><section class="pm-section"><div class="pm-shell"><div class="pm-heading"><div class="pm-kicker">The deployed substrate</div><h2>The proof route is anchored in real Mainnet infrastructure.</h2><p>Infrastructure existence is public. Mission outcomes remain evidence-gated.</p></div><div class="pm-stats"><div class="pm-stat"><strong>48</strong><span>GoalOS-created Mainnet contracts</span></div><div class="pm-stat"><strong>48/48</strong><span>recorded source verification</span></div><div class="pm-stat"><strong>14/14</strong><span>configuration grants active</span></div><div class="pm-stat"><strong>0</strong><span>recorded verification failures</span></div></div></div></section></main><footer class="pm-footer"><div class="pm-shell">GoalOS AGIALPHA Ascension · The Proof Missions · Not externally audited · No mission result predeclared</div></footer><script src="assets/goalos-v86-dynamic-ai.js" defer></script></body></html>'''


def home_style() -> str:
    return f'''{STYLE_START}<style>
.ap-home{{position:relative;overflow:hidden;padding:6.8rem 0;background:radial-gradient(circle at 76% 35%,rgba(243,201,107,.19),transparent 24%),radial-gradient(circle at 19% 62%,rgba(124,228,192,.12),transparent 28%),linear-gradient(145deg,#061018,#0b2031);color:#eef7fb;border-top:1px solid rgba(255,255,255,.12);border-bottom:1px solid rgba(255,255,255,.12)}}.ap-home:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.032) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.032) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(90deg,#000,transparent)}}.ap-home-in{{position:relative;z-index:1;width:min(1180px,calc(100% - 2rem));margin:auto;display:grid;grid-template-columns:1.08fr .92fr;gap:3rem;align-items:center}}.ap-home-kicker{{text-transform:uppercase;letter-spacing:.15em;color:#f3c96b;font-size:.72rem;font-weight:1000}}.ap-home h2{{font-size:clamp(3rem,7vw,6.4rem);line-height:.88;letter-spacing:-.065em;margin:.8rem 0 1.2rem}}.ap-home h2 span{{color:transparent;background:linear-gradient(90deg,#f3c96b,#fff 52%,#7ce4c0);background-clip:text}}.ap-home p{{font-size:1.17rem;line-height:1.65;color:#cfe1e9;max-width:720px}}.ap-home-actions{{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.6rem}}.ap-home-actions a{{padding:.78rem 1rem;border:1px solid rgba(255,255,255,.22);border-radius:999px;text-decoration:none;font-weight:950;color:#fff}}.ap-home-actions a:first-child{{background:#f3c96b;color:#061018;border-color:transparent}}.ap-home-visual{{position:relative;aspect-ratio:1;border-radius:50%;border:1px solid rgba(255,255,255,.16);display:grid;place-items:center;background:radial-gradient(circle,rgba(243,201,107,.17),transparent 34%),rgba(255,255,255,.025);box-shadow:inset 0 0 80px rgba(124,228,192,.06)}}.ap-home-visual:before,.ap-home-visual:after{{content:"";position:absolute;border-radius:50%;border:1px solid rgba(255,255,255,.15)}}.ap-home-visual:before{{inset:11%}}.ap-home-visual:after{{inset:25%;border-color:rgba(124,228,192,.28)}}.ap-home-core{{width:36%;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;text-align:center;background:radial-gradient(circle at 35% 30%,#fff,#f3c96b 40%,#7ce4c0 80%);color:#061018;font-weight:1000;box-shadow:0 0 60px rgba(243,201,107,.34);z-index:2}}.ap-home-stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:.65rem;margin-top:1.4rem}}.ap-home-stat{{padding:.9rem;border:1px solid rgba(255,255,255,.14);border-radius:16px;background:rgba(255,255,255,.045)}}.ap-home-stat strong{{display:block;font-size:1.55rem;color:#fff}}.ap-home-stat span{{font-size:.78rem;color:#abc0cc}}@media(max-width:820px){{.ap-home-in{{grid-template-columns:1fr}}.ap-home-visual{{max-width:460px;margin:auto;width:100%}}}}@media(max-width:520px){{.ap-home{{padding:4.6rem 0}}.ap-home h2{{font-size:3.45rem}}.ap-home-actions a{{width:100%;text-align:center}}}}
</style>{STYLE_END}'''


def home_section() -> str:
    return f'''{START}<section class="ap-home"><div class="ap-home-in"><div><div class="ap-home-kicker">Public Proof Mission 002 · Capability Transfer</div><h2>THE ASCENSION <span>PROTOCOL</span></h2><p><strong>Where proven capability learns to travel.</strong> Mission 002 tests whether accepted capability can survive domain shift, outperform memory-free search under half the original budget, abstain when unsupported, reproduce independently, and remain rollback-ready.</p><div class="ap-home-stats"><div class="ap-home-stat"><strong>½ budget</strong><span>harder destination mission</span></div><div class="ap-home-stat"><strong>M2 target</strong><span>Transfer-Proven maturity</span></div><div class="ap-home-stat"><strong>2 replays</strong><span>independent reproduction required</span></div><div class="ap-home-stat"><strong>0 claims</strong><span>before completed evidence</span></div></div><div class="ap-home-actions"><a href="{PAGE}">Enter Mission 002</a><a href="{HUB}">Open the Proof Missions</a><a href="{PAGE}#mainnet">Inspect the Mainnet route</a></div></div><div class="ap-home-visual"><div class="ap-home-core">M1<br>→<br>M2</div></div></div></section>{END}'''


def replace_marked(text: str, start: str, end: str, replacement: str) -> str:
    return re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, text, flags=re.S)


def inject_homepage(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    style = home_style()
    section = home_section()
    if STYLE_START in raw:
        raw = replace_marked(raw, STYLE_START, STYLE_END, style)
    else:
        raw = raw.replace("</head>", style + "\n</head>", 1)
    if START in raw:
        raw = replace_marked(raw, START, END, section)
    elif MISSION1_END in raw:
        raw = raw.replace(MISSION1_END, MISSION1_END + "\n" + section, 1)
    else:
        anchor = "<section class='asi-section white'><div class='asi-wrap'><div class='asi-kicker'>World-launch command pages</div>"
        if anchor not in raw:
            fail("homepage insertion anchor not found")
        raw = raw.replace(anchor, section + "\n" + anchor, 1)
    path.write_text(raw, encoding="utf-8")


def write_downloads(site: Path, content: dict[str, Any], mainnet: dict[str, Any]) -> None:
    output = site / "downloads" / "proof-missions"
    output.mkdir(parents=True, exist_ok=True)
    dump(output / "public-proof-mission-002.json", content)
    passport = {
        "schemaVersion": "1.0",
        "missionId": content["missionId"],
        "capabilityId": "TO_BE_BOUND_AFTER_MISSION_001_ACCEPTANCE",
        "sourceClaimBoundary": [],
        "destinationShift": [],
        "requiredInvariants": [],
        "unsupportedConditions": [],
        "permittedTransferAdapters": [],
        "falsificationTriggers": [],
        "fallback": "FROZEN_DESTINATION_BASELINE",
        "rollbackTriggers": [],
        "lineageCommitments": [],
        "status": "TEMPLATE_NOT_EVIDENCE",
    }
    dump(output / "mission-002-assumption-passport-template.json", passport)
    contract_by_name = {entry["name"]: entry for entry in mainnet["contracts"]}
    with (output / "mission-002-proof-route.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sequence", "stage", "contract", "address", "purpose", "etherscan_url"])
        writer.writeheader()
        for item in content["proofRoute"]:
            contract = contract_by_name[item["contractName"]]
            writer.writerow(
                {
                    "sequence": item["sequence"],
                    "stage": item["stage"],
                    "contract": item["contractName"],
                    "address": contract["address"],
                    "purpose": item["purpose"],
                    "etherscan_url": contract["etherscanUrl"],
                }
            )


def add_sitemap(path: Path) -> None:
    urls = [
        "https://montrealai.github.io/goalos-agialpha-ascension/proof-missions.html",
        "https://montrealai.github.io/goalos-agialpha-ascension/proof-mission-002.html",
    ]
    raw = path.read_text(encoding="utf-8") if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>"
    for url in urls:
        if url not in raw:
            raw = raw.replace("</urlset>", f"<url><loc>{url}</loc></urlset>")
    path.write_text(raw, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--content", default="content/proof-mission-002-ascension-protocol.json")
    parser.add_argument("--mainnet", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()
    repo = Path.cwd()
    site = repo / args.site
    content_path = repo / args.content
    mainnet_path = repo / args.mainnet
    content = load(content_path)
    mainnet = load(mainnet_path)
    validate(content, mainnet)
    if not (site / "index.html").exists():
        fail("build the canonical v86 site first")
    if not (site / "proof-gradient-challenge.html").exists():
        fail("build Public Proof Mission 001 before Mission 002")
    (site / PAGE).write_text(page(content, mainnet), encoding="utf-8")
    (site / HUB).write_text(hub_page(content, mainnet), encoding="utf-8")
    inject_homepage(site / "index.html")
    write_downloads(site, content, mainnet)
    add_sitemap(site / "sitemap.xml")
    status_path = site / "site-status.json"
    status = load(status_path) if status_path.exists() else {}
    status["proofMission002"] = {
        "edition": "ASCENSION_PROTOCOL_V1",
        "missionId": content["missionId"],
        "page": PAGE,
        "hub": HUB,
        "status": content["status"],
        "resultPredeclared": False,
        "publicNetworkTransactionSent": False,
    }
    dump(status_path, status)
    dump(
        site / "qa" / "proof-mission-002-build.json",
        {
            "status": "PASS",
            "mode": "ADDITIVE_GENERATED_SITE_OVERLAY",
            "canonicalSourceModified": False,
            "newPages": [PAGE, HUB],
            "contentSha256": sha256(content_path),
            "mainnetDataSha256": sha256(mainnet_path),
            "goalosCreatedContracts": 48,
            "verified": 48,
            "failed": 0,
            "phaseBGrants": 14,
            "resultPredeclared": False,
            "publicCompetitorReferences": 0,
            "publicNetworkTransactionSent": False,
        },
    )
    print(json.dumps({"status": "PASS", "page": PAGE, "hub": HUB, "missionId": content["missionId"]}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI diagnostic
        print("ERROR:", exc, file=sys.stderr)
        raise SystemExit(1)
