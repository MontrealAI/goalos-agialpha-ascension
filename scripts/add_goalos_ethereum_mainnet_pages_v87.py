#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

BASE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
RELEASE_URL = "https://github.com/MontrealAI/goalos-agialpha-ascension/releases/tag/v4.4.0-mainnet-2026-06-21"
RELEASE_TAG = "v4.4.0-mainnet-2026-06-21"
CANONICAL_AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
HOME_START = "<!-- GOALOS_MAINNET_V87_START -->"
HOME_END = "<!-- GOALOS_MAINNET_V87_END -->"
HOME_STYLE_START = "<!-- GOALOS_MAINNET_V87_STYLE_START -->"
HOME_STYLE_END = "<!-- GOALOS_MAINNET_V87_STYLE_END -->"
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")

GROUPS = [
    ("Capital, vaults & treasury infrastructure", [
        "CommercializationPerformanceVault", "ProofRewardsVault", "LiquidityVault",
        "SecurityVault", "CommunityVault", "TreasuryRouter",
    ]),
    ("Core proof, work & protocol registries", [
        "ProofSeedRegistry", "LegacyAGIJobManagerRegistry", "ReputationRegistry",
        "ReferralRegistry", "ProofCardRegistry", "ProofCredentialRegistry",
        "JobRegistry", "JobClaimBondManager", "PremiumAccessRegistry",
        "ProofSubmissionRegistry", "ReviewerBondRegistry",
        "ProtocolConfigRegistry", "LaunchGateRegistry",
    ]),
    ("Dispute, participation & credential governance", [
        "DisputeRegistry", "AppealRegistry", "SponsorRegistry",
        "BuilderProfileRegistry", "CredentialRevocationRegistry",
    ]),
    ("AEP execution, evidence & rollout architecture", [
        "AEPAgentRegistry", "AEPArtifactRegistry", "AEPGoalOSCommitRegistry",
        "AEPRunCommitmentRegistry", "AEPProofLedger", "AEPEvalRegistry",
        "AEPAttestationRegistry", "AEPSelectionGate", "AEPRolloutRouter",
        "AEPRollbackRegistry", "AEPEvidenceDocketRegistry",
        "AEPProofBundleRegistry", "AlphaWorkUnitLedger",
        "MandateEpochRegistry", "AGIEthNamespaceRegistry",
    ]),
    ("Institutional assurance, staking & accountability", [
        "AEPConformanceRegistry", "AEPClaimBoundaryRegistry", "AEPReplayRegistry",
        "AEPCommitRevealValidationRegistry", "AEPEvaluatorStakingRegistry",
        "AEPSlashingCourt", "AEPRewardVault", "AEPChronicleRegistry",
        "AEPFalsificationRegistry",
    ]),
]


