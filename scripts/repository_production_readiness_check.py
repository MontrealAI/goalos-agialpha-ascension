from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []

required = [
    "README.md",
    "START_HERE.md",
    "GITHUB_REPOSITORY_SETTINGS.md",
    "CREATE_REPOSITORY_WEB_UI_GUIDE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "docs/PRODUCTION_CONTINUATION_PLAN.md",
    "docs/GITHUB_DAY_0_CHECKLIST.md",
    "docs/GITHUB_RULESETS_AND_BRANCH_PROTECTION.md",
    "docs/RELEASE_AND_TAGGING_STRATEGY.md",
    "docs/CODEX_PRODUCTION_HANDOFF_PROMPT.md",
    "docs/FIRST_10_GITHUB_ISSUES.md",
    "docs/PROJECT_BOARD_SETUP.md",
    "docs/PRODUCTION_READINESS_SCORECARD.md",
    "docs/SAFE_PUBLIC_REPOSITORY_POSTURE.md",
    "docs/REPOSITORY_SOURCE_OF_TRUTH.md",
    "docs/REPOSITORY_CREATION_COMMAND_CENTER.md",
    "docs/UPLOAD_BATCH_GUIDE.md",
    "docs/POST_UPLOAD_VALIDATION_RUNBOOK.md",
    "docs/FOUNDATION_HANDOFF_MEMO.md",
    "docs/REPOSITORY_ABOUT_AND_TOPICS.md",
    "docs/CANONICAL_MAPPING_SUMMARY.md",
    "docs/DO_NOT_UPLOAD.md",
    "docs/ISSUE_SEED_MANIFEST.csv",
    "GITHUB_COMMAND_CENTER.html",
    ".github/workflows/agialpha-audit-candidate-ci.yml",
    ".github/workflows/mainnet-gate-watch.yml",
    ".github/labels.yml",
    ".github/CODEOWNERS",
    "scripts/repository_safety_check.py",
    "scripts/repository_status_check.py",
    "scripts/repository_production_readiness_check.py",
    "contracts/registry/LaunchGateRegistry.sol",
    "scripts/mainnet-authorization-check.py",
    "schemas/agialpha-mainnet-gate-v4.3.schema.json",
]

for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"Missing required file: {rel}")

if (ROOT / ".github/workflows/goalos-jobs-production-rc-ci.yml").exists():
    errors.append("Stale JOBS workflow must not exist: .github/workflows/goalos-jobs-production-rc-ci.yml")

readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="ignore") if (ROOT / "README.md").exists() else ""
cert_path = ROOT / "qa/mainnet-authorization-certificate.json"
cert = json.loads(cert_path.read_text(encoding="utf-8")) if cert_path.exists() else {}
expected_eth_auth = cert.get("ethereumMainnetAuthorized", "YES")
for phrase in ["GoalOS AGIALPHA Ascension", "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA", "Not externally audited", f"Ethereum Mainnet authorization: {expected_eth_auth}", "Ethereum Mainnet deployed: NO", "Public Sepolia"]:
    if phrase.lower() not in readme.lower():
        errors.append(f"README missing required phrase: {phrase}")
if cert and cert.get("mainnetDeployed") != "NO":
    errors.append("Mainnet deployment status must remain NO without transaction evidence")

pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8")) if (ROOT / "package.json").exists() else {}
scripts = pkg.get("scripts", {})
for script in ["repo:safety", "repo:status", "repo:production-readiness", "repo:all",
        "repo:no-paid-products", "compile", "test:all", "static-check", "readiness:v4.3", "evidence:docket:template", "mainnet:authorization-check", "deploy:ethereum-sepolia", "deploy:ethereum-mainnet:gated"]:
    if script not in scripts:
        errors.append(f"package.json missing script: {script}")
if "readiness:v4.2" in scripts:
    warnings.append("package.json still contains obsolete readiness:v4.2 script")

wf = (ROOT / ".github/workflows/agialpha-audit-candidate-ci.yml")
if wf.exists():
    txt = wf.read_text(encoding="utf-8", errors="ignore")
    for must in ["npm run verify:compiler-alignment", "npm run compile:ci", "npm run test:ci", "npm run test:all", "npm run static-check", "npm run readiness:v4.3", "npm run mainnet:status-consistency"]:
        if must not in txt:
            errors.append(f"AGIALPHA CI workflow missing: {must}")

launch = (ROOT / "contracts/registry/LaunchGateRegistry.sol").read_text(encoding="utf-8", errors="ignore") if (ROOT / "contracts/registry/LaunchGateRegistry.sol").exists() else ""
for must in ["ETHEREUM_SEPOLIA_REHEARSAL", "AGIALPHA_TOKEN_VERIFICATION", "AUTOMATED_SECURITY_TOOLCHAIN", "INTERNAL_SECURITY_REVIEW", "FOUNDER_APPROVAL"]:
    if must not in launch:
        errors.append(f"LaunchGateRegistry missing {must}")
if "BASE_SEPOLIA_REHEARSAL" in launch:
    errors.append("LaunchGateRegistry contains BASE_SEPOLIA_REHEARSAL; this is an Ethereum package")

for rel in ["schemas/job.schema.json", "schemas/launch-gate.schema.json", "schemas/mainnet-gate.schema.json"]:
    p = ROOT / rel
    if p.exists() and "GoalOS $JOBS" in p.read_text(encoding="utf-8", errors="ignore"):
        errors.append(f"Schema still uses GoalOS $JOBS title: {rel}")

print(json.dumps({
    "status": "passed" if not errors else "failed",
    "errors": errors,
    "warnings": warnings,
    "message": "Repository is production-continuation ready as a GitHub starter candidate." if not errors else "Fix errors before GitHub production continuation."
}, indent=2))
if errors:
    sys.exit(1)
