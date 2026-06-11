from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md",
    "START_HERE.md",
    "GITHUB_REPOSITORY_SETTINGS.md",
    "CREATE_REPOSITORY_WEB_UI_GUIDE.md",
    "LICENSE_DECISION.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "docs/REPOSITORY_STATUS.md",
    "docs/SAFE_CLAIMS.md",
]

missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    print("Missing required files:")
    for p in missing:
        print("-", p)
    sys.exit(1)

readme = (ROOT / "README.md").read_text(encoding="utf-8")
must_include = [
    "Not audited",
    "not mainnet authorized",
    "AGIALPHA",
    "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA",
]
for item in must_include:
    if item.lower() not in readme.lower():
        print(f"README missing required status phrase: {item}")
        sys.exit(1)

print("Repository status check passed.")
