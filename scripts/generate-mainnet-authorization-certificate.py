#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(args):
    try: return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def read_json(rel):
    p=ROOT/rel
    try: return json.loads(p.read_text())
    except Exception: return {}
def sha(rel):
    p=ROOT/rel
    if not p.exists(): return None
    h=hashlib.sha256()
    if p.is_dir():
        for child in sorted(x for x in p.rglob("*") if x.is_file()):
            h.update(child.relative_to(ROOT).as_posix().encode()); h.update(b"\0"); h.update(child.read_bytes())
    else:
        h.update(p.read_bytes())
    return "0x"+h.hexdigest()

def public_safe(rel):
    d=read_json(rel)
    txt=json.dumps(d, sort_keys=True).upper()
    return bool(d) and d.get("containsSecrets") is not True and d.get("containsPrivateAddresses") is not True and "PRIVATE_KEY" not in txt and "FOUNDER_APPROVAL_SIGNATURE" not in txt

def main():
    evidence_paths = {
        "repoDoctor":"qa/REPO_DOCTOR_REPORT.json",
        "dependencyBaseline":"docs/DEPENDENCY_BASELINE_FOR_MAINNET.md",
        "compile":"artifacts/build-info",
        "tests":"test",
        "testAll":"test/invariants/mainnetBoundary.invariant.test.ts",
        "staticCheck":"scripts/static_check.py",
        "publicStatus":"scripts/assert_public_status.py",
        "noPrivateOperatorData":"scripts/no_private_operator_data_check.py",
        "noPaidProducts":"scripts/no_paid_products_check.py",
        "slither":"docs/SLITHER_SECURITY_REPORT.md",
        "toolchainClearance":"qa/public-toolchain-clearance-evidence.json",
        "unresolvedFindings":"audit/AUDIT_FINDINGS_REGISTER.csv",
        "invariants":"security/INVARIANTS.md",
        "localRehearsal":"qa/local-rehearsal-report.json",
        "localEvidenceDocket":"evidence/local/EVIDENCE_DOCKET.json",
        "agialphaTokenVerification":"qa/public-agialpha-token-verification.json",
        "mainnetGuardrails":"scripts/deploy-ethereum-mainnet-gated.ts",
        "branchProtectionOrRiskAcceptance":"qa/public-branch-protection-evidence.json",
        "publicGovernanceApproval":"qa/public-governance-approval-evidence.json",
        "releaseGate":"docs/PUBLIC_MAINNET_AUTHORIZATION_RUNBOOK.md",
        "mainnetSimulation":"qa/ETHEREUM_MAINNET_FORK_SIMULATION.json",
    }
    evidence={k:{"path":v,"sha256":sha(v)} for k,v in evidence_paths.items()}
    blockers=[]; warnings=[]
    tool=read_json("qa/public-toolchain-clearance-evidence.json")
    rehearsal=read_json("qa/local-rehearsal-report.json")
    docket=read_json("evidence/local/EVIDENCE_DOCKET.json")
    token=read_json("qa/public-agialpha-token-verification.json")
    sim=read_json("qa/ETHEREUM_MAINNET_FORK_SIMULATION.json")
    gov=read_json("qa/public-governance-approval-evidence.json")
    branch=read_json("qa/public-branch-protection-evidence.json")
    if not (tool.get("status")=="PASSED" and int(tool.get("unresolvedCriticalHighFindings",0) or 0)==0): blockers.append("Tier 1 automated/internal security toolchain is not clear.")
    if rehearsal.get("status")!="PASSED": blockers.append("Local deterministic rehearsal has not passed.")
    if not ((docket.get("status")=="LOCAL_SIMULATION_ONLY" or docket.get("docketType")=="LOCAL_SIMULATION_ONLY") and (docket.get("manifestHash") or docket.get("deploymentManifestHash"))): blockers.append("Local Evidence Docket is missing or incomplete.")
    token_ok = token.get("status") in {"PASSED","ACCEPTED_BY_PUBLIC_GOVERNANCE","GOVERNANCE_ACCEPTED"} and str(token.get("agialphaToken", token.get("address", ""))).lower()==AGIALPHA.lower()
    if not token_ok: blockers.append("Public AGIALPHA token verification is missing or not governance-accepted.")
    sim_ok = sim.get("status")=="PASSED" and sim.get("checks",{}).get("deploysNewAGIALPHAOnMainnet") is False
    if not sim_ok: blockers.append("Mainnet-shaped simulation evidence is missing or failed.")
    if gov.get("status") not in {"PUBLIC_GOVERNANCE_APPROVED","PUBLIC_RISK_ACCEPTED"}: blockers.append("Public governance approval evidence is missing.")
    if branch.get("branchProtection") not in {"ENABLED","PUBLIC_RISK_ACCEPTED"}: blockers.append("Branch protection/risk acceptance evidence is missing.")
    for rel in ["qa/public-toolchain-clearance-evidence.json","qa/local-rehearsal-report.json","qa/public-agialpha-token-verification.json","qa/public-governance-approval-evidence.json","qa/public-branch-protection-evidence.json"]:
        if not public_safe(rel): blockers.append(f"Public-safety flags are missing or unsafe in {rel}.")
    required = ["scripts/deploy-ethereum-mainnet-gated.ts","scripts/preflight-ethereum-mainnet.ts","scripts/config/networkConfig.ts","docs/FINAL_LOCAL_MAINNET_DEPLOYMENT_RUNBOOK.md","docs/FINAL_ROLLBACK_AND_INCIDENT_PLAN.md"]
    for rel in required:
        if not (ROOT/rel).exists(): blockers.append(f"Missing required artifact {rel}.")
    ready="NO" if blockers else "YES"
    deploy_auth=ready if not blockers else "NO"
    eth_auth="YES" if ready=="YES" and deploy_auth=="YES" else "NO"
    cert={
      "schemaVersion":"1.0","generatedAt":now(),"generatedBy":"scripts/generate-mainnet-authorization-certificate.py",
      "repository":"MontrealAI/goalos-agialpha-ascension","commit":git(["rev-parse","HEAD"]),"branch":git(["branch","--show-current"]),
      "chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"scope":"public-repository-package-authorization-for-manual-gated-mainnet-deployment",
      "notExternallyAudited":True,"externalAuditPlanned":False,"externalAuditRequired":False,"legalTaxReviewClaimed":False,
      "mainnetDeployed":"NO","runtimeSecretsRequiredForBroadcast":True,"runtimeSecretsStoredInGitHub":False,"ciCanDeployMainnet":False,
      "technicallyMainnetReady":ready,"TECHNICALLY_MAINNET_READY":ready,
      "mainnetDeploymentAuthorized":deploy_auth,"MAINNET_DEPLOYMENT_AUTHORIZED":deploy_auth,
      "ethereumMainnetAuthorized":eth_auth,"ETHEREUM_MAINNET_AUTHORIZED":eth_auth,
      "evidence":evidence,"blockers":blockers,"warnings":warnings,
      "nextAction":"A. Public repo authorized. Founder/deployer may run the final manual gated deployment command with local runtime RPC/key." if eth_auth=="YES" else "B. Blocked, with exact blockers."
    }
    (ROOT/"qa").mkdir(exist_ok=True)
    (ROOT/"qa/mainnet-authorization-certificate.json").write_text(json.dumps(cert, indent=2)+"\n")
    (ROOT/"docs/MAINNET_AUTHORIZATION_CERTIFICATE.md").write_text(f"# Mainnet Authorization Certificate\n\nGenerated from `qa/mainnet-authorization-certificate.json`.\n\n- TECHNICALLY_MAINNET_READY: **{ready}**\n- MAINNET_DEPLOYMENT_AUTHORIZED: **{deploy_auth}**\n- ETHEREUM_MAINNET_AUTHORIZED: **{eth_auth}**\n- MAINNET_DEPLOYED: **NO**\n\nThis certificate authorizes only manual, local, gated Ethereum Mainnet deployment. It is not an external audit, legal approval, tax review, or proof that deployment occurred.\n")
    print(json.dumps(cert, indent=2))
if __name__ == "__main__": main()
