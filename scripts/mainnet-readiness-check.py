#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path: pathlib.Path): return "0x" + hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def read(path: pathlib.Path):
    try: return json.loads(path.read_text())
    except Exception: return {}
def git(args):
    try: return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def ok_file(path, pred=lambda d: True):
    p=ROOT/path; d=read(p); return p.exists() and pred(d), d

def public_safe(d):
    text=json.dumps(d,sort_keys=True).upper()
    return d.get("containsSecrets") is False and d.get("containsPrivateAddresses") is False and "PRIVATE_KEY" not in text and "RPC_URL" not in text

def compute():
    blockers=[]; ev={}
    checks={
      "toolchain": ("qa/public-toolchain-clearance-evidence.json", lambda d: d.get("automatedSecurityToolchain")=="PASSED" or d.get("status")=="PASSED"),
      "localRehearsal": ("qa/local-rehearsal-report.json", lambda d: d.get("status")=="PASSED"),
      "localDocket": ("evidence/local/EVIDENCE_DOCKET.json", lambda d: d.get("status")=="LOCAL_SIMULATION_ONLY" and d.get("manifestHash")),
      "agialphaVerification": ("qa/public-agialpha-token-verification.json", lambda d: d.get("status") == "PASSED" and d.get("addressHasCode") is True and str(d.get("agialphaToken","")).lower()==AGIALPHA.lower()),
      "mainnetSimulation": ("qa/ETHEREUM_MAINNET_FORK_SIMULATION.json", lambda d: d.get("status") == "PASSED" and d.get("checks",{}).get("deploysNewAGIALPHAOnMainnet") is False),
      "governance": ("qa/public-governance-approval-evidence.json", lambda d: d.get("status") in ["PUBLIC_GOVERNANCE_APPROVED","PUBLIC_RISK_ACCEPTED"]),
      "branchProtection": ("qa/public-branch-protection-evidence.json", lambda d: d.get("branchProtection") in ["ENABLED","PUBLIC_RISK_ACCEPTED"]),
    }
    for name,(path,pred) in checks.items():
        passed,d=ok_file(path,pred); ev[name]={"path":path,"sha256":sha(ROOT/path),"status":d.get("status") or d.get("branchProtection"),"present":(ROOT/path).exists()}
        if not passed: blockers.append(f"{name} evidence missing or not passed: {path}")
        if d and not public_safe(d): blockers.append(f"{name} evidence is not public-safe: {path}")
    pkg=read(ROOT/"package.json")
    for script in ["repo:all","assert:public-status","compile","test","test:all","static-check","audit:slither","audit:all","rehearse:local","evidence:local"]:
        if script not in pkg.get("scripts",{}): blockers.append(f"missing package script {script}")
    required_files=["scripts/deploy-ethereum-mainnet-gated.ts","scripts/preflight-ethereum-mainnet.ts","scripts/config/networkConfig.ts","docs/BRANCH_PROTECTION_PUBLIC_RISK_ACCEPTANCE.md","docs/PUBLIC_MAINNET_AUTHORIZATION_MODEL.md","docs/WHAT_YES_MEANS_AND_DOES_NOT_MEAN.md"]
    for f in required_files:
        if not (ROOT/f).exists(): blockers.append(f"missing required artifact {f}")
    status="NO" if blockers else "YES"
    return status, blockers, ev

def write(status, blockers, evidence):
    out={"status":status,"TECHNICALLY_MAINNET_READY":status,"technicallyMainnetReady":status,"commit":git(["rev-parse","HEAD"]),"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"mainnetDeployed":"NO","externalAuditPlanned":False,"externalAuditRequired":False,"authorizationScope":"manual-deployment-package-authorization","runtimeSecretsRequiredForBroadcast":True,"runtimeSecretsStoredInGitHub":False,"evidence":evidence,"blockers":blockers,"generatedAt":now(),"generatedBy":"scripts/mainnet-readiness-check.py"}
    (ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json").write_text(json.dumps(out,indent=2)+"\n")
    (ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.md").write_text(f"# Mainnet Technical Readiness Decision\n\nTECHNICALLY_MAINNET_READY: **{status}**\n\nMAINNET_DEPLOYED: **NO**\n\n## Blockers\n" + ("\n".join(f"- {b}" for b in blockers) if blockers else "- None.") + "\n\nThis is public evidence-computed package readiness for manual gated Ethereum Mainnet deployment. It is not an external audit and no deployment occurred.\n")
    (ROOT/"qa/public-mainnet-technical-readiness-evidence.json").write_text(json.dumps({"redacted":True,"containsSecrets":False,"containsPrivateAddresses":False,"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"commit":out["commit"],"technicalReadiness":status,"mainnetDeployed":"NO","blockers":blockers,"generatedAt":out["generatedAt"],"toolchainClearanceHash":evidence.get("toolchain",{}).get("sha256"),"localRehearsalEvidenceHash":evidence.get("localRehearsal",{}).get("sha256"),"agialphaTokenVerificationHash":evidence.get("agialphaVerification",{}).get("sha256"),"mainnetPreflightPolicyHash":sha(ROOT/"docs/ETHEREUM_MAINNET_PREFLIGHT_REPORT.md"),"governanceApprovalHash":evidence.get("governance",{}).get("sha256"),"branchProtectionEvidenceHash":evidence.get("branchProtection",{}).get("sha256")},indent=2)+"\n")
    return out

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--public-only-final", action="store_true"); parser.parse_args()
    print(json.dumps(write(*compute()),indent=2))
if __name__ == "__main__": main()
