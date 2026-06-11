#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, os, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
ALLOW_VALUE = "YES_FOUNDER_APPROVED_MAINNET_AUTHORIZATION"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha256_file(path: pathlib.Path) -> str | None: return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}
def git_commit() -> str:
    try: return subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"
def valid_bytes32(v: str | None) -> bool: return bool(v and re.fullmatch(r"0x[0-9a-fA-F]{64}", v) and not re.fullmatch(r"0x(0{64}|1{64}|f{64})", v, re.I))

def main() -> None:
    blockers: list[str] = []
    deploy = read_json(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json")
    technical = read_json(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json")
    if (technical.get("status") or technical.get("TECHNICALLY_MAINNET_READY")) != "YES": blockers.append("TECHNICALLY_MAINNET_READY is not YES")
    if (deploy.get("status") or deploy.get("MAINNET_DEPLOYMENT_AUTHORIZED")) != "YES": blockers.append("MAINNET_DEPLOYMENT_AUTHORIZED is not YES")
    if os.getenv("MAINNET_TARGET") != "ethereum": blockers.append("MAINNET_TARGET must equal ethereum")
    if str(os.getenv("AGIALPHA_TOKEN_ADDRESS", "")).lower() != AGIALPHA.lower(): blockers.append("AGIALPHA_TOKEN_ADDRESS must match the existing Ethereum Mainnet AGIALPHA token")
    if os.getenv("CHAIN_ID") not in {"1", None} and os.getenv("CHAIN_ID") != "1": blockers.append("CHAIN_ID must be 1 when supplied")
    if os.getenv("ALLOW_MAINNET_DEPLOYMENT") != ALLOW_VALUE: blockers.append(f"ALLOW_MAINNET_DEPLOYMENT must equal {ALLOW_VALUE}")
    if not valid_bytes32(os.getenv("FOUNDER_APPROVAL_HASH")): blockers.append("FOUNDER_APPROVAL_HASH missing or not bytes32")
    workflow_text = "\n".join(p.read_text(errors="ignore") for p in (ROOT/".github/workflows").glob("*.yml")) if (ROOT/".github/workflows").exists() else ""
    if "deploy:ethereum-mainnet:gated" in workflow_text or "deploy-ethereum-mainnet-gated" in workflow_text:
        blockers.append("CI workflow appears to contain an Ethereum Mainnet deployment command")
    runbook = ROOT/"docs/FINAL_ETHEREUM_MAINNET_DEPLOYMENT_RUNBOOK.md"
    if not runbook.exists() and not blockers:
        blockers.append("Final manual deployment runbook is missing")
    status = "NO" if blockers else "YES"
    generated = now()
    decision = {"status": status, "ETHEREUM_MAINNET_AUTHORIZED": status, "commit": git_commit(), "chain":"ethereum", "chainId":1, "agialphaToken":AGIALPHA, "evidence": {"technicalReadinessSha256": sha256_file(ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"), "deploymentAuthorizationSha256": sha256_file(ROOT/"docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json")}, "blockers": blockers, "generatedAt": generated, "generatedBy":"scripts/ethereum-mainnet-authorization-check.py", "finalManualDeploymentCommand": "npm run deploy:ethereum-mainnet:gated" if status == "YES" else None, "mainnetDeploymentExecuted": False}
    (ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json").write_text(json.dumps(decision, indent=2)+"\n")
    md = ["# Ethereum Mainnet Authorization Decision", "", f"Generated: {generated}", "", f"ETHEREUM_MAINNET_AUTHORIZED: **{status}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- None."]
    md += ["", "## Boundary", "- This decision only authorizes a manual founder/deployer-run gated command when YES.", "- CI must not automatically deploy Ethereum Mainnet.", "- No Ethereum Mainnet deployment occurred in this PR."]
    (ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md").write_text("\n".join(md)+"\n")
    print(json.dumps(decision, indent=2))
if __name__ == "__main__": main()
