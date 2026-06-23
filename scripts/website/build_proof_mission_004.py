#!/usr/bin/env python3
"""Generate GoalOS Public Proof Mission 004 as an additive website overlay.

The canonical v86 website source is never edited. This builder operates only
on the generated ``site`` directory after Missions 001–003 have been built.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

START = "<!-- GOALOS_PROOF_MISSION_004_START -->"
END = "<!-- GOALOS_PROOF_MISSION_004_END -->"
STYLE_START = "<!-- GOALOS_PROOF_MISSION_004_STYLE_START -->"
STYLE_END = "<!-- GOALOS_PROOF_MISSION_004_STYLE_END -->"
MISSION3_END = "<!-- GOALOS_PROOF_MISSION_003_END -->"
PROMOTION_START = "<!-- GOALOS_PROOF_MISSION_004_PROMOTION_START -->"
PROMOTION_END = "<!-- GOALOS_PROOF_MISSION_004_PROMOTION_END -->"
PAGE = "proof-mission-004.html"
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
    except Exception as exc:
        fail(f"cannot read {path}: {exc}")


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def validate(content: dict[str, Any], mainnet: dict[str, Any]) -> None:
    if content.get("missionId") != "GOALOS-PUBLIC-PROOF-MISSION-004":
        fail("wrong Mission 004 identifier")
    if content.get("sequence") != 4:
        fail("Mission 004 sequence must be 4")
    if content.get("status") != "PROTOCOL_PUBLISHED_AWAITING_ONE_COMPOSITION_PROVEN_CONSTELLATION":
        fail("unexpected Mission 004 status")
    if sum(int(item.get("share", 0)) for item in content.get("settlement", [])) != 100:
        fail("Mission 004 settlement shares must total 100")
    if len(content.get("proofRoute", [])) != 34:
        fail("Mission 004 proof route must contain 34 stages")
    if len(content.get("validators", [])) != 5:
        fail("Mission 004 requires five validators")
    if len(content.get("institutionalCampaign", {}).get("epochs", [])) != 5:
        fail("Mission 004 requires EPOCH_0 through EPOCH_4")
    budget = content.get("missionBudget", {})
    if budget.get("missionEpochs") != 4 or budget.get("challengeWindowHours") != 336:
        fail("Mission 004 budget/336-hour challenge policy mismatch")
    if content.get("mission5", {}).get("status") != "HORIZON_ONLY_NOT_YET_AUTHORIZED":
        fail("Mission 005 must remain a horizon only")
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


def institution_svg() -> str:
    epochs = [
        (250, 48, "E0", "CHARTER"),
        (450, 168, "E1", "ALLOCATE"),
        (403, 410, "E2", "STRESS"),
        (97, 410, "E3", "LEARN"),
        (50, 168, "E4", "RENEW"),
    ]
    spokes = "".join(f'<path d="M250 250 L{x} {y}"/>' for x, y, _, _ in epochs)
    nodes = "".join(
        f'<g class="si-epoch si-e{i}"><circle cx="{x}" cy="{y}" r="35"/><text class="id" x="{x}" y="{y-2}" text-anchor="middle">{eid}</text><text class="label" x="{x}" y="{y+15}" text-anchor="middle">{label}</text></g>'
        for i, (x, y, eid, label) in enumerate(epochs, 1)
    )
    return f'''<svg class="si-institution" viewBox="0 0 500 500" role="img" aria-label="A human-ratified mandate governing five institutional records"><defs><radialGradient id="siCore" cx="35%" cy="27%"><stop offset="0" stop-color="#fff"/><stop offset=".31" stop-color="#f4d98f"/><stop offset=".66" stop-color="#58e3c0"/><stop offset="1" stop-color="#071623"/></radialGradient><linearGradient id="siLine" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f2cb70"/><stop offset=".52" stop-color="#58e3c0"/><stop offset="1" stop-color="#70dcff"/></linearGradient><filter id="siGlow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><circle class="si-orbit outer" cx="250" cy="250" r="202"/><circle class="si-orbit mid" cx="250" cy="250" r="151"/><circle class="si-orbit inner" cx="250" cy="250" r="103"/><g class="si-spokes">{spokes}</g>{nodes}<g class="si-core" filter="url(#siGlow)"><path d="M250 164 315 201 315 277 250 314 185 277 185 201Z" fill="url(#siCore)"/><text x="250" y="223" text-anchor="middle">HUMAN</text><text x="250" y="247" text-anchor="middle">MANDATE</text><text class="m4" x="250" y="278" text-anchor="middle">M4</text></g><g class="si-rings-label"><text x="250" y="107" text-anchor="middle">PROOF-GOVERNED CAPITAL</text><text x="250" y="392" text-anchor="middle">REVIEW · ROLLBACK · RENEWAL</text></g></svg>'''


def critical_css() -> str:
    return r'''<style id="goalos-v86-critical">
:root{--si-night:#030711;--si-deep:#061521;--si-ink:#07121d;--si-ivory:#f8f4ea;--si-gold:#f2cb70;--si-mint:#58e3c0;--si-cyan:#70dcff;--si-violet:#a697ff;--si-rose:#ff9dac;--si-muted:#adbfca;--si-line:rgba(255,255,255,.14)}
*{box-sizing:border-box}.si-body{margin:0;background:var(--si-night);color:#eef7fb;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow-x:hidden}.si-body a{color:inherit}.si-skip{position:absolute;left:-999px;top:0}.si-skip:focus{left:1rem;top:1rem;z-index:999;background:#fff;color:#07121d;padding:.8rem 1rem;border-radius:999px}.si-shell{width:min(1220px,calc(100% - 2rem));margin:auto}.si-nav{position:sticky;top:0;z-index:100;background:rgba(3,7,17,.89);backdrop-filter:blur(22px);border-bottom:1px solid var(--si-line)}.si-navin{min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:1rem}.si-brand{text-decoration:none;font-weight:1000;letter-spacing:-.025em}.si-brand span{color:var(--si-gold)}.si-navlinks{display:flex;gap:.3rem;flex-wrap:wrap;justify-content:flex-end}.si-navlinks a{padding:.54rem .7rem;border-radius:999px;text-decoration:none;color:#c8d8e1;font-size:.82rem;font-weight:850}.si-navlinks a:hover,.si-navlinks a:focus{background:rgba(255,255,255,.09);color:#fff}.si-hero{min-height:calc(100vh - 72px);display:grid;place-items:center;position:relative;isolation:isolate;overflow:hidden;background:radial-gradient(circle at 78% 25%,rgba(88,227,192,.16),transparent 24%),radial-gradient(circle at 18% 45%,rgba(112,220,255,.12),transparent 29%),radial-gradient(circle at 53% 92%,rgba(242,203,112,.12),transparent 31%),linear-gradient(180deg,#02050d,#071521 56%,#0a2130)}.si-hero:before{content:"";position:absolute;inset:0;z-index:-2;background-image:radial-gradient(circle at center,rgba(255,255,255,.46) 0 1px,transparent 1.5px);background-size:77px 77px;opacity:.19;mask-image:linear-gradient(to bottom,#000,transparent 96%)}.si-hero:after{content:"";position:absolute;inset:-35%;z-index:-1;background:conic-gradient(from 150deg,transparent,rgba(88,227,192,.08),transparent 22%,rgba(112,220,255,.06),transparent 48%,rgba(242,203,112,.07),transparent 70%);animation:si-rotate 54s linear infinite}.si-hero-grid{display:grid;grid-template-columns:minmax(0,1.08fr) minmax(370px,.92fr);gap:4rem;align-items:center;padding:5.6rem 0}.si-kicker,.si-eyebrow{display:inline-flex;align-items:center;gap:.55rem;text-transform:uppercase;letter-spacing:.16em;font-size:.71rem;font-weight:1000;color:var(--si-gold)}.si-kicker:before,.si-eyebrow:before{content:"";width:30px;height:1px;background:currentColor}.si-hero h1{font-size:clamp(3.8rem,8.4vw,7.8rem);line-height:.83;letter-spacing:-.073em;margin:1.15rem 0 1.25rem}.si-hero h1 span{display:block;font-size:.61em;white-space:nowrap;letter-spacing:-.052em;color:transparent;background:linear-gradient(92deg,var(--si-gold),#fff 39%,var(--si-mint) 68%,var(--si-cyan));background-clip:text}.si-tagline{font-size:1.08rem;font-weight:1000;color:var(--si-gold);letter-spacing:.01em;margin:.2rem 0 1rem}.si-question{font-size:clamp(1.2rem,2.1vw,1.67rem);line-height:1.48;color:#e4edf3;max-width:800px}.si-manifesto{margin:1.5rem 0;padding:1rem 1.2rem;border-left:3px solid var(--si-mint);background:linear-gradient(90deg,rgba(88,227,192,.12),transparent);font-size:1.06rem;font-weight:900}.si-status{display:inline-flex;align-items:center;gap:.6rem;padding:.66rem .9rem;border:1px solid rgba(242,203,112,.33);background:rgba(242,203,112,.08);border-radius:999px;color:#f8dda0;font-size:.74rem;font-weight:950;text-transform:uppercase;letter-spacing:.08em}.si-status:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--si-gold);box-shadow:0 0 18px rgba(242,203,112,.85)}.si-actions{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1.8rem}.si-btn{display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:.78rem 1.08rem;border:1px solid rgba(255,255,255,.23);border-radius:999px;text-decoration:none;font-weight:950;background:rgba(255,255,255,.055);transition:.22s ease}.si-btn:hover,.si-btn:focus{transform:translateY(-2px);background:rgba(255,255,255,.11)}.si-btn.primary{background:linear-gradient(100deg,var(--si-gold),#f8e4af);color:#061018;border-color:transparent;box-shadow:0 0 38px rgba(242,203,112,.17)}.si-visual{position:relative;aspect-ratio:1;border-radius:50%;border:1px solid rgba(255,255,255,.15);background:radial-gradient(circle,rgba(88,227,192,.08),transparent 55%),rgba(255,255,255,.02);box-shadow:inset 0 0 110px rgba(112,220,255,.045),0 34px 110px rgba(0,0,0,.4);padding:4%}.si-institution{width:100%;height:100%;overflow:visible}.si-orbit{fill:none;stroke:#fff;stroke-opacity:.12;stroke-width:1}.si-orbit.mid{stroke:#58e3c0;stroke-opacity:.24;stroke-dasharray:3 9;animation:si-dash 22s linear infinite}.si-orbit.inner{stroke:#f2cb70;stroke-opacity:.33;stroke-dasharray:5 11;animation:si-dash 18s linear reverse infinite}.si-spokes path{stroke:url(#siLine);stroke-opacity:.36;stroke-width:1.5;stroke-dasharray:5 8;animation:si-dash 17s linear infinite}.si-epoch circle{fill:#071927;stroke:#d8e8ef;stroke-opacity:.5;stroke-width:1.3}.si-epoch text{fill:#eef8fb;font-weight:950}.si-epoch text.id{font-size:16px}.si-epoch text.label{font-size:8px;letter-spacing:.08em}.si-core text{fill:#061018;font-weight:1000;font-size:17px}.si-core text.m4{font-size:28px}.si-rings-label text{fill:#a9c1cc;font-size:8px;font-weight:900;letter-spacing:.16em}.si-section{padding:7rem 0;position:relative}.si-section.light{background:var(--si-ivory);color:#071521}.si-section.deep{background:#071521}.si-section.gold{background:linear-gradient(135deg,#f5d681,#e8b84d);color:#061018}.si-heading{max-width:950px;margin-bottom:2.6rem}.si-heading h2{font-size:clamp(2.45rem,5vw,4.9rem);line-height:.97;letter-spacing:-.056em;margin:.85rem 0}.si-heading p{font-size:1.15rem;line-height:1.72;opacity:.8}.si-constitution{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.si-law{padding:2rem;border:1px solid rgba(255,255,255,.15);border-radius:24px;background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025));font-size:clamp(1.22rem,2.2vw,1.7rem);font-weight:950;letter-spacing:-.035em}.si-architectures{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.si-architecture{padding:1.7rem;border-radius:24px;border:1px solid rgba(5,16,24,.11);background:#fff;box-shadow:0 16px 50px rgba(7,21,34,.07)}.si-architecture small{display:block;color:#8c6818;font-size:.7rem;font-weight:1000;letter-spacing:.12em}.si-architecture h3{font-size:1.45rem;margin:.55rem 0}.si-architecture p{color:#526776;line-height:1.62}.si-architecture.treatment{background:#071521;color:#fff;border-color:#071521;box-shadow:0 24px 70px rgba(7,21,33,.22)}.si-architecture.treatment p{color:#c1d2dd}.si-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:2rem}.si-metric{padding:1.35rem;border:1px solid rgba(5,16,24,.12);border-radius:20px;background:#fff}.si-metric strong{display:block;font-size:clamp(2rem,4vw,3.25rem);letter-spacing:-.05em}.si-metric span{color:#526776;font-size:.84rem;font-weight:800}.si-epochs{display:grid;gap:1rem}.si-epoch-row{display:grid;grid-template-columns:110px 1fr;gap:1.2rem;align-items:start;padding:1.5rem;border-radius:22px;background:#fff;border:1px solid rgba(5,16,24,.1);box-shadow:0 14px 42px rgba(7,21,33,.055)}.si-epoch-badge{display:grid;place-items:center;min-height:78px;border-radius:18px;background:linear-gradient(145deg,#071521,#0a3440);color:#fff;font-size:.8rem;font-weight:1000;letter-spacing:.08em}.si-epoch-row h3{font-size:1.4rem;margin:.15rem 0 .45rem}.si-epoch-row p{color:#526776;line-height:1.62;margin:0}.si-stack{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}.si-stack-card{padding:1.55rem;border-radius:22px;background:#fff;border:1px solid rgba(5,16,24,.1)}.si-stack-card b{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#071521;color:#fff}.si-stack-card h3{font-size:1.2rem;margin:1rem 0 .55rem}.si-stack-card p{color:#526776;line-height:1.58}.si-chain{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}.si-step{display:grid;grid-template-columns:54px 1fr;gap:1rem;padding:1.45rem;border-radius:22px;background:#fff;color:#071521;border:1px solid rgba(5,16,24,.1)}.si-step b{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:#071521;color:#fff}.si-step small{display:block;color:#0d8d78;font-weight:950;text-transform:uppercase;letter-spacing:.1em}.si-step h3{font-size:1.25rem;margin:.35rem 0}.si-step p{color:#526776;line-height:1.58;margin:.35rem 0 0}.si-gauntlet,.si-failure-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:.8rem}.si-failure{padding:1.2rem;border-radius:18px;background:#fff;border:1px solid rgba(5,16,24,.11)}.si-failure code{display:block;color:#087d69;font-weight:950;margin-bottom:.5rem}.si-failure p{margin:0;color:#526776;line-height:1.55}.si-acceptance{display:grid;gap:.75rem}.si-criterion{display:grid;grid-template-columns:42px 1fr;gap:1rem;align-items:start;padding:1.05rem;border:1px solid rgba(255,255,255,.14);border-radius:18px;background:rgba(255,255,255,.045)}.si-criterion b{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:var(--si-mint);color:#071521}.si-criterion p{margin:.4rem 0;color:#d4e2e8;line-height:1.55}.si-validators{display:grid;grid-template-columns:repeat(5,1fr);gap:.9rem}.si-validator{padding:1.35rem;border-radius:20px;background:#fff;border:1px solid rgba(5,16,24,.1)}.si-validator strong{font-size:2rem;color:#0d8d78}.si-validator h3{margin:.5rem 0}.si-validator p{color:#526776;line-height:1.55;font-size:.9rem}.si-settlement{display:grid;grid-template-columns:.8fr 1.2fr;gap:2rem;align-items:start}.si-treasury{position:relative;border-radius:28px;min-height:420px;display:grid;place-items:center;background:radial-gradient(circle,rgba(242,203,112,.2),transparent 43%),#071521;border:1px solid rgba(255,255,255,.15);overflow:hidden}.si-treasury:before,.si-treasury:after{content:"";position:absolute;border:1px solid rgba(88,227,192,.28);border-radius:50%}.si-treasury:before{width:270px;height:270px}.si-treasury:after{width:360px;height:360px;border-style:dashed;animation:si-rotate 30s linear infinite}.si-treasury-core{position:relative;z-index:2;width:170px;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;text-align:center;background:linear-gradient(145deg,#f8e5ae,#f2cb70);color:#071521;font-weight:1000;box-shadow:0 0 70px rgba(242,203,112,.3)}.si-shares{display:grid;gap:.62rem}.si-share{display:grid;grid-template-columns:68px 1fr;align-items:center;gap:.7rem}.si-share strong{font-size:1.2rem}.si-bar{padding:.7rem .85rem;border-radius:999px;background:linear-gradient(90deg,#0d8d78,#58e3c0);color:#061018;font-weight:900;min-width:max(42%,var(--w))}.si-ladder{display:grid;grid-template-columns:repeat(6,1fr);gap:.75rem}.si-level{padding:1.25rem;border:1px solid rgba(255,255,255,.14);border-radius:20px;background:rgba(255,255,255,.045)}.si-level strong{display:block;font-size:2rem;color:var(--si-gold)}.si-level h3{font-size:1rem;margin:.45rem 0}.si-level p{font-size:.83rem;color:#b8ccd6;line-height:1.5}.si-route-tools{display:flex;gap:.7rem;flex-wrap:wrap;margin-bottom:1.2rem}.si-route-tools input{min-width:min(100%,360px);padding:.8rem 1rem;border-radius:999px;border:1px solid rgba(5,16,24,.16);background:#fff;font:inherit}.si-route-count{padding:.8rem 1rem;border-radius:999px;background:#071521;color:#fff;font-weight:900}.si-route{display:grid;grid-template-columns:repeat(2,1fr);gap:.75rem}.si-route-item{display:grid;grid-template-columns:48px 1fr;gap:.9rem;padding:1.05rem;border-radius:18px;background:#fff;border:1px solid rgba(5,16,24,.1)}.si-route-num{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#071521;color:#fff;font-weight:1000}.si-route-item h3{font-size:1.03rem;margin:.1rem 0 .35rem}.si-route-item p{color:#526776;line-height:1.5;font-size:.88rem;margin:.2rem 0}.si-address{display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#087d69!important;font-size:.78rem;font-weight:900;text-decoration:none}.si-claim{padding:2rem;border-radius:26px;background:#fff;color:#071521}.si-claim ul{padding-left:1.25rem}.si-claim li{margin:.8rem 0;line-height:1.6;color:#435b69}.si-downloads{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.2rem}.si-downloads a{padding:.66rem .8rem;border:1px solid rgba(5,16,24,.15);border-radius:999px;text-decoration:none;font-size:.8rem;font-weight:900}.si-horizon{padding:2rem;border-radius:26px;border:1px solid rgba(7,18,29,.16);background:rgba(255,255,255,.28)}.si-footer{padding:2rem 0;color:#91a8b5;border-top:1px solid rgba(255,255,255,.12)}.si-hidden{display:none!important}@keyframes si-rotate{to{transform:rotate(360deg)}}@keyframes si-dash{to{stroke-dashoffset:-90}}
@media(max-width:1050px){.si-hero-grid{grid-template-columns:1fr}.si-visual{max-width:610px;width:100%;margin:auto}.si-stack{grid-template-columns:repeat(2,1fr)}.si-validators{grid-template-columns:repeat(3,1fr)}.si-ladder{grid-template-columns:repeat(3,1fr)}}
@media(max-width:760px){.si-navlinks{display:none}.si-section{padding:5rem 0}.si-constitution,.si-architectures,.si-chain,.si-gauntlet,.si-failure-grid,.si-route,.si-settlement{grid-template-columns:1fr}.si-metrics{grid-template-columns:repeat(2,1fr)}.si-validators{grid-template-columns:repeat(2,1fr)}.si-epoch-row{grid-template-columns:1fr}.si-epoch-badge{min-height:58px}.si-treasury{min-height:360px}}
@media(max-width:520px){.si-shell{width:min(100% - 1.15rem,1220px)}.si-hero-grid{padding:4.2rem 0;gap:2.4rem}.si-hero h1{font-size:3.65rem}.si-actions .si-btn{width:100%}.si-stack,.si-metrics,.si-validators,.si-ladder{grid-template-columns:1fr}.si-visual{padding:0}.si-route-tools input{min-width:100%}.si-section{padding:4.25rem 0}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.001ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important}}
</style>'''


def proof_route(content: dict[str, Any], mainnet: dict[str, Any]) -> str:
    by_name = {entry["name"]: entry for entry in mainnet["contracts"]}
    rows = []
    for item in content["proofRoute"]:
        contract = by_name[item["contractName"]]
        search = f"{item['stage']} {item['contractName']} {item['purpose']} {contract['address']}".lower()
        rows.append(f'''<article class="si-route-item" data-search="{esc(search)}"><div class="si-route-num">{item['sequence']}</div><div><h3>{esc(item['stage'])} · {esc(item['contractName'])}</h3><p>{esc(item['purpose'])}</p><a class="si-address" href="{esc(contract['etherscanUrl'])}" target="_blank" rel="noreferrer">{esc(contract['address'])} ↗</a></div></article>''')
    return "".join(rows)


def page(content: dict[str, Any], mainnet: dict[str, Any]) -> str:
    constitution = "".join(f'<article class="si-law">{esc(x)}</article>' for x in content["constitution"])
    architectures = "".join(f'''<article class="si-architecture {'treatment' if x['id'].startswith('TREATMENT') else ''}"><small>{esc(x['id'])}</small><h3>{esc(x['title'])}</h3><p>{esc(x['copy'])}</p></article>''' for x in content["controlArchitectures"])
    epochs = "".join(f'''<article class="si-epoch-row"><div class="si-epoch-badge">{esc(x['id'])}</div><div><h3>{esc(x['title'])}</h3><p>{esc(x['copy'])}</p></div></article>''' for x in content["institutionalCampaign"]["epochs"])
    stack = "".join(f'''<article class="si-stack-card"><b>{i:02d}</b><h3>{esc(x['title'])}</h3><p>{esc(x['copy'])}</p></article>''' for i, x in enumerate(content["sovereigntyStack"], 1))
    chain = "".join(f'''<article class="si-step"><b>{i:02d}</b><div><small>{esc(x['stage'])}</small><h3>{esc(x['title'])}</h3><p>{esc(x['copy'])}</p></div></article>''' for i, x in enumerate(content["proofChain"], 1))
    stress = "".join(f'''<article class="si-failure"><code>{esc(x['code'])}</code><p>{esc(x['copy'])}</p></article>''' for x in content["stressGauntlet"])
    failures = "".join(f'''<article class="si-failure"><code>{esc(x['code'])}</code><p>{esc(x['copy'])}</p></article>''' for x in content["failureAtlas"])
    acceptance = "".join(f'''<article class="si-criterion"><b>{i}</b><p>{esc(x)}</p></article>''' for i, x in enumerate(content["acceptance"], 1))
    validators = "".join(f'''<article class="si-validator"><strong>{esc(x['id'])}</strong><h3>{esc(x['title'])}</h3><p>{esc(x['copy'])}</p></article>''' for x in content["validators"])
    settlement = "".join(f'''<div class="si-share"><strong>{int(x['share'])}%</strong><div class="si-bar" style="--w:{max(14, int(x['share']) * 3.25)}%">{esc(x['label'])}</div></div>''' for x in content["settlement"])
    ladder = "".join(f'''<article class="si-level"><strong>{esc(x['level'])}</strong><h3>{esc(x['title'])}</h3><p>{esc(x['copy'])}</p></article>''' for x in content["maturityLadder"])
    claims = "".join(f'<li>{esc(x)}</li>' for x in content["claimBoundary"])
    route = proof_route(content, mainnet)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Public Proof Mission 004 — The Sovereign Institution | GoalOS</title><meta name="description" content="Can a Composition-Proven constellation operate through repeated mission epochs under proof-budgeted capital, explicit human mandate, independent challenge, succession, and rollback?"><meta property="og:title" content="The Sovereign Institution — GoalOS Public Proof Mission 004"><meta property="og:description" content="Where governed intelligence learns to endure."><meta property="og:type" content="website"><meta name="theme-color" content="#061521"><link rel="stylesheet" href="assets/goalos-v86-preserve.css">{critical_css()}</head><body class="si-body"><a class="si-skip" href="#mission">Skip to mission</a><header class="si-nav"><div class="si-shell si-navin"><a class="si-brand" href="index.html">GoalOS <span>AGIALPHA</span></a><nav class="si-navlinks" aria-label="Mission navigation"><a href="proof-missions.html">Proof Missions</a><a href="proof-gradient-challenge.html">Mission 001</a><a href="proof-mission-002.html">Mission 002</a><a href="proof-mission-003.html">Mission 003</a><a href="#mainnet">Mainnet route</a><a href="{esc(content['releaseUrl'])}" target="_blank" rel="noreferrer">Release ↗</a></nav></div></header><main id="mission"><section class="si-hero"><div class="si-shell si-hero-grid"><div><div class="si-kicker">{esc(content['kicker'])}</div><h1>THE SOVEREIGN <span>INSTITUTION</span></h1><p class="si-tagline">{esc(content['subtitle'])}</p><p class="si-question">{esc(content['heroQuestion'])}</p><div class="si-manifesto">{esc(content['manifesto'])}</div><span class="si-status">Protocol published · awaiting one Composition-Proven constellation</span><div class="si-actions"><a class="si-btn primary" href="#campaign">Enter the sovereignty trial</a><a class="si-btn" href="proof-missions.html">Open all Proof Missions</a><a class="si-btn" href="#mainnet">Inspect the Mainnet route</a></div></div><div class="si-visual">{institution_svg()}</div></div></section>
<section class="si-section deep"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The constitution</div><h2>Authority is borrowed. Proof is continuous. Renewal is earned.</h2><p>{esc(content['publicThesis'])}</p></div><div class="si-constitution">{constitution}</div></div></section>
<section class="si-section light" id="campaign"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The institutional experiment</div><h2>Same constellation. Three architectures. One question: which can endure?</h2><p>{esc(content['objective'])}</p></div><div class="si-architectures">{architectures}</div><div class="si-metrics"><article class="si-metric"><strong>4</strong><span>operating mission epochs</span></article><article class="si-metric"><strong>240h</strong><span>maximum GPU-equivalent budget</span></article><article class="si-metric"><strong>5</strong><span>independent validators</span></article><article class="si-metric"><strong>14 days</strong><span>public challenge window</span></article></div></div></section>
<section class="si-section light"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The Four-Epoch Sovereignty Trial</div><h2>Found. Allocate. Survive. Learn. Earn renewal—or end.</h2><p>{esc(content['institutionalCampaign']['brief'])}</p></div><div class="si-epochs">{epochs}</div></div></section>
<section class="si-section light"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The sovereignty stack</div><h2>An institution is not a larger agent. It is bounded authority made auditable.</h2></div><div class="si-stack">{stack}</div></div></section>
<section class="si-section light"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The proof chain</div><h2>Every epoch must remain reconstructible from mandate to renewal.</h2></div><div class="si-chain">{chain}</div></div></section>
<section class="si-section light"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The institutional stress gauntlet</div><h2>Mission 004 attacks governance, capital, continuity, and legitimacy.</h2><p>Success requires safe continuation or explicit abstention. Silent degradation is failure.</p></div><div class="si-gauntlet">{stress}</div><div style="height:3rem"></div><div class="si-heading"><div class="si-eyebrow">The failure atlas</div><h2>Institutional failure must become visible before it becomes permanent.</h2></div><div class="si-failure-grid">{failures}</div></div></section>
<section class="si-section deep"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">Acceptance standard</div><h2>M4 is earned only by repeated proof-governed operation.</h2><p>No single benchmark, deployment, website, or treasury event can satisfy this mission.</p></div><div class="si-acceptance">{acceptance}</div></div></section>
<section class="si-section light"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">Five-validator council</div><h2>No institution may certify itself.</h2></div><div class="si-validators">{validators}</div></div></section>
<section class="si-section light"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">Proof-budgeted settlement</div><h2>Capital follows accepted work—and always remembers its obligations.</h2><p>Settlement remains conditional on mission acceptance, replay, challenge closure, exact accounting, and a valid human mandate.</p></div><div class="si-settlement"><div class="si-treasury"><div class="si-treasury-core">PROOF<br>BUDGET<br>THERMOSTAT</div></div><div class="si-shares">{settlement}</div></div></div></section>
<section class="si-section deep"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">The maturity ladder</div><h2>Capability becomes institution only through narrower, cumulative proof.</h2></div><div class="si-ladder">{ladder}</div></div></section>
<section class="si-section light" id="mainnet"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">Ethereum Mainnet proof route</div><h2>Thirty-four institutional stages mapped to deployed GoalOS infrastructure.</h2><p>The recorded deployment contains 48 GoalOS-created contracts, 48/48 source verification, 14 configured grants, and a passing 48-contract postcheck. Infrastructure existence is public. Mission 004 outcomes remain evidence-gated.</p></div><div class="si-route-tools"><input id="si-route-search" type="search" placeholder="Search stage, contract, purpose, or address" aria-label="Search Mission 004 Mainnet proof route"><span class="si-route-count"><span id="si-route-visible">34</span> / 34 stages</span></div><div class="si-route">{route}</div></div></section>
<section class="si-section gold"><div class="si-shell"><div class="si-heading"><div class="si-eyebrow">Claim boundary</div><h2>Grand ambition. Exact language. No result predeclared.</h2></div><article class="si-claim"><ul>{claims}</ul><div class="si-downloads"><a href="downloads/proof-missions/public-proof-mission-004.json">Mission 004 JSON</a><a href="downloads/proof-missions/mission-004-institution-charter-template.json">Institution charter template</a><a href="downloads/proof-missions/mission-004-epoch-ledger-template.json">Epoch ledger template</a><a href="downloads/proof-missions/mission-004-treasury-policy-template.json">Treasury policy template</a><a href="downloads/proof-missions/mission-004-incident-recovery-template.json">Incident & recovery template</a><a href="downloads/proof-missions/mission-004-proof-route.csv">Mainnet route CSV</a></div></article><div style="height:2rem"></div><article class="si-horizon"><strong>MISSION 005 HORIZON</strong><h2 style="font-size:clamp(2rem,4vw,3.6rem);margin:.7rem 0">{esc(content['mission5']['title'])}</h2><p style="font-size:1.12rem;line-height:1.7;color:#19303c">{esc(content['mission5']['copy'])}</p><span class="si-status" style="color:#071521;border-color:rgba(7,18,29,.25);background:rgba(255,255,255,.28)">Horizon only · not authorized</span></article></div></section></main><footer class="si-footer"><div class="si-shell">GoalOS AGIALPHA Ascension · Public Proof Mission 004 · Not externally audited · No institutional result predeclared</div></footer><script src="assets/goalos-v86-dynamic-ai.js" defer></script><script>const q=document.getElementById('si-route-search'),items=[...document.querySelectorAll('.si-route-item')],visible=document.getElementById('si-route-visible');if(q)q.addEventListener('input',()=>{{const s=q.value.trim().toLowerCase();let n=0;items.forEach(x=>{{const show=!s||x.dataset.search.includes(s);x.classList.toggle('si-hidden',!show);if(show)n++}});visible.textContent=n}});</script></body></html>'''


def hub_page(content: dict[str, Any]) -> str:
    cards = [
        ("001", "The Proof Gradient", "Turn autonomous output into accepted capability through falsification, replay, validator decision, settlement, and Chronicle memory.", "proof-gradient-challenge.html", "M1 · Accepted"),
        ("002", "The Ascension Protocol", "Test whether accepted capability survives a harder domain, a lower budget, abstention, independent replay, and rollback.", "proof-mission-002.html", "M2 · Transfer-Proven"),
        ("003", "The Capability Constellation", "Test whether multiple Transfer-Proven capabilities compose safely through interfaces, fault domains, attribution, and collective replay.", "proof-mission-003.html", "M3 · Composition-Proven"),
        ("004", "The Sovereign Institution", "Test whether one Composition-Proven constellation can operate through repeated mandates, proof-budgeted capital, shocks, succession, replay, and human renewal.", PAGE, "M4 · Institution-Proven"),
    ]
    card_html = "".join(f'''<article class="pm-card m{n[-1]}"><div class="pm-num">PUBLIC PROOF MISSION {n}</div><h3>{esc(t)}</h3><p>{esc(c)}</p><span class="pm-status">{esc(level)}</span><a class="pm-button" href="{u}">Enter Mission {n[-1]}</a></article>''' for n, t, c, u, level in cards)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Proof Missions | GoalOS AGIALPHA Ascension</title><meta name="description" content="The GoalOS Public Proof Missions: acceptance, transfer, safe composition, and time-bounded institutional operation."><meta name="theme-color" content="#061521"><link rel="stylesheet" href="assets/goalos-v86-preserve.css"><style id="goalos-v86-critical">:root{{--pm-bg:#040812;--pm-ink:#071521;--pm-gold:#f2cb70;--pm-mint:#58e3c0;--pm-cyan:#70dcff;--pm-violet:#a697ff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pm-bg);color:#eef7fb;font-family:Inter,system-ui,sans-serif}}a{{color:inherit}}.pm-shell{{width:min(1180px,calc(100% - 2rem));margin:auto}}.pm-nav{{position:sticky;top:0;z-index:10;background:rgba(4,8,18,.88);backdrop-filter:blur(18px);border-bottom:1px solid rgba(255,255,255,.13)}}.pm-navin{{min-height:70px;display:flex;align-items:center;justify-content:space-between;gap:1rem}}.pm-brand{{font-weight:1000;text-decoration:none}}.pm-brand span{{color:var(--pm-gold)}}.pm-links{{display:flex;gap:.42rem;flex-wrap:wrap}}.pm-links a{{font-size:.8rem;text-decoration:none;color:#c6d7df;padding:.55rem .64rem;border-radius:999px}}.pm-links a:hover{{background:rgba(255,255,255,.08);color:#fff}}.pm-hero{{padding:8rem 0 6rem;position:relative;overflow:hidden;background:radial-gradient(circle at 75% 28%,rgba(88,227,192,.17),transparent 24%),radial-gradient(circle at 20% 68%,rgba(166,151,255,.14),transparent 28%),linear-gradient(160deg,#030610,#0a2030)}}.pm-hero:before{{content:"";position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.45) 0 1px,transparent 1.5px);background-size:74px 74px;opacity:.15}}.pm-hero-in{{position:relative;z-index:1}}.pm-kicker{{color:var(--pm-gold);font-size:.72rem;text-transform:uppercase;letter-spacing:.15em;font-weight:1000}}.pm-hero h1{{font-size:clamp(4rem,10vw,8.5rem);line-height:.82;letter-spacing:-.075em;margin:1rem 0}}.pm-hero h1 span{{display:block;color:transparent;background:linear-gradient(90deg,var(--pm-gold),#fff 40%,var(--pm-mint),var(--pm-cyan));background-clip:text}}.pm-lead{{max-width:930px;font-size:clamp(1.2rem,2.2vw,1.65rem);line-height:1.55;color:#d6e4ea}}.pm-law{{margin-top:2rem;max-width:960px;padding:1.1rem 1.25rem;border-left:3px solid var(--pm-mint);background:linear-gradient(90deg,rgba(88,227,192,.12),transparent);font-weight:900;line-height:1.55}}.pm-section{{padding:6.5rem 0}}.pm-section.light{{background:#f8f4ea;color:#071521}}.pm-heading{{max-width:920px;margin-bottom:2.5rem}}.pm-heading h2{{font-size:clamp(2.5rem,5vw,4.8rem);line-height:.98;letter-spacing:-.055em;margin:.75rem 0}}.pm-heading p{{font-size:1.12rem;line-height:1.7;color:#aebfcc}}.light .pm-heading p{{color:#526776}}.pm-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}}.pm-card{{position:relative;overflow:hidden;min-height:410px;padding:2rem;border:1px solid rgba(255,255,255,.14);border-radius:28px;background:radial-gradient(circle at 90% 10%,rgba(242,203,112,.16),transparent 28%),rgba(255,255,255,.045);display:flex;flex-direction:column}}.pm-card.m2{{background:radial-gradient(circle at 90% 10%,rgba(88,227,192,.16),transparent 28%),rgba(255,255,255,.045)}}.pm-card.m3{{background:radial-gradient(circle at 90% 10%,rgba(166,151,255,.19),transparent 28%),rgba(255,255,255,.045)}}.pm-card.m4{{background:radial-gradient(circle at 90% 10%,rgba(112,220,255,.2),transparent 28%),linear-gradient(145deg,rgba(88,227,192,.08),rgba(255,255,255,.045));border-color:rgba(242,203,112,.3)}}.pm-num{{font-size:.72rem;font-weight:1000;letter-spacing:.14em;color:var(--pm-gold)}}.pm-card h3{{font-size:clamp(2rem,4vw,3.2rem);line-height:.94;letter-spacing:-.05em;margin:.8rem 0}}.pm-card p{{color:#c3d4dc;line-height:1.67;font-size:1.02rem}}.pm-status{{display:inline-flex;align-self:flex-start;margin-top:auto;padding:.55rem .7rem;border:1px solid rgba(255,255,255,.16);border-radius:999px;color:#c9dbe3;font-size:.72rem;font-weight:900}}.pm-button{{display:inline-flex;align-self:flex-start;margin-top:1rem;padding:.72rem .9rem;border-radius:999px;text-decoration:none;background:#fff;color:#071521;font-weight:950}}.pm-ladder{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.pm-step{{padding:1.5rem;border-radius:22px;background:#fff;border:1px solid rgba(5,16,24,.1)}}.pm-step strong{{font-size:2.2rem;color:#0d8d78}}.pm-step h3{{font-size:1.25rem;margin:.5rem 0}}.pm-step p{{color:#526776;line-height:1.58}}.pm-stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.pm-stat{{padding:1.4rem;border:1px solid rgba(255,255,255,.14);border-radius:20px;background:rgba(255,255,255,.045)}}.pm-stat strong{{display:block;font-size:2.8rem;letter-spacing:-.05em}}.pm-stat span{{color:#b9cdd7;font-size:.82rem;font-weight:800}}.pm-horizon{{padding:2.2rem;border:1px solid rgba(255,255,255,.16);border-radius:28px;background:linear-gradient(145deg,rgba(255,255,255,.07),rgba(255,255,255,.025))}}.pm-horizon h3{{font-size:clamp(2.5rem,5vw,4.8rem);letter-spacing:-.05em;margin:.7rem 0}}.pm-horizon p{{max-width:900px;color:#c4d6df;line-height:1.7}}.pm-footer{{padding:2rem 0;border-top:1px solid rgba(255,255,255,.12);color:#91a7b3}}@media(max-width:850px){{.pm-grid,.pm-ladder,.pm-stats{{grid-template-columns:1fr 1fr}}}}@media(max-width:560px){{.pm-links{{display:none}}.pm-grid,.pm-ladder,.pm-stats{{grid-template-columns:1fr}}.pm-hero{{padding:5.5rem 0 4rem}}.pm-card{{min-height:auto}}}}</style></head><body><header class="pm-nav"><div class="pm-shell pm-navin"><a class="pm-brand" href="index.html">GoalOS <span>AGIALPHA</span></a><nav class="pm-links"><a href="proof-gradient-challenge.html">Mission 001</a><a href="proof-mission-002.html">Mission 002</a><a href="proof-mission-003.html">Mission 003</a><a href="proof-mission-004.html">Mission 004</a><a href="{esc(content['repositoryUrl'])}" target="_blank" rel="noreferrer">GitHub ↗</a></nav></div></header><main><section class="pm-hero"><div class="pm-shell pm-hero-in"><div class="pm-kicker">GoalOS Public Program · Ethereum Mainnet</div><h1>THE PROOF <span>MISSIONS</span></h1><p class="pm-lead">A public program for turning autonomous work into accepted capability, transfer evidence, safe composition, and time-bounded institutional operation.</p><div class="pm-law">A model can answer. An agent can act. An institution must prove—and a mature institution must prove that it can allocate capital, survive challenge, transfer authority, remember correctly, and stop.</div></div></section><section class="pm-section"><div class="pm-shell"><div class="pm-heading"><div class="pm-kicker">The mission sequence</div><h2>Trust. Transfer. Composition. Institution. No maturity without proof.</h2><p>Each mission earns one narrower propagation right. None inherits credibility from ambition.</p></div><div class="pm-grid">{card_html}</div></div></section><section class="pm-section light"><div class="pm-shell"><div class="pm-heading"><div class="pm-kicker">The maturity ladder</div><h2>Proof earns propagation rights in stages.</h2><p>Task acceptance, transfer evidence, safe composition, and institutional continuity remain separate claims.</p></div><div class="pm-ladder"><article class="pm-step"><strong>01</strong><h3>Earn trust</h3><p>Mission 001 accepts only work that survives falsification, hidden evaluation, independent replay, and validator quorum.</p></article><article class="pm-step"><strong>02</strong><h3>Survive transfer</h3><p>Mission 002 tests whether accepted capability accelerates a harder mission and abstains outside its evidence.</p></article><article class="pm-step"><strong>03</strong><h3>Compose safely</h3><p>Mission 003 tests interfaces, shared memory, fault domains, attribution, full replay, and rollback across multiple capabilities.</p></article><article class="pm-step"><strong>04</strong><h3>Operate institutionally</h3><p>Mission 004 tests repeated epochs, proof-budgeted capital, shocks, succession, human renewal, and dignified termination.</p></article></div></div></section><section class="pm-section"><div class="pm-shell"><div class="pm-heading"><div class="pm-kicker">The deployed substrate</div><h2>The proof routes are anchored in real Mainnet infrastructure.</h2><p>Infrastructure existence is public. Mission outcomes remain evidence-gated.</p></div><div class="pm-stats"><div class="pm-stat"><strong>48</strong><span>GoalOS-created Mainnet contracts</span></div><div class="pm-stat"><strong>48/48</strong><span>recorded source verification</span></div><div class="pm-stat"><strong>14/14</strong><span>configuration grants active</span></div><div class="pm-stat"><strong>0</strong><span>recorded verification failures</span></div></div></div></section><section class="pm-section"><div class="pm-shell"><div class="pm-horizon"><div class="pm-kicker">Mission 005 horizon</div><h3>{esc(content['mission5']['title'])}</h3><p>{esc(content['mission5']['copy'])}</p><p><strong>Status:</strong> horizon only; not yet authorized.</p></div></div></section></main><footer class="pm-footer"><div class="pm-shell">GoalOS AGIALPHA Ascension · The Proof Missions · Not externally audited · No mission result predeclared</div></footer><script src="assets/goalos-v86-dynamic-ai.js" defer></script></body></html>'''


def home_style() -> str:
    return f'''{STYLE_START}<style>.si-home{{position:relative;overflow:hidden;padding:7.1rem 0;background:radial-gradient(circle at 78% 27%,rgba(88,227,192,.18),transparent 25%),radial-gradient(circle at 18% 68%,rgba(112,220,255,.1),transparent 30%),radial-gradient(circle at 54% 90%,rgba(242,203,112,.11),transparent 24%),linear-gradient(145deg,#030711,#0a1d30);color:#eef7fb;border-top:1px solid rgba(255,255,255,.12);border-bottom:1px solid rgba(255,255,255,.12)}}.si-home:before{{content:"";position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.42) 0 1px,transparent 1.5px);background-size:61px 61px;opacity:.15}}.si-home-in{{position:relative;z-index:1;width:min(1180px,calc(100% - 2rem));margin:auto;display:grid;grid-template-columns:1.05fr .95fr;gap:3rem;align-items:center}}.si-home-kicker{{text-transform:uppercase;letter-spacing:.16em;color:#f2cb70;font-size:.72rem;font-weight:1000}}.si-home h2{{font-size:clamp(3rem,7vw,6.3rem);line-height:.87;letter-spacing:-.068em;margin:.8rem 0 1.2rem}}.si-home h2 span{{display:block;font-size:.63em;white-space:nowrap;color:transparent;background:linear-gradient(90deg,#f2cb70,#fff 44%,#58e3c0,#70dcff);background-clip:text}}.si-home p{{font-size:1.16rem;line-height:1.65;color:#cddde5;max-width:720px}}.si-home-law{{font-family:Georgia,serif;font-size:1.18rem;font-style:italic;color:#f4dc9c;margin:1rem 0}}.si-home-actions{{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.55rem}}.si-home-actions a{{padding:.78rem 1rem;border:1px solid rgba(255,255,255,.22);border-radius:999px;text-decoration:none;font-weight:950;color:#fff}}.si-home-actions a:first-child{{background:#f2cb70;color:#061018;border-color:transparent}}.si-home-visual{{position:relative;aspect-ratio:1;border-radius:50%;border:1px solid rgba(255,255,255,.16);display:grid;place-items:center;background:radial-gradient(circle,rgba(88,227,192,.15),transparent 37%),rgba(255,255,255,.025);box-shadow:inset 0 0 95px rgba(112,220,255,.055)}}.si-home-core{{width:34%;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;text-align:center;background:radial-gradient(circle at 35% 30%,#fff,#f2cb70 38%,#58e3c0 74%,#071426);color:#07121d;font-weight:1000;box-shadow:0 0 62px rgba(242,203,112,.31);z-index:2}}.si-home-orbit{{position:absolute;inset:9%;border:1px dashed rgba(255,255,255,.25);border-radius:50%}}.si-home-orbit.o2{{inset:21%;border-color:rgba(242,203,112,.28)}}.si-home-node{{position:absolute;width:64px;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;background:#071426;border:1px solid rgba(255,255,255,.22);font-size:.68rem;font-weight:950}}.si-home-node.n1{{top:5%;left:42%}}.si-home-node.n2{{right:8%;top:30%}}.si-home-node.n3{{right:15%;bottom:14%}}.si-home-node.n4{{left:15%;bottom:14%}}.si-home-node.n5{{left:8%;top:30%}}.si-home-stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:.65rem;margin-top:1.35rem}}.si-home-stat{{padding:.9rem;border:1px solid rgba(255,255,255,.14);border-radius:16px;background:rgba(255,255,255,.045)}}.si-home-stat strong{{display:block;font-size:1.55rem;color:#fff}}.si-home-stat span{{font-size:.78rem;color:#abc0cc}}@media(max-width:820px){{.si-home-in{{grid-template-columns:1fr}}.si-home-visual{{max-width:460px;margin:auto;width:100%}}}}@media(max-width:520px){{.si-home{{padding:4.7rem 0}}.si-home h2{{font-size:3.3rem}}.si-home-actions a{{width:100%;text-align:center}}}}</style>{STYLE_END}'''


def home_section() -> str:
    return f'''{START}<section class="si-home"><div class="si-home-in"><div><div class="si-home-kicker">Public Proof Mission 004 · Institutional Continuity</div><h2>THE SOVEREIGN <span>INSTITUTION</span></h2><p><strong>Where governed intelligence learns to endure.</strong> Mission 004 tests whether one Composition-Proven constellation can complete repeated mission epochs, allocate bounded capital, survive shocks and succession, improve through accepted memory, and still remain under explicit human renewal and rollback.</p><div class="si-home-law">No mandate, no mission. No capital without proof. No evolution beyond review and rollback.</div><div class="si-home-stats"><div class="si-home-stat"><strong>4 epochs</strong><span>proof-governed operating cycles</span></div><div class="si-home-stat"><strong>240h</strong><span>maximum compute envelope</span></div><div class="si-home-stat"><strong>5 validators</strong><span>independent institutional quorum</span></div><div class="si-home-stat"><strong>34 stages</strong><span>Ethereum Mainnet proof route</span></div></div><div class="si-home-actions"><a href="{PAGE}">Enter Mission 004</a><a href="{HUB}">Open the Proof Missions</a><a href="{PAGE}#mainnet">Inspect the Mainnet route</a></div></div><div class="si-home-visual"><div class="si-home-orbit"></div><div class="si-home-orbit o2"></div><div class="si-home-core">M4<br>INSTITUTION</div><div class="si-home-node n1">E0</div><div class="si-home-node n2">E1</div><div class="si-home-node n3">E2</div><div class="si-home-node n4">E3</div><div class="si-home-node n5">E4</div></div></div></section>{END}'''


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
    elif MISSION3_END in raw:
        raw = raw.replace(MISSION3_END, MISSION3_END + "\n" + section, 1)
    else:
        fail("Mission 003 homepage marker not found; build Missions 001–003 first")
    path.write_text(raw, encoding="utf-8")


def update_mission3_horizon(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    active = f'''{PROMOTION_START}<div class="cc-horizon"><div class="cc-eyebrow">PUBLIC PROOF MISSION 004 · NOW PUBLISHED</div><h3>The Sovereign Institution</h3><p>Mission 004 now publishes the protocol for repeated mission epochs, proof-budgeted capital, institutional shocks, succession, independent replay, human renewal, and safe termination.</p><p><a class="cc-btn primary" href="proof-mission-004.html">Enter Mission 004</a></p></div>{PROMOTION_END}'''
    if PROMOTION_START in raw:
        raw = replace_marked(raw, PROMOTION_START, PROMOTION_END, active)
    else:
        pattern = r'<div class="cc-horizon"><div class="cc-eyebrow">The next horizon</div><h3>The Sovereign Institution</h3>.*?</div>'
        changed, count = re.subn(pattern, active, raw, count=1, flags=re.S)
        if count != 1:
            fail("Mission 003 horizon block not found")
        raw = changed
    path.write_text(raw, encoding="utf-8")


def write_downloads(site: Path, content: dict[str, Any], mainnet: dict[str, Any]) -> None:
    out = site / "downloads" / "proof-missions"
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "public-proof-mission-004.json", content)
    dump(out / "mission-004-institution-charter-template.json", {
        "schemaVersion": "1.0", "missionId": content["missionId"], "institutionId": "TO_BE_ASSIGNED",
        "humanMandateRoot": "TO_BE_COMMITTED", "authorityGraph": [], "missionClasses": [],
        "treasuryPolicy": {}, "riskLimits": {}, "validatorCouncil": {}, "emergencyPowers": {},
        "successionPlan": {}, "expiresAt": "TO_BE_SET", "status": "TEMPLATE_NOT_EVIDENCE"
    })
    dump(out / "mission-004-epoch-ledger-template.json", {
        "schemaVersion": "1.0", "missionId": content["missionId"], "epochId": "EPOCH_TO_BE_ASSIGNED",
        "objectiveCommitment": "TO_BE_COMMITTED", "budget": {}, "capabilityRoster": [],
        "claimBoundary": [], "acceptance": [], "challengeWindow": {}, "rollbackPlan": {},
        "decision": "NOT_RUN", "status": "TEMPLATE_NOT_EVIDENCE"
    })
    dump(out / "mission-004-treasury-policy-template.json", {
        "schemaVersion": "1.0", "missionId": content["missionId"], "currency": "AGIALPHA_OR_DECLARED_UNIT",
        "maximumInstitutionalBudget": "TO_BE_COMMITTED", "purposeRestrictions": [], "riskCeilings": {},
        "reserves": {}, "settlementPolicy": {}, "reconciliation": {}, "status": "TEMPLATE_NOT_EVIDENCE"
    })
    dump(out / "mission-004-incident-recovery-template.json", {
        "schemaVersion": "1.0", "missionId": content["missionId"], "incidentId": "TO_BE_ASSIGNED",
        "trigger": "TO_BE_RECORDED", "faultDomain": {}, "pauseEvidence": [], "containmentEvidence": [],
        "rollbackEvidence": [], "remainingObligations": [], "humanDecision": "NOT_RECORDED",
        "status": "TEMPLATE_NOT_EVIDENCE"
    })
    by_name = {entry["name"]: entry for entry in mainnet["contracts"]}
    with (out / "mission-004-proof-route.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sequence", "stage", "contract", "address", "purpose", "etherscan_url"])
        writer.writeheader()
        for item in content["proofRoute"]:
            contract = by_name[item["contractName"]]
            writer.writerow({"sequence": item["sequence"], "stage": item["stage"], "contract": item["contractName"], "address": contract["address"], "purpose": item["purpose"], "etherscan_url": contract["etherscanUrl"]})


def add_sitemap(path: Path) -> None:
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    url = f"https://montrealai.github.io/goalos-agialpha-ascension/{PAGE}"
    if url not in raw:
        raw = raw.replace("</urlset>", f"<url><loc>{url}</loc></url>\n</urlset>")
        path.write_text(raw, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--content", default="content/proof-mission-004-sovereign-institution.json")
    parser.add_argument("--mainnet", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()
    site = Path(args.site)
    content_path = Path(args.content)
    mainnet_path = Path(args.mainnet)
    content = load(content_path)
    mainnet = load(mainnet_path)
    validate(content, mainnet)
    required = [site / "index.html", site / "proof-gradient-challenge.html", site / "proof-mission-002.html", site / "proof-mission-003.html", site / "proof-missions.html"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        fail("build Missions 001–003 first; missing: " + ", ".join(missing))
    mission1_hash = sha256(site / "proof-gradient-challenge.html")
    mission2_hash = sha256(site / "proof-mission-002.html")
    (site / PAGE).write_text(page(content, mainnet), encoding="utf-8")
    (site / HUB).write_text(hub_page(content), encoding="utf-8")
    inject_homepage(site / "index.html")
    update_mission3_horizon(site / "proof-mission-003.html")
    write_downloads(site, content, mainnet)
    add_sitemap(site / "sitemap.xml")
    if sha256(site / "proof-gradient-challenge.html") != mission1_hash or sha256(site / "proof-mission-002.html") != mission2_hash:
        fail("Mission 001 or Mission 002 changed unexpectedly")
    qa = {
        "status": "PASS",
        "page": PAGE,
        "hub": HUB,
        "missionId": content["missionId"],
        "proofRouteContracts": len(content["proofRoute"]),
        "operatingMissionEpochs": content["missionBudget"]["missionEpochs"],
        "validatorQuorum": content["missionBudget"]["validatorQuorum"],
        "challengeWindowHours": content["missionBudget"]["challengeWindowHours"],
        "contentSha256": sha256(content_path),
        "mainnetDataSha256": sha256(mainnet_path),
        "mission1Preserved": True,
        "mission2Preserved": True,
        "mission3HorizonPromoted": True,
        "publicNetworkTransactionSent": False,
    }
    dump(site / "qa" / "proof-mission-004-build.json", qa)
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
