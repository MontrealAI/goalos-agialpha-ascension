# Access Control Matrix

| Capability | Authorized role/account | Negative invariant |
|---|---|---|
| Grant/revoke roles | Admin | Operators cannot self-escalate to admin |
| Launch gate updates | Operator | Unauthorized callers cannot set gates |
| Credential issuance | ProofSubmissionRegistry/operator flow | No credential without approved proof |
| Reputation update | ProofSubmissionRegistry/operator flow | Arbitrary caller cannot increase reputation |
| Vault release | Admin/operator per vault | No zero recipient or over-release |
| Reviewer validation | Bonded reviewer through ReviewerBondRegistry | Unbonded reviewer cannot validate |
