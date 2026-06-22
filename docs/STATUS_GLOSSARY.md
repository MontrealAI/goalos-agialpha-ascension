# Status Glossary

- Deployment YES: chainId 1 deployment transaction evidence exists for GoalOS-created contracts.
- Configuration YES: postdeployment role/configuration readbacks are recorded as configured.
- Operator verification evidence 48/48: GoalOS-created contracts have Etherscan verification evidence or confirmed already-verified status.
- Independent dual-RPC revalidation: a separate readback result; use the evidence file's actual status.
- Stage-B certificate: a separate postdeployment certificate; use the certificate file's actual status.
- Production activation NO: production writes, user-fund flows, and public reliance remain disabled.
- User-fund authorization NO: no user funds are authorized.
- Historical Stage-A certificate: predeployment evidence, not the current sole source of truth.
- `DEFAULT_ADMIN_ROLE = 0x00...00`: role identifier, not a wallet address.
