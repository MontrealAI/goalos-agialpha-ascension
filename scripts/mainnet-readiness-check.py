#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
HEX32 = re.compile(r"^0x[0-9a-fA-F]{64}$")


def now() -> str: return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha256_file(path: pathlib.Path) -> str | None: return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}
def git_commit() -> str:
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def valid_hash(value: object) -> bool: return isinstance(value, str) and bool(HEX32.fullmatch(value)) and value.lower() != "0x" + "0" * 64

def evidence_has_no_private_data(data: dict) -> bool:
    text = json.dumps(data, sort_keys=True)
    forbidden = ["PRIVATE_KEY", "RPC_URL", "SEPOLIA_RPC", "MAINNET_RPC", "ETHERSCAN_API_KEY", "FOUNDER_APPROVAL_SIGNATURE"]
    if any(token in text.upper() for token in forbidden): return False
    if data.get("containsSecrets") is not False: return False
    if data.get("containsPrivateAddresses") is not False: return False
    if data.get("redacted") is not True: return False
    return True

def load_public_evidence() -> tuple[dict[str, dict], list[str]]:
    paths = {
        "technical": ROOT/"qa/public-mainnet-technical-readiness-evidence.json",
        "sepolia": ROOT/"qa/public-sepolia-rehearsal-evidence.json",
        "preflight": ROOT/"qa/public-mainnet-preflight-evidence.json",
        "toolchain": ROOT/"qa/public-toolchain-clearance-evidence.json",
    }
    evidence: dict[str, dict] = {}
    blockers: list[str] = []
    for name, path in paths.items():
        data = read_json(path)
        evidence[name] = {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "present": path.exists(), "status": data.get("status") or data.get("technicalReadiness")}
        if not path.exists(): blockers.append(f"PRIVATE_OPERATOR_EVIDENCE_PENDING: missing {path.relative_to(ROOT).as_posix()}")
        elif not evidence_has_no_private_data(data): blockers.append(f"Redacted evidence failed public-safety validation: {path.relative_to(ROOT).as_posix()}")
    return evidence, blockers

def validate_redacted_yes() -> tuple[dict[str, dict], list[str]]:
    evidence, blockers = load_public_evidence()
    tech = read_json(ROOT/"qa/public-mainnet-technical-readiness-evidence.json")
    sep = read_json(ROOT/"qa/public-sepolia-rehearsal-evidence.json")
    pre = read_json(ROOT/"qa/public-mainnet-preflight-evidence.json")
    tool = read_json(ROOT/"qa/public-toolchain-clearance-evidence.json")
    if blockers: return evidence, blockers
    if tech.get("technicalReadiness") != "YES": blockers.append("Redacted technical readiness evidence is not YES")
    if sep.get("sepoliaRehearsal") != "PASSED": blockers.append("Redacted private Sepolia rehearsal evidence is not PASSED")
    if pre.get("mainnetPreflight") != "PASSED": blockers.append("Redacted private mainnet preflight evidence is not PASSED")
    if tool.get("automatedSecurityToolchain") != "PASSED": blockers.append("Redacted toolchain clearance evidence is not PASSED")
    for key in ["toolchainClearanceHash", "sepoliaEvidenceDocketHash", "sepoliaReceiptVerificationHash", "mainnetPreflightHash", "addressCeremonyCommitmentHash", "founderApprovalCommitmentHash", "policyDecisionCommitmentHash"]:
        if not valid_hash(tech.get(key) or sep.get(key) or pre.get(key) or tool.get(key)):
            blockers.append(f"Missing or invalid redacted commitment hash: {key}")
    if tech.get("chain") != "ethereum" or tech.get("chainId") != 1 or str(tech.get("agialphaToken", "")).lower() != AGIALPHA.lower():
        blockers.append("Redacted technical evidence target chain/token mismatch")
    return evidence, blockers

def write_decision(status: str, blockers: list[str], evidence: dict) -> dict:
    generated = now()
    decision = {
        "status": status,
        "TECHNICALLY_MAINNET_READY": status,
        "commit": git_commit(),
        "chain": "ethereum",
        "chainId": 1,
        "agialphaToken": AGIALPHA,
        "evidence": evidence,
        "blockers": blockers,
        "generatedAt": generated,
        "generatedBy": "scripts/mainnet-readiness-check.py",
        "mainnetDeploymentExecuted": False,
    }
    (ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json").write_text(json.dumps(decision, indent=2)+"\n")
    md = ["# Mainnet Technical Readiness Decision", "", f"Generated: {generated}", "", f"TECHNICALLY_MAINNET_READY: **{status}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- None."]
    md += ["", "## Public/private evidence boundary", "- Public GitHub stores redacted commitments only.", "- Private RPC URLs, keys, signatures, and addresses are not required in GitHub.", "- No Ethereum Mainnet deployment occurred."]
    (ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.md").write_text("\n".join(md)+"\n")
    return decision

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-only", action="store_true")
    parser.add_argument("--with-redacted-private-evidence", action="store_true")
    args = parser.parse_args()
    if args.with_redacted_private_evidence:
        evidence, blockers = validate_redacted_yes()
    else:
        evidence, blockers = load_public_evidence()
        if blockers:
            blockers = ["PRIVATE_OPERATOR_EVIDENCE_PENDING"] + blockers
    status = "NO" if blockers else "YES"
    print(json.dumps(write_decision(status, blockers, evidence), indent=2))
if __name__ == "__main__": main()
