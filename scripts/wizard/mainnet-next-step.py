#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
def j(path):
    try: return json.loads((ROOT/path).read_text())
    except Exception: return {}
eth=j("docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json")
tech=j("docs/MAINNET_TECHNICAL_READINESS_DECISION.json")
if eth.get("status")=="YES" and eth.get("ETHEREUM_MAINNET_AUTHORIZED")=="YES":
    print("Next action: run npm run deploy:ethereum-mainnet:gated:local from a private local operator workstation only.")
elif tech.get("status")=="YES":
    print("Next action: complete founder/address ceremony and deployment authorization redacted evidence, then run npm run mainnet:final-check.")
else:
    print("Next action: private operator runs npm run mainnet:prepare-private, npm run mainnet:local-checks, npm run mainnet:security, npm run mainnet:local-rehearsal, private Sepolia rehearsal, private mainnet preflight, then npm run mainnet:private-authorize.")
