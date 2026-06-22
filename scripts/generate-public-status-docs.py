#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args=parser.parse_args()
ACTIVE_OUTPUTS=[
 'README.md','START_HERE.md','docs/CURRENT_STATUS.md','docs/MAINNET_AUTHORIZATION_CERTIFICATE.md','docs/START_HERE_MAINNET.md',
 'docs/MAINNET_TECHNICAL_READINESS_DECISION.json','docs/MAINNET_TECHNICAL_READINESS_DECISION.md',
 'docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json','docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md',
 'docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json','docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md',
 'docs/MAINNET_AUTHORIZATION_DECISION.json','docs/MAINNET_AUTHORIZATION_DECISION.md']
before={rel:(ROOT/rel).read_text() if (ROOT/rel).exists() else None for rel in ACTIVE_OUTPUTS}
cert=json.loads((ROOT/'qa/mainnet-authorization-certificate.json').read_text())
def cert_value(*names, default='NO'):
    for name in names:
        if name in cert:
            return cert[name]
    return default
tech=cert_value('technicallyMainnetReady','TECHNICALLY_MAINNET_READY'); dep=cert_value('mainnetDeploymentAuthorized','MAINNET_DEPLOYMENT_AUTHORIZED'); eth=cert_value('ethereumMainnetAuthorized','ETHEREUM_MAINNET_AUTHORIZED'); deployed=cert_value('mainnetDeployed','MAINNET_DEPLOYED')
release_state_path = ROOT/'qa/mainnet-release-state.json'
if release_state_path.exists():
    try:
        release_state=json.loads(release_state_path.read_text())
        deployed=release_state.get('summary',{}).get('ETHEREUM_MAINNET_DEPLOYED', deployed)
        postdeployment_status=release_state.get('postdeployment',{}).get('status','NO')
    except Exception:
        postdeployment_status='NO'
else:
    postdeployment_status='NO'
