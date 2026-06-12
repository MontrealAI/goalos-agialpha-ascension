#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
cert=json.loads((ROOT/'qa/mainnet-authorization-certificate.json').read_text())
ready=cert['technicallyMainnetReady']; deploy=cert['mainnetDeploymentAuthorized']; eth=cert['ethereumMainnetAuthorized']; deployed=cert['mainnetDeployed']
common=f"""GoalOS AGIALPHA Ascension v4.4 mainnet authorization candidate.

Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Public Sepolia: recommended but not required for public repository authorization.
Not externally audited.
Ethereum Mainnet technical readiness: {ready}.
Ethereum Mainnet deployment authorization: {deploy}.
Ethereum Mainnet authorization: {eth}.
Ethereum Mainnet deployed: {deployed}.

This means the repository package is authorized for manual gated Ethereum Mainnet deployment when the certificate says YES. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.

It does not claim external audit, legal approval, tax review, guaranteed security, guaranteed non-security, investment, yield, revenue share, price target, or production deployment.
"""
readme=f"# GoalOS AGIALPHA Ascension\n\n{common}\n\n## Final manual deployment command\n\n```bash\nnpm run deploy:ethereum-mainnet:gated\n```\n\nThe command is local/manual only and is blocked in GitHub Actions/CI. The AGIALPHA token on Ethereum Mainnet remains `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`; this repository does not deploy or mint a new AGIALPHA token on Ethereum Mainnet.\n"
(ROOT/'README.md').write_text(readme)
(ROOT/'docs/CURRENT_STATUS.md').write_text('# Current Status\n\n'+common)
(ROOT/'docs/START_HERE_MAINNET.md').write_text('# Start Here: Mainnet\n\n'+common+'\n1. Run `npm run mainnet:local-checks`.\n2. Run `npm run mainnet:security`.\n3. Run `npm run mainnet:local-rehearsal`.\n4. Run `npm run mainnet:certificate && npm run mainnet:certificate:validate`.\n5. If authorized, run `npm run deploy:ethereum-mainnet:gated` locally only with runtime RPC/key.\n')
for name,label,val in [
 ('MAINNET_TECHNICAL_READINESS_DECISION','TECHNICALLY_MAINNET_READY',ready),
 ('MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION','MAINNET_DEPLOYMENT_AUTHORIZED',deploy),
 ('ETHEREUM_MAINNET_AUTHORIZATION_DECISION','ETHEREUM_MAINNET_AUTHORIZED',eth)]:
    (ROOT/f'docs/{name}.md').write_text(f'# {name.replace("_"," ").title()}\n\n{label}: **{val}**\n\nMAINNET_DEPLOYED: **{deployed}**\n\nSource of truth: `qa/mainnet-authorization-certificate.json`. No Ethereum Mainnet deployment occurred.\n')
print('Generated README and public status docs from certificate.')
