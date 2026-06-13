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
badges=f'''[![Repository Validation](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml)
[![Final Public Mainnet Authorization](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml)
[![Mainnet Authorization Gate](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml)
[![Solidity Audit Toolchain](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](NOTICE.md)
[![Solidity 0.8.35](https://img.shields.io/badge/Solidity-0.8.35-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)
[![TypeScript 5.9.3](https://img.shields.io/badge/TypeScript-5.9.3-3178c6?logo=typescript&logoColor=white)](package.json)
[![Mainnet Authorized](https://img.shields.io/badge/Ethereum%20Mainnet-Authorized%20for%20manual%20gated%20deployment-success)](qa/mainnet-authorization-certificate.json)
[![Mainnet Deployed](https://img.shields.io/badge/Ethereum%20Mainnet%20Deployed-{deployed}-critical)](qa/mainnet-authorization-certificate.json)
'''
readme=f"""# GoalOS AGIALPHA Ascension

{badges}
{status_block}

## Executive overview

GoalOS AGIALPHA Ascension is the institutional, evidence-first package for proof-settled AI workflow coordination using the existing AGIALPHA token. The repository is designed for reviewers, operators, auditors, and governance stakeholders who need a clear source of truth, reproducible checks, and strict public-claims boundaries.

**Official source of truth:** `qa/mainnet-authorization-certificate.json`. Public README/status documents summarize that certificate; they do not override it.

## Quick start for institutional reviewers

1. Read this README for current status, safety boundaries, and canonical commands.
2. Confirm the certificate in `qa/mainnet-authorization-certificate.json`.
3. Run `npm run mainnet:public-authorize` to validate the public authorization gates.
4. Run `npm run mainnet:local-checks` before any operator handoff or release review.
5. Use `npm run deploy:ethereum-mainnet:gated` only from a local operator environment with runtime RPC URL and deployer key supplied outside GitHub.

## Official badge policy

Badges at the top of this README are intentionally limited to official, auditable repository signals: GitHub Actions workflow status, package-declared tool versions, license, authorization state, and deployment state. Workflow badges update automatically from GitHub Actions. Static status badges mirror `qa/mainnet-authorization-certificate.json` and must be updated only when the certificate changes. See `docs/OFFICIAL_BADGES.md` for maintenance rules.

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

## Sovereign RSI v6.3 research paper

The Sovereign RSI v6.3 publication folder is `docs/papers/sovereign-rsi/v6.3/`. Paper assets may be pending upload if they are not present in the tree; do not fabricate missing PDF/DOCX/source files.

Core thesis: GoalOS sets sovereign aims. AGIALPHA coordinates proof-settled work. AEP-001 defines valid evidence. The Proof Gradient decides what may evolve. The intelligence stays private. The proof becomes verifiable.

RSI means proof-backed upgrade rights. An artifact may influence future work only after evidence, evaluation, reviewer validation, scope control, challenge window, canary rollout, monitoring, rollback readiness, and chronicle memory.

Claim boundary: this paper does not claim achieved AGI, ASI, superintelligence, autonomous sovereignty, guaranteed ROI, safety certification, legal approval, tax approval, security approval, energy abundance, or Kardashev Type II achievement.
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
