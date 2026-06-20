This deployment is dormant infrastructure only. It is not production-ready. It does not authorize user funds, Phase-B configuration, activation, settlement, a public frontend, production announcements, or public reliance.

# Dormant Initial Mainnet Deployment Policy

The dormant authorization certificate is a separate `DORMANT_INITIAL_MAINNET_DEPLOYMENT` gate. It never edits or reinterprets the ordinary production certificate. Dormant YES fields may only describe predeployment readiness for a dormant Mainnet ceremony; all production, user-fund, activation, Phase-B, settlement, frontend, announcement, and public-reliance fields remain NO.

## Public/private evidence classes

- `PUBLIC_PREDEPLOYMENT_EVIDENCE`: tracked commitment-only certificate and public plan under `qa/dormant-mainnet-readiness/`.
- `PRIVATE_OPERATOR_OVERLAY`: ignored local files under `.private/dormant-mainnet/`, mode `0600` where supported.
- `PUBLIC_POSTDEPLOYMENT_CHAIN_EVIDENCE`: tracked chain-1 receipt-backed evidence only after real receipts, runtime bytecode, verification, and authority readback validate it.

Wallet A is the disposable transaction signer and gas payer only. Wallet B is the Ledger governance Owner and every permanent authority. Only commitments to these addresses may appear in tracked predeployment evidence. The Ledger seed or private key is prohibited.

Dormancy is an operational posture, not a protocol-wide immutable freeze. Phase-B configuration remains unexecuted, GoalOS funds no contract or vault, no public frontend is connected, no launch or invitation is made, and checked initial ETH/AGIALPHA balances are zero. Third parties may still call public functions or send unsolicited ETH/tokens; unsolicited transfers are unauthorized and do not constitute accepted user funds.

The certificate is short-lived (default 12 hours) and binds release/source, dependency lock, compiler/build inputs, scripts, tests, schemas, public plan hash, private operator commitment, fee policy, authority roots, and output paths. Production transition requires a fresh independent production certificate.
