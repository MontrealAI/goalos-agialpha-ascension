const message = [
  "Hardhat Ignition Ethereum Mainnet deployment is intentionally disabled.",
  "Use npm run deploy:ethereum-mainnet:gated:local so the private operator wrapper enforces CI rejection,",
  "canonical AGIALPHA token checks, redacted/private authorization YES, commitment hashes, and typed confirmation.",
  "Sepolia/local Ignition templates remain public-safe examples only."
].join(" ");
console.error(message);
process.exit(1);
