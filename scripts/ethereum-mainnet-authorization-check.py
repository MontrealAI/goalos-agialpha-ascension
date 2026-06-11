#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
ADDRESS_RE = re.compile(r"(?<![0-9a-fA-F])0x[0-9a-fA-F]{40}(?![0-9a-fA-F])")

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha256_file(path: pathlib.Path) -> str | None: return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}
def git_commit() -> str:
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def safe(data: dict) -> bool:
    text = json.dumps(data, sort_keys=True)
    upper = text.upper()
    if not (data.get("redacted") is True and data.get("containsSecrets") is False and data.get("containsPrivateAddresses") is False):
        return False
    if "PRIVATE_KEY" in upper or "RPC_URL" in upper:
        return False
    if any(addr.lower() != AGIALPHA.lower() for addr in ADDRESS_RE.findall(text)):
        return False
    return True

def compute(with_redacted: bool) -> tuple[str, list[str], dict]:
    blockers=[]; evidence={"technicalReadinessSha256": sha256_file(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"), "deploymentAuthorizationSha256": sha256_file(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json")}
    auth_path=ROOT/"qa/public-ethereum-mainnet-authorization-evidence.json"
    auth=read_json(auth_path); evidence["ethereumAuthorizationEvidence"]={"path":"qa/public-ethereum-mainnet-authorization-evidence.json", "sha256": sha256_file(auth_path), "present": auth_path.exists(), "status": auth.get("ethereumMainnetAuthorization")}
    tech=read_json(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"); dep=read_json(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json")
    if (tech.get("status") or tech.get("TECHNICALLY_MAINNET_READY")) != "YES": blockers.append("TECHNICALLY_MAINNET_READY is not YES")
    if (dep.get("status") or dep.get("MAINNET_DEPLOYMENT_AUTHORIZED")) != "YES": blockers.append("MAINNET_DEPLOYMENT_AUTHORIZED is not YES")
    if not auth_path.exists(): blockers.append("PRIVATE_OPERATOR_EVIDENCE_PENDING: missing qa/public-ethereum-mainnet-authorization-evidence.json")
    elif not safe(auth): blockers.append("Redacted Ethereum authorization evidence failed public-safety validation")
    elif auth.get("ethereumMainnetAuthorization") != "YES": blockers.append("Redacted Ethereum Mainnet authorization evidence is not YES")
    if auth and (auth.get("chain") != "ethereum" or auth.get("chainId") != 1 or str(auth.get("agialphaToken", "")).lower() != AGIALPHA.lower()): blockers.append("Redacted Ethereum authorization target chain/token mismatch")
    if not with_redacted:
        blockers = ["PRIVATE_OPERATOR_EVIDENCE_PENDING", "Run --with-redacted-private-evidence to evaluate committed redacted private evidence"] + blockers
    return ("NO" if blockers else "YES"), blockers, evidence

def write(status: str, blockers: list[str], evidence: dict) -> dict:
    generated=now(); decision={"status":status,"ETHEREUM_MAINNET_AUTHORIZED":status,"commit":git_commit(),"chain":"ethereum","chainId":1,"agialphaToken":AGIALPHA,"evidence":evidence,"blockers":blockers,"reason": blockers[0] if blockers else "AUTHORIZED", "generatedAt":generated,"generatedBy":"scripts/ethereum-mainnet-authorization-check.py","finalManualDeploymentCommand":"npm run deploy:ethereum-mainnet:gated:local" if status=="YES" else None,"mainnetDeploymentExecuted":False}
    (ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json").write_text(json.dumps(decision, indent=2)+"\n")
    md=["# Ethereum Mainnet Authorization Decision","",f"Generated: {generated}","",f"ETHEREUM_MAINNET_AUTHORIZED: **{status}**","","## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- None."]
    md += ["", "## Boundary", "- Final deployment is local-only and must not run in CI.", "- No Ethereum Mainnet deployment occurred."]
    (ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md").write_text("\n".join(md)+"\n")
    return decision

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--public-only", action="store_true"); parser.add_argument("--with-redacted-private-evidence", action="store_true"); args=parser.parse_args()
    status, blockers, evidence=compute(args.with_redacted_private_evidence)
    print(json.dumps(write(status, blockers, evidence), indent=2))
if __name__ == "__main__": main()
