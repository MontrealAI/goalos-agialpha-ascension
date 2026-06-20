#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "pr-readiness"

def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout

def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def audit_counts() -> dict:
    counts = {"critical": 0, "high": 0, "criticalHighUnresolved": 0, "source": "audit/AUDIT_FINDINGS_REGISTER.csv"}
    path = ROOT / "audit" / "AUDIT_FINDINGS_REGISTER.csv"
    if not path.exists():
        counts["missing"] = True
        counts["criticalHighUnresolved"] = 1
        return counts
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            sev = (row.get("Severity") or row.get("severity") or "").strip().lower()
            status = (row.get("Status") or row.get("status") or "").strip().lower()
            if sev in {"critical", "high"}:
                counts[sev] += 1
                if status not in {"closed", "resolved", "false_positive", "false positive", "accepted"}:
                    counts["criticalHighUnresolved"] += 1
    return counts

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = git(["rev-parse", "HEAD"])
    branch = git(["branch", "--show-current"])
    tree = git(["status", "--short"])
    commands = []
    # Generate fail-closed release-mode artifacts without requiring protected inputs.
    rc, out = run([sys.executable, "scripts/mainnet_operational_readiness.py"])
    commands.append({"command": "python scripts/mainnet_operational_readiness.py", "exitCode": rc, "status": "PASS" if rc == 0 else "FAIL", "outputTail": out[-4000:]})
    dossier = json.loads((ROOT / "qa" / "mainnet-production-readiness-dossier.json").read_text())
    audit = audit_counts()
    status = "PR_CHECKS_PASS" if rc == 0 and audit["criticalHighUnresolved"] == 0 else "PR_CHECKS_FAIL"
    report = {
        "schemaVersion": "1.0",
        "mode": "PR_MODE",
        "status": status,
        "releaseEvidenceStatus": "RELEASE_EVIDENCE_NOT_EXECUTED",
        "claimBoundary": "No Gate 1-5 PASS is emitted in PR_MODE; RELEASE_MODE evidence remains separate under qa/mainnet-readiness/ and fails closed until protected fork/Owner inputs execute.",
        "baselineSha": baseline,
        "finalShaAtGeneration": baseline,
        "branch": branch,
        "generatedAtUnix": int(time.time()),
        "sourceHash": dossier.get("sourceTreeHash"),
        "packageLockHash": sha(ROOT / "package-lock.json"),
        "compilerSettingsHash": sha(ROOT / "hardhat.config.ts"),
        "auditFindingCount": audit,
        "releaseReadinessStatus": dossier.get("status"),
        "releaseOnlyEvidenceRemaining": [
            "protected production Owner config commitment",
            "recent Ethereum Mainnet fork RPC rehearsal",
            "million-action invariant run with >=32 recorded deterministic seeds",
            "secondary fuzzer, symbolic/bounded, independent build, and critical mutation release evidence",
            "exact bytecode/configuration/fork certificate validation"
        ],
        "commands": commands,
        "workingTreeAtStart": tree,
        "mainnetBroadcastOccurred": False,
        "MAINNET_DEPLOYED": "NO",
        "MAINNET_VERIFIED": "NO",
        "LIVE_OWNER_HANDOFF_COMPLETE": "NO",
        "LIVE_CANARY_COMPLETE": "NO"
    }
    (OUT / "stage-a-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PR_CHECKS_PASS" else 2
if __name__ == "__main__":
    raise SystemExit(main())
