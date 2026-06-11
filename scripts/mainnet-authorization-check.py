from __future__ import annotations
import datetime
import json
import os
import pathlib
import re

REQUIRED_BYTES32 = [
    "LEGAL_SIGNOFF_HASH",
    "TAX_SIGNOFF_HASH",
    "SECURITY_REVIEW_HASH",
    "PUBLIC_CLAIMS_REVIEW_HASH",
    "TREASURY_REVIEW_HASH",
    "AGIALPHA_TOKEN_VERIFICATION_HASH",
    "SEPOLIA_REHEARSAL_EVIDENCE_HASH",
    "AUTOMATED_SECURITY_TOOLCHAIN_HASH",
    "INTERNAL_SECURITY_REVIEW_HASH",
    "FOUNDER_APPROVAL_HASH",
]
REQUIRED_ADDRESS = [
    "AGIALPHA_TOKEN_ADDRESS",
    "FOUNDER_ADDRESS",
    "TREASURY_ADDRESS",
    "COMMERCIALIZATION_PERFORMANCE_ADMIN",
    "PROOF_REWARDS_ADMIN",
    "LIQUIDITY_ADMIN",
    "SECURITY_ADMIN",
    "COMMUNITY_ADMIN",
]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"


def is_placeholder(v: str) -> bool:
    return v.lower() in {"0x" + "0" * 64, "0x" + "1" * 64, "0x" + "f" * 64}


def load_readiness_blockers() -> list[str]:
    path = pathlib.Path("docs/MAINNET_TECHNICAL_READINESS_DECISION.json")
    if not path.exists():
        return ["TECHNICALLY_MAINNET_READY decision is missing"]
    try:
        data = json.loads(path.read_text())
    except Exception:
        return ["TECHNICALLY_MAINNET_READY decision could not be parsed"]
    if data.get("TECHNICALLY_MAINNET_READY") != "YES":
        return ["TECHNICALLY_MAINNET_READY is not YES"] + [f"technical: {b}" for b in data.get("blockers", [])]
    return []


def main() -> None:
    blockers: list[str] = []
    if os.getenv("MAINNET_TARGET") != "ethereum":
        blockers.append("MAINNET_TARGET must equal ethereum")
    if os.getenv("ALLOW_MAINNET_DEPLOYMENT") != "YES_ALL_GATES_APPROVED":
        blockers.append("ALLOW_MAINNET_DEPLOYMENT must equal YES_ALL_GATES_APPROVED only after all real gates are complete and founder approval is explicit")
    for k in REQUIRED_BYTES32:
        v = os.getenv(k, "")
        if not re.fullmatch(r"0x[0-9a-fA-F]{64}", v):
            blockers.append(f"{k} missing or not bytes32")
        elif is_placeholder(v):
            blockers.append(f"{k} appears to be placeholder/fabricated and is not accepted")
    for k in REQUIRED_ADDRESS:
        v = os.getenv(k, "")
        if not re.fullmatch(r"0x[0-9a-fA-F]{40}", v):
            blockers.append(f"{k} missing or not EVM address")
        elif v.lower() == "0x" + "0" * 40:
            blockers.append(f"{k} cannot be zero address")
    if os.getenv("AGIALPHA_TOKEN_ADDRESS", "").lower() != AGIALPHA.lower():
        blockers.append("AGIALPHA_TOKEN_ADDRESS must be the existing Ethereum mainnet AGIALPHA token")
    blockers.extend(load_readiness_blockers())

    status = "YES" if not blockers else "NO"
    generated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    decision = {
        "generated_at": generated,
        "MAINNET_DEPLOYMENT_AUTHORIZED": status,
        "decision": "AUTHORIZED" if status == "YES" else "NOT_AUTHORIZED",
        "blockers": blockers,
        "agialpha_mainnet_token_required": AGIALPHA,
        "deploy_command_if_authorized": "hardhat run scripts/deploy-ethereum-mainnet-gated.ts --network mainnet" if status == "YES" else None,
        "final_founder_confirmation_required": True,
        "mainnet_deployment_executed": False,
    }
    pathlib.Path("docs").mkdir(exist_ok=True)
    for path in ["docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json", "docs/MAINNET_AUTHORIZATION_DECISION.json"]:
        pathlib.Path(path).write_text(json.dumps(decision, indent=2) + "\n")
    md = [
        "# Mainnet Deployment Authorization Decision",
        "",
        f"Generated: {generated}",
        "",
        f"MAINNET_DEPLOYMENT_AUTHORIZED: **{status}**",
        "",
        "## Blockers",
    ]
    md += [f"- {b}" for b in blockers] or ["- No computed blockers. Final founder confirmation is still required before deployment."]
    md += [
        "",
        "## Mainnet Boundary",
        f"- Required AGIALPHA token: `{AGIALPHA}`",
        "- This checker performs read-only/environment validation only and does not deploy.",
        "- This project is not externally audited; it relies on automated security/toolchain and internal security-review evidence.",
    ]
    for path in ["docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md", "docs/MAINNET_AUTHORIZATION_DECISION.md"]:
        pathlib.Path(path).write_text("\n".join(md) + "\n")
    print(json.dumps(decision, indent=2))
    if blockers and os.getenv("STRICT_MAINNET_AUTHORIZATION_CHECK") == "1":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
