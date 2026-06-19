# ADR: GoalOS ownership transfer design

GoalOS managed contracts keep RBAC authorization and expose ERC-173 ownership. The owner is coupled to `DEFAULT_ADMIN_ROLE` and the six operational roles. Fresh Mainnet deployment sets the governance owner in each constructor; the disposable payer is not an owner, default admin, operator, vault admin, or economic destination.

Future ownership changes are two-step. `transferOwnership(newOwner)` records a pending owner and a fixed 24 hour delay. `acceptOwnership()` can be called only by the pending owner after the delay; it grants owner-coupled roles to the new owner, transfers canonical ownership, and revokes owner-coupled roles from the previous owner atomically. Renunciation and zero-address transfer are disabled.

A fixed delay is used rather than a mutable delay to avoid a same-transaction or short-notice governance-delay reduction. This ADR does not authorize one-step Mainnet transfers, proxies, hidden guardians, tx.origin authorization, or deployment-time disposable control.
