#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
BLOCKED = [
    "production ready", "externally audited", "guaranteed secure", "guaranteed ROI",
    "achieved AGI", "achieved ASI", "superintelligence achieved", "Kardashev achieved",
    "legal approval complete", "tax approval complete"
]
MAINNET_YES = re.compile(r"Mainnet deployed:\s*YES|MAINNET_DEPLOYED\W+YES|mainnetDeployed\W+YES", re.I)
candidate_names = {"DEPLOYMENT_START_HERE.md", "SEPOLIA_DEPLOYMENT_GUIDE.md", "MAINNET_OPERATOR_RUNBOOK.md", "DEPLOYMENT_TROUBLESHOOTING.md", "DEPLOYMENT_FAQ.md", "DEPLOYMENT_CLAIM_BOUNDARY.md", "SEPOLIA_DEPLOYMENT_REPORT.md", "ETHEREUM_MAINNET_DEPLOYMENT_REPORT.md", "sepolia-deployment-evidence.json", "mainnet-deployment-evidence.json", "ethereum-mainnet.agialpha.latest.json", "ethereum-sepolia.agialpha.latest.json"}
paths = [p for base in ["docs", "qa", "deployments"] for p in (ROOT/base).rglob("*") if p.is_file() and p.name in candidate_names]
errors=[]
manifest_path = ROOT / "deployments/ethereum-mainnet.agialpha.latest.json"
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
real_mainnet = manifest.get("chainId") == 1 and manifest.get("status") != "TEMPLATE_NO_DEPLOYMENT" and manifest.get("contracts") and manifest.get("transactions")
CLAIM_BOUNDARY = "This evidence reports deployment mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment."
for path in paths:
    text = path.read_text(encoding="utf-8", errors="ignore").replace(CLAIM_BOUNDARY, "")
    rel = path.relative_to(ROOT).as_posix()
    for phrase in BLOCKED:
        for line in text.splitlines():
            lower = line.lower()
            if "does not claim" in lower or "not claim" in lower:
                continue
            if phrase.lower() in lower:
                errors.append(f"Unsafe deployment claim '{phrase}' in {rel}")
                break
    if MAINNET_YES.search(text) and not real_mainnet:
        errors.append(f"Unsupported Mainnet deployed YES claim in {rel}")
if errors:
    print("Deployment claim-boundary check failed:")
    for e in sorted(set(errors)): print(f"- {e}")
    sys.exit(1)
print("Deployment claim-boundary check passed.")
