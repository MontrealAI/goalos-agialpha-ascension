#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
FILES={
 "technical":"docs/MAINNET_TECHNICAL_READINESS_DECISION.json",
 "deployment":"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json",
 "ethereum":"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json",
 "local_rehearsal":"qa/local-rehearsal-report.json",
 "toolchain":"audit/TOOLCHAIN_CLEARANCE_REPORT.md",
 "agialpha_verification":"qa/public-agialpha-token-verification.json",
 "mainnet_simulation":"qa/ETHEREUM_MAINNET_FORK_SIMULATION.json"}
def load(p):
    q=ROOT/p
    if not q.exists(): return {"present":False,"status":"MISSING"}
    if q.suffix==".json":
        try:
            d=json.loads(q.read_text())
            return {"present":True,"status":d.get("status") or d.get("technicalReadiness") or d.get("deploymentAuthorization") or d.get("ethereumMainnetAuthorization") or "PRESENT"}
        except Exception: pass
    return {"present":True,"status":"PRESENT"}
print("GoalOS AGIALPHA Ethereum Mainnet Command Status")
for name,path in FILES.items():
    info=load(path); print(f"- {name}: {info['status']} ({path if info['present'] else 'missing '+path})")
print("Public authorization uses public evidence only. Runtime RPC/key are required only for actual manual broadcast.")
