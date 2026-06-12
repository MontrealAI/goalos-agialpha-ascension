# Public Mainnet Authorization Semantics

TECHNICALLY_MAINNET_READY: YES means public code, dependency graph, deterministic compiler, tests, static checks, automated/internal security tooling, Slither, local deterministic rehearsal, Evidence Docket, AGIALPHA boundary, deployment guardrails, public docs, CI, and evidence artifacts are sufficient to authorize the package for manual deployment.

MAINNET_DEPLOYMENT_AUTHORIZED: YES means public repository governance authorizes a manual deployer to run the gated deployment command if runtime inputs pass script validation.

ETHEREUM_MAINNET_AUTHORIZED: YES means technical readiness and deployment authorization are YES, the target is Ethereum Mainnet chainId 1, AGIALPHA is exact, deployment is manual/local, and CI cannot deploy mainnet.

MAINNET_DEPLOYED remains NO until real transaction evidence exists.
