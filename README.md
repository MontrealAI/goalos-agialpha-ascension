# GoalOS AGIALPHA Ascension

GoalOS AGIALPHA Ascension v4.4.0 mainnet authorization candidate.

Automated/internal security toolchain: passed.
Local deterministic rehearsal: passed.
Local Evidence Docket: generated.
Public AGIALPHA token verification: passed / governance-accepted.
Not externally audited.
Ethereum Mainnet technical readiness: YES.
Ethereum Mainnet deployment authorization: YES.
Ethereum Mainnet authorization: YES.
Ethereum Mainnet deployed: NO.

This means the repository package is authorized for manual gated Ethereum Mainnet deployment. It does not mean Ethereum Mainnet deployment has occurred. Actual deployment still requires a runtime RPC URL and deployer key outside GitHub.

It does not claim external audit completion, legal approval, tax review, guaranteed security, guaranteed token classification, investment return, yield, price target, revenue share, or production deployment.

Public Sepolia deployment is recommended but not mandatory for public authorization; local deterministic rehearsal and mainnet-shaped simulation are the active public gates.


## Core doctrine

- GoalOS decides what may evolve.
- AGIALPHA coordinates proof-settled work.
- Evidence Dockets make claims auditable.
- Do not put intelligence on-chain; put proof of intelligence on-chain.
- No proof, no evolution. No eval, no propagation. No rollback, no release.

## Ethereum Mainnet authorization

The source of truth is `qa/mainnet-authorization-certificate.json`. README/status documents are generated from that certificate; manual edits cannot create YES.

- TECHNICALLY_MAINNET_READY: **YES**
- MAINNET_DEPLOYMENT_AUTHORIZED: **YES**
- ETHEREUM_MAINNET_AUTHORIZED: **YES**
- MAINNET_DEPLOYED: **NO**
- Canonical AGIALPHA token: `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`
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
