#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASE_A_REPORT = ROOT / "qa" / "pr-readiness" / "phase-a-report.json"
FORK_REPORT = ROOT / "qa" / "mainnet-readiness" / "fork-rehearsal.json"


def run(cmd: list[str]) -> int:
    return subprocess.call(cmd, cwd=ROOT)


def fail_closed(reason: str, code: int = 2) -> int:
    FORK_REPORT.parent.mkdir(parents=True, exist_ok=True)
    FORK_REPORT.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0",
                "status": "BLOCKED",
                "reason": reason,
                "phaseARequiredBeforeProtectedInputs": True,
                "mainnetBroadcastOccurred": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(reason)
    return code


def phase_a_ready() -> bool:
    if not PHASE_A_REPORT.exists():
        return False
    try:
        report = json.loads(PHASE_A_REPORT.read_text())
    except json.JSONDecodeError:
        return False
    return (
        report.get("status") == "PHASE_A_PASS"
        and report.get("releaseStatus") == "RELEASE_EVIDENCE_NOT_EXECUTED"
        and report.get("mainnetBroadcastOccurred") is False
    )


def main() -> int:
    # Phase A must be complete before this RELEASE_MODE entry point is allowed
    # to read or validate protected fork/owner inputs.
    if not phase_a_ready():
        return fail_closed(
            "PHASE_A_REPORT_MISSING_OR_NOT_PASSING: run npm run codex:phase-a before protected release input validation."
        )

    rc = run([sys.executable, "scripts/mainnet_release_inputs.py"])
    if rc != 0:
        return rc

    # The readiness evaluator remains fail-closed until complete, real fork
    # evidence is generated and bound to the release identity. This wrapper does
    # not broadcast and does not convert local simulation evidence into PASS.
    return run([sys.executable, "scripts/mainnet_operational_readiness.py", "--validate"])


if __name__ == "__main__":
    raise SystemExit(main())
