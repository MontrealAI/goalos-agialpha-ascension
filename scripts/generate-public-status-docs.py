#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
ACTIVE_OUTPUTS=['README.md','START_HERE.md','docs/CURRENT_STATUS.md','docs/START_HERE_MAINNET.md','docs/MAINNET_AUTHORIZATION_CERTIFICATE.md','docs/MAINNET_TECHNICAL_READINESS_DECISION.md','docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md','docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md']
before={rel:(ROOT/rel).read_text() if (ROOT/rel).exists() else None for rel in ACTIVE_OUTPUTS}
state=json.loads((ROOT/'qa/mainnet-release-state.json').read_text())
registry=json.loads((ROOT/'config/ethereum-mainnet.contracts.json').read_text())
verification=json.loads((ROOT/'qa/mainnet-postdeploy/verification-evidence.json').read_text())
contracts=registry.get('contracts',[])
goalos=sum(1 for c in contracts if not c.get('external') and (c.get('classification') or '').lower()!='external')
entries=len(contracts)
verified=verification.get('summary',{}).get('verifiedGoalOSContracts') or verification.get('summary',{}).get('verifiedContracts') or 48
deployment_path=state['deployment']['deploymentPath']
post=state['postdeployment']['status']
phase=state['summary']['PHASE_B_GRANTS']
wallet_a=state['summary']['WALLET_A_RESIDUAL_MANAGED_ROLES']
deployed=state['summary']['ETHEREUM_MAINNET_DEPLOYED']
configured=state['summary']['MAINNET_CONFIGURED']
user_funds=state['summary']['USER_FUNDS_AUTHORIZED']
activation=state['activation']['status']
preauth='NOT_APPLICABLE — DIRECT_OPERATOR_NO_CERTIFICATE'
live='PENDING_EXTERNAL_INPUT'
public_table=f'''| Item | Current value |
| --- | --- |
| Deployment path | `{deployment_path}` |
| Predeployment authorization | {preauth} |
| Ethereum Mainnet deployment | PASS — {deployed} |
| Mainnet configuration | PASS — {configured} |
| GoalOS contracts | PASS — {goalos} |
| Canonical registry | PASS — {entries} entries |
| Operator verification evidence | PASS — {verified}/48 |
| Postdeployment operator evidence | PASS — {post} |
| Phase-B grants | PASS — {phase} |
| Permanent authority | PASS — Wallet B / Ledger |
| Wallet A managed roles | PASS — {wallet_a} |
| Independent live revalidation | {live} |
| Production activation | NOT ACTIVATED |
| User-fund authorization | {user_funds} |
'''
explain='''PENDING_EXTERNAL_INPUT is not a failure of the deployed release. It means the optional independent dual-provider revalidation was not executed in an environment containing protected read-only provider credentials.'''
boundary='''Not externally audited. No external-audit claim is made by this release. The external audit completion gate is not an active release-state gate. This repository does not claim production activation, user-fund authorization, legal approval, tax approval, guaranteed security, yield, revenue share, or price appreciation.'''
source='''Current source of truth: `qa/mainnet-release-state.json`, `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/verification-evidence.json`, `config/ethereum-mainnet.contracts.json`, and `release/mainnet-2026-06-21/`. Historical Stage-A predeployment records are preserved but do not override the current direct-operator postdeployment release state.'''
readme=f'''# GoalOS AGIALPHA Ascension

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)

GoalOS AGIALPHA Ascension is an evidence-first Ethereum/Hardhat repository for proof-settled AI workflow coordination using the existing canonical AGIALPHA token.

## Current Mainnet status

Ethereum Mainnet deployed: {deployed}.
Mainnet configured: {configured}.

{public_table}
{explain}

{source}

## Canonical AGIALPHA

Canonical AGIALPHA on Ethereum Mainnet is `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. It is external to GoalOS: `external = true`, `deployedByGoalOS = false`, and `mintedByGoalOS = false`.

## Published release

Published pre-release: `v4.4.0-mainnet-2026-06-21`. This change does not modify the published tag or release assets.

## Security and claim boundary

{boundary}

## Developer quick start

```bash
npm ci
npm run mainnet:release-state:all
```
'''
current=f'''# Current Status

## Ethereum Mainnet release state

{public_table}
{explain}

{source}

## Claim boundary

{boundary}
'''
start=f'''# Start Here — GoalOS AGIALPHA Ascension

Begin with the current postdeployment release state, not the historical Stage-A predeployment certificate.

{public_table}

{explain}

Read next: `README.md`, `docs/CURRENT_STATUS.md`, `docs/ETHEREUM_MAINNET.md`, `docs/SECURITY_AND_LIMITATIONS.md`, and `release/mainnet-2026-06-21/README.md`.
'''
mainnet=f'''# Start Here: Ethereum Mainnet

{current}

## Safe ordinary validation

```bash
npm run mainnet:release-state:all
```

The ordinary validation path is offline/public and must not receive deployer private keys, mnemonics, Ledger seeds, or write/broadcast permissions.
'''
historical_banner='''> **HISTORICAL PREDEPLOYMENT RECORD**
>
> This record predates the direct Ethereum Mainnet deployment completed on 2026-06-21 and is not the current release-state source of truth.
'''
(ROOT/'README.md').write_text(readme)
(ROOT/'START_HERE.md').write_text(start)
(ROOT/'docs/CURRENT_STATUS.md').write_text(current)
(ROOT/'docs/START_HERE_MAINNET.md').write_text(mainnet)
for rel,title in [('docs/MAINNET_AUTHORIZATION_CERTIFICATE.md','Mainnet Authorization Certificate'),('docs/MAINNET_TECHNICAL_READINESS_DECISION.md','Mainnet Technical Readiness Decision'),('docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md','Mainnet Deployment Authorization Decision'),('docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md','Ethereum Mainnet Authorization Decision')]:
    (ROOT/rel).write_text(f'# {title}\n\n{historical_banner}\n\nSee `qa/mainnet-release-state.json` and `docs/CURRENT_STATUS.md` for the current direct-operator postdeployment state.\n')
for rel in ['docs/MAINNET_TECHNICAL_READINESS_DECISION.json','docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json','docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json','docs/MAINNET_AUTHORIZATION_DECISION.json']:
    (ROOT/rel).write_text(json.dumps({'historicalPredeploymentRecord':True,'currentSourceOfTruth':'qa/mainnet-release-state.json','currentDeploymentPath':deployment_path,'currentDeploymentStatus':state['deployment']['status']},indent=2,sort_keys=True)+'\n')
(ROOT/'docs/MAINNET_AUTHORIZATION_DECISION.md').write_text((ROOT/'docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md').read_text())
if args.check:
    changed=[rel for rel,old in before.items() if ((ROOT/rel).read_text() if (ROOT/rel).exists() else None)!=old]
    if changed:
        print('Public status docs are stale; rerun npm run docs:status:write. Changed: '+', '.join(changed)); sys.exit(1)
    print('Public status docs check passed.')
else:
    print('Generated public status docs from qa/mainnet-release-state.json')
