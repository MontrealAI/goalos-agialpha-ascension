#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA".lower()
SKIP_PARTS = {".git", "node_modules", "cache", "artifacts", "typechain-types"}
FORBIDDEN_NAMES = {".env", "mainnet-operator-input.json", "mainnet-operator.env", "sepolia-operator.env", "deployment-private.env"}
FORBIDDEN_PARTS = {".private", "wallets", "keys"}
SECRET_PATTERNS = [
    re.compile(r"https?://[^\s\"']*(alchemy|infura|quicknode|ankr|blast|drpc|chainstack)[^\s\"']*", re.I),
    re.compile(r"\b(?:0x)?[0-9a-fA-F]{64}\b.*(?:private|secret|key|signature)", re.I),
    re.compile(r"(?:PRIVATE_KEY|SEED_PHRASE|MNEMONIC|ETHERSCAN_API_KEY|FOUNDER_APPROVAL_SIGNATURE)[ \t]*[:=][ \t]*(?!$|PRIVATE_LOCAL_ONLY|PRIVATE_LOCAL_ONLY_OR_EMPTY|<|\$|process\.env)[^\s\"']+", re.I),
]
PRIVATE_ADDRESS_CONTEXT = re.compile(r"(founder|treasury|deployer|admin|vault|security|community|operator|ceremony).{0,80}0x[0-9a-fA-F]{40}", re.I)
ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}")
ALLOWLIST_FILES = {
    "README.md", ".env.example", "docs/FOUNDER_MAINNET_DEPLOYMENT_APPROVAL_MESSAGE.txt",
    "docs/MAINNET_AUTHORIZATION_INPUTS_REQUIRED.md", "docs/PRIVATE_INPUTS_REQUIRED_BUT_NOT_COMMITTED.md", "hardhat.config.ts", "scripts/repository_safety_check.py", "scripts/verify-readiness-v4-2.py",
}
errors: list[str] = []
for path in ROOT.rglob("*"):
    if not path.is_file(): continue
    rel = path.relative_to(ROOT).as_posix()
    if any(part in SKIP_PARTS for part in path.parts): continue
    if path.name in FORBIDDEN_NAMES and path.name != ".env.example": errors.append(f"Forbidden private/env file committed: {rel}")
    if path.parts[0] in FORBIDDEN_PARTS or (len(path.parts) > 1 and path.parts[0] == "private"):
        errors.append(f"Forbidden private operator path committed: {rel}")
    if path.suffix in {".key", ".pem", ".p12", ".secret"} or rel.endswith((".private.json", ".private.env")):
        errors.append(f"Forbidden private secret file pattern committed: {rel}")
    try: text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception: continue
    if rel not in ALLOWLIST_FILES:
        for pattern in SECRET_PATTERNS:
            if pattern.search(text): errors.append(f"Potential secret/RPC/private artifact in {rel}")
    if rel not in ALLOWLIST_FILES and not (rel.startswith("deployments/") or rel.startswith("evidence/sepolia/") or rel.startswith("test/")):
        for m in PRIVATE_ADDRESS_CONTEXT.finditer(text):
            addresses = [a.lower() for a in ADDRESS_RE.findall(m.group(0))]
            if any(a != AGIALPHA for a in addresses):
                errors.append(f"Potential unredacted private operator address in {rel}")
                break
if errors:
    print("Private operator data check failed:")
    for e in sorted(set(errors)): print(f"- {e}")
    sys.exit(1)
print("Private operator data check passed.")
