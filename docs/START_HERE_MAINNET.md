# Start Here: Mainnet

GoalOS AGIALPHA Ascension v4.4 mainnet authorization candidate.

Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Public Sepolia: recommended but not required for public repository authorization.
Not externally audited.
Ethereum Mainnet technical readiness: YES.
Ethereum Mainnet deployment authorization: YES.
Ethereum Mainnet authorization: YES.
Ethereum Mainnet deployed: NO.

This means the repository package is authorized for manual gated Ethereum Mainnet deployment when the certificate says YES. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.

It does not claim external audit, legal approval, tax review, guaranteed security, guaranteed non-security, investment, yield, revenue share, price target, or production deployment.

1. Run `npm run mainnet:local-checks`.
2. Run `npm run mainnet:security`.
3. Run `npm run mainnet:local-rehearsal`.
4. Run `npm run mainnet:certificate && npm run mainnet:certificate:validate`.
5. If authorized, run `npm run deploy:ethereum-mainnet:gated` locally only with runtime RPC/key.
