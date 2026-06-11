from __future__ import annotations
import os, json, re, pathlib, datetime, sys

REQUIRED_BYTES32 = [
    "LEGAL_SIGNOFF_HASH", "TAX_SIGNOFF_HASH", "SECURITY_REVIEW_HASH",
    "PUBLIC_CLAIMS_REVIEW_HASH", "TREASURY_REVIEW_HASH",
    "AGIALPHA_TOKEN_VERIFICATION_HASH", "SEPOLIA_REHEARSAL_EVIDENCE_HASH",
    "EXTERNAL_AUDIT_CLOSURE_HASH", "FOUNDER_APPROVAL_HASH",
]
REQUIRED_ADDRESS = [
    "AGIALPHA_TOKEN_ADDRESS", "FOUNDER_ADDRESS", "TREASURY_ADDRESS",
    "COMMERCIALIZATION_PERFORMANCE_ADMIN", "PROOF_REWARDS_ADMIN",
    "LIQUIDITY_ADMIN", "SECURITY_ADMIN", "COMMUNITY_ADMIN",
]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"

def is_placeholder(v: str) -> bool:
    return v.lower() in {"0x" + "0"*64, "0x" + "1"*64, "0x" + "f"*64}

def main() -> None:
    blockers=[]
    if os.getenv("MAINNET_TARGET") != "ethereum": blockers.append("MAINNET_TARGET must equal ethereum")
    if os.getenv("ALLOW_MAINNET_DEPLOYMENT") != "YES_ALL_GATES_APPROVED": blockers.append("ALLOW_MAINNET_DEPLOYMENT must equal YES_ALL_GATES_APPROVED only after all real gates are complete")
    for k in REQUIRED_BYTES32:
        v=os.getenv(k,"")
        if not re.fullmatch(r"0x[0-9a-fA-F]{64}", v): blockers.append(f"{k} missing or not bytes32")
        elif is_placeholder(v): blockers.append(f"{k} appears to be placeholder/fabricated and is not accepted")
    for k in REQUIRED_ADDRESS:
        v=os.getenv(k,"")
        if not re.fullmatch(r"0x[0-9a-fA-F]{40}", v): blockers.append(f"{k} missing or not EVM address")
        elif v.lower() == "0x"+"0"*40: blockers.append(f"{k} cannot be zero address")
    if os.getenv("AGIALPHA_TOKEN_ADDRESS","").lower() != AGIALPHA.lower(): blockers.append("AGIALPHA_TOKEN_ADDRESS must be the existing Ethereum mainnet AGIALPHA token")
    audit_summary = pathlib.Path('audit/reports/latest.txt')
    if audit_summary.exists():
        summary_path=pathlib.Path(audit_summary.read_text().strip())/'audit-summary.json'
        if summary_path.exists():
            try:
                s=json.loads(summary_path.read_text())
                if s.get('critical_high_unresolved',0): blockers.append('Unresolved critical/high audit findings remain')
                if s.get('medium_unaccepted',0): blockers.append('Unaccepted medium audit findings remain')
            except Exception: blockers.append('Audit summary could not be parsed')
    status = "AUTHORIZED" if not blockers else "NOT_AUTHORIZED"
    decision = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "decision": status,
        "blockers": blockers,
        "mainnet": "blocked" if blockers else "technical environment gates present; final explicit founder approval still required before deployment",
        "agialpha_mainnet_token_required": AGIALPHA,
        "deploy_command_if_authorized": "hardhat run scripts/deploy-ethereum-mainnet-gated.ts --network mainnet" if not blockers else None,
        "final_human_confirmation_required": True,
    }
    pathlib.Path('docs').mkdir(exist_ok=True)
    pathlib.Path('docs/MAINNET_AUTHORIZATION_DECISION.json').write_text(json.dumps(decision, indent=2)+"\n")
    md=["# Mainnet Authorization Decision", "", f"Generated: {decision['generated_at']}", "", f"Decision: **{status}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- No technical environment blockers detected; final explicit founder deployment approval still required."]
    md += ["", "## Mainnet Boundary", f"- Required AGIALPHA token: `{AGIALPHA}`", "- This checker performs read-only/environment validation only and does not deploy."]
    pathlib.Path('docs/MAINNET_AUTHORIZATION_DECISION.md').write_text("\n".join(md)+"\n")
    print(json.dumps(decision, indent=2))
    # NOT_AUTHORIZED is expected when real gates are absent; keep CI non-failing unless strict mode is requested.
    if blockers and os.getenv('STRICT_MAINNET_AUTHORIZATION_CHECK') == '1':
        raise SystemExit(1)
if __name__ == "__main__": main()
