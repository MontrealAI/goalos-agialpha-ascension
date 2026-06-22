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
    if not isinstance(data, dict) or data.get("chainId") != 1:
        die("contract registry must be an object with chainId 1")
    contracts = data.get("contracts")
    if not isinstance(contracts, list) or len(contracts) != 49:
        die("contract registry must contain exactly 49 entries")

    seen_addresses: set[str] = set()
    seen_names: set[str] = set()
    by_name: dict[str, dict[str, Any]] = {}
    deployed = 0
    external = 0

    for entry in contracts:
        if not isinstance(entry, dict):
            die("every registry entry must be an object")
        name = entry.get("name")
        address = entry.get("address")
        classification = entry.get("classification")
        if not isinstance(name, str) or not name:
            die("registry entry has no valid name")
        if not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            die(f"invalid Ethereum address for {name}")
        if entry.get("chainId") != 1:
            die(f"wrong chainId for {name}")
        if classification not in {"deployed", "external"}:
            die(f"invalid classification for {name}")
        key = address.lower()
        if key in seen_addresses:
            die(f"duplicate contract address: {address}")
        if name in seen_names:
            die(f"duplicate contract name: {name}")
        seen_addresses.add(key)
        seen_names.add(name)
        by_name[name] = entry
        deployed += classification == "deployed"
        external += classification == "external"

    if deployed != 48 or external != 1:
        die(f"expected 48 deployed and 1 external entries, got {deployed} and {external}")
    agialpha = by_name.get("AGIALPHA")
    if not agialpha or agialpha["address"].lower() != CANONICAL_AGIALPHA.lower() or agialpha["classification"] != "external":
        die("canonical external AGIALPHA entry is missing or incorrect")

    grouped_names = {name for _, names in GROUPS for name in names}
    deployed_names = {c["name"] for c in contracts if c["classification"] == "deployed"}
    if grouped_names != deployed_names:
        missing = sorted(deployed_names - grouped_names)
        stale = sorted(grouped_names - deployed_names)
        die(f"contract grouping mismatch; missing={missing}, stale={stale}")
    return contracts, by_name


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
    return (
        f"<li><a data-mainnet-contract='true' data-classification='{classification}' "
        f"data-address='{address}' href='{url}' target='_blank' rel='noopener noreferrer'>"
        f"<strong>{name}</strong><span>{address}</span></a></li>"
    )


