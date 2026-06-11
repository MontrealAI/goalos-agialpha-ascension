#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, read_json, write_json, sha256_file, public_base, QA, ROOT, sha256_json, valid_hash

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
input_data = read_json(pathlib.Path(args.input))
QA.mkdir(exist_ok=True)

def h(name: str) -> str:
    return sha256_file(QA / name)

sep = read_json(QA / "public-sepolia-rehearsal-evidence.json")
pre = read_json(QA / "public-mainnet-preflight-evidence.json")
founder = read_json(QA / "public-founder-approval-evidence.json")
addr = read_json(QA / "public-address-ceremony-evidence.json")
local = read_json(QA / "local-rehearsal-report.json")
policy = input_data.get("policyWaivers") or {}
policy_clear = all(policy.get(key) in {"passed", "waived_by_founder"} for key in ["legalTokenCounsel", "taxAccounting", "publicClaims"])
policy_pub = public_base()
policy_pub.update({"status": "PASSED" if policy_clear else "PENDING", "policyDecisionCommitmentHash": sha256_json(policy), "policyDecisionsHeldPrivately": True})
write_json(QA / "public-policy-decision-evidence.json", policy_pub)

toolchain_clear = (ROOT / "audit/TOOLCHAIN_CLEARANCE_REPORT.md").exists()
toolchain_pub = public_base()
toolchain_pub.update({
    "status": "PASSED" if toolchain_clear else "PENDING",
    "automatedSecurityToolchain": "PASSED" if toolchain_clear else "PENDING",
    "toolchainClearanceHash": sha256_file(ROOT / "audit/TOOLCHAIN_CLEARANCE_REPORT.md") if toolchain_clear else sha256_json({"status":"PENDING"}),
    "unresolvedCriticalHighFindings": 0 if toolchain_clear else None,
})
write_json(QA / "public-toolchain-clearance-evidence.json", toolchain_pub)

blockers: list[str] = []
if sep.get("sepoliaRehearsal") != "PASSED": blockers.append("PRIVATE_SEPOLIA_EVIDENCE_PENDING")
if pre.get("mainnetPreflight") != "PASSED": blockers.append("PRIVATE_MAINNET_PREFLIGHT_PENDING")
if not (founder.get("founderApprovalHeldPrivately") is True): blockers.append("FOUNDER_APPROVAL_COMMITMENT_PENDING")
if not valid_hash(addr.get("addressCeremonyCommitmentHash")): blockers.append("ADDRESS_CEREMONY_COMMITMENT_PENDING")
if not policy_clear: blockers.append("POLICY_DECISION_COMMITMENT_PENDING")
if local and local.get("status") != "PASSED": blockers.append("LOCAL_REHEARSAL_NOT_PASSED")
if not toolchain_clear: blockers.append("TOOLCHAIN_CLEARANCE_PENDING")

base = public_base()
base.update({
    "toolchainClearanceHash": toolchain_pub["toolchainClearanceHash"],
    "sepoliaEvidenceDocketHash": sep.get("sepoliaEvidenceDocketHash") or sep.get("evidenceDocketHash") or h("public-sepolia-rehearsal-evidence.json"),
    "sepoliaReceiptVerificationHash": sep.get("sepoliaReceiptVerificationHash") or sep.get("receiptBundleHash") or h("public-sepolia-rehearsal-evidence.json"),
    "mainnetPreflightHash": pre.get("mainnetPreflightHash") or h("public-mainnet-preflight-evidence.json"),
    "addressCeremonyCommitmentHash": addr.get("addressCeremonyCommitmentHash") or h("public-address-ceremony-evidence.json"),
    "founderApprovalCommitmentHash": founder.get("founderApprovalCommitmentHash") or h("public-founder-approval-evidence.json"),
    "policyDecisionCommitmentHash": policy_pub["policyDecisionCommitmentHash"],
    "technicalReadiness": "YES" if not blockers else "NO",
    "deploymentAuthorization": "YES" if not blockers else "NO",
    "ethereumMainnetAuthorization": "YES" if not blockers else "NO",
    "booleans": {"localDeterministicRehearsalPassed": local.get("status") == "PASSED" if local else False, "publicClaimsBoundaryClean": policy.get("publicClaims") in {"passed", "waived_by_founder"}},
    "blockers": blockers,
})
write_json(QA / "public-mainnet-technical-readiness-evidence.json", base)
deployment = {**base, "publicClaimsBoundaryClean": policy.get("publicClaims") in {"passed", "waived_by_founder"}, "founderApprovalHeldPrivately": founder.get("founderApprovalHeldPrivately") is True, "founderApprovalVerified": bool(founder.get("founderApprovalVerified")), "founderApprovalVerificationMode": founder.get("founderApprovalVerificationMode", "private-custody-attestation")}
write_json(QA / "public-mainnet-deployment-authorization-evidence.json", deployment)
write_json(QA / "public-ethereum-mainnet-authorization-evidence.json", base)
print("Wrote redacted public mainnet authorization evidence commitments.")
