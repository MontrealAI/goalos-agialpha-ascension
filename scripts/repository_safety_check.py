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
    # These website verification scripts contain literal denylist regexes such as
    # MNEMONIC\s*= and SEED_PHRASE\s*= to detect secrets in generated sites.
    # The literals are scanner rules, not committed secrets.
    "verify_goalos_agialpha_final_main_website_v39.py",
    "verify_goalos_agialpha_final_main_website_v40.py",
    "verify_goalos_agialpha_final_main_website_v41.py",
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

for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
        continue
    if path.name in SKIP_FILES:
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
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
