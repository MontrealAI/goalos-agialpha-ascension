from pathlib import Path
import json
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
cert_path = ROOT / "qa/mainnet-authorization-certificate.json"
cert = json.loads(cert_path.read_text(encoding="utf-8")) if cert_path.exists() else {}
expected_eth_auth = cert.get("ethereumMainnetAuthorized", "YES")
release_state_path = ROOT / "qa/mainnet-release-state.json"
expected_deployed = "NO"
if release_state_path.exists():
    try:
        release_state = json.loads(release_state_path.read_text(encoding="utf-8"))
        expected_deployed = release_state.get("summary", {}).get("ETHEREUM_MAINNET_DEPLOYED", expected_deployed)
    except Exception:
        expected_deployed = cert.get("mainnetDeployed", expected_deployed)
else:
    expected_deployed = cert.get("mainnetDeployed", expected_deployed)
must_include = [
    "Not externally audited",
    f"Ethereum Mainnet authorization: {expected_eth_auth}",
    f"Ethereum Mainnet deployed: {expected_deployed}",
    "AGIALPHA",
    "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA",
]
for item in must_include:
    if item.lower() not in readme.lower():
        print(f"README missing required status phrase: {item}")
        sys.exit(1)

print("Repository status check passed.")
