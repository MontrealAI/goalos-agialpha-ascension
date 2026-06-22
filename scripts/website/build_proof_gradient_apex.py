#!/usr/bin/env python3
"""Add the Proof Gradient Apex experience to a generated GoalOS v86 site.

This script is deliberately additive: it never edits website/v86_actual_site.
It only augments the temporary generated site directory used by GitHub Pages.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

START = "<!-- GOALOS_PROOF_GRADIENT_APEX_START -->"
END = "<!-- GOALOS_PROOF_GRADIENT_APEX_END -->"
STYLE_START = "<!-- GOALOS_PROOF_GRADIENT_APEX_STYLE_START -->"
STYLE_END = "<!-- GOALOS_PROOF_GRADIENT_APEX_STYLE_END -->"
CANONICAL_AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
EXPECTED_OWNER = "0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99"


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing required source file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha256_file(path)
    return result


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def classify_contract(name: str, meta: dict[str, Any]) -> tuple[str, str]:
    item = meta.get(name, {})
    if item:
        return str(item.get("category", "other")), str(item.get("purpose", name))
    if name == "AGIALPHA":
        return "external", "Canonical external AGIALPHA coordination asset"
    if name.endswith("Vault"):
        return "vault", name
    if name.startswith("AEP") or name in {"AlphaWorkUnitLedger", "MandateEpochRegistry", "AGIEthNamespaceRegistry"}:
        return "aep", name
    if name.endswith("Registry") or name.endswith("Manager") or name.endswith("Router"):
        return "workflow", name
    return "other", name




def manifest_contract_map(manifest: dict[str, Any]) -> dict[str, str]:
    raw = manifest.get("contracts")
    if isinstance(raw, dict):
        return {str(name): str(address) for name, address in raw.items()}
    if isinstance(raw, list):
        result: dict[str, str] = {}
        for item in raw:
            if not isinstance(item, dict) or not item.get("name") or not item.get("address"):
                fail("Mainnet manifest contains an invalid contract entry")
            result[str(item["name"])] = str(item["address"])
        return result
    fail("Mainnet manifest has no contract address map")


def manifest_contract_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    raw = manifest.get("contracts")
    if isinstance(raw, list):
        return [dict(item) for item in raw]
    if isinstance(raw, dict):
        return [{"name": name, "address": address} for name, address in raw.items()]
    fail("Mainnet manifest has no contract entries")

def validate_sources(content: dict[str, Any], manifest: dict[str, Any]) -> None:
    contracts = manifest_contract_map(manifest)
    if manifest.get("chainId") != 1:
        fail("Mainnet manifest must have chainId 1")
    if not contracts:
        fail("Mainnet manifest has no contract address map")
    if contracts.get("AGIALPHA", "").lower() != CANONICAL_AGIALPHA.lower():
        fail("Mainnet manifest does not use canonical AGIALPHA")
    if manifest.get("mockAgialphaUsed") is not False:
        fail("Mainnet manifest reports MockAGIALPHA usage")
    if manifest.get("newAgialphaTokenDeployed") is not False:
        fail("Mainnet manifest reports a new AGIALPHA deployment")
    if len(contracts) != 49:
        fail(f"expected 49 manifest entries, found {len(contracts)}")
    if len([name for name in contracts if name != "AGIALPHA"]) != 48:
        fail("expected 48 GoalOS-created contract entries")
    if len(manifest.get("transactions", [])) != 48:
        fail("expected 48 GoalOS creation transaction hashes")
    if manifest.get("deploymentStatus") != "CONFIGURED":
        fail(f"expected configured Mainnet deployment, found {manifest.get('deploymentStatus')}")
    if len(manifest.get("phaseBGrants", [])) != 14:
        fail("expected 14 configured Phase-B grants")
    if content.get("missionId") != "GOALOS-PROOF-RUN-001-PROOF-GRADIENT":
        fail("unexpected Proof Gradient mission ID")
    route_names = [x.get("contractName") for x in content.get("proofRoute", [])]
    missing = [name for name in route_names if name not in contracts]
    if missing:
        fail("proof route references unknown contracts: " + ", ".join(missing))


def contract_records(content: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    meta = content.get("contractMetadata", {})
    txs = manifest.get("transactions", [])
    fqcns = manifest.get("fullyQualifiedNames", {})
    result: list[dict[str, Any]] = []
    created_index = 0
    for entry in manifest_contract_entries(manifest):
        name = str(entry["name"])
        address = str(entry["address"])
        category, purpose = classify_contract(name, meta)
        created = name != "AGIALPHA"
        tx_hash = txs[created_index] if created and created_index < len(txs) else None
        if created:
            created_index += 1
        result.append({
            "name": name,
            "address": address,
            "category": category,
            "purpose": purpose,
            "goalosCreated": created,
            "fullyQualifiedName": fqcns.get(name) or entry.get("fullyQualifiedName"),
            "deploymentTransactionHash": tx_hash,
            "etherscanUrl": entry.get("etherscanUrl") or f"https://etherscan.io/address/{address}",
            "transactionUrl": f"https://etherscan.io/tx/{tx_hash}" if tx_hash else None,
            "verificationStatus": entry.get("verified"),
        })
    return result


def proof_route(content: dict[str, Any], contracts: dict[str, str]) -> list[dict[str, Any]]:
    route = []
    for item in content["proofRoute"]:
        name = item["contractName"]
        address = contracts[name]
        route.append({
            **item,
            "address": address,
            "etherscanUrl": f"https://etherscan.io/address/{address}",
        })
    return route


def build_page(content: dict[str, Any], manifest: dict[str, Any], records: list[dict[str, Any]], route: list[dict[str, Any]]) -> str:
    sim = content["simulation"]
    scenarios = sim["scenarios"]
    realistic = next(x for x in scenarios if x["name"] == "Realistic")
    created = [x for x in records if x["goalosCreated"]]
    categories = sorted({x["category"] for x in created})

    metric_cards = "".join([
        f"<article class='pg-metric'><span>Hardened valid success</span><strong>{pct(realistic['baselineValidSuccess'])}</strong><small>Synthetic realistic scenario</small></article>",
        f"<article class='pg-metric'><span>GoalOS valid success</span><strong>{pct(realistic['goalosValidSuccess'])}</strong><small>Synthetic realistic scenario</small></article>",
        f"<article class='pg-metric'><span>Hardened false discovery</span><strong>{pct(realistic['baselineFalseDiscovery'])}</strong><small>Among accepted synthetic results</small></article>",
        f"<article class='pg-metric'><span>GoalOS false discovery</span><strong>{pct(realistic['goalosFalseDiscovery'])}</strong><small>Among accepted synthetic results</small></article>",
    ])
    scenario_rows = "".join(
        f"<tr><td><strong>{esc(x['name'])}</strong></td><td>{pct(x['baselineValidSuccess'])}</td><td>{pct(x['goalosValidSuccess'])}</td><td>{pct(x['baselineFalseDiscovery'])}</td><td>{pct(x['goalosFalseDiscovery'])}</td></tr>"
        for x in scenarios
    )
    arms = "".join(
        f"<article class='pg-card'><span class='pg-label'>{esc(x['budget'])}</span><h3>{esc(x['name'])}</h3><p>{esc(x['description'])}</p><div class='pg-big'>{x['candidates']} candidate experiments</div></article>"
        for x in content["arms"]
    )
    acceptance = "".join(f"<li>{esc(x)}</li>" for x in content["acceptance"])
    mission2 = "".join(f"<li>{esc(x)}</li>" for x in content["mission2"]["requirements"])
    route_html = "".join(
        f"<article class='pg-route-node'><span class='pg-route-number'>{x['sequence']:02d}</span><div><small>{esc(x['stage']).upper()}</small><h3>{esc(x['contractName'])}</h3><code>{esc(x['address'])}</code><p>{esc(x['functionSignature'])}</p></div><a href='{esc(x['etherscanUrl'])}' target='_blank' rel='noreferrer'>Etherscan ↗</a></article>"
        for x in route
    )
    filter_buttons = "".join(
        f"<button type='button' class='pg-filter{' active' if i == 0 else ''}' data-filter='{esc(cat)}'>{esc('All 48' if cat == 'all' else cat.upper())}</button>"
        for i, cat in enumerate(["all", *categories])
    )
    contract_cards = "".join(
        f"<article class='pg-contract' data-category='{esc(x['category'])}' data-search='{esc((x['name'] + ' ' + x['address'] + ' ' + x['purpose']).lower())}'><div class='pg-contract-top'><span class='pg-tag'>{esc(x['category'].upper())}</span><a href='{esc(x['etherscanUrl'])}' target='_blank' rel='noreferrer'>Etherscan ↗</a></div><h3>{esc(x['name'])}</h3><p>{esc(x['purpose'])}</p><code>{esc(x['address'])}</code></article>"
        for x in created
    )
    claim_items = "".join(f"<li>{esc(x)}</li>" for x in content["claimBoundary"])
    proof_steps = ["Objective", "Experiments", "Failed branches", "Reward-hack rejection", "Replay", "Validator decision", "Accepted capability", "Settlement", "Reuse in a harder mission"]
    chain = "".join(f"<span>{esc(x)}</span>{'<b>→</b>' if i < len(proof_steps)-1 else ''}" for i, x in enumerate(proof_steps))

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{esc(content['title'])} — GoalOS AGIALPHA Ascension</title>
<meta name='description' content='Same engine. Same objective. Same compute. Different institutional architecture.'>
<meta property='og:title' content='{esc(content['title'])}'>
<meta property='og:description' content='{esc(content['publicThesis'])}'>
<meta name='theme-color' content='#06152a'>
<link rel='stylesheet' href='assets/goalos-v86-preserve.css'>
<style id='goalos-v86-critical'>html,body{{margin:0;min-height:100%;overflow-x:hidden}}body{{background:#f7f1df;color:#071427;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}</style>
<style>
:root{{--pg-navy:#061326;--pg-blue:#0b2855;--pg-gold:#ffdc73;--pg-aqua:#58e6ff;--pg-mint:#8ff0c8;--pg-ink:#071427;--pg-paper:#fffdf7;--pg-muted:#61718b;--pg-line:rgba(7,20,39,.14);--pg-shadow:0 28px 90px rgba(7,20,39,.16);--pg-max:1240px}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{line-height:1.58}}a{{color:inherit}}.pg-skip{{position:absolute;left:-9999px}}.pg-skip:focus{{left:1rem;top:1rem;z-index:999;background:white;padding:.8rem 1rem;border-radius:999px}}.pg-top{{position:sticky;top:0;z-index:80;background:rgba(6,19,38,.93);backdrop-filter:blur(18px);border-bottom:1px solid rgba(255,255,255,.12)}}.pg-nav{{max-width:var(--pg-max);margin:auto;padding:.85rem 1.1rem;display:flex;justify-content:space-between;align-items:center;gap:1rem}}.pg-brand{{display:flex;gap:.65rem;align-items:center;color:white;text-decoration:none;font-weight:950;letter-spacing:.04em}}.pg-mark{{width:34px;height:34px;border-radius:13px;background:conic-gradient(from 140deg,var(--pg-gold),var(--pg-aqua),#9d8cff,var(--pg-gold));box-shadow:0 0 0 4px rgba(255,220,115,.11)}}.pg-links{{display:flex;flex-wrap:wrap;gap:.4rem;justify-content:flex-end}}.pg-links a{{color:#dfeaff;text-decoration:none;font-weight:850;font-size:.86rem;padding:.48rem .66rem;border-radius:999px}}.pg-links a:hover{{background:rgba(255,255,255,.1)}}.pg-hero{{position:relative;overflow:hidden;color:white;background:radial-gradient(circle at 80% 15%,rgba(88,230,255,.19),transparent 22rem),radial-gradient(circle at 10% 0%,rgba(255,220,115,.18),transparent 25rem),linear-gradient(135deg,#030713,#071a37 55%,#171039);padding:84px 18px 68px;border-radius:0 0 56px 56px}}.pg-hero:before{{content:"";position:absolute;inset:0;opacity:.15;background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px);background-size:34px 34px}}.pg-wrap{{max-width:var(--pg-max);margin:auto;position:relative}}.pg-hero-grid{{display:grid;grid-template-columns:1.08fr .92fr;gap:2rem;align-items:center}}.pg-kicker,.pg-label{{display:inline-flex;align-items:center;border:1px solid rgba(255,220,115,.36);background:rgba(255,220,115,.08);color:var(--pg-gold);padding:.38rem .7rem;border-radius:999px;text-transform:uppercase;letter-spacing:.1em;font-weight:950;font-size:.75rem}}.pg-hero h1{{font-size:clamp(3.2rem,8vw,7.4rem);line-height:.87;letter-spacing:-.075em;margin:.8rem 0 1rem}}.pg-hero h1 span{{color:var(--pg-gold)}}.pg-lead{{font-size:clamp(1.1rem,2vw,1.46rem);color:#dce9fb;max-width:760px;font-weight:650}}.pg-thesis{{margin-top:1.1rem;padding:1rem 1.1rem;border:1px solid rgba(255,255,255,.16);border-radius:20px;background:rgba(255,255,255,.065);font-weight:900}}.pg-actions{{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.25rem}}.pg-btn{{display:inline-flex;align-items:center;text-decoration:none;border-radius:999px;padding:.76rem 1rem;font-weight:950;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08)}}.pg-btn.primary{{background:linear-gradient(135deg,var(--pg-gold),#fff2b8);color:#101c32;border:0}}.pg-hero-panel{{border:1px solid rgba(255,255,255,.16);border-radius:32px;padding:1.15rem;background:rgba(255,255,255,.07);box-shadow:0 40px 120px rgba(0,0,0,.28)}}.pg-hero-panel h2{{margin:.2rem 0 1rem;font-size:1.45rem}}.pg-mini-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:.7rem}}.pg-mini{{border:1px solid rgba(255,255,255,.13);border-radius:17px;padding:.8rem;background:rgba(255,255,255,.055)}}.pg-mini strong{{display:block;color:var(--pg-gold);font-size:1.35rem}}.pg-mini span{{font-size:.78rem;color:#dce9fb;font-weight:800}}.pg-boundary{{margin-top:.8rem;border:1px solid rgba(255,143,163,.38);background:rgba(255,143,163,.09);border-radius:18px;padding:.85rem;color:#ffe4e9;font-size:.88rem}}.pg-section{{padding:72px 18px}}.pg-section.alt{{background:#eef5f6}}.pg-section.dark{{color:white;background:linear-gradient(135deg,#061326,#0b2855);border-radius:44px;margin:0 12px}}.pg-head{{max-width:900px;margin:0 auto 2rem;text-align:center}}.pg-eyebrow{{color:#9b7018;letter-spacing:.15em;text-transform:uppercase;font-weight:950;font-size:.76rem}}.dark .pg-eyebrow{{color:var(--pg-gold)}}.pg-head h2{{font-size:clamp(2rem,5vw,4.3rem);line-height:.98;letter-spacing:-.055em;margin:.35rem 0 .75rem}}.pg-head p{{color:var(--pg-muted);font-size:1.08rem}}.dark .pg-head p,.dark p,.dark li{{color:#dce9fb}}.pg-grid{{display:grid;gap:1rem}}.pg-two{{grid-template-columns:repeat(2,minmax(0,1fr))}}.pg-four{{grid-template-columns:repeat(4,minmax(0,1fr))}}.pg-card,.pg-metric,.pg-contract{{background:rgba(255,255,255,.82);border:1px solid var(--pg-line);border-radius:25px;padding:1.2rem;box-shadow:var(--pg-shadow);backdrop-filter:blur(14px)}}.pg-card h3,.pg-contract h3{{margin:.35rem 0 .5rem;font-size:1.35rem}}.pg-card p,.pg-contract p{{color:var(--pg-muted)}}.pg-big{{margin-top:.75rem;font-weight:950;color:#15305b}}.pg-metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem}}.pg-metric span,.pg-metric small{{display:block;color:var(--pg-muted);font-weight:800}}.pg-metric strong{{display:block;font-size:2rem;color:#102a53;margin:.15rem 0}}.pg-table{{overflow:auto;border:1px solid var(--pg-line);border-radius:22px;background:white;box-shadow:var(--pg-shadow)}}.pg-table table{{border-collapse:collapse;width:100%;min-width:760px}}.pg-table th,.pg-table td{{padding:.9rem;border-bottom:1px solid var(--pg-line);text-align:left}}.pg-table th{{background:#071a37;color:white;font-size:.76rem;text-transform:uppercase;letter-spacing:.07em}}.pg-proof-chain{{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:.5rem}}.pg-proof-chain span{{background:white;border:1px solid var(--pg-line);border-radius:999px;padding:.55rem .75rem;font-weight:900}}.pg-proof-chain b{{color:#ad7b17}}.pg-route{{display:grid;gap:.7rem}}.pg-route-node{{display:grid;grid-template-columns:48px 1fr auto;gap:.9rem;align-items:center;border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.055);border-radius:20px;padding:.85rem}}.pg-route-number{{width:43px;height:43px;display:grid;place-items:center;border-radius:14px;background:linear-gradient(135deg,var(--pg-gold),#fff1b5);color:#13213a;font-weight:950}}.pg-route-node h3{{margin:.08rem 0;font-size:1.02rem}}.pg-route-node small{{color:var(--pg-aqua);font-weight:950;letter-spacing:.08em}}.pg-route-node code{{display:block;color:#bcd0ea;overflow-wrap:anywhere;font-size:.78rem}}.pg-route-node p{{margin:.18rem 0 0;font-family:ui-monospace,monospace;font-size:.76rem}}.pg-route-node a{{color:var(--pg-gold);font-weight:900;text-decoration:none}}.pg-filterbar{{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem;align-items:center}}.pg-filterbar input{{flex:1;min-width:240px;border:1px solid var(--pg-line);border-radius:999px;padding:.72rem 1rem;font:inherit;background:white}}.pg-filter{{border:1px solid var(--pg-line);border-radius:999px;padding:.58rem .75rem;background:white;font-weight:900;cursor:pointer}}.pg-filter.active{{background:#071a37;color:white}}.pg-contracts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem}}.pg-contract{{box-shadow:none}}.pg-contract-top{{display:flex;justify-content:space-between;gap:.6rem;align-items:center}}.pg-contract-top a{{font-size:.78rem;font-weight:900;color:#2459a5;text-decoration:none}}.pg-tag{{font-size:.68rem;font-weight:950;letter-spacing:.08em;border-radius:999px;padding:.3rem .5rem;background:#edf3ff;color:#183b70}}.pg-contract code{{display:block;font-size:.73rem;overflow-wrap:anywhere;color:#1c355d;background:#f0f4f8;border-radius:12px;padding:.55rem}}.pg-list{{columns:2;gap:2rem}}.pg-list li{{break-inside:avoid;margin-bottom:.55rem}}.pg-callout{{border:1px solid rgba(88,230,255,.3);background:rgba(88,230,255,.08);border-radius:25px;padding:1.1rem}}.pg-downloads{{display:flex;flex-wrap:wrap;gap:.7rem;justify-content:center}}.pg-downloads a{{text-decoration:none;border:1px solid var(--pg-line);border-radius:999px;background:white;padding:.7rem .9rem;font-weight:900}}.pg-footer{{background:#061326;color:#dce9fb;padding:35px 18px}}.pg-footer .pg-wrap{{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}}.pg-hidden{{display:none!important}}@media(max-width:960px){{.pg-hero-grid,.pg-two,.pg-four,.pg-contracts{{grid-template-columns:1fr}}.pg-metrics{{grid-template-columns:repeat(2,1fr)}}.pg-route-node{{grid-template-columns:44px 1fr}}.pg-route-node>a{{grid-column:2}}.pg-list{{columns:1}}.pg-links{{justify-content:flex-start}}.pg-nav{{align-items:flex-start}}}}@media(max-width:520px){{.pg-metrics,.pg-mini-grid{{grid-template-columns:1fr}}.pg-hero{{padding-top:62px;border-radius:0 0 34px 34px}}.pg-hero h1{{font-size:3.15rem}}}}
</style>
</head>
<body>
<a class='pg-skip' href='#main'>Skip to content</a>
<header class='pg-top'><nav class='pg-nav' aria-label='Primary'><a class='pg-brand' href='index.html'><span class='pg-mark' aria-hidden='true'></span><span>GoalOS AGIALPHA</span></a><div class='pg-links'><a href='index.html'>Home</a><a href='mission-os.html'>Mission OS</a><a href='proof-cards.html'>Proof Cards</a><a href='proof-observatory.html'>Observatory</a></div></nav></header>
<main id='main'>
<section class='pg-hero'><div class='pg-wrap pg-hero-grid'><div><span class='pg-kicker'>GoalOS Public Proof Mission 001 · The Institutional Test</span><h1>The Proof <span>Gradient</span></h1><p class='pg-lead'>{esc(content['subtitle'])}</p><div class='pg-thesis'>{esc(content['publicThesis'])}</div><p style='margin:.85rem 0 0;color:#bdefff;font-weight:850'>{esc(content.get('categoryStatement',''))}</p><div class='pg-actions'><a class='pg-btn primary' href='#experiment'>Open the experiment</a><a class='pg-btn' href='#mainnet'>Inspect the Mainnet route</a><a class='pg-btn' href='{esc(content['releaseUrl'])}' target='_blank' rel='noreferrer'>Mainnet release ↗</a></div></div><aside class='pg-hero-panel'><h2>What is being tested?</h2><div class='pg-mini-grid'><div class='pg-mini'><strong>100,000</strong><span>Synthetic campaigns per scenario</span></div><div class='pg-mini'><strong>48h / arm</strong><span>Equal modeled budget</span></div><div class='pg-mini'><strong>48 / 48</strong><span>GoalOS-created contracts verified</span></div><div class='pg-mini'><strong>0 failed</strong><span>Mainnet verification failures</span></div></div><div class='pg-boundary'><strong>Synthetic design stress test.</strong> The comparison below is not an empirical result about GoalOS, Recursive, or another system.<br><code>Mission ID: {esc(content['missionId'])}</code></div></aside></div></section>
<section class='pg-section pg-manifesto'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>The category-defining proposition</span><h2>Autoresearch finds candidates. GoalOS governs what earns the right to become infrastructure.</h2><p>A fast result is not yet an institutional capability. It must survive evidence, falsification, independent replay, validator judgment, bounded claims, settlement discipline, and reuse under harder conditions.</p></div><div class='pg-grid pg-four'><article class='pg-law'><span>01</span><strong>No proof, no propagation.</strong></article><article class='pg-law'><span>02</span><strong>No replay, no settlement.</strong></article><article class='pg-law'><span>03</span><strong>No rollback, no release.</strong></article><article class='pg-law crown'><span>∞</span><strong>Only accepted proof may evolve.</strong></article></div></div></section>
<section class='pg-section' id='experiment'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Controlled experiment</span><h2>Same research engine. Different institutional architecture.</h2><p>{esc(content['objective'])}</p></div><div class='pg-grid pg-two'>{arms}</div><div class='pg-callout' style='margin-top:1rem'><strong>Preregistered acceptance:</strong><ul class='pg-list'>{acceptance}</ul></div></div></section>
<section class='pg-section alt'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Synthetic simulation</span><h2>An honest result, not a manufactured victory.</h2><p>{esc(sim['conclusion'])}</p></div><div class='pg-metrics'>{metric_cards}</div><div class='pg-table v86-scroll-table' style='margin-top:1rem'><table><thead><tr><th>Scenario</th><th>Hardened valid success</th><th>GoalOS valid success</th><th>Hardened false discovery</th><th>GoalOS false discovery</th></tr></thead><tbody>{scenario_rows}</tbody></table></div><div class='pg-callout' style='margin-top:1rem'><strong>Representative fixed-seed candidate:</strong> {esc(sim['representative']['candidate'])}, {esc(sim['representative']['hypothesis'])}; robust improvement {sim['representative']['robustImprovementPct']:.2f}%; validator decision {esc(sim['representative']['validatorDecision'])}. One false acceptance would need to cost about {sim['falseAcceptanceCostBreakEvenInValidDiscoveryUnits']:.1f} valid-discovery units before the modeled one-mission expected value favors GoalOS.</div></div></section>
<section class='pg-section'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Complete publication chain</span><h2>Only accepted proof may propagate, settle, or evolve.</h2><p>Every experiment, failure, reward-hack rejection, replay, validator decision, settlement condition, and reuse attempt belongs in the public chain.</p></div><div class='pg-proof-chain'>{chain}</div></div></section>
<section class='pg-section dark' id='mainnet'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Ethereum Mainnet proof route</span><h2>Institutional proof infrastructure is already addressable.</h2><p>The route below maps the mission stages to the configured GoalOS v4.4.0 deployment. It is an architectural route, not a claim that the synthetic experiment has been anchored or settled.</p></div><div class='pg-route'>{route_html}</div></div></section>
<section class='pg-section'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Mission 002</span><h2>{esc(content['mission2']['title'])}</h2><p>{esc(content['mission2']['description'])}</p></div><div class='pg-card'><ul class='pg-list'>{mission2}</ul></div></div></section>
<section class='pg-section alt'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Position versus autoresearch engines</span><h2>{esc(content['positioning']['headline'])}</h2><p>{esc(content['positioning']['body'])}</p></div></div></section>
<section class='pg-section' id='contracts'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Canonical address book</span><h2>All 48 GoalOS-created Ethereum Mainnet contracts.</h2><p>Generated from <code>data/mainnet/v4.4.0-mainnet-2026-06-21.json</code>. The canonical external AGIALPHA contract is listed separately in the downloadable map.</p></div><div class='pg-filterbar'><input id='pg-search' type='search' placeholder='Search contract name, purpose, or address' aria-label='Search contracts'>{filter_buttons}</div><div class='pg-contracts' id='pg-contracts'>{contract_cards}</div></div></section>
<section class='pg-section dark'><div class='pg-wrap'><div class='pg-head'><span class='pg-eyebrow'>Claim boundary</span><h2>Grand ambition. Strict evidence discipline.</h2></div><ul>{claim_items}</ul><div class='pg-downloads'><a href='downloads/proof-gradient/goalos-mainnet-contract-addresses.csv'>Download addresses CSV</a><a href='downloads/proof-gradient/proof-gradient-mainnet-map.json'>Download Mainnet map JSON</a><a href='downloads/proof-gradient/proof-gradient-mission.json'>Download mission JSON</a><a href='downloads/proof-gradient/proof-gradient-simulation-summary.json'>Download simulation summary</a></div></div></section>
</main>
<footer class='pg-footer'><div class='pg-wrap'><div><strong>GoalOS AGIALPHA Ascension</strong><br><small>Proof-governed autonomous work.</small></div><div><a href='{esc(content['repositoryUrl'])}' target='_blank' rel='noreferrer'>GitHub repository ↗</a></div></div></footer>
<script>
(function(){{const cards=[...document.querySelectorAll('.pg-contract')],filters=[...document.querySelectorAll('.pg-filter')],search=document.getElementById('pg-search');let active='all';function apply(){{const q=(search.value||'').trim().toLowerCase();cards.forEach(c=>{{const cat=c.dataset.category||'',text=c.dataset.search||'';c.classList.toggle('pg-hidden',!((active==='all'||cat===active)&&(!q||text.includes(q))))}})}}filters.forEach(b=>b.addEventListener('click',()=>{{filters.forEach(x=>x.classList.remove('active'));b.classList.add('active');active=b.dataset.filter||'all';apply()}}));search.addEventListener('input',apply);}})();
</script>
<script defer src='assets/goalos-v86-dynamic-ai.js'></script>
</body></html>"""


