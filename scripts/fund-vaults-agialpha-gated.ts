import { ethers } from "hardhat";
import fs from "fs";
import path from "path";

const erc20Abi = [
  "function transfer(address to, uint256 amount) returns (bool)",
  "function balanceOf(address account) view returns (uint256)"
];

const requiredHash = (name: string) => {
  const value = process.env[name] || "";
  if (!/^0x[0-9a-fA-F]{64}$/.test(value)) throw new Error(`${name} must be a 0x-prefixed 32-byte hash.`);
  return value;
};

async function main() {
  if (process.env.ALLOW_VAULT_FUNDING !== "YES_FUNDER_APPROVED") {
    throw new Error("Vault funding blocked. Set ALLOW_VAULT_FUNDING=YES_FUNDER_APPROVED only after treasury approval.");
  }
  requiredHash("VAULT_FUNDING_APPROVAL_HASH");

  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) throw new Error(`Expected Ethereum mainnet chainId 1; got ${net.chainId}`);

  const manifestPath = path.join(__dirname, "..", "deployments", "ethereum-mainnet.agialpha.latest.json");
  if (!fs.existsSync(manifestPath)) throw new Error(`Missing manifest: ${manifestPath}`);

  const deployment = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const token = new ethers.Contract(deployment.agialphaToken, erc20Abi, (await ethers.getSigners())[0]);

  const funding = [
    ["CommercializationPerformanceVault", process.env.FUND_COMMERCIALIZATION_VAULT || "0"],
    ["ProofRewardsVault", process.env.FUND_PROOF_REWARDS_VAULT || "0"],
    ["LiquidityVault", process.env.FUND_LIQUIDITY_VAULT || "0"],
    ["SecurityVault", process.env.FUND_SECURITY_VAULT || "0"],
    ["CommunityVault", process.env.FUND_COMMUNITY_VAULT || "0"]
  ];

  for (const [key, amountRaw] of funding) {
    const amount = BigInt(amountRaw);
    if (amount === 0n) continue;
    const to = deployment.contracts[key];
    if (!to) throw new Error(`Missing vault address: ${key}`);
    const tx = await token.transfer(to, amount);
    await tx.wait();
    console.log(`Funded ${key}: ${amount.toString()} AGIALPHA wei -> ${to}; tx=${tx.hash}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
