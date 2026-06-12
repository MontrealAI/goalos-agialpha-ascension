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
    blockers=[]; tech=read(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json")
    gov=read(ROOT/"qa/public-governance-approval-evidence.json"); branch=read(ROOT/"qa/public-branch-protection-evidence.json")
    if tech.get("TECHNICALLY_MAINNET_READY")!="YES": blockers.append("TECHNICALLY_MAINNET_READY is not YES")
    if gov.get("status") not in ["PUBLIC_GOVERNANCE_APPROVED","PUBLIC_RISK_ACCEPTED"]: blockers.append("public governance approval evidence missing")
    if branch.get("branchProtection") not in ["ENABLED","PUBLIC_RISK_ACCEPTED"]: blockers.append("branch protection or public risk acceptance missing")
    for f in ["docs/FINAL_LOCAL_MAINNET_DEPLOYMENT_RUNBOOK.md","docs/PUBLIC_MAINNET_AUTHORIZATION_RUNBOOK.md","docs/FINAL_PUBLIC_CLAIMS_BOUNDARY.md","scripts/deploy-ethereum-mainnet-gated.ts"]:
        if not (ROOT/f).exists(): blockers.append(f"missing {f}")
    text="\n".join(p.read_text(errors="ignore") for p in (ROOT/".github/workflows").glob("*.yml")) if (ROOT/".github/workflows").exists() else ""
    if "deploy:ethereum-mainnet:gated" in text: blockers.append("GitHub Actions references final mainnet deployment command")
    status="NO" if blockers else "YES"; return status, blockers, {"technical":sha(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"),"governance":sha(ROOT/"qa/public-governance-approval-evidence.json"),"branchProtection":sha(ROOT/"qa/public-branch-protection-evidence.json")}
def write(status,blockers,evidence):
    out={"status":status,"MAINNET_DEPLOYMENT_AUTHORIZED":status,"mainnetDeploymentAuthorized":status,"commit":git(),"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"mainnetDeployed":"NO","runtimeSecretsRequiredForBroadcast":True,"runtimeSecretsStoredInGitHub":False,"authorizationScope":"manual-deployment-package-authorization","evidence":evidence,"blockers":blockers,"generatedAt":now(),"generatedBy":"scripts/mainnet-deployment-authorization-check.py"}
    for path in [ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json",ROOT/"docs/MAINNET_AUTHORIZATION_DECISION.json"]: path.write_text(json.dumps(out,indent=2)+"\n")
    md=f"# Mainnet Deployment Authorization Decision\n\nMAINNET_DEPLOYMENT_AUTHORIZED: **{status}**\n\nMAINNET_DEPLOYED: **NO**\n\n## Blockers\n" + ("\n".join(f"- {b}" for b in blockers) if blockers else "- None.") + "\n\nPublic repository governance authorizes only manual, local, typed-confirmation gated deployment. Runtime RPC/key are not stored in GitHub.\n"
    for path in [ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md",ROOT/"docs/MAINNET_AUTHORIZATION_DECISION.md"]: path.write_text(md)
    (ROOT/"qa/public-mainnet-deployment-authorization-evidence.json").write_text(json.dumps({"redacted":True,"containsSecrets":False,"containsPrivateAddresses":False,"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"commit":out["commit"],"deploymentAuthorization":status,"mainnetDeployed":"NO","blockers":blockers,"generatedAt":out["generatedAt"],"technicalReadinessHash":evidence["technical"],"governanceApprovalHash":evidence["governance"],"branchProtectionEvidenceHash":evidence["branchProtection"]},indent=2)+"\n")
    return out
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--public-only-final", action="store_true"); parser.parse_args(); print(json.dumps(write(*compute()),indent=2))
if __name__=="__main__": main()