def die(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> Any:
    if not path.is_file():
        die(f"missing required data file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"invalid JSON in {path}: {exc}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registry(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    data = load_json(path)
    if not isinstance(data, dict):
        die("contract registry must be a JSON object")

    metadata = data.get("metadata")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        die("contract registry metadata must be an object")

    chain_id = data.get("chainId", metadata.get("chainId"))
    if chain_id != 1:
        die("contract registry must describe Ethereum Mainnet chainId 1")

    contracts = data.get("contracts")
    if not isinstance(contracts, list) or len(contracts) != 49:
        die("contract registry must contain exactly 49 entries")

    normalized: list[dict[str, Any]] = []
    seen_addresses: set[str] = set()
    seen_names: set[str] = set()
    by_name: dict[str, dict[str, Any]] = {}
    deployed = 0
    external = 0

    for raw in contracts:
        if not isinstance(raw, dict):
            die("every registry entry must be an object")
        entry = dict(raw)
        name = entry.get("name")
        address = entry.get("address")
        entry_chain_id = entry.get("chainId", chain_id)

        if not isinstance(name, str) or not name:
            die("registry entry has no valid name")
        if not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            die(f"invalid Ethereum address for {name}")
        if entry_chain_id != 1:
            die(f"wrong chainId for {name}")

        classification = entry.get("classification")
        if classification not in {"deployed", "external"}:
            if entry.get("external") is True and entry.get("deployedByGoalOS") is False:
                classification = "external"
            elif entry.get("external") is False and entry.get("deployedByGoalOS") is True:
                classification = "deployed"
            else:
                die(f"cannot determine deployed/external classification for {name}")

        key = address.lower()
        if key in seen_addresses:
            die(f"duplicate contract address: {address}")
        if name in seen_names:
            die(f"duplicate contract name: {name}")

        entry["chainId"] = 1
        entry["classification"] = classification
        entry["etherscanUrl"] = entry.get("etherscanUrl") or entry.get("etherscanLink") or f"https://etherscan.io/address/{address}"
        seen_addresses.add(key)
        seen_names.add(name)
        normalized.append(entry)
        by_name[name] = entry
        deployed += classification == "deployed"
        external += classification == "external"

    if deployed != 48 or external != 1:
        die(f"expected 48 deployed and 1 external entries, got {deployed} and {external}")

    agialpha = by_name.get("AGIALPHA")
    if not agialpha or agialpha["address"].lower() != CANONICAL_AGIALPHA.lower() or agialpha["classification"] != "external":
        die("canonical external AGIALPHA entry is missing or incorrect")

    grouped_names = {name for _, names in GROUPS for name in names}
    deployed_names = {c["name"] for c in normalized if c["classification"] == "deployed"}
    if grouped_names != deployed_names:
        missing = sorted(deployed_names - grouped_names)
        stale = sorted(grouped_names - deployed_names)
        die(f"contract grouping mismatch; missing={missing}, stale={stale}")
    return normalized, by_name

def validate_release_contracts(path: Path, registry: list[dict[str, Any]]) -> tuple[int, str]:
    data = load_json(path)
    if not isinstance(data, list) or len(data) != 49:
        die("release contract registry must contain exactly 49 entries")
    expected = {(c["name"], c["address"].lower(), c["classification"]) for c in registry}
    actual = {(c.get("name"), str(c.get("address", "")).lower(), c.get("classification")) for c in data if isinstance(c, dict)}
    if expected != actual:
        die("release contract registry does not match canonical contract registry")
    deployed = [c for c in data if c.get("classification") == "deployed"]
    operator_verified = sum(c.get("operatorVerificationStatus") == "VERIFIED" for c in deployed)
    independent_states = {str(c.get("independentReleaseVerificationStatus", "PENDING")) for c in deployed}
    independent = "PASS" if independent_states == {"PASS"} else "PENDING"
    if operator_verified != 48:
        die(f"expected 48 operator verification records, got {operator_verified}")
    return operator_verified, independent


def validate_release_manifest(path: Path, registry: list[dict[str, Any]]) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict) or data.get("chainId") != 1:
        die("release manifest must describe chainId 1")
    if data.get("releaseTag") != RELEASE_TAG:
        die("release manifest tag does not match the published release")
    if str(data.get("canonicalAgialpha", "")).lower() != CANONICAL_AGIALPHA.lower():
        die("release manifest canonical AGIALPHA mismatch")
    addresses = data.get("goalosContractAddresses")
    expected = {c["address"].lower() for c in registry if c["classification"] == "deployed"}
    if not isinstance(addresses, list) or {str(v).lower() for v in addresses} != expected:
        die("release manifest GoalOS contract addresses do not match registry")
    if len(data.get("deploymentTransactionHashes", [])) != 48:
        die("release manifest must contain 48 deployment transaction hashes")
    if len(data.get("phaseBGrants", [])) != 14:
        die("release manifest must contain 14 Phase-B grants")
    if data.get("productionActivated") is not False or data.get("userFundsAuthorized") is not False:
        die("release manifest safety boundary is not fail-closed")
    compiler = data.get("compilerSettings", {})
    if compiler.get("solidity") != "0.8.28" or compiler.get("hardhat") != "2.28.6":
        die("release manifest compiler/tool versions are unexpected")
    wallet_b = data.get("walletB")
    if not isinstance(wallet_b, str) or not ADDRESS_RE.fullmatch(wallet_b):
        die("release manifest Wallet B address is invalid")
    return data


def validate_deployment_evidence(path: Path) -> dict[str, Any]:
    data = load_json(path)
    state = data.get("releaseState") if isinstance(data, dict) else None
    if not isinstance(state, dict):
        die("deployment evidence has no releaseState")
    summary = state.get("summary", {})
    required = {
        "ETHEREUM_MAINNET_DEPLOYED": "YES",
        "MAINNET_CONFIGURED": "YES",
        "MAINNET_VERIFIED": "YES",
        "PHASE_B_GRANTS": "14/14",
        "PRODUCTION_ACTIVATION_EFFECTIVE": "NO",
        "USER_FUNDS_AUTHORIZED": "NO",
        "LIVE_CANARY_COMPLETE": "NO",
    }
    for key, expected in required.items():
        if summary.get(key) != expected:
            die(f"deployment evidence {key} must be {expected}")
    if summary.get("WALLET_A_RESIDUAL_MANAGED_ROLES") != 0:
        die("deployment evidence must record zero residual Wallet-A managed roles")
    return state


def extract_header(index_html: str) -> str:
    match = re.search(r"(<a class=['\"]skip['\"][\s\S]*?</header>)", index_html, re.IGNORECASE)
    if not match:
        die("could not preserve the existing site header from index.html")
    header = match.group(1)
    if "ethereum-mainnet.html" not in header:
        header = header.replace(
            "</nav>",
            "<a href='ethereum-mainnet.html' aria-current='page'>Mainnet</a></nav>",
            1,
        )
    return header


def contract_link(entry: dict[str, Any]) -> str:
    name = html.escape(entry["name"])
    address = html.escape(entry["address"])
    url = html.escape(str(entry.get("etherscanUrl") or f"https://etherscan.io/address/{entry['address']}"))
    if "#" not in url:
        url += "#code"
    classification = html.escape(entry["classification"])
    badge = "External dependency" if classification == "external" else "Verified contract"
    return (
        f"<li class='mn-contract-item'>"
        f"<a data-mainnet-contract='true' data-classification='{classification}' "
        f"data-address='{address}' href='{url}' target='_blank' rel='noopener noreferrer'>"
        f"<span class='mn-contract-copy'><strong>{name}</strong><code>{address}</code></span>"
        f"<span class='mn-contract-badge'>{badge}<span aria-hidden='true'>↗</span></span>"
        f"</a></li>"
    )

def make_page(index_html: str, by_name: dict[str, dict[str, Any]], manifest: dict[str, Any], operator_verified: int, independent: str) -> str:
    header = extract_header(index_html)
    group_html: list[str] = []
    for number, (title, names) in enumerate(GROUPS, start=1):
        items = "".join(contract_link(by_name[name]) for name in names)
        group_html.append(
            "<details class='mn-group'>"
            f"<summary><span class='mn-group-index'>{number:02d}</span>"
            f"<span class='mn-group-title'>{html.escape(title)}</span>"
            f"<span class='mn-group-count'>{len(names)} contracts</span>"
            "<span class='mn-group-chevron' aria-hidden='true'></span></summary>"
            f"<ul class='mn-contract-grid'>{items}</ul>"
            "</details>"
        )

    agialpha = by_name["AGIALPHA"]
    agialpha_address = html.escape(agialpha["address"])
    agialpha_url = html.escape(str(agialpha.get("etherscanUrl") or f"https://etherscan.io/address/{agialpha['address']}"))
    wallet_b = html.escape(manifest["walletB"])
    wallet_b_url = f"https://etherscan.io/address/{wallet_b}"
    source_identity = html.escape(str(manifest.get("sourceIdentityClassification", "SOURCE_IDENTITY_NOT_PROVEN")))
    target_sha = html.escape(str(manifest.get("targetGitSha", "not-recorded")))
    deployed_at = html.escape(str(manifest.get("deployedAt", "2026-06-21")))
    configured_at = html.escape(str(manifest.get("configuredAt", "2026-06-21")))

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Ethereum Mainnet Deployment Record — GoalOS AGIALPHA Ascension</title>
<meta name='description' content='Institutional Ethereum Mainnet deployment record for GoalOS AGIALPHA Ascension: 48 GoalOS contracts, Etherscan verification evidence, governance status, and explicit activation boundaries.'>
<meta property='og:title' content='GoalOS AGIALPHA Ascension — Ethereum Mainnet Deployment Record'>
<meta property='og:description' content='48 GoalOS contracts, public Etherscan records, configured governance, and explicit production boundaries.'>
<meta name='theme-color' content='#07111f'>
<meta name='color-scheme' content='light'>
<link rel='stylesheet' href='assets/goalos-v86-preserve.css'>
<style id='goalos-v86-critical'>html{{scroll-behavior:smooth}}body{{margin:0;overflow-x:clip}}img,svg,canvas,video,iframe{{max-width:100%;height:auto}}main{{min-height:70vh}}</style>
<style id='goalos-mainnet-v88-design'>
:root{{
  --mn-ink:#07111f;--mn-muted:#5c697c;--mn-paper:#f7f4ec;--mn-surface:#fff;
  --mn-navy:#07111f;--mn-navy-2:#0d213d;--mn-gold:#f0bd4f;--mn-gold-soft:#fff2bd;
  --mn-cyan:#77e7f4;--mn-green:#62d89a;--mn-rose:#ef7f97;--mn-line:rgba(7,17,31,.13);
  --mn-shadow:0 28px 90px rgba(7,17,31,.13);--mn-radius:28px;
}}
*{{box-sizing:border-box}}html{{width:100%;max-width:100%;overflow-x:hidden;background:var(--mn-paper)}}
body.mn-page{{width:100%;max-width:100%;margin:0;overflow-x:hidden;background:radial-gradient(circle at 8% 0%,rgba(240,189,79,.16),transparent 28rem),radial-gradient(circle at 100% 10%,rgba(119,231,244,.13),transparent 34rem),var(--mn-paper);color:var(--mn-ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}}
body.mn-page a{{color:inherit}}body.mn-page .skip{{position:absolute;left:-9999px;top:auto}}
body.mn-page .skip:focus{{left:18px;top:18px;z-index:9999;background:#fff;color:var(--mn-ink);padding:11px 16px;border-radius:999px;box-shadow:var(--mn-shadow)}}
body.mn-page .top{{position:sticky;top:0;z-index:100;background:rgba(247,244,236,.94);border-bottom:1px solid var(--mn-line);backdrop-filter:blur(18px)}}
body.mn-page .topin{{width:min(1240px,calc(100% - 32px));max-width:calc(100% - 32px);min-width:0;margin:0 auto;min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:24px}}
body.mn-page .topin>*{{min-width:0;max-width:100%}}
body.mn-page .brand{{display:inline-flex;align-items:center;gap:10px;text-decoration:none;font-size:.82rem;font-weight:950;letter-spacing:.09em;text-transform:uppercase;white-space:nowrap}}
body.mn-page .mark{{width:34px;height:34px;border-radius:12px;background:conic-gradient(from 160deg,var(--mn-gold),var(--mn-cyan),#8e8bff,var(--mn-gold));box-shadow:0 0 0 5px rgba(240,189,79,.12)}}
body.mn-page .nav{{display:flex;align-items:center;justify-content:flex-end;gap:3px;width:auto;max-width:100%;min-width:0;overflow-x:auto;overflow-y:hidden;overscroll-behavior-inline:contain;scrollbar-width:none}}
body.mn-page .nav::-webkit-scrollbar{{display:none}}body.mn-page .nav a{{text-decoration:none;color:#34445c;font-size:.78rem;font-weight:850;padding:9px 10px;border-radius:999px;white-space:nowrap}}
body.mn-page .nav a:hover,body.mn-page .nav a:focus-visible{{background:#fff;color:var(--mn-ink);outline:none}}body.mn-page .nav a[aria-current='page']{{background:var(--mn-ink);color:#fff}}
.mn-container{{width:min(1180px,calc(100% - 36px));max-width:calc(100% - 36px);min-width:0;margin-inline:auto;position:relative;z-index:2}}
.mn-container>*,.mn-section-header,.mn-registry-intro,.mn-registry-intro>*,.mn-dependency>*,.mn-governance>*,.mn-provenance>*,.mn-group,.mn-contract-grid,.mn-contract-item,.mn-contract-copy{{min-width:0;max-width:100%}}
.mn-hero{{position:relative;overflow:hidden;background:radial-gradient(circle at 13% 18%,rgba(119,231,244,.22),transparent 26rem),radial-gradient(circle at 85% 8%,rgba(240,189,79,.20),transparent 30rem),linear-gradient(135deg,#050a13 0%,#0a1b32 58%,#171537 100%);color:#fff;padding:clamp(74px,9vw,126px) 0 72px;border-radius:0 0 58px 58px;box-shadow:0 34px 100px rgba(7,17,31,.28)}}
.mn-hero:before{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.065) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.065) 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(#000,transparent 93%);opacity:.72}}
.mn-hero:after{{content:'';position:absolute;inset:auto -20% -45% -20%;height:70%;background:radial-gradient(ellipse at center,rgba(240,189,79,.25),transparent 62%)}}
.mn-eyebrow{{display:inline-flex;align-items:center;gap:9px;color:var(--mn-gold-soft);font-size:.76rem;font-weight:950;letter-spacing:.17em;text-transform:uppercase}}.mn-eyebrow:before{{content:'';width:32px;height:1px;background:currentColor}}
.mn-hero h1{{max-width:1000px;margin:18px 0 20px;font-size:clamp(3.2rem,8.4vw,7.8rem);line-height:.88;letter-spacing:-.078em;text-wrap:balance}}.mn-hero h1 span{{color:var(--mn-gold-soft)}}
.mn-hero-lead{{max-width:850px;margin:0;color:#dfe9f7;font-size:clamp(1.05rem,2vw,1.35rem);font-weight:620;line-height:1.7}}
.mn-metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:34px}}
.mn-metric{{min-height:128px;border:1px solid rgba(255,255,255,.16);background-color:rgba(255,255,255,.085);border-radius:22px;padding:18px;backdrop-filter:blur(14px)}}.mn-metric strong{{display:block;color:var(--mn-gold-soft);font-size:clamp(1.65rem,3vw,2.65rem);line-height:1.05;letter-spacing:-.04em}}.mn-metric span{{display:block;margin-top:8px;color:#e5edf8;font-size:.78rem;font-weight:850;line-height:1.35}}
.mn-actions{{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}}.mn-btn{{min-height:48px;display:inline-flex;align-items:center;justify-content:center;gap:9px;text-decoration:none;border-radius:999px;padding:12px 19px;font-weight:930;font-size:.92rem;border:1px solid transparent;transition:transform .18s ease,box-shadow .18s ease}}
.mn-btn:hover{{transform:translateY(-2px)}}.mn-btn:focus-visible{{outline:3px solid var(--mn-cyan);outline-offset:3px}}
body.mn-page .mn-btn--primary{{background-color:#f5c75e;background-image:linear-gradient(135deg,#f7d878,#efb840);color:#111827;box-shadow:0 18px 50px rgba(240,189,79,.28)}}body.mn-page .mn-btn--secondary{{background-color:#fff;color:#101b2d;border-color:#fff;box-shadow:0 15px 42px rgba(0,0,0,.18)}}body.mn-page .mn-btn--ghost{{background-color:#13243b;color:#fff;border-color:rgba(255,255,255,.24)}}
.mn-section{{padding:clamp(70px,8vw,112px) 0}}.mn-section--white{{background:rgba(255,255,255,.78)}}.mn-section--dark{{position:relative;background:linear-gradient(135deg,#07111f,#0d213d);color:#fff;overflow:hidden}}
.mn-section--dark:before{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:44px 44px;opacity:.5}}
.mn-section-header{{max-width:870px;margin-bottom:34px}}.mn-section-header h2{{margin:8px 0 14px;font-size:clamp(2.15rem,5.2vw,4.9rem);line-height:.97;letter-spacing:-.065em;text-wrap:balance}}.mn-section-header p{{margin:0;color:var(--mn-muted);font-size:1.06rem;line-height:1.75}}.mn-section--dark .mn-section-header p{{color:#cbd9e9}}
.mn-label{{color:#8b651c;font-size:.75rem;font-weight:950;letter-spacing:.16em;text-transform:uppercase}}.mn-section--dark .mn-label{{color:var(--mn-gold-soft)}}
.mn-boundaries{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}.mn-boundary{{min-height:170px;border-radius:var(--mn-radius);padding:22px;border:1px solid var(--mn-line);background:var(--mn-surface);box-shadow:0 18px 50px rgba(7,17,31,.08)}}.mn-boundary--yes{{border-top:4px solid var(--mn-green)}}.mn-boundary--no{{border-top:4px solid var(--mn-rose)}}.mn-boundary strong{{display:block;font-size:1.15rem;color:var(--mn-ink)}}.mn-boundary p{{margin:10px 0 0;color:var(--mn-muted)}}
.mn-dependency{{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:18px;align-items:stretch}}.mn-card{{min-width:0;max-width:100%;border:1px solid var(--mn-line);background-color:var(--mn-surface);border-radius:var(--mn-radius);padding:clamp(22px,3vw,32px);box-shadow:var(--mn-shadow)}}.mn-card--dark{{background-color:#10233e;color:#fff;border-color:rgba(255,255,255,.15)}}.mn-card h3{{margin:0 0 12px;font-size:1.35rem;letter-spacing:-.03em}}.mn-card p{{margin:0;color:var(--mn-muted)}}.mn-card--dark p{{color:#ccdae9}}
.mn-address{{min-width:0;max-width:100%;display:flex;align-items:center;justify-content:space-between;gap:14px;margin-top:22px;padding:14px 16px;border-radius:18px;background-color:#f2f5f8;border:1px solid var(--mn-line);text-decoration:none}}.mn-card--dark .mn-address{{background-color:#09172a;border-color:rgba(255,255,255,.14)}}.mn-address code{{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.82rem}}.mn-address span{{font-weight:900;color:#7b5915;white-space:nowrap}}.mn-card--dark .mn-address span{{color:var(--mn-gold-soft)}}
.mn-governance{{min-width:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.mn-registry-intro{{min-width:0;display:flex;align-items:end;justify-content:space-between;gap:24px;margin-bottom:26px}}.mn-registry-intro .mn-section-header{{min-width:0;margin:0}}.mn-registry-chip{{display:inline-flex;align-items:center;justify-content:center;gap:8px;max-width:100%;border-radius:999px;background:#e8f8ef;color:#14532d;padding:9px 13px;font-size:.78rem;font-weight:900;line-height:1.35;white-space:normal;overflow-wrap:anywhere;text-align:center}}
.mn-group{{border:1px solid var(--mn-line);background-color:#fff;border-radius:22px;margin:12px 0;overflow:hidden;box-shadow:0 12px 32px rgba(7,17,31,.055)}}.mn-group summary{{min-height:68px;cursor:pointer;display:grid;grid-template-columns:42px 1fr auto 18px;align-items:center;gap:13px;padding:15px 18px;list-style:none;color:var(--mn-ink)}}.mn-group summary::-webkit-details-marker{{display:none}}.mn-group summary:hover{{background:#faf8f1}}.mn-group-index{{display:grid;place-items:center;width:38px;height:38px;border-radius:13px;background:#0d213d;color:#fff;font-size:.75rem;font-weight:950}}.mn-group-title{{font-weight:920}}.mn-group-count{{color:#8b651c;font-size:.78rem;font-weight:900;white-space:nowrap}}.mn-group-chevron{{width:10px;height:10px;border-right:2px solid #5f6c7e;border-bottom:2px solid #5f6c7e;transform:rotate(45deg);transition:transform .2s ease}}.mn-group[open] .mn-group-chevron{{transform:rotate(225deg)}}
.mn-contract-grid{{list-style:none;margin:0;padding:0 16px 18px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}.mn-contract-item a{{min-height:88px;display:flex;align-items:center;justify-content:space-between;gap:14px;text-decoration:none;border:1px solid var(--mn-line);border-radius:17px;padding:14px;background-color:#f8fafc;transition:border-color .18s ease,transform .18s ease,box-shadow .18s ease}}.mn-contract-item a:hover{{transform:translateY(-2px);border-color:#79aee8;box-shadow:0 14px 30px rgba(7,17,31,.09)}}.mn-contract-copy{{min-width:0}}.mn-contract-copy strong{{display:block;color:var(--mn-ink);font-size:.88rem}}.mn-contract-copy code{{display:block;margin-top:5px;color:#5d6b7e;font-size:.69rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.mn-contract-badge{{display:flex;align-items:center;gap:6px;color:#7b5915;font-size:.7rem;font-weight:900;white-space:nowrap}}
.mn-provenance{{min-width:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.mn-card p,.mn-card code,.mn-section-header,.mn-group-title,.mn-contract-copy strong,.mn-claim{{max-width:100%;overflow-wrap:anywhere;word-break:break-word}}.mn-provenance code{{display:inline;max-width:100%;white-space:normal;overflow-wrap:anywhere;word-break:break-all}}.mn-claim{{margin-top:18px;border:1px solid rgba(239,127,151,.30);background:#fff1f4;border-radius:22px;padding:18px;color:#5f2432}}.mn-footer{{background:#050b14;color:#dce6f3;padding:36px 0}}.mn-footer-inner{{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}}.mn-footer strong{{color:#fff}}.mn-footer p{{margin:6px 0 0;color:#99a9bd;font-size:.84rem}}.mn-footer a{{color:var(--mn-gold-soft);text-decoration:none;font-weight:850}}
@media(max-width:980px){{body.mn-page .topin{{align-items:flex-start;padding:12px 0;flex-direction:column;gap:8px}}body.mn-page .nav{{width:100%;max-width:100%;min-width:0;justify-content:flex-start;padding-bottom:3px}}.mn-metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}.mn-dependency,.mn-governance,.mn-provenance{{grid-template-columns:minmax(0,1fr)}}}}
@media(max-width:700px){{.mn-container{{width:calc(100% - 24px);max-width:calc(100% - 24px)}}.mn-hero{{padding-top:62px;border-radius:0 0 34px 34px}}.mn-hero h1{{font-size:clamp(3rem,16vw,5rem)}}.mn-metrics,.mn-boundaries,.mn-contract-grid{{grid-template-columns:minmax(0,1fr)}}.mn-registry-intro{{display:block}}.mn-registry-chip{{display:flex;width:100%;max-width:100%;margin-top:16px;white-space:normal;overflow-wrap:anywhere;text-align:center}}.mn-group summary{{grid-template-columns:38px minmax(0,1fr) 16px}}.mn-group-count{{grid-column:2;font-size:.72rem;white-space:normal;overflow-wrap:anywhere}}.mn-group-chevron{{grid-column:3;grid-row:1 / span 2}}.mn-contract-item a{{align-items:flex-start;flex-direction:column;max-width:100%;overflow:hidden}}.mn-address{{align-items:flex-start;flex-direction:column;width:100%;max-width:100%;overflow:hidden}}.mn-address code{{width:100%;max-width:100%}}.mn-actions{{width:100%}}.mn-actions .mn-btn{{max-width:100%;white-space:normal;text-align:center}}.mn-footer-inner{{display:block}}.mn-footer-inner>div+div{{margin-top:14px}}}}
@media(prefers-reduced-motion:reduce){{*,*:before,*:after{{scroll-behavior:auto!important;transition:none!important;animation:none!important}}}}
</style>
</head>
<body class='mn-page goalos-v86-preserved' data-design-version='v88-institutional'>
{header}
<main id='main'>
<section class='mn-hero'><div class='mn-container'>
<div class='mn-eyebrow'>Ethereum Mainnet · institutional deployment record</div>
<h1>Proof moved from rehearsal to <span>chain&nbsp;1.</span></h1>
<p class='mn-hero-lead'>GoalOS AGIALPHA Ascension now has a recorded Ethereum Mainnet deployment and completed operator configuration. This page consolidates the canonical registry, public Etherscan records, governance status, release evidence, and the boundaries that remain intentionally disabled.</p>
<div class='mn-metrics' aria-label='Ethereum Mainnet deployment summary'>
<div class='mn-metric'><strong>48</strong><span>GoalOS-created contracts</span></div>
<div class='mn-metric'><strong>{operator_verified}/48</strong><span>operator Etherscan verification records</span></div>
<div class='mn-metric'><strong>14/14</strong><span>configuration grants recorded active</span></div>
<div class='mn-metric'><strong>CONFIGURED</strong><span>deployment status</span></div>
</div>
<div class='mn-actions'>
<a class='mn-btn mn-btn--primary' href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>Open published pre-release <span aria-hidden='true'>↗</span></a>
<a class='mn-btn mn-btn--secondary' href='#contracts'>Inspect contract registry</a>
<a class='mn-btn mn-btn--ghost' href='index.html'>Return home</a>
</div></div></section>
<section class='mn-section mn-section--white'><div class='mn-container'>
<div class='mn-section-header'><div class='mn-label'>Current operating boundary</div><h2>Deployment is recorded. Production activation remains separate.</h2><p>The public record supports deployment, configuration, and operator verification evidence. It does not authorize user funds, enable production write flows, claim an external audit, or convert the pre-release into a production-activation certificate.</p></div>
<div class='mn-boundaries'>
<article class='mn-boundary mn-boundary--yes' data-status='deployment' data-value='YES'><strong>Deployment record: YES</strong><p>Ethereum Mainnet, chain ID 1.</p></article>
<article class='mn-boundary mn-boundary--yes' data-status='configuration' data-value='YES'><strong>Configuration: YES</strong><p>Phase-B grants: 14/14; Wallet-A managed roles: 0.</p></article>
<article class='mn-boundary mn-boundary--no' data-status='production-activation' data-value='NO'><strong>Production activation: NO</strong><p>Live canary, user-fund authorization, and public production reliance remain disabled.</p></article>
</div></div></section>
<section class='mn-section mn-section--dark'><div class='mn-container'>
<div class='mn-section-header'><div class='mn-label'>Canonical dependency</div><h2>One external AGIALPHA. No replacement token.</h2><p>GoalOS integrates the existing canonical AGIALPHA contract. The GoalOS deployment did not create or mint a substitute token.</p></div>
<div class='mn-dependency'>
<article class='mn-card mn-card--dark'><h3>Canonical AGIALPHA</h3><p>External dependency · not deployed or minted by GoalOS.</p><a class='mn-address' data-mainnet-contract='true' data-classification='external' data-address='{agialpha_address}' href='{agialpha_url}#code' target='_blank' rel='noopener noreferrer'><code>{agialpha_address}</code><span>View source ↗</span></a></article>
<article class='mn-card mn-card--dark'><h3>Protocol boundary</h3><p>The public record distinguishes GoalOS infrastructure from the existing token dependency and preserves the no-replacement-token boundary.</p></article>
</div></div></section>
<section class='mn-section mn-section--white'><div class='mn-container'>
<div class='mn-section-header'><div class='mn-label'>Governance and authority</div><h2>Permanent authority is Ledger-controlled.</h2><p>Operational control is recorded under Wallet B. The disposable deployment wallet has zero managed roles in the reconciled release state.</p></div>
<div class='mn-governance'>
<article class='mn-card'><h3>Permanent authority</h3><p>Wallet B is the recorded permanent authority.</p><a class='mn-address' href='{wallet_b_url}' target='_blank' rel='noopener noreferrer'><code>{wallet_b}</code><span>Etherscan ↗</span></a></article>
<article class='mn-card'><h3>Verification boundary</h3><p>Operator verification evidence records {operator_verified}/48 GoalOS-created contracts. Independent dual-provider release revalidation is <strong>{independent}</strong> unless a later evidence update explicitly changes that status.</p><p style='margin-top:14px'>Source identity classification: <code>{source_identity}</code>.</p></article>
</div></div></section>
<section class='mn-section' id='contracts'><div class='mn-container'>
<div class='mn-registry-intro'><div class='mn-section-header'><div class='mn-label'>Public registry</div><h2>Every GoalOS Mainnet contract, one click from source.</h2><p>The registry contains 48 GoalOS-created contracts. The canonical external AGIALPHA dependency is documented separately above. Every contract entry opens its public Etherscan source page in a new tab.</p></div><div class='mn-registry-chip'>48 GoalOS contracts · 0 operator-verification failures</div></div>
{''.join(group_html)}
</div></section>
<section class='mn-section mn-section--white'><div class='mn-container'>
<div class='mn-section-header'><div class='mn-label'>Evidence and provenance</div><h2>Public record, explicit limits.</h2><p>The release packet binds the deployment record, contract registry, configuration evidence, compiler alignment, and checksum material while preserving pending independent-revalidation and source-provenance boundaries.</p></div>
<div class='mn-provenance'>
<article class='mn-card'><h3>Published release</h3><p><a href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'><strong>{RELEASE_TAG}</strong></a></p><p style='margin-top:14px'>Deployment recorded at <code>{deployed_at}</code>; configuration recorded at <code>{configured_at}</code>.</p></article>
<article class='mn-card'><h3>Tagged source record</h3><p>Release target SHA:</p><p style='margin-top:10px'><code>{target_sha}</code></p><p style='margin-top:14px'>Exact tagged-commit-to-deployed-bytecode reproduction remains a separate provenance exercise unless later evidence records completion.</p></article>
</div>
<div class='mn-claim'><strong>Claim boundary.</strong> This page does not claim achieved AGI, achieved ASI, superintelligence achievement, guaranteed ROI, token appreciation, external audit completion, production certification, user-fund authorization, or live production settlement.</div>
</div></section>
</main>
<footer class='mn-footer'><div class='mn-container mn-footer-inner'><div><strong>GoalOS AGIALPHA Ascension</strong><p>Evidence-first Ethereum Mainnet deployment record.</p></div><div><a href='index.html'>Home</a> · <a href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>GitHub release</a></div></div></footer>
<script defer src='assets/goalos-v86-dynamic-ai.js'></script>
</body></html>
"""


def home_styles() -> str:
    return f"""{HOME_STYLE_START}
<style id='goalos-mainnet-v88-home-design'>
#ethereum-mainnet-record{{padding:72px 18px;background:transparent}}#ethereum-mainnet-record *{{box-sizing:border-box}}
#ethereum-mainnet-record .mn-home-shell{{width:min(1260px,100%);margin:0 auto;position:relative;overflow:hidden;border-radius:42px;padding:clamp(30px,5vw,64px);background:radial-gradient(circle at 12% 18%,rgba(119,231,244,.21),transparent 26rem),radial-gradient(circle at 88% 2%,rgba(240,189,79,.22),transparent 28rem),linear-gradient(135deg,#06111f,#0d213d 62%,#171537);color:#fff;box-shadow:0 32px 100px rgba(7,17,31,.25)}}
#ethereum-mainnet-record .mn-home-shell:before{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.06) 1px,transparent 1px);background-size:42px 42px;opacity:.55;pointer-events:none}}
#ethereum-mainnet-record .mn-home-inner{{position:relative;z-index:1;display:grid;grid-template-columns:1.08fr .92fr;gap:32px;align-items:end}}
#ethereum-mainnet-record .mn-home-kicker{{color:#fff2bd;font-size:.76rem;font-weight:950;letter-spacing:.17em;text-transform:uppercase}}
#ethereum-mainnet-record h2{{margin:12px 0 16px;color:#fff;font-size:clamp(2.55rem,5.6vw,5.8rem);line-height:.92;letter-spacing:-.068em;text-wrap:balance}}
#ethereum-mainnet-record .mn-home-lead{{margin:0;max-width:760px;color:#dce7f4;font-size:1.06rem;line-height:1.72}}
#ethereum-mainnet-record .mn-home-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}
#ethereum-mainnet-record .mn-home-stat{{min-height:138px;padding:18px;border:1px solid rgba(255,255,255,.16);background-color:rgba(255,255,255,.09);border-radius:22px;backdrop-filter:blur(13px)}}
#ethereum-mainnet-record .mn-home-stat strong{{display:block;color:#fff2bd;font-size:1.65rem;line-height:1.05}}
#ethereum-mainnet-record .mn-home-stat span{{display:block;margin-top:8px;color:#e6edf7;font-size:.8rem;font-weight:820;line-height:1.42}}
#ethereum-mainnet-record .mn-home-actions{{position:relative;z-index:1;display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}}
#ethereum-mainnet-record .mn-home-btn{{min-height:48px;display:inline-flex;align-items:center;justify-content:center;text-decoration:none;border-radius:999px;padding:12px 18px;font-size:.9rem;font-weight:930;transition:transform .18s ease,box-shadow .18s ease}}
#ethereum-mainnet-record .mn-home-btn:hover{{transform:translateY(-2px)}}#ethereum-mainnet-record .mn-home-btn:focus-visible{{outline:3px solid #77e7f4;outline-offset:3px}}
#ethereum-mainnet-record .mn-home-btn--primary{{background-color:#f5c75e;background-image:linear-gradient(135deg,#f7d878,#efb840);color:#111827;box-shadow:0 17px 46px rgba(240,189,79,.28)}}
#ethereum-mainnet-record .mn-home-btn--secondary{{background-color:#fff;color:#101b2d;border:1px solid #fff;box-shadow:0 15px 42px rgba(0,0,0,.20)}}
@media(max-width:900px){{#ethereum-mainnet-record .mn-home-inner{{grid-template-columns:1fr}}}}
@media(max-width:620px){{#ethereum-mainnet-record{{padding:48px 12px}}#ethereum-mainnet-record .mn-home-shell{{border-radius:28px;padding:28px 20px}}#ethereum-mainnet-record .mn-home-grid{{grid-template-columns:1fr}}#ethereum-mainnet-record .mn-home-btn{{width:100%}}}}
</style>
{HOME_STYLE_END}"""


def make_home_block(operator_verified: int, independent: str) -> str:
    return f"""{HOME_START}
<section id='ethereum-mainnet-record' data-mainnet-home-card='v87' aria-labelledby='mainnet-home-title'>
<div class='mn-home-shell'><div class='mn-home-inner'>
<div><div class='mn-home-kicker'>Ethereum Mainnet · deployment record</div><h2 id='mainnet-home-title'>48 GoalOS contracts now have a public chain‑1 record.</h2><p class='mn-home-lead'>The canonical deployment is recorded as configured, with {operator_verified}/48 operator Etherscan verification records and 14/14 configuration grants. Independent release revalidation is {independent.lower()}. Production activation, user-fund authorization, and public production reliance remain disabled.</p></div>
<div class='mn-home-grid' aria-label='Ethereum Mainnet deployment summary'>
<div class='mn-home-stat'><strong>48 contracts</strong><span>GoalOS-created Mainnet components, plus one external canonical AGIALPHA dependency.</span></div>
<div class='mn-home-stat'><strong>{operator_verified}/48</strong><span>Public operator verification records with direct Etherscan links.</span></div>
<div class='mn-home-stat'><strong>14/14 grants</strong><span>Postdeployment configuration recorded active under Ledger-controlled authority.</span></div>
<div class='mn-home-stat'><strong>Activation: NO</strong><span>Production activation and user-fund authorization remain disabled.</span></div>
</div></div>
<div class='mn-home-actions'><a class='mn-home-btn mn-home-btn--primary' href='ethereum-mainnet.html'>Open the Ethereum Mainnet record</a><a class='mn-home-btn mn-home-btn--secondary' href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>View the published pre-release ↗</a></div>
</div></section>
{HOME_END}"""


def inject_home_styles(index_html: str, styles: str) -> str:
    pattern = re.compile(re.escape(HOME_STYLE_START) + r"[\s\S]*?" + re.escape(HOME_STYLE_END))
    if pattern.search(index_html):
        return pattern.sub(styles, index_html, count=1)
    close_head = index_html.lower().find("</head>")
    if close_head < 0:
        die("index.html has no closing head tag")
    return index_html[:close_head] + "\n" + styles + "\n" + index_html[close_head:]
def inject_homepage(index_html: str, block: str) -> str:
    pattern = re.compile(re.escape(HOME_START) + r"[\s\S]*?" + re.escape(HOME_END))
    if pattern.search(index_html):
        return pattern.sub(block, index_html, count=1)
    main_start = index_html.find("<main id='main'>")
    if main_start < 0:
        main_start = index_html.find('<main id="main">')
    if main_start < 0:
        die("index.html has no main landmark")
    first_close = index_html.find("</section>", main_start)
    if first_close >= 0:
        pos = first_close + len("</section>")
        return index_html[:pos] + "\n" + block + "\n" + index_html[pos:]
    close_main = index_html.find("</main>", main_start)
    if close_main < 0:
        die("index.html has no closing main tag")
    return index_html[:close_main] + block + "\n" + index_html[close_main:]


def write_sitemap(site: Path) -> None:
    pages = sorted(p.name for p in site.glob("*.html"))
    lines = ["<?xml version='1.0' encoding='UTF-8'?>", "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    lines.extend(f"  <url><loc>{BASE_URL}{html.escape(name)}</loc></url>" for name in pages)
    lines.append("</urlset>")
    (site / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_site_status(site: Path, operator_verified: int, independent: str) -> None:
    path = site / "site-status.json"
    status: dict[str, Any] = {}
    if path.is_file():
        loaded = load_json(path)
        if isinstance(loaded, dict):
            status.update(loaded)
    status.update({
        "ethereum_mainnet_page": "ethereum-mainnet.html",
        "ethereum_mainnet_release": RELEASE_TAG,
        "ethereum_mainnet_chain_id": 1,
        "ethereum_mainnet_registry_entries": 49,
        "goalos_mainnet_contracts": 48,
        "operator_etherscan_verification": f"{operator_verified}/48",
        "independent_release_revalidation": independent,
        "mainnet_configured": True,
        "production_activated": False,
        "user_funds_authorized": False,
    })
    path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a non-destructive Ethereum Mainnet page to the generated GoalOS v86 Pages artifact")
    parser.add_argument("--site", default="site")
    parser.add_argument("--registry", default="config/ethereum-mainnet.contracts.json")
    parser.add_argument("--release-contracts", default="release/mainnet-2026-06-21/CONTRACTS_MAINNET.json")
    parser.add_argument("--release-manifest", default="release/mainnet-2026-06-21/RELEASE_MANIFEST.json")
    parser.add_argument("--deployment-evidence", default="release/mainnet-2026-06-21/DEPLOYMENT_EVIDENCE.json")
    args = parser.parse_args()

    site = Path(args.site)
    index_path = site / "index.html"
    if not index_path.is_file():
        print(f"ERROR: generated site is missing {index_path}", file=sys.stderr)
        return 2

    try:
        registry, by_name = validate_registry(Path(args.registry))
        operator_verified, independent = validate_release_contracts(Path(args.release_contracts), registry)
        manifest = validate_release_manifest(Path(args.release_manifest), registry)
        validate_deployment_evidence(Path(args.deployment_evidence))
        index_before = index_path.read_text(encoding="utf-8")
        page = make_page(index_before, by_name, manifest, operator_verified, independent)
        styled_index = inject_home_styles(index_before, home_styles())
        home = inject_homepage(styled_index, make_home_block(operator_verified, independent))

        page_path = site / "ethereum-mainnet.html"
        page_path.write_text(page, encoding="utf-8")
        index_path.write_text(home, encoding="utf-8")
        write_sitemap(site)
        update_site_status(site, operator_verified, independent)

        qa = site / "qa"
        qa.mkdir(exist_ok=True)
        report = {
            "status": "PASS",
            "mode": "non-destructive-generated-artifact-augmentation",
            "source_directory_modified": False,
            "homepage_marker": "GOALOS_MAINNET_V87",
            "page": page_path.name,
            "registry_entries": 49,
            "goalos_contracts": 48,
            "operator_verified": operator_verified,
            "independent_revalidation": independent,
            "release": RELEASE_TAG,
            "hashes": {
                "registry": sha256(Path(args.registry)),
                "releaseContracts": sha256(Path(args.release_contracts)),
                "releaseManifest": sha256(Path(args.release_manifest)),
                "deploymentEvidence": sha256(Path(args.deployment_evidence)),
                "generatedPage": sha256(page_path),
                "generatedHomepage": sha256(index_path),
            },
        }
        (qa / "mainnet-page-build-v87.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
