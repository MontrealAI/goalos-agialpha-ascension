#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA".lower()
SKIP_PARTS = {".git", "node_modules", "cache", "artifacts", "typechain-types"}
MAX_TEXT_SCAN_BYTES = 5_000_000
FORBIDDEN_NAMES = {"mainnet-operator-input.json", "mainnet-operator.env", "sepolia-operator.env", "deployment-private.env"}
FORBIDDEN_PARTS = {".private", "wallets", "keys"}
SECRET_PATTERNS = [
    re.compile(r"https?://[^\s\"']*(alchemy|infura|quicknode|ankr|blast|drpc|chainstack)[^\s\"']*", re.I),
    re.compile(r"\b(?:0x)?[0-9a-fA-F]{64}\b.*(?:private|secret|key|signature)", re.I),
    re.compile(r"(?:PRIVATE_KEY|SEED_PHRASE|MNEMONIC|ETHERSCAN_API_KEY|FOUNDER_APPROVAL_SIGNATURE)[ \t]*[:=][ \t]*(?!$|PRIVATE_LOCAL_ONLY|PRIVATE_LOCAL_ONLY_OR_EMPTY|DO_NOT_COMMIT_FILL_LOCALLY|TYPE_CONFIRMATION_LOCALLY_ONLY|<|\$|process\.env)[^\s\"']+", re.I),
]
PRIVATE_ADDRESS_CONTEXT = re.compile(r"(founder|treasury|deployer|admin|vault|security|community|operator|ceremony).{0,80}0x[0-9a-fA-F]{40}", re.I)
ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}")
COMMITMENT_RE = re.compile(r"0x[0-9a-fA-F]{64}")
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
    scoped = __import__("os").environ.get("NO_PRIVATE_OPERATOR_SCAN_PATHS")
    if scoped:
        return [ROOT / item for item in scoped.split(":") if item]
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return [ROOT / line for line in out.splitlines() if line]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file()]

def content_candidate_rels() -> set[str] | None:
    try:
        args = ["git", "grep", "-Il", "-e", "0x", "-ie", "private_key", "-ie", "seed_phrase", "-ie", "mnemonic", "-ie", "etherscan_api_key", "-ie", "founder_approval_signature", "-e", "alchemy", "-e", "infura", "-e", "quicknode", "-e", "ankr", "-e", "blast", "-e", "drpc", "-e", "chainstack", "--"]
        out = subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return set(out.splitlines())
    except subprocess.CalledProcessError as exc:
        return set() if exc.returncode == 1 else None
    except Exception:
        return None


findings: list[dict] = []
CONTENT_CANDIDATES = None if __import__("os").environ.get("NO_PRIVATE_OPERATOR_SCAN_PATHS") else content_candidate_rels()

def line_col(text: str, start: int) -> tuple[int, int]:
    line = text.count("\n", 0, start) + 1
    last = text.rfind("\n", 0, start)
    return line, start - last

def redact(value: str) -> str:
    if len(value) <= 10:
        return "<redacted>"
    return value[:6] + "…" + value[-4:]

def receipt_backed_chain_evidence(rel: str, text: str) -> bool:
    if not rel.startswith("qa/dormant-mainnet-deployment/"):
        return False
    try:
        import json
        data = json.loads(text)
    except Exception:
        return False
    txs = data.get("transactionHashes") if isinstance(data.get("transactionHashes"), list) else []
    receipts = data.get("receipts") if isinstance(data.get("receipts"), list) else []
    return (
        data.get("chainId") == 1
        and data.get("deploymentStatus") == "DEPLOYED_DORMANT"
        and bool(txs)
        and bool(receipts)
        and data.get("allReceiptsSuccessful") is True
        and data.get("runtimeBytecodeHashesMatch") is True
        and data.get("canonicalAgialphaMatches") is True
        and data.get("ownerRoleReadbackSucceeded") is True
        and data.get("temporaryDeployerResidualAuthority") == 0
        and data.get("officialFunding") == 0
        and data.get("activation") is False
    )

def add(rule_id: str, rel: str, reason: str, value: str = "", line: int | None = None, column: int | None = None, classification: str = "PRIVATE_PREDEPLOYMENT_OPERATOR_DATA") -> None:
    findings.append({
        "ruleId": rule_id,
        "path": rel,
        "line": line,
        "column": column,
        "redactedValue": redact(value) if value else "",
        "classification": classification,
        "reason": reason,
    })
