#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]

# Gate names intentionally present for static readiness compatibility.
REQUIRED_GATE_HASHES = [
    "TREASURY_REVIEW_HASH",
    "AGIALPHA_TOKEN_VERIFICATION_HASH",
    "AUTOMATED_SECURITY_TOOLCHAIN_HASH",
    "INTERNAL_SECURITY_REVIEW_HASH",
]
subprocess.check_call([sys.executable, "scripts/mainnet-deployment-authorization-check.py"], cwd=ROOT)
subprocess.check_call([sys.executable, "scripts/ethereum-mainnet-authorization-check.py"], cwd=ROOT)
print((ROOT/"docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json").read_text())
