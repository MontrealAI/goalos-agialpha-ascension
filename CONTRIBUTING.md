# Contributing

Do not fabricate deployment, verification, audit, production activation, or user-fund evidence. Preserve private/operator boundaries and do not commit secrets, raw operator logs, `.private/` material, RPC URLs, API keys, mnemonics, Ledger secrets, browser profiles, caches, or coverage artifacts.

## Documentation changes

- Start with `docs/DOCUMENTATION_INDEX.md` and `docs/DOCUMENTATION_MAINTENANCE.md` before changing public status, deployment, verification, operator, or release documentation.
- Generated Mainnet docs and registries must be updated through their source inputs or generators; do not hand-edit generated outputs as the source of truth.
- Use `npm run docs:mainnet:write` only when generated Mainnet documentation intentionally needs to be refreshed, then run `npm run docs:all`.
- Run `npm run docs:all` before merging documentation changes; it checks deterministic Mainnet docs, internal documentation links, stale current claims, and the Mainnet contract registry.
- Keep claim boundaries explicit: Mainnet deployed YES requires chainId=1 transaction evidence, verified YES requires verification evidence or confirmed already-verified status, and production activation/user-fund authorization/external audit remain NO unless their evidence changes.

## Mainnet safety

Do not weaken Mainnet gates, add CI Mainnet broadcast, introduce a new Mainnet AGIALPHA token path, or promote historical/predeployment evidence into current live claims. Prefer wrappers around existing scripts over duplicate deployment or verification systems.
