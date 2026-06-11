# GoalOS AGIALPHA Ascension Security Invariants

## Token / AGIALPHA Boundary
- Ethereum Mainnet AGIALPHA token address is exactly `0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`.
- No new AGIALPHA token may be deployed on Ethereum Mainnet; `MockAGIALPHA` is Sepolia/local only.
- Vault funding is separate from deployment.
- No contract assumes mint authority over AGIALPHA.
- AGIALPHA transfers use SafeERC20 or equivalent safe handling.


## Launch Gates
- `LaunchGateRegistry` uses `ETHEREUM_SEPOLIA_REHEARSAL`, not Base Sepolia naming.
- Required gates: `LEGAL_REVIEW`, `TAX_REVIEW`, `SECURITY_REVIEW`, `PUBLIC_CLAIMS_REVIEW`, `TREASURY_REVIEW`, `AGIALPHA_TOKEN_VERIFICATION`, `ETHEREUM_SEPOLIA_REHEARSAL`, `AUTOMATED_SECURITY_TOOLCHAIN`, `INTERNAL_SECURITY_REVIEW`, `FOUNDER_APPROVAL`.
- `allCoreGatesPassed()` is false unless all required gates are true.
- Gate evidence hashes are nonzero `bytes32` values.
- Only authorized operators can set gates.
- Deploy scripts refuse mainnet unless all gates are valid.
- The mainnet authorization checker returns `NOT_AUTHORIZED` without real gates.

## Access Control
- Only admin grants/revokes privileged roles; operators cannot escalate to admin without admin.
- Unauthorized callers cannot issue credentials, set protocol config, slash, release vault funds, or update launch gates.
- Constructors and setters reject zero addresses.

## Proof Lifecycle
- Proof seed creation requires valid seed hash/category.
- Job posting requires valid metadata, reward, deadline, and AGIALPHA approval/transfer path.
- Job claim requires required bond.
- Proof submission requires claimed active job, proof hash, and proof-card hash.
- Reviewer validation requires reviewer bond; rejected proofs follow refund/slashing policy.
- Approved proof can create Proof Card, credential, and reputation update.
- No credential without approved proof.
- No reputation increase without approved proof or authorized credential event.
- No settlement without ProofBundle or proof-equivalent evidence hash.

## Vaults
- Performance vault cannot release without authorized milestone approval.
- Vault release cannot exceed available balance.
- No release to zero address.
- Proof/rewards/liquidity/security/community vaults enforce admin/operator constraints.
- Token-moving functions must be non-reentrant; critical paths must avoid unbounded user-controlled loops.

## Reputation / Referral / Premium Access
- Referral attribution cannot be overwritten unless explicitly allowed and documented.
- Reputation cannot be updated by arbitrary callers.
- Premium access cannot be unlocked by AGIALPHA balance alone if reputation/credential gates are required.
- Revocation blocks credential validity where applicable.

## AEP / GoalOS Proof-of-Evolution
- GoalOSCommit / RunCommitment / ProofBundle / EvalAttestation / SelectionCertificate flow cannot skip proof/eval.
- SelectionGate requires proof validity, eval pass, risk threshold, rollback readiness, canary readiness, scope authorization, and challenge clearance where implemented.
- Rollout requires rollback target; rollback receipts reference valid rollout/incident roots.
- Evidence Docket entries have nonzero hashes and valid status.

## Privacy Boundary
- Contracts store hashes, roots, URIs, attestations, and public-safe metadata only.
- Do not store private prompts, raw traces, customer data, legal memos, tax memos, or privileged workpapers on-chain.
