#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA".lower()
SKIP_PARTS = {".git", "node_modules", "cache", "artifacts", "typechain-types"}
FORBIDDEN_NAMES = {"mainnet-operator-input.json", "mainnet-operator.env", "sepolia-operator.env", "deployment-private.env"}
FORBIDDEN_PARTS = {".private", "wallets", "keys"}
SECRET_PATTERNS = [
    re.compile(r"https?://[^\s\"']*(alchemy|infura|quicknode|ankr|blast|drpc|chainstack)[^\s\"']*", re.I),
    re.compile(r"\b(?:0x)?[0-9a-fA-F]{64}\b.*(?:private|secret|key|signature)", re.I),
    re.compile(r"(?:PRIVATE_KEY|SEED_PHRASE|MNEMONIC|ETHERSCAN_API_KEY|FOUNDER_APPROVAL_SIGNATURE)[ \t]*[:=][ \t]*(?!$|PRIVATE_LOCAL_ONLY|PRIVATE_LOCAL_ONLY_OR_EMPTY|DO_NOT_COMMIT_FILL_LOCALLY|TYPE_CONFIRMATION_LOCALLY_ONLY|<|\$|process\.env)[^\s\"']+", re.I),
]
PRIVATE_ADDRESS_CONTEXT = re.compile(r"(founder|treasury|deployer|admin|vault|security|community|operator|ceremony).{0,80}0x[0-9a-fA-F]{40}", re.I)
ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}")
ENV_EXAMPLE_FILES = {".env.sepolia.example", ".env.mainnet.example", ".env.verification.example"}
ALLOWLIST_FILES = {
    "README.md",
    ".env.example",
    *ENV_EXAMPLE_FILES,
    "docs/FOUNDER_MAINNET_DEPLOYMENT_APPROVAL_MESSAGE.txt",
    "docs/MAINNET_AUTHORIZATION_INPUTS_REQUIRED.md",
    "docs/PRIVATE_INPUTS_REQUIRED_BUT_NOT_COMMITTED.md",
    "hardhat.config.ts",
    "scripts/repository_safety_check.py",
    "scripts/verify-readiness-v4-2.py",
    "scripts/deployment/lib/redact.ts",
    # The guided wizard writes ignored private templates; tracked source contains placeholder variable names only.
    "scripts/deployment/goalos-deploy-wizard.ts",
    "scripts/deployment/check-deployment-docs.js",
    # Public Sepolia verification fallback commands contain public contract addresses, not private operator addresses.
    "qa/manual-verification-commands.sepolia.md",
    ".private.example/authority-policy.mainnet.example.json",
}
SECRET_SCAN_ALLOWLIST_FILES = ALLOWLIST_FILES - ENV_EXAMPLE_FILES


def tracked_files() -> list[pathlib.Path]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return [ROOT / line for line in out.splitlines() if line]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file()]


errors: list[str] = []
for path in tracked_files():
    if not path.is_file():
        continue
    rel_path = path.relative_to(ROOT)
    rel_parts = rel_path.parts
    rel = rel_path.as_posix()
    if any(part in SKIP_PARTS for part in rel_parts):
        continue
    if path.name in FORBIDDEN_NAMES or (path.name.startswith(".env") and path.name not in {".env.example", ".env.sepolia.example", ".env.mainnet.example", ".env.verification.example"}):
        errors.append(f"Forbidden private/env file committed: {rel}")
    if (any(part in FORBIDDEN_PARTS for part in rel_parts) and not rel.startswith(".private.example/")) or (rel_parts and rel_parts[0] == "private"):
        errors.append(f"Forbidden private operator path committed: {rel}")
    if path.suffix in {".key", ".pem", ".p12", ".secret"} or rel.endswith((".private.json", ".private.env")):
        errors.append(f"Forbidden private secret file pattern committed: {rel}")
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if rel not in SECRET_SCAN_ALLOWLIST_FILES and not rel.startswith(".private.example/"):
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Potential secret/RPC/private artifact in {rel}")
    if rel not in ALLOWLIST_FILES and not (rel.startswith("deployments/") or rel.startswith("evidence/sepolia/") or rel.startswith("test/")):
        for m in PRIVATE_ADDRESS_CONTEXT.finditer(text):
            addresses = [a.lower() for a in ADDRESS_RE.findall(m.group(0))]
            if any(a != AGIALPHA for a in addresses):
                errors.append(f"Potential unredacted private operator address in {rel}")
                break
if errors:
    print("Private operator data check failed:")
    for e in sorted(set(errors)):
        print(f"- {e}")
    sys.exit(1)
print("Private operator data check passed.")
