# Public Mainnet Authorization Semantics

TECHNICALLY_MAINNET_READY: YES means tests, deterministic dependencies, internal automated security tooling, local rehearsal, token boundary checks, guardrails, docs, CI, and public evidence are sufficient for manual deployment authorization.

MAINNET_DEPLOYMENT_AUTHORIZED: YES means public repository governance authorizes a deployer to run the gated command if runtime validation passes locally.

ETHEREUM_MAINNET_AUTHORIZED: YES means both prior states are YES, target chain is Ethereum Mainnet chainId 1, AGIALPHA address is fixed, and CI cannot deploy mainnet.
