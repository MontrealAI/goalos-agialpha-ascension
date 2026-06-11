# v4.1 Sepolia-Safe Hotfix

## Reason

v4.0 was strong, but the `.env.example` placed the Ethereum mainnet AGIALPHA token address into `AGIALPHA_TOKEN_ADDRESS` by default. On Ethereum Sepolia that address normally has no code, so a new operator could copy `.env.example`, run Sepolia rehearsal, and hit a confusing token-code failure.

## Fix

- `AGIALPHA_TOKEN_ADDRESS` is blank by default in `.env.example`.
- On non-mainnet networks, blank `AGIALPHA_TOKEN_ADDRESS` deploys `MockAGIALPHA`.
- If the mainnet AGIALPHA address is accidentally supplied on non-mainnet, the script deploys `MockAGIALPHA` instead.
- If any other non-mainnet token address has no code, deployment fails unless `ALLOW_NONMAINNET_MOCK_ON_MISSING_TOKEN=YES`.
- Ethereum mainnet still requires the exact AGIALPHA token address and all signoff hashes.

## Mainnet boundary

This is not a mainnet authorization. It is an audit and rehearsal usability hotfix.
