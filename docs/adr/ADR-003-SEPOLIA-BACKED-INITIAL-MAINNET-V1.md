# ADR-003 — SEPOLIA_BACKED_INITIAL_MAINNET_V1 Stage-A Scope

## Status

Accepted for the limited initial Ethereum Mainnet infrastructure deployment path.

## Decision

`SEPOLIA_BACKED_INITIAL_MAINNET_V1` accepts the existing verified Sepolia deployment as public-chain deployment and verification experience, while proving current-release authority, safety, planning, verification readiness, and recovery readiness from local deterministic evidence and read-only Mainnet dependency checks.

Physical Ledger approval, the Wallet-A deployer private key, the live Etherscan API key, Wallet-A funding, final fee acceptance, and typed deployment confirmation are mandatory immediately before a later live broadcast, but they are not Stage-A predicates for repository-controlled predeployment authorization.

## Scope limits

This profile authorizes only initial Mainnet infrastructure deployment. It does not authorize production activation, public frontend publication, customer onboarding, settlement, user funds, public reliance, or Phase-B configuration.

The stricter `CONTROLLED_PRODUCTION_RELEASE` profile remains unchanged and retains its Mainnet-fork and production-readiness requirements.

## Residual risk

The historical Sepolia deployment used Solidity 0.8.35, MockAGIALPHA, and a different one-address authority model. Those facts are disclosed and accepted only as historical public-chain execution evidence. They do not prove current-release bytecode parity or final Mainnet authority configuration.
