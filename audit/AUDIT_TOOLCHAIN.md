# Audit Toolchain

Implemented scripts:
- `npm run audit:slither` emits `slither.txt`, `slither.json`, and `slither.sarif` when Slither is installed.
- `npm run audit:echidna` runs Echidna or records environment-blocked evidence.
- `npm run audit:mythril` runs Mythril symbolic execution or records environment-blocked evidence.
- `npm run audit:medusa` runs Medusa or records environment-blocked evidence.
- `npm run audit:foundry` runs Forge build/tests or records environment-blocked evidence.
- `npm run audit:all` writes a timestamped report directory and summary.

CI uploads audit artifacts and does not run mainnet deployment.
