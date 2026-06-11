# Mainnet Authorization Inputs Required

Required inputs before any YES decision can be generated:

1. Baseline green evidence: `npm ci`, repo checks, compile, tests, static checks, readiness, public status, and Evidence Docket template.
2. Automated/internal security clearance: no unresolved critical/high findings and medium findings fixed or explicitly accepted.
3. Public Ethereum Sepolia replay: chainId `11155111`, public transaction receipts, proof-work loop, negative paths, Evidence Docket, and independent RPC receipt verification.
4. Ethereum Mainnet AGIALPHA verification: read-only RPC proof that `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA` has token code and expected ERC-20 metadata where available.
5. Ethereum Mainnet preflight: read-only chainId 1 verification, exact AGIALPHA address, no MockAGIALPHA/new AGIALPHA path, and authorization gating.
6. Mainnet fork simulation: fork-only deployment and smoke tests using the existing AGIALPHA address.
7. Branch protection: enabled on `main`, or explicit founder risk acceptance.
8. Address ceremony: founder, deployer, treasury, admin, emergency/pause guardian, custody notes, and chainId 1.
9. Founder deployment approval: preferably wallet-signed message with message hash and signer verification.
10. Policy signoffs or founder waivers: legal/token counsel, tax/accounting, public claims, treasury, automated security, and internal security.

If any input is missing, the generated decisions must remain NO.
