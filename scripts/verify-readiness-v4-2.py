from __future__ import annotations
import json, hashlib, re, datetime, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "START_HERE.html",
    ".env.example",
    "package.json",
    "contracts/registry/JobRegistry.sol",
    "contracts/registry/JobClaimBondManager.sol",
    "contracts/registry/ProofSubmissionRegistry.sol",
    "contracts/registry/ReviewerBondRegistry.sol",
    "contracts/registry/ProofCardRegistry.sol",
    "contracts/registry/ProofCredentialRegistry.sol",
    "contracts/registry/ReputationRegistry.sol",
    "contracts/registry/LegacyAGIJobManagerRegistry.sol",
    "contracts/aep/AEPGoalOSCommitRegistry.sol",
    "contracts/aep/AEPSelectionGate.sol",
    "contracts/aep/AEPConformanceRegistry.sol",
    "contracts/aep/AEPClaimBoundaryRegistry.sol",
    "contracts/aep/AEPReplayRegistry.sol",
    "contracts/aep/AEPCommitRevealValidationRegistry.sol",
    "contracts/aep/AEPEvaluatorStakingRegistry.sol",
    "contracts/aep/AEPSlashingCourt.sol",
    "contracts/aep/AEPRewardVault.sol",
    "contracts/aep/AEPFalsificationRegistry.sol",
    "scripts/deploy-core.ts",
    "scripts/deploy-ethereum-mainnet-gated.ts",
    "scripts/preflight-ethereum-mainnet-gates.ts",
    "scripts/mainnet-authorization-check.py",
    "scripts/generate-evidence-docket-template.py",
    "docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_2.md",
    "docs/SEPOLIA_REHEARSAL_EVIDENCE_DOCKET_v4_2.md",
    "docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md",
    "docs/GOVERNANCE_ROLE_CEREMONY_v4_2.md",
    "docs/PUBLIC_CLAIMS_REVIEW_v4_2.md",
    "schemas/evidence-docket-v4.2.schema.json",
    "audit/FINDINGS_CLOSURE_MATRIX_v4_2.csv",
    "audit/MAINNET_GATE_REGISTER_v4_2.csv",
]
PROHIBITED_PHRASES = [
    "guaranteed " + "profit",
    "guaranteed yield",
    "guaranteed return",
    "mainnet ready now",
    "audited and approved",
    "guaranteed non-security",
]
ALLOW_CONTEXT = ["not ", "no ", "do not ", "without "]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="ignore")

def main():
    errors=[]
    warnings=[]
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")
    pkg = json.loads(read("package.json")) if (ROOT/"package.json").exists() else {}
    if pkg.get("version") != "4.2.0":
        errors.append("package.json version must equal 4.2.0")
    scripts = pkg.get("scripts", {})
    for s in ["readiness:v4.2", "evidence:docket:template", "mainnet:authorization-check", "compile", "test", "test:all", "static-check", "deploy:ethereum-sepolia", "deploy:ethereum-mainnet:gated"]:
        if s not in scripts:
            errors.append(f"package.json missing script: {s}")
    env = read(".env.example") if (ROOT/".env.example").exists() else ""
    if "AGIALPHA_TOKEN_ADDRESS=" not in env:
        errors.append(".env.example missing AGIALPHA_TOKEN_ADDRESS")
    # v4.2 should keep Sepolia blank-safe semantics
    for key in ["LEGAL_SIGNOFF_HASH", "TAX_SIGNOFF_HASH", "SECURITY_REVIEW_HASH", "PUBLIC_CLAIMS_REVIEW_HASH", "SEPOLIA_REHEARSAL_EVIDENCE_HASH", "EXTERNAL_AUDIT_CLOSURE_HASH", "FOUNDER_APPROVAL_HASH"]:
        if key not in env:
            errors.append(f".env.example missing {key}")
    deploy = read("scripts/deploy-core.ts") if (ROOT/"scripts/deploy-core.ts").exists() else ""
    for needle in ["AGIALPHA_MAINNET", "enforceEthereumMainnetGates", "MockAGIALPHA", "AEPConformanceRegistry", "AEPCommitRevealValidationRegistry", "AEPFalsificationRegistry"]:
        if needle not in deploy:
            errors.append(f"deploy-core.ts missing {needle}")
    if "|| deployer.address" in deploy:
        errors.append("deploy-core.ts must not default critical addresses to deployer")
    # check no obvious private key or mnemonic values
    secret_patterns=[r"PRIVATE_KEY=0x[0-9a-fA-F]{64}", r"MNEMONIC=.+", r"ALCHEMY.*KEY=.*[A-Za-z0-9]{16,}", r"INFURA.*KEY=.*[A-Za-z0-9]{16,}"]
    for p in ROOT.rglob("*"):
        if not p.is_file() or "node_modules" in p.parts or ".git" in p.parts or "qa" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        # Avoid self-matching this checker's own regex strings.
        if p.name != "verify-readiness-v4-2.py":
            for pat in secret_patterns:
                if re.search(pat, text):
                    errors.append(f"possible secret in {p.relative_to(ROOT)} matching {pat}")
        low=text.lower()
        for phrase in PROHIBITED_PHRASES:
            start=0
            while True:
                idx=low.find(phrase, start)
                if idx == -1:
                    break
                ctx=low[max(0, idx-24):idx]
                safe_context = any(x in ctx for x in ["not ", "no ", "do not ", "without ", "prohibited", "avoid", "never ", "do **not**", "do **not** call", "do not call"])
                if not safe_context and p.name != "verify-readiness-v4-2.py":
                    warnings.append(f"review public claims phrase in {p.relative_to(ROOT)}: {phrase}")
                start=idx+len(phrase)
    # Solidity basic checks
    for sol in (ROOT/"contracts").rglob("*.sol"):
        txt=sol.read_text(encoding="utf-8", errors="ignore")
        if "pragma solidity ^0.8.24;" not in txt:
            errors.append(f"missing pragma: {sol.relative_to(ROOT)}")
        if txt.count("{") != txt.count("}"):
            errors.append(f"brace mismatch: {sol.relative_to(ROOT)}")
    manifest=[]
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and "node_modules" not in p.parts and ".git" not in p.parts:
            data=p.read_bytes()
            manifest.append({"path":p.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    (ROOT/"qa").mkdir(exist_ok=True)
    (ROOT/"qa"/"MANIFEST_v4_2.json").write_text(json.dumps({"generated_at":datetime.datetime.now(datetime.UTC).isoformat(),"files":manifest},indent=2),encoding="utf-8")
    report={
        "package":"GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_2_EVIDENCE_READY_AUDIT_CANDIDATE",
        "generated_at":datetime.datetime.now(datetime.UTC).isoformat(),
        "static_readiness":"passed" if not errors else "failed",
        "files_checked":len(manifest),
        "errors":errors,
        "warnings":warnings,
        "status":"evidence-ready audit candidate; mainnet not authorized",
        "next_gate":"real Ethereum Sepolia rehearsal and Evidence Docket",
    }
    (ROOT/"qa"/"READINESS_REPORT_v4_2.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
