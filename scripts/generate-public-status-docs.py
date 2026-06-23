#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.release.current_mainnet_state import normalize

parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
ACTIVE_OUTPUTS = ['README.md','START_HERE.md','docs/CURRENT_STATUS.md','docs/START_HERE_MAINNET.md','docs/ETHEREUM_MAINNET.md','docs/REPOSITORY_STATUS.md']
before = {rel: (ROOT/rel).read_text() if (ROOT/rel).exists() else None for rel in ACTIVE_OUTPUTS}
state = normalize()
counts = state['counts']; statuses = state['statuses']; facts = state['facts']
public_table = f'''| Item | Current value |
| --- | --- |
| Ethereum Mainnet deployment | {statuses['deployment']} — {facts['mainnetDeployed']} |
| Mainnet configuration | {statuses['configuration']} — {facts['mainnetConfigured']} |
| GoalOS contracts | {counts['goalosContracts']} |
| Canonical external AGIALPHA | {counts['externalContracts']} |
| Operator verification evidence | {statuses['operatorVerification']} — {counts['operatorVerifiedContracts']}/48 |
| Postdeployment operator evidence | {statuses['operatorPostdeploymentEvidence']} — {facts['postdeploymentStatus']} |
| Phase-B grants | PASS — {facts['phaseBGrants']} |
| Permanent authority | PASS — Wallet B / Ledger |
| Wallet A managed roles | PASS — {counts['walletAManagedRoles']} |
| Predeployment authorization | {statuses['predeploymentAuthorization']} — {state['deploymentPath']} |
| Independent live revalidation | {statuses['independentLiveRevalidation']} |
| Source-identity reproducibility | {statuses['sourceIdentityReproducibility']} |
| Production activation | {statuses['productionActivation']} |
| User-fund authorization | {statuses['userFundAuthorization']} |
'''
explain = 'PENDING_EXTERNAL_INPUT is not a deployment failure. It means optional independent dual-provider validation was not run in an environment containing protected read-only credentials.'
boundary = 'No external-audit claim is made by this release. External-audit completion is not an active release-state gate. This repository does not claim production activation, user-fund authorization, legal approval, tax approval, guaranteed security, yield, revenue share, or price appreciation.'
source = 'Current source of truth: `qa/mainnet-release-state.json`, `deployments/ethereum-mainnet.agialpha.latest.json`, `qa/mainnet-postdeploy/verification-evidence.json`, `config/ethereum-mainnet.contracts.json`, and `release/mainnet-2026-06-21/`. Historical Stage-A predeployment records are preserved but do not override the current direct-operator postdeployment release state.'
readme = f'''# GoalOS AGIALPHA Ascension

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Solidity 0.8.28](https://img.shields.io/badge/Solidity-0.8.28-363636?logo=solidity)](package.json)
[![Hardhat 2.28.6](https://img.shields.io/badge/Hardhat-2.28.6-f5d061?logo=ethereum)](package.json)

GoalOS AGIALPHA Ascension is an evidence-first Ethereum/Hardhat repository for proof-settled AI workflow coordination using the existing canonical AGIALPHA token.

## Current Mainnet status

Ethereum Mainnet deployed: {facts['mainnetDeployed']}.
Mainnet configured: {facts['mainnetConfigured']}.

{public_table}
{explain}

{source}

## Canonical AGIALPHA

Canonical AGIALPHA on Ethereum Mainnet is `{facts['canonicalAgialpha']}`. It is external to GoalOS: `external = true`, `deployedByGoalOS = false`, and `mintedByGoalOS = false`.

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
current = f'''# Current Status

## Ethereum Mainnet release state

{public_table}
{explain}

{source}

## Claim boundary

{boundary}
'''
start = f'''# Start Here — GoalOS AGIALPHA Ascension

Begin with the current postdeployment release state, not the historical Stage-A predeployment certificate.

{public_table}

{explain}

Read next: `README.md`, `docs/CURRENT_STATUS.md`, `docs/ETHEREUM_MAINNET.md`, `docs/SECURITY_AND_LIMITATIONS.md`, and `release/mainnet-2026-06-21/README.md`.
'''
mainnet_start = f'''# Start Here: Ethereum Mainnet

{current}

## Safe ordinary validation

```bash
npm run mainnet:release-state:all
```

The ordinary validation path is offline/public and must not receive deployer private keys, mnemonics, Ledger seeds, RPC URLs, Etherscan keys, or write/broadcast permissions.
'''
eth = f'''# Ethereum Mainnet

{public_table}

{explain}

{boundary}
'''
repo = f'''# Repository Status

Current repository/release continuity status is derived from the canonical Mainnet lifecycle adapter.

{public_table}

{explain}
'''
(ROOT/'README.md').write_text(readme)
(ROOT/'START_HERE.md').write_text(start)
(ROOT/'docs/CURRENT_STATUS.md').write_text(current)
(ROOT/'docs/START_HERE_MAINNET.md').write_text(mainnet_start)
(ROOT/'docs/ETHEREUM_MAINNET.md').write_text(eth)
(ROOT/'docs/REPOSITORY_STATUS.md').write_text(repo)
if args.check:
    changed = [rel for rel, old in before.items() if ((ROOT/rel).read_text() if (ROOT/rel).exists() else None) != old]
    if changed:
        print('Public status docs are stale; rerun npm run docs:status:write. Changed: '+', '.join(changed)); sys.exit(1)
    print('Public status docs check passed.')
else:
    print('Generated public status docs from canonical current Mainnet state')
