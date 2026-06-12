# GoalOS AGIALPHA Ascension

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


## Final manual deployment command

```bash
npm run deploy:ethereum-mainnet:gated
```

The command is local/manual only and is blocked in GitHub Actions/CI. The AGIALPHA token on Ethereum Mainnet remains `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`; this repository does not deploy or mint a new AGIALPHA token on Ethereum Mainnet.
