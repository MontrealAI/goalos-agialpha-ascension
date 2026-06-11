#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
HEX32 = re.compile(r"^0x[0-9a-fA-F]{64}$")
ADDRESS_RE = re.compile(r"(?<![0-9a-fA-F])0x[0-9a-fA-F]{40}(?![0-9a-fA-F])")

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha256_file(path: pathlib.Path) -> str | None: return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}
def git_commit() -> str:
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def valid_hash(v: object) -> bool: return isinstance(v, str) and bool(HEX32.fullmatch(v)) and v.lower() != "0x" + "0"*64

def safe(data: dict) -> bool:
    text = json.dumps(data, sort_keys=True)
    upper = text.upper()
    if not (data.get("redacted") is True and data.get("containsSecrets") is False and data.get("containsPrivateAddresses") is False):
        return False
    if any(x in upper for x in ["PRIVATE_KEY", "RPC_URL", "FOUNDER_APPROVAL_SIGNATURE", "SEED_PHRASE"]):
        return False
    if any(addr.lower() != AGIALPHA.lower() for addr in ADDRESS_RE.findall(text)):
        return False
    return True

def load_evidence() -> tuple[dict, list[str]]:
    blockers: list[str] = []
    paths = {
        "deployment": ROOT/"qa/public-mainnet-deployment-authorization-evidence.json",
        "technical": ROOT/"qa/public-mainnet-technical-readiness-evidence.json",
    }
    evidence = {}
    for name, path in paths.items():
        data = read_json(path)
        evidence[name] = {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "present": path.exists(), "status": data.get("deploymentAuthorization") or data.get("technicalReadiness")}
        if not path.exists(): blockers.append(f"PRIVATE_OPERATOR_EVIDENCE_PENDING: missing {path.relative_to(ROOT).as_posix()}")
        elif not safe(data): blockers.append(f"Redacted evidence failed public-safety validation: {path.relative_to(ROOT).as_posix()}")
    return evidence, blockers

def validate_yes() -> tuple[dict, list[str]]:
    evidence, blockers = load_evidence()
    dep = read_json(ROOT/"qa/public-mainnet-deployment-authorization-evidence.json")
    tech = read_json(ROOT/"qa/public-mainnet-technical-readiness-evidence.json")
    if blockers: return evidence, blockers
    if tech.get("technicalReadiness") != "YES": blockers.append("Redacted technical readiness evidence is not YES")
    if dep.get("deploymentAuthorization") != "YES": blockers.append("Redacted deployment authorization evidence is not YES")
    if dep.get("founderApprovalHeldPrivately") is not True: blockers.append("Founder approval private-custody evidence is missing")
    if dep.get("publicClaimsBoundaryClean") is not True: blockers.append("Public claims boundary is not clean")
    for key in ["founderApprovalCommitmentHash", "addressCeremonyCommitmentHash", "policyDecisionCommitmentHash"]:
        if not valid_hash(dep.get(key)): blockers.append(f"Missing or invalid deployment commitment hash: {key}")
    return evidence, blockers

def write(status: str, blockers: list[str], evidence: dict) -> dict:
    generated = now()
    decision = {"status": status, "MAINNET_DEPLOYMENT_AUTHORIZED": status, "commit": git_commit(), "chain":"ethereum", "chainId":1, "agialphaToken":AGIALPHA, "evidence": evidence, "blockers": blockers, "reason": blockers[0] if blockers else "AUTHORIZED", "generatedAt": generated, "generatedBy":"scripts/mainnet-deployment-authorization-check.py", "mainnetDeploymentExecuted": False}
    for p in [ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json", ROOT/"docs/MAINNET_AUTHORIZATION_DECISION.json"]: p.write_text(json.dumps(decision, indent=2)+"\n")
    md=["# Mainnet Deployment Authorization Decision", "", f"Generated: {generated}", "", f"MAINNET_DEPLOYMENT_AUTHORIZED: **{status}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- None."]
    md += ["", "## Boundary", "- Public GitHub stores redacted commitments only; private approvals and addresses stay private.", "- No Ethereum Mainnet deployment occurred.", "- Not externally audited."]
    for p in [ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md", ROOT/"docs/MAINNET_AUTHORIZATION_DECISION.md"]: p.write_text("\n".join(md)+"\n")
    return decision

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--public-only", action="store_true"); parser.add_argument("--with-redacted-private-evidence", action="store_true"); args=parser.parse_args()
    evidence, blockers = validate_yes() if args.with_redacted_private_evidence else load_evidence()
    if not args.with_redacted_private_evidence:
        blockers = ["PRIVATE_OPERATOR_EVIDENCE_PENDING", "Run --with-redacted-private-evidence to evaluate committed redacted private evidence"] + blockers
    print(json.dumps(write("NO" if blockers else "YES", blockers, evidence), indent=2))
if __name__ == "__main__": main()
