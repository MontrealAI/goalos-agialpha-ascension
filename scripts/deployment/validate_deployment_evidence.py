#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
REQUIRED = ["networkName","chainId","timestamp","gitCommit","packageVersion","hardhatVersion","solidityCompilerVersion","agialphaTokenAddress","mockTokenUsed","newAgialphaTokenDeployed","deployedContractAddresses","transactionHashes","verificationStatus","manifestHash","claimBoundary","nextRecommendedAction"]
CLAIM = "This evidence reports Ethereum Mainnet deployment, verification, and configuration mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, user-fund authorization, or production activation."
paths = [ROOT / "qa/sepolia-deployment-evidence.json", ROOT / "qa/mainnet-deployment-evidence.json"]
errors=[]
for path in paths:
    if not path.exists():
        continue
    try:
        data=json.loads(path.read_text())
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)} invalid JSON: {exc}"); continue
    missing=[k for k in REQUIRED if k not in data]
    if missing: errors.append(f"{path.relative_to(ROOT)} missing {missing}")
    if data.get("claimBoundary") != CLAIM: errors.append(f"{path.relative_to(ROOT)} claimBoundary mismatch")
if errors:
    print(json.dumps({"status":"FAILED","errors":errors}, indent=2)); sys.exit(1)
print(json.dumps({"status":"PASSED","checked":[str(p.relative_to(ROOT)) for p in paths if p.exists()]}, indent=2))