for path in tracked_files():
    if not path.is_file():
        continue
    rel_path = path.relative_to(ROOT)
    rel_parts = rel_path.parts
    rel = rel_path.as_posix()
    if any(part in SKIP_PARTS for part in rel_parts):
        continue
    if path.name in FORBIDDEN_NAMES or (path.name.startswith(".env") and path.name not in {".env.example", ".env.sepolia.example", ".env.mainnet.example", ".env.verification.example"}):
        add("TRACKED_PRIVATE_FILE", rel, "Forbidden private/env file committed", path.name)
    if (any(part in FORBIDDEN_PARTS for part in rel_parts) and not rel.startswith(".private.example/")) or (rel_parts and rel_parts[0] == "private"):
        add("TRACKED_PRIVATE_FILE", rel, "Forbidden private operator path committed", rel)
    if path.suffix in {".key", ".pem", ".p12", ".secret"} or rel.endswith((".private.json", ".private.env")):
        add("TRACKED_PRIVATE_FILE", rel, "Forbidden private secret file pattern committed", rel)
    if CONTENT_CANDIDATES is not None and rel not in CONTENT_CANDIDATES:
        continue
    try:
        if path.stat().st_size > MAX_TEXT_SCAN_BYTES:
            continue
        raw = path.read_bytes()
    except Exception:
        continue
    raw_lower = raw.lower()
    interesting = (
        b"0x" in raw_lower
        or any(token.encode() in raw_lower for token in ("private_key", "seed_phrase", "mnemonic", "etherscan_api_key", "founder_approval_signature"))
        or any(provider.encode() in raw_lower for provider in ("alchemy", "infura", "quicknode", "ankr", "blast", "drpc", "chainstack"))
    )
    if not interesting:
        continue
    text = raw.decode("utf-8", errors="ignore")
    if rel not in SECRET_SCAN_ALLOWLIST_FILES and not rel.startswith(".private.example/"):
        lowered = text.lower()
        should_scan_secret_patterns = (
            any(provider in lowered for provider in ("alchemy", "infura", "quicknode", "ankr", "blast", "drpc", "chainstack"))
            or any(token in lowered for token in ("private_key", "seed_phrase", "mnemonic", "etherscan_api_key", "founder_approval_signature"))
            or ("0x" in lowered and any(term in lowered for term in ("private", "secret", "key", "signature")))
        )
        if should_scan_secret_patterns:
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    rule = "CREDENTIALLED_RPC_URL" if pattern.pattern.startswith("https?") else "PRIVATE_KEY_LITERAL" if "PRIVATE_KEY" in pattern.pattern else "API_KEY_LITERAL"
                    m = pattern.search(text)
                    ln, col = line_col(text, m.start()) if m else (None, None)
                    add(rule, rel, "Potential secret/RPC/private artifact", m.group(0) if m else "", ln, col)
    if rel not in ALLOWLIST_FILES and not receipt_backed_chain_evidence(rel, text) and not (rel.startswith("deployments/") or rel.startswith("evidence/sepolia/") or rel.startswith("test/")) and ADDRESS_RE.search(text):
        for m in PRIVATE_ADDRESS_CONTEXT.finditer(text):
            if re.match(r"[0-9a-fA-F]{24}", text[m.end():m.end()+24]):
                continue
            window = COMMITMENT_RE.sub("<PUBLIC_COMMITMENT>", m.group(0))
            addresses = [a.lower() for a in ADDRESS_RE.findall(window)]
            if any(a != AGIALPHA for a in addresses):
                addr = next((a for a in ADDRESS_RE.findall(window) if a.lower() != AGIALPHA), "")
                ln, col = line_col(text, m.start())
                add("PRIVATE_OPERATOR_ADDRESS", rel, "Potential unredacted private operator address", addr, ln, col)
                break
if findings:
    print("Private operator data check failed:")
    for f in findings:
        print(f"- {f['ruleId']} {f['path']}:{f.get('line') or '?'}:{f.get('column') or '?'} {f['redactedValue']} {f['reason']}")
    import json
    print(json.dumps({"status":"FAILED", "findings": findings}, indent=2, sort_keys=True))
    sys.exit(1)
print("Private operator data check passed.")
