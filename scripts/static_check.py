from pathlib import Path
import json, hashlib, datetime, sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    "contracts/registry/ProofSeedRegistry.sol",
    "contracts/registry/LegacyAGIJobManagerRegistry.sol",
    "contracts/registry/JobRegistry.sol",
    "contracts/registry/ProofSubmissionRegistry.sol",
    "contracts/registry/ReviewerBondRegistry.sol",
    "contracts/token/MockAGIALPHA.sol",
    "contracts/aep/AEPAgentRegistry.sol",
    "contracts/aep/AEPArtifactRegistry.sol",
    "contracts/aep/AEPGoalOSCommitRegistry.sol",
    "contracts/aep/AEPRunCommitmentRegistry.sol",
    "contracts/aep/AEPProofLedger.sol",
    "contracts/aep/AEPEvalRegistry.sol",
    "contracts/aep/AEPAttestationRegistry.sol",
    "contracts/aep/AEPSelectionGate.sol",
    "contracts/aep/AEPRolloutRouter.sol",
    "contracts/aep/AEPRollbackRegistry.sol",
    "contracts/aep/AEPEvidenceDocketRegistry.sol",
    "contracts/aep/AEPProofBundleRegistry.sol",
    "contracts/aep/AlphaWorkUnitLedger.sol",
    "contracts/aep/MandateEpochRegistry.sol",
    "contracts/aep/AGIEthNamespaceRegistry.sol",
    "scripts/deploy-core.ts",
    "scripts/deploy-ethereum-mainnet-gated.ts",
    "scripts/preflight-ethereum-mainnet-gates.ts",
    "scripts/verify-agialpha-token.ts",
    "scripts/verify-deployment.ts",
    "docs/START_HERE_v3_0.md",
    "docs/REFERENCE_GROUNDED_ARCHITECTURE_v3_0.md",
    "docs/CONTRACT_SUITE_INDEX_v3_0.md",
    "docs/ETHEREUM_MAINNET_DEPLOYMENT_RUNBOOK_v3_0.md",
    "docs/SEASON_001_MANDATE_EPOCH_PLAYBOOK_v3_0.md",
    "docs/AUDITOR_HANDOFF_v3_0.md",
    "docs/SAFE_CLAIMS_AND_TOKEN_BOUNDARY_v3_0.md",
    "docs/START_HERE_v4_2.md",
    "docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_2.md",
    "docs/SEPOLIA_REHEARSAL_EVIDENCE_DOCKET_v4_2.md",
    "docs/AUTOMATED_SECURITY_TOOLCHAIN_REQUEST_v4_2.md",
    "docs/GOVERNANCE_ROLE_CEREMONY_v4_2.md",
    "scripts/verify-readiness-v4-2.py",
    "scripts/generate-evidence-docket-template.py",
    "scripts/mainnet-authorization-check.py",
    "test/v4_3EthereumGateConsistency.test.ts",
    "scripts/verify-readiness-v4-3.py",
    "docs/NEAR_10_SCORECARD_v4_3.md",
    "docs/V4_3_GATE_CLEAN_DELTA.md",
    "docs/START_HERE_v4_3.md",
]
errors = []
for rel in required:
    if not (ROOT / rel).exists(): errors.append(f"Missing required file: {rel}")
for sol in (ROOT / "contracts").rglob("*.sol"):
    text = sol.read_text(encoding="utf-8", errors="ignore")
    if "pragma solidity ^0.8.24;" not in text: errors.append(f"Missing pragma: {sol.relative_to(ROOT)}")
    if text.count("{") != text.count("}"): errors.append(f"Brace mismatch: {sol.relative_to(ROOT)}")
deploy = (ROOT / "scripts/deploy-core.ts").read_text(encoding="utf-8", errors="ignore")
for needle in ["0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA", "ALLOW_MAINNET_DEPLOYMENT", "MockAGIALPHA", "AEPGoalOSCommitRegistry", "MandateEpochRegistry", "AlphaWorkUnitLedger"]:
    if needle not in deploy: errors.append(f"deploy-core.ts missing {needle}")
if "|| deployer.address" in deploy: errors.append("deploy-core.ts should not default critical addresses to deployer")
launch = (ROOT / "contracts/registry/LaunchGateRegistry.sol").read_text(encoding="utf-8", errors="ignore")
if "BASE_SEPOLIA_REHEARSAL" in launch: errors.append("LaunchGateRegistry must not contain BASE_SEPOLIA_REHEARSAL for Ethereum AGIALPHA package")
for needle in ["ETHEREUM_SEPOLIA_REHEARSAL", "AGIALPHA_TOKEN_VERIFICATION", "AUTOMATED_SECURITY_TOOLCHAIN", "INTERNAL_SECURITY_REVIEW", "FOUNDER_APPROVAL"]:
    if needle not in launch: errors.append(f"LaunchGateRegistry missing {needle}")
qa = ROOT / "qa"
qa.mkdir(exist_ok=True)
generated_at = datetime.datetime.now(datetime.UTC).isoformat()
qa_report = {
    "package": "GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY",
    "generated_at": generated_at,
    "static_checks": "passed" if not errors else "failed",
    "errors": errors,
    "notes": [
        "v4.2 supersedes v4.1 for audit and engineering handoff; it preserves v4.1 controls and adds Evidence Docket tooling, readiness verification, and mainnet authorization checks.",
        "Uses the existing AGIALPHA token on Ethereum mainnet.",
        "Does not deploy or mint AGIALPHA on mainnet.",
        "Adds AEP conformance, claim boundary, replay, commit-reveal validation, evaluator staking/slashing, reward vault, chronicle and falsification registries.",
        "Ethereum mainnet remains gated until compile/tests, automated security/toolchain review, internal security review, Sepolia rehearsal, AGIALPHA token verification, legal, tax, public claims, treasury and founder approvals are complete."
    ]
}
(qa / "QA_REPORT.json").write_text(json.dumps(qa_report, indent=2), encoding="utf-8")
manifest = []
manifest_excludes = {"qa/MANIFEST.json", "qa/MANIFEST_v4_3.json"}
for p in sorted(ROOT.rglob("*")):
    if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts:
        rel = p.relative_to(ROOT).as_posix()
        if rel in manifest_excludes:
            continue
        data = p.read_bytes()
        manifest.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
(qa / "MANIFEST.json").write_text(json.dumps({"generated_at": generated_at, "files": manifest}, indent=2), encoding="utf-8")
if errors:
    print("Static QA failed:")
    for e in errors: print("-", e)
    sys.exit(1)
print("Static QA passed.")
print(f"Files checked: {len(manifest)}")

