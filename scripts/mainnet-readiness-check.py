from __future__ import annotations
import datetime
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"


def sha256_file(path: pathlib.Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def read_json(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def main() -> None:
    blockers: list[str] = []
    latest = ROOT / "audit/reports/latest.txt"
    report_dir = ROOT / latest.read_text().strip() if latest.exists() else None
    summary_path = report_dir / "audit-summary.json" if report_dir else ROOT / "audit/reports/missing/audit-summary.json"
    summary = read_json(summary_path)
    if not summary:
        blockers.append("Automated security/toolchain summary is missing")
    else:
        if summary.get("critical_high_unresolved", 0):
            blockers.append("Unresolved critical/high toolchain findings remain")
        if summary.get("medium_unaccepted", 0):
            blockers.append("Unaccepted medium findings remain")
        for tool in summary.get("tools", []):
            if tool.get("blocks_technical_mainnet_readiness") or tool.get("blocks_mainnet"):
                blockers.append(f"{tool.get('tool')} is pending/environment-blocked or not internally accepted")
    manifest = ROOT / "deployments/ethereum-sepolia.agialpha.latest.json"
    docket = ROOT / "evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json"
    if not manifest.exists():
        blockers.append("Ethereum Sepolia deployment manifest is missing")
    if not docket.exists():
        blockers.append("Sepolia Evidence Docket is missing")
    else:
        docket_data = read_json(docket)
        if "PUBLIC_SEPOLIA_PENDING" in json.dumps(docket_data):
            blockers.append("Public Ethereum Sepolia replay remains pending; only local chainId 11155111 rehearsal evidence is present")
    agi_report = ROOT / "docs/AGIALPHA_TOKEN_VERIFICATION_REPORT.md"
    if not agi_report.exists() or "PENDING_RPC" in agi_report.read_text(errors="ignore"):
        blockers.append("AGIALPHA token verification requires Ethereum mainnet RPC evidence")
    for path in [ROOT/"qa/BASELINE_MAIN_STATUS.json", ROOT/"docs/DEPENDABOT_TRIAGE_REPORT.md", ROOT/"docs/TREASURY_FOUNDER_ADDRESS_CEREMONY.md"]:
        if not path.exists():
            blockers.append(f"Required readiness evidence missing: {path.relative_to(ROOT)}")
    if (ROOT/"docs/TREASURY_FOUNDER_ADDRESS_CEREMONY.md").exists() and "not complete" in (ROOT/"docs/TREASURY_FOUNDER_ADDRESS_CEREMONY.md").read_text(errors="ignore").lower():
        blockers.append("Treasury/founder address ceremony is not complete")

    ready = "NO" if blockers else "YES"
    generated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    decision = {
        "generated_at": generated,
        "TECHNICALLY_MAINNET_READY": ready,
        "blockers": blockers,
        "audit_report": str(summary_path.relative_to(ROOT)) if summary_path.exists() else None,
        "toolchain_report_hash": sha256_file(report_dir / "toolchain-clearance-report.md") if report_dir and (report_dir/"toolchain-clearance-report.md").exists() else None,
        "sepolia_manifest": str(manifest.relative_to(ROOT)) if manifest.exists() else None,
        "sepolia_manifest_hash": sha256_file(manifest),
        "sepolia_evidence_docket": str(docket.relative_to(ROOT)) if docket.exists() else None,
        "sepolia_evidence_docket_hash": sha256_file(docket),
        "agialpha_mainnet_token_required": AGIALPHA,
        "deployment_command_if_ready": "hardhat run scripts/deploy-ethereum-mainnet-gated.ts --network mainnet" if ready == "YES" else None,
        "final_founder_approval_required": True,
    }
    out_json = ROOT / "docs/MAINNET_TECHNICAL_READINESS_DECISION.json"
    out_md = ROOT / "docs/MAINNET_TECHNICAL_READINESS_DECISION.md"
    out_json.write_text(json.dumps(decision, indent=2)+"\n")
    md = ["# Mainnet Technical Readiness Decision", "", f"Generated: {generated}", "", f"TECHNICALLY_MAINNET_READY: **{ready}**", "", "## Blockers"]
    md += [f"- {b}" for b in blockers] or ["- No technical blockers recorded. Founder deployment authorization is still separate and required."]
    md += ["", "## Evidence", f"- Sepolia manifest: `{decision['sepolia_manifest']}`", f"- Sepolia Evidence Docket: `{decision['sepolia_evidence_docket']}`", f"- Required AGIALPHA token: `{AGIALPHA}`", "- Not externally audited; readiness uses automated security/toolchain and internal review gates."]
    out_md.write_text("\n".join(md)+"\n")
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
