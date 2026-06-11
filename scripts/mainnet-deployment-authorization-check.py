#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, os, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
ALLOW_VALUE = "YES_FOUNDER_APPROVED_MAINNET_AUTHORIZATION"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rel(p: pathlib.Path) -> str: return p.relative_to(ROOT).as_posix()
def sha256_file(path: pathlib.Path) -> str | None: return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}
def git_commit() -> str:
    try: return subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def has_text(path: pathlib.Path, needle: str) -> bool:
    return path.exists() and needle in path.read_text(errors="ignore")
def valid_bytes32(v: str | None) -> bool:
    return bool(v and re.fullmatch(r"0x[0-9a-fA-F]{64}", v) and not re.fullmatch(r"0x(0{64}|1{64}|f{64})", v, re.I))
def valid_address(v: str | None) -> bool:
    return bool(v and re.fullmatch(r"0x[0-9a-fA-F]{40}", v) and not re.fullmatch(r"0x0{40}", v, re.I))

def main() -> None:
    blockers: list[str] = []
    evidence: dict[str, object] = {}
    readiness = read_json(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json")
    evidence["technicalReadinessDecision"] = {"path":"docs/MAINNET_TECHNICAL_READINESS_DECISION.json", "sha256": sha256_file(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"), "status": readiness.get("status") or readiness.get("TECHNICALLY_MAINNET_READY")}
    if evidence["technicalReadinessDecision"]["status"] != "YES": blockers.append("TECHNICALLY_MAINNET_READY is not YES")
    for b in readiness.get("blockers", []): blockers.append(f"technical: {b}")

    address = read_json(ROOT/"qa/ADDRESS_CEREMONY.json")
    evidence["addressCeremony"] = {"path":"qa/ADDRESS_CEREMONY.json", "sha256": sha256_file(ROOT/"qa/ADDRESS_CEREMONY.json"), "status": address.get("status")}
    if address.get("status") != "PASSED": blockers.append("Treasury/founder/admin address ceremony is missing or not PASSED")
    for key in ["founderAddress","deployerAddress","treasuryAddress","commercializationPerformanceAdmin","proofRewardsAdmin","liquidityAdmin","securityAdmin","communityAdmin","emergencyAdmin"]:
        if not valid_address(address.get(key)): blockers.append(f"Address ceremony missing valid {key}")
    if str(address.get("chainId")) != "1": blockers.append("Address ceremony chainId must be 1")
    if str(address.get("agialphaToken", "")).lower() != AGIALPHA.lower(): blockers.append("Address ceremony AGIALPHA token mismatch")

    founder = read_json(ROOT/"qa/FOUNDER_APPROVAL.json")
    evidence["founderApproval"] = {"path":"qa/FOUNDER_APPROVAL.json", "sha256": sha256_file(ROOT/"qa/FOUNDER_APPROVAL.json"), "status": founder.get("status")}
    if founder.get("status") != "PASSED": blockers.append("Founder deployment approval is missing or not PASSED")
    if not valid_bytes32(founder.get("messageHash")): blockers.append("Founder approval message hash missing or invalid")
    if not valid_address(founder.get("signer")): blockers.append("Founder approval signer missing or invalid")
    if not founder.get("signatureVerified", False): blockers.append("Founder approval signature is not verified")

    policy = read_json(ROOT/"qa/POLICY_SIGNOFFS_OR_WAIVERS.json")
    evidence["policySignoffsOrWaivers"] = {"path":"qa/POLICY_SIGNOFFS_OR_WAIVERS.json", "sha256": sha256_file(ROOT/"qa/POLICY_SIGNOFFS_OR_WAIVERS.json"), "status": policy.get("status")}
    if policy.get("status") != "PASSED": blockers.append("Policy signoffs/waivers are missing or not PASSED")
    for key in ["LEGAL_TOKEN_COUNSEL","TAX_ACCOUNTING","PUBLIC_CLAIMS","TREASURY","AUTOMATED_SECURITY_TOOLCHAIN","INTERNAL_SECURITY_REVIEW"]:
        value = policy.get("statuses", {}).get(key)
        allowed = {"PASSED", "WAIVED_BY_FOUNDER"} if key in {"LEGAL_TOKEN_COUNSEL","TAX_ACCOUNTING","PUBLIC_CLAIMS"} else {"PASSED"}
        if value not in allowed: blockers.append(f"Policy gate {key} is {value or 'missing'}")

    if os.getenv("ALLOW_MAINNET_DEPLOYMENT") != ALLOW_VALUE:
        blockers.append(f"ALLOW_MAINNET_DEPLOYMENT must equal {ALLOW_VALUE} only after all evidence and founder approval are complete")
    if not valid_bytes32(os.getenv("FOUNDER_APPROVAL_HASH")): blockers.append("FOUNDER_APPROVAL_HASH missing or not bytes32")

    status = "NO" if blockers else "YES"
    generated = now()
    decision = {"status": status, "MAINNET_DEPLOYMENT_AUTHORIZED": status, "commit": git_commit(), "chain":"ethereum", "chainId":1, "agialphaToken":AGIALPHA, "evidence": evidence, "blockers": blockers, "generatedAt": generated, "generatedBy":"scripts/mainnet-deployment-authorization-check.py", "mainnetDeploymentExecuted": False}
    for out in [ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json", ROOT/"docs/MAINNET_AUTHORIZATION_DECISION.json"]: out.write_text(json.dumps(decision, indent=2)+"\n")
    md = ["# Mainnet Deployment Authorization Decision", "", f"Generated: {generated}", "", f"MAINNET_DEPLOYMENT_AUTHORIZED: **{status}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- None."]
    md += ["", "## Boundary", f"- Required AGIALPHA token: `{AGIALPHA}`", "- No Ethereum Mainnet deployment occurred in this PR.", "- Not externally audited."]
    for out in [ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md", ROOT/"docs/MAINNET_AUTHORIZATION_DECISION.md"]: out.write_text("\n".join(md)+"\n")
    print(json.dumps(decision, indent=2))

if __name__ == "__main__": main()
