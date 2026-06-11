from __future__ import annotations
import os, json, re, sys

REQUIRED_BYTES32 = [
    "LEGAL_SIGNOFF_HASH",
    "TAX_SIGNOFF_HASH",
    "SECURITY_REVIEW_HASH",
    "PUBLIC_CLAIMS_REVIEW_HASH",
  "AGIALPHA_TOKEN_VERIFICATION_HASH",
  "TREASURY_REVIEW_HASH",
    "SEPOLIA_REHEARSAL_EVIDENCE_HASH",
    "EXTERNAL_AUDIT_CLOSURE_HASH",
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
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA".lower()

def main() -> None:
    errors=[]
    if os.getenv("MAINNET_TARGET") != "ethereum":
        errors.append("MAINNET_TARGET must equal ethereum")
    if os.getenv("ALLOW_MAINNET_DEPLOYMENT") != "YES_ALL_GATES_APPROVED":
        errors.append("ALLOW_MAINNET_DEPLOYMENT must equal YES_ALL_GATES_APPROVED")
    for k in REQUIRED_BYTES32:
        v=os.getenv(k,"")
        if not re.fullmatch(r"0x[0-9a-fA-F]{64}", v):
            errors.append(f"{k} missing or not bytes32")
    for k in REQUIRED_ADDRESS:
        v=os.getenv(k,"")
        if not re.fullmatch(r"0x[0-9a-fA-F]{40}", v):
            errors.append(f"{k} missing or not EVM address")
    if os.getenv("AGIALPHA_TOKEN_ADDRESS","").lower() != AGIALPHA:
        errors.append("AGIALPHA_TOKEN_ADDRESS must be the existing Ethereum mainnet AGIALPHA token")
    status = "AUTHORIZED_ENV_PRESENT" if not errors else "NOT_AUTHORIZED"
    print(json.dumps({"status":status,"errors":errors,"mainnet":"blocked" if errors else "environment gates present; still requires human signoff and dry-run review"}, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
