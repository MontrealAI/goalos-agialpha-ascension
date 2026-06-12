#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
AGIALPHA="0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return "0x"+hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
def read(p):
    try: return json.loads(p.read_text())
    except Exception: return {}
def git():
    try: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    except Exception: return "UNKNOWN"
def compute():
    blockers=[]; tech=read(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"); dep=read(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json")
    if tech.get("TECHNICALLY_MAINNET_READY")!="YES": blockers.append("TECHNICALLY_MAINNET_READY is not YES")
    if dep.get("MAINNET_DEPLOYMENT_AUTHORIZED")!="YES": blockers.append("MAINNET_DEPLOYMENT_AUTHORIZED is not YES")
    if tech.get("chain")!="ethereum" or tech.get("chainId")!=1 or str(tech.get("agialphaToken","")).lower()!=AGIALPHA.lower(): blockers.append("technical decision target mismatch")
    if dep.get("chain")!="ethereum" or dep.get("chainId")!=1 or str(dep.get("agialphaToken","")).lower()!=AGIALPHA.lower(): blockers.append("deployment decision target mismatch")
    workflow_text="\n".join(p.read_text(errors="ignore") for p in (ROOT/".github/workflows").glob("*.yml")) if (ROOT/".github/workflows").exists() else ""
    if "deploy:ethereum-mainnet:gated" in workflow_text: blockers.append("CI can invoke mainnet deployment command")
    status="NO" if blockers else "YES"; return status, blockers, {"technicalReadinessSha256":sha(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"),"deploymentAuthorizationSha256":sha(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json"),"agialphaVerificationSha256":sha(ROOT/"qa/public-agialpha-token-verification.json")}
def write(status,blockers,evidence):
    out={"status":status,"ETHEREUM_MAINNET_AUTHORIZED":status,"ethereumMainnetAuthorized":status,"commit":git(),"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"mainnetDeployed":"NO","externalAuditPlanned":False,"externalAuditRequired":False,"authorizationScope":"manual-deployment-package-authorization","runtimeSecretsRequiredForBroadcast":True,"runtimeSecretsStoredInGitHub":False,"finalManualDeploymentCommand":"npm run deploy:ethereum-mainnet:gated" if status=="YES" else None,"evidence":evidence,"blockers":blockers,"generatedAt":now(),"generatedBy":"scripts/ethereum-mainnet-authorization-check.py"}
    (ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json").write_text(json.dumps(out,indent=2)+"\n")
    (ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md").write_text(f"# Ethereum Mainnet Authorization Decision\n\nETHEREUM_MAINNET_AUTHORIZED: **{status}**\n\nMAINNET_DEPLOYED: **NO**\n\n## Blockers\n" + ("\n".join(f"- {b}" for b in blockers) if blockers else "- None.") + "\n\nNo Ethereum Mainnet deployment occurred. This decision authorizes only manual local deployment with runtime RPC/key and typed confirmation.\n")
    (ROOT/"qa/public-ethereum-mainnet-authorization-evidence.json").write_text(json.dumps({"redacted":True,"containsSecrets":False,"containsPrivateAddresses":False,"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"commit":out["commit"],"ethereumMainnetAuthorization":status,"technicalReadiness":read(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json").get("TECHNICALLY_MAINNET_READY"),"deploymentAuthorization":read(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json").get("MAINNET_DEPLOYMENT_AUTHORIZED"),"mainnetDeployed":"NO","blockers":blockers,"generatedAt":out["generatedAt"],**evidence},indent=2)+"\n")
    return out
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--public-only-final", action="store_true"); parser.parse_args(); print(json.dumps(write(*compute()),indent=2))
if __name__=="__main__": main()