def make_page(index_html: str, by_name: dict[str, dict[str, Any]], manifest: dict[str, Any], operator_verified: int, independent: str) -> str:
    header = extract_header(index_html)
    group_html: list[str] = []
    for title, names in GROUPS:
        items = "".join(contract_link(by_name[name]) for name in names)
        group_html.append(
            "<details class='mainnet-group'>"
            f"<summary><span>{html.escape(title)}</span><b>{len(names)} contracts</b></summary>"
            f"<ul class='mainnet-contracts'>{items}</ul>"
            "</details>"
        )

    agialpha = by_name["AGIALPHA"]
    agialpha_link = contract_link(agialpha)
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
<meta name='description' content='Public Ethereum Mainnet deployment record for GoalOS AGIALPHA Ascension: 48 GoalOS contracts, Etherscan verification evidence, configuration status, and release links.'>
<meta property='og:title' content='GoalOS AGIALPHA Ascension — Ethereum Mainnet Deployment Record'>
<meta property='og:description' content='48 GoalOS contracts, public Etherscan records, configuration evidence, and strict activation boundaries.'>
<meta name='theme-color' content='#06152a'>
<style id='goalos-v86-critical'>html{{scroll-behavior:smooth}}body{{margin:0;overflow-x:clip}}img,svg,canvas,video,iframe{{max-width:100%;height:auto}}main{{min-height:70vh}}@media(max-width:980px){{.wrap,.container{{width:min(100% - 24px,760px)!important}}}}</style>
<link rel='stylesheet' href='assets/v75-apex.css'>
<link rel='stylesheet' href='assets/goalos-v86-preserve.css'>
<style>
.mainnet-hero{{padding:88px 18px 58px;background:radial-gradient(circle at 15% 10%,rgba(255,220,115,.24),transparent 30rem),radial-gradient(circle at 88% 4%,rgba(88,230,255,.22),transparent 34rem),linear-gradient(135deg,#030712,#071b38 60%,#161036);color:#fff;position:relative;overflow:hidden}}
.mainnet-hero:after{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.08) 1px,transparent 1px);background-size:36px 36px;mask-image:linear-gradient(180deg,#000,transparent 90%);pointer-events:none}}
.mainnet-hero .asi-wrap{{position:relative;z-index:1}}
.mainnet-hero h1{{font-size:clamp(3rem,8vw,7rem);line-height:.9;letter-spacing:-.075em;margin:.7rem 0 1rem}}
.mainnet-hero .lead{{font-size:clamp(1.08rem,2vw,1.48rem);max-width:900px;color:#dce8f7;font-weight:700}}
.mainnet-status-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem;margin-top:1.6rem}}
.mainnet-status{{border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);border-radius:22px;padding:1rem;backdrop-filter:blur(12px)}}
.mainnet-status strong{{display:block;color:#ffe39a;font-size:1.55rem;line-height:1.1}}.mainnet-status span{{font-size:.78rem;color:#dce8f7;font-weight:850}}
.mainnet-panel{{background:rgba(255,255,255,.76);border:1px solid rgba(6,17,31,.13);border-radius:30px;padding:1.3rem;box-shadow:0 30px 90px rgba(6,17,31,.13)}}
.mainnet-boundary{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}}
.mainnet-boundary .ok,.mainnet-boundary .hold{{border-radius:24px;padding:1rem}}
.mainnet-boundary .ok{{border:1px solid rgba(121,240,164,.35);background:rgba(121,240,164,.1)}}
.mainnet-boundary .hold{{border:1px solid rgba(255,143,163,.34);background:rgba(255,143,163,.09)}}
.mainnet-boundary b{{display:block;font-size:1.2rem}}.mainnet-boundary span{{color:#52637e;font-size:.86rem}}
.mainnet-group{{border:1px solid rgba(6,17,31,.13);background:#fff;border-radius:22px;margin:.8rem 0;overflow:hidden}}
.mainnet-group summary{{cursor:pointer;display:flex;justify-content:space-between;gap:1rem;padding:1rem 1.1rem;font-weight:900;color:#102141;list-style:none}}
.mainnet-group summary::-webkit-details-marker{{display:none}}.mainnet-group summary b{{color:#936914;font-size:.82rem}}
.mainnet-contracts{{list-style:none;margin:0;padding:0 1rem 1rem;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.6rem}}
.mainnet-contracts a{{display:block;text-decoration:none;border:1px solid rgba(6,17,31,.1);border-radius:16px;padding:.72rem;background:#fbfdff;overflow:hidden}}
.mainnet-contracts a:hover{{border-color:#7cb7ff;transform:translateY(-1px)}}.mainnet-contracts strong{{display:block;color:#102141}}.mainnet-contracts span{{display:block;color:#596a84;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.73rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.mainnet-meta{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}.mainnet-meta code{{overflow-wrap:anywhere}}
@media(max-width:900px){{.mainnet-status-grid,.mainnet-boundary,.mainnet-meta,.mainnet-contracts{{grid-template-columns:1fr}}.mainnet-hero{{padding-top:62px}}}}
</style>
</head>
<body class='platinum asi-dynamic goalos-v86-preserved'>
<div class='asi-bg'></div>
{header}
<main id='main'>
<section class='mainnet-hero'>
<div class='asi-field'></div>
<div class='asi-wrap'>
<div class='asi-kicker'>Ethereum Mainnet · public deployment record</div>
<h1>Proof moved from rehearsal to <span>chain&nbsp;1.</span></h1>
<p class='lead'>GoalOS AGIALPHA Ascension has a recorded Ethereum Mainnet deployment and completed operator configuration. This page consolidates the canonical contract registry, public Etherscan links, governance status, release evidence, and the boundaries that remain intentionally disabled.</p>
<div class='mainnet-status-grid' aria-label='Ethereum Mainnet deployment summary'>
<div class='mainnet-status'><strong>48</strong><span>GoalOS-created contracts</span></div>
<div class='mainnet-status'><strong>{operator_verified}/48</strong><span>operator Etherscan verification records</span></div>
<div class='mainnet-status'><strong>14/14</strong><span>configuration grants recorded active</span></div>
<div class='mainnet-status'><strong>CONFIGURED</strong><span>deployment status</span></div>
</div>
<div class='asi-actions'>
<a class='asi-btn primary' href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>Open published pre-release</a>
<a class='asi-btn' href='#contracts'>Inspect contract registry</a>
<a class='asi-btn' href='index.html'>Return home</a>
</div>
</div>
</section>
<section class='asi-section white'>
<div class='asi-wrap'>
<div class='asi-kicker'>Current operating boundary</div>
<h2>Deployment is recorded. Production activation remains separate.</h2>
<p class='asi-lead'>The public record supports deployment, configuration, and operator verification evidence. It does not authorize user funds, enable production write flows, claim an external security audit, or convert the pre-release into a production-activation certificate.</p>
<div class='mainnet-boundary'>
<div class='ok' data-status='deployment' data-value='YES'><b>Deployment record: YES</b><span>Ethereum Mainnet, chain ID 1.</span></div>
<div class='ok' data-status='configuration' data-value='YES'><b>Configuration: YES</b><span>Phase-B grants: 14/14; Wallet-A managed roles: 0.</span></div>
<div class='hold' data-status='production-activation' data-value='NO'><b>Production activation: NO</b><span>Live canary, user-fund authorization, and public production reliance remain disabled.</span></div>
</div>
</div>
</section>
<section class='asi-section dark'>
<div class='asi-field'></div>
<div class='asi-wrap'>
<div class='asi-kicker'>Canonical dependency</div>
<h2>One external AGIALPHA. No replacement token.</h2>
<p class='asi-lead'>GoalOS integrates the existing canonical AGIALPHA contract. The GoalOS deployment did not create or mint a substitute token.</p>
<ul class='mainnet-contracts'>{agialpha_link}</ul>
</div>
</section>
<section class='asi-section white'>
<div class='asi-wrap'>
<div class='asi-kicker'>Governance and authority</div>
<h2>Permanent authority is Ledger-controlled.</h2>
<div class='mainnet-meta'>
<div class='mainnet-panel'><h3>Permanent authority</h3><p><a href='{wallet_b_url}' target='_blank' rel='noopener noreferrer'><code>{wallet_b}</code></a></p><p>Wallet B is the recorded permanent authority. The disposable deployment wallet has zero managed roles according to the reconciled release state.</p></div>
<div class='mainnet-panel'><h3>Verification boundary</h3><p>Operator verification evidence records {operator_verified}/48 GoalOS-created contracts. Independent dual-provider release revalidation is <strong>{independent}</strong> unless a later evidence update explicitly changes that status.</p><p>Source identity classification: <code>{source_identity}</code>.</p></div>
</div>
</div>
</section>
<section class='asi-section' id='contracts'>
<div class='asi-wrap'>
<div class='asi-kicker'>Public registry</div>
<h2>Every GoalOS Mainnet contract, one click from source.</h2>
<p class='asi-lead'>The registry below contains 48 GoalOS-created contracts plus the canonical external AGIALPHA dependency. Each entry opens its public Etherscan contract page in a new tab.</p>
{''.join(group_html)}
</div>
</section>
<section class='asi-section white'>
<div class='asi-wrap'>
<div class='asi-kicker'>Evidence and provenance</div>
<h2>Public record, explicit limits.</h2>
<div class='mainnet-meta'>
<div class='mainnet-panel'><h3>Published release</h3><p><a href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>{RELEASE_TAG}</a></p><p>Deployment recorded at <code>{deployed_at}</code>; configuration recorded at <code>{configured_at}</code>.</p></div>
<div class='mainnet-panel'><h3>Tagged source record</h3><p>Release target SHA: <code>{target_sha}</code></p><p>An exact one-to-one tagged-commit-to-deployed-bytecode reproduction remains a separate provenance exercise unless later evidence records completion.</p></div>
</div>
<div class='boundary' style='margin-top:1rem'><strong>Claim boundary.</strong> This page does not claim achieved AGI, achieved ASI, superintelligence achievement, guaranteed ROI, token appreciation, external audit completion, production certification, user-fund authorization, or live production settlement.</div>
</div>
</section>
</main>
<footer class='footer'><div class='wrap'><div><strong>GoalOS AGIALPHA Ascension</strong><div class='small'>Evidence-first Ethereum Mainnet deployment record.</div></div><div class='small'><a href='index.html'>Home</a> · <a href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>GitHub release</a></div></div></footer>
<script defer src='assets/goalos-v86-dynamic-ai.js'></script>
</body>
</html>
"""


def make_home_block(operator_verified: int, independent: str) -> str:
    return f"""{HOME_START}
<section class='asi-section white' id='ethereum-mainnet-record' data-mainnet-home-card='v87'>
<div class='asi-wrap'>
<div class='asi-kicker'>Ethereum Mainnet · deployment record</div>
<h2>48 GoalOS contracts now have a public chain-1 record.</h2>
<p class='asi-lead'>The canonical deployment is recorded as configured, with {operator_verified}/48 operator Etherscan verification records and 14/14 configuration grants. Independent release revalidation is {independent.lower()}. Production activation, user-fund authorization, and public production reliance remain disabled.</p>
<div class='asi-cardgrid'>
<div class='asi-card'><h3>48 contracts</h3><p>GoalOS-created Ethereum Mainnet components, plus one external canonical AGIALPHA dependency.</p></div>
<div class='asi-card'><h3>{operator_verified}/48 verification</h3><p>Public operator verification records with direct Etherscan links on the dedicated page.</p></div>
<div class='asi-card'><h3>14/14 grants</h3><p>Postdeployment configuration recorded active under Ledger-controlled permanent authority.</p></div>
<div class='asi-card'><h3>Activation boundary</h3><p>Production activation and user-fund authorization remain NO.</p></div>
</div>
<div class='asi-actions'><a class='asi-btn primary' href='ethereum-mainnet.html'>Open the Ethereum Mainnet record</a><a class='asi-btn' href='{RELEASE_URL}' target='_blank' rel='noopener noreferrer'>View the published pre-release</a></div>
</div>
</section>
{HOME_END}"""


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
        home = inject_homepage(index_before, make_home_block(operator_verified, independent))

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
