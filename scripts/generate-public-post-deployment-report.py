#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, datetime, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
TX_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")
ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
manifest_path = ROOT / "deployments/ethereum-mainnet.agialpha.latest.json"
verification_path = ROOT / "qa/public-post-deployment-verification.json"
report_path = ROOT / "docs/ETHEREUM_MAINNET_DEPLOYMENT_REPORT.md"

def pending(reason: str) -> None:
    report_path.write_text("# Ethereum Mainnet Deployment Report\n\nMAINNET_DEPLOYED: **NO**.\n\nStatus: not generated because real post-deployment manifest and verification evidence are absent or incomplete.\n\nReason: " + reason + "\n")
    print("POST_DEPLOYMENT_REPORT_PENDING")

if not manifest_path.exists() or not manifest_path.read_text().strip() or not verification_path.exists():
    pending("missing non-empty deployment manifest or public post-deployment verification evidence")
    raise SystemExit(0)
manifest = json.loads(manifest_path.read_text())
verification = json.loads(verification_path.read_text())
errors: list[str] = []
if manifest.get('chain') != 'ethereum' or manifest.get('chainId') != 1:
    errors.append('manifest must be Ethereum Mainnet chainId 1')
if str(manifest.get('agialphaToken','')).lower() != AGIALPHA.lower():
    errors.append('manifest must use canonical AGIALPHA token')
if manifest.get('mockAgialphaUsed') is not False or manifest.get('newAgialphaTokenDeployed') is not False:
    errors.append('manifest must not use MockAGIALPHA or deploy a new AGIALPHA token')
contracts = manifest.get('contracts') or {}
if not contracts:
    errors.append('manifest must contain deployed contract addresses')
for name, meta in contracts.items():
    address = meta.get('address') if isinstance(meta, dict) else meta
    if not isinstance(address, str) or not ADDR_RE.match(address):
        errors.append(f'missing real contract address for {name}')
transactions = manifest.get('transactions') or manifest.get('txHashes') or []
if isinstance(transactions, dict):
    transactions = list(transactions.values())
if not transactions or not all(isinstance(tx, str) and TX_RE.match(tx) for tx in transactions):
    errors.append('real Ethereum Mainnet transaction hashes are required')
if verification.get('postDeploymentVerification') != 'PASSED':
    errors.append('post-deployment verifier has not passed')
if errors:
    pending('; '.join(errors))
    raise SystemExit(0)
lines = ["# Ethereum Mainnet Deployment Report", "", "MAINNET_DEPLOYED: **YES**.", "", f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}", "", "## Boundary", "- This report is generated only after real post-deployment evidence exists.", "- Chain ID is 1, canonical AGIALPHA is used, no MockAGIALPHA is used, and no new AGIALPHA token is deployed.", "", "## Manifest", f"- Chain: {manifest.get('chain')}", f"- Chain ID: {manifest.get('chainId')}", f"- AGIALPHA token: {manifest.get('agialphaToken')}", f"- Mock AGIALPHA used: {manifest.get('mockAgialphaUsed')}", f"- New AGIALPHA token deployed: {manifest.get('newAgialphaTokenDeployed')}", "", "## Verification", f"- Status: {verification.get('postDeploymentVerification')}"]
for name, meta in contracts.items():
    address = meta.get('address') if isinstance(meta, dict) else meta
    lines.append(f"- {name}: {address}")
report_path.write_text("\n".join(lines)+"\n")
print("POST_DEPLOYMENT_REPORT_WRITTEN")
