#!/usr/bin/env python3
from __future__ import annotations
import datetime,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
def git(args):
    try: return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    except Exception: return "UNKNOWN"
required=["docs/PUBLIC_GOVERNANCE_DEPLOYMENT_APPROVAL.md","docs/FOUNDER_APPROVAL_PUBLIC_REPO_POLICY.md","docs/BRANCH_PROTECTION_PUBLIC_RISK_ACCEPTANCE.md","CODEOWNERS"]
missing=[f for f in required if not (ROOT/f).exists()]
status="PUBLIC_GOVERNANCE_APPROVED" if not missing else "PUBLIC_GOVERNANCE_INCOMPLETE"
report={"redacted":True,"containsSecrets":False,"containsPrivateAddresses":False,"status":status,"commit":git(["rev-parse","HEAD"]),"branch":git(["branch","--show-current"]),"checksPassed":"evaluated-by-public-ci","branchProtectionOrRiskAcceptance":(ROOT/"docs/BRANCH_PROTECTION_PUBLIC_RISK_ACCEPTANCE.md").exists(),"codeownersOrSensitivePathPolicy":(ROOT/"CODEOWNERS").exists(),"releaseTagInstruction":"mainnet-authorization-vX.Y.Z","missing":missing,"generatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}
(ROOT/"qa/public-governance-approval-evidence.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
raise SystemExit(0 if status=="PUBLIC_GOVERNANCE_APPROVED" else 1)
