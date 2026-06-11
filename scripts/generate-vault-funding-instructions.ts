import fs from "fs";
import path from "path";

const target = process.argv[2] || "ethereum-mainnet";
const manifestPath = path.join(__dirname, "..", "deployments", `${target}.agialpha.latest.json`);

if (!fs.existsSync(manifestPath)) {
  throw new Error(`Missing deployment manifest: ${manifestPath}`);
}

const deployment = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const contracts = deployment.contracts || {};

const suggested = [
  ["CommercializationPerformanceVault", contracts.CommercializationPerformanceVault, "Performance vault. Fund only after approved strategy."],
  ["ProofRewardsVault", contracts.ProofRewardsVault, "Builder/proof-job rewards."],
  ["LiquidityVault", contracts.LiquidityVault, "Liquidity/operations reserve."],
  ["SecurityVault", contracts.SecurityVault, "Audit/bug bounty/security reserve."],
  ["CommunityVault", contracts.CommunityVault, "AGI Club/genesis community/credentials reserve."]
];

console.log(`# AGIALPHA Vault Funding Instructions for ${deployment.network}`);
console.log("");
console.log(`AGIALPHA token: ${deployment.agialphaToken}`);
console.log("");
console.log("Transfer AGIALPHA directly to the vault addresses below from an authorized treasury/funder wallet.");
console.log("Do not fund from the deployer unless the deployer is intentionally the funding wallet.");
console.log("");
for (const [name, address, memo] of suggested) {
  console.log(`- ${name}: ${address} — ${memo}`);
}
console.log("");
console.log("Record every transfer in the token event ledger and treasury evidence docket.");
