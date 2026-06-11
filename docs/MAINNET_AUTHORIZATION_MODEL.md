# Mainnet Authorization Model

This repository uses three separate machine-computed statuses. They must not be collapsed into a vague readiness flag.

## TECHNICALLY_MAINNET_READY

Meaning: contracts, dependency graph, tests, automated/internal security checks, public Ethereum Sepolia replay, AGIALPHA verification, mainnet preflight, fork simulation, and unresolved findings are acceptable for Ethereum Mainnet deployment.

## MAINNET_DEPLOYMENT_AUTHORIZED

Meaning: `TECHNICALLY_MAINNET_READY=YES`, founder approval is explicit, treasury/admin/founder address ceremony is complete, required policy signoffs exist or are explicitly waived by founder policy, and deployment is permitted.

## ETHEREUM_MAINNET_AUTHORIZED

Meaning: both technical readiness and deployment authorization are `YES`, target chain is Ethereum Mainnet, the existing AGIALPHA token address is exact, the final manual gated deployment command may be run by the founder/deployer, and CI still does not automatically deploy mainnet.

## Current status

- `TECHNICALLY_MAINNET_READY`: computed by `scripts/mainnet-readiness-check.py`.
- `MAINNET_DEPLOYMENT_AUTHORIZED`: computed by `scripts/mainnet-deployment-authorization-check.py`.
- `ETHEREUM_MAINNET_AUTHORIZED`: computed by `scripts/ethereum-mainnet-authorization-check.py`.

No Ethereum Mainnet deployment occurs in these checks.
