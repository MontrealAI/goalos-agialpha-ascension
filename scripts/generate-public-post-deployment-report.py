#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
manifest_path = ROOT / "deployments/ethereum-mainnet.agialpha.latest.json"
verification_path = ROOT / "qa/public-post-deployment-verification.json"
report_path = ROOT / "docs/ETHEREUM_MAINNET_DEPLOYMENT_REPORT.md"
if not manifest_path.exists() or not verification_path.exists():
    report_path.write_text("# Ethereum Mainnet Deployment Report\n\nStatus: not generated because real post-deployment manifest and verification evidence are absent.\n")
    print("POST_DEPLOYMENT_REPORT_PENDING")
    raise SystemExit(0)
manifest = json.loads(manifest_path.read_text())
verification = json.loads(verification_path.read_text())
lines = ["# Ethereum Mainnet Deployment Report", "", f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}", "", "## Boundary", "- This report may be published only after real post-deployment evidence exists.", "- Do not claim Ethereum Mainnet deployment from templates or simulations.", "", "## Manifest", f"- Chain: {manifest.get('chain')}", f"- Chain ID: {manifest.get('chainId')}", f"- AGIALPHA token: {manifest.get('agialphaToken')}", f"- Mock AGIALPHA used: {manifest.get('mockAgialphaUsed')}", f"- New AGIALPHA token deployed: {manifest.get('newAgialphaTokenDeployed')}", "", "## Verification", f"- Status: {verification.get('postDeploymentVerification')}"]
for name, meta in (manifest.get('contracts') or {}).items():
    address = meta.get('address') if isinstance(meta, dict) else meta
    lines.append(f"- {name}: {address}")
report_path.write_text("\n".join(lines)+"\n")
print("POST_DEPLOYMENT_REPORT_WRITTEN")