def homepage_style() -> str:
    return f"""{STYLE_START}
<style id='goalos-proof-gradient-home-style'>
.pg-home-feature{{padding:78px 18px;background:radial-gradient(circle at 88% 12%,rgba(88,230,255,.13),transparent 24rem),linear-gradient(135deg,#061326,#0d2853);color:white;border-radius:48px;margin:24px 12px;overflow:hidden;position:relative}}.pg-home-feature:before{{content:"";position:absolute;inset:0;opacity:.13;background-image:linear-gradient(rgba(255,255,255,.14) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.14) 1px,transparent 1px);background-size:32px 32px}}.pg-home-inner{{max-width:1180px;margin:auto;position:relative;display:grid;grid-template-columns:1.1fr .9fr;gap:1.2rem;align-items:center}}.pg-home-kicker{{color:#ffdc73;text-transform:uppercase;letter-spacing:.13em;font-size:.76rem;font-weight:950}}.pg-home-feature h2{{font-size:clamp(2.3rem,5.5vw,5.2rem);line-height:.94;letter-spacing:-.06em;margin:.4rem 0 .8rem}}.pg-home-feature p{{color:#dce9fb;font-size:1.08rem;max-width:760px}}.pg-home-actions{{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1rem}}.pg-home-button{{display:inline-flex;text-decoration:none;border-radius:999px;padding:.78rem 1rem;font-weight:950;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08)}}.pg-home-button.primary{{background:linear-gradient(135deg,#ffdc73,#fff1b5);color:#12213a;border:0}}.pg-home-stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:.7rem}}.pg-home-stat{{padding:1rem;border:1px solid rgba(255,255,255,.15);border-radius:20px;background:rgba(255,255,255,.06)}}.pg-home-stat strong{{display:block;color:#ffdc73;font-size:1.65rem}}.pg-home-stat span{{font-size:.78rem;color:#dce9fb;font-weight:800}}.pg-home-boundary{{grid-column:1/-1;padding:.75rem .9rem;border:1px solid rgba(255,143,163,.32);border-radius:17px;background:rgba(255,143,163,.08);color:#ffe5e9;font-size:.84rem}}@media(max-width:900px){{.pg-home-inner{{grid-template-columns:1fr}}}}@media(max-width:520px){{.pg-home-stats{{grid-template-columns:1fr}}.pg-home-feature{{border-radius:30px;margin:14px 8px}}}}
</style>
{STYLE_END}"""