authorization_meaning = 'The historical Stage-A predeployment certificate was not used for this deployment path. The repository now records a direct operator Mainnet deployment and postdeployment evidence separately from Stage-C production activation.' if deployed == 'YES' else ('This means the repository package is authorized for manual gated Ethereum Mainnet deployment. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.' if (tech == 'YES' and dep == 'YES' and eth == 'YES') else 'This means the repository package is not currently authorized for manual gated Ethereum Mainnet deployment. Resolve the certificate blockers, regenerate the certificate, and rerun the public checks before any mainnet deployment attempt. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.')
status_label=f"""GoalOS AGIALPHA Ascension v4.4.0 Mainnet release-state summary.
Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Historical predeployment authorization used: NO — DIRECT_OPERATOR_NO_CERTIFICATE.
Ethereum Mainnet technical readiness: {tech}.
Ethereum Mainnet deployment authorization: {dep}.
Ethereum Mainnet authorization: {eth}.
Ethereum Mainnet deployed: {deployed}.
GoalOS contracts deployed: 48.
Operator verification evidence: 48/48.
Operator configuration postcheck: PASS.
Independent dual-RPC revalidation: PENDING.
Stage B certificate: PENDING.
Canonical external AGIALPHA: confirmed.
Mainnet configured: YES.
Permanent authority: Wallet B / Ledger genesis authority assignment.
No ownership acceptance transaction is required for this deployed instance.
Wallet A managed roles: 0.
Phase-B grants: 14/14.
Production activated: NO.

Three-stage Mainnet release status:

| Stage | Status |
| --- | --- |
| Predeployment authorization | {eth} |
| Ethereum Mainnet deployed | {deployed} |
| Postdeployment verification | {postdeployment_status} |
| Production activation effective | NO |

A pre-broadcast state with predeployment authorization YES and Ethereum Mainnet deployed NO is a GO to deploy, not a contradiction. Stage B evaluates chain-1 receipts, bytecode, verification, and ownership/role readback only after human broadcast. Stage C separately governs bounded live canary, monitoring, reconciliation, Ledger activation, and production reliance."""
certificate_meaning = 'This certificate authorizes only manual, local, gated Ethereum Mainnet deployment.' if (tech == 'YES' and dep == 'YES' and eth == 'YES') else 'This certificate does not authorize Ethereum Mainnet deployment while readiness or authorization is NO.'
status_block=f"""{status_label}

{authorization_meaning}

Runtime RPC URL and deployer key outside GitHub remain mandatory for any local-only operator action; CI must not receive signing keys.

It does not claim external audit completion, legal approval, tax review, guaranteed security, guaranteed token classification, investment return, yield, price target, revenue share, or production deployment.

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.
"""
badges=f'''[![Repository Validation](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/repository-validation.yml)
[![Final Public Mainnet Authorization](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/final-public-mainnet-authorization.yml)
[![Mainnet Authorization Gate](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/mainnet-authorization-gate.yml)
[![Solidity Audit Toolchain](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml/badge.svg)](https://github.com/MontrealAI/goalos-agialpha-ascension/actions/workflows/solidity-audit-toolchain.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)
[![TypeScript 5.9.3](https://img.shields.io/badge/TypeScript-5.9.3-3178c6?logo=typescript&logoColor=white)](package.json)
[![Operator Verification Evidence 48/48](https://img.shields.io/badge/Operator%20Verification%20Evidence-48%2F48-informational)](qa/mainnet-postdeploy/verification-evidence.json)
[![Mainnet Configured YES](https://img.shields.io/badge/Mainnet%20Configured-YES-success)](qa/mainnet-release-state.json)
[![Production Activation NO](https://img.shields.io/badge/Production%20Activation-NO-critical)](qa/mainnet-release-state.json)
[![Mainnet Deployed](https://img.shields.io/badge/Ethereum%20Mainnet%20Deployed-{deployed}-{'success' if deployed == 'YES' else 'critical'})](qa/mainnet-release-state.json)
'''
readme=f"""# GoalOS AGIALPHA Ascension

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)
[![Ethereum Mainnet Deployed YES](https://img.shields.io/badge/Ethereum%20Mainnet%20Deployed-{deployed}-{'success' if deployed == 'YES' else 'critical'})](qa/mainnet-release-state.json)
[![Operator Verification Evidence 48/48](https://img.shields.io/badge/Operator%20Verification%20Evidence-48%2F48-informational)](qa/mainnet-postdeploy/verification-evidence.json)
[![Mainnet Configured YES](https://img.shields.io/badge/Mainnet%20Configured-YES-success)](qa/mainnet-release-state.json)
[![Production Activation NO](https://img.shields.io/badge/Production%20Activation-NO-critical)](qa/mainnet-release-state.json)

## Mission statement

GoalOS AGIALPHA Ascension is an evidence-first Ethereum/Hardhat repository for proof-settled AI workflow coordination using the existing canonical AGIALPHA token. The repository is organized for reviewers, operators, developers, and auditors who need clear public status, reproducible checks, and bounded claims.

## Current Mainnet status

| Item | Current value |
| --- | --- |
| Ethereum Mainnet deployment | {deployed} |
| Mainnet configuration | YES |
| GoalOS contracts | 48 |
| Operator verification evidence | 48/48 GoalOS contracts; `verified_from_seed_requires_api_refresh` |
| Phase-B grants | 14/14 |
| Stage-B/live postdeployment check | BLOCKED until read-only live evidence passes |
| Permanent authority | Wallet B / Ledger |
| Wallet A managed roles | 0 |
| Production activation | NO |
| User-fund authorization | NO |
| External audit completion | NO |

Not externally audited.
Ethereum Mainnet technical readiness: {tech}.
Ethereum Mainnet deployment authorization: {dep}.
Ethereum Mainnet authorization: {eth}.
Ethereum Mainnet deployed: {deployed}.
Production activated: NO.

Lifecycle boundaries remain separate: deployment and configuration are recorded for the pre-release, while operator verification evidence remains qualified by seed/API-refresh status. Independent dual-RPC revalidation, live-RPC bytecode validation, any Stage-B certificate, production activation, user-fund authorization, live canary completion, and external audit completion must retain the status recorded in their evidence files and must not be promoted by prose.

## Published release

Published pre-release: [`v4.4.0-mainnet-2026-06-21`](https://github.com/MontrealAI/goalos-agialpha-ascension/releases/tag/v4.4.0-mainnet-2026-06-21). Full tag SHA resolved from Git: `51bacf4fe58e4eb425240e74eef7e8461832767f`.

Release type: Pre-release. Release date: 2026-06-22. Deployment date: 2026-06-21. Package version: 4.4.0.

## Canonical AGIALPHA

Canonical AGIALPHA on Ethereum Mainnet is `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. It is external to GoalOS: `external = true`, `deployedByGoalOS = false`, and `mintedByGoalOS = false`.

## Governance and authority

The canonical 2026-06-21 deployment used `DIRECT_OPERATOR_NO_CERTIFICATE`, genesis authority assignment, and postdeployment role configuration. Wallet A deployer is documented in `qa/mainnet-release-state.json`; Wallet B permanent Ledger authority is documented in `qa/mainnet-release-state.json`. Wallet A has zero managed roles. No ERC-173 acceptance transaction is required for this deployed instance.

Historical predeployment certificate: not used. Deployment path: `DIRECT_OPERATOR_NO_CERTIFICATE`.

## Audience navigation

- Executive/reviewer: [`docs/CURRENT_STATUS.md`](docs/CURRENT_STATUS.md), [`docs/ETHEREUM_MAINNET.md`](docs/ETHEREUM_MAINNET.md), [`docs/SECURITY_AND_LIMITATIONS.md`](docs/SECURITY_AND_LIMITATIONS.md), [`docs/MAINNET_LIVE_GATE_IMPACT.md`](docs/MAINNET_LIVE_GATE_IMPACT.md).
- Developer: [`docs/DEVELOPER_QUICKSTART_MAINNET.md`](docs/DEVELOPER_QUICKSTART_MAINNET.md), [`docs/CONTRACT_INTERACTION_REFERENCE.md`](docs/CONTRACT_INTERACTION_REFERENCE.md), [`docs/ETHEREUM_MAINNET_CONTRACTS.md`](docs/ETHEREUM_MAINNET_CONTRACTS.md).
- Operator: [`docs/OPERATIONS_RUNBOOK_MAINNET.md`](docs/OPERATIONS_RUNBOOK_MAINNET.md), [`docs/MONITORING_AND_ALERTING.md`](docs/MONITORING_AND_ALERTING.md), [`docs/INCIDENT_RESPONSE_MAINNET.md`](docs/INCIDENT_RESPONSE_MAINNET.md), [`docs/WALLET_A_DECOMMISSION_REPORT.md`](docs/WALLET_A_DECOMMISSION_REPORT.md), [`docs/PRODUCTION_ACTIVATION.md`](docs/PRODUCTION_ACTIVATION.md).
- Contributor: [`START_HERE.md`](START_HERE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/DOCUMENTATION_MAINTENANCE.md`](docs/DOCUMENTATION_MAINTENANCE.md).

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.

## Developer quick start

```bash
npm ci
npm run mainnet:contracts:check
npm run docs:mainnet:check
```

Use the generated registry in [`config/ethereum-mainnet.contracts.json`](config/ethereum-mainnet.contracts.json) or [`app/config/ethereum-mainnet.contracts.generated.ts`](app/config/ethereum-mainnet.contracts.generated.ts). Validate `chainId === 1`, load ABIs from repository artifacts, and use read-only calls until Stage C explicitly enables production writes.

## Read-only operator commands

```bash
npm run mainnet:contracts:check
npm run mainnet:postdeploy:status
npm run docs:all
```

These commands are for status, registry, documentation, and read-only evidence review. Do not redeploy the canonical topology. Canonical redeployment commands must fail closed and must never run from CI with signing material.

## Security/claim boundary

This repository does not claim production activation, user-fund authorization, live canary completion, external audit completion, legal or tax approval, token classification, guaranteed security, investment return, AGI/ASI, yield, revenue share, or price appreciation. Do not commit secrets, `.private/` data, raw operator logs, private constructor inputs, private keys, mnemonics, RPC URLs, API keys, Ledger secrets, browser profiles, caches, or coverage artifacts.

## Architecture overview

The configured Mainnet topology contains 49 registry entries: 48 GoalOS-created contracts and one external canonical AGIALPHA token. Public contract discovery is centralized in the generated registry and the canonical Mainnet hub rather than duplicated across unrelated documents.

## Documentation index

Start with [`docs/DOCUMENTATION_INDEX.md`](docs/DOCUMENTATION_INDEX.md). The source-of-truth hierarchy is: Mainnet receipts/readbacks; `deployments/ethereum-mainnet.agialpha.latest.json`; `qa/mainnet-postdeploy/verification-evidence.json`; `qa/mainnet-postdeploy/`; `qa/mainnet-release-state.json`; `release/mainnet-2026-06-21/`; generated public docs.

## Citation and license

Use [`CITATION.cff`](CITATION.cff) for citation metadata. This repository is licensed under the MIT License; see [`LICENSE`](LICENSE).
"""

