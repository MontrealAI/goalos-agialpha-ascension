#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
cert=json.loads((ROOT/'qa/mainnet-authorization-certificate.json').read_text())
tech=cert['technicallyMainnetReady']; dep=cert['mainnetDeploymentAuthorized']; eth=cert['ethereumMainnetAuthorized']; deployed=cert['mainnetDeployed']
authorization_meaning = 'This means the repository package is authorized for manual gated Ethereum Mainnet deployment. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.' if (tech == 'YES' and dep == 'YES' and eth == 'YES') else 'This means the repository package is not currently authorized for manual gated Ethereum Mainnet deployment. Resolve the certificate blockers, regenerate the certificate, and rerun the public checks before any mainnet deployment attempt. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.'
status_block=f"""GoalOS AGIALPHA Ascension v4.4.0 mainnet authorization candidate.

Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Ethereum Mainnet technical readiness: {tech}.
Ethereum Mainnet deployment authorization: {dep}.
Ethereum Mainnet authorization: {eth}.
Ethereum Mainnet deployed: {deployed}.

{authorization_meaning}

It does not claim external audit completion, legal approval, tax review, guaranteed security, guaranteed token classification, investment return, yield, price target, revenue share, or production deployment.

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.
"""
readme=f"""# GoalOS AGIALPHA Ascension

{status_block}

## Core doctrine

- GoalOS decides what may evolve.
- AGIALPHA coordinates proof-settled work.
- Evidence Dockets make claims auditable.
- Do not put intelligence on-chain; put proof of intelligence on-chain.
- No proof, no evolution. No eval, no propagation. No rollback, no release.

## Ethereum Mainnet authorization

The source of truth is `qa/mainnet-authorization-certificate.json`. README/status documents are generated from that certificate; manual edits cannot create YES.

- TECHNICALLY_MAINNET_READY: **{tech}**
- MAINNET_DEPLOYMENT_AUTHORIZED: **{dep}**
- ETHEREUM_MAINNET_AUTHORIZED: **{eth}**
- MAINNET_DEPLOYED: **{deployed}**
- Canonical AGIALPHA token: `{cert['agialphaToken']}`
- Chain: Ethereum Mainnet (`chainId=1`)
- Final manual command: `npm run deploy:ethereum-mainnet:gated`

## Safety boundary

CI cannot deploy Ethereum Mainnet. Runtime RPC URL, deployer key, and runtime addresses are local broadcast inputs only and are not stored in GitHub. MockAGIALPHA is local/Sepolia-only and is forbidden on Ethereum Mainnet. No new AGIALPHA token is deployed on Ethereum Mainnet.

## Research paper

**GoalOS-native alpha-AGI Ascension using AGIALPHA — Sovereign RSI Edition v6.3**

This paper defines the GoalOS-native reimplementation of alpha-AGI Ascension using AGIALPHA as a sovereign RSI architecture for evidence-governed intelligence organizations.

- [Read the paper](docs/papers/sovereign-rsi/v6.3/GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.md)
- [Download the PDF](docs/papers/sovereign-rsi/v6.3/GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.pdf)
- [Download the editable DOCX](docs/papers/sovereign-rsi/v6.3/GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.docx)
- [View the TeX source](docs/papers/sovereign-rsi/v6.3/GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.tex)

Publication-safe boundary: this is an architecture, protocol, benchmark, and implementation-doctrine paper. It does not claim achieved AGI, ASI, superintelligence, empirical SOTA, guaranteed economic return, legal approval, tax approval, security approval, energy abundance, or achieved Kardashev-scale capability.
"""

