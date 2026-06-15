from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

SKIP_PARTS = {"node_modules", ".git", "qa", ".private", "private", "wallets", "keys"}
SKIP_FILES = {
    "repository_safety_check.py",
    "repository_production_readiness_check.py",
    "verify-readiness-v4-2.py",
    "verify-readiness-v4-3.py",
}

SECRET_PATTERNS = [
    r"PRIVATE_KEY=0x[0-9a-fA-F]{64}",
    r"MNEMONIC\s*=",
    r"SEED_PHRASE\s*=",
    r"API_KEY\s*=\s*['\"][A-Za-z0-9_\-]{20,}",
    r"RPC_URL\s*=\s*https?://.*[A-Za-z0-9]{20,}",
]

POSITIVE_UNSAFE_PATTERNS = [
    r"\bis\s+mainnet\s+authorized\b",
    r"\bmainnet\s+is\s+authorized\b",
    r"\baudited\s+and\s+approved\b",
    r"\bguaranteed\s+profit\b",
    r"\bguaranteed\s+yield\b",
    r"\bwill\s+increase\s+in\s+price\b",
]

SAFE_NEGATIONS = [
    "not ",
    "no ",
    "do not",
    "must not",
    "never",
    "without",
    "prohibited",
    "avoid",
    "blocked",
    "unauthorized",
    "not audited",
    "not mainnet authorized",
    "mainnet not authorized",
    "mainnet remains blocked",
]

def safe_context(text, idx):
    ctx = text[max(0, idx - 160): idx + 160].lower()
    return any(x in ctx for x in SAFE_NEGATIONS)

def line_for_index(text, idx):
    start = text.rfind("\n", 0, idx) + 1
    end = text.find("\n", idx)
    if end == -1:
        end = len(text)
    return text[start:end]

def is_regex_source_false_positive(line, path):
    # Repository verifier scripts intentionally contain secret-detector strings
    # (for example MNEMONIC\s*= or SEED_PHRASE\s*=) so they can reject
    # committed secrets in generated sites. Those detector patterns are not
    # themselves secrets. Keep normal files strict, but avoid blocking verifier
    # source code for containing the regexes it is supposed to run.
    verifier_source = path.name.startswith("verify_") or path.name.startswith("validate-")
    detector_terms = ("PRIVATE_KEY", "SEED_PHRASE", "MNEMONIC", "API_KEY", "RPC_URL")
    if verifier_source and any(term in line for term in detector_terms):
        return True
    return "\\s" in line or "re.compile" in line or "SECRET_PATTERNS" in line or "BAD_PATTERNS" in line

for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
        continue
    if path.name in SKIP_FILES:
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in SECRET_PATTERNS:
        for match in re.finditer(pattern, text):
            if is_regex_source_false_positive(line_for_index(text, match.start()), path):
                continue
            ERRORS.append(f"possible secret pattern in {path.relative_to(ROOT)}: {pattern}")

    low = text.lower()
    for pattern in POSITIVE_UNSAFE_PATTERNS:
        for match in re.finditer(pattern, low):
            if not safe_context(low, match.start()):
                ERRORS.append(f"unsafe affirmative public claim in {path.relative_to(ROOT)}: {match.group(0)}")

if ERRORS:
    print("Repository safety check failed:")
    for e in ERRORS:
        print("-", e)
    sys.exit(1)

print("Repository safety check passed.")
