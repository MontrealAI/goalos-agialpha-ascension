# Deterministic Solidity Compiler Policy

The public CI compiler baseline is the pinned local `solc` npm package: **solc-js 0.8.35**. `hardhat.config.ts`, deterministic compilation, Slither precompile, and generated Hardhat artifacts are aligned to this baseline.

Public CI must use:

```bash
npm ci
npm run verify:compiler-alignment
npm run compile:ci
npm run test:ci
```

`compile:ci` runs `scripts/compile-deterministic.js`, which invokes local `solc-js` directly and then generates Hardhat-compatible artifacts. It does not rely on a Hardhat network compiler download. `compile:hardhat` remains available for local development only.

This policy intentionally avoids mixed compiler assumptions. Any compiler change must update `package.json`, `package-lock.json`, `hardhat.config.ts`, this document, compiler-alignment evidence, Slither instructions, and CI workflows in one reviewed change.