# Decision JSON/Markdown documents are generated from the same certificate so docs:status is sufficient before assert/checker steps.
decisions = [
  ('docs/MAINNET_TECHNICAL_READINESS_DECISION', 'TECHNICALLY_MAINNET_READY', 'technicallyMainnetReady', tech, 'Ethereum Mainnet technical readiness'),
  ('docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION', 'MAINNET_DEPLOYMENT_AUTHORIZED', 'mainnetDeploymentAuthorized', dep, 'Ethereum Mainnet deployment authorization'),
  ('docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION', 'ETHEREUM_MAINNET_AUTHORIZED', 'ethereumMainnetAuthorized', eth, 'Ethereum Mainnet authorization'),
]
for base, upper, camel, value, label in decisions:
    data = {'status': value, upper: value, camel: value, 'commit': cert.get('commit'), 'chain': 'ethereum', 'chainId': 1, 'agialphaToken': cert.get('agialphaToken'), 'mainnetDeployed': deployed, 'MAINNET_DEPLOYED': deployed, 'evidence': cert.get('evidence', {}), 'blockers': cert.get('blockers', []), 'generatedBy': 'scripts/generate-public-status-docs.py'}
    if upper == 'ETHEREUM_MAINNET_AUTHORIZED': data['finalManualDeploymentCommand'] = 'npm run deploy:ethereum-mainnet:gated' if value == 'YES' else None
    (ROOT/f'{base}.json').write_text(json.dumps(data, indent=2)+'\n')
    (ROOT/f'{base}.md').write_text(f'# {label.title()} Decision\n\n{label}: **{value}**.\n\n{upper}: **{value}**\n\nMAINNET_DEPLOYED: **{deployed}**\n\nNot externally audited. External audit is not planned and is not an active mainnet gate. Automated/internal security-toolchain clearance is the active security gate.\n')