def homepage_section(content: dict[str, Any]) -> str:
    realistic = next(x for x in content["simulation"]["scenarios"] if x["name"] == "Realistic")
    return f"""{START}
<section class='pg-home-feature' id='proof-gradient-challenge'><div class='pg-home-inner'><div><span class='pg-home-kicker'>Public Proof Mission 001 · Institutional Autoresearch</span><h2>The Proof Gradient</h2><p><strong>Same engine. Same objective. Same compute. One difference: proof governance.</strong> Enter the controlled public test of what machine discovery must prove before it may propagate, settle, or evolve.</p><div class='pg-home-actions'><a class='pg-home-button primary' href='proof-gradient-challenge.html'>Enter the Proof Gradient</a><a class='pg-home-button' href='proof-gradient-challenge.html#mainnet'>Inspect the Mainnet route</a></div></div><div class='pg-home-stats'><div class='pg-home-stat'><strong>48h / arm</strong><span>Equal synthetic budget</span></div><div class='pg-home-stat'><strong>48 / 48</strong><span>GoalOS contracts recorded verified</span></div><div class='pg-home-stat'><strong>{pct(realistic['baselineValidSuccess'])}</strong><span>Hardened valid success</span></div><div class='pg-home-stat'><strong>{pct(realistic['goalosFalseDiscovery'])}</strong><span>GoalOS false discovery</span></div></div><div class='pg-home-boundary'>Synthetic design stress test—not an empirical comparison. The real mission must publish every experiment, failure, replay, validator decision, settlement condition, and reuse attempt.</div></div></section>
{END}"""


