from __future__ import annotations
import datetime, hashlib, json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rel(p: pathlib.Path) -> str: return p.relative_to(ROOT).as_posix()
def sha256_file(path: pathlib.Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}

def git_commit() -> str:
    try: return subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"

def has_text(path: pathlib.Path, *needles: str) -> bool:
    if not path.exists(): return False
    text = path.read_text(errors="ignore")
    return all(n in text for n in needles)

def main() -> None:
    blockers: list[str] = []
    evidence: dict[str, object] = {}

    baseline = read_json(ROOT/"qa/BASELINE_GREEN_REPORT.json")
    evidence["baselineGreenReport"] = {"path": "qa/BASELINE_GREEN_REPORT.json", "sha256": sha256_file(ROOT/"qa/BASELINE_GREEN_REPORT.json"), "status": baseline.get("status")}
    if baseline.get("status") != "BASELINE_GREEN": blockers.append("Baseline dependency/build/test report is missing or not BASELINE_GREEN")
    for cmd in ["npm ci", "npm run repo:all", "npm run repo:no-paid-products", "npm run compile", "npm test", "npm run test:all", "npm run static-check", "npm run readiness:v4.3", "npm run assert:public-status", "npm run evidence:docket:template"]:
        if baseline.get("commands", {}).get(cmd) not in {"PASS", "PASS_WITH_AUDIT_WARNINGS", "PASS_EXPECTED_NOT_AUTHORIZED", "PASS_EXPECTED_NOT_READY"}:
            blockers.append(f"Baseline command not recorded passing: {cmd}")

    latest = ROOT/"audit/reports/latest.txt"
    report_dir = ROOT/latest.read_text().strip() if latest.exists() else None
    summary_path = report_dir/"audit-summary.json" if report_dir else ROOT/"audit/reports/missing/audit-summary.json"
    summary = read_json(summary_path)
    clearance = report_dir/"toolchain-clearance-report.md" if report_dir else ROOT/"audit/reports/missing/toolchain-clearance-report.md"
    evidence["automatedSecurityToolchain"] = {"summary": rel(summary_path) if summary_path.exists() else None, "clearanceReport": rel(clearance) if clearance.exists() else None, "sha256": sha256_file(clearance), "decision": summary.get("decision")}
    if not summary: blockers.append("Automated security/toolchain summary is missing")
    if summary.get("critical_high_unresolved", 0): blockers.append("Unresolved critical/high security findings remain")
    if summary.get("medium_unaccepted", 0): blockers.append("Unaccepted medium security findings remain")
    for tool in summary.get("tools", []):
        if tool.get("blocks_technical_mainnet_readiness") or tool.get("blocks_mainnet"):
            blockers.append(f"{tool.get('tool')} is pending/environment-blocked or not internally accepted")
    if not has_text(ROOT/"security/INTERNAL_SECURITY_REVIEW.md", "INTERNAL_SECURITY_REVIEW: PASSED"):
        blockers.append("Internal security review is missing or not PASSED")

    docket = ROOT/"evidence/sepolia/EVIDENCE_DOCKET.json"
    legacy_docket = ROOT/"evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json"
    docket_path = docket if docket.exists() else legacy_docket
    docket_data = read_json(docket_path)
    evidence["sepoliaEvidenceDocket"] = {"path": rel(docket_path) if docket_path.exists() else None, "sha256": sha256_file(docket_path), "status": docket_data.get("status")}
    if not docket_path.exists(): blockers.append("Public Ethereum Sepolia Evidence Docket is missing")
    if docket_data.get("status") != "COMPLETED_PUBLIC_SEPOLIA": blockers.append("Public Ethereum Sepolia replay is not completed with public receipts")
    if not has_text(ROOT/"docs/ETHEREUM_SEPOLIA_REHEARSAL_INDEPENDENT_RPC_VERIFICATION.md", "INDEPENDENT_RPC_VERIFICATION: PASSED"):
        blockers.append("Public Sepolia independent RPC receipt verification is missing or not PASSED")

    agi_json = read_json(ROOT/"qa/AGIALPHA_TOKEN_VERIFICATION.json")
    evidence["agialphaTokenVerification"] = {"path": "qa/AGIALPHA_TOKEN_VERIFICATION.json", "sha256": sha256_file(ROOT/"qa/AGIALPHA_TOKEN_VERIFICATION.json"), "status": agi_json.get("status")}
    if agi_json.get("status") != "PASSED": blockers.append("AGIALPHA Ethereum Mainnet token verification is missing or not PASSED")

    preflight_json = read_json(ROOT/"qa/ETHEREUM_MAINNET_PREFLIGHT.json")
    evidence["mainnetPreflight"] = {"path": "qa/ETHEREUM_MAINNET_PREFLIGHT.json", "sha256": sha256_file(ROOT/"qa/ETHEREUM_MAINNET_PREFLIGHT.json"), "status": preflight_json.get("status")}
    if preflight_json.get("status") != "PASSED_READ_ONLY": blockers.append("Ethereum Mainnet read-only preflight is missing or not PASSED_READ_ONLY")

    fork_json = read_json(ROOT/"qa/ETHEREUM_MAINNET_FORK_SIMULATION.json")
    evidence["mainnetForkSimulation"] = {"path": "qa/ETHEREUM_MAINNET_FORK_SIMULATION.json", "sha256": sha256_file(ROOT/"qa/ETHEREUM_MAINNET_FORK_SIMULATION.json"), "status": fork_json.get("status")}
    if fork_json.get("status") != "PASSED": blockers.append("Ethereum Mainnet fork simulation is missing or not PASSED")

    dep_report = ROOT/"docs/DEPENDABOT_TRIAGE_REPORT.md"
    evidence["dependencyTriage"] = {"path": "docs/DEPENDABOT_TRIAGE_REPORT.md", "sha256": sha256_file(dep_report)}
    if not dep_report.exists(): blockers.append("Dependabot/dependency triage report is missing")

    bp = read_json(ROOT/"qa/BRANCH_PROTECTION_STATUS.json")
    evidence["branchProtection"] = {"path": "qa/BRANCH_PROTECTION_STATUS.json", "sha256": sha256_file(ROOT/"qa/BRANCH_PROTECTION_STATUS.json"), "status": bp.get("status")}
    founder_risk = has_text(ROOT/"docs/BRANCH_PROTECTION_REQUIRED_FOR_AUTHORIZATION.md", "FOUNDER_BRANCH_PROTECTION_RISK_ACCEPTANCE: RECORDED")
    if bp.get("status") != "ENABLED" and not founder_risk:
        blockers.append("Main branch protection is not enabled and no explicit founder risk acceptance is recorded")

    status = "NO" if blockers else "YES"
    generated = now()
    decision = {
        "status": status,
        "TECHNICALLY_MAINNET_READY": status,
        "commit": git_commit(),
        "chain": "ethereum",
        "chainId": 1,
        "agialphaToken": AGIALPHA,
        "evidence": evidence,
        "blockers": blockers,
        "generatedAt": generated,
        "generatedBy": "scripts/mainnet-readiness-check.py",
        "deploymentCommandIfReady": "npm run deploy:ethereum-mainnet:gated" if status == "YES" else None,
        "mainnetDeploymentExecuted": False,
    }
    out_json = ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.json"
    out_md = ROOT/"docs/MAINNET_TECHNICAL_READINESS_DECISION.md"
    out_json.write_text(json.dumps(decision, indent=2)+"\n")
    md = ["# Mainnet Technical Readiness Decision", "", f"Generated: {generated}", "", f"TECHNICALLY_MAINNET_READY: **{status}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- None."]
    md += ["", "## Evidence", f"- Decision JSON: `{rel(out_json)}`", f"- Required AGIALPHA token: `{AGIALPHA}`", "- Not externally audited; readiness uses automated/internal security evidence."]
    out_md.write_text("\n".join(md)+"\n")
    print(json.dumps(decision, indent=2))

if __name__ == "__main__": main()