# Backward-compatible alias consumed by older public-status links. It must
# mirror the deployment authorization decision and must not retain stale YES.
(ROOT/'docs/MAINNET_AUTHORIZATION_DECISION.json').write_text((ROOT/'docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json').read_text())
(ROOT/'docs/MAINNET_AUTHORIZATION_DECISION.md').write_text((ROOT/'docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md').read_text())
(ROOT/'README.md').write_text(readme)
(ROOT/'docs/CURRENT_STATUS.md').write_text('# Current Status\n\n'+status_block+f"\n## Certificate source\n\n`qa/mainnet-authorization-certificate.json` generated by `{cert_value('generatedBy', default='scripts/mainnet_three_stage.py')}`. Timestamp is intentionally omitted from generated docs to keep status checks deterministic.\n")
(ROOT/'START_HERE.md').write_text(f"""# Start Here — GoalOS AGIALPHA Ascension Repository

This repository is the institutional source package for **GoalOS AGIALPHA Ascension**.

## One-sentence description

GoalOS AGIALPHA Ascension is a GoalOS-native reimplementation of α‑AGI Ascension using the existing AGIALPHA token to coordinate proof-settled AI workflow work.

## Correct current label

```text
{status_label}
```

## What this means

{authorization_meaning.replace('This means the repository package', 'The repository package')}

The active source-of-truth hierarchy starts with Mainnet receipts and on-chain readbacks, then `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/verification-evidence.json`, `qa/mainnet-postdeploy/`, `qa/mainnet-release-state.json`, `release/mainnet-2026-06-21/`, and generated public docs. README and status documents summarize evidence; they cannot create deployment, verification, authorization, audit, production activation, or user-fund claims independently.

## Read in this order

1. `README.md`
2. `docs/DOCUMENTATION_INDEX.md`
3. `docs/DOCUMENTATION_MAINTENANCE.md`
4. `docs/CURRENT_STATUS.md`
5. `docs/OFFICIAL_BADGES.md`
6. `docs/ETHEREUM_MAINNET.md`
7. `docs/ETHEREUM_MAINNET_CONTRACTS.md`
8. `docs/SECURITY_AND_LIMITATIONS.md`
9. `docs/OPERATIONS_RUNBOOK_MAINNET.md`
10. `docs/SAFE_CLAIMS_AND_TOKEN_BOUNDARY.md`
11. `docs/EXTERNAL_AUDITOR_HANDOFF.md`

## Next real step

```text
For reviewers: run `npm run docs:all`, inspect current evidence files, and keep unresolved Stage-B/Stage-C items bounded.
For operators: use read-only status and postdeployment checks unless a separate private operator package explicitly authorizes a local-only action.
For contributors: preserve safety boundaries, update generated docs through their generators, and do not weaken Mainnet gates.
```
""")
(ROOT/'docs/MAINNET_AUTHORIZATION_CERTIFICATE.md').write_text(f"""# Mainnet Authorization Certificate

Generated from `qa/mainnet-authorization-certificate.json`.

- TECHNICALLY_MAINNET_READY: **{tech}**
- MAINNET_DEPLOYMENT_AUTHORIZED: **{dep}**
- ETHEREUM_MAINNET_AUTHORIZED: **{eth}**
- MAINNET_DEPLOYED: **{deployed}**
- Private operator authorization package required: **{cert_value('privateOperatorAuthorizationPackageRequired', default='False')}**
- Runtime secrets stored in GitHub: **{cert_value('runtimeSecretsStoredInGitHub', default='False')}**
- CI can deploy mainnet: **{cert_value('ciCanDeployMainnet', default='False')}**

{certificate_meaning} It is not an external audit, legal approval, tax review, proof of deployment, or guarantee of security/token classification.

## Next action

{cert_value('nextAction', default='Resolve Stage-A blockers; do not broadcast Mainnet.')}
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

if args.check:
    changed=[rel for rel, old in before.items() if ((ROOT/rel).read_text() if (ROOT/rel).exists() else None) != old]
    if changed:
        print('Public status docs are stale; rerun npm run docs:status:write. Changed: '+', '.join(changed))
        sys.exit(1)
    print('Public status docs check passed.')
else:
    print('Generated public status docs from qa/mainnet-authorization-certificate.json')