def replace_marked(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(replacement, text)
    return text


def inject_homepage(path: Path, content: dict[str, Any]) -> None:
    raw = path.read_text(encoding="utf-8")
    style = homepage_style()
    section = homepage_section(content)
    if STYLE_START in raw:
        raw = replace_marked(raw, STYLE_START, STYLE_END, style)
    else:
        if "</head>" not in raw:
            fail("generated homepage has no </head> anchor")
        raw = raw.replace("</head>", style + "\n</head>", 1)
    if START in raw:
        raw = replace_marked(raw, START, END, section)
    else:
        if "</main>" not in raw:
            fail("generated homepage has no </main> anchor")
        raw = raw.replace("</main>", section + "\n</main>", 1)
    path.write_text(raw, encoding="utf-8")


def update_routes(path: Path) -> None:
    if not path.exists():
        return
    value = read_json(path)
    routes = value.get("routes") if isinstance(value, dict) else None
    if isinstance(routes, list) and "proof-gradient-challenge.html" not in routes:
        routes.append("proof-gradient-challenge.html")
        routes.sort()
        write_json(path, value)


def update_sitemap(path: Path) -> None:
    url = "https://montrealai.github.io/goalos-agialpha-ascension/proof-gradient-challenge.html"
    if not path.exists():
        path.write_text(f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{url}</loc></url></urlset>\n", encoding="utf-8")
        return
    raw = path.read_text(encoding="utf-8")
    if url in raw:
        return
    if "</urlset>" not in raw:
        fail("generated sitemap has no </urlset> anchor")
    raw = raw.replace("</urlset>", f"<url><loc>{url}</loc></url></urlset>", 1)
    path.write_text(raw, encoding="utf-8")


def deterministic_timestamp(manifest: dict[str, Any]) -> str:
    return str(manifest.get("configuredAt") or manifest.get("deployedAt") or "2026-06-21T00:00:00Z")


def update_site_status(path: Path, manifest_hash: str, generated_at: str) -> None:
    value: dict[str, Any] = read_json(path) if path.exists() else {}
    value["proof_gradient"] = {
        "status": "GENERATED",
        "page": "proof-gradient-challenge.html",
        "mission_id": "GOALOS-PROOF-RUN-001-PROOF-GRADIENT",
        "source": "content/proof-gradient-apex.json",
        "mainnet_manifest_sha256": manifest_hash,
        "generated_at": generated_at,
        "public_network_transaction_sent": False,
    }
    write_json(path, value)


def write_downloads(site: Path, content: dict[str, Any], manifest: dict[str, Any], records: list[dict[str, Any]], route: list[dict[str, Any]], manifest_hash: str, generated_at: str) -> list[str]:
    out = site / "downloads" / "proof-gradient"
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "goalos-mainnet-contract-addresses.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "address", "category", "purpose", "goalos_created", "fully_qualified_name", "etherscan_url", "deployment_transaction_hash"])
        writer.writeheader()
        for item in records:
            writer.writerow({
                "name": item["name"], "address": item["address"], "category": item["category"], "purpose": item["purpose"],
                "goalos_created": str(item["goalosCreated"]).lower(), "fully_qualified_name": item["fullyQualifiedName"] or "",
                "etherscan_url": item["etherscanUrl"], "deployment_transaction_hash": item["deploymentTransactionHash"] or "",
            })
    map_value = {
        "schemaVersion": "1.0",
        "generatedAt": generated_at,
        "missionId": content["missionId"],
        "network": manifest.get("network"),
        "chainId": manifest.get("chainId"),
        "deploymentStatus": manifest.get("deploymentStatus"),
        "deploymentMode": manifest.get("deploymentMode"),
        "deployedAt": manifest.get("deployedAt"),
        "configuredAt": manifest.get("configuredAt"),
        "manifestSha256": manifest_hash,
        "canonicalAgialpha": manifest_contract_map(manifest)["AGIALPHA"],
        "goalosCreatedContractCount": 48,
        "phaseBGrantCount": len(manifest.get("phaseBGrants", [])),
        "proofRoute": route,
        "contracts": records,
        "claimBoundary": content["claimBoundary"],
    }
    write_json(out / "proof-gradient-mainnet-map.json", map_value)
    mission_value = {key: content[key] for key in ["schemaVersion", "pageVersion", "title", "subtitle", "missionId", "publicThesis", "objective", "arms", "acceptance", "mission2", "positioning", "proofRoute", "claimBoundary"]}
    write_json(out / "proof-gradient-mission.json", mission_value)
    write_json(out / "proof-gradient-simulation-summary.json", content["simulation"])
    return [str(p.relative_to(site)) for p in sorted(out.iterdir()) if p.is_file()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Add the Proof Gradient Challenge to a generated GoalOS v86 website")
    parser.add_argument("--site", default="site", help="Generated site directory")
    parser.add_argument("--content", default="content/proof-gradient-apex.json")
    parser.add_argument("--manifest", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    args = parser.parse_args()

    repo = Path.cwd()
    site = (repo / args.site).resolve()
    if not (site / "index.html").exists():
        fail(f"generated site is missing index.html: {site}")
    before = snapshot(site)
    content_path = repo / args.content
    manifest_path = repo / args.manifest
    content = read_json(content_path)
    manifest = read_json(manifest_path)
    validate_sources(content, manifest)
    records = contract_records(content, manifest)
    route = proof_route(content, manifest_contract_map(manifest))
    manifest_hash = sha256_file(manifest_path)
    generated_at = deterministic_timestamp(manifest)

    (site / "proof-gradient-challenge.html").write_text(build_page(content, manifest, records, route), encoding="utf-8")
    downloads = write_downloads(site, content, manifest, records, route, manifest_hash, generated_at)
    inject_homepage(site / "index.html", content)
    update_routes(site / "routes.json")
    update_sitemap(site / "sitemap.xml")
    update_site_status(site / "site-status.json", manifest_hash, generated_at)

    after = snapshot(site)
    removed = sorted(set(before) - set(after))
    modified = sorted(path for path in set(before) & set(after) if before[path] != after[path])
    added = sorted(set(after) - set(before))
    expected_modified = {"index.html", "routes.json", "sitemap.xml", "site-status.json"}
    def overlay_owned(path: str) -> bool:
        return path == "proof-gradient-challenge.html" or path.startswith("downloads/proof-gradient/") or path.startswith("qa/proof-gradient-")
    unexpected_modified = sorted(path for path in modified if path not in expected_modified and not overlay_owned(path))
    canonical_modified = sorted(path for path in modified if path in expected_modified)
    overlay_owned_modified = sorted(path for path in modified if overlay_owned(path))
    if removed:
        fail("additive overlay removed existing generated files: " + ", ".join(removed[:20]))
    if unexpected_modified:
        fail("additive overlay unexpectedly modified files: " + ", ".join(unexpected_modified[:20]))

    report = {
        "schemaVersion": "1.0",
        "status": "PASS",
        "mode": "ADDITIVE_GENERATED_SITE_OVERLAY",
        "canonicalSourceModified": False,
        "missionId": content["missionId"],
        "mainnetManifest": str(manifest_path.relative_to(repo)),
        "mainnetManifestSha256": manifest_hash,
        "manifestEntries": len(records),
        "goalosCreatedContracts": len([x for x in records if x["goalosCreated"]]),
        "phaseBGrants": len(manifest.get("phaseBGrants", [])),
        "modifiedExistingGeneratedFiles": modified,
        "canonicalGeneratedFilesModified": canonical_modified,
        "overlayOwnedFilesModified": overlay_owned_modified,
        "addedGeneratedFiles": added,
        "removedGeneratedFiles": removed,
        "unexpectedModifiedFiles": unexpected_modified,
        "downloadFiles": downloads,
        "publicNetworkTransactionSent": False,
        "generatedAt": generated_at,
    }
    write_json(site / "qa" / "proof-gradient-apex-build.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
