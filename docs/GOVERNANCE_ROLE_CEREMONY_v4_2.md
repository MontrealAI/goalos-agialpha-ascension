> Historical/deprecated note: this document describes a prior pre-certificate authorization model. The active source of truth is `qa/mainnet-authorization-certificate.json`.

# Governance Role Ceremony v4.2

Before mainnet, privileged roles must be reviewed and intentionally assigned.

## Required roles to review

```text
DEFAULT_ADMIN_ROLE
OPERATOR_ROLE
pauser / emergency operator
vault admin
reviewer manager
evaluator manager
falsification reporter admin
launch gate operator
```

## Recommended ceremony

1. Confirm Safe / multisig addresses.
2. Confirm founder address.
3. Confirm treasury address.
4. Confirm operator addresses.
5. Confirm no privileged role remains with an unintended deployer wallet.
6. Record role assignment transaction hashes.
7. Record signer roster.
8. Record emergency pause authority.
9. Record upgrade / no-upgrade policy.
10. Produce governance signoff hash.

## Output

```text
GOVERNANCE_ROLE_CEREMONY_HASH
```
