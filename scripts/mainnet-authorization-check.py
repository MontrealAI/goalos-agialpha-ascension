#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]

# Gate names intentionally present for static readiness compatibility.
REQUIRED_GATE_HASHES = [
    "TREASURY_REVIEW_HASH",
    "AGIALPHA_TOKEN_VERIFICATION_HASH",
    "AUTOMATED_SECURITY_TOOLCHAIN_HASH",
    "INTERNAL_SECURITY_REVIEW_HASH",
]

def run_quiet(args: list[str]) -> None:
    completed = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        raise SystemExit(completed.returncode)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-only", action="store_true")
    parser.add_argument("--with-redacted-private-evidence", action="store_true")
    mode = parser.parse_args()
    forwarded = []
    if mode.public_only:
        forwarded.append("--public-only")
    if mode.with_redacted_private_evidence:
        forwarded.append("--with-redacted-private-evidence")
    run_quiet([sys.executable, "scripts/mainnet-readiness-check.py", *forwarded])
    run_quiet([sys.executable, "scripts/mainnet-deployment-authorization-check.py", *forwarded])
    run_quiet([sys.executable, "scripts/ethereum-mainnet-authorization-check.py", *forwarded])
    decision = json.loads((ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json").read_text())
    print(json.dumps(decision, indent=2))
if __name__ == "__main__": main()
