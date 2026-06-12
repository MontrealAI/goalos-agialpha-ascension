# Security Invariants

## AGIALPHA/token boundary

Ethereum Mainnet AGIALPHA token address is exactly `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`. No new AGIALPHA token is deployed on Ethereum Mainnet. MockAGIALPHA is local/Sepolia only. No mint authority is assumed. Vault funding is separate from deployment.

## Launch gates

Automated/internal security gates are active; mandatory external audit gate is not active. All core gates require nonzero evidence hashes and authorized operators. Deploy scripts refuse mainnet unless certificate and guardrails pass.

## Access control

Admin-only grants/revocations, no operator-to-admin escalation, unauthorized users cannot issue credentials/config/slash/release funds/update launch gates, and zero addresses are rejected.

## Proof lifecycle

No credential or reputation increase without approved proof or authorized event. No settlement without ProofBundle/proof-equivalent evidence hash.

## Vaults and privacy

No release without milestone approval, no over-release, no zero-address release, no reentrancy on token-moving functions, and no unbounded user loops in critical paths. On-chain data stores hashes/roots/URIs/attestations/public-safe metadata only.

## Deployment guardrails

Mainnet deployment fails in GitHub Actions, wrong chainId, wrong AGIALPHA token, MockAGIALPHA, missing/NO certificate, missing typed confirmation, and never deploys a new AGIALPHA token or requires private authorization package.
