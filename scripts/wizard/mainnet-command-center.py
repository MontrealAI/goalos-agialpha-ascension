#!/usr/bin/env python3
from __future__ import annotations
MENU=[
("Check public repo status","npm run mainnet:status"),
("Prepare private operator files","npm run mainnet:prepare-private"),
("Run local public checks","npm run mainnet:local-checks"),
("Run automated/internal security toolchain","npm run mainnet:security"),
("Run local deterministic rehearsal","npm run mainnet:local-rehearsal"),
("Run private Sepolia rehearsal","python scripts/private/run-private-sepolia-rehearsal.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json"),
("Run private Ethereum Mainnet preflight","python scripts/private/run-private-mainnet-preflight.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json"),
("Generate redacted public evidence","npm run mainnet:private-authorize"),
("Compute technical readiness","npm run mainnet:readiness-check"),
("Compute deployment authorization","npm run mainnet:deployment-authorization-check"),
("Compute Ethereum Mainnet authorization","npm run mainnet:authorization-check"),
("Run final local gated deployment","npm run deploy:ethereum-mainnet:gated:local"),
("Generate post-deployment report","python scripts/generate-public-post-deployment-report.py"),
]
print("GoalOS AGIALPHA Ethereum Mainnet Command Center")
print("Private values must stay in .private/ only. Never paste secrets into GitHub or CI.")
for i,(label,cmd) in enumerate(MENU,1): print(f"{i}. {label}\n   {cmd}")