# Decision JSON/Markdown documents are generated from the same certificate so docs:status is sufficient before assert/checker steps.
decisions = [
  ('docs/MAINNET_TECHNICAL_READINESS_DECISION', 'TECHNICALLY_MAINNET_READY', 'technicallyMainnetReady', tech, 'Ethereum Mainnet technical readiness'),
  ('docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION', 'MAINNET_DEPLOYMENT_AUTHORIZED', 'mainnetDeploymentAuthorized', dep, 'Ethereum Mainnet deployment authorization'),
  ('docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION', 'ETHEREUM_MAINNET_AUTHORIZED', 'ethereumMainnetAuthorized', eth, 'Ethereum Mainnet authorization'),
]
for base, upper, camel, value, label in decisions:
    data = {'status': value, upper: value, camel: value, 'commit': cert.get('commit'), 'chain': 'ethereum', 'chainId': 1, 'agialphaToken': cert.get('agialphaToken'), 'mainnetDeployed': deployed, 'MAINNET_DEPLOYED': deployed, 'evidence': cert.get('evidence', {}), 'blockers': cert.get('blockers', []), 'generatedAt': cert.get('generatedAt'), 'generatedBy': 'scripts/generate-public-status-docs.py'}
    if upper == 'ETHEREUM_MAINNET_AUTHORIZED': data['finalManualDeploymentCommand'] = 'npm run deploy:ethereum-mainnet:gated' if value == 'YES' else None
    (ROOT/f'{base}.json').write_text(json.dumps(data, indent=2)+'\n')
    (ROOT/f'{base}.md').write_text(f'# {label.title()} Decision\n\n{label}: **{value}**.\n\n{upper}: **{value}**\n\nMAINNET_DEPLOYED: **{deployed}**\n\nNot externally audited. External audit is not planned and is not an active mainnet gate. Automated/internal security-toolchain clearance is the active security gate.\n')
(ROOT/'README.md').write_text(readme)
(ROOT/'docs/CURRENT_STATUS.md').write_text('# Current Status\n\n'+status_block+f"\n## Certificate source\n\n`qa/mainnet-authorization-certificate.json` generated by `{cert['generatedBy']}` at `{cert['generatedAt']}`.\n")
(ROOT/'docs/MAINNET_AUTHORIZATION_CERTIFICATE.md').write_text(f"""# Mainnet Authorization Certificate

Generated from `qa/mainnet-authorization-certificate.json`.

- TECHNICALLY_MAINNET_READY: **{tech}**
- MAINNET_DEPLOYMENT_AUTHORIZED: **{dep}**
- ETHEREUM_MAINNET_AUTHORIZED: **{eth}**
- MAINNET_DEPLOYED: **{deployed}**
- Private operator authorization package required: **{cert['privateOperatorAuthorizationPackageRequired']}**
- Runtime secrets stored in GitHub: **{cert['runtimeSecretsStoredInGitHub']}**
- CI can deploy mainnet: **{cert['ciCanDeployMainnet']}**

This certificate authorizes only manual, local, gated Ethereum Mainnet deployment. It is not an external audit, legal approval, tax review, proof of deployment, or guarantee of security/token classification.

## Next action

{cert['nextAction']}
""")
(ROOT/'docs/START_HERE_MAINNET.md').write_text(f"""# Start Here: Ethereum Mainnet

{status_block}

## Command center

1. Check public repo status: `npm run mainnet:status`
2. Run local public checks: `npm run mainnet:local-checks`
3. Run automated/internal security toolchain: `npm run mainnet:security`
4. Run local deterministic rehearsal: `npm run mainnet:local-rehearsal`
5. Run public AGIALPHA token verification: `npm run verify:agialpha-token:public`
6. Generate Mainnet Authorization Certificate: `npm run mainnet:certificate`
7. Compute technical readiness: `npm run mainnet:readiness-check`
8. Compute deployment authorization: `npm run mainnet:deployment-authorization-check`
9. Compute Ethereum Mainnet authorization: `npm run mainnet:authorization-check`
10. Show final manual deployment command: `npm run mainnet:next`
11. Run final local gated deployment: `npm run deploy:ethereum-mainnet:gated`
12. Generate post-deployment report after real transaction evidence exists.
""")
print('Generated public status docs from qa/mainnet-authorization-certificate.json')
